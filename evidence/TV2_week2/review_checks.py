"""Exercise the SQL and reference edge cases from the TV2 PR review."""
import argparse
from collections import Counter
from datetime import date

import duckdb

from audit_relationships import reference_metrics, state
from quality_handoff import lookup_query
from source_mapping import TABLES, fact_lineage_sql

SOURCE = """
SELECT * FROM (VALUES
    (1, '001', '123.45'),
    (2, '999', NULL),
    (3, '002', '  '),
    (4, NULL, 'redacted'),
    (5, '', ''),
    (6, '   ', ' REDACTED '),
    (7, ' redacted ', '0.00'),
    (8, '003', NULL)
) AS fixture_rows(ordinal, raw_code, raw_pay)
"""
REFERENCE = """
SELECT * FROM (VALUES
    ('001', 'valid label'),
    ('002', 'first label'),
    ('002', 'second label'),
    ('003', 'same label'),
    ('003', 'same label')
) AS fixture_rows(code, label)
"""
EXPECTED = """
SELECT * FROM (VALUES
    (1, '001', '123.45', 'PRESENT', 'PRESENT', 'MATCHED'),
    (2, '999', NULL, 'PRESENT', 'NULL', 'UNKNOWN'),
    (3, '002', '  ', 'PRESENT', 'EMPTY', 'AMBIGUOUS'),
    (4, NULL, 'redacted', 'NULL', 'REDACTED', 'NULL'),
    (5, '', '', 'EMPTY', 'EMPTY', 'EMPTY'),
    (6, '   ', ' REDACTED ', 'EMPTY', 'REDACTED', 'EMPTY'),
    (7, ' redacted ', '0.00', 'REDACTED', 'PRESENT', 'REDACTED'),
    (8, '003', NULL, 'PRESENT', 'NULL', 'AMBIGUOUS')
) AS fixture_rows(ordinal, raw_code, raw_pay, code_state, pay_state, lookup_state)
"""


def j02_fixture_sql():
    return f"""
WITH expected AS ({EXPECTED}), actual AS ({lookup_query(SOURCE, REFERENCE)}),
missing AS (SELECT * FROM expected EXCEPT ALL SELECT * FROM actual),
unexpected AS (SELECT * FROM actual EXCEPT ALL SELECT * FROM expected)
SELECT 'MISSING' AS finding, * FROM missing
UNION ALL
SELECT 'UNEXPECTED' AS finding, * FROM unexpected;
"""


def check_lineage(con):
    con.execute("CREATE SCHEMA ods")
    con.execute("CREATE SCHEMA dw")
    valid = [(1, 1), (1, 2), (2, 1)]
    cases = {
        "valid": (valid, valid, []),
        "missing": (valid, valid[1:], ["MISSING_FACT_KEY"]),
        "extra": (valid, [*valid, (2, 2)], ["EXTRA_FACT_KEY"]),
        "duplicate fact": (valid, [*valid, (1, 1)], ["DUPLICATE_FACT_KEY"]),
        "duplicate ods": ([*valid, (1, 1)], valid, ["DUPLICATE_ODS_KEY"]),
        "duplicate on both sides": ([*valid, (1, 1)], [*valid, (1, 1)],
                                    ["DUPLICATE_ODS_KEY", "DUPLICATE_FACT_KEY"]),
        "null": ([*valid, (None, 1)], [*valid, (2, None)], ["NULL_ODS_KEY", "NULL_FACT_KEY"]),
        "same total, different keys": (valid, [(1, 1), (2, 1), (2, 2)],
                                       ["MISSING_FACT_KEY", "EXTRA_FACT_KEY"]),
    }
    for ods, fact in TABLES.values():
        con.execute(f"CREATE TABLE ods.{ods} (file_id BIGINT, source_row_ordinal BIGINT)")
        con.execute(f"CREATE TABLE dw.{fact} (file_id BIGINT, source_row_ordinal BIGINT)")
        for name, (left, right, expected) in cases.items():
            con.execute(f"DELETE FROM ods.{ods}")
            con.execute(f"DELETE FROM dw.{fact}")
            con.executemany(f"INSERT INTO ods.{ods} VALUES (?, ?)", left)
            con.executemany(f"INSERT INTO dw.{fact} VALUES (?, ?)", right)
            actual = Counter(row[2] for row in con.execute(fact_lineage_sql(ods, fact)).fetchall())
            assert actual == Counter(expected), (fact, name, actual)
    print(f"{len(TABLES) * len(cases)} Fact lineage checks passed.")


def check_reference():
    assert state((None,)) == "null"
    assert state(("   ",)) == "empty"
    assert state((" redacted ",)) == "redacted"
    assert state(("001",)) == "present"
    assert state((" redacted ", " ")) == "empty"
    url = "https://data.opm.gov/data-standards/agency-subelement"
    start, end = date(2025, 3, 1), date(2025, 3, 31)
    complete = ("001", start, end, url, "COMPLETE")
    observed = {("001",): 9, ("999",): 3}
    mismatched = reference_metrics(observed, "202503", [complete, complete])
    assert mismatched["orphan_rows"] == 3 and mismatched["duplicate_ref_keys"] == 1
    assert mismatched["reference_left_join_rows"] == 21 and mismatched["k10_coverage_pct"] == ""
    sample = ("001", start, end, url, "SAMPLE")
    partial = reference_metrics(observed, "202503", [sample])
    assert partial["reference_unique_matches"] == 9 and partial["reference_eligible_rows"] == 9
    assert partial["orphan_rows"] == "" and partial["k10_coverage_pct"] == ""
    assert reference_metrics(observed, "202504", [sample])["reference_coverage"] == "NOT_CHECKED"
    assert reference_metrics({}, "202503", [complete])["k10_coverage_pct"] == ""
    valid = reference_metrics({("001",): 9}, "202503", [complete], source_rows=12)
    assert valid["reference_left_join_rows"] == 12 and valid["k10_coverage_pct"] == "100.000000"
    print("Reference scope, duplicate, orphan and K10 checks passed.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--postgres-j02", action="store_true",
                        help="Print the standalone PostgreSQL fixture; expected result is zero rows")
    args = parser.parse_args()
    if args.postgres_j02:
        print(j02_fixture_sql().strip())
        return
    check_reference()
    with duckdb.connect() as con:
        check_lineage(con)
        findings = con.execute(j02_fixture_sql()).fetchall()
        assert not findings, findings
        print("J02 fixture passed on DuckDB: 8 rows, all raw values and expected states retained.")


if __name__ == "__main__":
    main()
