# TV1 — Đối chiếu baseline trước khi merge PR #13 và #14

**Ngày chạy:** 18/11/2026. **Người chạy:** TV1. **Mục đích:** quyết định có merge sản phẩm tuần 1 của TV2/TV3 vào `main` ở trạng thái REVIEW hay không.

> Đây là kiểm tra điều phối của TV1. **Không thay review độc lập của TV5** (L5-02, L5-04) và không chuyển task nào sang DONE/PASS.

## Cách chạy lại

```bash
python3 -m venv .venv && .venv/bin/pip install pyarrow
.venv/bin/python evidence/TV1_week2/crosscheck_baseline.py <thư_mục_chứa_employment/accessions/separations> baseline_crosscheck.csv
```

Script đọc từng Parquet: SHA-256 toàn file, `num_rows` từ footer, số cột, hash 16 ký tự của schema (`tên:kiểu`), tập giá trị của `count`, và số dòng có tháng thời gian khác tháng trong tên file (`snapshot_yyyymm` cho Employment, `personnel_action_effective_date_yyyymm` cho Accessions/Separations).

## Kết quả — [`baseline_crosscheck.csv`](baseline_crosscheck.csv)

| Kiểm tra | Kỳ vọng (báo cáo TV2/TV3) | TV1 đo | Kết luận |
|---|---|---|---|
| Số file | 12 | 12 | Khớp |
| Tổng bản ghi | 9.181.290 | 9.181.290 | Khớp |
| Employment / Accessions / Separations | 9.057.997 / 30.782 / 92.511 | 9.057.997 / 30.782 / 92.511 | Khớp |
| Số cột | 64 / 68 / 69, ổn định 4 kỳ | 64 / 68 / 69; một schema hash cho mỗi họ | Khớp |
| `count` | chỉ `1` | chỉ `1` ở 12/12 file | Khớp |
| Event lệch tháng file | 593 | 269 (Accessions) + 324 (Separations) = 593; khớp từng file với `month_consistency.csv` | Khớp |
| Kích thước byte trong `TV2_Source_Inventory.xlsx` | 12 giá trị | khớp từng byte | Khớp |
| SHA-256 hai file prototype TV3 | `933b33c6…72fa`, `d0bfcf71…3e72` | trùng `accessions_202504_v5`, `employment_202504_v4` | Thuộc baseline |

## Giới hạn

- Chạy trên bản 12 Parquet TV1 lưu ở máy; TV2 cần tính SHA-256 trên bản của mình và so với file này khi làm L2-01. Khác hash ở file nào thì ghi version và quyết định giữ/cách ly.
- Không kiểm REDACTED/NULL theo giá trị, không kiểm khóa/FK, không kiểm ETL ngoài checksum và số dòng nguồn.
- `source_url` chưa có trong bảng này; là phần việc của TV2 ở L2-01.
