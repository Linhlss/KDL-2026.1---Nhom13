# TV2 — Hướng dẫn chạy Data Profiling (12 Parquet)

## 1. Yêu cầu
- Windows 10/11; Python 3.10 trở lên; 2–4 GB RAM trống trở lên được khuyến nghị; ổ đĩa còn tối thiểu khoảng 1 GB.
- Mở terminal trong thư mục chứa `profile_12_parquet.py`.
- Cài thư viện: `python -m pip install duckdb`.

## 2. Chuẩn bị dữ liệu
Tạo thư mục `data/zips/` nằm cạnh `profile_12_parquet.py` và đặt **ba ZIP gốc** vào đó, không cần giải nén:

```
TV2_Data_Profiling/
  profile_12_parquet.py
  data/
    zips/
      employment-20261116T044655Z-1-001.zip
      accessions-20261116T044630Z-1-001.zip
      separations-20261116T044657Z-1-001.zip
```

Nếu bạn đã giải nén, có thể để 12 `.parquet` trong `data/raw/employment/`, `data/raw/accessions/`, `data/raw/separations/` và không cần thêm ZIP.

## 3. Chạy
```bash
python profile_12_parquet.py
```

Script tự giải nén ZIP (nếu có), xác minh **4 file/nhóm**, profile từng file theo trình tự, lưu kết quả vào `reports/profiling/`.

Để kiểm tra thêm *các dòng có hash trùng nhau* (chỉ là dấu hiệu, không được tự xóa):
```bash
python profile_12_parquet.py --check-duplicates
```

## 4. Kết quả
- `column_profile.csv`: 804 dòng (64×4 + 68×4 + 69×4), NULL, chuỗi rỗng, REDACTED, số giá trị phân biệt **ước lượng** của từng cột/từng file.
- `count_quality.csv`: phân loại trường `count` thành số hợp lệ, NULL, REDACTED, giá trị bất thường; tính tổng phần có thể chuyển thành số.
- `month_consistency.csv`: phân biệt tháng ghi trong tên file với `snapshot_yyyymm` (Employment), hoặc `personnel_action_effective_date_yyyymm` (events).
- `category_top10.csv`: top 10 category theo số **bản ghi** ở từng file cho một số trường quan trọng; `count_numeric_sum` chỉ là phần có thể cast sang số.
- `file_summary.csv`: số hàng và cột đã đọc thật.
- `potential_duplicates_hash.csv` chỉ khi bật `--check-duplicates`: *dấu hiệu* trùng toàn dòng dựa trên hash, không phải lý do tự động loại dữ liệu.

## 5. Cách đọc đúng và gửi cho TV3
1. Phân biệt `NULL`, chuỗi rỗng và `REDACTED`: không gộp ba nhóm hay đổi REDACTED thành `0`.
2. `distinct_approx` là giá trị **ước lượng** từ DuckDB; chỉ xác nhận chính xác mã quan trọng bằng `COUNT(DISTINCT ...)` nếu cần.
3. Employment là dữ liệu theo kỳ; **không cộng số dòng của bốn tháng để kết luận 9,18 triệu nhân viên**.
4. Tháng hiệu lực khác tháng file ở Accessions/Separations chưa chắc là lỗi; báo cáo riêng để TV3/TV4 chọn đúng quy tắc thời gian.
5. `count` là dạng chuỗi ở nguồn; trước khi đưa vào warehouse, TV3 cần quy tắc parse, quy tắc che dữ liệu và định nghĩa grain được nhóm thống nhất.
6. Tên và mã cơ quan, nghề nghiệp, category phải đối chiếu **codebook OPM/EHRI**. Không dùng `approx_count_distinct` để khẳng định số lượng mã chính xác.
7. Trong báo cáo, nêu tối thiểu: (a) top cột NULL, (b) top cột REDACTED, (c) kiểm tra count, (d) kiểm tra tháng, (e) phát hiện khác biệt giữa ba nhóm.

## 6. Chú ý tài nguyên
Phân tích toàn bộ 12 file có thể tốn thời gian vì phải quét nội dung thực tế. Script chạy từng file để giảm áp lực bộ nhớ; không nạp cả 9 triệu bản ghi thành một DataFrame pandas. Nếu máy yếu, chạy bản thường trước và chỉ bật `--check-duplicates` sau.

## 7. Giới hạn kiểm chứng
Mã được viết theo schema và tên file thật của ZIP Nhóm 13, đã kiểm tra cú pháp Python. Phiên làm việc tạo bộ hướng dẫn chưa có DuckDB để chạy thử truy vấn trên giá trị thực, vì vậy hãy chạy trên máy của bạn và gửi lại CSV/log nếu có lỗi để hiệu chỉnh.
