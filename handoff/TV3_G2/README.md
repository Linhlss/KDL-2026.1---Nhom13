# Bản database G2 cho TV4

TV4 dùng `workforce_g2.dump` để khôi phục dữ liệu MVP tháng 04/2025 vào PostgreSQL 18 trên Windows và kết nối Power BI. File được tạo từ `workforce_g2_transfer` bằng PostgreSQL 18.7, định dạng custom, dung lượng 20.918 byte.

[Tải workforce_g2.dump](https://raw.githubusercontent.com/Linhlss/KDL-2026.1---Nhom13/tv3/g2-pipeline/handoff/TV3_G2/workforce_g2.dump) · [SHA-256](workforce_g2.dump.sha256) · [Runbook đầy đủ](../../docs/07_runbook.md)

Clone hoặc cập nhật nhánh `tv3/g2-pipeline` để nhận file tại `handoff/TV3_G2/workforce_g2.dump`. Cũng có thể dùng liên kết tải trực tiếp phía trên. Nếu tải file riêng, lưu file ở thư mục đang mở trong PowerShell.

## Kiểm file và restore trên Windows

Mở PowerShell tại thư mục chứa file. Nếu vừa clone repo, chuyển vào `handoff/TV3_G2` trước. PostgreSQL 18 cần có các lệnh `createdb`, `pg_restore` và `psql` trong PATH.

```powershell
Get-FileHash .\workforce_g2.dump -Algorithm SHA256
pg_restore --version
pg_restore --list .\workforce_g2.dump
```

Checksum kỳ vọng là `837729db8c478d0cd8a08fa7aebb0b1154f67fbfeeeff7e31483ab0a48b3bcfa`.

Thay `TV4_ROLE` bằng user PostgreSQL trên máy TV4. Dùng database mới hoặc rỗng. Nếu `workforce_g2` đang có dữ liệu, chọn tên đích mới và thay cùng tên trong các lệnh sau.

```powershell
createdb -h 127.0.0.1 -U TV4_ROLE workforce_g2
pg_restore -h 127.0.0.1 -U TV4_ROLE -d workforce_g2 --no-owner --no-acl --exit-on-error .\workforce_g2.dump
psql -X -h 127.0.0.1 -U TV4_ROLE -d workforce_g2 -c "SELECT SUM(headcount) AS k01 FROM mart.workforce_monthly WHERE month_key=202504;"
psql -X -h 127.0.0.1 -U TV4_ROLE -d workforce_g2 -c "SELECT SUM(accessions) AS k06, SUM(separations) AS k07 FROM mart.personnel_flows_monthly WHERE month_key=202504;"
```

| Bảng đã bàn giao | Số dòng |
| --- | ---: |
| `dw.dim_month` | 3 |
| `dw.dim_agency` | 123 |
| `dw.dim_action_category` | 14 |
| `mart.workforce_monthly` | 114 |
| `mart.personnel_flows_monthly` | 88 |

Kết quả kỳ vọng sau restore là **K01 = 2.271.969**, **K06 = 7.153**, **K07 = 24.088**. Trong Power BI Desktop, kết nối PostgreSQL với server `localhost:5432`, database đích vừa restore và tài khoản của TV4. Nạp hai bảng Mart để đối soát KPI.

Ngày 23/11/2026, TV3 đã thử restore lại chính bản dump này vào database tạm, đối chiếu đủ năm bảng và ba tổng KPI. [Bằng chứng kiểm lại](../../evidence/TV3_week2/08_dump_handoff_check.txt) ghi checksum và kết quả thực chạy.

Thiết kế Dimension và nhóm agency Unknown đang chờ TV2/TV4 review theo [báo cáo bàn giao](../../reports/TV3_week2_summary.md). Có 206.687 dòng Employment, 1.591 dòng Accessions và 1.936 dòng Separations được giữ trong agency Unknown. TV4/TV5 cần ghi nhận kết quả Windows, PBIX và SQL–DAX trước khi chốt G2.
