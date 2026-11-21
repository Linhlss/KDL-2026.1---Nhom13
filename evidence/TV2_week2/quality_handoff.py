"""Rehearse the J02 rules on the locked baseline and report measured cases."""
import argparse
from pathlib import Path

import duckdb

from source_baseline import (
    FAMILIES, ROOT, TIME, dq_checks, identifier, make_inventory, paths, read_csv, text_state_sql, write_csv,
)

MEASUREMENT_SQL = ROOT / "sql/tests/07_l212_before_after.sql"


def lookup_query(source_rows, reference_rows):
    """Accept text codes and labels and preserve one output row per source row."""
    return f"""
WITH s AS ({source_rows}), reference_candidates AS ({reference_rows}),
reference_counts AS (
    SELECT code, count(*) AS matches
    FROM reference_candidates
    WHERE ({text_state_sql('code')}) = 'PRESENT'
      AND ({text_state_sql('label')}) = 'PRESENT'
    GROUP BY code
), classified AS (
    SELECT s.*, ({text_state_sql('raw_code')}) AS code_state,
           ({text_state_sql('raw_pay')}) AS pay_state
    FROM s
)
SELECT c.*, CASE
           WHEN code_state <> 'PRESENT' THEN code_state
           WHEN r.matches IS NULL THEN 'UNKNOWN'
           WHEN r.matches = 1 THEN 'MATCHED'
           ELSE 'AMBIGUOUS'
       END AS lookup_state
FROM classified c LEFT JOIN reference_counts r ON c.raw_code = r.code
"""


def measure_file(con, path, month, time_field):
    source = f"""
        SELECT file_row_number + 1 AS ordinal, "count" AS raw_count, {identifier(time_field)} AS business_month,
               agency_code AS raw_code, agency AS agency_label, annualized_adjusted_basic_pay AS raw_pay
        FROM read_parquet(?, file_row_number=true)
    """
    derived_reference = "SELECT DISTINCT raw_code AS code, agency_label AS label FROM s"
    query = MEASUREMENT_SQL.read_text(encoding="utf-8").replace(
        "{{normalized}}", lookup_query(source, derived_reference))
    cursor = con.execute(query, [month, str(path)])
    return dict(zip([item[0] for item in cursor.description], cursor.fetchone(), strict=True))


def compare_file(item, measured, quality, expected_mismatch):
    before = item["row_count"]
    if (measured["after_rows"], measured["unique_ordinals"], measured["parse_count"]) != (before,) * 3:
        raise ValueError(f"J02 changed the rows, lineage or count of {item['filename']}")
    if measured["different_month"] != expected_mismatch:
        raise ValueError(f"Period mismatch count changed in {item['filename']}")
    for field in ("pay_null", "pay_empty", "pay_redacted", "pay_invalid"):
        if measured[field] != quality[field]:
            raise ValueError(f"J02 changed {field} in {item['filename']}")
    if sum(n for key, n in measured.items() if key.startswith("lookup_")) != before:
        raise ValueError(f"Lookup states do not partition {item['filename']}")

    pay = dict(null_rows=measured["pay_null"], empty_rows=measured["pay_empty"],
               redacted_rows=measured["pay_redacted"])
    lookup = dict(null_rows=measured["lookup_null"], empty_rows=measured["lookup_empty"],
                  redacted_rows=measured["lookup_redacted"], matched_rows=measured["lookup_matched"],
                  unknown_rows=measured["lookup_unknown"], ambiguous_rows=measured["lookup_ambiguous"])
    unavailable_pay = sum(pay.values())
    numeric_pay = before - unavailable_pay - measured["pay_invalid"]
    outside_match = before - lookup["matched_rows"]
    different_month = measured["different_month"]
    rules = (
        ("DQ01", "Raw count text", "Validate and cast count to BIGINT", "count = 1",
         measured["parse_count"], f"Each row contributes one count. The count total equals {before} source rows.",
         {}),
        ("DQ02", "Raw annualized pay", "Carry NULL / EMPTY / REDACTED states separately",
         "Keep raw value and state. Cast only present pay", unavailable_pay,
         f"Preserves {unavailable_pay} unavailable pay values by state. {numeric_pay} rows have usable numeric pay.",
         pay),
        ("DQ03", "Source agency code", "LEFT JOIN per-file derived agency lookup",
         "Preserve each ordinal and report lookup states separately", outside_match,
         f"Retains all {before} source rows. {outside_match} rows lack a unique match in the per-file lookup.",
         lookup),
        ("DQ04", "Snapshot/effective YYYYMM", "Carry report month and business month separately",
         "Retain all mismatched periods", different_month,
         f"Keeps {different_month} rows with different periods. Counts can still use the original report month.",
         {}),
    )
    return [
        dict(family=item["family"], report_month=item["report_month"], source_file=item["filename"],
             rule_id=code, before=raw, rule=rule, after=target, affected_rows=affected, impact=impact,
             before_rows=before, after_rows=measured["after_rows"],
             **{key: details.get(key, "") for key in ("null_rows", "empty_rows", "redacted_rows",
                                                     "matched_rows", "unknown_rows", "ambiguous_rows")},
             validation="MEASURED in DuckDB. PostgreSQL J02 pending")
        for code, raw, rule, target, affected, impact, details in rules
    ]


def print_summary(result):
    print(f"DuckDB {duckdb.__version__}  |  {MEASUREMENT_SQL.relative_to(ROOT).as_posix()}")
    print(f"{'Family':<13} {'Before':>11} {'After':>11} {'Count = 1':>11} "
          f"{'Pay unavailable':>16} {'Agency unmatched':>17} {'Month differs':>13}")
    groups = {family: [row for row in result if row["family"] == family] for family in FAMILIES}
    groups["Total"] = result
    for family, rows in groups.items():
        by_rule = {rule: [row for row in rows if row["rule_id"] == rule]
                   for rule in ("DQ01", "DQ02", "DQ03", "DQ04")}
        before = sum(row["before_rows"] for row in by_rule["DQ01"])
        after = sum(row["after_rows"] for row in by_rule["DQ01"])
        affected = [sum(row["affected_rows"] for row in rows) for rows in by_rule.values()]
        print(f"{family:<13} {before:>11,} {after:>11,} {affected[0]:>11,} "
              f"{affected[1]:>16,} {affected[2]:>17,} {affected[3]:>13,}")
    print(f"{len(result) // 4} Parquet files  |  {len(result)} rule measurements")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw", type=Path)
    args = parser.parse_args()
    files = paths(args.raw.resolve())
    inventory, _ = make_inventory(files)
    crosscheck = {row["filename"]: row for row in read_csv(
        ROOT / "evidence/TV1_week2/baseline_crosscheck.csv")}
    result = []
    with duckdb.connect() as con:
        checks = {row["source_file"]: row for row in dq_checks(con, files, inventory)}
        for item in inventory:
            family, month, name = item["family"], item["report_month"], item["filename"]
            time_field = "snapshot_yyyymm" if family == "employment" else TIME
            measured = measure_file(con, files[family, month], month, time_field)
            expected = int(crosscheck[name]["rows_time_field_ne_file_month"])
            result.extend(compare_file(item, measured, checks[name], expected))
    write_csv(ROOT / "reports/07_source_quality_to_etl_rules.csv", result)
    print_summary(result)


if __name__ == "__main__":
    main()
