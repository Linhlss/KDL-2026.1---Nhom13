# Backup schema đầy đủ của kho dữ liệu (L3-16, issue #56)

**Nội dung:** `workforce_schema.sql` là bản `pg_dump --schema-only --no-owner --no-acl` của DB G3 đầy đủ. DB đó được tạo bằng code `0d36e10` trong lượt chạy ngày 27/11/2026, trên PostgreSQL 17.12.
- **Phạm vi:** đủ 7 schema `raw_meta`, `staging`, `ref`, `ods`, `dw`, `mart`, `audit`. Gồm 22 bảng và 1 VIEW (`audit.fk_lookup_coverage`).
- **Ràng buộc:** 21 PK, 33 FK, 6 UNIQUE, 32 CHECK, cùng các index.
- **Đã bỏ khỏi file:** dòng ghi phiên bản và lệnh `\restrict` do `pg_dump` tự sinh, để file ổn định giữa các lần xuất.
- **Không chứa dữ liệu.**

SHA-256: xem `workforce_schema.sql.sha256`.

## Kiểm chứng

TV1 đã kiểm như sau:
1. Tạo DB trống `tv1_schema_check` và nạp `workforce_schema.sql` với `ON_ERROR_STOP=1`.
2. So số ràng buộc theo loại và số bảng/VIEW với DB gốc. Kết quả: **khớp hoàn toàn** (`c=32, f=33, p=21, u=6`; 22 bảng, 1 VIEW).

## Cách dùng

```sh
createdb -h 127.0.0.1 -U <role> workforce_schema_only
psql -X -v ON_ERROR_STOP=1 -h 127.0.0.1 -U <role> -d workforce_schema_only -f handoff/TV3_schema/workforce_schema.sql
```

Muốn có cả dữ liệu thì không dùng file này. Có hai cách:
- **Dựng lại từ Parquet:** theo `docs/TV3_week3_runbook.md`.
- **Backup DB đầy đủ** (vài GB, **không commit**): `pg_dump -Fc -d <DB G3> -f <ổ cá nhân>/workforce_full.dump`, rồi `shasum -a 256` để lưu checksum. Restore bằng `pg_restore --no-owner --no-acl --exit-on-error`.

Dashboard chỉ cần dump tổng hợp tại `handoff/TV3_G3/`.
