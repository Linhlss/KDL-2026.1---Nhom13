# Review khóa và ERD nguồn tuần 1

**L3-04 · BLOCKED cho review chính thức.** TV3 đã kiểm sơ bộ khóa ứng viên trên toàn bộ Accessions 202504 v5 và 50.000 dòng đầu của Employment 202504 v4. ERD v0, dictionary, codebook/reference và audit của TV2 chưa có trong repo để gắn kết quả với các quan hệ cụ thể. Phiên bản ERD review: chờ TV2. Mốc cần nhận: Ngày 7 của nhóm, chờ TV1/TV2 xác nhận ngày lịch. R03 cần bản đầu ở Ngày 7 và chốt theo kế hoạch vào Ngày 12.

## Kết quả sơ bộ trên dữ liệu đã nạp

| Mã ứng viên | Accessions · 7.153 dòng | Employment · 50.000 dòng | Kết luận |
| --- | --- | --- | --- |
| `agency_code` | 54 mã, 0 mã nhiều nhãn | 31 mã, 0 mã nhiều nhãn | Partial. Cần codebook và phạm vi mã qua các kỳ. |
| `occupational_series_code` | 265 mã, 0 mã nhiều nhãn | 426 mã, 0 mã nhiều nhãn | Partial. Cần xác minh mã, nhãn và phiên bản bộ mã. |
| `duty_station_code` | 2.593 dòng REDACTED; 17 mã chưa có nhãn city hợp lệ | 16.004 dòng REDACTED; 97 mã chưa có nhãn city hợp lệ | Partial. Cần trường nhãn đúng từ codebook, kiểm khóa theo phạm vi địa lý và quy tắc xử lý mã đặc biệt. |
| `pay_plan_code` | 55 mã và 20 dòng mã thiếu | 55 mã và 0 dòng mã thiếu | Partial. Cần bảng ref và quy tắc xử lý NULL trong Accessions. |

`duty_station_city` chỉ là trường nhãn dùng để khảo sát. “0 mã nhiều nhãn” chỉ phản ánh phần đã nạp và các nhãn đọc được. Các thống kê đó chưa đủ để kết luận phạm vi khóa, lịch sử mã hoặc độ phủ FK. Câu lệnh và số đo nằm trong [SQL profile](../sql/tests/TV3_week1_key_profile.sql) và [bằng chứng](../evidence/TV3_week1/07_key_profile.txt).

## Kiểm tiếp khi TV2 cung cấp ERD và bảng tham chiếu

1. Ghi version ERD và nguồn codebook. Với từng quan hệ đề xuất, ghi bảng/cột hai đầu, grain, phạm vi hiệu lực của mã, cardinality và expected/actual.
2. Kiểm phía ref bằng `GROUP BY` trên toàn bộ khóa ứng viên và `HAVING COUNT(*) > 1`. Đếm NULL và chuỗi rỗng riêng. Kỳ vọng khóa hợp lệ đủ thành phần và duy nhất trong phạm vi đã ghi.
3. Trên bản ghi nguồn, đếm mã thiếu, `REDACTED` và ngoại lệ đã có quy tắc riêng. Dùng `NOT EXISTS` với đủ thành phần khóa để đếm orphan của mã hợp lệ. So số dòng trước và sau lookup để phát hiện nhân dòng. Bàn với TV2 cách xử lý các ngoại lệ có thật trước khi thêm FK.
4. Ghi từng quan hệ `verified`, `partial` hoặc `unsupported` và người xử lý. TV3 chỉ đưa FK vào DDL sau khi đã kiểm đủ khóa, độ phủ và quy tắc ngoại lệ.

ERD mô tả **mô hình nguồn quan hệ tái cấu trúc**. Theo R01, nhóm đã ghi nhận việc chấp thuận phương án này. Khóa kỹ thuật `(file_id, source_row_ordinal)` dùng để truy vết bản ghi. Prototype tuần 1 dùng checksum thay `file_id`. Giữ ba họ dữ liệu theo grain riêng và chỉ liên hệ ở mức tổng hợp đã thống nhất. Giữ riêng kỳ báo cáo và kỳ hiệu lực. Các bản ghi có nội dung giống nhau được giữ nếu source identity khác nhau.

**Cần TV2 bàn giao:** `diagrams/04_relational_source_erd.drawio`, dictionary, inventory/checksum và codebook hoặc audit hiện có. **TV3** cập nhật biên bản khi nhận đầu vào. **TV5** kiểm lại các truy vấn và số liệu.
