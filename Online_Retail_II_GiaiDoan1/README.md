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
- `outputs/tables/cluster_interpretation.csv` và `.md`: so sánh trung vị từng cụm với trung vị mẫu để hỗ trợ diễn giải.
- `outputs/figures/08_selected_cluster_rfm_profiles.png`, `09_clustering_silhouette_comparison.png`.
- `logs/experiment_log.csv`: nhật ký cấu hình và kết quả các lần chạy.


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

Lần chạy đã lưu đánh giá 33 cấu hình trên mẫu cố định 2.000 khách hàng (seed 42), với Silhouette tính trên cùng 1.000 khách hàng. Theo quy tắc lựa chọn trong Notebook 02, cấu hình đứng đầu là K-Means `k=2`, Silhouette `0.4246`, tỷ lệ nhiễu 0%. Hai cụm có lần lượt 1.162 và 838 khách hàng trong mẫu. Đây là kết quả khám phá; cần kiểm tra độ ổn định qua nhiều seed/bootstrap trước khi kết luận mô hình cuối.
