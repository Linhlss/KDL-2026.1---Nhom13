"""Replay safety regressions in a disposable database; no real Parquet needed."""

import argparse
import csv
import hashlib
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "etl"))
sys.path.insert(0, str(ROOT / "evidence/TV3_week2"))
from g2_pipeline import FAMILIES, initialize, resolve_config, source_load
from g2_model import build_model
from g2_test_support import temporary_database
from reconcile_sources import preflight_sources


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def fixture(directory, family):
    time = "snapshot_yyyymm" if family == "employment" else "personnel_action_effective_date_yyyymm"
    table = pa.table({
        "count": pa.array(["1", "1"], type=pa.string()),
        "agency_code": pa.array([family + "A", family + "B"], type=pa.string()),
        "annualized_adjusted_basic_pay": pa.array([None, "REDACTED"], type=pa.string()),
        "occupational_series_code": pa.array(["0018", "0343"], type=pa.string()),
        time: pa.array(["202504", "202504" if family == "employment" else "202503"], type=pa.string()),
    })
    path = directory / f"{family}_202504_v5.parquet"
    pq.write_table(table, path)
    schema = "|".join(f"{field.name}:{field.type}" for field in table.schema)
    return dict(family=family, report_month="202504", version="v5", filename=path.name,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                schema_hash=hashlib.sha256(schema.encode()).hexdigest()[:16],
                size_bytes=str(path.stat().st_size), row_count="2", column_count=str(len(table.schema)),
                source_url="synthetic-replay-regression")


def write_inventory(path, records):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def expect_preflight_failure(args, error_type):
    try:
        preflight_sources(args)
    except error_type:
        return
    raise AssertionError("Incomplete or invalid direct-source input unexpectedly accepted")


def check_preflight(directory, config, inventory, records):
    args = SimpleNamespace(raw_dir=directory, config=config, inventory=inventory, month="202504")
    require(len(preflight_sources(args)) == 3, "Flat-directory preflight failed")
    for family in FAMILIES:
        (directory / family).mkdir()
        filename = f"{family}_202504_v5.parquet"
        (directory / filename).rename(directory / family / filename)
    require(len(preflight_sources(args)) == 3, "Family-directory preflight failed")
    print("PASS direct checker accepts all three verified files in flat and family directories")
    for month in ("202513", "202500", "20251", "000004", "202507"):
        args.month = month
        expect_preflight_failure(args, ValueError)
    args.month = "202504"
    for selected in (records[:1], records[:2], records + [records[0]]):
        write_inventory(inventory, selected)
        expect_preflight_failure(args, ValueError)
    write_inventory(inventory, records)
    missing = directory / FAMILIES[2] / records[2]["filename"]
    saved = missing.with_suffix(".saved")
    missing.rename(saved)
    expect_preflight_failure(args, FileNotFoundError)
    saved.rename(missing)
    bad = [dict(record) for record in records]
    bad[-1]["sha256"] = "0" * 64
    write_inventory(inventory, bad)
    expect_preflight_failure(args, ValueError)
    write_inventory(inventory, records)
    print("PASS direct checker rejects invalid/absent months, missing/duplicate families, missing file and checksum mismatch")


def check_configuration(directory):
    config = directory / "precedence.env"
    config.write_text("PGDATABASE=qa_from_config\nRAW_DATA_DIR=reviewer/raw\n", encoding="utf-8")
    args = resolve_config(SimpleNamespace(config=config, database=None, raw_dir=None))
    require(args.database == "qa_from_config" and args.raw_dir == Path("reviewer/raw"),
            "dotenv values did not override legacy defaults")
    args = resolve_config(SimpleNamespace(config=config, database="qa_cli", raw_dir=directory / "cli"))
    require(args.database == "qa_cli" and args.raw_dir == directory / "cli", "CLI did not override dotenv")
    config.write_text("PGDATABASE=\nRAW_DATA_DIR=\n", encoding="utf-8")
    args = resolve_config(SimpleNamespace(config=config, database=None, raw_dir=None))
    require(args.database == "workforce_dw" and args.raw_dir == ROOT / "data/raw", "Legacy defaults changed")
    print("PASS CLI > dotenv > legacy database/raw-directory defaults")


def run_script(script, *args, expected=0, optimized=False):
    command = [sys.executable]
    if optimized:
        command.append("-O")
    result = subprocess.run([*command, str(ROOT / script), *map(str, args)], cwd=ROOT,
                            capture_output=True, text=True)
    require(result.returncode == expected,
            f"{script} returned {result.returncode}, expected {expected}: {result.stdout} {result.stderr}")
    if expected:
        require("crosscheck passed" not in result.stdout and "Completed check" not in result.stdout,
                "Failure output contained a success summary")
    return result


def check_database(conn, config, directory, inventory, records):
    initialize(conn)
    database = conn.info.dbname
    report_dir = directory / "reviewer_reports"
    handed_off = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in (ROOT / "reports").glob("*")
                  if path.is_file()}
    pipeline_args = ("--config", config, "--database", database, "--report-dir", report_dir, "--job", "check")

    def check_j06(loaded, expected):
        run_script("etl/g2_pipeline.py", *pipeline_args, expected=expected)
        audit = conn.execute("SELECT status,error FROM audit.load_run WHERE job='J06' "
                             "ORDER BY started_at DESC LIMIT 1").fetchone()
        require(audit[0] == ("FAIL" if expected else "SUCCESS"), "J06 audit status incorrect")
        with (report_dir / "07_reconciliation.csv").open(newline="", encoding="utf-8") as stream:
            report = list(csv.DictReader(stream))
        coverage = [row for row in report if row["check"] == "active_loaded_sources"]
        require(len(coverage) == 3, "Expected coverage evidence for all three families")
        require(sum(int(row["actual"]) for row in coverage) == loaded, "Source coverage count incorrect")
        require(any(row["status"] == "FAIL" for row in report) == bool(expected), "Reconciliation verdict incorrect")

    check_j06(0, 1)
    args = SimpleNamespace(raw_dir=directory, batch_size=1)
    for number, record in enumerate(records, 1):
        source_load(conn, args, record, "synthetic-replay-regression")
        if number < 3:
            check_j06(number, 1)
    print("PASS J06 rejects zero, one and two LOADED families, exports FAIL coverage and records audit FAIL")
    check_j06(3, 1)
    print("PASS complete source coverage alone cannot pass missing Fact/Mart reconciliation")
    with conn.transaction():
        build_model(conn, "202504")
    check_j06(3, 0)
    conn.execute("UPDATE mart.workforce_monthly SET headcount=headcount+1")
    check_j06(3, 1)
    conn.execute("UPDATE mart.workforce_monthly SET headcount=headcount-1")
    conn.execute("UPDATE raw_meta.source_file SET status='REGISTERED' WHERE family='separations'")
    check_j06(2, 1)
    conn.execute("UPDATE raw_meta.source_file SET status='LOADED',is_active=false WHERE family='separations'")
    check_j06(2, 1)
    conn.execute("UPDATE raw_meta.source_file SET is_active=true WHERE family='separations'")
    check_j06(3, 0)
    print("PASS J06 passes only complete matching layers and excludes inactive/unloaded sources")
    absent = run_script("etl/g2_pipeline.py", *pipeline_args, "--month", "202505", expected=1)
    require("FAIL" in absent.stderr, "Absent month did not fail")
    print("PASS J06 valid inventory month without loaded data fails with audit evidence")

    direct_args = ("--config", config, "--database", database, "--raw-dir", directory, "--inventory", inventory)
    result = run_script("evidence/TV3_week2/reconcile_sources.py", *direct_args)
    require(result.stdout.count("PASS ") == 3, "Direct checker did not compare all three families")
    run_script("evidence/TV3_week2/reconcile_sources.py", *direct_args, "--month", "202507", expected=1)
    run_script("evidence/TV3_week2/reconcile_sources.py", *direct_args, "--month", "202513", expected=2)
    conn.execute("UPDATE ods.ods_employment_record SET pay_state='VALUE' WHERE source_row_ordinal=1")
    failed = run_script("evidence/TV3_week2/reconcile_sources.py", *direct_args, expected=1, optimized=True)
    require("Parquet/ODS mismatch" in failed.stderr, "Optimized Python skipped mismatch validation")
    print("PASS source-direct compares all three inputs, rejects absent/invalid months and fails mismatches under python -O")
    require(all(hashlib.sha256(path.read_bytes()).hexdigest() == digest for path, digest in handed_off.items()),
            "Replay modified handed-off reports")
    require((report_dir / "07_load_log.csv").is_file(), "Local audit export missing")
    require(conn.execute("SELECT count(*) FROM audit.load_run WHERE status='RUNNING'").fetchone()[0] == 0,
            "Unfinished audit runs after replay checks")
    print("PASS --report-dir keeps reviewer outputs separate and handed-off report hashes unchanged")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/.env")
    args = parser.parse_args()
    with TemporaryDirectory(prefix="tv3_g2_replay_") as temporary:
        directory = Path(temporary)
        inventory = directory / "inventory.csv"
        records = [fixture(directory, family) for family in FAMILIES]
        write_inventory(inventory, records)
        check_configuration(directory)
        check_preflight(directory, args.config, inventory, records)
        with temporary_database(args.config) as conn:
            check_database(conn, args.config.resolve(), directory, inventory, records)
    print("PASS disposable database, Parquet fixtures and reviewer reports removed")


if __name__ == "__main__":
    main()
