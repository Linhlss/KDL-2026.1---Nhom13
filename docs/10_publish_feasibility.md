# Kiểm tra khả năng Publish to web (L4-01 / R02)

**Task:** L4-01 — Owner: TV4 — Review: TV1 / TV5
**Ngày thử:** 18/11/2026
**Trạng thái:** REVIEW (chờ TV1/TV5 xem; chưa nghiệm thu)
**Kết luận ngắn:** Publish lên Power BI Service thành công, nhưng **Publish to web (public) bị admin tenant của trường chặn**. Chưa có link public. Cần xin xử lý hoặc xin thầy duyệt phương án thay thế.

## 1. Mục tiêu

Xác định sớm nhóm có công bố được dashboard lên web hay không (yêu cầu của môn học và rủi ro R02), bằng một báo cáo mẫu chỉ chứa số tổng hợp, trước khi xây dashboard thật.

## 2. Điều kiện thử

| Mục | Nội dung |
|---|---|
| Công cụ | Power BI Desktop (Windows) và Power BI Service (app.powerbi.com) |
| Tài khoản | Email trường (tài khoản thuộc tenant của trường). Không ghi mật khẩu trong tài liệu. |
| File thử | `test_publish.pbix`, lưu ngoài repo, không commit |
| Nơi publish | My workspace |
| Dữ liệu | 4 dòng số tổng hợp lấy từ KPI v0 của nhóm (`docs/02_kpi_dictionary.csv`). Không có dữ liệu cấp bản ghi, không có `REDACTED`, không có lương. |

Bảng dữ liệu mẫu `test_publish`:

| Chi_so | Gia_tri |
|---|---|
| Headcount 03/2025 | 2.289.192 |
| Headcount 04/2025 | 2.271.969 |
| Accessions 04/2025 | 7.153 |
| Separations 04/2025 | 24.088 |

Đây là số tổng kiểm theo metadata nguồn, chưa phải kết quả pipeline.

## 3. Các bước đã làm và kết quả

| # | Bước | Kết quả |
|---|---|---|
| 1 | Tạo báo cáo mẫu trong Power BI Desktop (Enter data, một biểu đồ cột), lưu `test_publish.pbix` | Thành công |
| 2 | Publish từ Desktop lên My workspace bằng tài khoản email trường | Thành công; báo cáo `test_publish` mở được trên Power BI Service |
| 3 | Trên Power BI Service: File → Embed report → Publish to web (public) | **Bị chặn.** Hộp thoại: "Liên hệ với người quản trị của bạn để bật tính năng tạo mã nhúng" |
| 4 | Mở link public trong cửa sổ ẩn danh | **Không thực hiện được** vì chưa tạo được mã nhúng/link |

Nội dung thông báo ở bước 3: để phát hành báo cáo lên web, cần hỏi người quản trị Power BI xem có cho phép tạo mã nhúng mới không; sau khi họ bật tùy chọn này thì mới phát hành được.

## 4. Nhận định

- Nguyên nhân là cài đặt ở cấp tenant do admin quản lý. Người dùng thông thường không tự bật được.
- Việc publish lên service và dùng My workspace vẫn hoạt động, nên chỉ riêng phần công bố public bị chặn.
- Chưa kiểm tra được: link public có truy cập được ở trình duyệt ẩn danh không, và có chặn export dữ liệu không. Hai việc này chỉ kiểm được khi có quyền tạo mã nhúng.
- Ảnh chụp thông báo lỗi **không thay thế** link public. Theo quy ước nhóm, chỉ coi yêu cầu public được đáp ứng khi có URL hoạt động hoặc phương án thay thế đã được thầy chấp thuận.

## 5. Bằng chứng

Lưu trong `evidence/TV4_week1/`:

- [ ] `publish_blocked.png`: hộp thoại admin chặn tạo mã nhúng
- [ ] `published_to_service.png`: báo cáo `test_publish` trên Power BI Service (thấy thanh địa chỉ và tên báo cáo)
- [ ] `desktop_report.png`: báo cáo mẫu trong Power BI Desktop

## 6. Hướng xử lý (làm theo thứ tự)

1. **Báo TV1 và TV5** kết quả này; cập nhật R02 thành "bị chặn, đang xin xử lý". TV1 nêu với thầy.
2. **Hỏi bộ phận IT/quản trị Power BI của trường** (hoặc nhờ thầy hỏi) xem có bật được cài đặt "Publish to web" cho tài khoản của nhóm không.
3. **Thử tài khoản khác:** nhờ TV2/TV3/TV5 thử cùng các bước. Nếu ai publish được thì thống nhất người giữ báo cáo công khai; chỉ dùng số tổng hợp.
4. **Nếu không giải quyết được**, đề xuất thầy duyệt một trong các phương án thay thế:
   - Chia sẻ báo cáo trong Power BI Service cho người được mời (không public hoàn toàn)
   - Nộp file `.pbix` kèm video demo
   - Xuất báo cáo ra PDF/ảnh làm bằng chứng

   Không tự coi phương án thay thế là đã đáp ứng yêu cầu public khi thầy chưa đồng ý.

## 7. An toàn dữ liệu khi công bố sau này

- Chỉ công bố semantic model tổng hợp từ Mart (L4-13); không công bố bản ghi raw/ODS, cột `REDACTED` hay thông tin lương.
- Sau mỗi lần thử Publish to web, vào Settings → Manage embed codes để xóa mã nhúng không còn dùng.
- Báo cáo `test_publish` chỉ ở My workspace, không chia sẻ công khai; có thể xóa sau khi hoàn tất R02.

## 8. Việc còn lại

- [ ] TV1/TV5 review và ghi nhận kết quả R02
- [ ] Có phản hồi từ admin trường hoặc thầy
- [ ] Nếu có quyền: tạo link, TV5 mở ẩn danh, kiểm tra export, cập nhật tài liệu này
- [ ] Cập nhật tracker (L4-01) và issue tương ứng với đường dẫn tài liệu này
