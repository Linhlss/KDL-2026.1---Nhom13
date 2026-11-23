# Bàn giao mô hình nguồn TV2 · G2

Trạng thái đề xuất là REVIEW. [ERD](../diagrams/04_relational_source_erd.drawio) có trang v1 bàn giao và v0 phác thảo. Mô hình nguồn quan hệ tái cấu trúc theo R01. Mỗi dòng giữ grain của file công bố. Vị trí dòng ODS bắt đầu từ 1 theo loader prototype. Khi kiểm nguồn, dùng vị trí DuckDB cộng 1.

| Quan hệ | Bằng chứng | Trạng thái TV2 |
|---|---|---|
| Source file → ba bảng ODS | 12 checksum khớp manifest, ordinal trong mỗi file duy nhất từ 1 đến n | VERIFIED trên Parquet; chờ áp vào DDL và review |
| Subelement | Danh mục EHRI đúng kỳ đã đối chiếu trên 12 file. Không trùng khóa hoạt động. Có 1.339 dòng `HU**` cần giữ riêng trong Unknown/DQ | PARTIAL ở cấp quan hệ |
| Agency và Action Category | Đã đối chiếu mẫu Agency hai ký tự và nhãn action từ bản công bố FedScope đến 03/2025. Các mã và nhãn tra được theo tháng nằm trong bảng lookup dẫn xuất | PARTIAL |
| Department, Occupation, Duty Station và Pay Plan | Có số liệu audit bốn kỳ. Cần danh mục đầy đủ để xác minh FK | PARTIAL |
| FK riêng cho Grade hoặc khóa nhân viên xuyên họ | Grade phụ thuộc pay plan; ba họ giữ grain riêng | UNSUPPORTED |

[Audit](04_relationship_audit.csv) · [Nguồn tham chiếu](../data/reference/README.md) · [Lookup theo kỳ](../data/reference/derived_lookup_g2.csv) · [Mapping](04_source_to_target_mapping.csv)

L2-08 đã đối chiếu từng đích của mapping dự kiến với DDL G2 của TV3. [Bảng tên và cột vật lý](04_g2_ddl_comparison.csv) ghi các đích thực thi kèm SQL kiểm. [Biên bản review](04_g2_ddl_review.md) ghi kết quả đối chiếu ERD và các mục cần TV3, TV4, TV5 xác nhận.

**TV3** đối chiếu các bảng/cột ứng viên với DDL. Kiểm tra lineage ODS → Fact phải trả về 0 lỗi cho từng cặp bảng. Báo cáo phân biệt khóa thiếu, thừa, trùng và NULL theo file và ordinal.

**TV4** đối chiếu vai trò tháng và bus matrix. K01–K05/K09 dùng snapshot. K06–K08 mặc định theo tháng báo cáo. K10 đo theo từng file và trường kiểm. Mẫu số là số dòng có mã đủ điều kiện, tử số là số dòng khớp đúng một khóa tham chiếu chính thức. Tỷ lệ để trống cho phạm vi chưa xác minh hoặc mẫu số bằng 0.

**TV5** chạy lại bộ kiểm và đối soát số dòng trước/sau lookup. Gắn DDL G2, bus matrix và biên bản review khi có trên GitHub.
