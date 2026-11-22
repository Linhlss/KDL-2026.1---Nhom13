# Bus matrix v0 (L4-03)

**Task:** L4-03 — Owner: TV4 — Review: TV3, TV1
**Trạng thái:** REVIEW (bản nháp v0; chưa nghiệm thu)
**Nguồn thiết kế:** `sql/03_dw_ddl.sql` và `docs/TV3_g2_model_decisions.md` (nhánh `tv3/g2-pipeline`, PR #43); audit TV2 (PR #42).
**Phạm vi dữ liệu hiện có:** tháng 04/2025. Chưa có đủ 4 tháng trong DW G2.

## 1. Grain của từng Fact

| Fact | Grain (một dòng Fact là gì) | Measure | Loại cộng dồn |
|---|---|---|---|
| `dw.fact_employment_snapshot` | 1 dòng nguồn trong file Employment. Khóa `(file_id, source_row_ordinal)` | `count_value` | **Bán cộng dồn.** Cộng theo agency trong một snapshot; không cộng qua các tháng |
| `dw.fact_accessions` | 1 dòng nguồn trong file Accessions | `count_value` | Cộng dồn được |
| `dw.fact_separations` | 1 dòng nguồn trong file Separations | `count_value` | Cộng dồn được |

Ghi chú:
- Mỗi dòng Fact trỏ về đúng một dòng ODS qua `(file_id, source_row_ordinal)`, nên truy vết được từng dòng.
- Nguồn **không có mã nhân viên**: không đếm người duy nhất, không nối Fact với Fact.
- K02 (thay đổi headcount, từ hai snapshot) khác K08 (Accessions − Separations, đơn vị "lượt"). Không gộp hai khái niệm.

## 2. Bus matrix

| Dimension / vai trò | `fact_employment_snapshot` | `fact_accessions` | `fact_separations` |
|---|---|---|---|
| `dim_month` — **snapshot** | ✔ `snapshot_month_key` (mặc định, dùng cho K01) | – | – |
| `dim_month` — **report** | ✔ `report_month_key` (truy vết kỳ file) | ✔ `report_month_key` (**mặc định**, K06/K07) | ✔ `report_month_key` (**mặc định**) |
| `dim_month` — **effective** | – | ✔ `effective_month_key` (quan hệ không hoạt động; dùng `USERELATIONSHIP`) | ✔ `effective_month_key` (quan hệ không hoạt động) |
| `dim_agency` | ✔ `agency_key` | ✔ `agency_key` | ✔ `agency_key` |
| `dim_action_category` (family = accessions) | – | ✔ `category_key` | – |
| `dim_action_category` (family = separations) | – | – | ✔ `category_key` |

Quy tắc dùng chung:
1. Các Fact chỉ so sánh với nhau qua Dimension chung (tháng, agency). Không có quan hệ Fact–Fact.
2. `dim_month` và `dim_agency` là Dimension chung (conformed) giữa cả ba Fact.
3. Báo cáo mặc định theo `report_month`. Xem theo `effective_month` chỉ khi người dùng chọn, kèm ghi chú: có dòng sự kiện với tháng hiệu lực khác tháng của file (tháng 04: 43 Accessions và 61 Separations; toàn bộ 4 tháng: 593 dòng theo audit TV2).
4. Trong Power BI, một quan hệ `dim_month` → Fact đặt hoạt động (snapshot cho Employment, report cho hai Fact sự kiện); các vai trò còn lại là quan hệ không hoạt động hoặc bản sao `dim_month` theo vai trò.
5. Dimension `dim_action_category` nối Fact sự kiện, luôn lọc theo `family` tương ứng để không lẫn Accessions với Separations.

## 3. Ánh xạ KPI và Fact

| KPI | Fact | Dimension dùng |
|---|---|---|
| K01 Headcount | employment | month (snapshot), agency |
| K02, K03 Thay đổi, MoM % | employment | month (snapshot, tháng liền trước) |
| K04, K05 Tỷ trọng agency, nhóm | employment | month, agency |
| K06 Accessions | accessions | month (report), agency, category |
| K07 Separations | separations | month (report), agency, category |
| K08 Chênh lệch sự kiện | accessions + separations | month (report), agency (qua Dimension chung) |
| K09 Xếp hạng đóng góp | employment (hoặc hai Fact sự kiện) | agency |
| K10 Độ phủ chất lượng dữ liệu | cả ba | `agency_lookup_state`, `category_lookup_state`, `dq_flags` |

## 4. Ranh giới của bản v0

- Chưa có chiều nghề, địa điểm, grade, pay plan trong DW G2. TV3 sẽ thêm khi audit đủ căn cứ. Xem `08_dimension_catalog.csv` (dòng `NOT_IN_G2`).
- `grade` không dùng một mình (UNSUPPORTED); khi có sẽ dùng cặp `pay_plan` + `grade`.
- `duty_station` khoảng 46% REDACTED nên không đưa vào slicer chính.
- Trạng thái của agency và category là `PARTIAL` do lookup tham chiếu chưa READY.

## 5. Kết quả duyệt thiết kế TV4 (gửi TV3)

| Hạng mục TV3 đề xuất | Kết luận TV4 | Điều kiện / ghi chú |
|---|---|---|
| Grain: 1 dòng nguồn = 1 dòng Fact | Đồng ý | Giữ khóa truy vết; không nối Fact–Fact |
| Key 0 = Unknown (agency, category, month) | Đồng ý có điều kiện | Dashboard phải hiện nhóm Unknown và ghi số dòng; tháng 04 có 206.687 / 1.591 / 1.936 dòng Employment / Accessions / Separations ở agency Unknown |
| 3 vai trò thời gian (snapshot, report, effective) | Đồng ý | Mặc định report; effective qua `USERELATIONSHIP` |
| Một `dim_action_category` có cột `family` | Đồng ý | Spec D2 sửa theo bảng này; luôn lọc theo `family` |
| `dim_agency` theo từng tháng (UNIQUE `month_key`, `agency_code`) | **Cần xem lại** | Cùng một agency có `agency_key` khác nhau mỗi tháng. So sánh nhiều tháng (K02, K03) phải dùng `agency_code`. Đề nghị TV3 cân nhắc thêm Dimension agency ổn định qua các tháng |
| Mart: `workforce_monthly`, `personnel_flows_monthly` | Đồng ý để dựng MVP | Đối soát K01/K06/K07 tháng 04 trên Windows trước khi chốt |
| Dữ liệu mới có tháng 04/2025 | **Cần bổ sung** | D1 và D3 cần đủ các tháng; hỏi TV3 lịch nạp 03, 05, 06 |

Chưa có mục nào được ghi PASS; việc chốt G2 phụ thuộc kết quả restore, kết nối Power BI và đối soát SQL–DAX của TV4/TV5.

## 6. Việc còn lại

- [ ] TV3 phản hồi các mục "Cần xem lại / Cần bổ sung"
- [ ] TV1 review
- [ ] Cập nhật `10_dashboard_specs.md` mục 4 theo tên bảng và cột trong tài liệu này
- [ ] Cập nhật sau khi TV4 restore DB và nối Power BI (L4-05/L4-06)
