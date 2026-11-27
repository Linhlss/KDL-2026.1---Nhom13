"""Compare source quality totals directly from real Parquet with PostgreSQL ODS."""
import argparse
import json
import sys
from pathlib import Path

import pyarrow.compute as pc
import pyarrow.parquet as pq
from psycopg import sql

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "etl"))
from g2_pipeline import (
    connect, resolve_config, rows, safe_error, selected_sources, validate_month, verify_file,
)


def preflight_sources(args):
    """Validate complete inventory and all input files before comparing any family."""
    validate_month(args.month)
    selected = selected_sources(rows(args.inventory), args.month)
    sources = []
    for item in selected:
        path = args.raw_dir / item["filename"]
        if not path.is_file():
            path = args.raw_dir / item["family"] / item["filename"]
        verify_file(path, item)
        sources.append((item, path))
    return sources


def source_metrics(path, family, month):
    time = "snapshot_yyyymm" if family == "employment" else "personnel_action_effective_date_yyyymm"
    metrics = dict(rows=0, count_not_one=0, pay_null=0, pay_empty=0, pay_redacted=0, other_month=0,
                   occupation_leading_zero=0)
    for batch in pq.ParquetFile(path).iter_batches(columns=[
        "count", "annualized_adjusted_basic_pay", time, "occupational_series_code"
    ], batch_size=50000):
        def count_true(values):
            return pc.sum(pc.cast(pc.fill_null(values, False), "int64")).as_py() or 0
        metrics["rows"] += batch.num_rows
        metrics["count_not_one"] += count_true(pc.invert(pc.fill_null(pc.equal(batch["count"], "1"), False)))
        pay = batch["annualized_adjusted_basic_pay"]
        metrics["pay_null"] += pay.null_count
        metrics["pay_empty"] += count_true(pc.equal(pc.utf8_trim_whitespace(pay), ""))
        metrics["pay_redacted"] += count_true(pc.equal(pc.utf8_upper(pc.utf8_trim_whitespace(pay)), "REDACTED"))
        metrics["other_month"] += count_true(pc.not_equal(batch[time], month))
        metrics["occupation_leading_zero"] += count_true(pc.match_substring_regex(
            batch["occupational_series_code"], "^0[0-9]"))
    return metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT/"configs/.env")
    parser.add_argument("--database")
    parser.add_argument("--month", default="202504")
    parser.add_argument("--raw-dir", type=Path)
    parser.add_argument("--inventory", type=Path, default=ROOT/"docs/03_source_inventory.csv")
    args = parser.parse_args()
    try:
        validate_month(args.month)
    except ValueError as error:
        parser.error(str(error))
    if not args.config.is_file():
        parser.error("config file missing")
    resolve_config(args)
    try:
        sources = preflight_sources(args)
        results = []
        with connect(args) as conn:
            for item, path in sources:
                family = item["family"]
                registered = conn.execute(
                    "SELECT filename,sha256,row_count FROM raw_meta.source_file "
                    "WHERE family=%s AND report_month=%s AND is_active AND status='LOADED'",
                    (family, args.month),
                ).fetchall()
                if registered != [(item["filename"], item["sha256"], int(item["row_count"]))]:
                    raise ValueError(f"{family}: exactly one matching active LOADED source required")
                expected = source_metrics(path, family, args.month)
                time = "snapshot_yyyymm" if family == "employment" else "effective_month"
                query = sql.SQL("""
             SELECT count(*),count(*) FILTER(WHERE "count" IS DISTINCT FROM '1'),
             count(*) FILTER(WHERE pay_state='NULL'),count(*) FILTER(WHERE pay_state='EMPTY'),
             count(*) FILTER(WHERE pay_state='REDACTED'),count(*) FILTER(WHERE o.{time}<>%s),
             count(*) FILTER(WHERE occupational_series_code ~ '^0[0-9]')
             FROM ods.{table} o JOIN raw_meta.source_file f USING(file_id)
             WHERE f.report_month=%s AND f.is_active AND f.status='LOADED'
                """).format(time=sql.Identifier(time), table=sql.Identifier("ods_"+family+"_record"))
                actual = dict(zip(expected, conn.execute(query,(args.month,args.month)).fetchone(),strict=True))
                if actual != expected:
                    raise ValueError(f"{family}: Parquet/ODS mismatch; expected={expected}; actual={actual}")
                results.append((family, actual))
        for family, actual in results:
            print("PASS",family,json.dumps(actual,sort_keys=True))
    except Exception as error:
        print("FAIL " + safe_error(error), file=sys.stderr)
        return 1
    print("TV3 source-direct crosscheck passed; independent TV5 review pending.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
