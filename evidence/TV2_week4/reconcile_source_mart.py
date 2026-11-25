"""L2-14: reconcile the locked Parquet source with TV3's exported PostgreSQL Marts."""
import argparse
import csv
import hashlib
import io
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

import duckdb
import pyarrow.compute as pc
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "TV2_week2"))
from source_baseline import MONTHS, ROOT, TIME, make_inventory, paths, write_csv

TV3_REF = "3a1a6199df53cfa9ef5dbc556a146c844c378f87"
EXPORT = "reports/week3"
MEASURES = {
    "employment": ("K01", "snapshot", "snapshot_yyyymm", "headcount"),
    "accessions": ("K06", "report", TIME, "accessions"),
    "separations": ("K07", "report", TIME, "separations"),
}
SCOPES = ("ALL", "AF", "UNKNOWN")
CHECKS = {"mart_measure", "ods_fact_lineage_differences"}


def blob(path):
    return subprocess.check_output(["git", "show", f"{TV3_REF}:{path}"], cwd=ROOT)


def git_rows(path):
    return list(csv.DictReader(io.StringIO(blob(path).decode("utf-8-sig"), newline="")))


def verify_mart_inputs(inventory):
    run = json.loads(blob(f"{EXPORT}/run_manifest.json"))
    if run["status"] != "SUCCESS" or tuple(run["months"]) != MONTHS:
        raise ValueError("TV3 run manifest does not cover the full baseline")
    digests = {"docs/03_source_inventory.csv": run["inventory_sha256"], **run["code_sha256"]}
    for path, digest in digests.items():
        if hashlib.sha256(blob(path)).hexdigest() != digest:
            raise ValueError(f"TV3 run manifest hash mismatch: {path}")

    reported = git_rows(f"{EXPORT}/07_file_counts.csv")
    source_files = {(r["family"], r["report_month"], r["filename"], r["sha256"], r["row_count"])
                    for r in inventory}
    mart_files = {(r["family"], r["report_month"], r["filename"], r["sha256"], int(r["expected"]))
                  for r in reported}
    if len(reported) != len(source_files) or source_files != mart_files:
        raise ValueError("The TV3 run and the local source must use the same 12 Parquet files")
    if any(r["status"] != "PASS" or {r[k] for k in ("expected", "staging", "ods", "dw")} != {r["expected"]}
           for r in reported):
        raise ValueError("TV3 file-count evidence failed Source → Staging → ODS → Fact")


def from_duckdb(files, lookup):
    agency_counts, period_counts = Counter(), Counter()
    with duckdb.connect() as con:
        con.execute("CREATE TEMP TABLE lookup (report_month VARCHAR, code VARCHAR, label VARCHAR, load_status VARCHAR)")
        con.executemany("INSERT INTO lookup VALUES (?, ?, ?, ?)",
                        [(r["report_month"], r["code"], r["label"], r["load_status"]) for r in lookup])
        con.execute("""
            CREATE TEMP TABLE ready_agency AS
            SELECT report_month, code FROM lookup
            WHERE trim(code) <> '' AND code <> 'REDACTED'
            GROUP BY report_month, code
            HAVING count(*) = 1 AND bool_and(load_status = 'READY' AND trim(label) <> '')
        """)
        for (family, month), path in files.items():
            time_field = MEASURES[family][2]
            groups = con.execute(f"""
                SELECT coalesce(a.code, 'UNKNOWN') AS agency, p.{time_field} AS business_month,
                       count(*) AS records, count(*) FILTER (WHERE p."count" IS DISTINCT FROM '1') AS not_one
                FROM read_parquet(?) p
                LEFT JOIN ready_agency a ON a.report_month = ? AND a.code = p.agency_code
                GROUP BY 1, 2
            """, [str(path), month]).fetchall()
            for agency, business_month, records, invalid_count in groups:
                if invalid_count:
                    raise ValueError(f"{path.name} has {invalid_count} non-unit count values")
                if family == "employment" and business_month != month:
                    raise ValueError(f"{path.name} has a snapshot outside its baseline month")
                agency_counts[family, month, agency] += records
                period_counts[family, month, business_month] += records
    return agency_counts, period_counts


def from_pyarrow(files, lookup):
    """Independently count Parquet batches and resolve eligibility by raw string."""
    candidates = defaultdict(list)
    for row in lookup:
        candidates[row["report_month"], row["code"]].append(row)
    ready = {(month, code) for (month, code), found in candidates.items()
             if len(found) == 1 and code and code.strip(" ") and code != "REDACTED"
             and found[0]["load_status"] == "READY" and found[0]["label"].strip(" ")}

    agency_counts, period_counts = Counter(), Counter()
    for (family, month), path in files.items():
        time_field = MEASURES[family][2]
        for batch in pq.ParquetFile(path).iter_batches(columns=["agency_code", time_field, "count"]):
            count_states = pc.value_counts(batch.column("count")).to_pylist()
            if any(item["values"] != "1" for item in count_states):
                raise ValueError(f"PyArrow found a non-unit count in {path.name}")
            for item in pc.value_counts(batch.column("agency_code")).to_pylist():
                raw_code = item["values"]
                code = raw_code if (month, raw_code) in ready else "UNKNOWN"
                agency_counts[family, month, code] += item["counts"]
            for item in pc.value_counts(batch.column(time_field)).to_pylist():
                period_counts[family, month, item["values"]] += item["counts"]
    return agency_counts, period_counts


def index_rows(records, key_columns):
    indexed = {tuple(row[key] for key in key_columns): row for row in records}
    if len(indexed) != len(records):
        raise ValueError(f"Duplicate export key: {', '.join(key_columns)}")
    return indexed


def reconcile(monthly, detail, quality, j06, counts):
    reconciled, omissions = [], []
    reasons = {
        "ALL": "Same period role and all Agency groups, including Unknown",
        "AF": "Raw Agency AF maps to a unique READY label in each report month",
        "UNKNOWN": "Raw Agency has no unique READY mapping in the report month",
    }
    if set(monthly) != {(month,) for month in MONTHS} or {m for m, _ in detail} != set(MONTHS):
        raise ValueError("Monthly Mart export has unexpected months")
    for month in MONTHS:
        groups = {code: row for (period, code), row in detail.items() if period == month}
        for family, (kpi, role, _, column) in MEASURES.items():
            expected = {agency: value for (source, period, agency), value in counts.items()
                        if source == family and period == month}
            mart_total = int(monthly[month,][kpi.lower()])
            official = j06[family, month, "mart_measure"]
            lineage = j06[family, month, "ods_fact_lineage_differences"]
            if (official["status"], int(official["actual"])) != ("PASS", mart_total) or (
                lineage["status"], int(lineage["actual"])
            ) != ("PASS", 0):
                raise ValueError(f"TV3 J06 and Mart export disagree for {family}/{month}")
            for scope in SCOPES:
                source = sum(expected.values()) if scope == "ALL" else expected.get(scope, 0)
                mart = mart_total if scope == "ALL" else int(groups[scope][column])
                if scope == "UNKNOWN" and mart != int(quality[family, month]["unknown_agency_rows"]):
                    raise ValueError(f"TV3 Unknown reports disagree: {family}/{month}")
                reconciled.append(dict(report_month=month, period_role=role, kpi=kpi, agency_scope=scope,
                                       source_value=source, mart_value=mart, mart_minus_source=mart-source,
                                       status="PASS" if mart == source else "DIFF",
                                       reason=reasons[scope] if mart == source else "Unexplained difference to investigate"))
            for code, row in groups.items():
                if int(row[column]) != expected.get(code, 0):
                    raise ValueError(f"Published detail differs from source for {month}/{kpi}/{code}")
            missing = {code: value for code, value in expected.items() if code not in groups and value}
            if family == "employment" and missing:
                raise ValueError(f"Workforce detail omitted a source group in {month}")
            if sum(missing.values()) != mart_total - sum(int(r[column]) for r in groups.values()):
                raise ValueError(f"Unexplained difference between monthly total and detail export for {month}/{kpi}")
            for code, value in sorted(missing.items()):
                omissions.append(dict(report_month=month, kpi=kpi, agency_code=code, source_value=value,
                                      detail_export_presence="MISSING", omitted_rows=value,
                                      reason="TV3 detail CSV starts from workforce; this group exists only in event source"))
    return reconciled, omissions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw", type=Path, help="Baseline root containing the three family directories")
    args = parser.parse_args()

    files = paths(args.raw.resolve())
    inventory, _ = make_inventory(files)
    verify_mart_inputs(inventory)
    lookup = [row for row in git_rows("data/reference/derived_lookup_g2.csv") if row["relation"] == "agency"]
    source, periods = from_duckdb(files, lookup)
    if (source, periods) != from_pyarrow(files, lookup):
        raise ValueError("Independent PyArrow and DuckDB source counts differ")
    for item in inventory:
        family, month = item["family"], item["report_month"]
        rows = sum(value for (f, m, _), value in source.items() if (f, m) == (family, month))
        if rows != item["row_count"]:
            raise ValueError(f"Source regrouping changed row count for {item['filename']}")

    monthly = index_rows(git_rows(f"{EXPORT}/05_kpi_monthly.csv"), ("month_key",))
    detail = index_rows(git_rows(f"{EXPORT}/05_kpi_agency.csv"), ("month_key", "agency_code"))
    quality = index_rows(git_rows(f"{EXPORT}/09_source_quality.csv"), ("family", "report_month"))
    j06 = index_rows([r for r in git_rows(f"{EXPORT}/07_reconciliation.csv") if r["check"] in CHECKS],
                     ("family", "report_month", "check"))
    rows, omissions = reconcile(monthly, detail, quality, j06, source)

    for family in MEASURES:
        by_month = Counter()
        for (kind, report, business), value in periods.items():
            if kind == family and report != business:
                by_month[report] += value
        measured = {month: by_month[month] for month in MONTHS}
        if any(value != int(quality[family, month]["other_month"]) for month, value in measured.items()):
            raise ValueError(f"TV3 and source disagree on period exceptions for {family}")
        if family != "employment":
            effective = {month: sum(n for (kind, _, business), n in periods.items()
                                    if kind == family and business == month) for month in MONTHS}
            outside = {business: sum(n for (kind, _, observed), n in periods.items()
                                     if kind == family and observed == business)
                       for kind, _, business in periods if kind == family and business not in MONTHS}
            print(f"{family}: off-period by report month {measured}; effective totals {effective}; outside {outside}")
    write_csv(ROOT / "reports/TV2_l2_14_source_mart.csv", rows)
    if omissions:
        write_csv(ROOT / "reports/TV2_l2_14_mart_export_gaps.csv", omissions)
    print(f"DuckDB/PyArrow agree on {sum(source.values()):,} source rows from {len(files)} files")
    print(f"Reconciled {len(rows)} aligned metrics and explained {sum(r['source_value'] for r in omissions)} "
          f"rows omitted across {len(omissions)} agency/KPI export groups")
    for row in omissions:
        print(row["report_month"], row["kpi"], row["agency_code"], row["source_value"])
    if any(row["status"] != "PASS" for row in rows):
        raise ValueError("One or more aligned source/Mart comparisons differ")


if __name__ == "__main__":
    main()
