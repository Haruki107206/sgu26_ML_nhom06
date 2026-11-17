# Chương 3. Dữ liệu, khám phá và tiền xử lý


## 3.1. Nguồn và phạm vi dữ liệu

Đồ án sử dụng bộ dữ liệu Online Retail II, ghi nhận giao dịch của một nhà bán lẻ trực tuyến tại Vương quốc Anh trong giai đoạn 01/12/2009–09/12/2011. Bảng tổng hợp tiền xử lý lưu trong repository có 1.067.371 dòng và 8 cột ban đầu. Đơn vị quan sát của phân tích RFM và phân cụm là khách hàng. `CustomerID` dùng để nhận diện, đếm và ghép kết quả; không đưa vào khoảng cách của mô hình.

## 3.2. Khám phá và làm sạch dữ liệu

Các bước làm sạch được áp dụng tuần tự:

| Bước | Dòng bị loại | Dòng còn lại |
|---|---:|---:|
| Dữ liệu gốc | 0 | 1.067.371 |
| Loại bản ghi trùng hoàn toàn | 34.335 | 1.033.036 |
| Loại dòng thiếu `CustomerID` | 235.151 | 797.885 |
| Loại hóa đơn hủy có mã bắt đầu bằng `C` | 18.390 | 779.495 |
| Loại `Quantity <= 0`, `UnitPrice <= 0` hoặc ngày không hợp lệ | 70 | 779.425 |

Sau làm sạch còn 779.425 dòng giao dịch, 36.969 hóa đơn và 5.878 khách hàng. Thời gian giao dịch hợp lệ trải từ 01/12/2009 07:45 đến 09/12/2011 12:50. Tổng doanh thu của dữ liệu sạch là £17.374.804,268. Các số liệu được lấy từ `outputs/tables/preprocessing_summary.csv` và `outputs/tables/eda_summary.csv`; dữ liệu giao dịch gốc không nằm trong bản repo hiện tại.

## 3.3. Tạo đặc trưng RFM

Mỗi dòng trong `outputs/tables/rfm_table.csv` đại diện cho một khách hàng. Ngày tham chiếu là 10/12/2011, tức ngày sau ngày giao dịch cuối cùng.

| Đặc trưng | Định nghĩa |
|---|---|
| Recency | Số ngày từ lần mua gần nhất đến ngày tham chiếu; giá trị nhỏ hơn thể hiện lần mua gần hơn. |
| Frequency | Số hóa đơn khác nhau của khách trong giai đoạn dữ liệu. |
| Monetary | Tổng `Quantity × UnitPrice` của khách, đơn vị GBP. |

Bảng RFM hiện có 5.878 dòng và mã khách duy nhất. Các kiểm tra trong `outputs/tables/rfm_validation_report.csv` đều PASS: không thiếu hoặc trùng mã khách; giá trị số hữu hạn; RFM không âm; Frequency là số nguyên dương; Monetary dương.

| Đặc trưng | Trung vị | Trung bình |
|---|---:|---:|
| Recency (ngày) | 96 | 201,87 |
| Frequency (hóa đơn) | 3 | 6,29 |
| Monetary (GBP) | 867,74 | 2.955,90 |

Frequency và Monetary có phân phối lệch phải. Pipeline phân cụm áp dụng `log1p` lên ba biến RFM, sau đó chuẩn hóa trước khi tính khoảng cách.

## 3.4. Đầu vào và quy tắc chọn mô hình

Đầu vào mô hình gồm `Recency`, `Frequency`, `Monetary`; `CustomerID` chỉ phục vụ đối chiếu. Các thí nghiệm hiện lưu dùng mẫu cố định 2.000 khách hàng, lấy không hoàn lại với seed 42. Quy tắc chọn là ưu tiên Silhouette cao nhất trong các cấu hình có 2–8 cụm và tỷ lệ nhiễu không quá 20%.

Kết quả đang được chọn là K-Means k=2, `init=k-means++`, `n_init=20`, `random_state=42`, tiền xử lý `log1p` và RobustScaler. Silhouette đạt 0,430303; Davies–Bouldin đạt 0,875147; Calinski–Harabasz đạt 1.058,491; tỷ lệ nhiễu bằng 0%. So sánh EXP-035 cho thấy RobustScaler tốt hơn StandardScaler một mức nhỏ trên cùng k=2 và cùng mẫu. Kiểm tra EXP-034 ghi nhận ARI nhỏ nhất giữa các seed là 0,9741.

Các chỉ số này được tính trong thí nghiệm trên mẫu: mô hình được fit với 2.000 khách, các metric EXP-035/036 được đánh giá trên 1.000 khách dùng chung. Vì vậy, không diễn giải chúng như hiệu năng đã xác nhận trên toàn bộ 5.878 khách.

## 3.5. Giới hạn và phần cần hoàn tất

Hiện `outputs/tables/selected_model_customer_labels.csv` có nhãn cho mẫu 2.000 khách. Chưa có `outputs/tables/customer_clusters_full.csv` và `outputs/tables/final_cluster_profiles.csv` của EXP-037, nên chưa thể kết luận số khách từng cụm sau khi áp dụng mô hình lên toàn bộ RFM. Khi TV3 hoàn tất EXP-037, kiểm tra bằng:

```powershell
python src/validate_exp037_customer_counts.py
```

Sau đó cập nhật kích thước cụm và hồ sơ cụm toàn bộ vào phần báo cáo cuối.

## Tệp tham chiếu

- `outputs/tables/eda_summary.csv`
- `outputs/tables/preprocessing_summary.csv`
- `outputs/tables/rfm_table.csv`
- `outputs/tables/rfm_validation_report.csv`
- `outputs/tables/selected_clustering_model.csv`
- `outputs/tables/exp035_scaling_comparison.csv`
- `outputs/tables/exp036_multi_metrics.csv`
- `outputs/tables/exp034_seed_stability.csv`
- `outputs/tables/selected_model_customer_labels.csv`
- `01_Kham_pha_du_lieu_va_RFM.ipynb`
- `02_Thuc_nghiem_phan_cum.ipynb`
