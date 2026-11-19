"""Measure source-level before/after rules for the handoff to TV3 J02."""
import argparse
from pathlib import Path

import duckdb

from source_baseline import ROOT, TIME, identifier, make_inventory, paths, write_csv

QUERY = """
WITH s AS (
    SELECT "count", {{time_field}} AS business_month, agency_code, agency,
           annualized_adjusted_basic_pay AS raw_pay
    FROM read_parquet(?)
), agency_lookup AS (
    SELECT agency_code, min(agency) AS checked_label FROM s
    WHERE agency_code NOT IN ('', 'REDACTED') AND agency NOT IN ('', 'REDACTED')
    GROUP BY agency_code
    HAVING count(DISTINCT agency) = 1
), normalized AS (
    SELECT try_cast("count" AS BIGINT) AS record_count, business_month,
           ? AS report_month, raw_pay,
           try_cast(raw_pay AS DECIMAL(18,2)) AS pay_numeric,
           CASE WHEN raw_pay IS NULL THEN 'NULL'
                WHEN raw_pay = '' THEN 'EMPTY'
                WHEN raw_pay = 'REDACTED' THEN 'REDACTED'
                WHEN try_cast(raw_pay AS DECIMAL(18,2)) IS NULL THEN 'INVALID'
                ELSE 'OBSERVED' END AS pay_state,
           checked_label
    FROM s LEFT JOIN agency_lookup USING (agency_code)
)
SELECT count(*) AS after_rows,
       count(*) FILTER (WHERE record_count = 1) AS cast_count,
       count(*) FILTER (WHERE business_month <> report_month) AS different_month,
       count(*) FILTER (WHERE pay_state = 'NULL') AS null_pay,
       count(*) FILTER (WHERE pay_state = 'EMPTY') AS empty_pay,
       count(*) FILTER (WHERE pay_state = 'REDACTED' AND pay_numeric IS NULL) AS redacted_pay,
       count(*) FILTER (WHERE checked_label IS NULL) AS unknown_agency
FROM normalized;
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw", type=Path)
    args = parser.parse_args()
    files = paths(args.raw.resolve())
    inventory, _ = make_inventory(files)
    result = []
    mismatches = 0
    with duckdb.connect() as con:
        for item in inventory:
            family, month = item["family"], item["report_month"]
            time_field = identifier("snapshot_yyyymm" if family == "employment" else TIME)
            after, cast, mismatch, null, empty, redacted, unknown = con.execute(
                QUERY.replace("{{time_field}}", time_field),
                [str(files[family, month]), month]).fetchone()
            before = item["row_count"]
            if before != after or cast != before:
                raise ValueError(f"J02 rehearsal changed baseline {item['filename']}")
            mismatches += mismatch
            rules = (
                ("DQ01", "Raw count text", "Validate and cast count to BIGINT", "count = 1", cast),
                ("DQ02", "Raw annualized pay", "Carry NULL / EMPTY / REDACTED states separately",
                 "Numeric NULL with explicit raw state", null + empty + redacted),
                ("DQ03", "Source agency code", "LEFT JOIN unique per-file derived agency lookup",
                 "Keep row; unmatched as Unknown candidate", unknown),
                ("DQ04", "Snapshot/effective YYYYMM", "Carry report month and business month separately",
                 "Retain all mismatched periods", mismatch),
            )
            result.extend(dict(family=family, report_month=month, source_file=item["filename"],
                               rule_id=code, before=raw, rule=rule, after=target, affected_rows=affected,
                               before_rows=before, after_rows=after,
                               validation="PASS in DuckDB source rehearsal; PostgreSQL J02 pending")
                          for code, raw, rule, target, affected in rules)
    if mismatches != 593:
        raise ValueError(f"Expected 593 events with different months, found {mismatches}")
    write_csv(ROOT / "reports/07_source_quality_to_etl_rules.csv", result)
    print(f"{len(result)} tests across all files; all rows and {mismatches} month differences retained")


if __name__ == "__main__":
    main()
