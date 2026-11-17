# Diễn giải cụm từ mẫu RFM

Mô hình được chọn: **K-Means + log1p + RobustScaler + k=2**, `n_init=20`, `random_state=42`.
Silhouette=0.4303; Davies–Bouldin=0.8751; 
Calinski–Harabasz=1058.49; noise=0%.
Nhãn cụm được tạo lại bằng RobustScaler; phần diễn giải dưới đây dùng trung vị của cùng mẫu 2.000 khách.
Trung vị toàn mẫu: Recency=92.00 ngày, 
Frequency=3.00 hóa đơn, Monetary=915.03 GBP.

- **Cụm 0** (1,190 khách): Recency trung vị 282.00 ngày (cao hơn trung vị mẫu), Frequency 2.00 (thấp hơn trung vị mẫu), Monetary 417.76 GBP (thấp hơn trung vị mẫu); tổng Monetary 671072.21 GBP.
- **Cụm 1** (810 khách): Recency trung vị 24.00 ngày (thấp hơn trung vị mẫu), Frequency 8.50 (cao hơn trung vị mẫu), Monetary 3037.61 GBP (cao hơn trung vị mẫu); tổng Monetary 4953883.86 GBP.

## Giới hạn

Đây là mô tả trên mẫu cố định, không phải nhãn chuẩn hay bằng chứng nhân quả; cần kiểm tra ý nghĩa kinh doanh và xác nhận thêm trên toàn bộ dữ liệu.
