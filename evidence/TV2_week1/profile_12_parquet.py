"""TV2 - Data Profiling cho 12 tệp Parquet của Nhóm 13.

Cài đặt: python -m pip install duckdb
Chạy:     python profile_12_parquet.py
Tùy chọn: python profile_12_parquet.py --check-duplicates

Đặt ba ZIP nguồn vào ./data/zips/; script tự giải nén sang ./data/raw/
Kết quả CSV ở ./reports/profiling/.
"""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import zipfile
from pathlib import Path

try:
    import duckdb
except ImportError as exc:
    raise SystemExit(
        "Chưa có DuckDB. Hãy chạy: python -m pip install duckdb"
    ) from exc

ROOT = Path(__file__).resolve().parent
ZIP_DIR = ROOT / "data" / "zips"
RAW_DIR = ROOT / "data" / "raw"
OUTPUT_DIR = ROOT / "reports" / "profiling"
MONTH_RE = re.compile(r"_(20\d{4})_v\d+\.parquet$", re.IGNORECASE)
EXPECTED = {"employment": 4, "accessions": 4, "separations": 4}
CATEGORICAL_FIELDS = [
    "agency_code", "occupational_series_code", "grade", "duty_station_state",
    "appointment_type_code", "accession_category_code", "separation_category_code",
]


def qid(name: str) -> str:
    """Bao chuỗi làm SQL identifier, phòng tên cột có ký tự đặc biệt."""
    return '"' + name.replace('"', '""') + '"'


def qstr(value: str | Path) -> str:
    """Bao chuỗi làm SQL literal (chỉ dùng với file nguồn tin cậy)."""
    return "'" + str(value).replace("'", "''") + "'"


def export_csv(filename: str, rows: list[dict], columns: list[str]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"  -> {path.relative_to(ROOT)} ({len(rows)} dòng)")


def unpack_zip_sources() -> None:
    """Chỉ giải nén các file .parquet, không ghi đè file đã tồn tại."""
    for archive_path in sorted(ZIP_DIR.glob("*.zip")):
        with zipfile.ZipFile(archive_path) as archive:
            for member in archive.infolist():
                path_in_zip = Path(member.filename)
                if member.is_dir() or path_in_zip.suffix.lower() != ".parquet":
                    continue
                if len(path_in_zip.parts) < 2 or path_in_zip.parts[0] not in EXPECTED:
                    raise ValueError(f"Đường dẫn Parquet không dự kiến: {member.filename}")
                target = RAW_DIR / path_in_zip.parts[0] / path_in_zip.name
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists() or target.stat().st_size != member.file_size:
                    with archive.open(member) as source, target.open("wb") as out:
                        shutil.copyfileobj(source, out)
                print(f"Đã chuẩn bị {target.relative_to(ROOT)}")


def get_files() -> list[tuple[str, str, Path]]:
    items: list[tuple[str, str, Path]] = []
    for dataset in EXPECTED:
        for path in sorted((RAW_DIR / dataset).glob("*.parquet")):
            matched = MONTH_RE.search(path.name)
            if matched:
                items.append((dataset, matched.group(1), path))
    counts = {d: sum(item[0] == d for item in items) for d in EXPECTED}
    if counts != EXPECTED:
        raise SystemExit(
            f"Cần đủ 12 Parquet đúng kỳ, tìm được: {counts}. "
            f"Hãy kiểm tra thư mục {ZIP_DIR} hoặc {RAW_DIR}."
        )
    return items


def summarize_file(con, dataset: str, period: str, path: Path, check_duplicates: bool):
    source = f"read_parquet({qstr(path)})"
    description = con.execute(f"DESCRIBE SELECT * FROM {source}").fetchall()
    columns = [row[0] for row in description]
    types = {row[0]: row[1] for row in description}
    select_parts = ["COUNT(*) AS n"]
    for i, col in enumerate(columns):
        ident = qid(col)
        as_text = f"TRIM(CAST({ident} AS VARCHAR))"
        select_parts.extend([
            f"COUNT(*) FILTER (WHERE {ident} IS NULL) AS null_{i}",
            f"COUNT(*) FILTER (WHERE {ident} IS NOT NULL AND {as_text} = '') AS empty_{i}",
            f"COUNT(*) FILTER (WHERE UPPER({as_text}) = 'REDACTED') AS redacted_{i}",
            f"APPROX_COUNT_DISTINCT({ident}) AS distinct_approx_{i}",
        ])
    sql = "SELECT " + ", ".join(select_parts) + f" FROM {source}"
    result = con.execute(sql).fetchone()
    n_rows = int(result[0])
    profiles: list[dict] = []
    for i, col in enumerate(columns):
        nulls, empty, redacted, distinct = result[1 + 4*i : 5 + 4*i]
        profiles.append({
            "dataset": dataset, "period": period, "file": path.name,
            "column": col, "parquet_type": types[col], "total_rows": n_rows,
            "null_count": nulls, "null_pct": round(100 * nulls/n_rows, 4) if n_rows else 0,
            "empty_string_count": empty, "redacted_count": redacted,
            "redacted_pct": round(100 * redacted/n_rows, 4) if n_rows else 0,
            "distinct_approx": distinct,
        })

    # Chỉ đánh giá khả năng chuyển 'count' sang số. Không suy diễn 1 dòng = 1 người.
    count_result = None
    if "count" in columns:
        ct = qid("count")
        txt = f"TRIM(CAST({ct} AS VARCHAR))"
        conv = f"TRY_CAST({txt} AS DOUBLE)"
        sql_count = f"""
        SELECT
            COUNT(*) FILTER (WHERE {ct} IS NULL) AS null_count,
            COUNT(*) FILTER (WHERE {ct} IS NOT NULL AND {txt}='') AS empty_count,
            COUNT(*) FILTER (WHERE UPPER({txt})='REDACTED') AS redacted_count,
            COUNT(*) FILTER (WHERE {conv} IS NOT NULL) AS numeric_count,
            COUNT(*) FILTER (WHERE {ct} IS NOT NULL AND {txt}<>''
                AND UPPER({txt})<>'REDACTED' AND {conv} IS NULL) AS other_invalid_count,
            COUNT(*) FILTER (WHERE {conv}<0) AS negative_numeric_count,
            COUNT(*) FILTER (WHERE {conv}=0) AS zero_numeric_count,
            MIN({conv}) AS min_numeric,
            MAX({conv}) AS max_numeric,
            SUM({conv}) AS sum_numeric_nonredacted
        FROM {source}
        """
        vals = con.execute(sql_count).fetchone()
        count_result = dict(zip([
            "null_count", "empty_count", "redacted_count", "numeric_count",
            "other_invalid_count", "negative_numeric_count", "zero_numeric_count",
            "min_numeric", "max_numeric", "sum_numeric_nonredacted",
        ], vals))
        count_result.update({"dataset":dataset,"period":period,"file":path.name,"total_rows":n_rows})

    month_col = "snapshot_yyyymm" if dataset == "employment" else "personnel_action_effective_date_yyyymm"
    month_result = None
    if month_col in columns:
        col = qid(month_col)
        txt = f"TRIM(CAST({col} AS VARCHAR))"
        # YYYYMM hợp lệ; ngày hiệu lực khác kỳ file không nhất thiết là lỗi.
        is_valid = f"REGEXP_FULL_MATCH({txt}, '^(19|20)[0-9]{{2}}(0[1-9]|1[0-2])$')"
        sql_month = f"""
        SELECT
            COUNT(*) FILTER (WHERE {col} IS NULL) AS null_month,
            COUNT(*) FILTER (WHERE {col} IS NOT NULL AND NOT {is_valid}) AS malformed_month,
            COUNT(*) FILTER (WHERE {is_valid} AND {txt} <> {qstr(period)}) AS mismatch_month,
            COUNT(*) FILTER (WHERE {is_valid} AND {txt} = {qstr(period)}) AS matching_month
        FROM {source}
        """
        vals = con.execute(sql_month).fetchone()
        month_result = dict(zip(["null_month","malformed_month","mismatch_month","matching_month"],vals))
        month_result.update({"dataset":dataset,"period":period,"file":path.name,
                             "month_column":month_col,"total_rows":n_rows})

    categories: list[dict] = []
    for col in CATEGORICAL_FIELDS:
        if col not in columns:
            continue
        ident = qid(col)
        # count_numeric_sum chỉ cộng được các giá trị count chuyển được sang số.
        sql_top = f"""
        SELECT CAST({ident} AS VARCHAR) AS value, COUNT(*) AS record_count,
            SUM(TRY_CAST(TRIM(CAST({qid('count')} AS VARCHAR)) AS DOUBLE)) AS count_numeric_sum
        FROM {source}
        GROUP BY 1
        ORDER BY record_count DESC, value
        LIMIT 10
        """
        for rank, (value, frequency, weighted_sum) in enumerate(con.execute(sql_top).fetchall(), 1):
            categories.append({"dataset":dataset,"period":period,"file":path.name,
                               "column":col,"rank":rank,"value":value,
                               "record_count":frequency,"count_numeric_sum":weighted_sum})

    duplicates = None
    if check_duplicates:
        # Hash nguyên hàng: chỉ để *sàng lọc*, có rủi ro va chạm hash nhỏ.
        hashed = ", ".join(qid(c) for c in columns)
        distinct_hash = con.execute(f"SELECT COUNT(DISTINCT HASH({hashed})) FROM {source}").fetchone()[0]
        duplicates = {"dataset":dataset,"period":period,"file":path.name,
                      "total_rows":n_rows,"distinct_row_hashes":distinct_hash,
                      "potential_duplicate_rows_hash":n_rows - distinct_hash}
    return profiles, count_result, month_result, categories, duplicates, n_rows


def main() -> None:
    parser = argparse.ArgumentParser(description="TV2 Data Profiling - 12 tệp Parquet")
    parser.add_argument("--check-duplicates", action="store_true",
                        help="Thêm sàng lọc dòng trùng qua hash (tốn thời gian hơn)")
    args = parser.parse_args()
    unpack_zip_sources()
    files = get_files()
    con = duckdb.connect()
    con.execute("PRAGMA threads=4")
    profiles, counts, months, cats, dupes, files_summary = [], [], [], [], [], []
    for index, (dataset, period, path) in enumerate(files, start=1):
        print(f"[{index}/12] Đang profiling: {path.name}", flush=True)
        p, c, m, a, d, n = summarize_file(con, dataset, period, path, args.check_duplicates)
        profiles.extend(p)
        if c is not None: counts.append(c)
        if m is not None: months.append(m)
        cats.extend(a)
        if d is not None: dupes.append(d)
        files_summary.append({"dataset":dataset,"period":period,"file":path.name,
                              "rows":n,"columns":len(p)})

    export_csv("column_profile.csv", profiles, [
        "dataset","period","file","column","parquet_type","total_rows",
        "null_count","null_pct","empty_string_count","redacted_count","redacted_pct","distinct_approx",
    ])
    export_csv("count_quality.csv", counts, [
        "dataset","period","file","total_rows","null_count","empty_count",
        "redacted_count","numeric_count","other_invalid_count","negative_numeric_count",
        "zero_numeric_count","min_numeric","max_numeric","sum_numeric_nonredacted",
    ])
    export_csv("month_consistency.csv", months, [
        "dataset","period","file","month_column","total_rows","null_month",
        "malformed_month","mismatch_month","matching_month",
    ])
    export_csv("category_top10.csv", cats, [
        "dataset","period","file","column","rank","value","record_count","count_numeric_sum",
    ])
    export_csv("file_summary.csv", files_summary, ["dataset","period","file","rows","columns"])
    if args.check_duplicates:
        export_csv("potential_duplicates_hash.csv", dupes, [
            "dataset","period","file","total_rows","distinct_row_hashes","potential_duplicate_rows_hash",
        ])
    print("HOÀN THÀNH. Lưu ý: distinct_approx là ước lượng; "
          "không coi mismatch_month hay duplicate hash mặc nhiên là lỗi. "
          "Không dùng COUNT(*) để kết luận số nhân viên.")

if __name__ == "__main__":
    main()
