# Nhận xét sau triển khai tuần 3 TV3

> **Ghi chú TV1, 27/11/2026:** biên bản này là bản tự rà ngày 23/11 của TV3, được giữ nguyên làm lịch sử.
> - **Đã thay đổi:** sau khi TV1 sửa lỗi Unknown, các file trong `reports/week3/`, các file log `00`–`08`, `06_transfer_restore.txt`, `12_dump_handoff_check.txt` và dump bàn giao đã được tạo lại. Lượt chạy mới thực hiện trên PostgreSQL 17.12 macOS, code `51ab0d9`.
> - **Số liệu cũ, không dùng nữa:** `dim_agency` 493, Mart 486/340 nhóm, dump `6d85ea29…`. Số liệu mới: 521, 510/361, cùng Mart category 1.697 nhóm và Mart K10 104 dòng. Dump mới nhất là `3b467c00…`; bản `ec3ddf32…` cũng đã được thay.
> - **Không đổi:** tổng K01/K06/K07 của từng tháng.
>
> Xem [giải trình TV1](../../docs/TV1_giai_trinh_tich_hop_G3.md).

**Bổ sung bàn giao theo yêu cầu TV3:** bản aggregate G3 đã kiểm nay có trong [handoff/TV3_G3](../../handoff/TV3_G3/README.md), kèm dump, SHA-256 và lệnh restore. Các ghi nhận “dump cục bộ/không commit” bên dưới và trong log cũ mô tả lượt kiểm ban đầu; ngoại lệ bàn giao mới chỉ áp dụng đúng file này. [Bằng chứng kiểm lại bản bổ sung](12_dump_handoff_check.txt) xác nhận năm bảng và KPI bốn kỳ.

Ngày 23/11/2026, tự rà soát lại theo kế hoạch tuần 3 phiên bản 1.0 sau khi lượt nạp thật và rerun May kết thúc SUCCESS. Phạm vi kỹ thuật là 12 Parquet, 3 Fact và 2 Mart đủ tháng 03–06. [Run manifest](../../reports/week3/run_manifest.json) ghi SHA-256 mã/inventory; [lệnh và môi trường](00_environment_and_commands.txt) ghi Python 3.12.14, PostgreSQL 18.7 và database riêng. Các file ETL hiện tại khớp hash đã chạy; DDL Fact/Mart kế thừa G2, không đổi grain hoặc tự thêm FK/hierarchy khi chưa có thiết kế TV4.

**Nhận xét:** chưa phát hiện lỗi chặn phần dữ liệu/ETL trong phạm vi mô hình tháng/cơ quan hiện tại. Có đủ bằng chứng để TV4/TV5 nhận review. G3 chưa được nghiệm thu: bus matrix/catalog/grain chính thức, Windows/PBIX/SQL–DAX và QA độc lập vẫn chờ đúng người phụ trách; phần mở rộng chiều/category không được ghi là đã có.

| Mục kế hoạch | Kiểm chứng thực tế | Kết luận tự kiểm |
| --- | --- | --- |
| T01 / L3-10, đủ 12 nguồn | [Source receipt](00_receive_sources.txt) kiểm SHA/metadata; [12-file counts](../../reports/week3/07_file_counts.csv) có Source=Staging=ODS=Fact từng file. Tổng Employment 9.057.997, Accessions 30.782, Separations 92.511. | PASS kỹ thuật |
| T02, grain/identity/Fact | [J06](../../reports/week3/07_reconciliation.csv) đối soát lineage hai chiều, count và measure từng file; ordinal/PK được kiểm trong quality suite. Gate count_value=1 bảo vệ grain một dòng nguồn. | PASS kỹ thuật |
| T03 / L3-11, Dim/FK/Unknown | [152 quality checks](../../reports/week3/09_quality_checks.csv), [constraints](../../reports/week3/09_constraints.csv) và catalog quan sát: month 9, agency 493, category 53 dòng; key/natural key/Unknown/provenance/examples/version policy có thực đo. FK tồn tại không biến miền mã PARTIAL thành VERIFIED. | PASS kỹ thuật; thiết kế chờ TV4 |
| T04, J02 và thời gian | [Quality theo file](../../reports/week3/09_source_quality.csv) so trực tiếp Parquet với ODS về count, NULL/rỗng/REDACTED, mã nghề đầu 0, khác kỳ. Giữ 593 event lệch kỳ, May 107; report/snapshot/effective month trong Fact khớp ODS. | PASS kỹ thuật |
| T05 / L3-12, Mart thật | Workforce 486 nhóm, flows 340 nhóm, có đủ bốn kỳ; aggregate event riêng rồi UNION ALL. [SQL assertion](07_sql_assertions.txt) kiểm baseline từng file/lớp và Mart từng tháng. | PASS tháng/cơ quan |
| T06, May rerun thật | [Full run log](05_full_pipeline.txt): 3 J00 kiểm lại, 6 J01/J02 SKIPPED, rebuild May rồi J06. [15 bảng trước–sau](../../reports/week3/TV3_week3_rerun_results.csv) có count và SHA-256 COPY theo PK giống nhau. Staging/ODS so source identities; Fact/Dim/Mart so mọi cột nghiệp vụ. Registry bỏ timestamps, audit được thêm run. Các tháng 03/04/06 và MoM June giữ nguyên. | PASS phạm vi đã nêu |
| T07, lỗi/rollback | [Source regression](02_source_regression.txt) có file thiếu/hash/version sai, cùng tên/hash đổi, schema non-text và lỗi COPY giữa transaction. Audit FAIL sống qua rollback, nguồn hợp lệ không bị thay. [G3 regression](01_synthetic_g3.txt) kiểm run_manifest FAIL và CSV lỗi không báo thành công. Fixture tách biệt, không sửa raw thật. | PASS nhánh lỗi đã thử |
| T08, version | Một nguồn/version mỗi family/kỳ theo registry; cùng identity/hash skip. Đã thử nhánh từ chối mismatch, không thử activation/replacement thành công vì chưa có republish thật đã xác minh và quy trình được duyệt. | Skip/reject PASS; real replacement NOT_TESTED |
| T09, SQL/KPI và TV4 | [KPI tháng](../../reports/week3/05_kpi_monthly.csv), [agency filter](../../reports/week3/05_kpi_agency.csv). April K02 −17.223, K08 −16.935; March thiếu kỳ trước giữ NULL ở K02/K03. Có nhóm thật AA April headcount 10, accessions/separations 0 cho reviewer đối chiếu. | SQL PASS; 12 DAX PENDING |
| H07, DB chuyển cho TV4 | [Transfer/restore](06_transfer_restore.txt): dump G3 cục bộ, so toàn bộ dữ liệu 5 bảng sau restore, counts 9/493/53/486/340 và KPI 4 kỳ khớp. Source/target PostgreSQL 18.7. Dump/raw/secrets không commit. | Restore macOS PASS; Windows chờ TV4 |
| Replay, tài liệu và tracker | [Runbook](../../docs/TV3_week3_runbook.md) có macOS/PowerShell, requirements, QA/CREATEDB, scope tham số, lỗi/phục hồi/version, expected/actual và output riêng. Sơ đồ G3 có SVG/draw.io. [Tracker check](09_tracker_check.txt): chỉ 26 ô đích đổi trên 9 sheet, công thức/native feature giữ nguyên, REVIEW/CHUA_REVIEW và nghiệm thu 0. | Đủ để gửi review |

Các điểm kiểm/sửa trong quá trình thực hiện: chặn count khác 1 trước publish để không lệch grain; test thêm cùng filename/hash đổi và schema không hỗ trợ; kiểm digest có thể phát hiện thay đổi field dù tổng/count không đổi; khi kiểm hình tracker đã sửa đơn vị cột tiến độ theo thang 0–100 và rút gọn ghi chú để không bị cắt. Không sửa expected nhằm làm xanh test.

Bốn regression đều đã chạy trên database tạm và dọn sau test; đây là tự kiểm TV3, không thay kết luận TV5. 84 J06 kỹ thuật PASS, 152 quality check PASS và 15 bảng rerun PASS. Có 12 dòng DAX PENDING. Cả 20 báo cáo G2 giữ nguyên byte. [Danh sách còn mở](../../reports/TV3_week3_open_items.csv) ghi owner và trạng thái, gồm dependency PR G2 #43, thiết kế TV4, nhãn PARTIAL, Windows/PBIX, QA độc lập và replacement NOT_TESTED.

Sau tự kiểm, kiểm checkout sạch và các liên kết/artifact rồi mới đẩy nhánh G3, tạo PR nháp dựa trên nhánh G2 chưa merge. Không tự đóng G2/G3 hoặc đánh DONE/PASS thay TV1/TV4/TV5.

Đã kiểm lại checkout sạch commit `342ae0d`: cả bốn regression exit 0, các entrypoint tải được, compile thành công và checkout giữ sạch; mã ETL đã commit khớp SHA-256 lượt dữ liệu thật. [Log kiểm checkout](11_clean_checkout_review.txt) ghi lệnh/kết quả. Lượt nhận xét cũng bổ sung task và mốc cần nhận vào danh sách dependency; phần thiết kế/nghiệm thu thiếu đầu vào ghi BLOCKED, không suy ngày lịch khi chưa có T0.
