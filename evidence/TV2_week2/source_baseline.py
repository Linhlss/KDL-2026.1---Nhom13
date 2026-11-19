"""Rebuild the TV2 inventory, dictionary and checks directly from baseline Parquet."""
import argparse
import csv
import hashlib
from pathlib import Path

import duckdb
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]
FAMILIES = {"employment": "v4", "accessions": "v5", "separations": "v5"}
MONTHS = ("202503", "202504", "202505", "202506")
FWD = "https://data.opm.gov/FWD%20Data%20Dictionary.xlsx"
EHRI = "https://data.opm.gov/data-standards/ehri-data-standards"
DUTY = "https://data.opm.gov/data-standards/duty-stations"
MIRROR = "https://huggingface.co/datasets/impactproject/opm-ehri-data/resolve/main"
TIME = "personnel_action_effective_date_yyyymm"
FIELDS = {
    "count": ("Trọng số bản ghi công bố, bằng 1 trong baseline", "record_count"),
    "snapshot_yyyymm": ("Tháng snapshot Employment", "snapshot_month"),
    TIME: ("Tháng hiệu lực của hành động nhân sự", "effective_month"),
    "department_code": ("Mã cấp department trong file công bố", "dim_agency.department_code"),
    "department": ("Nhãn department theo file công bố", "dim_agency.department"),
    "agency_code": ("Mã cơ quan sử dụng lao động", "dim_agency.agency_code"),
    "agency": ("Nhãn cơ quan theo file công bố", "dim_agency.agency"),
    "agency_subelement_code": ("Mã đơn vị hành chính thuộc cơ quan", "agency_subelement_code"),
    "agency_subelement": ("Nhãn đơn vị hành chính theo file công bố", "agency_subelement"),
    "occupational_group_code": ("Mã nhóm nghề", "dim_occupation.occupational_group_code"),
    "occupational_group": ("Nhãn nhóm nghề", "dim_occupation.occupational_group"),
    "occupational_series_code": ("Mã series nghề, giữ số 0 đầu", "dim_occupation.occupational_series_code"),
    "occupational_series": ("Nhãn series nghề", "dim_occupation.occupational_series"),
    "duty_station_code": ("Mã nơi làm việc chính thức", "dim_location.duty_station_code"),
    "duty_station_city": ("Tên thành phố nơi làm việc theo file", "dim_location.duty_station_city"),
    "pay_plan_code": ("Mã hệ thống trả lương", "dim_grade.pay_plan_code"),
    "pay_plan": ("Nhãn hệ thống trả lương", "dim_grade.pay_plan"),
    "grade": ("Cấp bậc trong ngữ cảnh pay plan", "dim_grade.grade"),
    "age_bracket": ("Khoảng tuổi được phát hành", "dim_age_bracket.age_bracket"),
    "annualized_adjusted_basic_pay": ("Lương cơ bản đã điều chỉnh, quy đổi năm", "annualized_adjusted_basic_pay"),
    "accession_category_code": ("Mã nhóm hành động tiếp nhận", "dim_accession_category.accession_category_code"),
    "accession_category": ("Nhãn nhóm hành động tiếp nhận", "dim_accession_category.accession_category"),
    "separation_category_code": ("Mã nhóm hành động rời cơ quan", "dim_separation_category.separation_category_code"),
    "separation_category": ("Nhãn nhóm hành động rời cơ quan", "dim_separation_category.separation_category"),
}


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def paths(raw):
    return {(family, month): raw / family / f"{family}_{month}_{version}.parquet"
            for family, version in FAMILIES.items() for month in MONTHS}


def make_inventory(files):
    crosscheck = {row["filename"]: row for row in read_csv(
        ROOT / "evidence/TV1_week2/baseline_crosscheck.csv")}
    inventory = []
    schemas = {}
    for (family, month), path in files.items():
        parquet = pq.ParquetFile(path)
        schema = parquet.schema_arrow
        schemas[family, month] = {field.name: str(field.type) for field in schema}
        schema_text = "|".join(f"{field.name}:{field.type}" for field in schema)
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        row = dict(family=family, report_month=month, version=FAMILIES[family],
                   filename=path.name, size_bytes=path.stat().st_size,
                   row_count=parquet.metadata.num_rows, column_count=len(schema),
                   schema_hash=hashlib.sha256(schema_text.encode()).hexdigest()[:16],
                   sha256=digest, source_url=f"{MIRROR}/{family}/{path.name}",
                   acquisition_method="Local team baseline; mirror identified in data/README.md")
        for field in ("size_bytes", "row_count", "column_count", "schema_hash", "sha256"):
            reference_field = "schema_hash16" if field == "schema_hash" else field
            if str(row[field]) != crosscheck[path.name][reference_field]:
                raise ValueError(f"Baseline mismatch: {path.name}, {field}")
        inventory.append(row)
    return inventory, schemas


def identifier(value):
    return '"' + value.replace('"', '""') + '"'


def dictionary(con, files, schemas, inventory):
    profiling = ROOT / "evidence/TV2_week1/TV2_Data_Quality_Phan_Tich_V1/column_quality_aggregated.csv"
    quality = {(row["dataset"], row["column"]): row for row in read_csv(profiling)}
    rows = []
    for family in FAMILIES:
        sample = files[family, "202504"]
        family_rows = sum(row["row_count"] for row in inventory if row["family"] == family)
        for field, (meaning, target) in FIELDS.items():
            observed_types = {schema[field] for (group, _), schema in schemas.items()
                              if group == family and field in schema}
            if not observed_types:
                continue
            if len(observed_types) != 1:
                raise ValueError(f"Type drift: {family}.{field}")
            raw = identifier(field)
            example = con.execute(f"""
                SELECT {raw}, count(*) AS n FROM read_parquet(?)
                WHERE {raw} IS NOT NULL AND {raw} NOT IN ('', 'REDACTED')
                GROUP BY {raw} ORDER BY n DESC, {raw} LIMIT 1
            """, [str(sample)]).fetchone()
            stats = quality[family, field]
            if int(stats["rows"]) != family_rows:
                raise ValueError(f"Profiling denominator mismatch: {family}.{field}")
            missing = int(stats["null_count"]) + int(stats["empty_count"])
            source = DUTY if field.startswith("duty_station") else FWD
            status = "DOCUMENTED" if field in ("count", "snapshot_yyyymm", TIME) else "NEED_VERIFY"
            rows.append(dict(dataset=family, raw_field=field, raw_type=observed_types.pop(),
                             meaning_vi=meaning, real_example=example[0] if example else "",
                             example_file=sample.name,
                             source_reference=source, missing_pct=f"{100 * missing / family_rows:.6f}",
                             null_rows=stats["null_count"], empty_rows=stats["empty_count"],
                             redacted_pct=f"{100 * int(stats['redacted_count']) / family_rows:.6f}",
                             denominator=family_rows, target_candidate=target,
                             verified_status=status, reviewer="PENDING TV5"))
        rows.append(dict(dataset=family, raw_field="report_month", raw_type="derived",
                         meaning_vi="Kỳ báo cáo lấy từ tên file và manifest",
                         real_example="202504", example_file=sample.name,
                         source_reference="docs/03_source_inventory.csv", missing_pct="0",
                         null_rows="0", empty_rows="0", redacted_pct="0", denominator=family_rows,
                         target_candidate="source_file.report_month",
                         verified_status="DOCUMENTED", reviewer="PENDING TV5"))
    return rows


def dq_checks(con, files, inventory):
    query = (ROOT / "sql/tests/05_dq_checks.sql").read_text(encoding="utf-8")
    rows = []
    totals = {family: 0 for family in FAMILIES}
    for row in inventory:
        family, month = row["family"], row["report_month"]
        path = files[family, month]
        args = [str(path), month]
        cur = con.execute(query.replace("{{time_field}}", identifier(
            "snapshot_yyyymm" if family == "employment" else TIME)), args)
        result = dict(zip([item[0] for item in cur.description], cur.fetchone(), strict=True))
        if result["records"] != row["row_count"] or result["numeric_count_sum"] != row["row_count"]:
            raise ValueError(f"Count reconciliation failed for {path.name}: {result}")
        if result["invalid_count"] or result["invalid_month"]:
            raise ValueError(f"Invalid count or period in {path.name}: {result}")
        totals[family] += result["different_month"]
        rows.append(dict(family=family, report_month=month, source_file=path.name, **result))
    if totals != {"employment": 0, "accessions": 269, "separations": 324}:
        raise ValueError(f"Baseline effective-month reconciliation failed: {totals}")
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw", type=Path, help="Root containing employment/accessions/separations")
    args = parser.parse_args()
    files = paths(args.raw.resolve())
    inventory, schemas = make_inventory(files)
    with duckdb.connect() as con:
        fields = dictionary(con, files, schemas, inventory)
        quality = dq_checks(con, files, inventory)
    write_csv(ROOT / "docs/03_source_inventory.csv", inventory)
    manifest = ROOT / "data/manifest/sha256.txt"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text("".join(f"{row['sha256']}  {row['filename']}\n"
                                for row in inventory), encoding="utf-8")
    write_csv(ROOT / "docs/03_data_dictionary.csv", fields)
    write_csv(ROOT / "reports/05_data_quality.csv", quality)
    print(f"{len(inventory)} files, {sum(row['records'] for row in quality):,} rows")
    print(f"{len(fields)} dictionary rows; effective-month differences: "
          f"{sum(row['different_month'] for row in quality)}")


if __name__ == "__main__":
    main()
