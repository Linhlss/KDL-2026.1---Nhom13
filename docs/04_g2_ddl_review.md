# L2-08 · Đối chiếu mapping và ERD với DDL G2

**23/11/2026 · REVIEW.** TV2 đối chiếu mapping và ERD tại commit `1e3b5fc` với DDL và code nạp tại commit `cb4f55b` của TV3. Phạm vi thực chạy của TV3 là ba file kỳ 04/2025. Bus matrix và Dimension catalog cần TV4 xác nhận. [Issue L2-08](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/18) · [PR TV3](https://github.com/Linhlss/KDL-2026.1---Nhom13/pull/43) · [Bus matrix TV4](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/32)

## Kết quả theo từng trường

[Bảng đối chiếu](04_g2_ddl_comparison.csv) ghi số dòng trong [mapping TV2](04_source_to_target_mapping.csv), đích dự kiến, đích vật lý TV3, kiểu và khả năng nhận NULL theo catalog. `tv3_validation_sql` chứa truy vấn theo tên vật lý của TV3. Cột `original_sql_status` ghi kết quả chạy `EXPLAIN` trên câu SQL trong mapping ban đầu.

| Kết quả | Dòng | Cách đọc |
| --- | ---: | --- |
| `EXACT_TARGET` | 54 | Cùng tên schema, bảng và cột |
| `TARGET_CHANGED` | 70 | Có đích vật lý tương ứng với tên bảng hoặc cột khác |
| `ODS_ONLY` | 30 | Dữ liệu có ở ODS. Chiều hoặc cột Fact dự kiến chưa có trong DDL G2 |
| `NOT_IN_DDL` | 21 | Các dòng định nghĩa K10 tham chiếu bảng coverage dự kiến |
| `IMPLEMENTED_ONLY` | 40 | Bổ sung đối chiếu cho 25 cột DW và 15 cột dẫn xuất ODS mà mapping dự kiến chưa có dòng riêng |

Bốn dòng đầu cộng thành **175 dòng mapping gốc**. Bảng đối chiếu bao phủ đủ **50 cột vật lý** của ba Fact và ba Dimension TV3.

## ERD, khóa và vai trò tháng

| Phần kiểm | Kết quả |
| --- | --- |
| Source file → ODS | ERD v1 và DDL cùng dùng PK `raw_meta.source_file.file_id`, SHA-256 duy nhất và FK từ ODS về source file. DDL còn đặt duy nhất `filename` và cặp `(family, report_month)`. |
| Bảng ODS | Employment khớp tên. ERD ghi `ods_accession_record` và `ods_separation_record`, còn DDL dùng `ods_accessions_record` và `ods_separations_record`. |
| ODS → Fact | Mỗi Fact giữ grain một dòng Parquet. Cả ba dùng PK `(file_id, source_row_ordinal)` và FK ghép đến đúng bảng ODS. |
| Kỳ báo cáo | `manifest.report_month` đi vào `source_file.report_month` và ODS `report_month`. Cả ba Fact dùng `report_month_key` tham chiếu `dim_month.month_key`. |
| Kỳ snapshot | Employment lấy `snapshot_yyyymm` từ Parquet và tra `snapshot_month_key` riêng. |
| Kỳ hiệu lực | Hai Fact event dùng `effective_month_key` từ `personnel_action_effective_date_yyyymm` qua ODS `effective_month`. Kỳ báo cáo vẫn được lưu riêng. |

Đối chiếu dựa trên [ERD v1 TV2](../diagrams/04_relational_source_erd.drawio), [DDL ODS](https://github.com/Linhlss/KDL-2026.1---Nhom13/blob/cb4f55baf2fc6c47c40a81a07d6cef96fe13c445/sql/00_raw_ref_ods_ddl.sql), [DDL DW](https://github.com/Linhlss/KDL-2026.1---Nhom13/blob/cb4f55baf2fc6c47c40a81a07d6cef96fe13c445/sql/03_dw_ddl.sql) và [đường đi dữ liệu trong ETL](https://github.com/Linhlss/KDL-2026.1---Nhom13/blob/cb4f55baf2fc6c47c40a81a07d6cef96fe13c445/etl/g2_model.py#L171).

## Dimension, measure và các mục cần xác nhận

- **Tháng.** TV3 dùng `dim_month.yyyymm` và khóa số `month_key`. Khóa 0 đại diện kỳ nghiệp vụ Unknown. TV4 xác nhận dùng snapshot cho Employment và report month mặc định cho luồng event.
- **Agency và loại action.** Agency tra bằng `(month_key, agency_code)`. Accessions và Separations dùng chung `dim_action_category` với khóa tự nhiên `(month_key, family, category_code)` và khóa Fact `category_key`. Lookup chỉ dùng một bản ghi có nhãn `READY` duy nhất theo mã và tháng. Fact giữ mã gốc, trạng thái tra cứu và khóa 0 cho Unknown. Tính toàn vẹn của FK kỹ thuật và trạng thái `PARTIAL` của danh mục nghiệp vụ được đánh giá riêng. Các nhãn còn vướng có bằng chứng tại [bảng đối chiếu 131 khóa–tháng](../evidence/TV2_week2/ehri_label_review_131.csv).
- **Chiều hoãn.** Nghề, địa điểm, nhóm tuổi, grade/pay plan và Subelement có trường gốc ở ODS. TV4 cần xác nhận phạm vi các chiều dự kiến theo catalog. FK nghiệp vụ riêng cho Grade và khóa nhân viên xuyên ba họ ở `UNSUPPORTED`.
- **Measure.** Cả ba Fact dùng `count_value bigint`. Lương được ép sang `pay_value numeric` và gắn `pay_state` trong ODS. TV3 và TV4 cần xác nhận phạm vi KPI dùng lương trước khi chốt đích Fact.
- **K10.** `audit.fk_lookup_coverage` chưa có trong DDL. Giữ định nghĩa tử số là số dòng đủ điều kiện khớp đúng một khóa chính thức, mẫu số là số dòng đủ điều kiện. Tỷ lệ để trống khi nguồn chưa xác minh hoặc mẫu số bằng 0. [Audit nguồn TV2](04_relationship_audit.csv)
- **Trạng thái mã nguồn.** `g2_model.py` hiện so sánh mã Agency và action trực tiếp với chuỗi rỗng và `REDACTED`. Quy tắc TV2 phân loại sau khi bỏ khoảng trắng đầu/cuối và so `REDACTED` không phân biệt hoa thường, đồng thời lưu mã gốc. TV3 cần đối chiếu riêng hành vi này khi review J02. [Mã nạp Fact](https://github.com/Linhlss/KDL-2026.1---Nhom13/blob/cb4f55baf2fc6c47c40a81a07d6cef96fe13c445/etl/g2_model.py#L175) · [J02](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/27)

## Bằng chứng kiểm

- Khởi tạo nguyên văn DDL từ PR #43 trong PostgreSQL 18.7 cô lập bằng PGlite 0.5.17. Kiểm tra mã blob Git của ba file DDL trước khi chạy. PostgreSQL xác nhận **51/175** dòng SQL cũ lập được kế hoạch truy vấn. Có **106** dòng lỗi tên bảng và **18** dòng lỗi tên cột. Toàn bộ **116 câu SQL khác nhau** ở cột `tv3_validation_sql` lập được kế hoạch, bao phủ **154 dòng** có đích vật lý. [PGlite](https://pglite.dev/docs/)
- **15 ca lineage dữ liệu thử đạt** trên đúng ba cặp bảng của DDL. Mỗi cặp có ca hợp lệ trả về 0 lỗi, ODS thiếu Fact được báo và DDL chặn Fact thừa, trùng hoặc NULL bằng FK, PK và ràng buộc bắt buộc tương ứng.
- **12 ca kiểm vai trò tháng đạt** trên cùng dữ liệu thử. Hai Fact event giữ được tháng hiệu lực khác tháng báo cáo. Khi cố tình làm lệch tháng báo cáo giữa ODS và Fact, truy vấn báo đúng một dòng lỗi và phép kiểm tháng nghiệp vụ vẫn trả 0 lỗi.
- Đọc lại trực tiếp ba Parquet 04/2025, khớp **2.271.969 Employment**, **7.153 Accessions**, **24.088 Separations** và giữ **43 Accessions**, **61 Separations** lệch kỳ. TV3 đã công bố 0 sai biệt lineage cho từng họ trong PostgreSQL trên chính kỳ này. [Báo cáo đối soát TV3](https://github.com/Linhlss/KDL-2026.1---Nhom13/blob/cb4f55baf2fc6c47c40a81a07d6cef96fe13c445/reports/07_reconciliation.csv) · [Kiểm trực tiếp nguồn của TV3](https://github.com/Linhlss/KDL-2026.1---Nhom13/blob/cb4f55baf2fc6c47c40a81a07d6cef96fe13c445/evidence/TV3_week2/07_source_direct_crosscheck.txt)

Để kiểm lại các câu truy vấn, khởi tạo database kiểm tra bằng [runbook TV3 tại commit đã đối chiếu](https://github.com/Linhlss/KDL-2026.1---Nhom13/blob/cb4f55baf2fc6c47c40a81a07d6cef96fe13c445/docs/07_runbook.md#tạo-bảng-và-chạy), rồi chạy ở gốc repo TV2 với cấu hình kết nối của máy.

```powershell
$tv3Db = 'workforce_dw_g2_check'
@'
from csv import DictReader

with open("docs/04_g2_ddl_comparison.csv", encoding="utf-8", newline="") as source:
    statements = dict.fromkeys(row["tv3_validation_sql"] for row in DictReader(source))
for sql in statements:
    if sql:
        print("EXPLAIN (COSTS OFF) " + sql + ";")
'@ | python -X utf8 -B - | psql -X -v ON_ERROR_STOP=1 -d $tv3Db
```

TV3 xác nhận đích vật lý và các khác biệt về cột. TV4 đối chiếu bus matrix, KPI và cách hiển thị Unknown. TV5 kiểm độc lập trước khi ghi PASS tại issue #18.
