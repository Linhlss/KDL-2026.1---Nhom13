# Bảng công việc tuần 1 và bàn giao TV1 → TV2

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
| L2-01 | TV2 | 19/11 | DOING | TV5 | Bản đầu: [TV2_Source_Inventory.xlsx](../evidence/TV2_week1/TV2_Source_Inventory.xlsx) (số dòng/byte khớp [đối chiếu TV1](../evidence/TV1_week2/README.md)); còn thiếu `docs/03_source_inventory.csv` có SHA-256/schema_hash/source_url và `data/manifest/sha256.txt` | [#7](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/7) |
| L2-02 | TV2 | 20/11 | TODO | TV5 | `data/reference/README.md` (sẽ tạo)<br>`data/reference/reference_manifest.csv` (sẽ tạo) | [#8](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/8) |
| L2-03 | TV2 | 20/11 | DOING | TV5 | Bản nháp: sheet *Data Dictionary* trong TV2_Source_Inventory.xlsx (chưa xác minh codebook); cần `docs/03_data_dictionary.csv` đủ cột theo kế hoạch | [#9](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/9) |
| L2-04 | TV2 | 21/11 | TODO | TV3 / TV5 | `diagrams/04_relational_source_erd.drawio` (sẽ tạo) | [#10](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/10) |
| L2-05 | TV2 | 25/11 | TODO | TV5 | `docs/03_taxonomy.md` (sẽ tạo)<br>`diagrams/03_opm_source_flow.drawio` (sẽ tạo) | [#11](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/11) |
| L2-profiling | TV2 | — | REVIEW | TV5 (L5-02) | [data_quality.md](../evidence/TV2_week1/TV2_Data_Quality_Phan_Tich_V1/data_quality.md) — PR #13; TV1 đo lại khớp 12 file, 9.181.290 dòng, `count`=1, 593 event lệch tháng | [#13](https://github.com/Linhlss/KDL-2026.1---Nhom13/pull/13) |
| L3-01 | TV3 | 19/11 | REVIEW | TV5 | [06_environment_setup.md](06_environment_setup.md), [01_create_schemas.sql](../sql/01_create_schemas.sql) | [#14](https://github.com/Linhlss/KDL-2026.1---Nhom13/pull/14) |
| L3-02 | TV3 | 20/11 | REVIEW (thiếu Separations) | TV5 | [Kết quả prototype](../reports/TV3_week1_prototype_results.md): Accessions 7.153 đủ, Employment mẫu 50.000; checksum thuộc baseline (TV1 kiểm). Còn nạp Separations 202504 = 24.088 | [#14](https://github.com/Linhlss/KDL-2026.1---Nhom13/pull/14) |
| L3-03 | TV3 | 20/11 | REVIEW | TV4 / TV5 | [06_architecture_components.drawio](../diagrams/06_architecture_components.drawio); chờ TV4 tự kết nối | [#14](https://github.com/Linhlss/KDL-2026.1---Nhom13/pull/14) |
| L3-04 | TV3 | khi có ERD v0 | BLOCKED (chờ L2-04/L2-06) | TV5 | [TV3_week1_erd_review.md](TV3_week1_erd_review.md) | [#14](https://github.com/Linhlss/KDL-2026.1---Nhom13/pull/14) |
| L4-01 | TV4 | 19/11 | TODO | TV5 | `docs/10_publish_feasibility.md`, `evidence/TV4_week1/` (sẽ tạo) | [#12](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/12) |
| L5-01 | TV5 | 19/11 | TODO | TV1 | `tests/test_plan.md`, `reports/qa_issue_log.csv` (sẽ tạo) | — |

## Sẵn sàng bàn giao nghĩa là gì?

Tiến độ L3-01 đến L3-04, sản phẩm và bằng chứng nằm trong [bảng bàn giao tuần 1 của TV3](../reports/TV3_week1_summary.md).

TV2 đọc được phạm vi và biết phải trả inventory, dictionary, ERD v0, taxonomy/flow cho ai. TV2 không đợi cả chuỗi TV1 → TV2 → TV3 tuần tự kết thúc: có thể khảo sát dữ liệu ngay, TV3 thử môi trường, TV4 thử công bố và TV5 kiểm đếm song song.

Chưa có người review thực tế; ngày khởi động, tên thật và lịch họp chưa điền. Các issue để mở. Bản tracker trong repo có link sản phẩm, nhưng cột nghiệm thu vẫn bằng 0 cho đến khi có DONE, PASS, reviewer và bằng chứng đúng quy ước. Mức tự báo 100% ở sáu task TV1 chỉ ghi đã nộp bản soạn; không có nghĩa đã review hoặc đã xác nhận xong các quy định học kỳ còn mở.

Xem [phiếu bắt đầu của TV2](00_handoff_tv1_tv2.md) và [ghi nhận bàn giao](../evidence/TV1_week1/handoff_record.md). Gói này chưa có ETL, database, EDA hoặc PBIX hoàn thành.
