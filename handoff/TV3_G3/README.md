# Database G3 đủ bốn kỳ cho TV4

[Tải workforce_g3.dump](https://raw.githubusercontent.com/Linhlss/KDL-2026.1---Nhom13/main/handoff/TV3_G3/workforce_g3.dump) · [SHA-256](workforce_g3.dump.sha256) · [File trong repo](workforce_g3.dump)

> **Bản mới ngày 27/11/2026 — thay bản `6d85ea29…` cũ.** Bản cũ đưa 7 cơ quan (Bộ Tài chính, Bộ Nội vụ, NASA, HUD, FQ, AH, HB) vào nhóm Unknown, chiếm khoảng 9% headcount. Bản này dùng kết quả duyệt nhãn EHRI của TV2, nên **Agency Unknown = 0**. Tổng K01/K06/K07 từng tháng không đổi; chỉ phần chia theo cơ quan thay đổi. TV4 hãy **restore lại vào database mới** và làm mới PBIX trước khi chụp ảnh minh chứng. Chi tiết: [giải trình TV1](../../docs/TV1_giai_trinh_tich_hop_G3.md).

Cập nhật nhánh **`main`** (`git pull`) để nhận cả hai file tại `handoff/TV3_G3/`.
- **Nội dung:** bản tổng hợp G3 tháng 03–06/2025, gồm ba Dimension và hai Mart.
- **Định dạng:** custom archive tạo bằng `pg_dump` 17.12, **30.343 byte**. `pg_restore` 17 hoặc 18 đều đọc được.
- **Kiểm chứng:** file khớp nguyên byte bản đã kiểm tại [bằng chứng chuyển/restore](../../evidence/TV3_week3/06_transfer_restore.txt) và [kiểm lại file bàn giao](../../evidence/TV3_week3/12_dump_handoff_check.txt).

Không dùng dump G2 (chỉ có tháng 04) để đại diện dữ liệu G3.

SHA-256 kỳ vọng:

```text
ec3ddf32a29cadb8e8c2b974f79d53959b6bcda1d49017925b46a2ed0aa94cef
```

## Restore trên Windows

Mở PowerShell tại gốc repo. Cần PostgreSQL 18 và các lệnh `createdb`, `pg_restore`, `psql` trong PATH. Thay `TV4_ROLE` bằng role thực tế; chọn database mới. Các lệnh CLI hỏi mật khẩu theo cấu hình server, không tự đọc file dotenv.

```powershell
$Dump = '.\handoff\TV3_G3\workforce_g3.dump'
$Expected = ((Get-Content '.\handoff\TV3_G3\workforce_g3.dump.sha256').Trim() -split '\s+')[0]
$Actual = (Get-FileHash $Dump -Algorithm SHA256).Hash.ToLowerInvariant()
if ($Actual -ne $Expected) { throw 'SHA-256 không khớp, dừng restore.' }
pg_restore --list $Dump
if ($LASTEXITCODE -ne 0) { throw 'Không đọc được archive.' }
$PgRole = 'TV4_ROLE'
$Database = 'workforce_g3_tv4'
createdb -h 127.0.0.1 -p 5432 -U $PgRole $Database
if ($LASTEXITCODE -ne 0) { throw 'Cần database đích mới; kiểm tra tên và quyền trước khi tiếp tục.' }
pg_restore -h 127.0.0.1 -p 5432 -U $PgRole -d $Database --no-owner --no-acl --exit-on-error $Dump
if ($LASTEXITCODE -ne 0) { throw 'Restore thất bại.' }
psql -X -v ON_ERROR_STOP=1 -h 127.0.0.1 -p 5432 -U $PgRole -d $Database -c "SELECT 'dw.dim_month' AS table_name,count(*) FROM dw.dim_month UNION ALL SELECT 'dw.dim_agency',count(*) FROM dw.dim_agency UNION ALL SELECT 'dw.dim_action_category',count(*) FROM dw.dim_action_category UNION ALL SELECT 'mart.workforce_monthly',count(*) FROM mart.workforce_monthly UNION ALL SELECT 'mart.personnel_flows_monthly',count(*) FROM mart.personnel_flows_monthly;"
if ($LASTEXITCODE -ne 0) { throw 'Kiểm count thất bại.' }
psql -X -v ON_ERROR_STOP=1 -h 127.0.0.1 -p 5432 -U $PgRole -d $Database -f .\sql\07_g3_kpi.sql
if ($LASTEXITCODE -ne 0) { throw 'Kiểm SQL KPI thất bại.' }
```

| Bảng | Số dòng |
| --- | ---: |
| dw.dim_month | 9 |
| dw.dim_agency | 521 |
| dw.dim_action_category | 53 |
| mart.workforce_monthly | 510 |
| mart.personnel_flows_monthly | 361 |

| Tháng | K01 Headcount | K06 Accessions | K07 Separations |
| --- | ---: | ---: | ---: |
| 202503 | 2.289.192 | 4.862 | 22.061 |
| 202504 | 2.271.969 | 7.153 | 24.088 |
| 202505 | 2.255.056 | 8.813 | 26.415 |
| 202506 | 2.241.780 | 9.954 | 19.947 |

TV4 kết nối Power BI tới database vừa restore, nạp `dim_month`, `dim_agency`, `workforce_monthly`, `personnel_flows_monthly`. [Bốn quan hệ Single và cách giữ Unknown](../TV3_G2/README.md) tiếp tục áp dụng cho grain tháng/cơ quan. Category/các chiều bổ sung cần duyệt thiết kế; dump không chứa Raw/ODS/Fact. TV5 replay đầy đủ từ Parquet theo [runbook G3](../../docs/TV3_week3_runbook.md).

[Kiểm lại đúng bản dump bàn giao](../../evidence/TV3_week3/12_dump_handoff_check.txt) ghi checksum, năm bảng, KPI bốn kỳ, Agency Unknown = 0 và nhãn của TR/IN/NN/HU sau restore (TV1 chạy trên macOS ngày 27/11/2026). Windows/PBIX và SQL–DAX vẫn cần TV4/TV5 xác nhận thực tế.
