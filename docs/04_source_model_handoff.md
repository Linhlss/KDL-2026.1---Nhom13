# Bàn giao mô hình nguồn TV2 · G2

Trạng thái đề xuất là REVIEW. [ERD](../diagrams/04_relational_source_erd.drawio) có trang v1 bàn giao và v0 phác thảo. Mô hình nguồn quan hệ tái cấu trúc theo R01. Mỗi dòng giữ grain của file công bố. Vị trí dòng ODS bắt đầu từ 1 theo loader prototype. Khi kiểm nguồn, dùng vị trí DuckDB cộng 1.

| Quan hệ | Bằng chứng | Trạng thái TV2 |
|---|---|---|
| Source file → ba bảng ODS | 12 checksum khớp manifest, ordinal trong mỗi file duy nhất từ 1 đến n | VERIFIED trên Parquet; chờ áp vào DDL và review |
| Department, Agency, Subelement, Occupation, Duty Station, Pay Plan và Action Category | Audit đủ bốn kỳ; định nghĩa OPM đã tra; phạm vi danh mục mã lịch sử cần đối chiếu | PARTIAL |
| FK riêng cho Grade hoặc khóa nhân viên xuyên họ | Grade phụ thuộc pay plan; ba họ giữ grain riêng | UNSUPPORTED |

[Audit](04_relationship_audit.csv) · [Nguồn tham chiếu](../data/reference/verified_codebook_manifest.csv) · [Mapping](04_source_to_target_mapping.csv)

**TV3** đối chiếu các bảng/cột ứng viên với DDL. **TV4** đối chiếu role tháng và bus matrix. K01–K05/K09 dùng snapshot, K06–K08 mặc định theo tháng báo cáo và K10 dùng mẫu số eligible theo phép kiểm. **TV5** chạy lại bằng chứng và kiểm tổng dòng trước/sau lookup. DDL G2, bus matrix và biên bản review cần được gắn khi có trên GitHub.
