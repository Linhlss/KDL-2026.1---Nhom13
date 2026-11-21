# Bàn giao tuần 2 của TV3

Nhánh `tv3/g2-pipeline` triển khai MVP tháng 04/2025 dựa trên đầu vào TV2 commit `8f9ea8d26b529381ce4d6bf69ee2d9f7e3536448`, tích hợp từ `main` commit `f109bbff05726cce6f231ee9644a170b51251f4e`. [Runbook](../docs/07_runbook.md) ghi cách chạy và bàn giao. [Thiết kế G2](../docs/TV3_g2_model_decisions.md) ghi các lựa chọn kỹ thuật cần TV4 review.

| Task | Trạng thái bàn giao | Sản phẩm | Review còn cần |
| --- | --- | --- | --- |
| L3-05 · DDL nguồn/ODS/audit | REVIEW | [DDL](../sql/00_raw_ref_ods_ddl.sql), 7 schema, PK nguồn và metadata file | TV2 đối chiếu ERD, TV5 replay DDL trên DB sạch |
| L3-06 · J00/J01 ba nguồn | REVIEW | Entrypoint pipeline, kiểm manifest và COPY theo batch, log theo file/run | TV5 kiểm trực tiếp Parquet, checksum, số dòng, ordinal và xử lý lỗi |
| J02 · Chuẩn hóa | REVIEW | Giữ raw, thêm typed count/pay, time roles và DQ | TV2 review quy tắc, TV5 kiểm before–after |
| L3-04 · Review ERD | REVIEW | [Biên bản cập nhật G2](../docs/TV3_week1_erd_review.md) theo audit/mapping TV2 | TV5 kiểm lineage và quan hệ khóa độc lập |
| L3-07 · DW/Mart | PROPOSED · chờ TV4 | [3 Fact/Dimension](../sql/03_dw_ddl.sql), [2 Mart](../sql/04_create_marts.sql) | TV4 giao bus matrix/catalog và duyệt grain, Unknown, time roles; TV5 kiểm PK/FK |
| L3-08 · MVP tích hợp | BLOCKED tại bước TV4/TV5 | Luồng tháng 04, [SQL K01/K06/K07](../sql/05_g2_kpi.sql) và gói chuyển DB | TV4 tự restore/kết nối PBIX, TV5 đối soát SQL–DAX và ký kết quả |
| L3-09 · Sơ đồ | REVIEW | Architecture, ETL data flow và DW physical overall cùng bản xem | TV4/TV5 đối chiếu với DDL và hệ thống chạy |

## Phạm vi và điều kiện nghiệm thu

Đã chạy ba file MVP Employment v4, Accessions v5 và Separations v5 của kỳ 202504 trên PostgreSQL cục bộ. [Đầu ra chạy thực](../evidence/TV3_week2/01_pipeline_run.txt), [log nạp](07_load_log.csv), [before–after](07_before_after.csv) và [reconciliation SQL](07_reconciliation.csv) ghi kết quả và phạm vi.

Inventory và manifest 12 file được tiếp nhận theo commit TV2. TV3 quét lại metadata và tính lại SHA-256 cục bộ cho đúng ba file 202504 dùng trong MVP. Chín file các kỳ còn lại chưa được TV3 tính lại hash hoặc nạp trong lượt chạy G2 này; audit đủ bốn kỳ trong đầu vào vẫn thuộc gói bằng chứng TV2.

| Họ | Nguồn = Staging = ODS = Fact | Tổng measure tại Mart | Khác biệt khóa ODS–Fact | Dòng lệch kỳ được giữ |
| --- | ---: | ---: | ---: | ---: |
| Employment | 2.271.969 | 2.271.969 | 0 | 0 |
| Accessions | 7.153 | 7.153 | 0 | 43 |
| Separations | 24.088 | 24.088 | 0 | 61 |

`mart.workforce_monthly` có 114 nhóm và `mart.personnel_flows_monthly` có 88 nhóm trong lượt chạy tháng 04. K01/K06/K07 khớp tổng nguồn tại SQL. Các kết quả này do TV3 chạy; xác nhận SQL–DAX và review độc lập đang chờ TV4/TV5.

Đã chạy lại bằng mã tại commit `36c50ad71024f356d4c9ed944377e623c217639f`. J01/J02 của cả ba file ghi SKIPPED, rebuild model giữ nguyên tổng và J06 có 18 phép kiểm SQL PASS. Ba dòng đối soát DAX giữ trạng thái PENDING. [Bằng chứng chạy lại](../evidence/TV3_week2/05_repeat_pipeline.txt) và CSV log ghi run_id cùng code version.

Kiểm hồi quy dùng dữ liệu tổng hợp và database riêng đã PASS các trường hợp lookup agency trùng/khác nhãn được chuyển Unknown, giữ kỳ khác khi build lại, chạy lại model giữ tổng số, count lỗi chặn build và bảo toàn Mart trước đó. Test nguồn cũng PASS rerun SKIPPED, file thiếu, checksum sai, sai version trong manifest, COPY lỗi rollback và audit FAIL còn tồn tại. [Bằng chứng regression](../evidence/TV3_week2/04_model_regression.txt) phân biệt các fixture với lượt chạy dữ liệu thật.

[Đối soát trực tiếp Parquet–ODS](../evidence/TV3_week2/07_source_direct_crosscheck.txt) khớp trên cả ba file về tổng dòng, `count`, NULL/rỗng/REDACTED ở pay, mã nghề có số 0 đầu và số dòng khác kỳ. Script tái hiện nằm trong [gói bằng chứng](../evidence/TV3_week2/reconcile_sources.py). Đây là phép kiểm TV3 thực hiện để TV5 tiếp tục replay độc lập.

Separations đã được bổ sung vào prototype tuần 1 với 24.088 dòng, có [log mới riêng](TV3_week2_prototype_log.csv) và [đầu ra chạy](../evidence/TV3_week2/03_separations_prototype.txt). Hồ sơ tuần 1 được giữ theo lượt chạy cũ.

Đã tạo `workforce_g2_transfer`, dump chuyển riêng tại `db_dumps/workforce_g2.dump` và kiểm restore trên Mac vào `workforce_g2_restore_check`. Bản chuyển có 3 dòng month, 123 dòng agency, 14 dòng category, 114 dòng workforce Mart và 88 dòng flows Mart. K01/K06/K07 sau restore lần lượt là 2.271.969, 7.153 và 24.088. [Bằng chứng copy/restore và SHA-256 dump](../evidence/TV3_week2/06_transfer_restore.txt) cùng [SQL KPI](../evidence/TV3_week2/02_sql_kpi.txt) phục vụ TV4/TV5 kiểm lại. TV4 vẫn cần tự restore trên Windows và chạy Power BI.

Phần agency/category trong DW dùng lookup dẫn xuất TV2 đã gate READY, kèm Unknown và mã gốc. Trạng thái xác minh miền mã vẫn PARTIAL. Mô hình thực thi hiện tại giữ grain một dòng nguồn cho từng Fact và phạm vi Dimension theo tháng. TV4 cần duyệt các quyết định này khi giao bus matrix/catalog.

**Giới hạn agency cần TV2/TV4 review.** Có 206.687 dòng Employment, 1.591 dòng Accessions và 1.936 dòng Separations vào nhóm agency Unknown vì khóa chưa có một nhãn READY trong lookup TV2 theo kỳ. Tổng toàn kỳ vẫn được giữ. Bộ lọc agency dùng nhãn Dimension chỉ tách được các nhóm đã qua gate; phần Unknown cần đối chiếu mã gốc ở ODS/Fact và xử lý trước khi kết luận theo từng agency.

## Đầu vào và người nhận tiếp theo

- **TV4** cung cấp `docs/09_bus_matrix.md`, `docs/08_dimension_catalog.csv` hoặc bản bàn giao theo commit. Review thiết kế SQL, tự SELECT Mart và tạo PBIX trên Windows. Cần ghi SQL và DAX cùng bộ lọc tháng/agency.
- **TV5** replay nguồn, DDL và ETL trên môi trường riêng. Review checksum, row reconciliation, lineage, lookup không nhân dòng, chạy lại và rollback. Sau đó kiểm KPI SQL–DAX và ghi kết luận G2 độc lập.
- **TV2** đối chiếu các trường mapping với DDL và review các nhãn PARTIAL/REVIEW, gồm Unknown của agency/subelement theo kỳ.
- **TV1** điều phối reviewer và kết luận cổng G2 theo bằng chứng của TV4/TV5.

Trạng thái này ghi sản phẩm và phần phụ thuộc của TV3. Mục DONE cần có reviewer cùng kết luận PASS thực tế của nhóm.
