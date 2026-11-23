# Quyết định mô hình và dependency G3

Nhánh G3 kế thừa G2 tại `3b30235`, giữ DDL và grain Fact một dòng nguồn. Cột `count_value=1` được enforce trước publish, tương ứng record_count/event_count. Mã gốc, trạng thái lookup, DQ và lineage file_id–ordinal vẫn còn. Không nối Fact–Fact, không tạo employee_id.

| Fact | Tháng báo cáo | Snapshot month | Effective month | Agency | Action category |
| --- | --- | --- | --- | --- | --- |
| fact_employment_snapshot | Có, lineage | Vai trò K01 | Không | Theo kỳ | Không |
| fact_accessions | Vai trò K06 | Không | Vai trò riêng | Theo kỳ | Family Accessions |
| fact_separations | Vai trò K07 | Không | Vai trò riêng | Theo kỳ | Family Separations |

Đây là ma trận thực thi để TV4 review, chưa thay bus matrix/catalog do TV4 duyệt. `dw.dim_month` dùng YYYYMM + Unknown 0. Agency natural key = (month_key, agency_code); category natural key = (month_key, family, category_code). Surrogate key upsert giữ nguyên trên rerun, có thể có khoảng trống sequence. Nhãn lookup chỉ dùng khi đúng một dòng READY cho toàn key TV2; dữ liệu chưa READY/mơ hồ/missing/REDACTED vẫn vào Unknown, giữ raw và lookup_state. Nhãn và phạm vi mã dẫn xuất còn PARTIAL.

Mỗi Fact giữ FK về ODS và Dimension có PK/UNIQUE/FK vật lý. Month Dimension phủ mọi tháng báo cáo và tháng nghiệp vụ hợp lệ quan sát được, kể cả ngoài 03–06. Các hierarchy tổ chức/nghề/địa lý/grade chưa có catalog/audit được duyệt nên không tự thêm FK hoặc suy quan hệ.

Hai Mart giữ grain tháng/cơ quan đã chạy ở G2, mở rộng sang đủ bốn kỳ. Workforce dùng snapshot month; flows dùng report month, aggregate riêng từng event rồi UNION ALL. Mart không có category key; các nhóm nghề/địa lý/cấp bậc hoặc category trong kế hoạch chỉ thêm sau khi TV4 thống nhất grain. Đây là dependency thiết kế, không gọi là tính năng đã triển khai.

Catalog quan sát có số dòng và ba ví dụ thật mỗi Dimension do pipeline xuất ở [08_dimension_observed.csv](../reports/week3/08_dimension_observed.csv), kèm provenance, Unknown, chính sách version, Fact dùng và cột approval PROPOSED_PENDING_TV4. [Runbook G3](TV3_week3_runbook.md) có lệnh tái tạo và SQL KPI.

Ngày 23/11/2026: GitHub main còn `f109bbf`, PR G2 #43 mở; nhánh `tv4/week1` tại `d3c9359` chưa có bus matrix/Dimension catalog trong tree đã kiểm. Không suy trạng thái này từ tài liệu main cũ. Dependency G2, thiết kế TV4 và review độc lập TV5 được giữ mở trong [báo cáo tuần 3](../reports/TV3_week3_summary.md). Chưa ghi nhận TV2/TV4/TV5 đã ký xác nhận.
