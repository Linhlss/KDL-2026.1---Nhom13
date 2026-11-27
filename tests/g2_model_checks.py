"""Run synthetic DW/Mart regressions against a disposable PostgreSQL database."""

import argparse
import sys
from pathlib import Path

from psycopg import sql

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "etl"))
from g2_model import build_model
from g2_test_support import ROOT, temporary_database


def fixture(conn):
    conn.execute(
        "CREATE SCHEMA raw_meta; CREATE SCHEMA ods; CREATE SCHEMA ref; "
        "CREATE SCHEMA dw; CREATE SCHEMA mart; CREATE SCHEMA audit;"
    )
    # Minimal stand-in for the TV2 K10 view (sql/00_raw_ref_ods_ddl.sql) used by build_model.
    conn.execute(
        "CREATE TABLE audit.fk_lookup_coverage(file_id bigint, family text, source_file text, "
        "source_sha256 text, report_month text, lookup_field text, lookup_status text, "
        "reference_coverage text, eligible_rows bigint, matched_rows bigint, coverage_pct numeric)"
    )
    conn.execute(
        "CREATE TABLE raw_meta.source_file(file_id bigint primary key, family text, "
        "report_month text, is_active boolean, status text, row_count bigint); "
        "CREATE TABLE ref.derived_lookup(relation text, report_month text, code text, "
        "label text, provenance text, load_status text); "
        "CREATE TABLE ref.label_review(relation text, report_month text, code text, "
        "review_result text, proposed_display_label text, "
        "PRIMARY KEY(relation, report_month, code))"
    )
    for family in ("employment", "accessions", "separations"):
        conn.execute(sql.SQL(
            "CREATE TABLE {}(file_id bigint, source_row_ordinal bigint, report_month text, "
            "count_value bigint, snapshot_yyyymm text, effective_month text, agency_code text, "
            "accession_category_code text, separation_category_code text, dq_flags text[], "
            "PRIMARY KEY(file_id,source_row_ordinal))"
        ).format(sql.Identifier("ods", f"ods_{family}_record")))
    file_id = 0
    for month in ("202504", "202505"):
        for family in ("employment", "accessions", "separations"):
            file_id += 1
            conn.execute(
                "INSERT INTO raw_meta.source_file VALUES(%s,%s,%s,true,'LOADED',2)",
                (file_id, family, month),
            )
            for ordinal, agency in ((1, "AA"), (2, "BB")):
                conn.execute(sql.SQL(
                    "INSERT INTO {} VALUES(%s,%s,%s,1,%s,'202503',%s,'AC','SB',ARRAY[]::text[])"
                ).format(sql.Identifier("ods", f"ods_{family}_record")),
                    (file_id, ordinal, month, month, agency))
        for relation, code in (
            ("agency", "AA"), ("agency", "BB"),
            ("accession_category", "AC"), ("separation_category", "SB"),
        ):
            conn.execute(
                "INSERT INTO ref.derived_lookup VALUES(%s,%s,%s,%s,'DERIVED_LOOKUP','READY')",
                (relation, month, code, "Label " + code),
            )
    conn.execute(
        "INSERT INTO ref.derived_lookup "
        "VALUES('agency','202504','BB','Conflicting label','DERIVED_LOOKUP','READY')"
    )


def check(conn):
    fixture(conn)
    with conn.transaction():
        initial = build_model(conn, "202504")
    assert initial["marts"]["headcount"] == 2
    assert initial["marts"]["accessions"] == 2
    assert initial["marts"]["separations"] == 2
    assert all(f["unknown_agency_rows"] == 1 for f in initial["facts"].values())
    print("PASS ambiguous duplicate agency lookup preserves rows under Unknown0")
    with conn.transaction():
        following = build_model(conn, "202505")
    assert following["marts"]["headcount"] == 2
    assert conn.execute("SELECT sum(headcount) FROM mart.workforce_monthly").fetchone()[0] == 4
    print("PASS building another month preserves prior Fact and Mart totals")
    with conn.transaction():
        repeated = build_model(conn, "202504")
    assert repeated == initial
    assert conn.execute("SELECT count(*) FROM dw.fact_accessions").fetchone()[0] == 4
    print("PASS repeat model build preserves totals without duplicate Facts")
    try:
        with conn.transaction():
            conn.execute(
                "UPDATE ods.ods_accessions_record SET count_value=NULL "
                "WHERE file_id=2 AND source_row_ordinal=1"
            )
            build_model(conn, "202504")
    except ValueError as error:
        assert "invalid count" in str(error)
    else:
        raise AssertionError("Invalid counts unexpectedly published")
    assert conn.execute("SELECT sum(headcount) FROM mart.workforce_monthly").fetchone()[0] == 4
    print("PASS invalid count blocks publish and preserves previous Mart state")
    check_lookup_states(conn)


def check_lookup_states(conn):
    cases = (
        (3, "   ", "EMPTY"),
        (4, " redacted ", "REDACTED"),
        (5, None, "NULL"),
        (6, "001", "MATCHED_DERIVED"),
        (7, " 001 ", "UNKNOWN"),
    )
    for relation in ("agency", "accession_category", "separation_category"):
        for code in ("001", " redacted "):
            conn.execute(
                "INSERT INTO ref.derived_lookup VALUES(%s,'202504',%s,'Fixture','DERIVED_LOOKUP','READY')",
                (relation, code),
            )
    for file_id, family in enumerate(("employment", "accessions", "separations"), 1):
        for ordinal, code, _ in cases:
            conn.execute(sql.SQL(
                "INSERT INTO {} VALUES(%s,%s,'202504',1,'202504','202503',%s,%s,%s,ARRAY[]::text[])"
            ).format(sql.Identifier("ods", f"ods_{family}_record")),
                (file_id, ordinal, code, code, code))
        conn.execute("UPDATE raw_meta.source_file SET row_count=7 WHERE file_id=%s", (file_id,))

    with conn.transaction():
        result = build_model(conn, "202504")
    for family, fact in (
        ("employment", "fact_employment_snapshot"),
        ("accessions", "fact_accessions"),
        ("separations", "fact_separations"),
    ):
        assert result["facts"][family]["rows"] == 7
        prefixes = ("agency",) if family == "employment" else ("agency", "category")
        for prefix in prefixes:
            actual = conn.execute(sql.SQL(
                "SELECT source_row_ordinal, {code}, {state}, {key} <> 0 "
                "FROM {fact} WHERE report_month_key=202504 AND source_row_ordinal>=3 ORDER BY 1"
            ).format(code=sql.Identifier(f"{prefix}_code"), state=sql.Identifier(f"{prefix}_lookup_state"),
                     key=sql.Identifier(f"{prefix}_key"), fact=sql.Identifier("dw", fact))).fetchall()
            assert actual == [(ordinal, code, state, state == "MATCHED_DERIVED")
                              for ordinal, code, state in cases], (fact, prefix, actual)
    print("PASS Fact lookup states preserve whitespace, leading zeros, row counts and key 0")


def check_label_review(conn):
    """REVIEW rows: TV2-reviewed wording differences load; HOLD/unreviewed stay Unknown."""
    fixture(conn)
    conn.execute("UPDATE ods.ods_employment_record SET agency_code = CASE source_row_ordinal "
                 "WHEN 1 THEN 'TR' ELSE 'HL' END WHERE report_month = '202505'")
    conn.execute(
        "INSERT INTO ref.derived_lookup VALUES "
        "('agency','202505','TR','DEPARTMENT OF TREASURY','DERIVED_LOOKUP','REVIEW'),"
        "('agency','202505','HL','HELD AGENCY','DERIVED_LOOKUP','REVIEW')"
    )
    conn.execute(
        "INSERT INTO ref.label_review VALUES "
        "('agency','202505','TR','ABBREVIATION','DEPARTMENT OF THE TREASURY'),"
        "('agency','202505','HL','HOLD_ORG_SCOPE','HELD AGENCY FULL NAME')"
    )
    with conn.transaction():
        result = build_model(conn, "202505")
    assert result["facts"]["employment"]["unknown_agency_rows"] == 1, result
    label, status = conn.execute(
        "SELECT agency_label, verification_status FROM dw.dim_agency "
        "WHERE month_key = 202505 AND agency_code = 'TR'").fetchone()
    assert (label, status) == ("DEPARTMENT OF THE TREASURY", "REVIEWED_TV2"), (label, status)
    assert conn.execute("SELECT count(*) FROM dw.dim_agency WHERE agency_code = 'HL'"
                        ).fetchone()[0] == 0
    assert conn.execute("SELECT verification_status FROM dw.dim_agency "
                        "WHERE month_key = 202505 AND agency_code = 'AA'").fetchone()[0] == "PARTIAL"
    print("PASS TV2-reviewed REVIEW agency loads with display label; HOLD stays Unknown")


def check_new_marts(conn):
    """Category Mart splits event totals (key 0 kept); K10 Mart carries TV2 audit + DW states."""
    fixture(conn)
    conn.execute("UPDATE ods.ods_accessions_record SET accession_category_code='ZZ' "
                 "WHERE report_month='202504' AND source_row_ordinal=2")
    conn.execute(
        "INSERT INTO audit.fk_lookup_coverage VALUES "
        "(1,'employment','e.parquet','sha','202504','agency_code','VERIFIED','COMPLETE',2,2,100),"
        "(2,'accessions','a.parquet','sha','202504','accession_category_code','PARTIAL','SAMPLE',2,NULL,NULL)"
    )
    with conn.transaction():
        result = build_model(conn, "202504")
    rows = dict(conn.execute(
        "SELECT category_key = 0, sum(events) FROM mart.personnel_flows_category_monthly "
        "WHERE month_key=202504 AND family='accessions' GROUP BY 1").fetchall())
    assert rows == {False: 1, True: 1}, rows
    assert result["marts"]["category_groups"] >= 3, result
    employment = conn.execute(
        "SELECT lookup_status, official_coverage_pct, dw_total_rows, dw_matched_rows, dw_unknown_rows "
        "FROM mart.dq_coverage_monthly WHERE month_key=202504 AND family='employment' "
        "AND lookup_field='agency_code'").fetchone()
    assert employment == ("VERIFIED", 100, 2, 1, 1), employment
    accessions = conn.execute(
        "SELECT official_matched_rows, official_coverage_pct, dw_matched_rows, dw_unknown_rows "
        "FROM mart.dq_coverage_monthly WHERE month_key=202504 AND family='accessions' "
        "AND lookup_field='accession_category_code'").fetchone()
    assert accessions == (None, None, 1, 1), accessions
    print("PASS category Mart keeps key 0 in totals; K10 Mart shows TV2 coverage and DW lookup states")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/.env")
    args = parser.parse_args()
    with temporary_database(args.config) as conn:
        check(conn)
    with temporary_database(args.config) as conn:
        check_label_review(conn)
    with temporary_database(args.config) as conn:
        check_new_marts(conn)
    print("PASS temporary database removed")


if __name__ == "__main__":
    main()
