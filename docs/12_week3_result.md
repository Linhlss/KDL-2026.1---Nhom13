# Kết quả tuần 3 của TV4: Mart G3 đủ 4 kỳ, DAX K01–K10, Dimension catalog (L4-07/L4-08/L4-09)

**Task:** L4-07, L4-08, L4-09 · Owner: TV4 · Review: TV3, TV5, TV2
**Ngày thực hiện:** [điền ngày]
**Trạng thái:** REVIEW. Chưa PASS: chờ TV5 đối soát SQL–DAX độc lập và TV3 xác nhận kết quả trên Windows.
**Phạm vi:** dữ liệu G3 tổng hợp (3 Dimension, 2 Mart) cho 4 kỳ 03–06/2025. Mart có grain tháng + cơ quan.

## 1. Môi trường và dữ liệu nhận

| Mục | Giá trị |
|---|---|
| Nhánh / commit nhận | `tv3/g3-full-pipeline` · `9368437` |
| Dump | `handoff/TV3_G3/workforce_g3.dump`, 29.843 byte |
| SHA-256 kỳ vọng (TV3) | `6d85ea2932e226f05d293bfd48bde7f2cb9b21c54ba9987d419167afbe54e1b8` |
| SHA-256 trên máy TV4 | [điền] → [khớp / không khớp] |
| Hệ điều hành | Windows, PowerShell |
| PostgreSQL / pg_restore | 18 (dịch vụ Windows) |
| Database | `workforce_g3_tv4`, user `postgres`, `localhost:5432` |
| Power BI Desktop | [điền phiên bản: Help > About] |
| File báo cáo | `workforce_mvp_g3.pbix` (lưu ngoài repo) |
| Chế độ nạp | Import; kết nối không mã hóa (PostgreSQL cục bộ không bật SSL) |

## 2. Restore và SELECT (Windows)

| Kiểm tra | Thực tế | Kỳ vọng (TV3) | Kết quả |
|---|---:|---:|---|
| `dw.dim_month` | 9 | 9 | PASS |
| `dw.dim_agency` | 493 | 493 | PASS |
| `dw.dim_action_category` | 53 | 53 | PASS |
| `mart.workforce_monthly` | 486 | 486 | PASS |
| `mart.personnel_flows_monthly` | 340 | 340 | PASS |

SQL KPI (`sql/07_g3_kpi.sql`):

| Tháng | K01 thực tế | K01 kỳ vọng | K06 thực tế | K06 kỳ vọng | K07 thực tế | K07 kỳ vọng | Kết quả |
|---|---:|---:|---:|---:|---:|---:|---|
| 202503 | [điền] | 2.289.192 | [điền] | 4.862 | [điền] | 22.061 | [PASS/FAIL] |
| 202504 | [điền] | 2.271.969 | [điền] | 7.153 | [điền] | 24.088 | [PASS/FAIL] |
| 202505 | [điền] | 2.255.056 | [điền] | 8.813 | [điền] | 26.415 | [PASS/FAIL] |
| 202506 | [điền] | 2.241.780 | [điền] | 9.954 | [điền] | 19.947 | [PASS/FAIL] |

Ghi chú: chạy lại `createdb` và `pg_restore` trên database đã restore báo `already exists`/`schema "dw" already exists`; đây là hành vi mong đợi, dữ liệu đã đầy đủ (đếm dòng đúng). Không dùng ảnh lỗi này làm bằng chứng restore.

Bằng chứng: `evidence/TV4_week3/01_g3_checksum_restore.png`, `02_g3_row_counts.png`, `03_g3_sql_kpi.png`.

## 3. Mô hình Power BI (L4-07)

Nạp 4 bảng: `dim_month`, `dim_agency`, `workforce_monthly`, `personnel_flows_monthly` (và `dim_action_category` để xem, chưa nối). Tắt tự phát hiện quan hệ. Bốn quan hệ đang hoạt động, Many to one (\*:1), Cross-filter Single, từ Dimension tới Mart:

| Dimension (phía 1) | Mart (phía \*) |
|---|---|
| `dim_month[month_key]` | `workforce_monthly[month_key]` |
| `dim_month[month_key]` | `personnel_flows_monthly[month_key]` |
| `dim_agency[agency_key]` | `workforce_monthly[agency_key]` |
| `dim_agency[agency_key]` | `personnel_flows_monthly[agency_key]` |

Ghi chú về cấu hình:
- `dim_action_category` không có quan hệ vì Mart không có `category_key`. Hai Mart không nối với nhau.
- Role dates: Mart workforce theo tháng snapshot, Mart flows theo tháng báo cáo (report month). Không có tháng hiệu lực (effective) trong Mart.
- `dim_month` có 9 dòng, gồm tháng ngoài 4 kỳ (ví dụ 202303, 202304). Slicer tháng được lọc chỉ còn 202503–202506.
- Nhóm Unknown (`agency_key = 0`) giữ trong tổng toàn kỳ và hiển thị riêng khi lọc. Tháng lọc trực tiếp hai Mart qua `dim_month`.
- Cùng một mã agency có `agency_key` khác nhau theo từng tháng (ví dụ AF: 15 / 139 / 261 / 384), nên slicer và bảng dùng `dim_agency[agency_code]` hoặc `agency_label`.

Bằng chứng: `04_g3_model_view.png`.

## 4. DAX K01–K10 (L4-08)

```dax
K01 Headcount =
IF ( HASONEVALUE ( dim_month[month_key] ), SUM ( workforce_monthly[headcount] ), BLANK () )

Prev Month Key =
VAR m = MAX ( dim_month[month_key] )
RETURN CALCULATE ( MAX ( workforce_monthly[month_key] ), REMOVEFILTERS ( dim_month ), workforce_monthly[month_key] < m )

K01 Prev =
VAR pm = [Prev Month Key]
RETURN IF ( ISBLANK ( pm ), BLANK (),
            CALCULATE ( SUM ( workforce_monthly[headcount] ), REMOVEFILTERS ( dim_month ), workforce_monthly[month_key] = pm ) )

K02 Change = IF ( ISBLANK ( [K01 Prev] ), BLANK (), [K01] - [K01 Prev] )
K03 MoM % = DIVIDE ( [K02 Change], [K01 Prev] )
K04 Agency Share = DIVIDE ( [K01], CALCULATE ( [K01], REMOVEFILTERS ( dim_agency ) ) )
K06 Accessions = SUM ( personnel_flows_monthly[accessions] )
K07 Separations = SUM ( personnel_flows_monthly[separations] )
K08 Event Difference = IF ( ISBLANK ( [K06] ) && ISBLANK ( [K07] ), BLANK (), [K06] - [K07] )
```

Tháng trước lấy từ Mart (không từ `dim_month`) để tháng 202503 không bị coi là có tháng trước (`dim_month` có các tháng 2023). Thiếu kỳ trước hoặc mẫu số bằng 0 thì K02 và K03 để trống. K01 chỉ trả giá trị khi chọn đúng một tháng (không cộng các snapshot). Định dạng: K01, K02, K06, K07, K08 là số nguyên có dấu nghìn (người/lượt); K03, K04 là phần trăm 2 số lẻ.

| KPI | Trạng thái | Ghi chú |
|---|---|---|
| K01 | Đã dựng | Bán cộng dồn |
| K02, K03 | Đã dựng | Trống khi thiếu kỳ trước hoặc mẫu số 0 |
| K04 | Đã dựng | Tỷ trọng cơ quan trên toàn bộ cơ quan cùng kỳ, gồm Unknown |
| K05 | Chưa tính | Mart chưa có chiều nhóm (nghề, cấp bậc, địa điểm) |
| K06, K07 | Đã dựng | Đơn vị: lượt |
| K08 | Đã dựng | Đơn vị: lượt; không phải thay đổi headcount |
| K09 | Tạm ẩn | Chờ xử lý nhóm vắng kỳ và Unknown, đối soát tổng đóng góp |
| K10 | Chưa tính | Cần dữ liệu độ phủ khóa tham chiếu từ TV2/TV3 |

## 5. Đối soát SQL–DAX

| # | Bộ lọc | Chỉ số | SQL | DAX | Kết quả |
|---|---|---|---:|---:|---|
| 1 | 202503, toàn kỳ | K01 | 2.289.192 | 2.289.192 | PASS |
| 2 | 202503, toàn kỳ | K02 | trống | trống (`--`) | PASS |
| 3 | 202504, toàn kỳ | K01 | 2.271.969 | 2.271.969 | PASS |
| 4 | 202504, toàn kỳ | K02 | −17.223 | −17.223 | PASS |
| 5 | 202504, toàn kỳ | K03 | −0,75% | −0,75% | PASS |
| 6 | 202504, toàn kỳ | K06 / K07 / K08 | 7.153 / 24.088 / −16.935 | 7.153 / 24.088 / −16.935 | PASS |
| 7 | 202505, toàn kỳ | K01 / K02 | 2.255.056 / −16.913 | 2.255.056 / −16.913 | PASS |
| 8 | 202506, toàn kỳ | K01 / K02 | 2.241.780 / −13.276 | 2.241.780 / −13.276 | PASS |
| 9 | 202504, AF | K01 | 170.447 | 170.447 | PASS |
| 10 | 202503, AF | K01 | 171.750 | 171.750 | PASS |
| 11 | 202504, AF | K02 | −1.303 | −1.303 | PASS |
| 12 | 202504, AF | K06 / K07 / K08 | 270 / 1.269 / −999 | 270 / 1.269 / −999 | PASS |
| 13 | 202504, AF | K04 | ≈ 7,50% (= 170.447 / 2.271.969) | 7,50% | PASS |
| 14 | 202504, Unknown | K01 / K06 / K07 | 206.687 / 1.591 / 1.936 | 206.687 / 1.591 / 1.936 | PASS |
| 16 | 202503–06, AF | K01 | 171.750 / 170.447 / 170.024 / 169.002 | 171.750 / 170.447 / 170.024 / 169.002 | PASS |
| 17 | 202503–06, AF | K06 | 72 / 270 / 255 / 350 | 72 / 270 / 255 / 350 | PASS |
| 18 | 202503–06, AF | K07 | 1.867 / 1.269 / 1.390 / 1.179 | 1.867 / 1.269 / 1.390 / 1.179 | PASS |
| 19 | 202503–06, AF | K02 | trống / −1.303 / −423 / −1.022 (từ K01 SQL) | trống / −1.303 / −423 / −1.022 | PASS |
| 20 | 202503, Unknown | K01 / K03 | 208.006 / trống | 208.006 / trống | PASS |
| 21 | 202504, Unknown | K03 | −0,63% (= (206.687 − 208.006) / 208.006) | −0,63% | PASS |
| 22 | 202503, Unknown | K04 | 9,09% (= 208.006 / 2.289.192) | 9,09% | PASS |
| 23 | 202504, AF | K03 | −0,76% (= −1.303 / 171.750) | −0,76% | PASS |
| 24 | 202503, 05, 06, toàn kỳ | K08 | −17.199 / −17.602 / −9.993 | −17.199 / −17.602 / −9.993 | PASS |
| 15 | Bỏ lọc agency sau ca 9–14 | K01 (202504) | 2.271.969 | 2.271.969 | PASS |

Số SQL của các ca 1–8 lấy từ `sql/07_g3_kpi.sql`; ca 9–14 và 16–22 chạy truy vấn theo `agency_code` trên `workforce_g3_tv4`:

```sql
-- AF, 4 tháng
SELECT m.month_key, m.k01, f.k06, f.k07
FROM (SELECT month_key, SUM(headcount) k01 FROM mart.workforce_monthly WHERE agency_code='AF' GROUP BY month_key) m
LEFT JOIN (SELECT month_key, SUM(accessions) k06, SUM(separations) k07 FROM mart.personnel_flows_monthly WHERE agency_code='AF' GROUP BY month_key) f USING (month_key)
ORDER BY 1;

-- Unknown
SELECT month_key, SUM(headcount) AS k01 FROM mart.workforce_monthly
WHERE agency_code='UNKNOWN' AND month_key IN (202503,202504) GROUP BY month_key ORDER BY month_key;
```

Kết quả SQL AF: 171750/72/1867 (03), 170447/270/1269 (04), 170024/255/1390 (05), 169002/350/1179 (06). Unknown: 208006 (03), 206687 (04). Các ca báo cáo (2, 7, 8, 12, 13, 15, 23, 24) chụp trực tiếp từ trang báo cáo với từng tháng được chọn riêng.

Lưu ý: ở DAX query view, kết quả hiện giá trị thô (K03 = −0,0075, K04 = 0,0910). Định dạng % xem ảnh chụp từ trang báo cáo.
Bằng chứng: `05_g3_months.png`, `06_g3_dax_AF_202504.png`, `07_g3_dax_unknown.png`, `08_g3_dax_total_202504.png`, `09_g3_unknown_row.png`, `10_g3_report_total_202504.png`, `11_g3_report_unknown_202504.png`, `12_g3_report_unknown_202503.png`, `13_g3_sql_AF.png`, `14_g3_sql_unknown.png`, `15_g3_report_total_202503.png`, `16_g3_report_total_202505.png`, `17_g3_report_total_202506.png`, `18_g3_report_AF_202504.png`, `19_g3_report_cleared_202504.png`.

## 6. Dimension catalog chính thức (L4-09)

`docs/08_dimension_catalog.csv` được cập nhật theo `reports/week3/08_dimension_observed.csv` của TV3:

| Dimension | Số dòng (G3) | Natural key | Hierarchy | Trạng thái |
|---|---:|---|---|---|
| `dw.dim_month` | 9 | `yyyymm` | năm > tháng | PROPOSED, TV4 đồng ý |
| `dw.dim_agency` | 493 | `(month_key, agency_code)` | chưa có | PARTIAL, đồng ý có điều kiện |
| `dw.dim_action_category` | 53 | `(month_key, family, category_code)` | family > category | PARTIAL, đồng ý có điều kiện |

Điểm duyệt: grain một dòng nguồn = một dòng Fact; Unknown key 0 giữ và hiện riêng; ba vai trò tháng (snapshot, report, effective). Tỷ lệ agency Unknown của Employment tháng 04 là 9,10% (206.687/2.271.969). Nhãn agency và category dẫn xuất còn PARTIAL (G3-D07). Dòng `NOT_IN_G2` (pay_plan + grade, duty_station, occupation) chưa được thêm.
Phối hợp TV3 kiểm sơ đồ vật lý: [điền kết quả / chưa làm].

## 7. Giới hạn đã biết

- Mart có grain tháng + cơ quan. Chưa có category, tháng hiệu lực, nghề, địa điểm, cấp bậc; do đó D2 theo loại hành động và K05 chưa làm được. Đề nghị TV3 thêm Mart tháng + cơ quan + category (giữ `category_key = 0` trong tổng).
- K09 tạm ẩn; K10 chưa tính.
- Nhóm Unknown lớn (Employment tháng 04: 206.687 dòng); nhãn agency và category còn PARTIAL.
- `dim_agency` có `agency_key` khác nhau theo tháng; luôn lọc và nhóm theo `agency_code`.
- Chỉ có số tổng hợp; không có dữ liệu cấp bản ghi, cột REDACTED hay lương trong file PBIX.
- Publish to web vẫn bị chặn (R02, xem `docs/10_publish_feasibility.md`); đang chờ phương án thay thế được duyệt.

## 8. Việc còn lại

- [ ] TV5 đối soát SQL–DAX độc lập (12 ca DAX PENDING trong báo cáo G3 của TV3)
- [ ] TV3 trả lời mục G3-D02/D03/D07 và Mart category
- [ ] TV2 rà nhãn agency PARTIAL (bảy nhãn đang review, issue #17)
- [ ] Dựng D1–D3 theo `docs/02_requirements.md` và `docs/10_dashboard_specs.md` (L4-10 đến L4-12)
- [ ] TV1 xử lý R02 và cập nhật tracker
