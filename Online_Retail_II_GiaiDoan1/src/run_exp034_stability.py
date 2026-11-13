"""EXP-034: Run K-Means seed stability experiment and handle label switching.

Evaluates K-Means k=2 across 5 random seeds on the fixed 2,000 customer sample.
Measures stability using Adjusted Rand Index (ARI), Silhouette, Inertia, and cluster sizes.
Handles cluster label switching by ordering clusters by Monetary median.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
import uuid

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "outputs" / "tables"
FIGURES = ROOT / "outputs" / "figures"
LOG_CSV = ROOT / "logs" / "experiment_log.csv"
LOG_XLSX = ROOT / "logs" / "experiment_log.xlsx"
RFM_FILE = TABLES / "rfm_table.csv"
SAMPLE_FILE = TABLES / "exp034_fixed_customer_sample.csv"
FEATURES = ["Recency", "Frequency", "Monetary"]
SEEDS = [42, 7, 21, 123, 2026]
EVAL_N = 1000


def align_labels_by_monetary(sample_df: pd.DataFrame, raw_labels: np.ndarray) -> np.ndarray:
    """Normalize cluster labels so cluster 0 has lower median Monetary than cluster 1.
    
    This eliminates artificial differences caused by random centroid initialization (Label Switching).
    """
    temp_df = sample_df.copy()
    temp_df["raw_cluster"] = raw_labels
    medians = temp_df.groupby("raw_cluster")["Monetary"].median().sort_values()
    # Map raw cluster ID to rank (0 = lowest median monetary, 1 = highest)
    label_map = {raw_id: new_id for new_id, raw_id in enumerate(medians.index)}
    return np.array([label_map[c] for c in raw_labels])


def run_exp034():
    run_started_at = datetime.now().astimezone()
    run_id = f"{run_started_at.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

    print(f"=== BẮT ĐẦU EXP-034: KIỂM TRA ĐỘ ỔN ĐỊNH K-MEANS (5 SEEDS) ===")
    print(f"Thời gian: {run_started_at.isoformat()}")
    print(f"Run ID: {run_id}")

    if not RFM_FILE.exists():
        raise FileNotFoundError(f"Không tìm thấy {RFM_FILE}")
    if not SAMPLE_FILE.exists():
        raise FileNotFoundError(f"Không tìm thấy {SAMPLE_FILE}")

    rfm_df = pd.read_csv(RFM_FILE)
    sample_ids = pd.read_csv(SAMPLE_FILE)["CustomerID"].tolist()
    
    # Filter exact 2,000 customers in sample order
    sample_df = rfm_df[rfm_df["CustomerID"].isin(sample_ids)].copy()
    sample_df = sample_df.drop_duplicates(subset=["CustomerID"]).reset_index(drop=True)
    sample_n = len(sample_df)
    print(f"Đã nạp mẫu cố định: {sample_n} khách hàng")

    # Log1p and StandardScale
    transformed = np.log1p(sample_df[FEATURES].astype(float))
    scaler = StandardScaler()
    X = scaler.fit_transform(transformed)
    X_eval = X[:EVAL_N]

    seed_results = []
    labels_dict = {}
    aligned_labels_dict = {}
    profiles_list = []

    for seed in SEEDS:
        model = KMeans(n_clusters=2, init="k-means++", n_init=20, random_state=seed)
        raw_labels = model.fit_predict(X)
        labels_dict[seed] = raw_labels

        # Detect label switching
        c0_median_raw = sample_df.loc[raw_labels == 0, "Monetary"].median()
        c1_median_raw = sample_df.loc[raw_labels == 1, "Monetary"].median()
        is_switched = (c0_median_raw > c1_median_raw)

        # Standardize labels
        aligned_labels = align_labels_by_monetary(sample_df, raw_labels)
        aligned_labels_dict[seed] = aligned_labels

        # Silhouette on fixed first EVAL_N samples
        eval_labels = raw_labels[:EVAL_N]
        sil = silhouette_score(X_eval, eval_labels)
        inertia = float(model.inertia_)

        c0_size = int(np.sum(aligned_labels == 0))
        c1_size = int(np.sum(aligned_labels == 1))

        c0_r = float(sample_df.loc[aligned_labels == 0, "Recency"].median())
        c0_f = float(sample_df.loc[aligned_labels == 0, "Frequency"].median())
        c0_m = float(sample_df.loc[aligned_labels == 0, "Monetary"].median())
        c0_rev = float(sample_df.loc[aligned_labels == 0, "Monetary"].sum())

        c1_r = float(sample_df.loc[aligned_labels == 1, "Recency"].median())
        c1_f = float(sample_df.loc[aligned_labels == 1, "Frequency"].median())
        c1_m = float(sample_df.loc[aligned_labels == 1, "Monetary"].median())
        c1_rev = float(sample_df.loc[aligned_labels == 1, "Monetary"].sum())

        seed_results.append({
            "Experiment_ID": f"EXP034_seed_{seed}",
            "Seed": seed,
            "k": 2,
            "Silhouette": round(sil, 6),
            "Inertia": round(inertia, 2),
            "Raw_Label_Switched": is_switched,
            "Cluster_0_Customers": c0_size,
            "Cluster_1_Customers": c1_size,
            "Cluster_0_Recency_Median": c0_r,
            "Cluster_0_Frequency_Median": c0_f,
            "Cluster_0_Monetary_Median": c0_m,
            "Cluster_0_Revenue_GBP": round(c0_rev, 2),
            "Cluster_1_Recency_Median": c1_r,
            "Cluster_1_Frequency_Median": c1_f,
            "Cluster_1_Monetary_Median": c1_m,
            "Cluster_1_Revenue_GBP": round(c1_rev, 2),
        })

    stability_df = pd.DataFrame(seed_results)
    stability_csv = TABLES / "exp034_seed_stability.csv"
    stability_df.to_csv(stability_csv, index=False, encoding="utf-8-sig")
    print(f"Đã lưu bảng độ ổn định: {stability_csv}")

    # Compute pairwise ARI matrix
    ari_matrix = pd.DataFrame(index=SEEDS, columns=SEEDS, dtype=float)
    for s1 in SEEDS:
        for s2 in SEEDS:
            ari = adjusted_rand_score(labels_dict[s1], labels_dict[s2])
            ari_matrix.loc[s1, s2] = round(ari, 6)

    ari_csv = TABLES / "exp034_pairwise_ari.csv"
    ari_matrix.to_csv(ari_csv, encoding="utf-8-sig")
    print(f"Đã lưu ma trận ARI: {ari_csv}")
    print("\n--- MA TRẬN ADJUSTED RAND INDEX (ARI) GIỮA CÁC SEED ---")
    print(ari_matrix.to_string())

    # Save customer labels across seeds
    labels_export = pd.DataFrame({"CustomerID": sample_df["CustomerID"]})
    for seed in SEEDS:
        labels_export[f"cluster_seed_{seed}"] = aligned_labels_dict[seed]
    labels_csv = TABLES / "exp034_customer_labels.csv"
    labels_export.to_csv(labels_csv, index=False, encoding="utf-8-sig")

    # Plot 10_exp034_seed_stability.png
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    
    # Subplot 1: Silhouette & Inertia
    color_sil = "#1f77b4"
    ax1.set_xlabel("Random State (Seed)")
    ax1.set_ylabel("Silhouette Score (eval N=1000)", color=color_sil)
    line1 = ax1.plot([str(s) for s in SEEDS], stability_df["Silhouette"], marker="o", color=color_sil, linewidth=2, label="Silhouette")
    ax1.tick_params(axis="y", labelcolor=color_sil)
    ax1.set_ylim(0.40, 0.45)

    ax1_twin = ax1.twinx()
    color_ine = "#d62728"
    ax1_twin.set_ylabel("Inertia", color=color_ine)
    line2 = ax1_twin.plot([str(s) for s in SEEDS], stability_df["Inertia"], marker="s", linestyle="--", color=color_ine, linewidth=2, label="Inertia")
    ax1_twin.tick_params(axis="y", labelcolor=color_ine)

    lines = line1 + line2
    labels_legend = [l.get_label() for l in lines]
    ax1.legend(lines, labels_legend, loc="upper right")
    ax1.set_title("EXP-034: Điểm Silhouette & Inertia qua 5 Seed")
    ax1.grid(True, linestyle=":", alpha=0.6)

    # Subplot 2: Cluster Sizes
    x_indices = np.arange(len(SEEDS))
    width = 0.35
    bars0 = ax2.bar(x_indices - width/2, stability_df["Cluster_0_Customers"], width, label="Cụm 0 (Chi tiêu thấp)", color="#aec7e8")
    bars1 = ax2.bar(x_indices + width/2, stability_df["Cluster_1_Customers"], width, label="Cụm 1 (Chi tiêu cao)", color="#2ca02c")
    ax2.set_xlabel("Random State (Seed)")
    ax2.set_ylabel("Số lượng khách hàng")
    ax2.set_title("EXP-034: Kích thước 2 cụm sau chuẩn hóa nhãn")
    ax2.set_xticks(x_indices)
    ax2.set_xticklabels([f"seed={s}" for s in SEEDS])
    ax2.legend()
    ax2.set_ylim(0, 1500)
    for bar in bars0:
        ax2.annotate(f"{bar.get_height()}", (bar.get_x() + bar.get_width() / 2, bar.get_height() + 20),
                     ha="center", va="bottom", fontsize=9)
    for bar in bars1:
        ax2.annotate(f"{bar.get_height()}", (bar.get_x() + bar.get_width() / 2, bar.get_height() + 20),
                     ha="center", va="bottom", fontsize=9)
    ax2.grid(True, linestyle=":", alpha=0.6)

    fig.suptitle("EXP-034: Đánh giá độ ổn định của K-Means k=2 qua 5 Seed ngẫu nhiên", fontsize=14, fontweight="bold")
    fig.tight_layout()
    fig_path = FIGURES / "10_exp034_seed_stability.png"
    fig.savefig(fig_path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"Đã lưu biểu đồ: {fig_path}")

    # Append to experiment log
    log_rows = []
    for _, r in stability_df.iterrows():
        seed_val = int(r["Seed"])
        ari_vs_42 = float(ari_matrix.loc[seed_val, 42])
        switched_note = "Phát hiện nhãn gốc bị đảo (Cluster 0 <-> 1); đã chuẩn hóa nhãn theo Monetary." if r["Raw_Label_Switched"] else "Nhãn gốc giữ nguyên thứ tự chuẩn."
        log_rows.append({
            "Run_ID": run_id,
            "Experiment_ID": f"EXP-034-{seed_val}",
            "Run_Started_At": run_started_at.isoformat(timespec="seconds"),
            "Date": run_started_at.date().isoformat(),
            "Research_Question": "K-Means k=2 có ổn định khi thay đổi random_state (5 seeds) không?",
            "Dataset_Version": "Online Retail II UCI; exp034_fixed_customer_sample.csv (2000 IDs)",
            "RFM_Rows_Before_DropNA": sample_n,
            "RFM_Rows_After_DropNA": sample_n,
            "Unique_Customers_After_RFM_Cleaning": sample_n,
            "Sample_Rows_For_Clustering": sample_n,
            "Unique_Customers_Sampled": sample_n,
            "Evaluation_Rows_For_Silhouette": EVAL_N,
            "Unique_Customers_Evaluated": EVAL_N,
            "Feature_Set": "Recency, Frequency, Monetary",
            "Algorithm": "KMeans",
            "Hyperparameters": f"n_clusters=2; init=k-means++; n_init=20; random_state={seed_val}",
            "Validation_Strategy": f"Mẫu cố định n={sample_n}; eval n={EVAL_N}; ARI vs seed 42",
            "Scaling": "log1p + StandardScaler",
            "Metric_Name": "Silhouette Score & Adjusted Rand Index (ARI)",
            "Metric_Value": float(r["Silhouette"]),
            "Random_State": seed_val,
            "Observation": f"Silhouette={r['Silhouette']:.4f}; Inertia={r['Inertia']:.1f}; ARI_vs_42={ari_vs_42:.4f}; Sizes: C0={int(r['Cluster_0_Customers'])}, C1={int(r['Cluster_1_Customers'])}; {switched_note}",
            "Next_Action": "Chuyển sang EXP-035 (so sánh StandardScaler vs RobustScaler) trên cùng mẫu.",
        })

    # Read existing log and append
    if LOG_CSV.exists():
        old_log = pd.read_csv(LOG_CSV)
        combined = pd.concat([old_log, pd.DataFrame(log_rows)], ignore_index=True)
    else:
        combined = pd.DataFrame(log_rows)

    combined.to_csv(LOG_CSV, index=False, encoding="utf-8-sig")
    print(f"Đã cập nhật {len(log_rows)} dòng vào {LOG_CSV} (Tổng: {len(combined)} dòng)")

    # Update Excel experiment log
    try:
        with pd.ExcelWriter(LOG_XLSX, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            combined.to_excel(writer, sheet_name="Experiment_Log", index=False)
            stability_df.to_excel(writer, sheet_name="EXP034_Seed_Stability", index=False)
            ari_matrix.to_excel(writer, sheet_name="EXP034_Pairwise_ARI")
        print(f"Đã cập nhật thành công các sheet trong Excel: {LOG_XLSX}")
    except Exception as exc:
        print(f"Lỗi khi cập nhật Excel {LOG_XLSX}: {exc}")

    print("=== HOÀN THÀNH EXP-034 THÀNH CÔNG ===")


if __name__ == "__main__":
    run_exp034()
