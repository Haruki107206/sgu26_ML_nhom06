# Thiết lập và đánh giá mô hình phân cụm (EXP-034–EXP-036)

## Bài toán và dữ liệu

Đồ án phân nhóm khách hàng Online Retail II theo ba biến RFM: **Recency**, **Frequency** và **Monetary**. Đây là bài toán học không giám sát, không có nhãn chuẩn để tính accuracy. Bảng RFM sạch có 5.878 khách hàng; các thực nghiệm so sánh dùng cùng danh sách cố định 2.000 `CustomerID` tại `outputs/tables/exp034_fixed_customer_sample.csv`.

## Pipeline và thiết lập

1. Đọc RFM và mẫu cố định, kiểm tra ba thuộc tính không thiếu và không âm.
2. Áp dụng `log1p` cho từng biến RFM để nén độ lệch phải và giữ được giá trị 0.
3. Chuẩn hóa trên cùng mẫu. EXP-035 so sánh `StandardScaler` với `RobustScaler`; các đánh giá K-Means/Ward/DBSCAN đa thuật toán ở EXP-036 dùng `StandardScaler`. Kết quả EXP-035 và kiểm tra thêm 5 seed được dùng để xác nhận cấu hình cuối RobustScaler.
4. Fit K-Means (`k=2..8`, `init=k-means++`, `n_init=20`, `random_state=42`), Agglomerative Ward (`k=2..8`) và DBSCAN (`eps=0.25, 0.35, 0.45, 0.6, 0.8, 1.0`; `min_samples=5, 10, 20`; Euclidean) trên cùng sample cố định tối đa 2.000 khách.
5. Tính Silhouette, Davies-Bouldin và Calinski-Harabasz trên cùng 1.000 khách đầu của sample (hoặc toàn sample nếu nhỏ hơn). Với DBSCAN, loại nhãn `-1` khỏi metrics, nhưng báo số và tỷ lệ noise trên toàn bộ sample fit. Inertia được tính trong lượt K-Means fit trên sample 2.000 và chỉ so trong cùng scaler/pipeline.

## Ý nghĩa độ đo

- **Silhouette:** càng cao càng tốt, phản ánh độ gần trong cụm và độ tách khỏi cụm khác.
- **Davies-Bouldin (DBI):** càng thấp càng tốt.
- **Calinski-Harabasz (CHI):** càng cao càng tốt.
- **Inertia:** tổng bình phương khoảng cách đến tâm cụm của K-Means. Chỉ so trong cùng dữ liệu, đặc trưng, scaler và thuật toán; thường giảm khi tăng `k`, vì vậy không chọn mô hình chỉ dựa vào inertia. Ward/DBSCAN không có inertia tương đương để so.
- **Noise DBSCAN:** tỷ lệ noise là một phần của quyết định. Metric DBSCAN loại noise nên không so trực tiếp với K-Means/Ward như thể đánh giá cùng số khách; cần đọc đồng thời số điểm được đánh giá.

## Kết quả và quyết định

### EXP-034: ổn định theo seed

K-Means `k=2` chạy với 5 seed trên cùng sample có ARI từng cặp **0,974137–1,000000**, Silhouette **0,297894–0,300278** và inertia **2.855,72–2.855,77**. ARI gần 1 cho thấy phân hoạch ổn định cao trên mẫu này; ARI không phải accuracy. Dao động nhỏ của Silhouette/Inertia đến từ khởi tạo centroid và hội tụ đến các nghiệm cục bộ gần nhau. Kết luận chỉ áp dụng cho sample và pipeline đã cố định.

### EXP-035: so scaler trong điều kiện kiểm soát

Hai scaler được so trên cùng danh sách 2.000 khách fit, cùng `k` (đánh giá riêng `k=2` và `k=3`), cùng `n_init=20`, seed 42 và cùng `log1p`; scaler là yếu tố duy nhất thay đổi. Ba metric tính trên cùng 1.000 khách đầu của sample; Inertia và nhãn dùng để tính ARI dựa trên toàn bộ 2.000 khách fit.

Ở `k=2`, RobustScaler có Silhouette **0,430303** so với **0,424588**, DBI **0,8751** so với **0,8976**, CHI **1.058,49** so với **1.019,49**. ARI giữa hai phân hoạch là **0,8684**, nghĩa là scaler làm thay đổi đáng kể việc gán khách dù metric chỉ nhỉnh vừa phải. Inertia giữa hai scaler khác thang đo nên không so trực tiếp. Sau khi xác nhận độ ổn định RobustScaler qua 5 seed, cấu hình cuối được cập nhật sang RobustScaler.

### EXP-036: thuật toán và số cụm

- **K-Means:** trong `k=2..8`, `k=2` đạt Silhouette cao nhất **0,424588**, DBI thấp nhất **0,8976** và CHI **1.019,49**; không có noise. Khi tăng `k`, Inertia giảm như dự kiến, nhưng metric tách cụm không cải thiện tương ứng và số phân khúc khó diễn giải hơn.
- **Ward:** `k=2` đạt Silhouette **0,332902**, DBI **1,0825**, CHI **633,37**, không có noise. Ward cho cấu trúc phân cấp nhưng không có Inertia để so với K-Means.
- **DBSCAN:** đã tính đủ 18 cấu hình. Có 9 cấu hình cho ít nhất 2 cụm trong sample đánh giá và 9 cấu hình có metric không xác định. Trong các nghiệm hợp lệ có noise không quá 20%, `eps=0.45, min_samples=20` có Silhouette cao nhất **0,316413**, DBI **0,9554**, CHI **542,84**, 2 cụm, **9,7% noise** trên sample fit. Các metric này chỉ tính trên **898** điểm không nhiễu thuộc 1.000 khách đánh giá; không diễn giải như metric toàn bộ sample.

### Cấu hình được chọn

Theo quy tắc chọn Silhouette cao nhất với noise không quá 20% trong bảng quyết định, cấu hình chốt là **K-Means + `log1p` + RobustScaler + `k=2` + `init=k-means++` + `n_init=20` + `random_state=42`**, fit trên sample cố định 2.000 khách. Metric trên cùng 1.000 khách đánh giá: Silhouette **0,430303**, DBI **0,8751**, CHI **1.058,49**; không có noise. Đây là ứng viên có Silhouette cao nhất trong các cấu hình hợp lệ có 2–8 cụm và noise không quá 20%.

Độ ổn định được kiểm tra với 5 seed giống EXP-034: **42, 7, 21, 123, 2026**. ARI nhỏ nhất giữa mọi cặp là **1,000000**; Silhouette và inertia không dao động ở độ chính xác lưu trong bảng. Nhãn cụm có thể đổi thứ tự giữa seed 7, vì vậy chỉ so phân hoạch bằng ARI và diễn giải hồ sơ theo thuộc tính RFM.

Hồ sơ RobustScaler (seed 42): Cụm 0 có **1.190 khách**, Recency trung vị 282 ngày, Frequency 2, Monetary 417,76 GBP; Cụm 1 có **810 khách**, Recency 24 ngày, Frequency 8,5, Monetary 3.037,61 GBP. Vì ARI giữa RobustScaler và StandardScaler là **0,8684**, hồ sơ nhãn StandardScaler cũ đã được tính lại theo RobustScaler.

## Giới hạn

Đây là các chỉ số nội tại trên sample cố định, không chứng minh phân khúc đúng về mặt kinh doanh và chưa đại diện chắc chắn cho toàn bộ 5.878 khách. Cần kiểm tra hồ sơ cụm và đánh giá thêm trên toàn bộ dữ liệu hoặc nhiều mẫu/seed trước khi khái quát. Không so inertia giữa scaler/thuật toán; không bỏ qua tỷ lệ noise khi đọc metric DBSCAN.

## Tệp kết quả và tái lập

- `outputs/tables/exp036_multi_metrics.csv` — K-Means.
- `outputs/tables/exp036_ward_multi_metrics.csv` — Ward.
- `outputs/tables/exp036_dbscan_multi_metrics.csv` — DBSCAN và noise.
- `outputs/tables/exp036_all_algorithms_multi_metrics.csv` — gộp metric ba họ thuật toán.
- `outputs/tables/exp036_robust_stability.csv` — kiểm tra RobustScaler K-Means qua 5 seed.
- `outputs/tables/model_decision_exp034_exp036.csv` — bảng quyết định và đánh đổi.
- `outputs/tables/selected_clustering_model.csv` — cấu hình chọn hiện tại.
- `outputs/tables/selected_model_cluster_profiles.csv` và `selected_model_customer_labels.csv` — hồ sơ và nhãn theo RobustScaler đã chọn.
- `src/complete_model_evaluation.py` — chạy lại metric, quyết định và CSV đầu ra.
- `src/write_model_evaluation_journals.py` — đồng bộ nội dung vào hai workbook nhật ký.
