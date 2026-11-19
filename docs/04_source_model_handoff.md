# Bàn giao mô hình nguồn TV2 · G2

Trạng thái đề xuất là REVIEW. [ERD](../diagrams/04_relational_source_erd.drawio) có trang v1 bàn giao và v0 phác thảo. Mô hình nguồn quan hệ tái cấu trúc theo R01. Mỗi dòng giữ grain của file công bố. Vị trí dòng ODS bắt đầu từ 1 theo loader prototype. Khi kiểm nguồn, dùng vị trí DuckDB cộng 1.

| Quan hệ | Bằng chứng | Trạng thái TV2 |
|---|---|---|
| Source file → ba bảng ODS | 12 checksum khớp manifest, ordinal trong mỗi file duy nhất từ 1 đến n | VERIFIED trên Parquet; chờ áp vào DDL và review |
| Department, Agency, Subelement, Occupation, Duty Station, Pay Plan và Action Category | Audit đủ bốn kỳ. Đã đối chiếu mẫu mã Agency/Subelement và hai nhóm action với OPM. Cần danh mục đầy đủ để xác minh FK | PARTIAL |
| FK riêng cho Grade hoặc khóa nhân viên xuyên họ | Grade phụ thuộc pay plan; ba họ giữ grain riêng | UNSUPPORTED |

[Audit](04_relationship_audit.csv) · [Nguồn tham chiếu](../data/reference/verified_codebook_manifest.csv) · [Mapping](04_source_to_target_mapping.csv)

**TV3** đối chiếu các bảng/cột ứng viên với DDL. Kiểm tra lineage ODS → Fact phải trả về 0 lỗi cho từng cặp bảng. Báo cáo phân biệt khóa thiếu, thừa, trùng và NULL theo file và ordinal.

**TV4** đối chiếu vai trò tháng và bus matrix. K01–K05/K09 dùng snapshot. K06–K08 mặc định theo tháng báo cáo. K10 đo theo từng file và trường kiểm. Mẫu số là số dòng có mã đủ điều kiện, tử số là số dòng khớp đúng một khóa tham chiếu chính thức. Tỷ lệ để trống cho phạm vi chưa xác minh hoặc mẫu số bằng 0.

**TV5** chạy lại bộ kiểm và đối soát số dòng trước/sau lookup. Gắn DDL G2, bus matrix và biên bản review khi có trên GitHub.
