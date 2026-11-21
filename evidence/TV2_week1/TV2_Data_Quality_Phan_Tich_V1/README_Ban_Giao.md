# TV2 — Gói kết quả Data Profiling / Data Quality (bản 1)

> Chuẩn nghiệm thu hiện hành là V3 và kế hoạch G2. Xem [gói TV2 cập nhật](../../TV2_week2/README.md).

**Nguồn nhập:** `csv.zip`, gồm 5 CSV do lệnh `py profile_12_parquet.py` trên máy TV2 xuất ra từ 12 Parquet.  
**Đối chiếu yêu cầu:** đề cương và phân công Nhóm 13 bản V2.

## Những file nên mở trước

- `data_quality.md` — báo cáo đầy đủ: số liệu, diễn giải, rủi ro, kiến nghị và việc chưa làm.
- `TV2_Profiling_Analysis.xlsx` — workbook 10 sheet, gồm tổng quan tháng, chất lượng cột, findings, month checks, count quality, top 10 agency, validation và 2 sheet CSV raw.
- `data_quality_findings.csv` — 10 phát hiện, mức độ ưu tiên, đề xuất xử lý, chủ sở hữu và trạng thái xác minh.
- `validation_checks.csv` — 7 phép đối soát tính nhất quán của 5 CSV.

## File kết quả phân tích bổ sung

- `column_quality_aggregated.csv` — 201 cặp dataset/cột, gom qua 4 kỳ, NULL/empty/REDACTED riêng biệt.
- `monthly_trends.csv` — số dòng theo tháng và thay đổi MoM từ file_summary.
- `month_check_extended.csv` — tỷ lệ lệch kỳ theo file.
- `count_check_by_dataset.csv` — thống kê count theo 3 nhóm.
- `agency_top10_share.csv` — tỷ trọng top 1/top 10 mã cơ quan theo tháng.
- `chart_*.png` — biểu đồ minh chứng 4 nội dung: thời gian, NULL, REDACTED.
- `metrics_summary.json` — tóm tắt kiểm chứng cho lập trình.

## Năm CSV gốc được giữ nguyên

`file_summary.csv`, `column_profile.csv`, `count_quality.csv`, `month_consistency.csv`, `category_top10.csv`.

## Tái lập bảng phân tích

```powershell
py -m pip install matplotlib
py analyze_profile_csv.py
```

Chạy lệnh trong thư mục có đủ 5 CSV. Script tạo lại báo cáo Markdown, CSV tổng hợp và 4 biểu đồ. File Excel tổng hợp đã được tạo từ các kết quả đó bằng công cụ tạo bảng tính; không phải output của `analyze_profile_csv.py`.

## Quy tắc sử dụng

- Không thay 12 Parquet nguồn bằng 5 CSV profiling. TV3 vẫn cần dữ liệu nguồn để xây ETL.
- Các số lượng được thống kê theo **bản ghi**, không phải nhân viên duy nhất qua nhiều kỳ.
- REDACTED không bằng 0, không đồng nhất với NULL hoặc chuỗi rỗng.
- `distinct_approx` là xấp xỉ.
- 593 dòng lệch kỳ file và effective month **chưa được xác định là lỗi**.
- Gói này **chưa hoàn thiện** Data Dictionary/codebook audit, Taxonomy có mẫu hàng gốc, ERD và EDA đa chiều theo V2.

**Cách bàn giao TV3:** gửi `data_quality.md`, `data_quality_findings.csv`, `validation_checks.csv`, 5 CSV gốc, script chạy `profile_12_parquet.py` cùng đường dẫn/nguồn của 12 Parquet. Gửi XLSX làm bản xem tổng hợp nếu cần.
