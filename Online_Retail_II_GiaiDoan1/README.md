# Online Retail II – Giai đoạn 1: Khám phá dữ liệu và RFM

## Mục tiêu của giai đoạn này

Đây là phần khởi đầu của đồ án Machine Learning **“Phân khúc khách hàng bằng RFM và hành vi mua hàng”**. Notebook tập trung vào:

1. Đọc dữ liệu giao dịch gốc từ UCI Machine Learning Repository.
2. Kiểm tra cấu trúc, kiểu dữ liệu, giá trị thiếu, dữ liệu trùng, hóa đơn hủy và giao dịch bất thường.
3. Trực quan hóa một số đặc điểm giao dịch.
4. Nêu rõ quy tắc lọc dữ liệu phục vụ phân tích hành vi mua hàng.
5. Tạo bảng RFM ở mức khách hàng và lưu bảng này để sử dụng ở giai đoạn phân cụm.

### Đầu ra của giai đoạn 1

- Bảng tóm tắt EDA: `outputs/tables/eda_summary.csv`
- Bảng quy tắc tiền xử lý: `outputs/tables/preprocessing_summary.csv`
- Bảng giá trị thiếu: `outputs/tables/missing_values_summary.csv`
- Bảng khách hàng RFM: `outputs/tables/rfm_table.csv`
- Biểu đồ gốc: `outputs/figures/`

### Báo cáo giữa kì hiện có hai phần triển khai:

1. Notebook 01: EDA, quy tắc làm sạch, tính RFM và lưu đầu ra.
2. Notebook 02: tiền xử lý RFM, baseline K-Means, so sánh K-Means/Hierarchical/DBSCAN, chọn cấu hình theo silhouette và diễn giải hồ sơ cụm.

### Đầu ra Notebook 01

- `outputs/figures/01_missing_values.png` — tỷ lệ dữ liệu thiếu.
- `outputs/figures/02_raw_rows_by_month.png` — số dòng giao dịch theo tháng trước lọc.
- `outputs/figures/03_top_countries_by_rows.png` — 10 quốc gia có nhiều dòng giao dịch nhất.
- `outputs/figures/04_monthly_revenue_cleaned.png` — doanh thu theo tháng sau lọc.
- `outputs/figures/05_top_countries_by_revenue.png` — 10 quốc gia có doanh thu cao nhất.
- `outputs/figures/06_rfm_distributions.png` — phân phối Recency, Frequency và Monetary.
- `outputs/figures/07_rfm_correlation.png` — tương quan giữa ba đặc trưng RFM.

### Đầu ra Notebook 02

- `outputs/tables/clustering_preprocessing.csv`: thống kê quy trình log và scaling.
- `outputs/tables/clustering_model_comparison.csv`: metric, số cụm, noise và cấu hình từng mô hình.
- `outputs/tables/selected_clustering_model.csv`: quy tắc và cấu hình được chọn.
- `outputs/tables/customer_clusters_sample.csv`: nhãn cụm trên mẫu đánh giá cố định.
- `outputs/tables/selected_model_cluster_profiles.csv`: hồ sơ RFM theo cụm.
- `outputs/tables/exp036_all_algorithms_multi_metrics.csv`: Silhouette, Davies–Bouldin, Calinski–Harabasz và noise của các thuật toán trong EXP-036.
- `outputs/tables/model_decision_exp034_exp036.csv`: bảng quyết định và đánh đổi giữa các ứng viên EXP-034–EXP-036.
- `outputs/tables/selected_model_customer_labels.csv`: nhãn khách hàng theo cấu hình chốt.
- `outputs/tables/cluster_interpretation.csv` và `.md`: so sánh trung vị từng cụm với trung vị mẫu để hỗ trợ diễn giải.
- `outputs/figures/08_selected_cluster_rfm_profiles.png`, `09_clustering_silhouette_comparison.png`.
- `logs/experiment_log.xlsx`: nhật ký thực nghiệm dạng workbook; `logs/experiment_log.csv` là bản ghi chi tiết dạng CSV.
- `logs/Daily_Journal.xlsx`: nhật ký công việc hằng ngày.


## Nguồn dữ liệu

- Dataset: [Online Retail II – UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/502/online+retail+ii)
- Tác giả: Daqing Chen.
- DOI: https://doi.org/10.24432/C5CG6D
- Giấy phép: CC BY 4.0; khi sử dụng cần ghi công nguồn dữ liệu.
- Dữ liệu giao dịch của một nhà bán lẻ trực tuyến tại Anh, từ 01/12/2009 đến 09/12/2011 theo mô tả của UCI.


## Cài đặt và chạy lại từ đầu

- Mở thư mục `Online_Retail_II_GiaiDoan1` trong VS Code. Trong Terminal, cài thư viện vào đúng Python interpreter sẽ chọn làm Jupyter kernel:

```powershell
python -m pip install -r requirements.txt
```

- Chọn kernel Python có các thư viện trên, sau đó chạy lần lượt **Run All** cho `01_Kham_pha_du_lieu_va_RFM.ipynb` và `02_Thuc_nghiem_phan_cum.ipynb`. 

- Có thể chạy riêng thực nghiệm từ Terminal tại thư mục dự án:

```powershell
python src/run_clustering_experiments.py
```

Lệnh riêng này cần `outputs/tables/rfm_table.csv`, do đó phải chạy Notebook 01 trước. Nếu dùng `py` launcher hoặc đường dẫn Python cụ thể, thay `python` bằng interpreter đã cài requirements.

## Thực nghiệm phân cụm hiện có

EXP-036 đánh giá K-Means, Ward và lưới DBSCAN trên cùng mẫu fit cố định tối đa 2.000 khách hàng. Silhouette, Davies–Bouldin và Calinski–Harabasz tính trên cùng 1.000 khách đánh giá; DBSCAN loại noise khỏi các metric nhưng báo riêng số/tỷ lệ noise trên sample fit. Kết hợp EXP-035 (so sánh scaler cùng sample/k/seed) và kiểm tra độ ổn định 5 seed, cấu hình hiện được chọn là K-Means `k=2`, `log1p` + `RobustScaler`, `n_init=20`, `random_state=42`. Các giá trị metric cuối được lưu ở `outputs/tables/selected_clustering_model.csv`; đây là đánh giá nội tại trên mẫu, chưa phải đánh giá có nhãn chuẩn hay xác nhận trên toàn bộ khách hàng. Xem `docs/Danh_gia_mo_hinh_EXP034_EXP036.md` và `outputs/tables/model_decision_exp034_exp036.csv` để biết quy trình, đánh đổi và giới hạn.

Để tính lại các metric đa thuật toán và cập nhật cấu hình/nhãn được chọn sau khi đã chạy Notebook 01, dùng:

```powershell
python src/run_clustering_experiments.py
```

Script chạy lượt so sánh K-Means/Ward/DBSCAN, làm mới lượt K-Means đa chỉ số của EXP-036, gọi `src/complete_model_evaluation.py` để tái lập bảng quyết định/kiểm tra độ ổn định RobustScaler/cập nhật hồ sơ cụm cuối, rồi đồng bộ hai workbook nhật ký. Các sheet sẵn có trong workbook được giữ lại khi ghi log.

## EXP-037 và demo phân khúc

Từ thư mục dự án, với bảng RFM đã có:

~~~powershell
python -m pip install -r requirements.txt
python src/run_exp037.py
python -X utf8 src/validate_exp037_customer_counts.py
python -m streamlit run app.py
~~~

EXP-037 tạo bảng nhãn toàn bộ, hồ sơ cụm và cấu hình trong outputs/tables,
biểu đồ PCA trong outputs/figures và pipeline trong models.
Demo nhận RFM gốc và áp dụng log1p, RobustScaler rồi K-Means.
