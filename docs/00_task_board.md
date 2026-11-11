# Bảng công việc tuần 1 và bàn giao TV1 → TV2

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
| L2-01 | TV2 | Ngày 3 | TODO | TV5 | `docs/03_source_inventory.csv` (sẽ tạo)<br>`data/manifest/sha256.txt` (sẽ tạo) | [#7](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/7) |
| L2-02 | TV2 | Ngày 5 | TODO | TV5 | `data/reference/README.md` (sẽ tạo)<br>`data/reference/reference_manifest.csv` (sẽ tạo) | [#8](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/8) |
| L2-03 | TV2 | Ngày 6 | TODO | TV5 | `docs/03_data_dictionary.csv` (sẽ tạo) | [#9](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/9) |
| L2-04 | TV2 | Ngày 7 | TODO | TV1 | `diagrams/04_relational_source_erd.drawio` (sẽ tạo) | [#10](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/10) |
| L2-05 | TV2 | Ngày 7 | TODO | TV5 | `docs/03_taxonomy.md` (sẽ tạo)<br>`diagrams/03_opm_source_flow.drawio` (sẽ tạo) | [#11](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/11) |

## Sẵn sàng bàn giao nghĩa là gì?

TV2 đọc được phạm vi và biết phải trả inventory, dictionary, ERD v0, taxonomy/flow cho ai. TV2 không đợi cả chuỗi TV1 → TV2 → TV3 tuần tự kết thúc: có thể khảo sát dữ liệu ngay, TV3 thử môi trường, TV4 thử công bố và TV5 kiểm đếm song song.

Chưa có người review thực tế; ngày khởi động, tên thật và lịch họp chưa điền. Các issue để mở. Bản tracker trong repo có link sản phẩm, nhưng cột nghiệm thu vẫn bằng 0 cho đến khi có DONE, PASS, reviewer và bằng chứng đúng quy ước. Mức tự báo 100% ở sáu task TV1 chỉ ghi đã nộp bản soạn; không có nghĩa đã review hoặc đã xác nhận xong các quy định học kỳ còn mở.

Xem [phiếu bắt đầu của TV2](00_handoff_tv1_tv2.md) và [ghi nhận bàn giao](../evidence/TV1_week1/handoff_record.md). Gói này chưa có ETL, database, EDA hoặc PBIX hoàn thành.
