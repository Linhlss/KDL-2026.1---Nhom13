"""EDA on one Employment snapshot plus descriptive comparisons over the baseline."""
import argparse
from collections import Counter
from io import StringIO
from pathlib import Path

import duckdb
import matplotlib
import numpy as np
from scipy.stats import chi2

from source_baseline import FAMILIES, MONTHS, ROOT, identifier, make_inventory, paths, read_csv, write_csv

matplotlib.use("Agg")
from matplotlib import pyplot as plt

REPORTS = ROOT / "reports"
CHARTS = REPORTS / "05_charts"
SNAPSHOT = "202504"
plt.rcParams["svg.hashsalt"] = "tv2-baseline"
plt.rcParams["svg.fonttype"] = "none"


def save_chart(fig, name):
    CHARTS.mkdir(parents=True, exist_ok=True)
    svg = StringIO()
    fig.savefig(svg, format="svg", bbox_inches="tight", metadata={"Date": None})
    clean_svg = "\n".join(line.rstrip() for line in svg.getvalue().splitlines()) + "\n"
    (CHARTS / f"{name}.svg").write_text(clean_svg, encoding="utf-8", newline="\n")
    plt.close(fig)


def grouped_codes(con, path, field):
    column = identifier(field)
    return con.execute(f"""
        SELECT {column}, count(*) AS n FROM read_parquet(?)
        GROUP BY {column} ORDER BY n DESC, {column} NULLS LAST
    """, [str(path)]).fetchall()


def distribution(con, files):
    fields = {"employment": "agency_code", "accessions": "accession_category_code",
              "separations": "separation_category_code"}
    output = []
    agency_summary = []
    for family, field in fields.items():
        for month in MONTHS:
            pairs = grouped_codes(con, files[family, month], field)
            observed = [(key, n) for key, n in pairs if key not in (None, "", "REDACTED")]
            total = sum(n for _, n in pairs)
            running = 0
            for rank, (key, count) in enumerate(observed, 1):
                running += count
                output.append(dict(family=family, report_month=month, field=field,
                                   code=key, status="OBSERVED", rank=rank, records=count,
                                   total_records=total, cumulative_records=running))
            for key, count in pairs:
                if key in (None, "", "REDACTED"):
                    status = {None: "NULL", "": "EMPTY", "REDACTED": "REDACTED"}[key]
                    output.append(dict(family=family, report_month=month, field=field,
                                       code="", status=status, rank="", records=count,
                                       total_records=total, cumulative_records=""))
            if family == "employment":
                top = (len(observed) + 4) // 5
                top_n = sum(n for _, n in observed[:top])
                agency_summary.append((month, len(observed), top, top_n, total))
    write_csv(REPORTS / "05_code_distribution.csv", output)
    chosen = [row for row in output if row["family"] == "employment"
              and row["report_month"] == SNAPSHOT and row["status"] == "OBSERVED"]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot([row["rank"] for row in chosen],
            [100 * row["cumulative_records"] / row["total_records"] for row in chosen])
    ax.axhline(80, color="#888", linestyle="--")
    ax.axvline((len(chosen) + 4) // 5, color="#df7020", linestyle="--")
    ax.set(xlabel="Agency rank", ylabel="Share of all snapshot records (%)",
           title="Employment 2025-04 · cumulative share by agency")
    save_chart(fig, "agency_pareto")
    return agency_summary


def keep_top(pairs, index):
    frequency = Counter()
    for record in pairs:
        frequency[record[index]] += record[2]
    return sorted(frequency, key=lambda key: (-frequency[key], key))[:10]


def association(con, path, label, x, y):
    expected_excluded = (None, "", "REDACTED")
    pairs = con.execute(f"""
        SELECT {identifier(x)}, {y}, count(*) FROM read_parquet(?) GROUP BY ALL
    """, [str(path)]).fetchall()
    eligible = [(a, b, n) for a, b, n in pairs
                if a not in expected_excluded and b not in expected_excluded]
    top_x, top_y = keep_top(eligible, 0), keep_top(eligible, 1)
    top_x, top_y = top_x + ["(Other)"], top_y + ["(Other)"]
    counts = Counter()
    for a, b, n in eligible:
        counts[a if a in top_x else "(Other)", b if b in top_y else "(Other)"] += n
    observed = np.array([[counts[a, b] for b in top_y] for a in top_x])
    row_mask, col_mask = observed.sum(axis=1) > 0, observed.sum(axis=0) > 0
    observed = observed[np.ix_(row_mask, col_mask)]
    x_values = [value for value, keep in zip(top_x, row_mask) if keep]
    y_values = [value for value, keep in zip(top_y, col_mask) if keep]
    n = int(observed.sum())
    r, c = observed.shape
    if r < 2 or c < 2:
        raise ValueError(f"Degenerate contingency table: {label}")
    expected = np.outer(observed.sum(axis=1), observed.sum(axis=0)) / n
    contributions = (observed - expected) ** 2 / expected
    x2 = float(contributions.sum())
    dof = (r - 1) * (c - 1)
    v = float(np.sqrt(x2 / (n * min(r - 1, c - 1))))
    low = int((expected < 5).sum())
    assumptions_met = bool(expected.min() >= 1 and low / expected.size <= 0.2)
    p_value = float(chi2.sf(x2, dof)) if assumptions_met else None
    cells = [dict(row=a, column=b, observed=int(observed[i, j]),
                  row_total=int(observed[i].sum()), column_total=int(observed[:, j].sum()),
                  expected=f"{expected[i,j]:.8f}", chi_square_component=f"{contributions[i,j]:.8f}")
             for i, a in enumerate(x_values) for j, b in enumerate(y_values)]
    write_csv(REPORTS / f"05_crosstab_{label}.csv", cells)
    return dict(label=label, n=n, excluded=sum(item[2] for item in pairs) - n,
                rows=r, columns=c, chi_square=x2, dof=dof, v=v, minimum_expected=float(expected.min()),
                low_expected=low, assumptions_met=assumptions_met, p_value=p_value, sample=cells[0])


def pay_distribution(con, path):
    intervals = con.execute("""
        WITH numeric_pay AS (
            SELECT try_cast(annualized_adjusted_basic_pay AS DECIMAL(18,2)) AS pay
            FROM read_parquet(?)
        )
        SELECT CASE WHEN pay >= 300000 THEN 300000
                    ELSE floor(pay / 25000)::INTEGER * 25000 END AS lower_usd,
               count(*) AS n
        FROM numeric_pay WHERE pay >= 0 GROUP BY 1 ORDER BY 1
    """, [str(path)]).fetchall()
    counts = dict(intervals)
    buckets = list(range(0, 325000, 25000))
    labels = [f"{value // 1000}k" for value in buckets[:-1]] + ["300k+"]
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(labels, [counts.get(value, 0) for value in buckets], color="#1f7184")
    ax.set(xlabel="Lower bound (USD)", ylabel="Records",
           title="Employment 2025-04 · observed annualized adjusted basic pay")
    save_chart(fig, "pay_histogram")
    write_csv(REPORTS / "05_pay_histogram.csv",
              [dict(lower_usd=value, upper_usd=value + 25000 if value < 300000 else "",
                    records=counts.get(value, 0)) for value in buckets])
    return sum(counts.values())


def monthly_chart(inventory):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    monthly = []
    for family in FAMILIES:
        counts = [row["row_count"] for row in inventory if row["family"] == family]
        target = axes[0] if family == "employment" else axes[1]
        target.plot(MONTHS, counts, marker="o", label=family.capitalize())
        previous = None
        for month, count in zip(MONTHS, counts):
            monthly.append(dict(family=family, report_month=month, records=count,
                                mom_delta=count - previous if previous is not None else "",
                                mom_pct=f"{100 * (count - previous) / previous:.6f}" if previous else ""))
            previous = count
    for ax in axes:
        ax.legend()
        ax.set(xlabel="File month", ylabel="Records")
        ax.ticklabel_format(axis="y", style="plain")
    save_chart(fig, "monthly_records")
    write_csv(REPORTS / "05_monthly_records.csv", monthly)


def report(results, pareto, pay_count, snapshot_n):
    lines = [
        "# EDA bổ sung TV2 · C05", "",
        "Phạm vi là 12 Parquet baseline 03–06/2025. Hai bảng chéo dùng riêng Employment "
        "202504. Đơn vị phân tích là bản ghi snapshot hoặc lượt hành động công bố.", "",
        "## Bảy chiều chất lượng", "",
        "| Chiều | Bằng chứng |", "|---|---|",
        "| Đầy đủ | Profiling v1 đo NULL, rỗng và REDACTED theo từng cột/file. |",
        "| Hợp lệ | Kiểm cú pháp tháng, count và chuyển kiểu lương qua DuckDB. |",
        "| Nhất quán | Schema hash ổn định theo họ, cột thời gian được kiểm theo grain. |",
        "| Duy nhất | Vị trí dòng duy nhất theo file, cùng checksum khóa bộ nguồn. |",
        "| Toàn vẹn tham chiếu | Audit exact đủ kỳ. Phạm vi catalog lịch sử đang chờ đối chiếu. |",
        "| Bất thường | Kiểm lương không parse được hoặc âm và phân bố lương quan sát được. |",
        "| Kịp thời | 593 event khác kỳ công bố/hiệu lực. Chưa có timestamp gửi để đo trễ. |", "",
        "[Kiểm dữ liệu](05_data_quality.csv) · [Audit khóa](../docs/04_relationship_audit.csv) · "
        "[Profiling theo file](../evidence/TV2_week1/TV2_Data_Quality_Phan_Tich_V1/column_profile.csv)", "",
        "## Phân bố và thời gian", "",
        "| Tháng | Agency có mã quan sát | Số agency trong top 20% | Bản ghi top 20% | % toàn snapshot |",
        "|---|---:|---:|---:|---:|",
    ]
    lines.extend(f"| {month} | {codes} | {top} | {n:,} | {100*n/total:.2f} |"
                 for month, codes, top, n, total in pareto)
    lines.extend([
        "", "Top 20% làm tròn lên theo số mã agency có mặt. Tỷ lệ lấy toàn bộ snapshot làm mẫu số. "
        "Bảng phân bố chứa cả mã hành động và các trạng thái bị thiếu.", "",
        f"Histogram lương 202504 dùng {pay_count:,}/{snapshot_n:,} giá trị quan sát được. "
        "Các cột có bề rộng 25.000 USD và một cột gom từ 300.000 USD.",
        "", "So sánh MoM mô tả phạm vi bốn kỳ. Employment giảm trong bốn snapshot, "
        "Accessions tăng theo kỳ file và Separations đạt đỉnh tháng 05.", "",
        "[Phân bố mã](05_code_distribution.csv) · [Pareto](05_charts/agency_pareto.svg) · "
        "[Histogram](05_charts/pay_histogram.svg) · [MoM](05_monthly_records.csv) · "
        "[Biểu đồ theo tháng](05_charts/monthly_records.svg)", "",
        "## Liên hệ giữa biến phân loại", "",
        "Mỗi trục giữ 10 mã có tần suất biên cao nhất, gom các mã còn lại vào Other. "
        "Bản ghi thiếu hoặc REDACTED ở một trong hai trục được tính vào số loại khỏi bảng chéo. "
        "Grade dùng cặp Pay Plan + Grade để giữ ngữ cảnh. Kiểm expected count trước khi đọc p-value.", "",
        "| Bảng | N | Loại | Kích thước | χ² | df | Cramér’s V | E nhỏ nhất | Ô E < 5 | p |",
        "|---|---:|---:|---|---:|---:|---:|---:|---:|---|",
    ])
    for item in results:
        p = item["p_value"]
        p_text = "< 1e-300" if p == 0 else f"{p:.3g}" if p is not None else "—"
        lines.append(
            f"| [{item['label']}](05_crosstab_{item['label']}.csv) | {item['n']:,} | "
            f"{item['excluded']:,} | {item['rows']} × {item['columns']} | "
            f"{item['chi_square']:.2f} | {item['dof']} | {item['v']:.4f} | "
            f"{item['minimum_expected']:.2f} | {item['low_expected']} | {p_text} |")
    lines.extend(["", "V mô tả độ liên hệ trong các nhóm đã gom của snapshot này. "
                  "Với dữ liệu toàn snapshot và cỡ N lớn, p-value dùng để minh họa phương pháp. "
                  "Bốn kỳ chỉ đủ mô tả biến động ngắn hạn.", "", "[Ví dụ tính từng ô](05_categorical_method_example.md)"])
    (REPORTS / "05_eda_findings.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    result = next((item for item in results if item["assumptions_met"]), results[0])
    cell = result["sample"]
    example = [
        "# Ví dụ Chi-square và Cramér’s V từ Employment 202504", "",
        f"Nguồn là bảng chéo [{result['label']}](05_crosstab_{result['label']}.csv). "
        f"Ô minh họa có nhóm dòng **{cell['row']}** và nhóm cột **{cell['column']}**.", "",
        f"1. Oij = {cell['observed']:,}. Tổng dòng = {cell['row_total']:,}. "
        f"Tổng cột = {cell['column_total']:,}. N = {result['n']:,}.",
        f"2. Eij = tổng dòng × tổng cột / N = {cell['expected']}.",
        f"3. Đóng góp của ô = (Oij − Eij)² / Eij = {cell['chi_square_component']}.",
        f"4. Cộng mọi ô được χ² = {result['chi_square']:.6f}, df = {result['dof']}.",
        f"5. V = sqrt(χ² / [N × min(r−1, c−1)]) = {result['v']:.6f}.",
        "", f"E nhỏ nhất = {result['minimum_expected']:.3f}. "
        f"Có {result['low_expected']}/{result['rows'] * result['columns']} ô E < 5. "
        "Cramér’s V phụ thuộc cách phân nhóm. Các mã hiếm được gom vào Other.",
    ]
    (REPORTS / "05_categorical_method_example.md").write_text("\n".join(example) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw", type=Path)
    args = parser.parse_args()
    files = paths(args.raw.resolve())
    inventory, _ = make_inventory(files)
    snapshot = files["employment", SNAPSHOT]
    snapshot_n = next(row["row_count"] for row in inventory if row["filename"] == snapshot.name)
    with duckdb.connect() as con:
        pareto = distribution(con, files)
        results = [
            association(con, snapshot, "agency_occupation", "agency_code", '"occupational_series_code"'),
            association(con, snapshot, "occupation_grade", "occupational_series_code", """
                CASE WHEN pay_plan_code NOT IN ('', 'REDACTED') AND grade NOT IN ('', 'REDACTED')
                     THEN pay_plan_code || ':' || grade END
            """)]
        pay_count = pay_distribution(con, snapshot)
    for result in results:
        assert result["n"] + result["excluded"] == snapshot_n
    monthly_chart(inventory)
    report(results, pareto, pay_count, snapshot_n)
    print(f"EDA {SNAPSHOT}: {snapshot_n:,} rows; two reconciled contingency tables")


if __name__ == "__main__":
    main()
