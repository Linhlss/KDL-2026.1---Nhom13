# L2-08 · Đối chiếu mapping và ERD với DDL G2

**23/11/2026 · REVIEW.** Nhánh tích hợp dùng đầu vào TV2 tại `e23de2c` và cập nhật bàn giao TV3 tại `3b30235`. Phạm vi thực chạy G2 dùng ba file kỳ 04/2025. [PR TV3](https://github.com/Linhlss/KDL-2026.1---Nhom13/pull/43) · [Issue L2-08](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/18)

## Kết quả sau đồng bộ

- **24 dòng DW.** [Mapping vật lý](04_source_to_target_mapping.csv) dùng các khóa `report_month_key`, `snapshot_month_key`, `effective_month_key`, `count_value`, nhãn Agency và một `dim_action_category` có cột `family`. Mapping ghi cả mã gốc, trạng thái lookup, cờ chất lượng và provenance. Cả 50 cột của ba Fact và ba Dimension đều có dòng truy vết.
- **30 đích thiết kế.** Mapping chỉ tới trường gốc đang lưu ở ODS cho nghề, địa điểm, nhóm tuổi, pay plan và grade. Lương có `annualized_adjusted_basic_pay`, `pay_value` và `pay_state` tại ODS. TV4 xác nhận phạm vi các chiều và KPI bổ sung trong bus matrix. [Issue bus matrix](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/32)
- **21 dòng K10 trước đối chiếu.** `audit.fk_lookup_coverage` đã có trong DDL. [Audit TV2](04_relationship_audit.csv) lưu SHA-256 của Parquet được kiểm theo từng file và trường. Luồng `init` và `all` so hash đó với inventory trước khi nạp. View chỉ hiển thị audit của file đang `LOADED`, còn hoạt động và khớp định danh lẫn SHA-256. `SAMPLE` và `NOT_CHECKED` để trống tử số. Tỷ lệ chỉ hiện với `VERIFIED` và mẫu số dương.
- **ETL lookup.** Phân loại mã Agency và action theo khoảng trắng đầu/cuối và chữ hoa/thường đối với `REDACTED`. Mã dùng làm khóa lookup vẫn so khớp nguyên văn. Ca kiểm sử dụng cả `001` và ` 001 ` để xác nhận số 0 đầu và khoảng trắng gốc được giữ. [ETL](../etl/g2_model.py) · [Ca kiểm](../tests/g2_model_checks.py)

Kiểm thử trên PostgreSQL 18.7 đã xác nhận **228 dòng mapping**, với **127 truy vấn SQL khác nhau** lập được kế hoạch. Các bộ kiểm model, K10, nạp nguồn và chạy lại đạt trên database thử riêng.

Lượt rà soát trước khi push chạy lại audit trên 12 Parquet. Cả 104 dòng chi tiết theo file có hash khớp inventory và 36 dòng tổng hợp để trống hash. Các số đo, lookup và bảng ngoại lệ khớp bản trước. Ca hồi quy K10 từ chối inventory có SHA-256 khác audit dù số dòng bằng nhau.

Replay `--job all --month 202504` trên PostgreSQL 18.7 giữ đúng **2.271.969 Employment**, **7.153 Accessions** và **24.088 Separations** từ nguồn đến Fact. Tổng measure của cả hai Mart khớp, lineage ODS → Fact trả 0 sai biệt cho cả ba họ. Đủ 43 Accessions và 61 Separations lệch kỳ được giữ. J06 ghi 21 phép kiểm đạt và 3 phép kiểm DAX chờ TV4/TV5. View K10 trả 26 kết quả theo file và trường, gồm 8 Employment, 9 Accessions và 9 Separations. Các tỷ lệ của kỳ này để trống theo phạm vi kiểm chứng của audit.

Sau khi nạp kỳ 04/2025, đọc K10 theo từng file và trường bằng câu SQL sau.

```sql
SELECT family, source_file, lookup_field, lookup_status, reference_coverage,
       eligible_rows, matched_rows, coverage_pct
FROM audit.fk_lookup_coverage
WHERE report_month = '202504'
ORDER BY family, lookup_field;
```

### Kịch bản duyệt Agency tháng 04/2025

Thử LEFT JOIN trên ba Parquet đã kiểm SHA-256, đưa đúng bảy mã `AH`, `FQ`, `HB`, `HU`, `IN`, `NN`, `TR` vào tập tra cứu thử nghiệm. Các nhãn đề xuất và căn cứ nằm trong [bảng review 131 khóa–tháng](../evidence/TV2_week2/ehri_label_review_131.csv).

| Họ | Số dòng nguồn | Agency Unknown theo lookup hiện hành | Agency Unknown nếu duyệt cả 7 nhãn |
| --- | ---: | ---: | ---: |
| Employment | 2.271.969 | 206.687 | 0 |
| Accessions | 7.153 | 1.591 | 0 |
| Separations | 24.088 | 1.936 | 0 |

TV4 xác nhận bảy nhãn trước khi đưa vào lookup chính. Hai mã Subelement `AF4F` và `ARE1` cần bằng chứng về phạm vi tổ chức. Các quyết định đó được ghi tại [issue #17](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/17).

## Đối chiếu trước đồng bộ DW

[Bảng đối chiếu](04_g2_ddl_comparison.csv) lưu lịch sử so sánh trên [mapping TV2 tại commit `e23de2c`](https://github.com/Linhlss/KDL-2026.1---Nhom13/blob/e23de2cb5cf8baea34335a2a525d307b41937699/docs/04_source_to_target_mapping.csv). Cột `tv3_validation_sql` ghi truy vấn theo tên vật lý ở lần đối chiếu đó.

| Kết quả | Dòng | Cách đọc |
| --- | ---: | --- |
| `EXACT_TARGET` | 100 | Cùng tên schema, bảng và cột, gồm đủ 67 dòng có đích ODS |
| `TARGET_CHANGED` | 24 | Có đích vật lý tương ứng với tên bảng hoặc cột DW khác |
| `ODS_ONLY` | 30 | Dữ liệu có ở ODS. Chiều hoặc cột Fact dự kiến chưa có trong DDL G2 |
| `NOT_IN_DDL` | 21 | Các dòng định nghĩa K10 tham chiếu bảng coverage dự kiến |
| `IMPLEMENTED_ONLY` | 40 | Bổ sung đối chiếu cho 25 cột DW và 15 cột dẫn xuất ODS mà mapping dự kiến chưa có dòng riêng |

Bốn dòng đầu cộng thành **175 dòng mapping gốc**. Bảng đối chiếu bao phủ đủ **50 cột vật lý** của ba Fact và ba Dimension TV3.

## ERD, khóa và vai trò tháng

| Phần kiểm | Kết quả |
| --- | --- |
| Source file → ODS | ERD v1 và DDL cùng dùng PK `raw_meta.source_file.file_id`, SHA-256 duy nhất và FK từ ODS về source file. DDL còn đặt duy nhất `filename` và cặp `(family, report_month)`. |
| Bảng ODS | Mapping, ERD v1 và bản SVG dùng đúng tên DDL cho cả ba họ. Hai bảng event dùng `ods_accessions_record` và `ods_separations_record`. |
| ODS → Fact | Mỗi Fact giữ grain một dòng Parquet. Cả ba dùng PK `(file_id, source_row_ordinal)` và FK ghép đến đúng bảng ODS. |
| Kỳ báo cáo | `manifest.report_month` đi vào `source_file.report_month` và ODS `report_month`. Cả ba Fact dùng `report_month_key` tham chiếu `dim_month.month_key`. |
| Kỳ snapshot | Employment lấy `snapshot_yyyymm` từ Parquet và tra `snapshot_month_key` riêng. |
| Kỳ hiệu lực | Hai Fact event dùng `effective_month_key` từ `personnel_action_effective_date_yyyymm` qua ODS `effective_month`. Kỳ báo cáo vẫn được lưu riêng. |

Đối chiếu dựa trên [ERD v1 TV2](../diagrams/04_relational_source_erd.drawio), [DDL ODS](https://github.com/Linhlss/KDL-2026.1---Nhom13/blob/cb4f55baf2fc6c47c40a81a07d6cef96fe13c445/sql/00_raw_ref_ods_ddl.sql), [DDL DW](https://github.com/Linhlss/KDL-2026.1---Nhom13/blob/cb4f55baf2fc6c47c40a81a07d6cef96fe13c445/sql/03_dw_ddl.sql) và [đường đi dữ liệu trong ETL](https://github.com/Linhlss/KDL-2026.1---Nhom13/blob/cb4f55baf2fc6c47c40a81a07d6cef96fe13c445/etl/g2_model.py#L171).

## Dimension và measure tại lần đối chiếu ban đầu

- **Tháng.** TV3 dùng `dim_month.yyyymm` và khóa số `month_key`. Khóa 0 đại diện kỳ nghiệp vụ Unknown. TV4 xác nhận dùng snapshot cho Employment và report month mặc định cho luồng event.
- **Agency và loại action.** Agency tra bằng `(month_key, agency_code)`. Accessions và Separations dùng chung `dim_action_category` với khóa tự nhiên `(month_key, family, category_code)` và khóa Fact `category_key`. Lookup chỉ dùng một bản ghi có nhãn `READY` duy nhất theo mã và tháng. Fact giữ mã gốc, trạng thái tra cứu và khóa 0 cho Unknown. Tính toàn vẹn của FK kỹ thuật và trạng thái `PARTIAL` của danh mục nghiệp vụ được đánh giá riêng. Các nhãn còn vướng có bằng chứng tại [bảng đối chiếu 131 khóa–tháng](../evidence/TV2_week2/ehri_label_review_131.csv).
- **Chiều hoãn.** Nghề, địa điểm, nhóm tuổi, grade/pay plan và Subelement có trường gốc ở ODS. TV4 cần xác nhận phạm vi các chiều dự kiến theo catalog. FK nghiệp vụ riêng cho Grade và khóa nhân viên xuyên ba họ ở `UNSUPPORTED`.
- **Measure.** Cả ba Fact dùng `count_value bigint`. Lương được ép sang `pay_value numeric` và gắn `pay_state` trong ODS. TV3 và TV4 cần xác nhận phạm vi KPI dùng lương trước khi chốt đích Fact.
- **K10.** `audit.fk_lookup_coverage` chưa có trong DDL. Giữ định nghĩa tử số là số dòng đủ điều kiện khớp đúng một khóa chính thức, mẫu số là số dòng đủ điều kiện. Tỷ lệ để trống khi nguồn chưa xác minh hoặc mẫu số bằng 0. [Audit nguồn TV2](04_relationship_audit.csv)
- **Trạng thái mã nguồn.** `g2_model.py` hiện so sánh mã Agency và action trực tiếp với chuỗi rỗng và `REDACTED`. Quy tắc TV2 phân loại sau khi bỏ khoảng trắng đầu/cuối và so `REDACTED` không phân biệt hoa thường, đồng thời lưu mã gốc. TV3 cần đối chiếu riêng hành vi này khi review J02. [Mã nạp Fact](https://github.com/Linhlss/KDL-2026.1---Nhom13/blob/cb4f55baf2fc6c47c40a81a07d6cef96fe13c445/etl/g2_model.py#L175) · [J02](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/27)

## Bằng chứng tại lần đối chiếu ban đầu

- Khởi tạo nguyên văn DDL từ PR #43 trong PostgreSQL 18.7 cô lập bằng PGlite 0.5.17. Sửa tên ODS cập nhật **46 đích mapping** và **54 dòng SQL kiểm**, gồm các truy vấn lineage và tra nhãn đọc ODS. Số dòng SQL trong mapping lập được kế hoạch tăng từ **51 lên 105** trên tổng 175. Còn 52 dòng lỗi tên bảng và 18 dòng lỗi tên cột liên quan DW và K10. Toàn bộ **116 câu SQL khác nhau** ở cột `tv3_validation_sql` lập được kế hoạch, bao phủ **154 dòng** có đích vật lý. [PGlite](https://pglite.dev/docs/)
- **15 ca lineage dữ liệu thử đạt** trên đúng ba cặp bảng của DDL. Mỗi cặp có ca hợp lệ trả về 0 lỗi, ODS thiếu Fact được báo và DDL chặn Fact thừa, trùng hoặc NULL bằng FK, PK và ràng buộc bắt buộc tương ứng.
- **12 ca kiểm vai trò tháng đạt** trên cùng dữ liệu thử. Hai Fact event giữ được tháng hiệu lực khác tháng báo cáo. Khi cố tình làm lệch tháng báo cáo giữa ODS và Fact, truy vấn báo đúng một dòng lỗi và phép kiểm tháng nghiệp vụ vẫn trả 0 lỗi.
- Đọc lại trực tiếp ba Parquet 04/2025, khớp **2.271.969 Employment**, **7.153 Accessions**, **24.088 Separations** và giữ **43 Accessions**, **61 Separations** lệch kỳ. TV3 đã công bố 0 sai biệt lineage cho từng họ trong PostgreSQL trên chính kỳ này. [Báo cáo đối soát TV3](https://github.com/Linhlss/KDL-2026.1---Nhom13/blob/cb4f55baf2fc6c47c40a81a07d6cef96fe13c445/reports/07_reconciliation.csv) · [Kiểm trực tiếp nguồn của TV3](https://github.com/Linhlss/KDL-2026.1---Nhom13/blob/cb4f55baf2fc6c47c40a81a07d6cef96fe13c445/evidence/TV3_week2/07_source_direct_crosscheck.txt)

Để kiểm lại các câu truy vấn, khởi tạo database kiểm tra bằng `etl/g2_pipeline.py --job init` trên nhánh tích hợp theo [runbook](07_runbook.md#tạo-bảng-và-chạy), rồi chạy lệnh dưới tại gốc repo với cấu hình kết nối của máy.

```powershell
$tv3Db = 'workforce_dw_g2_check'
@'
from csv import DictReader

with open("docs/04_source_to_target_mapping.csv", encoding="utf-8", newline="") as source:
    statements = dict.fromkeys(row["validation_sql"] for row in DictReader(source))
for sql in statements:
    if sql:
        print("EXPLAIN (COSTS OFF) " + sql + ";")
'@ | python -X utf8 -B - | psql -X -v ON_ERROR_STOP=1 -d $tv3Db
```

Chạy thêm `python tests/g2_model_checks.py --config configs/.env` và `python tests/g2_coverage_checks.py --config configs/.env` trên máy có PostgreSQL và quyền tạo database kiểm thử. TV5 kiểm độc lập trước khi ghi PASS tại issue #18.
