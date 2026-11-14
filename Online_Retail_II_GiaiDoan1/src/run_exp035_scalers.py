"""Run EXP-035: compare StandardScaler and RobustScaler on the fixed sample.

Run from the repository root: python src/run_exp035_scalers.py
Inputs: outputs/tables/rfm_table.csv and exp034_fixed_customer_sample.csv.
Outputs are new EXP-035 files; previous experiment history is not overwritten.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
import time
import uuid

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
LOG = ROOT / "logs" / "experiment_log.csv"
FEATURES = ["Recency", "Frequency", "Monetary"]
SCALERS = {"StandardScaler": StandardScaler, "RobustScaler": RobustScaler}
K_VALUES = (2, 3)
SEED = 42
N_INIT = 20


def append_log(rows: list[dict]) -> None:
    """Append EXP-035 records atomically without replacing experiment history."""
    LOG.parent.mkdir(parents=True, exist_ok=True)
    if LOG.exists():
        try:
            previous = pd.read_csv(LOG)
        except Exception as exc:
            raise RuntimeError(f"Cannot read existing experiment log; stopped to preserve it: {LOG}") from exc
    else:
        previous = pd.DataFrame()
    combined = pd.concat([previous, pd.DataFrame(rows)], ignore_index=True, sort=False)
    temp_path = LOG.with_name(f"{LOG.stem}.tmp{LOG.suffix}")
    try:
        combined.to_csv(temp_path, index=False, encoding="utf-8-sig")
        temp_path.replace(LOG)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def main() -> None:
    run_started_at = datetime.now().astimezone()
    run_id = f"{run_started_at.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    rfm_path = TABLES / "rfm_table.csv"
    ids_path = TABLES / "exp034_fixed_customer_sample.csv"
    if not rfm_path.is_file() or not ids_path.is_file():
        raise FileNotFoundError("EXP-035 needs rfm_table.csv and exp034_fixed_customer_sample.csv.")

    rfm = pd.read_csv(rfm_path)
    sample_ids = pd.read_csv(ids_path)["CustomerID"]
    sample = sample_ids.to_frame().merge(rfm, on="CustomerID", how="left", validate="one_to_one")
    if sample[FEATURES].isna().any().any():
        raise ValueError("Some fixed sample customers have missing RFM values.")
    if sample["CustomerID"].duplicated().any():
        raise ValueError("The fixed sample contains duplicate CustomerID values.")
    if len(sample) != len(sample_ids):
        raise ValueError("Not all fixed sample IDs resolved to an RFM row.")
    if (sample[FEATURES] < 0).any().any():
        raise ValueError("RFM values must be nonnegative before log1p.")

    log_features = np.log1p(sample[FEATURES].astype(float))
    metrics_rows: list[dict] = []
    profile_rows: list[pd.DataFrame] = []
    scaler_diagnostics: list[dict] = []
    labels_by_config: dict[tuple[str, int], np.ndarray] = {}
    scaled_by_scaler: dict[str, np.ndarray] = {}
    models_by_config: dict[tuple[str, int], tuple[KMeans, np.ndarray, float]] = {}

    for scaler_name, scaler_type in SCALERS.items():
        scaled = scaler_type().fit_transform(log_features)
        scaled_by_scaler[scaler_name] = scaled
        for i, feature in enumerate(FEATURES):
            scaler_diagnostics.append({
                "experiment_id": "EXP-035", "scaler": scaler_name, "feature": feature,
                "mean_after_scaling": float(np.mean(scaled[:, i])),
                "variance_after_scaling": float(np.var(scaled[:, i], ddof=0)),
                "std_after_scaling": float(np.std(scaled[:, i], ddof=0)),
                "sample_n": len(sample), "transform_before_scaling": "log1p",
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
            labels_by_config[("StandardScaler", k)], labels_by_config[("RobustScaler", k)]
        )
        for scaler_name in SCALERS:
            model, labels, elapsed = models_by_config[(scaler_name, k)]
            counts = pd.Series(labels).value_counts().sort_index()
            row = {
                "experiment_id": "EXP-035", "scaler": scaler_name,
                "algorithm": "KMeans", "k": k, "init": "k-means++",
                "n_init": N_INIT, "seed": SEED, "sample_n": len(sample),
                "features": ",".join(FEATURES), "transform": "log1p",
                "silhouette": np.nan, "davies_bouldin": np.nan,
                "calinski_harabasz": np.nan, "inertia": float(model.inertia_),
                "runtime_seconds": elapsed, "ari_vs_other_scaler_same_k": float(ari),
                "cluster_sizes": json.dumps({str(c): int(n) for c, n in counts.items()}),
                "status": "valid", "error": "",
            }
            try:
                row["silhouette"] = float(silhouette_score(scaled_by_scaler[scaler_name], labels))
                row["davies_bouldin"] = float(davies_bouldin_score(scaled_by_scaler[scaler_name], labels))
                row["calinski_harabasz"] = float(calinski_harabasz_score(scaled_by_scaler[scaler_name], labels))
            except ValueError as exc:
                row["status"] = "invalid_metrics"
                row["error"] = str(exc)
            metrics_rows.append(row)

            profile = sample.assign(cluster=labels).groupby("cluster").agg(
                customers=("CustomerID", "nunique"),
                Recency_median=("Recency", "median"),
                Frequency_median=("Frequency", "median"),
                Monetary_median=("Monetary", "median"),
                Monetary_sum=("Monetary", "sum"),
            ).reset_index()
            profile.insert(0, "scaler", scaler_name)
            profile.insert(1, "k", k)
            profile_rows.append(profile)

    TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(metrics_rows).to_csv(
        TABLES / "exp035_scaling_comparison.csv", index=False, encoding="utf-8-sig"
    )
    pd.DataFrame(scaler_diagnostics).to_csv(
        TABLES / "exp035_scaling_diagnostics.csv", index=False, encoding="utf-8-sig"
    )
    pd.concat(profile_rows, ignore_index=True).to_csv(
        TABLES / "exp035_cluster_profiles.csv", index=False, encoding="utf-8-sig"
    )

    rfm_rows = len(rfm)
    log_rows = []
    for row in metrics_rows:
        score_text = (
            f"Silhouette={row['silhouette']}; DBI={row['davies_bouldin']}; "
            f"CHI={row['calinski_harabasz']}; inertia={row['inertia']}; "
            f"sizes={row['cluster_sizes']}; ARI_vs_other_scaler={row['ari_vs_other_scaler_same_k']}"
        )
        log_rows.append({
            "Run_ID": run_id, "Experiment_ID": "EXP-035",
            "Run_Started_At": run_started_at.isoformat(timespec="seconds"),
            "Date": run_started_at.date().isoformat(),
            "Research_Question": "StandardScaler va RobustScaler lam thay doi chat luong/hinh hoc cum RFM nhu the nao?",
            "Dataset_Version": "Online Retail II UCI; outputs/tables/rfm_table.csv",
            "RFM_Rows_Before_DropNA": rfm_rows, "RFM_Rows_After_DropNA": len(sample),
            "Unique_Customers_After_RFM_Cleaning": int(rfm["CustomerID"].nunique()),
            "Sample_Rows_For_Clustering": len(sample),
            "Unique_Customers_Sampled": int(sample["CustomerID"].nunique()),
            "Evaluation_Rows_For_Silhouette": len(sample),
            "Unique_Customers_Evaluated": int(sample["CustomerID"].nunique()),
            "Feature_Set": ", ".join(FEATURES), "Algorithm": "KMeans",
            "Hyperparameters": f"n_clusters={row['k']}; init=k-means++; n_init={N_INIT}; random_state={SEED}",
            "Validation_Strategy": "Same fixed customer IDs and features; full-sample unsupervised metrics",
            "Scaling": f"log1p + {row['scaler']}",
            "Metric_Name": "Silhouette; Davies-Bouldin; Calinski-Harabasz; inertia",
            "Metric_Value": row["silhouette"], "Random_State": SEED,
            "Observation": f"status={row['status']}; {score_text}; error={row['error']}",
            "Next_Action": "Compare metrics, feature variances, ARI and RFM profiles; choose scaler with business interpretation.",
        })
    append_log(log_rows)

    fig, axes = plt.subplots(2, len(FEATURES), figsize=(15, 8))
    for row, scaler_name in enumerate(SCALERS):
        scaled = scaled_by_scaler[scaler_name]
        for col, feature in enumerate(FEATURES):
            axes[row, col].boxplot(scaled[:, col], showfliers=False)
            axes[row, col].set_title(f"{scaler_name}: {feature}")
            axes[row, col].set_ylabel("Scaled value")
            axes[row, col].set_xticks([])
    fig.suptitle("EXP-035 — Feature distributions after scaling (log1p RFM)")
    fig.tight_layout()
    fig.savefig(FIGURES / "10_exp035_scaler_feature_distributions.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(pd.DataFrame(metrics_rows).to_string(index=False))
    print(f"Saved EXP-035 tables, figure and appended experiment log under {ROOT}.")


if __name__ == "__main__":
    main()
