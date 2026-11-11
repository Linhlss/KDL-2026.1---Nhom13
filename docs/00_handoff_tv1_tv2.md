# TV2 bắt đầu từ đây

**Bạn cần biến “nhóm có 12 file” thành “nhóm biết mỗi file/cột là gì, dùng được thế nào và không được hiểu sai chỗ nào”.** Bạn chưa phải xây database hoặc dashboard. Khi thiếu đầu vào, gửi câu hỏi cụ thể; không ngồi đợi tất cả thành viên làm xong.

## 1. Đọc theo thứ tự

1. [Bài toán và dòng công việc](01_business_scope.md): hiểu ba câu hỏi và ví dụ tháng 04.
2. [Phạm vi đã chọn](00_scope_decisions.md): giữ OPM, ERD tái cấu trúc được chấp thuận theo TV1, mở rộng hướng 1.
3. [KPI v0 và lưu ý kỳ đo](02_kpi_draft_notes.md): biết cột cần tìm.
4. [Bảng giao việc tuần 1](00_task_board.md): mở issue L2-01 đến L2-05 và nhận việc theo vai trò TV2.

## 2. Trong 48 giờ đầu, làm theo thứ tự này

48 giờ tính từ khi TV2 nhận việc, không tự coi ngày cập nhật tài liệu là ngày bắt đầu dự án. Hạn toàn tuần vẫn theo Ngày 1–7 trong kế hoạch 39 ngày.

| Thứ tự | Hành động cụ thể | Sản phẩm tối thiểu gửi lại | Người nhận / điều kiện nhận |
|---|---|---|---|
| 1 | Nhận đúng 12 file; ghi một hàng cho mỗi file gồm họ, tháng, version, tên, byte, dòng, cột và SHA-256 | Inventory v0 có đủ 12 hàng; schema/checksum có thể hoàn thiện theo hạn Ngày 3 | TV3, TV5; đủ 3 họ × 4 kỳ, chỉ rõ số nào đọc từ metadata |
| 2 | Mở cấu trúc/mẫu một file của mỗi họ; tìm cột snapshot, effective month, mã cơ quan và category | Dictionary v0 cho các trường ở mục 3; ví dụ lấy từ file thật | TV1, TV3, TV4; phân biệt cột raw với metadata nhóm tạo |
| 3 | Ghi đường dẫn tài liệu định nghĩa; đọc trước các mã thật sự cần dùng | Danh sách nguồn tham chiếu kèm ngày truy cập; đánh dấu chưa/đã kiểm | TV3/TV5; không tải hàng loạt tài liệu không liên quan |
| 4 | Phác ba bảng bản ghi, bảng file và các bảng mã dự kiến; ghi loại khóa và chỗ chưa xác minh | ERD v0 và danh sách câu hỏi/kiểm còn thiếu | TV1/TV3; không có employee_id giả hoặc quan hệ nhân viên xuyên ba nguồn |
| 5 | Gửi một gói ngắn: đã hiểu gì, file sản phẩm ở đâu, số nào khớp, đang vướng gì | Cập nhật issue kèm link sản phẩm và người cần hỗ trợ | TV1, TV3, TV5 phản hồi trong 24 giờ |

## 3. Những trường cần giải thích trước

| Trường / nguồn kỳ | TV2 cần viết gì? |
|---|---|
| `snapshot_yyyymm` — Employment | Là tháng trạng thái; kiểm đúng với kỳ file; nêu ví dụ tháng 04 từ dữ liệu thật |
| Tên file và version — cả 3 họ | Tháng báo cáo của file, phiên bản, vị trí lấy; `report_month` là metadata bổ sung |
| `personnel_action_effective_date_yyyymm` — event | Tháng hiệu lực; có thể khác tháng file; không tự kết luận là “nộp chậm” |
| `count` | Kiểu raw là chuỗi; kiểm giá trị và quan hệ giữa COUNT bản ghi với tổng count sau chuyển kiểu |
| `agency_code`, `agency`, `department_code`, `agency_subelement_code` | Mã, nhãn, phạm vi; không mặc định hierarchy hoặc FK đã đúng |
| `accession_category_code`, `accession_category`; `separation_category_code`, `separation_category` | Định nghĩa hành động; dùng đúng họ dữ liệu; không biến mọi accession thành tuyển mới |
| `occupational_series_code`, `occupational_group_code`, `duty_station_code`, `pay_plan_code`, `grade` | Ý nghĩa, mã–nhãn, nguồn tham chiếu; quan hệ/khóa nào phải kiểm tiếp |
| NULL, rỗng, `REDACTED` | Phân biệt; chỉ ghi tỷ lệ sau khi đã scan và ghi rõ mẫu số |

Mỗi hàng dictionary nên có: họ dữ liệu, tên cột raw, nghĩa bằng tiếng Việt, kiểu raw/kiểu dự kiến, ví dụ thật, cách dùng/KPI, nguồn định nghĩa, quy tắc thiếu/REDACTED và điều chưa kiểm.

## 4. Ví dụ bàn giao hoàn chỉnh cho câu hỏi tháng 04

“Em dùng `employment_202503_v4.parquet` và `employment_202504_v4.parquet` để so snapshot, `accessions_202504_v5.parquet` và `separations_202504_v5.parquet` để đếm lượt theo kỳ file. Metadata của gói TV1 cho các số lần lượt 2.289.192; 2.271.969; 7.153; 24.088. Em sẽ kiểm độc lập và ghi phương pháp trong inventory. Hai hiệu cần ra −17.223 người và −16.935 lượt. Em không nối theo nhân viên và không coi hai hiệu phải bằng nhau.”

Đây là mẫu diễn đạt với tổng nguồn thật, chưa phải kết quả TV2 đã kiểm xong. TV2 thay câu “sẽ kiểm” bằng phương pháp và bằng chứng thật sau khi thực hiện.

## 5. Toàn bộ sản phẩm tuần 1 phải trả lại

| Task chuẩn tracker | Sản phẩm theo phân công V3 | Hạn | Review |
|---|---|---|---|
| L2-01 | `docs/03_source_inventory.csv`, `data/manifest/sha256.txt` | Ngày 3 | TV3, TV5 |
| L2-02 | `data/reference/README.md` và manifest nguồn tham chiếu | Ngày 5 | TV3, TV5 |
| L2-03 | `docs/03_data_dictionary.csv` v0 | Ngày 6 | TV5, TV1/TV4 dùng kết quả |
| L2-04 | `diagrams/04_relational_source_erd.drawio` v0 | Ngày 4 | TV3; TV1 nhận để đối chiếu phương án đã được đồng ý |
| L2-05 | `docs/03_taxonomy.md`, `diagrams/03_opm_source_flow.drawio` | Ngày 7 | TV1, TV5 |

Các đường dẫn trong bảng là sản phẩm **TV2 sẽ tạo**, chưa có trong repo. Audit mã/khóa hoàn chỉnh, mapping v1 và EDA thống kê chi tiết tiếp tục ở tuần 2; không gắn PASS sớm cho bản phác.

## 6. ERD cần chứng minh những gì?

Giữ một bảng `source_file` để truy vết tệp; ba loại record giữ đúng grain (một dòng đại diện cho gì). Khóa kỹ thuật dự kiến `(file_id, source_row_ordinal)` chỉ định vị bản ghi trong file, không nhận diện nhân viên. Nếu dùng file hash phải ghi quy tắc nhận diện phiên bản. Khóa của bảng mã phải kiểm tính duy nhất, phạm vi và lịch sử hiệu lực; chưa đủ chứng cứ thì vẽ nét đứt/ghi chưa xác minh, chưa đặt FK như đã đúng.

Mô hình đó phục vụ mục ERD theo [chấp thuận R01 được TV1 xác nhận](../evidence/TV1_week1/R01_confirmation.md). Thầy đồng ý phương án không có nghĩa ERD đã được làm thay bạn.

## 7. Khi vướng, báo như thế nào?

Ghi task ID, tên file/version, tên cột, bước vừa làm, kết quả thấy, điều đang cần và link minh chứng. Ví dụ: “L2-03, file Accessions 202504 v5: có tháng hiệu lực trước 202504. Em chưa rõ cách ghi kỳ dashboard; đề xuất giữ report_month từ tên file và effective month riêng, nhờ TV1/TV4 review.” Không gửi mật khẩu hoặc chụp thông tin kết nối thật.

Mẫu trưởng nhóm giao việc: “TV2 nhận gói [bắt đầu từ đây](00_handoff_tv1_tv2.md). Trong 48 giờ đầu gửi inventory v0, dictionary trường cốt lõi và ERD v0 có đánh dấu chưa kiểm; cập nhật issue tương ứng. TV3/TV5 review kỹ thuật, TV1/TV4 kiểm ý nghĩa. Có vướng ghi file, cột và bằng chứng, không cần chờ đủ toàn bộ tài liệu mới báo.”
