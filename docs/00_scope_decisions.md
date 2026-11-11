# Phạm vi và các quyết định của Nhóm 13

TV1 soạn ngày 11/11/2026, **REVIEW — chờ TV4 review**. Ngày này là ngày cập nhật tài liệu, không phải ngày khởi động hoặc ngày thầy trả lời.

## 1. Nhóm đang giải quyết việc gì?

Người đọc có các file nhân sự từng tháng nhưng khó nhìn ngay quy mô, cơ cấu và biến động. Nhóm tổ chức lại dữ liệu, kiểm số và tạo báo cáo để trả lời ba câu hỏi: tháng đang chọn có bao nhiêu người; có bao nhiêu lượt tiếp nhận/rời cơ quan được báo cáo; nhóm nào góp phần vào thay đổi quy mô giữa hai tháng.

Người dùng dự kiến là chuyên viên phân tích nhân lực. Đây là vai trò nhóm thiết kế để xác định câu hỏi, chưa phải khách hàng đã được phỏng vấn. Dự án phân tích dữ liệu công bố, không quản lý hồ sơ từng nhân viên.

## 2. Những quyết định đã chọn

| Quyết định | Nội dung | Căn cứ |
|---|---|---|
| Nguồn và baseline | Giữ 12 Parquet OPM/EHRI, 03–06/2025; khoảng 301,5 MB; 9.181.290 bản ghi qua các kỳ | Bộ file local và kiểm metadata; TV2 vẫn kiểm độc lập inventory/version/checksum |
| Phương án mục ERD OLTP | Dựng ERD mô hình nguồn quan hệ tái cấu trúc từ dữ liệu OPM và các mã đã kiểm chứng | Thầy đã đồng ý, theo xác nhận của trưởng nhóm trong trao đổi ngày 11/11/2026; xem [ghi nhận R01](../evidence/TV1_week1/R01_confirmation.md) |
| Ranh giới của chấp thuận | Không gọi mô hình tái cấu trúc là OLTP gốc của OPM; không coi khóa/quan hệ đã được kiểm chỉ vì thầy đồng ý | TV2 audit khóa, TV3 kiểm cấu trúc và TV5 review |
| Sản phẩm mục tiêu | Python/PostgreSQL → Staging/ODS → DW với 3 Fact → ít nhất 2 Mart → 3 dashboard Power BI | Quyết định thiết kế của nhóm, chưa triển khai |
| D1 | Quy mô và cơ cấu tại một kỳ snapshot | Employment |
| D2 | Lượt Accessions/Separations theo kỳ báo cáo và category | Hai họ sự kiện; không gọi mọi accession là tuyển mới |
| D3 | Thay đổi headcount và đóng góp theo nhóm giữa hai kỳ | Hai snapshot tương ứng; không dùng event difference thay headcount change |
| Mở rộng đã chốt | Tự phát hiện/nạp kỳ mới và kiểm chất lượng; ghi phiên bản, log và chạy lại không trùng | Trưởng nhóm chọn hướng 1; triển khai sau MVP cơ bản |
| Mở rộng dự kiến | Phân tích chênh tháng báo cáo–hiệu lực | Chưa cam kết; giữ hai loại tháng để không khóa mất khả năng này |
| Thời gian | 39 ngày từ ngày nhóm thống nhất khởi động | Chưa điền ngày bắt đầu/hạn nộp lịch thật |

## 3. Ranh giới phải giữ

Không tạo employee_id, không nối lịch sử cá nhân, không cộng bốn snapshot thành số người khác nhau. Giữ đúng REDACTED (giá trị bị che) và phân biệt với thiếu dữ liệu/0. Các tháng hiệu lực cũ trong file sự kiện không đủ để kết luận cơ quan nộp chậm. Bốn kỳ chỉ hỗ trợ phân tích ngắn hạn. Không đổi sang dataset HR giả để có ERD đẹp.

## 4. Ưu tiên và các việc còn mở

| Mức | Việc | Owner và người nhận | Điều kiện |
|---|---|---|---|
| P0 — phải có | Hiểu nguồn, ERD/mapping có căn cứ, bản chạy 3 nguồn tới một KPI; sau đó hoàn thiện 12 file/3 Fact/2 Mart/3 dashboard | TV2 → TV3 → TV4; TV5 kiểm từ đầu | Số khớp nguồn, không mất/nhân dòng, tái chạy được |
| P1 — mở rộng đã chốt | Nhận diện kỳ mới/version mới, kiểm trước khi nạp, ghi log kết quả | TV2 định nghĩa kiểm; TV3 thực hiện; TV4 thể hiện kỳ cập nhật; TV5 thử; TV1 chốt phạm vi | Có demo thêm kỳ mà không nạp trùng |
| P2 — chỉ dự kiến | Trang phân tích lệch kỳ | Cả nhóm xem xét sau MVP | Không lấn yêu cầu chính và không tự gán nguyên nhân |

R01 đã được chấp thuận theo TV1; ảnh/tin nhắn gốc chưa đính kèm. R02 (quyền công bố Power BI), R03 (audit mã/khóa), R04 (baseline/version) vẫn cần TV4/TV5, TV2/TV3 và TV2 thực hiện tương ứng. Cách hiểu “100M”, thông báo học kỳ, tên thật, ngày bắt đầu và lịch họp chưa có bằng chứng chốt; xem [đối chiếu yêu cầu](00_course_requirements.md). Không mở lại câu hỏi ERD với thầy nếu phương án không thay đổi.

## 5. Ai đóng góp và giao lại gì?

| Vai trò | Việc của mình trong dòng chảy | Giao cho ai |
|---|---|---|
| TV1 | Xác định câu hỏi, nghĩa chỉ số, phạm vi, quyết định và lịch review | TV2/TV4; nhận phát hiện nguồn để sửa yêu cầu |
| TV2 | Giải thích file, cột, mã, thời gian, lỗi và quan hệ có căn cứ | TV3 nhận quy tắc; TV4 nhận ý nghĩa cột; TV1 nhận giới hạn |
| TV3 | Xây database và đường xử lý, giữ số đúng, có log và chạy lại được | TV4 nhận bảng tổng hợp và số đối soát; TV5 nhận log |
| TV4 | Mô hình phân tích, DAX và 3 dashboard trả lời câu hỏi | TV1 review nội dung; TV5 kiểm số và thao tác |
| TV5 | Đếm độc lập, kiểm xử lý/bộ lọc, ghi lỗi và benchmark | Gửi lỗi đúng TV2/TV3/TV4; báo tình trạng cho TV1 |

Mỗi người review trong 24 giờ sau khi nhận sản phẩm. Giữ TV1–TV5 đến khi nhóm điền tên thật. Bản này đủ làm đầu vào cho TV2 khảo sát; không khóa thay các quyết định grain, mã và KPI phải review ở tuần 2.
