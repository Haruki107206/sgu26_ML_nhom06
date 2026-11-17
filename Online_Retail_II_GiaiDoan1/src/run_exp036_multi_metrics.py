# -*- coding: utf-8 -*-
"""EXP-036 – Đánh giá đa chỉ số cho K‑Means (k=2..8) trên mẫu cố định 2.000 khách.

Công việc:
- Đọc `exp034_fixed_customer_sample.csv` (2 000 khách).
- Áp dụng `log1p` lên các đặc trưng R, F, M.
- Chuẩn hoá bằng `StandardScaler` (đã chứng minh ổn định).
- Với mỗi k ∈ {2,…,8} chạy K‑Means (n_init=20, seed=42).
- Tính các chỉ số: Silhouette, Davies‑Bouldin, Calinski‑Harabasz, Inertia.
- Ghi kết quả vào `outputs/tables/exp036_multi_metrics.csv` và vẽ:
  * Đồ thị Elbow (Inertia) cho k=2..8.
  * Đồ thị Silhouette cho mỗi k.
- Ghi lại bản ghi chi tiết vào `logs/experiment_log.csv` (và đồng bộ sang XLSX).
- Tạo file `exp036_cluster_profiles.csv` mô tả trung vị & tổng Monetary cho mỗi cụm.
"""

from __future__ import annotations

import json
import time
import uuid
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import (
    adjusted_rand_score,
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "outputs" / "tables"
FIGURES = ROOT / "outputs" / "figures"
LOG_CSV = ROOT / "logs" / "experiment_log.csv"
LOG_XLSX = ROOT / "logs" / "experiment_log.xlsx"
FEATURES = ["Recency", "Frequency", "Monetary"]
SEED = 42
N_INIT = 20
K_RANGE = range(2, 9)  # 2‑8
EVALUATION_SIZE = 1000


def append_log(rows: list[dict]) -> None:
    """Atomic append of EXP‑036 rows to CSV (preserve history)."""
    LOG_CSV.parent.mkdir(parents=True, exist_ok=True)
    if LOG_CSV.exists():
        previous = pd.read_csv(LOG_CSV)
    else:
        previous = pd.DataFrame()
    combined = pd.concat([previous, pd.DataFrame(rows)], ignore_index=True, sort=False)
    tmp = LOG_CSV.with_name(f"{LOG_CSV.stem}.tmp{LOG_CSV.suffix}")
    combined.to_csv(tmp, index=False, encoding="utf-8-sig")
    tmp.replace(LOG_CSV)


def sync_to_xlsx(df: pd.DataFrame, sheet: str) -> None:
    """Append a DataFrame to experiment_log.xlsx (create sheet or replace)."""
    if not LOG_XLSX.exists():
        print(f"[CẢNH BÁO] {LOG_XLSX} không tồn tại, bỏ qua đồng bộ XLSX.")
        return
    try:
        with pd.ExcelWriter(LOG_XLSX, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            df.to_excel(writer, sheet_name=sheet, index=False)
        print(f"Đã đồng bộ {sheet} vào {LOG_XLSX}")
    except Exception as exc:
        print(f"[CẢNH BÁO] Ghi XLSX thất bại: {exc}")


def main() -> None:
    run_started = datetime.now().astimezone()
    run_id = f"{run_started.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

    rfm_path = TABLES / "rfm_table.csv"
    ids_path = TABLES / "exp034_fixed_customer_sample.csv"
    if not rfm_path.is_file() or not ids_path.is_file():
        raise FileNotFoundError("Cần rfm_table.csv và exp034_fixed_customer_sample.csv cho EXP‑036")

    rfm = pd.read_csv(rfm_path)
    ids = pd.read_csv(ids_path)["CustomerID"]
    sample = ids.to_frame().merge(rfm, on="CustomerID", how="left", validate="one_to_one")

    # Kiểm tra dữ liệu mẫu
    if sample[FEATURES].isna().any().any():
        raise ValueError("Có giá trị RFM missing trong mẫu cố định.")
    if (sample[FEATURES] < 0).any().any():
        raise ValueError("Giá trị RFM phải >= 0 trước log1p.")

    # Log‑transform
    log_feat = np.log1p(sample[FEATURES].astype(float))
    scaler = StandardScaler()
    scaled = scaler.fit_transform(log_feat)
    eval_n = min(EVALUATION_SIZE, len(sample))
    scaled_eval = scaled[:eval_n]

    # Lưu diagnostics về scaling
    diag_rows = []
    for i, f in enumerate(FEATURES):
        diag_rows.append({
            "experiment_id": "EXP-036",
            "feature": f,
            "mean_after_scaling": float(np.mean(scaled[:, i])),
            "var_after_scaling": float(np.var(scaled[:, i], ddof=0)),
            "std_after_scaling": float(np.std(scaled[:, i], ddof=0)),
            "sample_n": len(sample),
        })
    pd.DataFrame(diag_rows).to_csv(TABLES / "exp036_scaling_diagnostics.csv", index=False, encoding="utf-8-sig")

    metrics: list[dict] = []
    profiles: list[pd.DataFrame] = []
    inertia_vals = []
    silhouette_vals = []
    for k in K_RANGE:
        km = KMeans(n_clusters=k, init="k-means++", n_init=N_INIT, random_state=SEED)
        start = time.perf_counter()
        labels = km.fit_predict(scaled)
        elapsed = time.perf_counter() - start
        inertia_vals.append(km.inertia_)
        try:
            sil = silhouette_score(scaled_eval, labels[:eval_n])
        except Exception:
            sil = np.nan
        silhouette_vals.append(sil)

        row = {
            "experiment_id": "EXP-036",
            "algorithm": "KMeans",
            "k": k,
            "silhouette": float(sil),
            "davies_bouldin": float(davies_bouldin_score(scaled_eval, labels[:eval_n])),
            "calinski_harabasz": float(calinski_harabasz_score(scaled_eval, labels[:eval_n])),
            "sample_n": len(sample),
            "evaluation_sample_n": eval_n,
            "inertia": float(km.inertia_),
            "runtime_seconds": round(elapsed, 4),
            "cluster_sizes": json.dumps({str(c): int(n) for c, n in pd.Series(labels).value_counts().sort_index().items()}),
            "status": "valid",
            "evaluation_note": "Ba metric tính trên cùng 1.000 khách hàng đầu; mô hình fit trên mẫu 2.000 khách. Inertia fit trên toàn bộ mẫu.",
            "error": "",
        }
        metrics.append(row)

        profile = sample.assign(cluster=labels).groupby("cluster").agg(
            customers=("CustomerID", "nunique"),
            Recency_median=("Recency", "median"),
            Frequency_median=("Frequency", "median"),
            Monetary_median=("Monetary", "median"),
            Monetary_sum=("Monetary", "sum"),
        ).reset_index()
        profile.insert(0, "k", k)
        profiles.append(profile)

    # Lưu kết quả
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(metrics).to_csv(TABLES / "exp036_multi_metrics.csv", index=False, encoding="utf-8-sig")
    pd.concat(profiles, ignore_index=True).to_csv(TABLES / "exp036_cluster_profiles.csv", index=False, encoding="utf-8-sig")

    # Vẽ Elbow
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(list(K_RANGE), inertia_vals, marker='o')
    ax.set_xlabel('k (số cụm)')
    ax.set_ylabel('Inertia')
    ax.set_title('EXP‑036 – Đồ thị Elbow (Inertia)')
    fig.tight_layout()
    fig.savefig(FIGURES / "12_exp036_elbow.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    # Vẽ Silhouette
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    ax2.plot(list(K_RANGE), silhouette_vals, marker='o', color='steelblue')
    ax2.set_xlabel('k (số cụm)')
    ax2.set_ylabel('Silhouette Score')
    ax2.set_title('EXP‑036 – Silhouette cho các k')
    ax2.set_ylim(0, 1)
    fig2.tight_layout()
    fig2.savefig(FIGURES / "12b_exp036_silhouette.png", dpi=160, bbox_inches="tight")
    plt.close(fig2)

    # Ghi log CSV
    rfm_rows = len(rfm)
    log_rows = []
    for row in metrics:
        log_rows.append({
            "Run_ID": run_id,
            "Experiment_ID": "EXP-036",
            "Run_Started_At": run_started.isoformat(timespec="seconds"),
            "Date": run_started.date().isoformat(),
            "Research_Question": "Đánh giá đa chỉ số (Silhouette, DBI, CHI trên 1.000 điểm chung; Inertia trên mẫu fit 2.000 khách) cho K‑Means.",
            "Dataset_Version": "Online Retail II; outputs/tables/rfm_table.csv",
            "RFM_Rows_Before_DropNA": rfm_rows,
            "Sample_Rows": len(sample),
            "Unique_Customers_Sampled": int(sample["CustomerID"].nunique()),
            "Evaluation_Rows_For_Silhouette": int(row["evaluation_sample_n"]),
            "Unique_Customers_Evaluated": int(sample.iloc[:int(row["evaluation_sample_n"])]["CustomerID"].nunique()),
            "Feature_Set": ", ".join(FEATURES),
            "Algorithm": "KMeans",
            "Hyperparameters": f"n_clusters={row['k']}; init=k-means++; n_init={N_INIT}; random_state={SEED}",
            "Scaling": "log1p + StandardScaler",
            "Metric_Name": "Silhouette/DBI/CHI trên sample đánh giá chung; Inertia trên sample fit",
            "Metric_Value": row["silhouette"],
            "Random_State": SEED,
            "Observation": f"status={row['status']}; eval_n={row['evaluation_sample_n']}; inertia={row['inertia']:.2f}; DBI={row['davies_bouldin']:.3f}; CHI={row['calinski_harabasz']:.2f}",
            "Next_Action": "So sánh các k, chọn k tối ưu (cân nhắc Silhouette, DBI, CHI, tính thực tiễn).",
        })
    append_log(log_rows)
    sync_to_xlsx(pd.DataFrame(metrics), sheet="EXP036_Multi_Metrics")
    sync_to_xlsx(pd.DataFrame(diag_rows), sheet="EXP036_Scaling_Diagnostics")

    print("✅ EXP‑036 hoàn thành. Run_ID:", run_id)
    print("   K đã thử:", list(K_RANGE))
    print("   Các file đã lưu:")
    print("   -", TABLES / "exp036_multi_metrics.csv")
    print("   -", TABLES / "exp036_cluster_profiles.csv")
    print("   -", FIGURES / "12_exp036_elbow.png")
    print("   -", FIGURES / "12b_exp036_silhouette.png")


if __name__ == "__main__":
    main()
