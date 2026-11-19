# EDA bổ sung TV2 · C05

Phạm vi là 12 Parquet baseline 03–06/2025. Hai bảng chéo dùng riêng Employment 202504. Đơn vị phân tích là bản ghi snapshot hoặc lượt hành động công bố.

## Bảy chiều chất lượng

| Chiều | Bằng chứng |
|---|---|
| Đầy đủ | Profiling v1 đo NULL, rỗng và REDACTED theo từng cột/file. |
| Hợp lệ | Kiểm cú pháp tháng, count và chuyển kiểu lương qua DuckDB. |
| Nhất quán | Schema hash ổn định theo họ, cột thời gian được kiểm theo grain. |
| Duy nhất | Vị trí dòng duy nhất theo file, cùng checksum khóa bộ nguồn. |
| Toàn vẹn tham chiếu | Audit exact đủ kỳ. Phạm vi catalog lịch sử đang chờ đối chiếu. |
| Bất thường | Kiểm lương không parse được hoặc âm và phân bố lương quan sát được. |
| Kịp thời | 593 event khác kỳ công bố/hiệu lực. Chưa có timestamp gửi để đo trễ. |

[Kiểm dữ liệu](05_data_quality.csv) · [Audit khóa](../docs/04_relationship_audit.csv) · [Profiling theo file](../evidence/TV2_week1/TV2_Data_Quality_Phan_Tich_V1/column_profile.csv)

## Phân bố và thời gian

| Tháng | Agency có mã quan sát | Số agency trong top 20% | Bản ghi top 20% | % toàn snapshot |
|---|---:|---:|---:|---:|
| 202503 | 130 | 26 | 2,248,189 | 98.21 |
| 202504 | 120 | 24 | 2,224,030 | 97.89 |
| 202505 | 130 | 26 | 2,215,414 | 98.24 |
| 202506 | 130 | 26 | 2,202,642 | 98.25 |

Top 20% làm tròn lên theo số mã agency có mặt. Tỷ lệ lấy toàn bộ snapshot làm mẫu số. Bảng phân bố chứa cả mã hành động và các trạng thái bị thiếu.

Histogram lương 202504 dùng 1,217,956/2,271,969 giá trị quan sát được. Các cột có bề rộng 25.000 USD và một cột gom từ 300.000 USD.

So sánh MoM mô tả phạm vi bốn kỳ. Employment giảm trong bốn snapshot, Accessions tăng theo kỳ file và Separations đạt đỉnh tháng 05.

[Phân bố mã](05_code_distribution.csv) · [Pareto](05_charts/agency_pareto.svg) · [Histogram](05_charts/pay_histogram.svg) · [MoM](05_monthly_records.csv) · [Biểu đồ theo tháng](05_charts/monthly_records.svg)

## Liên hệ giữa biến phân loại

Mỗi trục giữ 10 mã có tần suất biên cao nhất, gom các mã còn lại vào Other. Bản ghi thiếu hoặc REDACTED ở một trong hai trục được tính vào số loại khỏi bảng chéo. Grade dùng cặp Pay Plan + Grade để giữ ngữ cảnh. Kiểm expected count trước khi đọc p-value.

| Bảng | N | Loại | Kích thước | χ² | df | Cramér’s V | E nhỏ nhất | Ô E < 5 | p |
|---|---:|---:|---|---:|---:|---:|---:|---:|---|
| [agency_occupation](05_crosstab_agency_occupation.csv) | 2,271,969 | 0 | 11 × 11 | 1395108.20 | 100 | 0.2478 | 1682.74 | 0 | < 1e-300 |
| [occupation_grade](05_crosstab_occupation_grade.csv) | 2,267,274 | 4,695 | 11 × 11 | 1641894.90 | 100 | 0.2691 | 911.79 | 0 | < 1e-300 |

V mô tả độ liên hệ trong các nhóm đã gom của snapshot này. Với dữ liệu toàn snapshot và cỡ N lớn, p-value dùng để minh họa phương pháp. Bốn kỳ chỉ đủ mô tả biến động ngắn hạn.

[Ví dụ tính từng ô](05_categorical_method_example.md)
