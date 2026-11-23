# Bảng công việc và bàn giao G2 G3

## Tuần 3 của TV3

Nhánh `tv3/g3-full-pipeline` kế thừa PR G2 #43 chưa merge. [Báo cáo G3](../reports/TV3_week3_summary.md) và [runbook](TV3_week3_runbook.md) ghi actual và dependency, không tự chốt G3/DONE thay reviewer. ID dưới đây theo phân công V3; chưa gán số issue GitHub tuần 3 khi chưa có.

| Task | Owner | Trạng thái gửi review | Sản phẩm và phần chờ |
| --- | --- | --- | --- |
| L3-10 | TV3 | REVIEW | [12-file counts](../reports/week3/07_file_counts.csv), [load log](../reports/week3/07_load_log.csv), [before–after](../reports/week3/07_before_after.csv); TV2/TV5 xác nhận |
| L3-11 | TV3 | REVIEW phần thực thi; model PROPOSED | 3 Fact, PK/FK/Unknown, [catalog quan sát](../reports/week3/08_dimension_observed.csv); chờ bus matrix/catalog và grain chính thức TV4 |
| L3-12 | TV3 | REVIEW phần tháng/cơ quan | 2 Mart đủ bốn kỳ, [SQL KPI](../sql/07_g3_kpi.sql); chiều/category bổ sung chờ TV4 thống nhất |
| L3-13 | TV3 | REVIEW tự kiểm | [J06](../reports/week3/07_reconciliation.csv), [May rerun](../reports/week3/TV3_week3_rerun_results.csv), [hướng dẫn lỗi/version](TV3_week3_runbook.md); TV5 QA độc lập còn chờ, replacement thật NOT_TESTED |

H07 gửi review; TV4 còn cần nhận Mart/Windows/PBIX và TV5 ký kết quả độc lập. TV1 điền lịch thực tế và chốt G3. Chi tiết phần còn mở nằm trong báo cáo tuần 3.

> **Cập nhật nhánh TV3 ngày 23/11/2026:** gói tuần 2 **REVIEW** tại [PR nháp #43](https://github.com/Linhlss/KDL-2026.1---Nhom13/pull/43). Đã có đầu vào TV2, pipeline ba nguồn tháng 04 và gói [TV4 restore/Power BI](../handoff/TV3_G2/README.md), [TV5 replay Windows](../handoff/TV3_G2/TV5_REPLAY.md). Mô hình **PROPOSED, chờ TV4**; tích hợp và nghiệm thu **chờ TV4/TV5**. Kết quả tự kiểm của TV3 chưa thay cho nghiệm thu độc lập. Các mốc 18/11 bên dưới giữ để truy vết lịch sử.

> **Cập nhật 18/11/2026:** PR [#13](https://github.com/Linhlss/KDL-2026.1---Nhom13/pull/13) (TV2 profiling v1) và [#14](https://github.com/Linhlss/KDL-2026.1---Nhom13/pull/14) (TV3 prototype) đã merge vào `main` ở trạng thái REVIEW. Thứ tự việc tiếp theo và hạn theo T0 = 18/11: [**Việc tiếp theo của từng thành viên**](00_next_steps_by_member.md). Tiêu chuẩn PASS: [Kế hoạch thực thi](../Ke_hoach_thuc_thi_TV2_TV3_phoi_hop_TV4_TV5_Nhom13.md).

ID tracker là chuẩn. [Bảng đối chiếu ID](00_task_id_crosswalk.csv) giải thích 23 task tracker TV1 và 21 mục gộp trong phân công Markdown.

**REVIEW** nghĩa là đã có bản soạn để nhận góp ý, chưa nghiệm thu. **TODO** nghĩa là chưa có sản phẩm được xác nhận. Không đánh dấu checkbox hoàn thành thay người review.

| Task | Owner | Hạn | Trạng thái | Reviewer | Sản phẩm / việc tiếp theo | Issue |
|---|---|---|---|---|---|---|
| L1-01 | TV1 | Ngày 1 | REVIEW | TV4 | [00_scope_decisions.md](../docs/00_scope_decisions.md)<br>[00_task_board.md](../docs/00_task_board.md) | [#1](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/1) |
| L1-02 | TV1 | Ngày 3 | REVIEW | TV2 / TV3 | [R01_confirmation.md](../evidence/TV1_week1/R01_confirmation.md) | [#2](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/2) |
| L1-03 | TV1 | Ngày 3 | REVIEW | TV5 | [00_course_requirements.md](../docs/00_course_requirements.md) | [#3](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/3) |
| L1-04 | TV1 | Ngày 6 | REVIEW | TV2 | [01_business_scope.md](../docs/01_business_scope.md) | [#4](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/4) |
| L1-05 | TV1 | Ngày 7 | REVIEW | TV2 | [01_business_process.drawio](../diagrams/01_business_process.drawio)<br>[01_business_tree.drawio](../diagrams/01_business_tree.drawio) | [#5](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/5) |
| L1-06 | TV1 | Ngày 7 | REVIEW | TV2 | [01_touchpoint_mapping.csv](../docs/01_touchpoint_mapping.csv)<br>[02_kpi_dictionary.csv](../docs/02_kpi_dictionary.csv) | [#6](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/6) |
| L2-01 | TV2 | 19/11 | REVIEW | TV5 | [Inventory CSV](03_source_inventory.csv) có SHA-256/schema_hash/source_url và [manifest](../data/manifest/sha256.txt); TV3 kiểm lại ba file MVP, chín file còn lại theo bằng chứng TV2 | [#7](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/7) |
| L2-02 | TV2 | 20/11 | REVIEW · miền mã PARTIAL | TV5 | [Nguồn reference và phạm vi](../data/reference/README.md)<br>[Reference manifest](../data/reference/reference_manifest.csv) | [#8](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/8) |
| L2-03 | TV2 | 20/11 | REVIEW | TV5 | [Dictionary CSV](03_data_dictionary.csv); giới hạn codebook theo gói reference | [#9](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/9) |
| L2-04 | TV2 | 21/11 | REVIEW | TV3 / TV5 | [ERD nguồn](../diagrams/04_relational_source_erd.drawio), [audit và mapping](04_source_model_handoff.md) | [#10](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/10) |
| L2-05 | TV2 | 25/11 | REVIEW | TV5 | [Taxonomy](03_taxonomy.md)<br>[Source flow](../diagrams/03_opm_source_flow.drawio) | [#11](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/11) |
| L2-profiling | TV2 | — | REVIEW | TV5 (L5-02) | [data_quality.md](../evidence/TV2_week1/TV2_Data_Quality_Phan_Tich_V1/data_quality.md) — PR #13; TV1 đo lại khớp 12 file, 9.181.290 dòng, `count`=1, 593 event lệch tháng | [#13](https://github.com/Linhlss/KDL-2026.1---Nhom13/pull/13) |
| L3-01 | TV3 | 19/11 | REVIEW | TV5 | [06_environment_setup.md](06_environment_setup.md), [01_create_schemas.sql](../sql/01_create_schemas.sql) | [#21](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/21) |
| L3-02 | TV3 | 20/11 | REVIEW | TV5 | [Prototype tuần 1](../reports/TV3_week1_prototype_results.md); đã bổ sung Separations 24.088, [bằng chứng tuần 2](../evidence/TV3_week2/03_separations_prototype.txt). Pipeline G2 nạp đủ ba file tháng 04 | [#22](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/22) |
| L3-03 | TV3 | 20/11 | REVIEW | TV4 / TV5 | [06_architecture_components.drawio](../diagrams/06_architecture_components.drawio); chờ TV4 tự kết nối | [#23](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/23) |
| L3-04 | TV3 | khi có ERD v0 | REVIEW | TV5 | [Biên bản ERD đã cập nhật G2](TV3_week1_erd_review.md); TV5 kiểm lineage và ngoại lệ miền mã độc lập | [#24](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/24) |
| L4-01 | TV4 | 19/11 | TODO | TV5 | `docs/10_publish_feasibility.md`, `evidence/TV4_week1/` (sẽ tạo) | [#12](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/12) |
| L5-01 | TV5 | 19/11 | TODO | TV1 | `tests/test_plan.md`, `reports/qa_issue_log.csv` (sẽ tạo) | [#34](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/34) |

## Issue tuần 2 — đường tới G2 (tạo 18/11/2026)

Hạn theo T0 = 18/11/2026. Thứ tự và phụ thuộc: [Việc tiếp theo của từng thành viên](00_next_steps_by_member.md). Hạn mới của #7–#12 được ghi trong comment của từng issue.

| Task | Owner | Hạn | Trạng thái | Issue |
|---|---|---|---|---|
| L2-06 | TV2 | 21/11 | REVIEW · [gói audit/mapping](04_source_model_handoff.md) | [#16](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/16) |
| L2-07 | TV2 | 22/11 | REVIEW · [lookup và ngoại lệ](../data/reference/README.md), miền mã PARTIAL | [#17](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/17) |
| L2-08 | TV2 | 23/11 | REVIEW · [source-to-target](04_source_to_target_mapping.csv) | [#18](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/18) |
| L2-11/12/13 | TV2 | 25/11 | REVIEW · [bằng chứng quy tắc nguồn](../evidence/TV2_week2/README.md), J02 PostgreSQL theo bằng chứng TV3 | [#19](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/19) |
| L2-09/L2-10 | TV2 | sau ERD v0 | REVIEW · [EDA](../reports/05_eda_findings.md) | [#20](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/20) |
| L3-05 | TV3 | 20/11 | REVIEW · DDL nguồn/ODS/audit có bằng chứng; chờ TV5 | [#25](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/25) |
| L3-06 | TV3 | 21/11 | REVIEW · J00/J01 đủ ba nguồn; chờ TV5 replay | [#26](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/26) |
| J02 | TV3 | 22/11 | REVIEW · typed/raw và before–after; chờ TV2/TV5 | [#27](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/27) |
| L3-07 | TV3 | 23/11 | PROPOSED · mô hình chạy được; chờ TV4 duyệt bus matrix/catalog/grain | [#28](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/28) |
| L3-08 | TV3 | 24/11 | REVIEW · phần TV3; tích hợp Windows/PBIX/SQL–DAX và QA chờ TV4/TV5 | [#29](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/29) |
| L3-09 | TV3 | 25/11 | REVIEW · đủ sơ đồ và bản xem; chờ TV4/TV5 | [#30](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/30) |
| L4-02 | TV4 | 20/11 | TODO | [#31](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/31) |
| L4-03/L4-04 | TV4 | 21/11 | TODO | [#32](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/32) |
| L4-05/L4-06 | TV4 | 25/11 | TODO | [#33](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/33) |
| L5-02 | TV5 | 20/11 | TODO | [#35](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/35) |
| L5-03 | TV5 | 21/11 | TODO | [#36](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/36) |
| L5-04 | TV5 | 21/11 | TODO | [#37](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/37) |
| L5-05 | TV5 | 21–23/11 | TODO | [#38](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/38) |
| L5-06 | TV5 | 25/11 | TODO | [#39](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/39) |

## Sẵn sàng bàn giao nghĩa là gì?

Tiến độ L3-01 đến L3-04, sản phẩm và bằng chứng nằm trong [bảng bàn giao tuần 1 của TV3](../reports/TV3_week1_summary.md).

Tiến độ triển khai G2 của TV3, đầu vào TV2 đã tích hợp và phần còn chờ TV4/TV5 nằm trong [bảng bàn giao tuần 2](../reports/TV3_week2_summary.md).

TV2 đọc được phạm vi và biết phải trả inventory, dictionary, ERD v0, taxonomy/flow cho ai. TV2 không đợi cả chuỗi TV1 → TV2 → TV3 tuần tự kết thúc: có thể khảo sát dữ liệu ngay, TV3 thử môi trường, TV4 thử công bố và TV5 kiểm đếm song song.

Chưa có người review thực tế; ngày khởi động, tên thật và lịch họp chưa điền. Các issue để mở. Bản tracker trong repo có link sản phẩm, nhưng cột nghiệm thu vẫn bằng 0 cho đến khi có DONE, PASS, reviewer và bằng chứng đúng quy ước. Mức tự báo 100% ở sáu task TV1 chỉ ghi đã nộp bản soạn; không có nghĩa đã review hoặc đã xác nhận xong các quy định học kỳ còn mở.

Xem [phiếu bắt đầu của TV2](00_handoff_tv1_tv2.md) và [ghi nhận bàn giao tuần 1](../evidence/TV1_week1/handoff_record.md) để truy vết lịch sử. Nhánh này đã có ETL/database/EDA và bằng chứng kỹ thuật; PBIX, bằng chứng Windows và kết luận QA độc lập vẫn do TV4/TV5 bổ sung.
