# Thiết kế thực thi G2 của TV3

Nhánh `tv3/g2-pipeline` tích hợp đầu vào TV2 tại commit `8f9ea8d26b529381ce4d6bf69ee2d9f7e3536448`, trên nền `main` tại `f109bbff05726cce6f231ee9644a170b51251f4e`. Mô hình tháng 04/2025 là bản thực thi để TV4 review grain, Dimension và quy tắc Unknown. TV4 chưa bàn giao bus matrix/catalog và chưa duyệt thiết kế này.

## Nguồn và khóa

Inventory, SHA-256 và schema hash lấy từ [gói TV2](04_source_model_handoff.md). `raw_meta.source_file` đăng ký một file/version cụ thể. Ba bảng Staging và ba bảng ODS giữ một dòng cho mỗi dòng Parquet. Khóa `(file_id, source_row_ordinal)` truy vết đúng dòng theo thứ tự đọc, ordinal bắt đầu từ 1 và tăng xuyên batch.

Các cột gốc giữ dạng text. ODS bổ sung `report_month`, `count_value`, `effective_month`, `pay_value`, `pay_state` và `dq_flags`. NULL, chuỗi rỗng và REDACTED vẫn có thể kiểm lại từ cột gốc. Tháng báo cáo lấy từ inventory; tháng snapshot và tháng hiệu lực giữ theo nguồn.

Một file/version/hash đã nạp hợp lệ được kiểm lại rồi ghi SKIPPED khi chạy lại. Tên file đã đăng ký mà hash đổi, hoặc phiên bản mới cho cùng family/tháng, phải được nhóm xác minh trước khi nạp. Dữ liệu các kỳ khác được giữ theo `file_id`. Lượt nạp và lỗi có `run_id`, code version cùng bằng chứng audit.

## Grain và Dimension dự kiến

| Bảng | Grain và vai trò thời gian |
| --- | --- |
| `dw.fact_employment_snapshot` | Một dòng nguồn Employment; `snapshot_month_key` cho K01, thêm `report_month_key` để truy vết kỳ file |
| `dw.fact_accessions` | Một dòng nguồn Accessions; `report_month_key` và `effective_month_key` riêng |
| `dw.fact_separations` | Một dòng nguồn Separations; `report_month_key` và `effective_month_key` riêng |
| `dw.dim_month` | Một kỳ YYYYMM hợp lệ, dùng nhiều vai trò tháng; khóa 0 dành Unknown |
| `dw.dim_agency` | Một mã agency trong một tháng báo cáo, surrogate key; nhãn từ lookup TV2 đã qua gate READY |
| `dw.dim_action_category` | Một category trong một family và tháng báo cáo, surrogate key; nhãn từ lookup TV2 READY |

Mỗi Fact giữ khóa nguồn và FK đến đúng bảng ODS. Điều này cho phép kiểm thiếu/thừa/trùng dòng giữa ODS và Fact. Agency và category dùng lookup dẫn xuất có provenance `DERIVED_LOOKUP`, trạng thái xác minh `PARTIAL`. Chỉ khóa có một nhãn được TV2 đánh dấu READY mới được dùng. Mã gốc và trạng thái lookup vẫn nằm trong Fact. Nhóm REVIEW, UNKNOWN hoặc mã không khớp dùng surrogate key 0, giữ nguồn và có số đo để review.

TV4 cần duyệt grain một dòng nguồn, phạm vi agency theo tháng, việc gộp hai loại category vào một Dimension có cột family, cách trình bày Unknown và các role tháng trong Power BI. Các chiều nghề, địa điểm, grade và hierarchy sẽ được thêm theo catalog và audit đủ căn cứ của nhóm.

Mô hình Power BI cho bản dump tổng hợp được đề xuất trong [gói TV4](../handoff/TV3_G2/README.md): `dim_month` và `dim_agency` lọc một chiều trực tiếp tới cả hai Mart. Dùng slicer Dimension; tránh tạo thêm đường lọc Month → Agency hoặc Mart → Mart. `dim_agency` key 0 có tháng Unknown riêng, nên lọc tháng bằng `dim_month` trực tiếp tới Mart để vẫn giữ nhóm Unknown của tháng được chọn. Đây là đề xuất chờ TV4 xác nhận.

Lượt chạy tháng 04 giữ 206.687 dòng Employment, 1.591 dòng Accessions và 1.936 dòng Separations trong agency key 0 do lookup agency chưa có nhãn READY duy nhất. Tổng measure toàn kỳ vẫn khớp nguồn. Cần TV2/TV4 xử lý nhãn REVIEW và quyết định hiển thị Unknown trước khi sử dụng slicer agency để nhận xét đầy đủ theo cơ quan. [Kết quả model](../evidence/TV3_week2/01_pipeline_run.txt) và [báo cáo bàn giao](../reports/TV3_week2_summary.md) ghi số đo.

## Mart và KPI

| Mart | Grain | Measure |
| --- | --- | --- |
| `mart.workforce_monthly` | Snapshot month + agency key | `headcount = SUM(count_value)`, `source_rows` |
| `mart.personnel_flows_monthly` | Report month + agency key | `accessions`, `separations`, `net_actions = accessions - separations`, `source_rows` |

Mart flows tổng hợp từng Fact sự kiện trước rồi UNION ALL về grain chung. Mỗi KPI dùng cùng kỳ và filter khi so với SQL/DAX. K01 tháng 04 cần toàn bộ Employment v4. `count_value` không hợp lệ phải được sửa hoặc xác minh trước khi build model. SQL tham chiếu nằm trong [05_g2_kpi.sql](../sql/05_g2_kpi.sql).

Hai Mart hiện chỉ có grain tháng/cơ quan. Category Dimension chưa liên kết được tới Mart bằng category key; TV4 cần thống nhất grain và Mart bổ sung nếu muốn phân tích theo category.

## Phần chờ xác nhận

- **TV4** giao bus matrix, Dimension catalog và review grain/Unknown/time roles trên PR; tự restore dữ liệu bàn giao, SELECT Mart và kết nối PBIX.
- **TV5** replay từ Parquet trên môi trường riêng, kiểm count/ordinal/lineage/lookup/rollback, đối soát SQL–DAX và ghi kết luận độc lập.
- **TV2/TV5** review các khóa còn PARTIAL và ngoại lệ trong [biên bản ERD cập nhật](TV3_week1_erd_review.md). Các surrogate FK kỹ thuật trong DW có thể kiểm toàn vẹn bằng SQL; trạng thái xác minh miền mã vẫn theo audit nguồn.

G2 được chốt theo kết quả tích hợp Power BI và review độc lập của nhóm. Kết quả SQL do TV3 chạy là bằng chứng kỹ thuật để reviewer tái hiện.
