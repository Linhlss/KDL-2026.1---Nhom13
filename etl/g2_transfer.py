"""Create an aggregate-only PostgreSQL database for TV4."""
import argparse
import re
from pathlib import Path

import psycopg
from dotenv import dotenv_values
from psycopg import sql

ROOT = Path(__file__).resolve().parents[1]
TABLES = ("dw.dim_month", "dw.dim_agency", "dw.dim_action_category",
          "mart.workforce_monthly", "mart.personnel_flows_monthly")
TRANSFER_DDL = ROOT / "sql/06_g2_transfer.sql"
SOURCE_DDL = (ROOT / "sql/03_dw_ddl.sql", ROOT / "sql/04_create_marts.sql")


def table_blocks(text):
    """CREATE TABLE statements keyed by table name, whitespace-normalised."""
    return {name: " ".join(body.split()) for name, body in re.findall(
        r"CREATE TABLE IF NOT EXISTS ([a-z_.]+) (\(.*?\n\);)", text, re.S)}


def check_transfer_ddl():
    """06_g2_transfer.sql copies the Dimension/Mart DDL; refuse to run if it drifted."""
    transfer = table_blocks(TRANSFER_DDL.read_text(encoding="utf-8"))
    source = {}
    for path in SOURCE_DDL:
        source.update(table_blocks(path.read_text(encoding="utf-8")))
    drift = [name for name in TABLES if transfer.get(name) is None or transfer[name] != source.get(name)]
    if drift:
        raise ValueError("06_g2_transfer.sql differs from 03/04 DDL for: " + ", ".join(drift))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT/"configs/.env")
    parser.add_argument("--source", default="workforce_dw")
    parser.add_argument("--target", default="workforce_g2_transfer")
    args = parser.parse_args()
    if args.source == args.target:
        parser.error("source and target must differ")
    check_transfer_ddl()
    config = dotenv_values(args.config, interpolate=False)
    settings = {k[2:].lower():config[k] for k in
                ("PGHOST","PGPORT","PGUSER","PGPASSWORD") if config.get(k)}
    with psycopg.connect(dbname="postgres",autocommit=True,**settings) as admin:
        exists = admin.execute("SELECT 1 FROM pg_database WHERE datname=%s",(args.target,)).fetchone()
        if not exists:
            admin.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(args.target)))
    with psycopg.connect(dbname=args.source,**settings) as source, psycopg.connect(dbname=args.target,**settings) as target:
        source.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY")
        if target.execute(
            "SELECT count(*) FROM pg_tables WHERE schemaname NOT IN ('pg_catalog','information_schema')"
        ).fetchone()[0]:
            raise ValueError("Transfer target must be empty; choose a new database name")
        target.execute(TRANSFER_DDL.read_text(encoding="utf-8"))
        target.execute("TRUNCATE mart.workforce_monthly,mart.personnel_flows_monthly,dw.dim_agency,dw.dim_action_category,dw.dim_month")
        for name in TABLES:
            table = sql.Identifier(*name.split("."))
            with source.cursor().copy(sql.SQL("COPY {} TO STDOUT").format(table)) as reader:
                with target.cursor().copy(sql.SQL("COPY {} FROM STDIN").format(table)) as writer:
                    for block in reader:
                        writer.write(block)
            source_count = source.execute(sql.SQL("SELECT count(*) FROM {}").format(table)).fetchone()[0]
            target_count = target.execute(sql.SQL("SELECT count(*) FROM {}").format(table)).fetchone()[0]
            if source_count != target_count:
                raise ValueError(f"Transfer count mismatch: {name}")
            print(f"{name}: {target_count} rows copied")
        target.execute("COMMENT ON SCHEMA mart IS 'TV3 G2 aggregate MVP; TV4/TV5 review pending'")
    print(f"Transfer ready: {args.target}; validate private dump/restore before TV4 handoff")


if __name__ == "__main__":
    main()
