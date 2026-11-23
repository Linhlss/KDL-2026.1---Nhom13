"""Check K10 against the audited source identity and official coverage scope."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "etl"))
from g2_pipeline import initialize, rows
from g2_test_support import ROOT, temporary_database


def check(conn):
    initialize(conn)
    initialize(conn)
    assert conn.execute("SELECT count(*) FROM audit.lookup_coverage_snapshot").fetchone()[0] == 104
    assert conn.execute("SELECT count(*) FROM audit.fk_lookup_coverage").fetchone()[0] == 0
    source = next(item for item in rows(ROOT / "docs/03_source_inventory.csv")
                  if item["family"] == "employment" and item["report_month"] == "202504")
    conn.execute(
        "INSERT INTO raw_meta.source_file(family, report_month, version, filename, sha256, schema_hash, "
        "size_bytes, row_count, column_count, source_url, status) VALUES "
        "(%(family)s, %(report_month)s, %(version)s, %(filename)s, %(sha256)s, %(schema_hash)s, "
        "%(size_bytes)s, %(row_count)s, %(column_count)s, %(source_url)s, 'LOADED')",
        source,
    )
    audit = dict((field, (status, eligible, matched, rate)) for field, status, eligible, matched, rate in conn.execute(
        "SELECT lookup_field, lookup_status, eligible_rows, matched_rows, coverage_pct FROM audit.fk_lookup_coverage"
    ))
    assert audit["agency_subelement_code"] == ("PARTIAL", 2271969, 2271538, None), audit
    assert audit["agency_code"] == ("PARTIAL", 2271969, None, None), audit
    for field, eligible, matched in (("fixture_verified", 3, 2), ("fixture_zero", 0, 0)):
        conn.execute(
            "INSERT INTO audit.lookup_coverage_snapshot VALUES "
            "(%(family)s, %(report_month)s, %(filename)s, %(sha256)s, %(field)s, "
            "'VERIFIED','COMPLETE',%(eligible)s,%(matched)s)",
            {**source, "field": field, "eligible": eligible, "matched": matched},
        )
    rates = dict(conn.execute(
        "SELECT lookup_field, coverage_pct::text FROM audit.fk_lookup_coverage WHERE lookup_field LIKE 'fixture%'"
    ))
    assert rates == {"fixture_verified": "66.666667", "fixture_zero": None}, rates
    conn.execute("UPDATE raw_meta.source_file SET sha256='fixture-different-sha'")
    assert conn.execute("SELECT count(*) FROM audit.fk_lookup_coverage").fetchone()[0] == 0
    print("PASS K10 initialization, official scope, zero denominator and source hash")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/.env")
    with temporary_database(parser.parse_args().config) as conn:
        check(conn)
