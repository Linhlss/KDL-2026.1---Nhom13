import sys, hashlib, csv, re, pathlib
import pyarrow.parquet as pq, pyarrow.compute as pc
base = pathlib.Path(sys.argv[1]); out = sys.argv[2]
rows=[]
for f in sorted(base.glob("*/*.parquet")):
    m = re.match(r"(\w+)_(\d{6})_v(\d+)\.parquet", f.name)
    fam, month, ver = m.groups()
    h = hashlib.sha256(f.read_bytes()).hexdigest()
    pf = pq.ParquetFile(f)
    schema = pf.schema_arrow
    sh = hashlib.sha256("|".join(f"{n}:{t}" for n,t in zip(schema.names, schema.types)).encode()).hexdigest()[:16]
    timecol = "snapshot_yyyymm" if fam=="employment" else "personnel_action_effective_date_yyyymm"
    t = pq.read_table(f, columns=["count", timecol])
    cnt_vals = sorted(set(pc.unique(t["count"]).to_pylist()), key=str)
    mism = pc.sum(pc.not_equal(t[timecol].cast("string"), month)).as_py() or 0
    rows.append(dict(family=fam, report_month=month, version="v"+ver, filename=f.name,
        size_bytes=f.stat().st_size, row_count=pf.metadata.num_rows, column_count=len(schema.names),
        schema_hash16=sh, sha256=h, count_distinct_values=";".join(map(str,cnt_vals[:5])),
        time_field=timecol, rows_time_field_ne_file_month=mism))
with open(out,"w",newline="") as fh:
    w=csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for r in rows: print(r["filename"], r["row_count"], r["column_count"], r["count_distinct_values"], r["rows_time_field_ne_file_month"])
print("TOTAL rows", sum(r["row_count"] for r in rows), "files", len(rows))
for fam in ("employment","accessions","separations"):
    print(fam, sum(r["row_count"] for r in rows if r["family"]==fam), "mismatch", sum(r["rows_time_field_ne_file_month"] for r in rows if r["family"]==fam))
