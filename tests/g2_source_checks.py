"""Synthetic source-loader failures and rerun checks in a disposable database."""

import argparse
import hashlib
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

import psycopg
import pyarrow as pa
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "etl"))
from g2_pipeline import initialize, source_load
from g2_test_support import ROOT, temporary_database


def parquet_fixture(directory, family, invalid=False):
    filename = f"{family}_202504_v5.parquet"
    time = "snapshot_yyyymm" if family == "employment" else "personnel_action_effective_date_yyyymm"
    table = pa.table({
        "count": pa.array(["1", "1"], type=pa.string()),
        "agency_code": pa.array(["00A", "bad" + chr(0) if invalid else "00B"], type=pa.string()),
        "annualized_adjusted_basic_pay": pa.array([None, "REDACTED"], type=pa.string()),
        time: pa.array(["202504", "202503"], type=pa.string()),
    })
    path = directory / filename
    pq.write_table(table, path)
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    schema = "|".join(f"{field.name}:{field.type}" for field in table.schema)
    return {
        "family": family, "report_month": "202504", "version": "v5",
        "filename": filename, "sha256": digest,
        "schema_hash": hashlib.sha256(schema.encode()).hexdigest()[:16],
        "size_bytes": str(path.stat().st_size), "row_count": "2",
        "column_count": str(len(table.schema)), "source_url": "synthetic-regression-fixture",
    }


def preserved_source(conn, file_id):
    assert conn.execute(
        "SELECT count(*) FROM raw_meta.source_file WHERE file_id=%s AND status='LOADED'",
        (file_id,),
    ).fetchone()[0] == 1
    assert conn.execute(
        "SELECT count(*),min(source_row_ordinal),max(source_row_ordinal),"
        "count(*) FILTER(WHERE agency_code LIKE '00%%') "
        "FROM ods.ods_employment_record WHERE file_id=%s", (file_id,),
    ).fetchone() == (2, 1, 2, 2)


def expect_failure(conn, args, item, error_types):
    previous = conn.execute("SELECT count(*) FROM audit.load_run WHERE status='FAIL'").fetchone()[0]
    try:
        source_load(conn, args, item, "synthetic-source-regression")
    except error_types:
        pass
    else:
        raise AssertionError("Expected loader failure")
    assert conn.execute(
        "SELECT count(*) FROM audit.load_run WHERE status='FAIL'"
    ).fetchone()[0] > previous


def check(conn, directory):
    initialize(conn)
    args = SimpleNamespace(raw_dir=directory, batch_size=1)
    good = parquet_fixture(directory, "employment")
    source_load(conn, args, good, "synthetic-source-regression")
    file_id = conn.execute(
        "SELECT file_id FROM raw_meta.source_file WHERE family='employment'"
    ).fetchone()[0]
    preserved_source(conn, file_id)
    source_load(conn, args, good, "synthetic-source-regression")
    assert conn.execute("SELECT count(*) FROM raw_meta.source_file").fetchone()[0] == 1
    assert conn.execute("SELECT count(*) FROM audit.load_run WHERE status='SKIPPED'").fetchone()[0] == 2
    print("PASS identical source rerun skips J01/J02 without duplicating rows")

    missing = dict(good, family="separations", filename="separations_202504_v5.parquet")
    expect_failure(conn, args, missing, (FileNotFoundError,))
    preserved_source(conn, file_id)
    print("PASS missing file records FAIL and preserves another valid source")

    checksum_bad = dict(good, sha256="0" * 64)
    expect_failure(conn, args, checksum_bad, (ValueError,))
    preserved_source(conn, file_id)
    print("PASS checksum mismatch records FAIL and preserves the loaded source")

    invalid = parquet_fixture(directory, "accessions", invalid=True)
    expect_failure(conn, args, invalid, (psycopg.Error,))
    assert conn.execute(
        "SELECT count(*) FROM raw_meta.source_file WHERE family='accessions'"
    ).fetchone()[0] == 0
    assert conn.execute("SELECT count(*) FROM staging.accessions_record").fetchone()[0] == 0
    assert conn.execute("SELECT count(*) FROM ods.ods_accessions_record").fetchone()[0] == 0
    assert conn.execute(
        "SELECT count(*) FROM audit.load_run WHERE family='accessions' "
        "AND job IN ('J01','J02') AND status='FAIL'"
    ).fetchone()[0] == 2
    preserved_source(conn, file_id)
    print("PASS COPY failure rolls back metadata/Staging/ODS while both FAIL audit records survive")
    assert conn.execute(
        "SELECT count(*) FROM audit.load_run WHERE status='RUNNING'"
    ).fetchone()[0] == 0
    print("PASS no unfinished audit runs after handled failures")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/.env")
    args = parser.parse_args()
    with TemporaryDirectory(prefix="tv3_g2_source_") as path:
        with temporary_database(args.config) as conn:
            check(conn, Path(path))
    print("PASS temporary database and Parquet fixtures removed")


if __name__ == "__main__":
    main()
