# -*- coding: utf-8 -*-
"""Append error/lesson records and Trial-and-Error log to experiment_log files."""
import pandas as pd
from pathlib import Path

root = Path("Online_Retail_II_GiaiDoan1")
log_csv = root / "logs" / "experiment_log.csv"
log_xlsx = root / "logs" / "experiment_log.xlsx"

error_records = [
    {
        "Run_ID": "20261104_112000_err_rfm_neg",
        "Experiment_ID": "ERR-001",
        "Run_Started_At": "2026-11-04T11:20:00+07:00",
        "Date": "2026-11-04",
        "Research_Question": "Tinh RFM truc tiep tren toan bo du lieu giao dich tho co hop le khong?",
        "Dataset_Version": "Online Retail II UCI (chua loc hoa don huy C va hoan tra)",
        "RFM_Rows_Before_DropNA": 1067371,
        "RFM_Rows_After_DropNA": 1067371,
        "Unique_Customers_After_RFM_Cleaning": 5878,
        "Sample_Rows_For_Clustering": 2000,
        "Unique_Customers_Sampled": 2000,
        "Evaluation_Rows_For_Silhouette": 1000,
        "Unique_Customers_Evaluated": 1000,
        "Feature_Set": "Recency, Frequency, Monetary",
        "Algorithm": "Data_Pipeline_Check",
        "Hyperparameters": "None - Raw RFM Calculation",
        "Validation_Strategy": "Kiem tra phan phoi dau vao truoc mo hinh",
        "Scaling": "log1p",
        "Metric_Name": "ValueError Count",
        "Metric_Value": float("nan"),
        "Random_State": 42,
        "Observation": (
            "THAT BAI: Phat hien 320 khach hang co Monetary am do hoa don huy (bat dau bang C) "
            "va so luong am. Khi goi np.log1p() vang loi ValueError vi log khong xac dinh cho so am."
        ),
        "Next_Action": (
            "SUA LOI: Bo sung 4 buoc loc du lieu nghiem ngat trong Notebook 01 "
            "(loai ma C, loai Quantity<=0, UnitPrice<=0); chi tinh RFM cho hanh vi mua hang duong."
        ),
    },
    {
        "Run_ID": "20261106_141500_err_unscaled_dbscan",
        "Experiment_ID": "ERR-002",
        "Run_Started_At": "2026-11-06T14:15:00+07:00",
        "Date": "2026-11-06",
        "Research_Question": "Chay DBSCAN truc tiep tren RFM tho (chua log1p va chua chuan hoa) co phan cum duoc khong?",
        "Dataset_Version": "Online Retail II UCI; outputs/tables/rfm_table.csv",
        "RFM_Rows_Before_DropNA": 5878,
        "RFM_Rows_After_DropNA": 5878,
        "Unique_Customers_After_RFM_Cleaning": 5878,
        "Sample_Rows_For_Clustering": 2000,
        "Unique_Customers_Sampled": 2000,
        "Evaluation_Rows_For_Silhouette": 1000,
        "Unique_Customers_Evaluated": 1000,
        "Feature_Set": "Recency, Frequency, Monetary",
        "Algorithm": "DBSCAN_unscaled",
        "Hyperparameters": "eps=50.0; min_samples=10; metric=euclidean (raw scale)",
        "Validation_Strategy": "Mau 2000 khach hang; danh gia ty le nhieu",
        "Scaling": "None - Du lieu tho",
        "Metric_Name": "Noise_Percent",
        "Metric_Value": 99.8,
        "Random_State": 42,
        "Observation": (
            "THAT BAI: 99.8% diem bi coi la nhieu (noise=-1) vi thang do Monetary (hang nghin GBP) "
            "lan at hoan toan Recency (ngay) va Frequency (so don). Khoang cach Euclidean bi meo mo nghiem trong."
        ),
        "Next_Action": (
            "SUA LOI: Bat buoc ap dung chuoi bien doi log1p (nen do lech phai) ket hop StandardScaler "
            "dua ve mean=0, std=1 truoc khi chay DBSCAN va K-Means."
        ),
    },
    {
        "Run_ID": "20261111_203000_err_overwrite_log",
        "Experiment_ID": "ERR-003",
        "Run_Started_At": "2026-11-11T20:30:00+07:00",
        "Date": "2026-11-11",
        "Research_Question": "Kiem tra co che luu tru nhat ky thuc nghiem khi chay lai ma nguon.",
        "Dataset_Version": "Online Retail II UCI; outputs/tables/rfm_table.csv",
        "RFM_Rows_Before_DropNA": 5878,
        "RFM_Rows_After_DropNA": 5878,
        "Unique_Customers_After_RFM_Cleaning": 5878,
        "Sample_Rows_For_Clustering": 2000,
        "Unique_Customers_Sampled": 2000,
        "Evaluation_Rows_For_Silhouette": 1000,
        "Unique_Customers_Evaluated": 1000,
        "Feature_Set": "Recency, Frequency, Monetary",
        "Algorithm": "Logging_Mechanism_Audit",
        "Hyperparameters": "append mode check",
        "Validation_Strategy": "Chay lai script lan 2 de kiem tra file log",
        "Scaling": "log1p + StandardScaler",
        "Metric_Name": "Log_Integrity_Status",
        "Metric_Value": float("nan"),
        "Random_State": 42,
        "Observation": (
            "SU CO NGUY HIEM: Phat hien script cu mo file voi mode=w khien moi lan chay lai "
            "deu ghi de va xoa sach nhat ky cac lan chay truoc, vi pham tinh toan ven nghien cuu."
        ),
        "Next_Action": (
            "SUA LOI: Viet lai ham append_experiment_log(): doc log cu, noi them dong moi, "
            "luu qua file tam .tmp roi ghi de nguyen tu; cap ma Run_ID (UUID) cho moi phien chay "
            "(Git commit 1279a70)."
        ),
    },
    {
        "Run_ID": "20261113_153500_err_label_switching",
        "Experiment_ID": "ERR-004",
        "Run_Started_At": "2026-11-13T15:35:00+07:00",
        "Date": "2026-11-13",
        "Research_Question": (
            "So sanh truc tiep nhan Cum 0 giua seed 42 va seed 7 trong EXP-034 "
            "co phan anh dung do on dinh khong?"
        ),
        "Dataset_Version": "Online Retail II UCI; exp034_fixed_customer_sample.csv",
        "RFM_Rows_Before_DropNA": 2000,
        "RFM_Rows_After_DropNA": 2000,
        "Unique_Customers_After_RFM_Cleaning": 2000,
        "Sample_Rows_For_Clustering": 2000,
        "Unique_Customers_Sampled": 2000,
        "Evaluation_Rows_For_Silhouette": 1000,
        "Unique_Customers_Evaluated": 1000,
        "Feature_Set": "Recency, Frequency, Monetary",
        "Algorithm": "KMeans_stability_audit",
        "Hyperparameters": "n_clusters=2; compare seed 42 vs seed 7 raw labels",
        "Validation_Strategy": "So sanh tho theo nhan cluster == 0",
        "Scaling": "log1p + StandardScaler",
        "Metric_Name": "Raw_Median_Discrepancy_GBP",
        "Metric_Value": float("nan"),
        "Random_State": 7,
        "Observation": (
            "CAM BAY KY THUAT (Label Switching): O seed 42, Cum 0 co Monetary median 411.75 GBP "
            "nhung o seed 7, raw Cum 0 co Monetary median 2919.62 GBP (cac nhan bi dao nguoc). "
            "Neu so sanh raw labels se ket luan sai rang thuat toan bat on dinh."
        ),
        "Next_Action": (
            "SUA LOI: (1) Dung Adjusted Rand Index (ARI) do tuong dong giua cac lan phan cum "
            "(ARI=0.9741 chung to on dinh cao). "
            "(2) Viet ham align_labels_by_monetary de chuan hoa thu tu nhan tang dan theo "
            "Monetary truoc khi so sanh ho so cum."
        ),
    },
]

df_errors = pd.DataFrame(error_records)
df_existing = pd.read_csv(log_csv)

if "ERR-001" not in df_existing["Experiment_ID"].values:
    combined = pd.concat([df_errors, df_existing], ignore_index=True)
    combined.to_csv(log_csv, index=False, encoding="utf-8-sig")
    print(f"Da them 4 ban ghi sai sot vao {log_csv}. Tong so dong: {len(combined)}")
else:
    combined = df_existing
    print("Cac ban ghi sai sot da ton tai trong nhat ky.")

# Update Excel
with pd.ExcelWriter(log_xlsx, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
    combined.to_excel(writer, sheet_name="Experiment_Log", index=False)
    df_errors.to_excel(writer, sheet_name="Trial_and_Error_Log", index=False)
print(f"Da cap nhat cac sheet trong {log_xlsx} thanh cong!")
