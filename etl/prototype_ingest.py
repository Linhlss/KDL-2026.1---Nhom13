"""Week 1 OPM Parquet loader. Run from the repository root."""

import argparse
import csv
import hashlib
import os
import re
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

import psycopg
import pyarrow as pa
import pyarrow.parquet as pq
from dotenv import dotenv_values
from psycopg import sql


FAMILIES = ("accessions", "separations", "employment")
SOURCE_COLUMNS = ("source_file_sha256", "source_row_ordinal")
TABLE_MARKER = "TV3 week 1 prototype; managed by etl/prototype_ingest.py"
LOG_FIELDS = (
    "run_id", "started_at", "family", "report_month", "version", "filename",
    "size_bytes", "sha256", "checksum_status", "source_rows", "source_columns",
    "selection", "batch_size", "expected_rows", "copied_rows", "sql_count",
    "distinct_ordinals", "first_ordinal", "last_ordinal", "checksum_seconds",
    "read_seconds", "copy_seconds", "check_seconds", "duration_seconds",
    "status", "error", "target_table",
)


def positive_int(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return number


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, required=True,
                        help="Parquet path or filename under RAW_DATA_DIR")
    parser.add_argument("--family", choices=FAMILIES, required=True)
    parser.add_argument("--month", required=True, help="report month in YYYYMM")
    parser.add_argument("--version", type=positive_int, required=True)
    parser.add_argument("--limit", type=positive_int, help="first N rows; full file if omitted")
    parser.add_argument("--batch-size", type=positive_int, default=10_000)
    parser.add_argument("--config", type=Path, default=Path("configs/.env"))
    parser.add_argument("--expected-sha256", help="full-file checksum from an independent source")
    parser.add_argument("--log", type=Path, default=Path("reports/TV3_week1_load_log.csv"))
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9]{4}(0[1-9]|1[0-2])", args.month):
        parser.error("--month must be YYYYMM with a valid month")
    source_name = f"{args.family}_{args.month}_v{args.version}.parquet"
    if args.file.name != source_name:
        parser.error(f"filename must match family/month/version: {source_name}")
    if args.expected_sha256 and not re.fullmatch(r"[0-9a-fA-F]{64}", args.expected_sha256):
        parser.error("--expected-sha256 must contain 64 hexadecimal characters")
    return args


def postgres_type(field):
    kind = field.type
    if pa.types.is_dictionary(kind):
        kind = kind.value_type
    if (pa.types.is_string(kind) or pa.types.is_large_string(kind)
            or pa.types.is_null(kind)):
        return "text"
    if field.name.endswith("_code"):
        raise ValueError(f"Code column {field.name!r} is {kind}, expected text; inspect the dictionary")
    if pa.types.is_boolean(kind):
        return "boolean"
    if pa.types.is_uint64(kind) or pa.types.is_decimal(kind):
        return "numeric"
    if pa.types.is_integer(kind):
        return "bigint"
    if pa.types.is_floating(kind):
        return "double precision"
    if pa.types.is_date(kind):
        return "date"
    if pa.types.is_timestamp(kind) and kind.unit != "ns":
        return "timestamp with time zone" if kind.tz else "timestamp without time zone"
    raise ValueError(f"Unsupported Arrow type {kind} for {field.name!r}; inspect the source schema")


def create_target(cur, table_name, table, schema):
    names = schema.names
    if len(set(names)) != len(names) or any(
        not name or len(name.encode("utf-8")) > 63 or name in SOURCE_COLUMNS for name in names
    ):
        raise ValueError("Parquet column names are not usable as distinct PostgreSQL identifiers")
    columns = [
        sql.SQL("{} {}").format(sql.Identifier(field.name), sql.SQL(postgres_type(field)))
        for field in schema
    ]
    columns.extend([
        sql.SQL("source_file_sha256 text NOT NULL"),
        sql.SQL("source_row_ordinal bigint NOT NULL CHECK (source_row_ordinal > 0)"),
    ])
    cur.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (f"staging.{table_name}",))
    cur.execute(
        "SELECT oid IS NOT NULL, obj_description(oid, 'pg_class') "
        "FROM (SELECT to_regclass(%s)::oid AS oid) AS target",
        (f"staging.{table_name}",),
    )
    exists, marker = cur.fetchone()
    if exists and marker != TABLE_MARKER:
        raise ValueError(f"staging.{table_name} exists without the prototype marker")
    if exists:
        cur.execute(sql.SQL("DROP TABLE {}").format(table))
    cur.execute(sql.SQL("CREATE TABLE {} ({})").format(table, sql.SQL(", ").join(columns)))
    cur.execute(sql.SQL("COMMENT ON TABLE {} IS {}").format(table, sql.Literal(TABLE_MARKER)))


def copy_rows(cur, table, parquet, run):
    target_columns = sql.SQL(", ").join(
        map(sql.Identifier, [*parquet.schema_arrow.names, *SOURCE_COLUMNS])
    )
    statement = sql.SQL("COPY {} ({}) FROM STDIN").format(table, target_columns)
    batches = parquet.iter_batches(batch_size=run["batch_size"], use_threads=False)
    remaining = run["expected_rows"]
    ordinal = 0
    read_seconds = 0.0
    start = perf_counter()
    with cur.copy(statement) as writer:
        while remaining:
            read_start = perf_counter()
            batch = next(batches, None)
            if batch is None:
                raise ValueError("Parquet batches ended before the expected number of rows")
            batch = batch.slice(0, min(remaining, batch.num_rows))
            values = [column.to_pylist() for column in batch.columns]
            read_seconds += perf_counter() - read_start
            for row in zip(*values, strict=True):
                ordinal += 1
                writer.write_row((*row, run["sha256"], ordinal))
            remaining -= batch.num_rows
            run["copied_rows"] = ordinal
    run["read_seconds"] = round(read_seconds, 6)
    run["copy_seconds"] = round(perf_counter() - start - read_seconds, 6)


def load(args, run):
    if not args.config.is_file():
        raise ValueError("Config missing; copy configs/.env.example to configs/.env and fill PGUSER")
    config = dotenv_values(args.config, interpolate=False)
    settings = {
        key[2:].lower(): config[key]
        for key in ("PGHOST", "PGPORT", "PGUSER", "PGPASSWORD")
        if config.get(key)
    }
    if config.get("PGDATABASE") != "workforce_dw" or not settings.get("user"):
        raise ValueError("Set PGDATABASE=workforce_dw and a valid PGUSER in configs/.env")
    path = args.file
    if not path.is_absolute() and not path.is_file():
        path = Path(config.get("RAW_DATA_DIR") or "data/raw") / path

    table_name = f"prototype_{args.family}"
    table = sql.Identifier("staging", table_name)
    with path.open("rb") as source:
        initial_stat = os.fstat(source.fileno())
        run["size_bytes"] = initial_stat.st_size
        start = perf_counter()
        run["sha256"] = hashlib.file_digest(source, "sha256").hexdigest()
        run["checksum_seconds"] = round(perf_counter() - start, 6)
        if args.expected_sha256:
            if run["sha256"] != args.expected_sha256.lower():
                run["checksum_status"] = "mismatch"
                raise ValueError("Full-file SHA-256 does not match --expected-sha256")
            run["checksum_status"] = "matches_supplied_checksum"
        else:
            run["checksum_status"] = "computed_only"
        source.seek(0)
        parquet = pq.ParquetFile(source)
        total = parquet.metadata.num_rows
        run["source_rows"] = total
        run["source_columns"] = len(parquet.schema_arrow)
        expected = min(args.limit, total) if args.limit is not None else total
        run["expected_rows"] = expected
        run["copied_rows"] = 0
        with psycopg.connect(dbname="workforce_dw", connect_timeout=5, **settings) as conn:
            with conn.cursor() as cur:
                create_target(cur, table_name, table, parquet.schema_arrow)
                copy_rows(cur, table, parquet, run)
                final_stat = os.fstat(source.fileno())
                if (final_stat.st_size, final_stat.st_mtime_ns) != (
                    initial_stat.st_size, initial_stat.st_mtime_ns
                ):
                    raise ValueError("Source file changed during the load")
                start = perf_counter()
                cur.execute(sql.SQL(
                    "SELECT count(*), count(DISTINCT source_row_ordinal), "
                    "min(source_row_ordinal), max(source_row_ordinal), "
                    "count(*) FILTER (WHERE source_file_sha256 <> %s) FROM {}"
                ).format(table), (run["sha256"],))
                count, distinct_count, first, last, wrong_hash = cur.fetchone()
                run.update(sql_count=count, distinct_ordinals=distinct_count,
                           first_ordinal=first, last_ordinal=last,
                           check_seconds=round(perf_counter() - start, 6))
                bounds = (1, expected) if expected else (None, None)
                if count != expected or distinct_count != expected or (first, last) != bounds or wrong_hash:
                    raise ValueError("SQL count, source hash or ordinal check failed")


def main():
    args = arguments()
    start = perf_counter()
    run = {
        "run_id": str(uuid.uuid4()),
        "started_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "family": args.family,
        "report_month": args.month,
        "version": args.version,
        "filename": args.file.name,
        "selection": f"first {args.limit}" if args.limit else "full",
        "batch_size": args.batch_size,
        "target_table": f"staging.prototype_{args.family}",
    }
    try:
        load(args, run)
        run["status"] = "PASS"
    except psycopg.Error as error:
        # PostgreSQL error context can include source values; keep only type and code.
        run.update(status="FAIL", error=f"{type(error).__name__} (SQLSTATE {error.sqlstate or 'n/a'})")
    except FileNotFoundError:
        run.update(status="FAIL", error="Parquet not found; check --file and RAW_DATA_DIR")
    except (ValueError, OSError, pa.ArrowException) as error:
        message = str(error) if type(error) is ValueError else type(error).__name__
        run.update(status="FAIL", error=message)
    run["duration_seconds"] = round(perf_counter() - start, 6)
    args.log.parent.mkdir(parents=True, exist_ok=True)
    with args.log.open("a", newline="", encoding="utf-8") as log:
        writer = csv.DictWriter(log, fieldnames=LOG_FIELDS, lineterminator="\n")
        if log.tell() == 0:
            writer.writeheader()
        writer.writerow(run)
    print(f'{run["status"]} {run["target_table"]} run={run["run_id"]} '
          f'expected={run.get("expected_rows", "-")} sql_count={run.get("sql_count", "-")} '
          f'seconds={run["duration_seconds"]} log={args.log}')
    if run["status"] == "FAIL":
        print(run["error"], file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
