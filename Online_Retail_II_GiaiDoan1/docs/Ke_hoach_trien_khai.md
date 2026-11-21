

# KẾ HOẠCH TRIỂN KHAI ĐỒ ÁN MÔN MÁY HỌC
## PHÂN KHÚC KHÁCH HÀNG BẰNG RFM VÀ HÀNH VI MUA HÀNG TRÊN BỘ DỮ LIỆU ONLINE RETAIL II

**NHÓM 06 – 03 THÀNH VIÊN**

| Vai trò tạm thời | Họ và tên thành viên | Nhiệm vụ trọng tâm |
|---|---|---|
| **Thành viên 1 (TV1)** – Dữ liệu & Tiền xử lý --- Dữ liệu gốc, kiểm tra RFM, chủ trì EXP-035 (Scaler), viết Chương 3. |
| **TV2 – Thuật toán và mã nguồn** | Chủ trì EXP-034, EXP-036, viết Chương 2 và mục 4.1. |
| **TV3 – Phân tích và báo cáo** | Chủ trì EXP-037, trình bày PCA và hồ sơ cụm, viết Chương 1, mục 4.2 và Chương 5. |


---

### HƯỚNG DẪN SỬ DỤNG KẾ HOẠCH
Tài liệu này là bản phân công và hướng dẫn làm việc nội bộ đã được **hiệu chỉnh kỹ thuật** nhằm:
1. Giải quyết triệt để 5 rủi ro/cạm bẫy kỹ thuật (Label switching, DBSCAN multi-metrics crash, bẫy $k=2$, RobustScaler, thiếu PCA trực quan hóa).
2. Hoàn thiện báo cáo năm chương và slide sau khi chốt thực nghiệm.

> **Nguyên tắc quan trọng:** Mọi kết quả số liệu trong báo cáo phải đến từ lần chạy thực tế. Không điền trước điểm số, không tự tạo nhật ký hồi tố và không ghi một thí nghiệm là hoàn thành khi chưa có file kết quả/bằng chứng.

---

### 1. MỤC TIÊU CUỐI CÙNG
1. Có quy trình hoàn chỉnh từ dữ liệu giao dịch Online Retail II $\rightarrow$ làm sạch $\rightarrow$ tạo RFM $\rightarrow$ phân cụm $\rightarrow$ đánh giá $\rightarrow$ diễn giải hành vi khách hàng.
2. Có thực nghiệm có mục đích, biết rõ mỗi lần thay đổi tham số hay phương pháp nhằm trả lời câu hỏi nào.
3. Giải quyết bài toán cân bằng giữa **độ đo toán học** và **ý nghĩa ứng dụng kinh doanh** (không cứng nhắc chọn $k=2$ chỉ vì Silhouette cao nhất).
4. Có nhật ký thực nghiệm (`experiment_log.csv`) và nhật ký công việc hằng ngày của cả ba thành viên.
5. Trình bày hai phân khúc bằng bảng hồ sơ cụm và biểu đồ PCA.
6. Có báo cáo Word (5 chương), slide thuyết trình, biểu đồ, bảng kết quả, mã nguồn và hướng dẫn chạy lại rõ ràng.

---

### 2. TÌNH TRẠNG DỰ ÁN HIỆN TẠI

| Hạng mục | Hiện trạng đã có | Việc cần làm tiếp (Đã hiệu chỉnh) |
|---|---|---|
| **Notebook 01 – EDA & RFM** | Đã có EDA, quy tắc làm sạch, biểu đồ và bảng RFM. | Rà soát quy tắc làm sạch, kiểm tra tính toàn vẹn bằng `validate_rfm_data.py`. |
| **Bảng RFM** | Đã tạo ra 5.878 dòng khách hàng; CustomerID duy nhất là 5.878. | Giữ cố định file `rfm_table.csv` làm chuẩn đầu vào cho toàn bộ thực nghiệm tiếp theo. |
| **Notebook 02 – Phân cụm** | Có K-Means, Hierarchical Ward và DBSCAN. | Bổ sung kiểm tra độ ổn định, đánh giá đa chỉ số, Elbow plot, Silhouette plot và PCA. |
| **Thực nghiệm hiện có** | 33 cấu hình trên mẫu 2.000 khách hàng; Silhouette tính trên 1.000 khách hàng. | Giữ nguyên kết quả khám phá ban đầu; thực hiện tiếp EXP-034 đến EXP-037. |
| **Kết quả ứng viên ban đầu** | K-Means $k=2$ đạt Silhouette 0,4246. | Xem đây là mốc toán học; đối chiếu với $k=3, 4$ về giá trị phân khúc nghiệp vụ. |
| **Nhật ký** | Đã có `experiment_log.csv` (CL-001 đến CL-033). | Dùng cơ chế nối log tự động với `Run_ID`, ghi nhận tiếp EXP-034 đến EXP-037. |
| **Trình bày EXP-037** | Có hồ sơ hai cụm và biểu đồ PCA. | Sử dụng kết quả trong báo cáo và slide. |

---

### 3. THỨ TỰ LÀM VIỆC BẮT BUỘC (QUY TRÌNH KỸ THUẬT AN TOÀN)

1. **Khóa dữ liệu đầu vào:** TV1 chạy xác thực `python src/validate_rfm_data.py` để đảm bảo `rfm_table.csv` hợp lệ 100%.
2. **Khóa mẫu cố định:** Sử dụng danh sách 2.000 CustomerID trong `outputs/tables/exp034_fixed_customer_sample.csv` xuyên suốt EXP-034, EXP-035, EXP-036.
3. **Thực hiện EXP-034:** Chạy kiểm tra độ ổn định với 5 seed, tính ARI và chuẩn hóa nhãn cụm trước khi tính profiles.
4. **Thực hiện EXP-035:** So sánh `StandardScaler` và `RobustScaler`, kiểm tra phương sai sau scale.
5. **Thực hiện EXP-036:** Đánh giá đa chỉ số (Silhouette, Davies-Bouldin, Calinski-Harabasz) kèm bọc lỗi cho DBSCAN; vẽ đồ thị Elbow & Silhouette analysis.
6. **Chốt mô hình cuối:** Họp nhóm chọn mô hình dựa trên cả metric và ý nghĩa kinh doanh.
7. **Thực hiện EXP-037:** Huấn luyện mô hình đã chọn trên toàn bộ 5.878 khách hàng, giảm chiều PCA 2D/3D trực quan hóa, lưu model `joblib`.
8. **Hoàn thiện báo cáo và slide:** Tổng hợp kết quả theo phân công.
9. **Rà soát & Đóng gói:** Kiểm tra chéo số liệu, chạy thử từ đầu trên máy sạch, xuất slide và nộp bài.

---

### 4. CÁC THỰC NGHIỆM ĐÃ HIỆU CHỈNH KỸ THUẬT

#### EXP-034 – Kiểm tra độ ổn định của K-Means & Xử lý hoán đổi nhãn (Label Switching)
- **Câu hỏi nghiên cứu:** Kết quả phân cụm K-Means $k=2$ (và đối chiếu $k=3$) có thay đổi khi thay đổi `random_state` hay không?
- **Người phụ trách:** TV2 chủ trì code; TV1 kiểm tra mẫu dữ liệu; TV3 tổng hợp bảng và biểu đồ.
- **Giữ cố định:** Cùng danh sách 2.000 khách hàng trong `exp034_fixed_customer_sample.csv`; cùng đặc trưng RFM; cùng `log1p + StandardScaler`; cùng $k=2$, `init='k-means++'`, `n_init=20`.
- **Thay đổi:** Chạy lần lượt `random_state = [42, 7, 21, 123, 2026]`.
- **LƯU Ý KỸ THUẬT BẮT BUỘC:**
  1. **Đo lường độ ổn định:** Dùng **Adjusted Rand Index (ARI)** giữa từng cặp kết quả (hoặc so với mốc seed=42). ARI gần 1 chứng minh thuật toán tìm ra cấu trúc cụm nhất quán mà không phụ thuộc vào thứ tự gán nhãn.
  2. **Chống lỗi hoán đổi nhãn (Label Switching):** Centroid ban đầu ngẫu nhiên có thể hoán đổi Cụm 0 thành Cụm 1. Trước khi so sánh trung vị/mean R/F/M giữa các seed, **phải sắp xếp lại nhãn cụm tăng dần theo trung vị Monetary**.
- **Đầu ra:** `outputs/tables/exp034_seed_stability.csv`; biểu đồ phân bố kích thước cụm và điểm số theo seed.

---

#### EXP-035 – So sánh phương pháp chuẩn hóa (StandardScaler vs RobustScaler)
- **Câu hỏi nghiên cứu:** `StandardScaler` và `RobustScaler` có làm thay đổi chất lượng cụm và hình học cụm RFM không?
- **Người phụ trách:** TV1 chủ trì; TV2 chạy mô hình kiểm chứng; TV3 vẽ biểu đồ so sánh.
- **Giữ cố định:** Cùng mẫu 2.000 khách hàng, cùng 3 đặc trưng RFM đã qua `log1p`, cùng thuật toán K-Means ($k=2, 3$), `n_init=20`, `random_state=42`.
- **Thay đổi:** Phương pháp chuẩn hóa (`StandardScaler` vs `RobustScaler`).
- **LƯU Ý KỸ THUẬT BẮT BUỘC:**
  * Vì `Frequency` có số lượng đơn hàng tập trung nhiều ở 1–2 lần mua, khoảng tứ phân vị (IQR) có thể rất hẹp. TV1 cần kiểm tra phương sai của từng đặc trưng sau khi scale: nếu phương sai của `Frequency` quá lớn so với `Recency` và `Monetary`, khoảng cách Euclidean sẽ bị chi phối bởi Frequency.
- **Đầu ra:** `outputs/tables/exp035_scaling_comparison.csv`; biểu đồ Boxplot so sánh phân phối các biến sau 2 phương pháp scaling.

---

#### EXP-036 – Đánh giá bằng nhiều chỉ số & Phân tích Đánh đổi Kinh doanh
- **Câu hỏi nghiên cứu:** Kết luận chọn mô hình thay đổi ra sao khi xem xét đồng thời nhiều chỉ số hình học và ý nghĩa phân khúc kinh doanh?
- **Người phụ trách:** TV2 chủ trì; TV1 kiểm tra tính toán; TV3 phân tích nghiệp vụ.
- **Các chỉ số đánh giá:**
  1. **Silhouette Score:** Đo độ gắn kết nội cụm và tách biệt ngoại cụm (càng gần 1 càng tốt).
  2. **Davies-Bouldin Index (DBI):** Tỷ lệ khoảng cách nội cụm trên khoảng cách giữa các tâm (càng nhỏ càng tốt).
  3. **Calinski-Harabasz Index (CHI):** Tỷ số phương sai phân tán giữa các cụm và trong từng cụm (càng lớn càng tốt).
  4. **Inertia (Elbow Method):** Tổng bình phương khoảng cách tới tâm (dùng cho K-Means).
- **LƯU Ý KỸ THUẬT BẮT BUỘC:**
  1. **Xử lý ngoại lệ DBSCAN:** Với DBSCAN, phải lọc nhãn `-1` trước khi đưa vào hàm. Nếu số cụm hợp lệ sau lọc $< 2$, **phải gán `np.nan`**, tuyệt đối không để script dừng đột ngột vì `ValueError`.
  2. **Tránh bẫy toán học $k=2$:** Vẽ thêm đồ thị **Elbow Curve ($k=2..8$)** và **Silhouette Plot** từng cụm cho $k=2, 3, 4$. Trình bày phân tích đánh đổi: $k=2$ đạt metric cao nhất nhưng $k=3$ hoặc $k=4$ phân tách được khách hàng VIP, khách hàng tiềm năng và khách hàng có nguy cơ rời bỏ.
- **Đầu ra:** `outputs/tables/exp036_multi_metrics.csv`; hình ảnh `elbow_inertia_curve.png` và `silhouette_analysis_k2_k3_k4.png`.

---

#### EXP-037 – Huấn luyện trên toàn bộ khách hàng & Giảm chiều PCA 2D/3D
- **Câu hỏi nghiên cứu:** Khi áp dụng mô hình cuối cùng lên toàn bộ 5.878 khách hàng, quy mô doanh thu, đặc điểm hành vi và không gian phân cụm thể hiện như thế nào?
- **Người phụ trách:** TV3 chủ trì; TV1 xác nhận số liệu doanh thu; TV2 kiểm tra pipeline và xuất file model.
- **Cách làm:**
  1. Đọc toàn bộ `rfm_table.csv` sạch (5.878 khách hàng).
  2. Áp dụng pipeline: `log1p` $\rightarrow$ scaler được chọn $\rightarrow$ fit mô hình đã chốt.
  3. Gán nhãn cụm cho toàn bộ khách hàng và lưu mô hình vào `models/customer_clustering_pipeline.joblib`.
  4. Áp dụng **PCA giảm 3 chiều RFM xuống 2 thành phần chính (PC1, PC2)** để vẽ biểu đồ phân tán (2D Scatter Plot) tô màu theo cụm và biểu diễn vị trí các tâm cụm (centroids).
- **Đầu ra:**
  - `outputs/tables/customer_clusters_full.csv` (5.878 khách hàng kèm nhãn cụm).
  - `outputs/tables/final_cluster_profiles.csv` (Tổng khách, % khách, % doanh thu đóng góp, Median R/F/M).
  - `outputs/figures/pca_2d_clusters.png` (Biểu đồ phân tán PCA 2D trực quan).
  - `models/customer_clustering_pipeline.joblib`.

---

### 5. PHÂN CÔNG CHI TIẾT THEO TỪNG THÀNH VIÊN (CẬP NHẬT)

#### TV1 – Phụ trách Dữ liệu, EDA & Tiền xử lý
- **Đầu việc chính:**
  1. Chạy xác thực dữ liệu nguồn bằng `src/validate_rfm_data.py`; lưu file báo cáo `outputs/tables/rfm_validation_report.csv`.
  2. Chủ trì thực hiện **EXP-035 (So sánh Scaler)**; phân tích ảnh hưởng của `StandardScaler` vs `RobustScaler` lên các biến RFM.
  3. Soạn thảo nội dung **Chương 3 (Dữ liệu và phương pháp)** của Báo cáo: mô tả dataset gốc, bảng quy tắc làm sạch từng bước, công thức tính RFM.
  4. Rà soát tính nhất quán số liệu dòng/cột/doanh thu trên toàn bộ báo cáo và bảng kết quả.
- **Sản phẩm bàn giao:**
  - Báo cáo kiểm định chất lượng RFM.
  - File kết quả `outputs/tables/exp035_scaling_comparison.csv` và biểu đồ liên quan.
  - Bản nháp hoàn chỉnh Chương 3 của Báo cáo Word.

#### TV2 – Phụ trách Thuật toán, Mã nguồn
- **Đầu việc chính:**
  1. Viết code và chủ trì chạy **EXP-034 (Kiểm tra độ ổn định & ARI)** với 5 seed, giải quyết hiện tượng Label Switching.
  2. Viết code và chủ trì chạy **EXP-036 (Đánh giá đa chỉ số & Elbow/Silhouette plot)**, tích hợp xử lý ngoại lệ cho DBSCAN.
  3. Đóng gói pipeline mô hình đã chọn dưới dạng .joblib.
  4. Soạn thảo nội dung **Chương 2 (Cơ sở lý thuyết)** và **Chương 4.1 (Thiết kế thực nghiệm và so sánh mô hình)**.
  5. Đảm bảo toàn bộ mã nguồn sạch, có chú thích, chạy lại được từ đầu qua file script tự động.
- **Sản phẩm bàn giao:**
  - File kết quả `exp034_seed_stability.csv` và `exp036_multi_metrics.csv`.
  - Các hình ảnh đánh giá: Elbow curve, Silhouette plots.
  - File model lưu trữ `models/customer_clustering_pipeline.joblib`.
  - Bản nháp hoàn chỉnh Chương 2 và mục 4.1 của Báo cáo.

#### TV3 – Phụ trách Phân tích nghiệp vụ và Báo cáo
- **Đầu việc chính:**
  1. Chủ trì **EXP-037**: Áp dụng mô hình lên toàn bộ 5.878 khách hàng, thực hiện PCA giảm chiều 2D, lập hồ sơ cụm chuyên sâu.
  2. Đặt tên phân khúc khách hàng theo chuẩn kinh doanh (ví dụ: *Champions, Loyal Customers, At Risk, Lost Customers*) và đề xuất chiến lược tiếp thị (Marketing Actions) tương ứng.
  3. Trình bày hồ sơ hai cụm và biểu đồ PCA.
  4. Soạn thảo **Chương 1 (Giới thiệu)**, **Chương 4.2 (Diễn giải nghiệp vụ & Khuyến nghị)**, **Chương 5 (Kết luận)**.
  5. Thiết kế Slide thuyết trình PowerPoint và điều phối tiến độ chung của nhóm.
- **Sản phẩm bàn giao:**
  - File kết quả `customer_clusters_full.csv`, `final_cluster_profiles.csv` và biểu đồ PCA.
  - File PowerPoint thuyết trình và bản ghép hoàn chỉnh của Báo cáo Word.

---

### 6. LỊCH LÀM VIỆC ĐIỀU CHỈNH (ĐẨY NHANH TIẾN ĐỘ – TRÁNH NÚT THẮT CỔ CHAI)

> Hoàn thành thực nghiệm, báo cáo và slide trước khi đóng gói.

| Ngày | TV1 – Dữ liệu | TV2 – Thuật toán | TV3 – Nghiệp vụ | Cột mốc hoàn thành trong ngày |
|---|---|---|---|---|
| **11/11 – 12/11** | *(Đã qua)* Rà soát Notebook 01 và tạo `rfm_table.csv`. | *(Đã qua)* Rà soát Notebook 02 và cấu hình 33 mô hình ban đầu. | *(Đã qua)* Thiết lập bảng theo dõi và cấu trúc thư mục. | Dữ liệu RFM sẵn sàng; nhật ký ban đầu được lưu vết. |
| **13/11** | Kiểm định `validate_rfm_data.py`; chốt danh sách 2.000 khách hàng. | Triển khai code và chạy **EXP-034** (5 seed K-Means, tính ARI). | Tổng hợp bảng kết quả EXP-034, vẽ biểu đồ phân bố cụm theo seed. | Hoàn thành EXP-034; xác nhận độ ổn định của K-Means. |
| **14/11** | Chủ trì chạy **EXP-035** (StandardScaler vs RobustScaler). | Kiểm tra phương sai sau scaling; hỗ trợ phân tích khoảng cách Euclidean. | Vẽ Boxplot phân bố sau scaling; cập nhật nhật ký thực nghiệm. | Hoàn thành EXP-035; chốt phương pháp chuẩn hóa tối ưu. |
| **15/11** | Rà soát ma trận đặc trưng cho đa chỉ số. | Chạy **EXP-036** (Silhouette, DBI, CHI, Elbow plot, bọc lỗi DBSCAN). | Lập bảng so sánh đa tiêu chí; họp nhóm chốt mô hình và số cụm ($k$). | **HOÀN THÀNH TOÀN BỘ CHỌN MÔ HÌNH; CHỐT CẤU HÌNH CUỐI.** |
| **16/11** | Hỗ trợ kiểm tra số liệu toàn bộ 5.878 khách hàng. | Chạy **EXP-037** trên full dataset; xuất file model `.joblib`. | Viết code PCA 2D/3D; lập hồ sơ cụm phân tích doanh thu. | Hoàn thành EXP-037; có bộ dữ liệu phân cụm cuối cùng. |
| **17/11** | Soạn Chương 3. | Soạn Chương 2 và mục 4.1. | Rà hồ sơ cụm và PCA. | Có bản thảo theo phân công. |
| **18/11** | Hoàn thiện bảng biểu Chương 3. | Hoàn thiện mục 4.1. | Viết Chương 1 và mục 4.2. | Đối chiếu số liệu báo cáo với EXP-037. |
| **19/11** | Đọc soát chéo Chương 2 và Chương 4; đối chiếu số liệu. | Đọc soát chéo Chương 3; kiểm tra code scripts tái lập kết quả. | Viết **Chương 5** (Kết luận & Hướng mở rộng); ghép Báo cáo Word lần 1. | **Có bản Báo cáo Word hoàn chỉnh 5 chương lần 1.** |
| **20/11** | Rà soát tài liệu tham khảo và định dạng bảng biểu. | Kiểm tra `requirements.txt`, script chạy 1 lệnh (`run_all`). | Thiết kế Slide thuyết trình PowerPoint hoàn chỉnh (15-20 slide). | Báo cáo hoàn thiện lần 2; Slide hoàn thành. |
| **21/11** | Kiểm tra chạy lại dữ liệu. | Kiểm tra mô hình và notebook. | Tập trình bày PCA, hồ sơ cụm và rà bộ nộp. | Sẵn sàng nộp báo cáo, slide và mã nguồn. |
| **22/11** | Kiểm tra file nộp cuối cùng. | Đóng gói mã nguồn & README. | Đại diện nộp trên Google Classroom trước 20:00 (tránh nghẽn mạng). | **HOÀN THÀNH VÀ NỘP BÀI THÀNH CÔNG.** |

---

### 7. TRÌNH BÀY KẾT QUẢ EXP-037

Dùng bảng hồ sơ hai cụm, biểu đồ PCA và số liệu kiểm định để trình bày kết quả.

### 8. CẤU TRÚC BÁO CÁO 5 CHƯƠNG CHUẨN RUBRIC (100 ĐIỂM)

- **Chương 1. Giới thiệu (10đ):**
  - Bối cảnh thị trường bán lẻ trực tuyến tại Anh; ý nghĩa của cá nhân hóa tiếp thị.
  - Mục tiêu nghiên cứu và 3 câu hỏi nghiên cứu cụ thể.
  - Xác định bài toán: Học không giám sát (Clustering) dựa trên hành vi RFM.
- **Chương 2. Cơ sở lý thuyết và nghiên cứu liên quan:**
  - Nguyên lý mô hình RFM trong phân khúc khách hàng.
  - Các thuật toán gom cụm: K-Means, Agglomerative Hierarchical (Ward), DBSCAN (ưu/nhược điểm từng phương pháp).
  - Các chỉ số đánh giá: Silhouette Score, Davies-Bouldin, Calinski-Harabasz, Inertia/Elbow.
  - Kỹ thuật tiền xử lý: `log1p`, `StandardScaler`, `RobustScaler`, và giảm chiều dữ liệu PCA.
- **Chương 3. Dữ liệu và phương pháp (25đ):**
  - Nguồn dữ liệu UCI *Online Retail II*, mô tả thuộc tính và bản quyền CC BY 4.0.
  - Quá trình khám phá dữ liệu (EDA) và bảng thống kê số dòng sau từng bước làm sạch.
  - Công thức tính RFM và kiểm định chất lượng bảng RFM.
  - Thiết kế thực nghiệm: chia mẫu cố định, thiết lập baseline, kiểm soát tính khách quan.
- **Chương 4. Thực nghiệm, kết quả và thảo luận (50đ):**
  - Kết quả kiểm tra độ ổn định theo seed và chỉ số ARI (EXP-034).
  - So sánh phương pháp chuẩn hóa dữ liệu (EXP-035).
  - So sánh đa chỉ số giữa K-Means, Ward, DBSCAN; phân tích Elbow và Silhouette plot; thảo luận đánh đổi giữa toán học và nghiệp vụ để chọn $k$ (EXP-036).
  - Kết quả phân cụm trên toàn bộ 5.878 khách hàng và trực quan hóa không gian PCA 2D (EXP-037).
  - Diễn giải ý nghĩa kinh doanh, đặt tên phân khúc, phân tích đóng góp doanh thu và đề xuất chiến lược tiếp thị.
- **Chương 5. Kết luận và hướng phát triển:**
  - Tóm tắt kết quả chính và giải đáp 3 câu hỏi nghiên cứu.
  - Nêu rõ hạn chế của dữ liệu (dữ liệu giao dịch tĩnh, chưa có biến danh mục hàng hóa, chưa có hành vi click web).
  - Hướng mở rộng trong tương lai: Dự đoán giá trị vòng đời khách hàng (CLV) và bài toán dự báo rời bỏ (Churn Prediction).

---

### 9. NHỮNG ĐIỀU NHÓM TUYỆT ĐỐI KHÔNG LÀM
1. **Không chọn $k=2$ chỉ vì Silhouette cao nhất:** Bắt buộc phải giải thích lý do chọn số cụm có ý nghĩa kinh doanh.
2. **Không dùng Accuracy/Confusion Matrix:** Đây là bài toán học không giám sát, không có nhãn ground-truth.
3. **Không để script bị sập bởi DBSCAN:** Luôn bọc kiểm tra điều kiện $\ge 2$ cụm trước khi tính DBI/CHI.
4. **Không so sánh nhãn cụm trực tiếp giữa các seed:** Phải dùng ARI và sắp xếp lại nhãn trước khi so sánh profiles để tránh bẫy Label Switching.
5. **Không dồn việc viết báo cáo vào 2 ngày cuối cùng.**

---

### 10. VIỆC CẦN CHỐT NGAY HÔM NAY (13/11/2026)
- [ ] Điền tên thật của 3 thành viên vào bảng phân công ở trang đầu.
- [ ] TV1: Chạy kiểm định `validate_rfm_data.py` và xác nhận file `rfm_table.csv`.
- [ ] TV2: Nhận mã nguồn các thực nghiệm EXP-034 đến EXP-036 để tiến hành chạy lấy số liệu.
- [ ] TV3: Khởi tạo repository Google Docs / Word chung và tạo khung 5 chương báo cáo.
