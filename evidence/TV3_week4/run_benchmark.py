"""L3-15 benchmark driver (issue #55): Fact vs Mart and before/after index, 3 measured runs each.

Run only against a separate benchmark database: B2 creates and finally drops two indexes.
    python evidence/TV3_week4/run_benchmark.py --config configs/.env.g3.local \
        --database workforce_dw_g3_bench --operator "TV3"
Outputs: reports/week4/benchmark_results.csv, evidence/TV3_week4/benchmark_explain_<variant>.txt
"""
import argparse
import json
import platform
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "etl"))
from g2_pipeline import connect, write_csv  # noqa: E402

RUNS = 3
INDEXES = {
    "B2-SEP": ("bench_sep_agency", "dw.fact_separations (agency_code, effective_month_key)"),
    "B2-EMP": ("bench_emp_agency", "dw.fact_employment_snapshot (agency_code, snapshot_month_key)"),
}


def queries():
    text = (ROOT / "sql/tests/09_benchmark.sql").read_text(encoding="utf-8")
    blocks = re.split(r"^-- name: ([A-Z0-9-]+)[^\n]*\n", text, flags=re.M)
    out = {}
    for name, body in zip(blocks[1::2], blocks[2::2]):
        out[name] = "\n".join(l for l in body.splitlines() if not l.lstrip().startswith("--")).strip().rstrip(";")
    return out


def plan_nodes(node):
    yield node
    for child in node.get("Plans", []):
        yield from plan_nodes(child)


def measure(conn, sql_text, variant, test_id, query_id, meta, explain_dir):
    conn.execute("EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) " + sql_text)  # warm-up, not recorded
    records = []
    for run in range(1, RUNS + 1):
        plan = conn.execute("EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) " + sql_text).fetchone()[0][0]
        top = plan["Plan"]
        scans = sorted({n["Node Type"] + (" on " + n["Relation Name"] if "Relation Name" in n else "")
                        for n in plan_nodes(top) if "Scan" in n["Node Type"]})
        records.append(dict(
            test_id=test_id, query=query_id, variant=variant, run=run,
            execution_ms=round(plan["Execution Time"], 3), planning_ms=round(plan["Planning Time"], 3),
            rows=top.get("Actual Rows"), buffers_hit=top.get("Shared Hit Blocks"),
            buffers_read=top.get("Shared Read Blocks"), plan_node_top=top["Node Type"],
            scans="; ".join(scans), **meta))
        if run == 1:
            text = conn.execute("EXPLAIN (ANALYZE, BUFFERS) " + sql_text).fetchall()
            (explain_dir / f"benchmark_explain_{query_id}_{variant}.txt").write_text(
                sql_text + "\n\n" + "\n".join(r[0] for r in text) + "\n", encoding="utf-8")
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/.env.g3.local")
    parser.add_argument("--database", required=True)
    parser.add_argument("--operator", default="TV3")
    args = parser.parse_args()
    q = queries()
    explain_dir = ROOT / "evidence/TV3_week4"
    out = ROOT / "reports/week4"
    out.mkdir(parents=True, exist_ok=True)
    with connect(args) as conn:
        settings = {k: conn.execute(f"SHOW {k}").fetchone()[0]
                    for k in ("server_version", "shared_buffers", "work_mem", "max_parallel_workers_per_gather")}
        try:
            cpu = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"], text=True).strip()
        except (OSError, subprocess.CalledProcessError):
            cpu = platform.processor()
        meta = dict(machine=f"{platform.system()} {platform.machine()} {cpu}",
                    pg_version=settings["server_version"],
                    pg_settings=";".join(f"{k}={v}" for k, v in settings.items() if k != "server_version"),
                    tested_at=datetime.now(UTC).isoformat(), operator=args.operator)
        differences = conn.execute(q["B1-CHECK"]).fetchone()[0]
        if differences:
            raise SystemExit(f"B1 FACT and MART results differ in {differences} rows; benchmark invalid")
        print("PASS B1 FACT and MART return identical agency totals (EXCEPT both ways = 0)")
        for name, _ in INDEXES.values():
            conn.execute(f"DROP INDEX IF EXISTS dw.{name}")
        conn.execute("ANALYZE dw.fact_employment_snapshot; ANALYZE dw.fact_separations; ANALYZE mart.workforce_monthly")
        records = []
        records += measure(conn, q["B1-FACT"], "FACT", "B1", "B1", meta, explain_dir)
        records += measure(conn, q["B1-MART"], "MART", "B1", "B1", meta, explain_dir)
        for query_id, (name, target) in INDEXES.items():
            before = conn.execute(q[query_id]).fetchall()
            records += measure(conn, q[query_id], "BEFORE", "B2", query_id, meta, explain_dir)
            conn.execute(f"CREATE INDEX {name} ON {target}")
            conn.execute(f"ANALYZE {target.split(' ')[0]}")
            records += measure(conn, q[query_id], "AFTER", "B2", query_id, meta, explain_dir)
            if sorted(conn.execute(q[query_id]).fetchall()) != sorted(before):
                raise SystemExit(f"{query_id} result changed after index")
            conn.execute(f"DROP INDEX dw.{name}")
    write_csv(out / "benchmark_results.csv", records)
    summary = {}
    for r in records:
        summary.setdefault((r["query"], r["variant"]), []).append(r["execution_ms"])
    for key, values in summary.items():
        print(f"{key[0]:7} {key[1]:6} median {median(values):10.3f} ms  runs {values}")
    (out / "benchmark_summary.json").write_text(json.dumps(
        {f"{k[0]}/{k[1]}": {"median_ms": median(v), "runs_ms": v} for k, v in summary.items()},
        indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
