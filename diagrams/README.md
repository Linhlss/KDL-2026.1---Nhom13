# Sơ đồ nghiệp vụ

Các sơ đồ mô tả thiết kế nhóm sẽ triển khai, chưa khẳng định hệ thống đã chạy. SVG xem trực tiếp trên GitHub; mở draw.io bằng diagrams.net để chỉnh sửa.

| Nội dung | Bản xem | Bản chỉnh sửa |
|---|---|---|
| Dòng đóng góp của các thành viên | [SVG](00_team_river.svg) | [draw.io](00_team_river.drawio) |
| Quy trình snapshot | [SVG](01_business_process_snapshot.svg) | [draw.io — trang 1](01_business_process.drawio) |
| Quy trình hành động nhân sự | [SVG](01_business_process_events.svg) | [draw.io — trang 2](01_business_process.drawio) |
| Cây nghiệp vụ A01–A10 | [SVG](01_business_tree.svg) | [draw.io](01_business_tree.drawio) |

Các bảng nguồn, ERD nguồn, DW và kiến trúc vật lý do TV2–TV4 xây tiếp; những hình nghiệp vụ này không thay chúng.

## Sơ đồ thực thi TV3

| Phạm vi | Bản xem | Bản chỉnh sửa |
| --- | --- | --- |
| G3: kiến trúc/ETL đủ bốn kỳ, audit và rerun May | [SVG](10_g3_full_pipeline.svg) | [draw.io](10_g3_full_pipeline.drawio) |
| G2: architecture MVP tháng 04 | [PNG](06_architecture_components.png) | [draw.io](06_architecture_components.drawio) |
| G2: checkpoint từng file | [PNG](06_etl_data_flow.png) | [draw.io](06_etl_data_flow.drawio) |
| DW physical, tiếp tục dùng ở G3 vì grain/FK không đổi | [PNG](09_dw_physical_overall.png) | [draw.io](09_dw_physical_overall.drawio) |

G3 mở rộng kỳ dữ liệu và điều phối/kiểm thử; mô hình tháng/cơ quan vẫn PROPOSED chờ TV4. Xem [runbook G3](../docs/TV3_week3_runbook.md). Sơ đồ không phải bằng chứng TV4 đã chạy Power BI hoặc TV5 đã ký QA.
