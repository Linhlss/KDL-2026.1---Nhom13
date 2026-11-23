"""Manifest-driven G2 loader. Source data and logs are committed per file."""
import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

import psycopg
import pyarrow as pa
import pyarrow.parquet as pq
from dotenv import dotenv_values
from psycopg import sql

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = ("employment", "accessions", "separations")
ODS = {family: f"ods_{family}_record" for family in FAMILIES}
DEFAULT_REPORT_DIR = ROOT / "reports"


def validate_month(month):
    if not re.fullmatch(r"[0-9]{4}(0[1-9]|1[0-2])", month) or int(month[:4]) == 0:
        raise ValueError("month must be a valid YYYYMM value")
    return month


def selected_sources(inventory, month):
    validate_month(month)
    selected = [item for item in inventory if item["report_month"] == month]
    if sorted(item["family"] for item in selected) != sorted(FAMILIES):
        raise ValueError("inventory must contain exactly one file for each family in the selected month")
    return selected


def resolve_config(args):
    """Resolve CLI > .env > legacy defaults; relative paths use the working directory."""
    config = dotenv_values(args.config, interpolate=False)
    if args.database is None:
        args.database = config.get("PGDATABASE") or "workforce_dw"
    if args.raw_dir is None:
        args.raw_dir = Path(config["RAW_DATA_DIR"]) if config.get("RAW_DATA_DIR") else ROOT / "data/raw"
    return args


def rows(path):
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, records, fields=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields or list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def connect(args):
    config = dotenv_values(args.config, interpolate=False)
    settings = {key[2:].lower(): config[key] for key in
                ("PGHOST", "PGPORT", "PGUSER", "PGPASSWORD") if config.get(key)}
    database = getattr(args, "database", None)
    if database is None:
        database = config.get("PGDATABASE") or "workforce_dw"
    return psycopg.connect(dbname=database, connect_timeout=5, autocommit=True, **settings)


def apply_sql(conn, path):
    content = "\n".join(line for line in path.read_text().splitlines()
                        if not line.startswith("\\"))
    conn.execute(content)


def coverage_snapshot_rows(inventory, audit):
    files = {f"{item['family']}/{item['report_month']}": item for item in inventory}
    output = []
    for result in audit:
        file = files.get(result["scope"])
        if file is None:
            continue
        source_sha256 = result.get("source_sha256")
        if source_sha256 != file["sha256"]:
            raise ValueError(f"K10 audit SHA-256 disagrees with inventory for {file['filename']}")
        if int(result["tested_rows"]) != int(file["row_count"]):
            raise ValueError(f"K10 audit row count disagrees with inventory for {file['filename']}")
        eligible = int(result["eligible_rows"])
        coverage = result["reference_coverage"]
        matched = None
        if coverage == "COMPLETE":
            if int(result["reference_eligible_rows"]) != eligible:
                raise ValueError(f"K10 audit denominator disagrees for {result['key_columns']} in {file['filename']}")
            matched = int(result["reference_unique_matches"])
        output.append((
            file["family"], file["report_month"], file["filename"], source_sha256,
            result["key_columns"], result["status"], coverage, eligible, matched,
        ))
    return output


def initialize(conn):
    for name in ("01_create_schemas.sql", "00_raw_ref_ods_ddl.sql",
                 "03_dw_ddl.sql", "04_create_marts.sql"):
        apply_sql(conn, ROOT / "sql" / name)
    # Snapshot the handed-off TV2 reference without claiming official coverage.
    lookup = rows(ROOT / "data/reference/derived_lookup_g2.csv")
    coverage = coverage_snapshot_rows(
        rows(ROOT / "docs/03_source_inventory.csv"), rows(ROOT / "docs/04_relationship_audit.csv")
    )
    with conn.transaction():
        conn.execute("LOCK TABLE ref.derived_lookup IN EXCLUSIVE MODE")
        conn.execute("DELETE FROM ref.derived_lookup")
        columns = list(lookup[0])
        with conn.cursor().copy(sql.SQL("COPY ref.derived_lookup ({}) FROM STDIN").format(
            sql.SQL(",").join(map(sql.Identifier, columns))
        )) as copy:
            for row in lookup:
                copy.write_row([row[column] for column in columns])
        conn.execute("DELETE FROM audit.lookup_coverage_snapshot")
        with conn.cursor().copy(
            "COPY audit.lookup_coverage_snapshot "
            "(family, report_month, source_file, source_sha256, lookup_field, lookup_status, "
            "reference_coverage, eligible_rows, matched_rows) FROM STDIN"
        ) as copy:
            for row in coverage:
                copy.write_row(row)


def start_run(conn, job, file, code_version):
    run_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO audit.load_run
        (run_id,job,family,report_month,version,filename,sha256,expected_rows,status,started_at,code_version)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'RUNNING',now(),%s)""",
        (run_id, job, file["family"], file["report_month"], file["version"], file["filename"],
         file["sha256"], int(file["row_count"]), code_version),
    )
    return run_id


def finish_run(conn, run_id, status, start, actual=None, file_id=None, error=None):
    conn.execute(
        """UPDATE audit.load_run SET status=%s, actual_rows=%s, file_id=%s, error=%s,
        duration_seconds=%s, finished_at=now() WHERE run_id=%s""",
        (status, actual, file_id, error, round(perf_counter() - start, 6), run_id),
    )


def safe_error(error):
    if isinstance(error, psycopg.Error):
        return f"{type(error).__name__} SQLSTATE {error.sqlstate or 'n/a'}"
    if isinstance(error, ValueError):
        return str(error)
    return type(error).__name__


def verify_file(path, item):
    expected_name = f"{item['family']}_{item['report_month']}_{item['version']}.parquet"
    if item["family"] not in FAMILIES or item["filename"] != expected_name:
        raise ValueError("Filename must match manifest family, report month and version")
    with path.open("rb") as stream:
        sha = hashlib.file_digest(stream, "sha256").hexdigest()
    if sha != item["sha256"]:
        raise ValueError(f"SHA-256 mismatch: {item['filename']}")
    pf = pq.ParquetFile(path)
    schema_text = "|".join(f"{field.name}:{field.type}" for field in pf.schema_arrow)
    actual = {
        "size_bytes": path.stat().st_size, "row_count": pf.metadata.num_rows,
        "column_count": len(pf.schema_arrow),
        "schema_hash": hashlib.sha256(schema_text.encode()).hexdigest()[:16],
    }
    for key, value in actual.items():
        if str(value) != item[key]:
            raise ValueError(f"{key} mismatch: {item['filename']}")
    if any(not pa.types.is_string(field.type) for field in pf.schema_arrow):
        raise ValueError("Baseline schema must contain text fields")
    return pf


def transform(conn, item, file_id, run_id):
    family = item["family"]
    time_col = "snapshot_yyyymm" if family == "employment" else "personnel_action_effective_date_yyyymm"
    names = [field[0] for field in conn.execute(
        """SELECT column_name FROM information_schema.columns
        WHERE table_schema='staging' AND table_name=%s
        AND column_name NOT IN ('file_id','source_row_ordinal') ORDER BY ordinal_position""",
        (f"{family}_record",),
    )]
    raw_columns = sql.SQL(",").join(map(sql.Identifier, ["file_id", "source_row_ordinal", *names]))
    target_columns = sql.SQL(",").join(map(sql.Identifier, [
        "file_id", "source_row_ordinal", *names, "report_month",
        "count_value", "effective_month", "pay_value", "pay_state", "dq_flags",
    ]))
    query = sql.SQL("""
    INSERT INTO ods.{target} ({target_columns})
    SELECT {raw}, %s,
      CASE WHEN pg_input_is_valid("count",'bigint') THEN "count"::bigint END,
      {effective},
      CASE WHEN pg_input_is_valid(annualized_adjusted_basic_pay,'numeric')
           THEN annualized_adjusted_basic_pay::numeric END,
      CASE WHEN annualized_adjusted_basic_pay IS NULL THEN 'NULL'
           WHEN btrim(annualized_adjusted_basic_pay)='' THEN 'EMPTY'
           WHEN upper(btrim(annualized_adjusted_basic_pay))='REDACTED' THEN 'REDACTED'
           WHEN pg_input_is_valid(annualized_adjusted_basic_pay,'numeric') THEN 'VALUE'
           ELSE 'INVALID' END,
      array_remove(ARRAY[
        CASE WHEN "count" IS DISTINCT FROM '1' THEN 'COUNT_NOT_ONE' END,
        CASE WHEN {time} IS NULL OR {time} !~ '^[0-9]{{4}}(0[1-9]|1[0-2])$'
             THEN 'INVALID_MONTH' END,
        CASE WHEN {time} <> %s THEN 'TIME_DIFFERS_FROM_REPORT' END,
        CASE WHEN annualized_adjusted_basic_pay IS NULL THEN 'PAY_NULL'
             WHEN btrim(annualized_adjusted_basic_pay)='' THEN 'PAY_EMPTY'
             WHEN upper(btrim(annualized_adjusted_basic_pay))='REDACTED' THEN 'PAY_REDACTED'
             WHEN NOT pg_input_is_valid(annualized_adjusted_basic_pay,'numeric') THEN 'PAY_INVALID' END
      ], NULL)
    FROM staging.{source} WHERE file_id=%s
    """).format(
        target=sql.Identifier(ODS[family]), target_columns=target_columns, raw=raw_columns,
        effective=sql.Identifier(time_col) if family != "employment" else sql.SQL("NULL::text"),
        time=sql.Identifier(time_col), source=sql.Identifier(f"{family}_record"),
    )
    conn.execute(query, (item["report_month"], item["report_month"], file_id))
    conn.execute(sql.SQL("""
    INSERT INTO audit.dq_issue(run_id,file_id,column_name,rule_id,details,affected_rows)
    SELECT %s,file_id,
       CASE WHEN flag LIKE 'PAY_%%' THEN 'annualized_adjusted_basic_pay'
            WHEN flag='COUNT_NOT_ONE' THEN 'count' ELSE %s END,
       flag,'Preserved raw row; see ODS raw fields and dq_flags',count(*)
    FROM ods.{table} CROSS JOIN LATERAL unnest(dq_flags) AS flag
    WHERE file_id=%s GROUP BY file_id,flag
    """).format(table=sql.Identifier(ODS[family])), (run_id, time_col, file_id))


def source_load(conn, args, item, code_version):
    start = perf_counter()
    scan_id = start_run(conn, "J00", item, code_version)
    try:
        path = args.raw_dir / item["filename"]
        if not path.exists():
            path = args.raw_dir / item["family"] / item["filename"]
        pf = verify_file(path, item)
        finish_run(conn, scan_id, "SUCCESS", start, int(item["row_count"]))
    except Exception as error:
        finish_run(conn, scan_id, "FAIL", start, error=safe_error(error))
        raise
    run_ids = [start_run(conn, job, item, code_version) for job in ("J01", "J02")]
    file_id = None
    try:
        with conn.transaction():
            conn.execute("SELECT pg_advisory_xact_lock(hashtext(%s))",
                         (f"{item['family']}/{item['report_month']}",))
            existing = conn.execute(
                """SELECT file_id,sha256,filename,status,family,report_month,version,
                          schema_hash,size_bytes,row_count,column_count,is_active
                FROM raw_meta.source_file
                WHERE (family=%s AND report_month=%s) OR filename=%s OR sha256=%s""",
                (item["family"], item["report_month"], item["filename"], item["sha256"]),
            ).fetchall()
            skipped = bool(existing)
            if existing:
                if len(existing) != 1 or existing[0][1:3] != (item["sha256"], item["filename"]):
                    raise ValueError("Source identity/version conflict; explicit version decision required")
                file_id, _, _, status, *identity = existing[0]
                expected_identity = [item["family"],item["report_month"],item["version"],
                                     item["schema_hash"],int(item["size_bytes"]),
                                     int(item["row_count"]),int(item["column_count"]),True]
                if identity != expected_identity:
                    raise ValueError("Registered source metadata disagrees with the manifest")
                if status != "LOADED":
                    raise ValueError("Existing source is not LOADED; investigate before retry")
            else:
                fields = ["family", "report_month", "version", "filename", "sha256",
                          "schema_hash", "size_bytes", "row_count", "column_count", "source_url"]
                file_id = conn.execute(sql.SQL(
                    "INSERT INTO raw_meta.source_file ({}) VALUES ({}) RETURNING file_id"
                ).format(sql.SQL(",").join(map(sql.Identifier, fields)),
                         sql.SQL(",").join(sql.Placeholder() for _ in fields)),
                    [item[key] for key in fields]).fetchone()[0]
                statement = sql.SQL("COPY staging.{} ({}) FROM STDIN").format(
                    sql.Identifier(f"{item['family']}_record"),
                    sql.SQL(",").join(map(sql.Identifier, ["file_id", "source_row_ordinal", *pf.schema_arrow.names])),
                )
                ordinal = 0
                with conn.cursor().copy(statement) as writer:
                    for batch in pf.iter_batches(batch_size=args.batch_size, use_threads=False):
                        columns = [column.to_pylist() for column in batch.columns]
                        for values in zip(*columns, strict=True):
                            ordinal += 1
                            writer.write_row((file_id, ordinal, *values))
                # Detect source replacement/mutation while iterating, before commit.
                verify_file(path, item)
                transform(conn, item, file_id, run_ids[1])
                conn.execute("UPDATE raw_meta.source_file SET status='LOADED',loaded_at=now() WHERE file_id=%s",
                             (file_id,))
            expected = int(item["row_count"])
            for schema, table in (("staging", f"{item['family']}_record"), ("ods", ODS[item["family"]])):
                result = conn.execute(sql.SQL(
                    "SELECT count(*),count(DISTINCT source_row_ordinal),min(source_row_ordinal),max(source_row_ordinal)"
                    " FROM {}.{} WHERE file_id=%s"
                ).format(sql.Identifier(schema), sql.Identifier(table)), (file_id,)).fetchone()
                if result != (expected, expected, 1, expected):
                    raise ValueError(f"Row/ordinal reconciliation failed in {schema}.{table}")
        for run_id in run_ids:
            finish_run(conn, run_id, "SKIPPED" if skipped else "SUCCESS", start, expected, file_id)
        print(f"{'SKIPPED' if skipped else 'SUCCESS'} {item['filename']} {expected} rows")
    except Exception as error:
        # Failure evidence survives the rolled-back data transaction.
        for run_id in run_ids:
            finish_run(conn, run_id, "FAIL", start, error=safe_error(error))
        raise


def export_logs(conn, report_dir=DEFAULT_REPORT_DIR):
    columns = ["run_id", "job", "family", "report_month", "version", "filename",
               "file_id", "sha256", "expected_rows", "actual_rows", "status",
               "duration_seconds", "error", "started_at", "finished_at", "code_version"]
    with conn.cursor() as cur:
        cur.execute("SELECT " + ",".join(columns) + " FROM audit.load_run ORDER BY started_at,run_id")
        records = [dict(zip(columns, row, strict=True)) for row in cur.fetchall()]
    write_csv(report_dir / "07_load_log.csv", records, columns)


def before_after(conn, month, report_dir=DEFAULT_REPORT_DIR):
    output = []
    for family in FAMILIES:
        table = sql.Identifier("ods", ODS[family])
        records = conn.execute(sql.SQL("""
          SELECT o.file_id,count(*),count(*) FILTER (WHERE count_value IS NULL OR count_value<>1),
          count(*) FILTER (WHERE pay_state='NULL'),count(*) FILTER (WHERE pay_state='EMPTY'),
          count(*) FILTER (WHERE pay_state='REDACTED'),count(*) FILTER (WHERE pay_state='INVALID'),
          count(*) FILTER (WHERE 'TIME_DIFFERS_FROM_REPORT'=ANY(dq_flags))
          FROM {table} o JOIN raw_meta.source_file f USING(file_id)
          WHERE f.report_month=%s AND f.is_active GROUP BY o.file_id
        """).format(table=table), (month,)).fetchall()
        for file_id, n, count_bad, nulls, empty, redacted, invalid, mismatch in records:
            for rule, column, before, after, affected in [
                ("DQ01","count","raw text","validated bigint; raw retained",n),
                ("DQ02","annualized_adjusted_basic_pay","raw text","numeric plus raw/state",nulls+empty+redacted+invalid),
                ("DQ04","business_month","raw source month","report and business month retained",mismatch),
            ]:
                output.append(dict(file_id=file_id,family=family,report_month=month,column=column,rule=rule,
                                   before=before,after=after,affected_rows=affected,before_rows=n,after_rows=n,
                                   invalid_count=count_bad,pay_null=nulls,pay_empty=empty,pay_redacted=redacted,
                                   pay_invalid=invalid,reviewer="PENDING TV5"))
            fact = "fact_employment_snapshot" if family == "employment" else f"fact_{family}"
            unknown, fact_rows = conn.execute(sql.SQL(
                "SELECT count(*) FILTER (WHERE agency_key=0),count(*) FROM dw.{} WHERE file_id=%s"
            ).format(sql.Identifier(fact)), (file_id,)).fetchone()
            if fact_rows == n:
                output.append(dict(file_id=file_id,family=family,report_month=month,column="agency_code",
                                   rule="DQ03",before="raw agency code",after="derived lookup key or Unknown; raw retained",
                                   affected_rows=unknown,before_rows=n,after_rows=fact_rows,
                                   invalid_count=count_bad,pay_null=nulls,pay_empty=empty,pay_redacted=redacted,
                                   pay_invalid=invalid,reviewer="PENDING TV4/TV5"))
    if output:
        write_csv(report_dir / "07_before_after.csv", output)


def reconciliation(conn, month, report_dir=DEFAULT_REPORT_DIR):
    validate_month(month)
    result = []
    sources = {}
    fields = ["family","report_month","file_id","check","expected","actual","status","reviewer"]
    for family in FAMILIES:
        sources[family] = conn.execute(
            "SELECT file_id,row_count FROM raw_meta.source_file "
            "WHERE family=%s AND report_month=%s AND is_active AND status='LOADED'",
            (family, month),
        ).fetchall()
        actual = len(sources[family])
        result.append(dict(family=family,report_month=month,
                           file_id=sources[family][0][0] if actual == 1 else "",
                           check="active_loaded_sources",expected=1,actual=actual,
                           status="PASS" if actual == 1 else "FAIL",reviewer="TV3; PENDING TV5"))
    if any(record["status"] == "FAIL" for record in result):
        write_csv(report_dir / "07_reconciliation.csv", result, fields)
        raise ValueError("Reconciliation requires exactly one active LOADED source for each family")
    for family in FAMILIES:
        fact = "fact_employment_snapshot" if family == "employment" else f"fact_{family}"
        for file_id, expected in sources[family]:
            for layer, table in [("staging", f"{family}_record"), ("ods", ODS[family]), ("dw", fact)]:
                count = conn.execute(sql.SQL("SELECT count(*) FROM {}.{} WHERE file_id=%s").format(
                    sql.Identifier(layer), sql.Identifier(table)), (file_id,)).fetchone()[0]
                result.append(dict(family=family,report_month=month,file_id=file_id,
                                   check=f"{layer}_rows",expected=expected,actual=count,
                                   status="PASS" if count==expected else "FAIL",reviewer="TV3; PENDING TV5"))
            missing = conn.execute(sql.SQL("""
                SELECT count(*) FROM (
                 (SELECT file_id,source_row_ordinal FROM ods.{ods} WHERE file_id=%s
                  EXCEPT SELECT file_id,source_row_ordinal FROM dw.{fact} WHERE file_id=%s)
                 UNION ALL
                 (SELECT file_id,source_row_ordinal FROM dw.{fact} WHERE file_id=%s
                  EXCEPT SELECT file_id,source_row_ordinal FROM ods.{ods} WHERE file_id=%s)
                ) differences
            """).format(ods=sql.Identifier(ODS[family]), fact=sql.Identifier(fact)), (file_id,)*4).fetchone()[0]
            result.append(dict(family=family,report_month=month,file_id=file_id,check="ods_fact_lineage_differences",
                               expected=0,actual=missing,status="PASS" if missing==0 else "FAIL",reviewer="TV3; PENDING TV5"))
            field = {"employment":"headcount","accessions":"accessions","separations":"separations"}[family]
            mart = "workforce_monthly" if family == "employment" else "personnel_flows_monthly"
            measure = conn.execute(sql.SQL(
                "SELECT coalesce(sum(count_value),0) FROM dw.{} WHERE file_id=%s"
            ).format(sql.Identifier(fact)), (file_id,)).fetchone()[0]
            actual = conn.execute(sql.SQL(
                "SELECT coalesce(sum({}),0) FROM mart.{} WHERE month_key=%s"
            ).format(sql.Identifier(field),sql.Identifier(mart)), (int(month),)).fetchone()[0]
            for check, value in (("fact_measure",measure),("mart_measure",actual)):
                result.append(dict(family=family,report_month=month,file_id=file_id,check=check,
                                   expected=expected,actual=int(value),
                                   status="PASS" if value==expected else "FAIL",reviewer="TV3; PENDING TV5"))
            result.append(dict(family=family,report_month=month,file_id=file_id,check="powerbi_dax",
                               expected=expected,actual="",status="PENDING",reviewer="PENDING TV4/TV5"))
    write_csv(report_dir / "07_reconciliation.csv", result, fields)
    if any(record["status"] == "FAIL" for record in result):
        raise ValueError("Source/ODS/Fact reconciliation failed")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT/"configs/.env")
    parser.add_argument("--database", help="database override; otherwise PGDATABASE from config or workforce_dw")
    parser.add_argument("--month", default="202504")
    parser.add_argument("--raw-dir", type=Path, help="source directory override; otherwise RAW_DATA_DIR from config or data/raw")
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR,
                        help="CSV output directory (default: repository reports)")
    parser.add_argument("--inventory", type=Path, default=ROOT/"docs/03_source_inventory.csv")
    parser.add_argument("--batch-size", type=int, default=10000)
    parser.add_argument("--job", choices=("init","source","model","check","all"), default="all")
    args = parser.parse_args()
    try:
        validate_month(args.month)
    except ValueError as error:
        parser.error(str(error))
    if args.batch_size < 1:
        parser.error("positive batch-size required")
    if not args.config.is_file():
        parser.error("config file missing")
    resolve_config(args)
    code_version = subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    if subprocess.check_output(
        ["git","status","--porcelain","--untracked-files=all","--",
         "etl","sql","requirements.txt","configs/.env.example"],cwd=ROOT,text=True
    ):
        code_version += "+working-tree"
    manifest = dict(line.strip().split(None,1)[::-1] for line in
                    (ROOT/"data/manifest/sha256.txt").read_text().splitlines() if line.strip())
    inventory = rows(args.inventory)
    try:
        selected = selected_sources(inventory, args.month)
    except ValueError as error:
        parser.error(str(error))
    if len({item["filename"] for item in inventory}) != len(inventory):
        parser.error("duplicate inventory filename")
    for item in inventory:
        if manifest.get(item["filename"]) != item["sha256"]:
            parser.error("inventory and TV2 SHA manifest disagree")
    try:
        with connect(args) as conn:
            try:
                if args.job in ("init","all"):
                    initialize(conn)
                if args.job in ("source","all"):
                    for item in selected:
                        source_load(conn,args,item,code_version)
                    before_after(conn,args.month,args.report_dir)
                if args.job in ("model","all"):
                    from g2_model import build_model
                    start = perf_counter()
                    meta = dict(family="employment",report_month=args.month,version="model",
                                filename="G2_MODEL",sha256="",row_count="0")
                    run_id = start_run(conn,"J03-J05",meta,code_version)
                    try:
                        with conn.transaction():
                            metrics = build_model(conn,args.month)
                        finish_run(conn,run_id,"SUCCESS",start)
                        before_after(conn,args.month,args.report_dir)
                        print(json.dumps(metrics,default=str))
                    except Exception as error:
                        finish_run(conn,run_id,"FAIL",start,error=safe_error(error))
                        raise
                if args.job in ("check","all"):
                    start = perf_counter()
                    meta = dict(family="employment",report_month=args.month,version="check",
                                filename="G2_RECONCILIATION",sha256="",row_count="0")
                    run_id = start_run(conn,"J06",meta,code_version)
                    try:
                        result = reconciliation(conn,args.month,args.report_dir)
                        finish_run(conn,run_id,"SUCCESS",start,actual=len(result))
                    except Exception as error:
                        finish_run(conn,run_id,"FAIL",start,error=safe_error(error))
                        raise
            finally:
                export_logs(conn,args.report_dir)
    except Exception as error:
        print("FAIL " + safe_error(error),file=sys.stderr)
        return 1
    print(f"Completed {args.job} month={args.month} db={args.database}; TV4/TV5 review pending")
    return 0


if __name__ == "__main__":
    sys.exit(main())
