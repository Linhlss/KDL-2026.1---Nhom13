"""L3-14 (issue #54): run sql/08_dashboard_reference.sql and write the SQL side of the SQL–DAX check.

    python evidence/TV3_week4/build_sql_dax_reference.py --config configs/.env.g3.local --database <DB>
Outputs (read-only on the database):
  reports/week4/sql_reference/<BLOCK>.csv   full result of every named block
  reports/week4/sql_dax_reference.csv       sample filters TV4 must reproduce in DAX (dax_value empty)
"""
import argparse
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "etl"))
from g2_pipeline import connect, write_csv  # noqa: E402

SAMPLE_MONTHS = ("202503", "202504")
SAMPLE_AGENCIES = ("VA", "TR", "IN", "AF")
SAMPLE_CATEGORIES = (("accessions", "AC"), ("separations", "SC"))


def blocks():
    text = (ROOT / "sql/08_dashboard_reference.sql").read_text(encoding="utf-8")
    parts = re.split(r"^-- name: ([A-Z0-9_]+)\s*\n", text, flags=re.M)
    return {name: "\n".join(l for l in body.splitlines() if not l.lstrip().startswith("--")).strip().rstrip(";")
            for name, body in zip(parts[1::2], parts[2::2])}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/.env.g3.local")
    parser.add_argument("--database", required=True)
    args = parser.parse_args()
    out = ROOT / "reports/week4/sql_reference"
    out.mkdir(parents=True, exist_ok=True)
    results = {}
    with connect(args) as conn:
        conn.execute("SET default_transaction_read_only = on")
        for name, query in blocks().items():
            cur = conn.execute(query)
            cols = [c.name for c in cur.description]
            results[name] = [dict(zip(cols, r, strict=True)) for r in cur.fetchall()]
            write_csv(out / f"{name}.csv", results[name], cols)
    now = datetime.now(UTC).isoformat()
    ref = []

    def add(kpi, filters, value, block):
        ref.append(dict(kpi=kpi, filters=filters, sql_value="" if value is None else value,
                        dax_value="", status="PENDING_TV4", sql_block=block,
                        sql_file="sql/08_dashboard_reference.sql", tested_at=now))

    for r in results["K01_K02_K03_TOTAL"]:
        f = f"month={r['month_key']}; all agencies"
        add("K01", f, r["k01"], "K01_K02_K03_TOTAL")
        add("K02", f, r["k02"], "K01_K02_K03_TOTAL")
        add("K03", f, r["k03"], "K01_K02_K03_TOTAL")
    for r in results["K01_K02_K03_AGENCY"]:
        if str(r["month_key"]) in SAMPLE_MONTHS and r["agency_code"] in SAMPLE_AGENCIES:
            f = f"month={r['month_key']}; agency_code={r['agency_code']}"
            for k in ("k01", "k02", "k03"):
                add(k.upper(), f, r[k], "K01_K02_K03_AGENCY")
    for r in results["K04_AGENCY_SHARE"]:
        if str(r["month_key"]) == "202504" and r["agency_code"] in SAMPLE_AGENCIES:
            add("K04", f"month=202504; agency_code={r['agency_code']} (denominator ignores agency filter)",
                r["k04"], "K04_AGENCY_SHARE")
    for r in results["K06_K07_K08_TOTAL"]:
        f = f"month={r['month_key']}; all agencies"
        for k in ("k06", "k07", "k08"):
            add(k.upper(), f, r[k], "K06_K07_K08_TOTAL")
    for r in results["K06_K07_K08_AGENCY"]:
        if str(r["month_key"]) == "202504" and r["agency_code"] in SAMPLE_AGENCIES:
            f = f"month=202504; agency_code={r['agency_code']}"
            for k in ("k06", "k07", "k08"):
                add(k.upper(), f, r[k], "K06_K07_K08_AGENCY")
    for r in results["K06_K07_CATEGORY"]:
        if str(r["month_key"]) == "202504" and (r["family"], r["category_code"]) in SAMPLE_CATEGORIES:
            kpi = "K06" if r["family"] == "accessions" else "K07"
            add(kpi, f"month=202504; category={r['category_code']} {r['category_label']}", r["events"],
                "K06_K07_CATEGORY")
    for r in results["K10_COVERAGE"]:
        if r["k10"] is not None or (str(r["month_key"]) == "202504" and r["lookup_field"] == "agency_code"):
            add("K10", f"month={r['month_key']}; family={r['family']}; field={r['lookup_field']} "
                       f"[{r['lookup_status']}/{r['reference_coverage']}]", r["k10"], "K10_COVERAGE")
    for r in results["UNKNOWN_CHECK"]:
        add("UNKNOWN", r["item"], r["value"], "UNKNOWN_CHECK")
    write_csv(ROOT / "reports/week4/sql_dax_reference.csv", ref)
    print(f"Wrote {len(ref)} reference values and {len(results)} full SQL results")


if __name__ == "__main__":
    main()
