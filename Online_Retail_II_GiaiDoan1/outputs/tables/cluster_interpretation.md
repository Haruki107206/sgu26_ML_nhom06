# Diễn giải cụm từ mẫu RFM

Mô hình được chọn theo silhouette: **KMeans_tuned** (n_clusters=2; init=k-means++; n_init=20; random_state=42).
Silhouette trên tập đánh giá cố định: **0.4246**; 2 cụm; noise DBSCAN 0.00%.
Trung vị toàn mẫu: Recency=92.00 ngày, Frequency=3.00 hóa đơn, Monetary=915.03 GBP.

Các mô tả dưới đây so sánh trung vị của từng cụm với trung vị mẫu chung; đây là diễn giải mô tả, không phải nhãn chân lý hay bằng chứng nhân quả.

- **Cụm 0** (1,162 khách hàng trong mẫu): Recency 306.00 ngày (cao hơn trung vị mẫu), Frequency 2.00 hóa đơn (thấp hơn trung vị mẫu), Monetary 412.66 GBP (thấp hơn trung vị mẫu); doanh thu gộp trong cụm 716635.46 GBP.
- **Cụm 1** (838 khách hàng trong mẫu): Recency 24.00 ngày (thấp hơn trung vị mẫu), Frequency 8.00 hóa đơn (cao hơn trung vị mẫu), Monetary 2880.55 GBP (cao hơn trung vị mẫu); doanh thu gộp trong cụm 4908320.61 GBP.

## Giới hạn

Kết quả và hồ sơ chỉ đại diện cho mẫu ngẫu nhiên cố định tối đa 2.000 khách hàng. Cần kiểm tra độ ổn định trên nhiều seed/bootstrap và xem ý nghĩa kinh doanh trước khi dùng làm kết luận cuối.
