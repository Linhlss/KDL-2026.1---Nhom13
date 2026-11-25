# Kết quả MVP Power BI: K01, K06, K07 tháng 04/2025 (L4-05/L4-06)

**Task:** L4-05/L4-06 · Owner: TV4 · Review: TV3, TV5
**Ngày thực hiện:** 23–25/11/2026 (cập nhật 25/11/2026)
**Trạng thái:** REVIEW. Chưa PASS: chờ TV5 đối soát SQL–DAX độc lập và TV3 xác nhận kết quả trên Windows.
**Phạm vi:** kỳ 202504, bản dữ liệu tổng hợp của TV3 (Mart và Dimension). Chưa có dữ liệu nhiều tháng.

## 1. Môi trường và dữ liệu nhận

| Mục | Giá trị |
|---|---|
| Nhánh / commit nhận | `tv3/g2-pipeline` · `3b30235` |
| Dump | `handoff/TV3_G2/workforce_g2.dump`, 20.918 byte |
| SHA-256 | `837729db8c478d0cd8a08fa7aebb0b1154f67fbfeeeff7e31483ab0a48b3bcfa` (khớp file `.sha256` của TV3) |
| Máy / hệ điều hành | Windows, PowerShell |
| PostgreSQL | 18 trên Windows (`pg_restore` 18.6 đọc archive tạo bằng 18.7; restore thành công) |
| Database | `workforce_g2_tv4`, user `postgres`, `localhost:5432` |
| Power BI Desktop | Phiên bản hiện tại của Power BI Desktop (bản tháng 11/2026); ghi số phiên bản chính xác từ Help > About nếu reviewer yêu cầu |
| Chế độ nạp | Import; kết nối không mã hóa (PostgreSQL cục bộ không bật SSL) |

## 2. Restore và SELECT (Windows)

| Kiểm tra | Thực tế | Kỳ vọng (TV3) | Kết quả |
|---|---:|---:|---|
| `dw.dim_month` | 3 | 3 | PASS |
| `dw.dim_agency` | 123 | 123 | PASS |
| `dw.dim_action_category` | 14 | 14 | PASS |
| `mart.workforce_monthly` | 114 | 114 | PASS |
| `mart.personnel_flows_monthly` | 88 | 88 | PASS |
| K01 (`sql/05_g2_kpi.sql`, 202504) | 2.271.969 | 2.271.969 | PASS |
| K06 | 7.153 | 7.153 | PASS |
| K07 | 24.088 | 24.088 | PASS |

Bằng chứng: `evidence/TV4_week2/01_checksum_restore.png`, `02_row_counts.png`, `03_sql_kpi.png`.

## 3. Mô hình Power BI

Nạp 5 bảng, đổi tên query: `dim_month`, `dim_agency`, `dim_action_category`, `workforce_monthly`, `personnel_flows_monthly`. Tắt tự phát hiện quan hệ; xóa quan hệ tự suy ra từ khóa ngoại `month_key` của `dim_agency` và `dim_action_category`.

Bốn quan hệ đang hoạt động, Many to one (\*:1), Cross-filter Single, từ Dimension tới Mart:

| Dimension (phía 1) | Mart (phía \*) |
|---|---|
| `dim_month[month_key]` | `workforce_monthly[month_key]` |
| `dim_month[month_key]` | `personnel_flows_monthly[month_key]` |
| `dim_agency[agency_key]` | `workforce_monthly[agency_key]` |
| `dim_agency[agency_key]` | `personnel_flows_monthly[agency_key]` |

`dim_action_category` được nạp nhưng chưa nối: Mart hiện không có `category_key`. Hai Mart không nối với nhau. Bằng chứng: `04_model_view.png`.

Measure:
```dax
K01 Headcount  = SUM ( workforce_monthly[headcount] )
K06 Accessions = SUM ( personnel_flows_monthly[accessions] )
K07 Separations = SUM ( personnel_flows_monthly[separations] )
```

## 4. Đối soát SQL–DAX (tháng 202504)

| # | Bộ lọc | Chỉ số | SQL | DAX (Power BI) | Kết quả |
|---|---|---|---:|---:|---|
| 1 | Toàn kỳ, không chọn agency | K01 | 2.271.969 | 2.271.969 | PASS |
| 1 | | K06 | 7.153 | 7.153 | PASS |
| 1 | | K07 | 24.088 | 24.088 | PASS |
| 2 | Agency Unknown (`agency_key = 0`) | K01 | 206.687 (số TV3, chưa chạy lại SQL trên máy TV4) | 206.687 | PASS |
| 2 | | K06 | 1.591 (số TV3) | 1.591 | PASS |
| 2 | | K07 | 1.936 (số TV3) | 1.936 | PASS |
| 3 | DEPARTMENT OF THE AIR FORCE (`AF`) | K01 | 170.447 | 170.447 | PASS |
| 3 | | K06 | 270 | 270 | PASS |
| 3 | | K07 | 1.269 | 1.269 | PASS |
| 4 | Bỏ chọn agency sau phép thử 2/3 | K01 | 2.271.969 | 2.271.969 | PASS |

Bằng chứng: `05_report_total.png`, `06_report_unknown.png`, `07_report_agency.png`, `08_sql_agency_AF.png`.

SQL phép thử 3 chạy trên `workforce_g2_tv4`:
```sql
SELECT 'AF' AS agency,
  (SELECT sum(headcount) FROM mart.workforce_monthly WHERE month_key=202504 AND agency_code='AF') AS k01,
  (SELECT sum(accessions) FROM mart.personnel_flows_monthly WHERE month_key=202504 AND agency_code='AF') AS k06,
  (SELECT sum(separations) FROM mart.personnel_flows_monthly WHERE month_key=202504 AND agency_code='AF') AS k07;
```
Kết quả: 170447 / 270 / 1269.
Nhóm Unknown được giữ trong tổng toàn kỳ và hiển thị riêng khi lọc. Tháng lọc trực tiếp hai Mart qua `dim_month`, không lọc `dim_agency` theo `month_key`.

## 5. Giới hạn đã biết

- Chỉ có tháng 202504 trong Mart. K02, K03 và các trang so sánh nhiều tháng (D1, D3) chưa dựng được.
- Mart có grain tháng + agency. Không có category và không có tháng hiệu lực, nên chưa làm được biểu đồ theo loại hành động và góc nhìn theo `effective_month` ở D2. Cần nạp Fact sự kiện hoặc thêm Mart (đề nghị TV3).
- `dim_agency` có `agency_key` khác nhau theo từng tháng; khi so sánh nhiều tháng phải nhóm theo `agency_code`.
- Nhóm agency Unknown lớn (206.687 dòng Employment). Nhãn agency/category còn `PARTIAL` theo lookup của TV2.
- Chỉ có số tổng hợp; không có dữ liệu cấp bản ghi hoặc cột REDACTED/lương trong file PBIX.

## 6. Việc còn lại

- [ ] TV5 đối soát SQL–DAX độc lập (3 phép thử DAX còn PENDING trong báo cáo TV3)
- [ ] TV3 xác nhận kết quả Windows và trả lời các điểm "Cần xem lại" trong `docs/09_bus_matrix.md`
- [ ] Bổ sung dữ liệu nhiều tháng và (nếu cần) category/tháng hiệu lực để dựng D1–D3 đầy đủ
- [ ] Cập nhật tracker (L4-05/L4-06) và issue #33 với đường dẫn tài liệu này
