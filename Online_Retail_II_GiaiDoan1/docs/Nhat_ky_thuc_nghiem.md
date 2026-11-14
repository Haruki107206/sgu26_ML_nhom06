# NHẬT KÝ THỰC NGHIỆM – ĐỒ ÁN MÁY HỌC NHÓM 06
## Phân khúc khách hàng bằng RFM và hành vi mua hàng – Online Retail II

> Nhật ký ghi lại **quá trình thực tế** của từng thực nghiệm, bao gồm cả lỗi phát sinh, nguyên nhân, và hành động khắc phục.
> Mọi kết quả số liệu trong báo cáo được truy nguyên về các dòng trong nhật ký này.
> File bổ sung chi tiết: `logs/experiment_log.xlsx` (sheet: **Experiment_Log**, **Trial_and_Error_Log**, **Daily_Journal**).

---

## TUẦN 1 (04/11 – 09/11): Xây dựng nền tảng dữ liệu và thực nghiệm ban đầu

---

### ERR-001 – Thứ Tư, 04/11/2026 – 11:20
**Thực hiện:** TV1 (Dữ liệu)
**Nhiệm vụ:** Thử tính bảng RFM trực tiếp trên dữ liệu giao dịch thô để xem kết quả.

**Vấn đề phát sinh:**
Chạy đoạn code tính `Monetary = Quantity * UnitPrice` cho mỗi khách hàng mà không lọc hóa đơn hủy và số lượng âm trước. Khi gọi `np.log1p(rfm["Monetary"])` ở bước tiếp theo, script dừng và văng lỗi:
```
ValueError: Input contains NaN, infinity or a value too large
```
Kiểm tra thêm phát hiện **320 khách hàng có tổng Monetary âm** do các hóa đơn hủy (mã bắt đầu bằng `C`) có số lượng âm làm tổng doanh thu âm.

**Nguyên nhân gốc rễ:** Pipeline RFM không có bước lọc "hành vi mua hàng dương" – lẫn hóa đơn hủy, hoàn trả, giao dịch bất thường vào cùng bảng tổng hợp.

**Hành động khắc phục (TV1 – hoàn thành 04/11 lúc 14:07):**
1. Thêm 4 bước lọc nghiêm ngặt vào Notebook 01:
   - Bước 1: Loại bỏ bản ghi trùng hoàn toàn (–34.335 dòng)
   - Bước 2: Loại bỏ bản ghi thiếu `CustomerID` (–235.151 dòng)
   - Bước 3: Loại bỏ hóa đơn có mã bắt đầu bằng `C` (–18.390 dòng)
   - Bước 4: Loại bỏ `Quantity ≤ 0`, `UnitPrice ≤ 0` hoặc ngày không hợp lệ (–70 dòng)
2. Thêm kiểm tra `assert (rfm["Monetary"] > 0).all()` trước khi gọi log.

**Kết quả sau sửa (Git commit `32a15c7`):**
- Bảng RFM sạch: **5.878 khách hàng**, **0 giá trị âm**, sẵn sàng cho log1p.

---

### CL-001 đến CL-033 – Thứ Năm, 06/11/2026 (TV2) & Thứ Bảy, 08/11/2026 (TV3)
**Mục tiêu:** Khám phá không gian thuật toán và tham số phân cụm.

**Thực hiện:**
- Thứ Năm 06/11 (commit `0409e57`, TV2 Trần Thiện Hùng): Chạy baseline K-Means k=3 và thử sơ bộ DBSCAN.
- Thứ Bảy 08/11 (commit `a3754d7`, TV3 Võ Thuận Thiên): Mở rộng thành 33 cấu hình đầy đủ.

---

### ERR-002 – Thứ Năm, 06/11/2026 – 14:15
**Thực hiện:** TV2 (Thuật toán)
**Nhiệm vụ:** Thử chạy DBSCAN trực tiếp trên dữ liệu RFM chưa chuẩn hóa để xem thuật toán có phát hiện được cụm không.

**Vấn đề phát sinh:**
Chạy DBSCAN với `eps=50.0, min_samples=10` trên dữ liệu RFM thô (Recency tính bằng ngày, Monetary tính bằng GBP). Kết quả: **99.8% điểm bị gán nhãn nhiễu (-1)**, chỉ có 4 khách hàng thuộc 1 cụm. Thực nghiệm thất bại hoàn toàn.

**Nguyên nhân gốc rễ:** Monetary có giá trị lên đến hàng chục nghìn GBP trong khi Recency chỉ 0–700 ngày và Frequency 1–200. Khoảng cách Euclidean bị chi phối tuyệt đối bởi chiều Monetary, khiến DBSCAN không nhìn thấy cụm thực sự.

**Hành động khắc phục (TV2 – hoàn thành 06/11 lúc 16:10):**
1. Áp dụng biến đổi `log1p(x)` để nén phân phối lệch phải mạnh của Frequency và Monetary.
2. Áp dụng `StandardScaler` đưa cả 3 biến về cùng thang: mean=0, std=1.
3. Điều chỉnh lại eps về khoảng 0.25–1.0 phù hợp với dữ liệu đã chuẩn hóa.

**Kết quả sau sửa:**
DBSCAN với `eps=1.0, min_samples=20` đạt Silhouette=0.3355 với tỷ lệ nhiễu 5.65% – có thể xử lý được.

---

## TUẦN 2 (10/11 – 12/11): Kiểm soát chất lượng thực nghiệm

---

### ERR-003 – Thứ Tư, 11/11/2026 – 20:30
**Thực hiện:** TV1 (Haruki107206)
**Nhiệm vụ:** Chạy lại toàn bộ script thực nghiệm lần thứ 2 để kiểm tra khả năng tái lập.

**Vấn đề phát sinh – NGHIÊM TRỌNG:**
Sau khi chạy lại `python src/run_clustering_experiments.py`, kiểm tra file `experiment_log.csv`:
- File chỉ có **33 dòng** thay vì phải có **66 dòng** (33 lần chạy đầu + 33 lần chạy lại).
- Phát hiện script cũ sử dụng `df.to_csv(path, mode="w")` – **ghi đè hoàn toàn** lịch sử mỗi lần chạy.
- Toàn bộ metadata thực nghiệm (thời gian chạy, seed, cấu hình) của 33 lần chạy trước bị xóa.

**Mức độ tác hại:** Vi phạm nguyên tắc bất biến của nhật ký nghiên cứu khoa học – không thể truy nguyên kết quả.

**Hành động khắc phục (TV1 – hoàn thành 11/11 lúc 21:55, commit `1279a70`):**
1. Viết lại hoàn toàn hàm `append_experiment_log()`:
   - Đọc file log cũ trước khi ghi bất kỳ dòng nào.
   - Migrate các cột tên cũ (`Rows_After_Preprocessing` → `Sample_Rows_For_Clustering`).
   - Nối dòng mới vào cuối bảng cũ.
   - Ghi qua file tạm `.tmp` rồi thay thế nguyên tử (atomic replace) – không bao giờ mất dữ liệu giữa chừng.
2. Cấp `Run_ID = timestamp + UUID_8ký_tự` để phân biệt từng phiên chạy dù chạy cùng ngày.

**Kết quả:** Chạy lại thêm 2 lần – log tích lũy đúng, không mất dữ liệu.

---

### Thứ Tư, 12/11/2026 – 20:19 (commit `374a588`)
**Thực hiện:** TV1 (Haruki107206)
**Nhiệm vụ:** Xây dựng bộ công cụ kiểm tra chất lượng dữ liệu RFM và khóa mẫu cố định cho EXP-034.

**Hành động:**
- Viết `src/validate_rfm_data.py` với 10 tiêu chí kiểm định độc lập.
- Tạo file `outputs/tables/exp034_fixed_customer_sample.csv` chứa danh sách 2.000 `CustomerID` cố định – sẽ dùng xuyên suốt EXP-034, 035, 036.

**Kết quả:** Báo cáo kiểm định **PASS 10/10 tiêu chí**.

---

## TUẦN 2 (13/11): Thực nghiệm ngày 13/11 theo lịch

---

### Sáng, 13/11/2026 – 14:00 | Kiểm thử nền tảng 11/11 – 12/11
**Thực hiện:** TV1 (Dữ liệu)
**Hành động:**
- Chạy `python src/validate_rfm_data.py` → **PASS 10/10**.
- Rà soát toàn bộ 7 biểu đồ EDA và 3 bảng tóm tắt.
- Xác nhận dữ liệu khởi đầu cho EXP-034.

**Kết quả:** Biên bản kiểm thử `docs/Bao_cao_kiem_thu_11_12_11.md` phê duyệt 100%.

---

### ERR-004 – 13/11/2026 – 15:35 | Phát hiện Label Switching trong EXP-034
**Thực hiện:** TV2 (Trần Thiện Hùng)
**Nhiệm vụ:** So sánh hồ sơ cụm K-Means k=2 giữa seed 42 và seed 7.

**Vấn đề phát sinh:**
Viết code so sánh thô `sample[sample["cluster"] == 0]["Monetary"].median()` giữa 2 seed:
- seed 42: Cụm 0 → Monetary median = **411.75 GBP** (nhóm chi tiêu thấp)
- seed 7: Cụm 0 → Monetary median = **2.919.62 GBP** (nhóm chi tiêu cao!)

Nhóm ban đầu kết luận nhầm: *"K-Means không ổn định, thuật toán bị loạn với các seed khác nhau"*.

**Phân tích nguyên nhân thực sự:**
Đây là hiện tượng **Label Switching** – K-Means là thuật toán không giám sát, không có nhãn ground-truth. Tâm cụm khởi tạo ngẫu nhiên theo seed khác nhau dẫn đến Cụm 0 ở seed 7 chính là Cụm 1 ở seed 42 về mặt ngữ nghĩa, nhưng thuật toán không biết điều đó.

**Hành động khắc phục (TV2 – hoàn thành 13/11 lúc 16:06):**
1. Dùng **Adjusted Rand Index (ARI)** để đo độ tương đồng phân cụm – ARI không quan tâm đến thứ tự nhãn.
2. Viết hàm `align_labels_by_monetary(sample_df, raw_labels)`: sắp xếp lại nhãn tăng dần theo Monetary median của từng cụm → Cụm 0 luôn là "chi tiêu thấp", Cụm 1 luôn là "chi tiêu cao".

---

### 13/11/2026 – 16:06 | EXP-034 hoàn thành
**Thực hiện:** TV2 (chủ trì) + TV3 (tổng hợp)
**Run ID:** `20261113_160623_1e570559`

**Kết quả ma trận ARI (sau khi chuẩn hóa nhãn):**

| | seed 42 | seed 7 | seed 21 | seed 123 | seed 2026 |
|---|---|---|---|---|---|
| **seed 42** | 1.0000 | 0.9741 | **1.0000** | 0.9960 | 0.9960 |
| **seed 7** | 0.9741 | 1.0000 | 0.9741 | 0.9781 | 0.9781 |
| **seed 21** | **1.0000** | 0.9741 | 1.0000 | 0.9960 | 0.9960 |
| **seed 123** | 0.9960 | 0.9781 | 0.9960 | 1.0000 | **1.0000** |
| **seed 2026** | 0.9960 | 0.9781 | 0.9960 | **1.0000** | 1.0000 |

**Kết luận:** ARI nhỏ nhất = 0.9741 (rất gần 1.0) → K-Means k=2 **cực kỳ ổn định**. Hiện tượng Label Switching đã được xử lý hoàn toàn.

**Hồ sơ cụm sau chuẩn hóa nhãn (seed 42):**
- **Cụm 0** (1.162 khách – 58.1%): Recency trung vị 306 ngày, Frequency 2 đơn, Monetary 412 GBP → *Khách ít hoạt động/chi tiêu thấp*
- **Cụm 1** (838 khách – 41.9%): Recency trung vị 24 ngày, Frequency 8 đơn, Monetary 2.880 GBP → *Khách mua thường xuyên/chi tiêu cao*

**Đầu ra:** `exp034_seed_stability.csv`, `exp034_pairwise_ari.csv`, `outputs/figures/10_exp034_seed_stability.png`

---

### 13/11/2026 – 16:08 | Chuẩn hóa hệ thống nhật ký sang file Excel
**Thực hiện:** Phân tích & Quản lý

**Hành động:**
1. Tạo `logs/Daily_Journal.xlsx` – sổ nhật ký công việc hằng ngày (10 bản ghi từ commit đầu tiên 13/10 đến 13/11).
2. Cập nhật `logs/experiment_log.xlsx` với **7 sheets**:
   - `Experiment_Log`: 75 dòng (CL-001 đến CL-033 + EXP-034 × 5 seeds + ERR-001 đến ERR-004)
   - `Trial_and_Error_Log`: 4 bản ghi sai sót có cấu trúc rõ ràng
   - `Daily_Journal`: Nhật ký công việc hằng ngày
   - `Model_Comparison`, `Preprocessing_Summary`, `Cluster_Profiles_k2`, `RFM_Data_Validation`
3. Cập nhật `src/run_clustering_experiments.py` để **tự động đồng bộ** vào Excel sau mỗi lần chạy.

---



## EXP-034 — Độ ổn định theo seed: ARI, Silhouette và Inertia

Thí nghiệm giữ nguyên mẫu khách hàng 2.000 dòng, ba biến RFM, log1p + StandardScaler, K-Means k=2, `n_init=20`; chỉ đổi seed (42, 7, 21, 123, 2026). So sánh ARI trên nhãn của cùng khách hàng, xử lý việc đổi tên nhãn cụm (label switching) theo thứ tự trung vị Monetary.

- **ARI theo cặp:** 0.974137–0.995999. ARI gần 1 cho thấy hai lần chạy tạo cách phân nhóm gần như tương đồng; đây không phải accuracy.
- **Silhouette:** 0.297894–0.300278, biên độ 0.002384 (trung bình 0.298695).
- **Inertia:** 2855.72–2855.77, biên độ 0.05, tương đương 0.00175% so với trung bình.
- **Kích thước cụm:** seed 7 là 1.173/827; các seed còn lại nằm trong khoảng 1.160–1.162 và 838–840.

Seed khác nhau làm thay đổi centroid khởi tạo nên K-Means có thể hội tụ vào nghiệm cục bộ hơi khác. Silhouette biến động nhẹ vì độ tách biệt của cùng 1.000 điểm đánh giá thay đổi theo ranh giới cụm. Inertia là tổng bình phương khoảng cách đến centroid trên toàn mẫu huấn luyện; biên độ rất nhỏ cho thấy các nghiệm có độ khớp gần nhau. Chỉ so sánh Inertia khi cùng dữ liệu, đặc trưng, scaling và thuật toán.

**Nhận xét:** trên mẫu và pipeline cố định này, phân cụm k=2 ổn định cao qua năm seed. Kết luận chưa khái quát ra mẫu khác. Số liệu chi tiết tại `outputs/tables/exp034_seed_stability.csv` và `exp034_pairwise_ari.csv`; diễn giải đã được thêm vào sheet `EXP034_Interpretation` trong `logs/experiment_log.xlsx`.
