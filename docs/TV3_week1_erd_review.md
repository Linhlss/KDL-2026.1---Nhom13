# Review khóa và ERD nguồn tuần 1

Phần tuần 1 dưới đây giữ lại lịch sử review. [Cập nhật G2 ngày 21/11/2026](#cập-nhật-g2-ngày-21112026) ghi đầu vào TV2 đã nhận và trạng thái hiện tại.

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

## Cập nhật G2 ngày 21/11/2026

**L3-04 · REVIEW kỹ thuật TV3, chờ TV5 review độc lập.** Đã tích hợp gói TV2 tại commit `8f9ea8d26b529381ce4d6bf69ee2d9f7e3536448`, gồm ERD nguồn v1, inventory, dictionary, audit, mapping và lookup có provenance. Vướng mắc thiếu ERD trong ghi nhận tuần 1 đã có đầu vào để xử lý. Kết luận dưới đây dựa trên tài liệu và audit TV2; kết quả PostgreSQL của TV3 được lưu trong gói bằng chứng G2.

| Quan hệ | Đánh giá áp vào thiết kế TV3 | Phần chờ review |
| --- | --- | --- |
| `source_file` → 3 Staging/ODS | DDL giữ `file_id` FK và PK `(file_id, source_row_ordinal)` trên từng bảng. Grain mỗi dòng Parquet. | TV5 replay DDL và count/ordinal trên ba file tháng 04. |
| Ba ODS → đúng Fact | Fact giữ nguyên cặp lineage và FK đến đúng ODS. | TV5 kiểm khóa thiếu, thừa, trùng và NULL bằng truy vấn lineage. |
| Agency → Dimension | `PARTIAL` theo TV2. Dùng lookup dẫn xuất READY theo `(relation, report_month, code)`, kiểm khóa duy nhất, giữ mã gốc và trạng thái Unknown. | TV4 duyệt phạm vi theo tháng và cách hiển thị Unknown; TV2/TV5 kiểm nhãn REVIEW. |
| Action category → Dimension | `PARTIAL`. Nhãn quan sát khớp archive FedScope đến 03/2025 trong phạm vi TV2 kiểm. Dùng lookup READY theo family/tháng/mã. | TV4 duyệt Dimension chung và TV5 kiểm đầy đủ domain đúng kỳ. |
| Subelement | `PARTIAL`. Audit TV2 ghi 431 orphan Employment, 10 Accessions và 4 Separations ở 202504 khi so danh mục EHRI theo kỳ. Giữ mã gốc ở ODS. | TV2/TV5 xử lý `HU**` và khác nhãn. Chờ catalog trước khi thêm Dimension/FK nghiệp vụ. |
| Department, nghề, địa điểm, pay plan | `PARTIAL`. Audit đủ bốn kỳ đã có nhưng miền mã chính thức đầy đủ vẫn cần kiểm. Các trường gốc giữ ở ODS. | TV2/TV5 kiểm phạm vi mã và ngoại lệ, TV4 duyệt các chiều bổ sung. |
| FK riêng Grade, hoặc khóa nhân viên xuyên họ | `UNSUPPORTED` theo TV2. Thiết kế giữ từng họ Fact theo grain nguồn và chỉ tổng hợp theo chiều đã chọn. | TV4 review grain và cách sử dụng measure. |

Riêng tháng 04, lookup dẫn xuất TV2 có 122 agency READY và 7 agency REVIEW; category có 4 mã Accessions READY và 9 mã Separations READY. Hai tập trạng thái được giữ khi nạp lookup để số liệu không bị mất qua INNER JOIN hoặc nhãn chưa được xử lý. Số khóa READY dùng cho Dimension được gate trước lookup. Nguồn thống kê là [derived_lookup_g2.csv](../data/reference/derived_lookup_g2.csv), với chi tiết phương pháp trong [README tham chiếu](../data/reference/README.md).

Các điểm cần TV5 kiểm độc lập gồm số dòng trước–sau lookup, NULL/empty/REDACTED, checksum ba file, ordinal 1…N, full lineage ODS–Fact và tổng measure cùng kỳ. [Thiết kế G2](TV3_g2_model_decisions.md) ghi grain, khóa kỹ thuật, vai trò thời gian và quyết định đang chờ TV4.
