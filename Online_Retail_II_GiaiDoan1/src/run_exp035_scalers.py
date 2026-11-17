# -*- coding: utf-8 -*-
"""EXP-035: So sánh StandardScaler và RobustScaler trên mẫu cố định 2.000 khách hàng.

Chạy từ thư mục gốc dự án: python Online_Retail_II_GiaiDoan1/src/run_exp035_scalers.py
Input: outputs/tables/rfm_table.csv và exp034_fixed_customer_sample.csv
Output: file EXP-035 mới; lịch sử thực nghiệm không bị ghi đè.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
import time
import uuid

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
from sklearn.preprocessing import RobustScaler, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "outputs" / "tables"
FIGURES = ROOT / "outputs" / "figures"
LOG_CSV = ROOT / "logs" / "experiment_log.csv"
LOG_XLSX = ROOT / "logs" / "experiment_log.xlsx"
FEATURES = ["Recency", "Frequency", "Monetary"]
SCALERS = {"StandardScaler": StandardScaler, "RobustScaler": RobustScaler}
K_VALUES = (2, 3)
SEED = 42
N_INIT = 20


def append_log_csv(rows: list[dict]) -> None:
    """Ghi thêm bản ghi EXP-035 vào CSV theo kiểu nguyên tử (không ghi đè lịch sử)."""
    LOG_CSV.parent.mkdir(parents=True, exist_ok=True)
    if LOG_CSV.exists():
        try:
            previous = pd.read_csv(LOG_CSV)
        except Exception as exc:
            raise RuntimeError(f"Không thể đọc experiment_log.csv: {LOG_CSV}") from exc
    else:
        previous = pd.DataFrame()
    combined = pd.concat([previous, pd.DataFrame(rows)], ignore_index=True, sort=False)
    temp_path = LOG_CSV.with_name(f"{LOG_CSV.stem}.tmp{LOG_CSV.suffix}")
    try:
        combined.to_csv(temp_path, index=False, encoding="utf-8-sig")
        temp_path.replace(LOG_CSV)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def sync_to_xlsx(df_new: pd.DataFrame, sheet_name: str = "EXP035_Scaler_Comparison") -> None:
    """Đồng bộ kết quả EXP-035 vào file experiment_log.xlsx."""
    if not LOG_XLSX.exists():
        print(f"[CẢNH BÁO] {LOG_XLSX} chưa tồn tại, bỏ qua đồng bộ XLSX.")
        return
    try:
        import openpyxl
        with pd.ExcelWriter(LOG_XLSX, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            df_new.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"Đã đồng bộ {sheet_name} vào {LOG_XLSX}")
    except Exception as exc:
        print(f"[CẢNH BÁO] Không thể ghi XLSX: {exc}")


def main() -> None:
    run_started_at = datetime.now().astimezone()
    run_id = f"{run_started_at.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

    rfm_path = TABLES / "rfm_table.csv"
    ids_path = TABLES / "exp034_fixed_customer_sample.csv"
    if not rfm_path.is_file() or not ids_path.is_file():
        raise FileNotFoundError("EXP-035 cần rfm_table.csv và exp034_fixed_customer_sample.csv.")

    rfm = pd.read_csv(rfm_path)
    sample_ids = pd.read_csv(ids_path)["CustomerID"]
    sample = sample_ids.to_frame().merge(rfm, on="CustomerID", how="left", validate="one_to_one")

    # Kiểm tra điều kiện so sánh nghiêm ngặt
    if sample[FEATURES].isna().any().any():
        raise ValueError("Một số khách hàng mẫu cố định thiếu giá trị RFM.")
    if sample["CustomerID"].duplicated().any():
        raise ValueError("Mẫu cố định có CustomerID trùng lặp.")
    if len(sample) != len(sample_ids):
        raise ValueError("Không khớp số lượng khách hàng trong mẫu cố định.")
    if (sample[FEATURES] < 0).any().any():
        raise ValueError("Giá trị RFM phải không âm trước khi log1p.")

    print(f"[EXP-035] Mẫu cố định: {len(sample)} khách hàng | Seed: {SEED} | k: {list(K_VALUES)}")

    # Biến đổi log1p
    log_features = np.log1p(sample[FEATURES].astype(float))
    eval_n = min(1000, len(sample))

    # Kiểm tra IQR sau log1p (ngăn RobustScaler chia 0)
    print("\n[Kiểm tra IQR sau log1p]")
    for feature in FEATURES:
        q1 = np.percentile(log_features[feature], 25)
        q3 = np.percentile(log_features[feature], 75)
        iqr = q3 - q1
        flag = " ⚠ IQR ≈ 0!" if iqr < 1e-6 else ""
        print(f"  {feature}: Q1={q1:.4f} | Q3={q3:.4f} | IQR={iqr:.4f}{flag}")

    metrics_rows: list[dict] = []
    profile_rows: list[pd.DataFrame] = []
    scaler_diagnostics: list[dict] = []
    labels_by_config: dict[tuple[str, int], np.ndarray] = {}
    scaled_by_scaler: dict[str, np.ndarray] = {}
    models_by_config: dict[tuple[str, int], tuple] = {}

    for scaler_name, scaler_type in SCALERS.items():
        scaled = scaler_type().fit_transform(log_features)
        scaled_by_scaler[scaler_name] = scaled
        for i, feature in enumerate(FEATURES):
            scaler_diagnostics.append({
                "experiment_id": "EXP-035",
                "scaler": scaler_name,
                "feature": feature,
                "mean_after_scaling": float(np.mean(scaled[:, i])),
                "variance_after_scaling": float(np.var(scaled[:, i], ddof=0)),
                "std_after_scaling": float(np.std(scaled[:, i], ddof=0)),
                "sample_n": len(sample),
                "transform_before_scaling": "log1p",
            })
        for k in K_VALUES:
            start = time.perf_counter()
            model = KMeans(n_clusters=k, init="k-means++", n_init=N_INIT, random_state=SEED)
            labels = model.fit_predict(scaled)
            elapsed = time.perf_counter() - start
            labels_by_config[(scaler_name, k)] = labels
            models_by_config[(scaler_name, k)] = (model, labels, elapsed)

    for k in K_VALUES:
        ari = adjusted_rand_score(
            labels_by_config[("StandardScaler", k)],
            labels_by_config[("RobustScaler", k)]
        )
        for scaler_name in SCALERS:
            model, labels, elapsed = models_by_config[(scaler_name, k)]
            counts = pd.Series(labels).value_counts().sort_index()
            scaled_data = scaled_by_scaler[scaler_name]
            row = {
                "experiment_id": "EXP-035",
                "scaler": scaler_name,
                "algorithm": "KMeans",
                "k": k,
                "init": "k-means++",
                "n_init": N_INIT,
                "seed": SEED,
                "sample_n": len(sample),
                "features": ",".join(FEATURES),
                "transform": "log1p",
                "silhouette": np.nan,
                "davies_bouldin": np.nan,
                "calinski_harabasz": np.nan,
                "inertia": float(model.inertia_),
                "runtime_seconds": round(elapsed, 4),
                "ari_vs_other_scaler_same_k": float(ari),
                "cluster_sizes": json.dumps({str(c): int(n) for c, n in counts.items()}),
                "status": "hop_le",
                "error": "",
            }
            try:
                row["silhouette"] = float(silhouette_score(scaled_data[:eval_n], labels[:eval_n]))
                row["davies_bouldin"] = float(davies_bouldin_score(scaled_data[:eval_n], labels[:eval_n]))
                row["calinski_harabasz"] = float(calinski_harabasz_score(scaled_data[:eval_n], labels[:eval_n]))
                row["evaluation_sample_n"] = eval_n
                row["metric_note"] = "Metric trên cùng phần đầu 1.000 CustomerID của sample; fit K-Means và inertia trên toàn bộ sample cố định."
            except ValueError as exc:
                row["status"] = "khong_hop_le_metric"
                row["error"] = str(exc)
            metrics_rows.append(row)

            profile = sample.assign(cluster=labels).groupby("cluster").agg(
                so_khach=("CustomerID", "nunique"),
                Recency_trung_vi=("Recency", "median"),
                Frequency_trung_vi=("Frequency", "median"),
                Monetary_trung_vi=("Monetary", "median"),
                Monetary_tong=("Monetary", "sum"),
            ).reset_index()
            profile.insert(0, "scaler", scaler_name)
            profile.insert(1, "k", k)
            profile_rows.append(profile)

    # Lưu kết quả
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)

    df_metrics = pd.DataFrame(metrics_rows)
    df_metrics.to_csv(TABLES / "exp035_scaling_comparison.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(scaler_diagnostics).to_csv(
        TABLES / "exp035_scaling_diagnostics.csv", index=False, encoding="utf-8-sig"
    )
    pd.concat(profile_rows, ignore_index=True).to_csv(
        TABLES / "exp035_cluster_profiles.csv", index=False, encoding="utf-8-sig"
    )
    print("\n[Kết quả EXP-035]")
    print(df_metrics[["scaler", "k", "silhouette", "davies_bouldin", "calinski_harabasz",
                       "inertia", "ari_vs_other_scaler_same_k", "cluster_sizes"]].to_string(index=False))

    # Vẽ biểu đồ phân phối đặc trưng sau chuẩn hóa
    fig, axes = plt.subplots(2, len(FEATURES), figsize=(15, 8))
    for row_idx, scaler_name in enumerate(SCALERS):
        scaled = scaled_by_scaler[scaler_name]
        for col_idx, feature in enumerate(FEATURES):
            axes[row_idx, col_idx].boxplot(scaled[:, col_idx], showfliers=False)
            axes[row_idx, col_idx].set_title(f"{scaler_name}: {feature}")
            axes[row_idx, col_idx].set_ylabel("Giá trị sau chuẩn hóa")
            axes[row_idx, col_idx].set_xticks([])
    fig.suptitle("EXP-035 — Phân phối đặc trưng sau chuẩn hóa (log1p → Scaler)")
    fig.tight_layout()
    fig.savefig(FIGURES / "11_exp035_scaler_feature_distributions.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"\nBiểu đồ đã lưu: 11_exp035_scaler_feature_distributions.png")

    # Vẽ biểu đồ so sánh Silhouette giữa 2 scaler
    fig2, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(K_VALUES))
    width = 0.35
    std_sil = [r["silhouette"] for r in metrics_rows if r["scaler"] == "StandardScaler"]
    rob_sil = [r["silhouette"] for r in metrics_rows if r["scaler"] == "RobustScaler"]
    ax.bar(x - width/2, std_sil, width, label="StandardScaler", color="steelblue")
    ax.bar(x + width/2, rob_sil, width, label="RobustScaler", color="coral")
    ax.set_xticks(x)
    ax.set_xticklabels([f"k={k}" for k in K_VALUES])
    ax.set_ylabel("Silhouette Score")
    ax.set_title("EXP-035 — So sánh Silhouette: StandardScaler vs RobustScaler")
    ax.legend()
    ax.set_ylim(0, 1)
    fig2.tight_layout()
    fig2.savefig(FIGURES / "11b_exp035_silhouette_comparison.png", dpi=160, bbox_inches="tight")
    plt.close(fig2)
    print("Biểu đồ đã lưu: 11b_exp035_silhouette_comparison.png")

    # Ghi vào experiment_log.csv
    rfm_rows_count = len(rfm)
    rfm_rows_before_dropna = len(rfm)
    rfm_rows_after_dropna = int(rfm.dropna(subset=FEATURES).shape[0])
    log_rows = []
    for row in metrics_rows:
        score_text = (
            f"Silhouette={row['silhouette']:.4f}; DBI={row['davies_bouldin']:.4f}; "
            f"CHI={row['calinski_harabasz']:.2f}; inertia={row['inertia']:.2f}; "
            f"sizes={row['cluster_sizes']}; ARI_vs_other_scaler={row['ari_vs_other_scaler_same_k']:.4f}"
        )
        log_rows.append({
            "Run_ID": run_id,
            "Experiment_ID": "EXP-035",
            "Run_Started_At": run_started_at.isoformat(timespec="seconds"),
            "Date": run_started_at.date().isoformat(),
            "Research_Question": "StandardScaler và RobustScaler làm thay đổi chất lượng/hình học cụm RFM như thế nào?",
            "Dataset_Version": "Online Retail II UCI; outputs/tables/rfm_table.csv",
            "RFM_Rows_Before_DropNA": rfm_rows_before_dropna,
            "RFM_Rows_After_DropNA": rfm_rows_after_dropna,
            "Unique_Customers_After_RFM_Cleaning": int(rfm["CustomerID"].nunique()),
            "Sample_Rows_For_Clustering": len(sample),
            "Unique_Customers_Sampled": int(sample["CustomerID"].nunique()),
            "Evaluation_Rows_For_Silhouette": eval_n,
            "Unique_Customers_Evaluated": int(sample.iloc[:eval_n]["CustomerID"].nunique()),
            "Feature_Set": ", ".join(FEATURES),
            "Algorithm": "KMeans",
            "Hyperparameters": f"n_clusters={row['k']}; init=k-means++; n_init={N_INIT}; random_state={SEED}",
            "Validation_Strategy": f"Cùng {len(sample)} CustomerID fit và {eval_n} CustomerID đánh giá; so sánh riêng từng k={row['k']}; cùng n_init={N_INIT}, seed={SEED}; chỉ scaler thay đổi",
            "Scaling": f"log1p + {row['scaler']}",
            "Metric_Name": "Silhouette; Davies-Bouldin; Calinski-Harabasz; inertia",
            "Metric_Value": row["silhouette"],
            "Random_State": SEED,
            "Observation": f"status={row['status']}; {score_text}; error={row['error']}",
            "Next_Action": "So sánh metric, phương sai đặc trưng, ARI và hồ sơ RFM; chọn scaler phù hợp nhất.",
        })
    append_log_csv(log_rows)
    print(f"\nĐã ghi {len(log_rows)} bản ghi EXP-035 vào {LOG_CSV}")

    # Đồng bộ sang XLSX
    sync_to_xlsx(df_metrics, sheet_name="EXP035_Scaler_Comparison")
    sync_to_xlsx(pd.DataFrame(scaler_diagnostics), sheet_name="EXP035_Diagnostics")

    print(f"\n✅ EXP-035 hoàn thành. Run_ID: {run_id}")
    print(f"   Thời gian: {run_started_at.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
