# Đối chiếu yêu cầu môn học

**L1-03: TV5 (Minh Châu) xác nhận PASS để TV2 dùng làm đầu vào.** Nguồn đối chiếu là `Hướng dẫn môn học - DW & BI 20252.xlsx`, đã đọc ngày 11/11/2026. [Biên bản ghi nhận review](../evidence/TV5_week1/L1-03_review.md) nêu phạm vi xác nhận. Chưa có thông báo học kỳ hiện hành để xác nhận mọi quy định hành chính vẫn giữ nguyên.

Đọc bảng này như một danh sách việc phải chứng minh. Các mã C01–C11 là cách nhóm tổ chức minh chứng; không phải điểm số đã được giảng viên chấm.

## 1. Yêu cầu và sản phẩm đối chiếu

| Nội dung trong tài liệu giảng viên | Vị trí nguồn | Sản phẩm nhóm phải làm | Chủ trì | Cách kiểm tra |
|---|---|---|---|---|
| Dữ liệu phù hợp chủ đề; dung lượng **lớn hơn 100 MB** | Hướng dẫn bài tập nhóm, B2:C5 ghi “Lớn hơn 100M”; xem [ghi nhận xác nhận đơn vị](../evidence/TV1_week1/100MB_confirmation.md) | Phạm vi dữ liệu và inventory; ghi rõ byte, dòng, bảng, cột | TV1/TV2 | Bộ 12 Parquet có tổng 301.504.795 byte (khoảng 301,5 MB), vượt ngưỡng dung lượng; TV5 đối chiếu inventory |
| Các lớp data sources → DW → Mart → BI; Power BI và hệ quản trị CSDL | Hướng dẫn bài tập nhóm, C17:C19, C26:C27 | Kiến trúc, database, luồng xử lý và báo cáo chạy thực tế | TV3/TV4 | Có sản phẩm xuyên suốt, đối soát được ít nhất một KPI |
| Quy trình nghiệp vụ, điểm phân tích, cây nghiệp vụ, mô hình kinh doanh | Hướng dẫn bài tập nhóm, D35/I35 | Hai quy trình, cây nghiệp vụ, bảng A01–A10; mô tả giá trị, người dùng và nguồn lực phù hợp đề tài | TV1 | TV2 kiểm nguồn; phân biệt bối cảnh có tài liệu với luồng nhóm thiết kế |
| Chủ điểm, khía cạnh phân tích, cây yêu cầu tổng và từng dashboard | Hướng dẫn bài tập nhóm, D36/I36 | Requirement, KPI, cây D1–D3 | TV1/TV4 | Câu hỏi và chỉ số có trường dữ liệu trả lời; phần chốt chính thức ở tuần 2 |
| Quy mô, cập nhật, taxonomy và luồng dữ liệu giữa hệ thống | Hướng dẫn bài tập nhóm, D37/I37 | Inventory, dictionary, taxonomy, nguồn và tần suất | TV2 | TV5 kiểm độc lập; không dùng số kỳ cộng dồn để đếm người duy nhất |
| ERD OLTP, data flow và mapping trường sang OLAP | Hướng dẫn bài tập nhóm, D38/I38 | ERD nguồn và mapping; ghi đúng phương án đã được thầy chấp thuận | TV2/TV3 | Kiểm khóa, quan hệ và giới hạn; sự chấp thuận không thay bằng chứng kiểm dữ liệu |
| Lỗi dữ liệu, phân bố, đặc trưng và tương quan | Hướng dẫn bài tập nhóm, D40/I40 | EDA, bảng/biểu đồ và giải thích phương pháp | TV2 | Kết quả từ dữ liệu thật, thống kê phù hợp loại biến |
| Kiến trúc DW gắn bài toán và công nghệ | Hướng dẫn bài tập nhóm, D41/I41 | Sơ đồ thành phần, triển khai và mô tả công nghệ thực dùng | TV3 | Sơ đồ khớp hệ thống triển khai |
| ETL jobs/pipeline, dữ liệu before–after và OLTP → OLAP | Hướng dẫn bài tập nhóm, D42/I42 | Mã xử lý, mapping, log, before–after | TV3, TV2 hỗ trợ | TV5 kiểm số dòng, lỗi, chạy lại và khả năng tái lập |
| Dimension có dữ liệu cụ thể, số dòng và nhóm liên quan | Hướng dẫn bài tập nhóm, D43/I43 | Dimension catalog, mẫu thật và phân cấp có căn cứ | TV4/TV3 | Đối chiếu catalog với bảng thực tế |
| Model logic/vật lý của staging, mart và DW | Hướng dẫn bài tập nhóm, D44/I44 | Mô hình có phân biệt Fact/Dimension và vùng liên quan | TV3/TV4 | Grain và khóa khớp DDL, không nối Fact làm nhân bản ghi |
| KPI, cây phân tích; thống kê số lượng dashboard theo loại; biểu đồ đa dạng, slicer, định dạng có điều kiện, DAX và công bố lên website | Hướng dẫn bài tập nhóm, D45/I45, D47/I47 | Định nghĩa KPI, danh sách dashboard theo loại, báo cáo Power BI có ví dụ định dạng có điều kiện (ví dụ đánh dấu tăng/giảm), đối soát và bằng chứng công bố | TV4, TV1 review nghiệp vụ | Kiểm danh sách với dashboard thực tế; TV5 kiểm SQL–DAX, bộ lọc, định dạng có điều kiện và truy cập theo phương án được chấp nhận |
| Bài học và phần trình bày 30–45 phút | Hướng dẫn bài tập nhóm, D48, B58 | Kết luận, benchmark, slide, kịch bản demo | TV5/TV1 | Số đo có điều kiện đo; demo đúng thời lượng |
| Các chủ đề mở rộng: thu thập, tiền xử lý, lưu trữ, công cụ… | Hướng dẫn bài tập nhóm, C49:D56 | Tách yêu cầu chính khỏi phần mở rộng nhóm lựa chọn | Cả nhóm | Không tự coi mọi chủ đề liệt kê là bắt buộc |

## 2. Báo cáo và hồ sơ nộp

Nguồn: sheet **Nội dung báo cáo**, B3:C14, B18:B21.

- Bảng đánh giá thành viên, tự đánh giá báo cáo.
- Phần I: Tổng quan Data Warehouse; Phần II: Tổng quan BI.
- Phần III: ứng dụng vào bài toán, gồm requirement, ODS, kiến trúc, tiền xử lý, OLTP, OLAP và dashboard.
- Mục lục, kết luận, tài liệu tham khảo, số trang; Times New Roman 12, căn đều hai bên, kiểm chính tả.
- Sheet **Đánh giá thành viên nhóm**, B13:C16 yêu cầu trưởng nhóm làm bảng, thang 1–5, tối thiểu bốn bậc điểm và chữ ký của tất cả thành viên. Không sử dụng dữ liệu mẫu trong sheet như thông tin thật của Nhóm 13.
- Theo sheet **Hướng dẫn bài tập nhóm**, B61–B62: báo cáo cá nhân tính vào điểm giữa kỳ; báo cáo nhóm tính vào điểm cuối kỳ. TV1 đối chiếu lại hình thức và hạn nộp với thông báo học kỳ hiện hành khi có.

## 3. Phân biệt yêu cầu thầy và quyết định nhóm

| Nội dung | Căn cứ và tình trạng |
|---|---|
| Cần dùng Power BI, hệ quản trị CSDL và các lớp dữ liệu | Có trong tài liệu nguồn |
| 3 Fact, ít nhất 2 Mart, 3 dashboard; PostgreSQL và Python | Quyết định thiết kế của Nhóm 13, không viết là số lượng tối thiểu do thầy nêu trong các dòng nguồn trên |
| Lịch 39 ngày | Kế hoạch nhóm; chưa có ngày bắt đầu và hạn nộp lịch thật |
| Ý nghĩa “100M” | Giảng viên xác nhận là **100 MB**, theo xác nhận của TV1; xem [ghi nhận và số byte của bộ nguồn](../evidence/TV1_week1/100MB_confirmation.md) |
| Mã học kỳ, hạn nộp, kênh nộp và mẫu hiện hành | Cần TV1 đối chiếu thông báo hiện hành khi nhận được; chưa khẳng định đã kiểm đủ |
| Phương án ERD | Trưởng nhóm xác nhận trong trao đổi ngày 11/11/2026 rằng thầy đã đồng ý. Chưa có ảnh/tin nhắn gốc đính kèm; không tự đặt ngày thầy trả lời |
| Công bố Power BI | Có yêu cầu public; khả năng của tài khoản thực tế vẫn cần TV4/TV5 thử |

## 4. Kết quả review và việc theo dõi

TV5 xác nhận bản đối chiếu đủ để TV2 triển khai. Hai góp ý về dashboard và tính điểm báo cáo đã được bổ sung ở mục 1 và 2. Sau review, TV1 ghi nhận giảng viên đã xác nhận đơn vị 100 MB. [Issue #3](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/3) đã DONE/PASS **riêng phần đối chiếu workbook 20252 cho TV2**. Việc cần bổ sung còn mở tại [#1](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/1) (thông báo học kỳ hiện hành, hạn/kênh nộp), [#2](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/2) (ảnh/tin nhắn gốc xác nhận phương án ERD); kiểm Publish to web tại [#12](https://github.com/Linhlss/KDL-2026.1---Nhom13/issues/12). PASS này áp dụng cho bản đối chiếu làm đầu vào, không xác nhận từng sản phẩm của nhóm đã đạt yêu cầu.

Trích xuất các ô nguồn liên quan được lưu trong [minh chứng yêu cầu](../evidence/TV1_week1/course_requirements_excerpt.json); tên file và SHA-256 giúp đối chiếu bản gốc mà không công bố toàn bộ workbook mẫu.
