# Ví dụ Chi-square và Cramér’s V từ Employment 202504

Nguồn là bảng chéo [agency_occupation](05_crosstab_agency_occupation.csv). Ô minh họa có nhóm dòng **VA** và nhóm cột **0301**.

1. Oij = 9,765. Tổng dòng = 471,620. Tổng cột = 109,661. N = 2,271,969.
2. Eij = tổng dòng × tổng cột / N = 22763.65602700.
3. Đóng góp của ô = (Oij − Eij)² / Eij = 7422.58002439.
4. Cộng mọi ô được χ² = 1395108.202648, df = 100.
5. V = sqrt(χ² / [N × min(r−1, c−1)]) = 0.247801.

E nhỏ nhất = 1682.739. Có 0/121 ô E < 5. Cramér’s V phụ thuộc cách phân nhóm. Các mã hiếm được gom vào Other.
