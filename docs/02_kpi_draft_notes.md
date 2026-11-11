# Cách dùng KPI bản nháp

Đọc cùng [bảng K01–K10](02_kpi_dictionary.csv). Đây là **v0 để TV2 khảo sát**, chưa chốt DAX, Fact/Dim hoặc tiêu chí nghiệm thu tuần 2.

- Một dòng Employment trong baseline là một bản ghi của snapshot, không phải ID của một người tồn tại xuyên tháng. K01 đếm bản ghi trong đúng một kỳ.
- Metadata hiện có cho thấy `count` là chuỗi `"1"`, không NULL ở 12 file. TV2 xác nhận lại khi đọc dữ liệu. Chỉ SUM cột này sau khi chuyển kiểu và kiểm giá trị hợp lệ; COUNT bản ghi vẫn phải đối soát được.
- `snapshot_yyyymm` có thật trong Employment. `personnel_action_effective_date_yyyymm` có thật trong hai họ sự kiện.
- **`report_month` là metadata nhóm tạo từ tên file/kỳ file, không phải cột raw có sẵn.** TV2 ghi cả nguồn xác định kỳ và quy tắc tên file; TV3 kiểm nó khớp manifest.
- D1/D3 dùng tháng snapshot. D2 mặc định tháng báo cáo. Nếu thêm góc nhìn theo tháng hiệu lực, nhãn và bộ lọc phải ghi rõ phạm vi file báo cáo đang bao phủ.
- TV2 đánh dấu trường nào đủ nghĩa, mã nào cần kiểm scope và KPI nào chưa thể tính; không tự sửa dữ liệu để số đẹp. TV4/TV1 chốt filter, BLANK/0 và phép so sánh ở tuần 2.
- Không có số thật theo cơ quan/nhóm trong gói này. Các tên Fact/Dim/Mart là thiết kế mục tiêu, chưa phải bảng đã xây.
