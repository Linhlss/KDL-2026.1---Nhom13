# Cách nhận dữ liệu và giữ baseline

Raw Parquet không đưa vào Git. TV2 nhận bộ `Group13_HR_Management_Dataset` hiện có từ trưởng nhóm; bộ này có 12 file 03–06/2025. Tự kiểm checksum trước khi dùng; không mở Employment toàn bộ bằng Excel vì số dòng vượt giới hạn của một sheet.

Nguồn bản sao mà nhóm đang dùng: [impactproject/opm-ehri-data](https://huggingface.co/datasets/impactproject/opm-ehri-data/tree/main). Nguồn định nghĩa và phát hành chính thức: [OPM Data Downloads](https://data.opm.gov/get-data/data-downloads). TV2 lưu URL cụ thể, version và SHA-256 trong inventory. Không giả định file tải hôm nay từ OPM sẽ có cùng version/hash với baseline local.

Employment baseline dùng v4, Accessions/Separations dùng v5. Với mỗi họ, các tháng là 202503, 202504, 202505, 202506. Tổng 9.181.290 bản ghi qua các kỳ, khoảng 301,5 MB. Xem [metadata đã trích](../evidence/TV1_week1/source_metadata_summary.json); đây là điểm đối chiếu ban đầu, không thay việc TV2 kiểm độc lập.

Để mở rộng cập nhật, [OPM API](https://data.opm.gov/get-data/api-access) có danh sách file và thông tin kỳ/phiên bản. TV3 triển khai nhận kỳ mới sau MVP; không tự nạp các phiên bản mới đè baseline. Có thể demo nạp tháng 03–05 trước rồi nhận tháng 06 đã có, không cần tải thêm nhiều năm dữ liệu. Tải file mới từ API và chạy ETL chưa được thực hiện trong gói TV1 này.

Sản phẩm TV2 sẽ bổ sung: manifest checksum, inventory và tham chiếu mã cần dùng. Chưa có nguồn HR thứ hai, và không cần tìm dataset giả để tạo lịch sử nhân viên.
