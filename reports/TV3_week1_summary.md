# Bàn giao tuần 1 của TV3

| Task | Trạng thái | Kết quả đã có | Việc cần khi review |
| --- | --- | --- | --- |
| L3-01 · Ngày 3 | REVIEW | Kết nối PostgreSQL 18.7, tạo đủ 7 schema, cài và kiểm thư viện. [Hướng dẫn môi trường](../docs/06_environment_setup.md) · [Bằng chứng](../evidence/TV3_week1/01_postgres_environment.txt) | TV2/TV5 chạy lại hướng dẫn và kiểm schema. |
| L3-02 · Ngày 5 | REVIEW | Nạp đủ 7.153 dòng Accessions và 50.000 dòng đầu Employment, SQL và đối soát từng ô đều PASS. [Kết quả](TV3_week1_prototype_results.md) · [Log](TV3_week1_load_log.csv) | TV2 đối chiếu SHA-256 với baseline của nhóm. TV5 chạy lại và kiểm SQL. |
| L3-03 · Ngày 7 | REVIEW | Có sơ đồ thành phần v0 và phương án chuyển bản sao DB riêng. [Draw.io](../diagrams/06_architecture_components.drawio) · [PNG](../diagrams/06_architecture_components.png) | TV2/TV5 review sơ đồ. TV4 xác nhận môi trường Windows và cách nhận DB. |
| L3-04 · Ngày 7 | BLOCKED | Đã profile 4 mã ứng viên trên hai bảng thử. [Biên bản sơ bộ](../docs/TV3_week1_erd_review.md) · [Số đo](../evidence/TV3_week1/07_key_profile.txt) | TV2 cung cấp ERD v0, dictionary, codebook và audit. TV3 áp kết quả vào từng quan hệ, TV5 kiểm lại. |

Nhánh cục bộ `tv3/week1-setup`. Ba mục `REVIEW` đã có sản phẩm và bằng chứng để kiểm. TV1 điều phối xác nhận người review và mốc phản hồi. Chuyển sang `DONE` sau khi reviewer xác nhận.
