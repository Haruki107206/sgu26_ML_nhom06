# -*- coding: utf-8 -*-
"""Complete internal-cluster metrics and model decision artifacts (EXP-034..036).

Run with the project's Python environment from the project root:
    python Online_Retail_II_GiaiDoan1/src/complete_model_evaluation.py

DBSCAN validation metrics are computed on non-noise records only. Noise count and
rate are always retained; metrics are undefined when fewer than two clusters or
fewer than two valid records remain. Inertia is defined only for K-Means.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import AgglomerativeClustering, DBSCAN, KMeans
from sklearn.metrics import adjusted_rand_score, calinski_harabasz_score, davies_bouldin_score, silhouette_score
from sklearn.preprocessing import RobustScaler, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "outputs" / "tables"
FIGURES = ROOT / "outputs" / "figures"
LOGS = ROOT / "logs"
FEATURES = ["Recency", "Frequency", "Monetary"]
SEED = 42
EVALUATION_SIZE = 1000
DBSCAN_GRID = [(eps, min_samples) for eps in (0.25, 0.35, 0.45, 0.6, 0.8, 1.0) for min_samples in (5, 10, 20)]


def evaluate(labels: np.ndarray, X: np.ndarray) -> dict:
    noise = labels == -1
    valid_labels = labels[~noise]
    valid_X = X[~noise]
    unique = np.unique(valid_labels)
    result = {
        "clusters_excluding_noise": int(len(unique)),
        "noise_points": int(noise.sum()),
        "noise_percent": float(noise.mean() * 100),
        "evaluated_points_excluding_noise": int((~noise).sum()),
        "silhouette": np.nan,
        "davies_bouldin": np.nan,
        "calinski_harabasz": np.nan,
        "status": "valid",
        "evaluation_note": "",
    }
    if len(unique) < 2 or len(valid_X) <= len(unique):
        result["status"] = "undefined_metrics"
        result["evaluation_note"] = "Cần ít nhất 2 cụm và số điểm hợp lệ lớn hơn số cụm; bỏ nhãn nhiễu -1 khi đánh giá."
        return result
    result["silhouette"] = float(silhouette_score(valid_X, valid_labels))
    result["davies_bouldin"] = float(davies_bouldin_score(valid_X, valid_labels))
    result["calinski_harabasz"] = float(calinski_harabasz_score(valid_X, valid_labels))
    result["evaluation_note"] = "Ba chỉ số tính trên điểm không nhiễu; tỷ lệ nhiễu báo riêng."
    return result


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    rfm = pd.read_csv(TABLES / "rfm_table.csv")
    sample_ids = pd.read_csv(TABLES / "exp034_fixed_customer_sample.csv")["CustomerID"]
    sample = sample_ids.to_frame().merge(rfm, on="CustomerID", how="left", validate="one_to_one")
    if sample[FEATURES].isna().any().any() or (sample[FEATURES] < 0).any().any():
        raise ValueError("RFM sample contains missing or negative values; cannot proceed with log1p.")
    X = StandardScaler().fit_transform(np.log1p(sample[FEATURES].astype(float)))
    eval_n = min(EVALUATION_SIZE, len(sample))
    X_eval = X[:eval_n]

    # DBSCAN metrics/noise were missing from EXP-036. Evaluate the predeclared grid.
    dbscan_rows = []
    for eps, min_samples in DBSCAN_GRID:
        model = DBSCAN(eps=eps, min_samples=min_samples, metric="euclidean")
        labels = model.fit_predict(X)
        row = {"experiment_id": "EXP-036", "algorithm": "DBSCAN", "k": np.nan,
               "parameters": f"eps={eps}; min_samples={min_samples}; metric=euclidean",
               "sample_n": len(sample), "evaluation_sample_n": eval_n, "seed": SEED, "features": ",".join(FEATURES),
               "transform_scaling": "log1p + StandardScaler (fit on fixed sample)"}
        row.update(evaluate(labels[:eval_n], X_eval))
        row["noise_points"] = int(np.sum(labels == -1))
        row["noise_percent"] = float(np.mean(labels == -1) * 100)
        row["evaluated_points_excluding_noise"] = int(np.sum(labels[:eval_n] != -1))
        row["evaluation_note"] += " Metrics use the first shared 1,000 evaluation points; noise count/rate use the full 2,000-customer fit sample."
        row["cluster_sizes"] = json.dumps({str(int(k)): int(v) for k, v in pd.Series(labels).value_counts().sort_index().items()})
        row["inertia"] = np.nan
        dbscan_rows.append(row)
    dbscan = pd.DataFrame(dbscan_rows)
    dbscan.to_csv(TABLES / "exp036_dbscan_multi_metrics.csv", index=False, encoding="utf-8-sig")

    # Ward is the hierarchical family tested in EXP-034; add the same metrics on
    # the identical sample/preprocessing so it can be compared with K-Means.
    ward_rows = []
    for k in range(2, 9):
        labels = AgglomerativeClustering(n_clusters=k, linkage="ward", metric="euclidean").fit_predict(X)
        row = {"experiment_id": "EXP-036", "algorithm": "Agglomerative_Ward", "k": k,
               "parameters": f"n_clusters={k}; linkage=ward; metric=euclidean",
               "sample_n": len(sample), "evaluation_sample_n": eval_n, "seed": SEED, "features": ",".join(FEATURES),
               "transform_scaling": "log1p + StandardScaler (fit on fixed sample)"}
        row.update(evaluate(labels[:eval_n], X_eval))
        row["noise_points"] = 0
        row["noise_percent"] = 0.0
        row["evaluation_note"] += " Metrics use the first shared 1,000 evaluation points; clustering is fit on the full 2,000-customer sample."
        row["cluster_sizes"] = json.dumps({str(int(c)): int(n) for c, n in pd.Series(labels).value_counts().sort_index().items()})
        row["inertia"] = np.nan
        ward_rows.append(row)
    ward = pd.DataFrame(ward_rows)
    ward.to_csv(TABLES / "exp036_ward_multi_metrics.csv", index=False, encoding="utf-8-sig")

    # A combined, transparent decision table. Silhouette values across experiments
    # are not treated as directly comparable unless protocol/scaler are identical.
    old = pd.read_csv(TABLES / "clustering_model_comparison.csv")
    exp35 = pd.read_csv(TABLES / "exp035_scaling_comparison.csv")
    exp36 = pd.read_csv(TABLES / "exp036_multi_metrics.csv")
    ward = pd.read_csv(TABLES / "exp036_ward_multi_metrics.csv")
    decisions = []
    for _, row in exp35.iterrows():
        decisions.append({
            "experiment": "EXP-035", "candidate": f"KMeans {row['scaler']} k={int(row['k'])}",
            "sample_n": int(row["sample_n"]), "evaluation_sample_n": int(row.get("evaluation_sample_n", eval_n)),
            "seed": int(row["seed"]), "clusters": int(row["k"]),
            "noise_percent": 0.0, "silhouette": row["silhouette"], "davies_bouldin": row["davies_bouldin"],
            "calinski_harabasz": row["calinski_harabasz"], "inertia": row["inertia"],
            "tradeoff": ("k=2: chỉ số nội tại nhỉnh nhẹ, nhưng phân hoạch scaler khác nhau (ARI=0.868); inertia chỉ so trong cùng scaler."
                         if int(row["k"]) == 2 else "k=3: thêm phân khúc nhưng Silhouette thấp hơn k=2; scaler làm thay đổi cách gán cụm (ARI=0.843)."),
            "selection_note": "Cặp scaler dùng chung sample/k/seed; không so inertia khác scaler.",
        })
    for _, row in exp36.iterrows():
        decisions.append({
            "experiment": "EXP-036", "candidate": f"KMeans StandardScaler k={int(row['k'])}",
            "sample_n": len(sample), "evaluation_sample_n": int(row.get("evaluation_sample_n", eval_n)),
            "seed": SEED, "clusters": int(row["k"]), "noise_percent": 0.0,
            "silhouette": row["silhouette"], "davies_bouldin": row["davies_bouldin"],
            "calinski_harabasz": row["calinski_harabasz"], "inertia": row["inertia"],
        "tradeoff": "k=2 đạt Silhouette cao nhất và DBI thấp nhất trong k=2..8; k lớn giảm inertia nhưng tăng độ phức tạp, CHI giảm.",
            "selection_note": "log1p + StandardScaler; metric trên cùng 1.000 điểm đầu; inertia chỉ so trong cùng pipeline và model fit trên 2.000 điểm.",
        })
    for _, row in ward.iterrows():
        decisions.append({
            "experiment": "EXP-034/036", "candidate": f"Agglomerative Ward k={int(row['k'])}",
            "sample_n": len(sample), "evaluation_sample_n": int(row.get("evaluation_sample_n", eval_n)),
            "seed": SEED, "clusters": int(row["k"]), "noise_percent": 0.0,
            "silhouette": row["silhouette"], "davies_bouldin": row["davies_bouldin"],
            "calinski_harabasz": row["calinski_harabasz"], "inertia": np.nan,
            "tradeoff": "Ward không tạo điểm nhiễu và tạo cụm phân cấp; không có inertia tương đương K-Means. Chỉ số nội tại so trên cùng mẫu/preprocessing.",
            "selection_note": "Cùng sample fit 2.000 và metric trên cùng 1.000 điểm đầu, log1p + StandardScaler; k=2..8; không so inertia với K-Means.",
        })
    for _, row in old[old["model"].astype(str).str.startswith("DBSCAN")].iterrows():
        params = str(row["parameters"])
        matching = dbscan[dbscan["parameters"] == params]
        metric = matching.iloc[0] if len(matching) else {}
        decisions.append({
            "experiment": "EXP-034/036", "candidate": f"DBSCAN {params}",
            "sample_n": int(metric.get("sample_n", row["evaluated_customers"])),
            "evaluation_sample_n": int(metric.get("evaluation_sample_n", eval_n)), "seed": SEED,
            "clusters": int(metric.get("clusters_excluding_noise", row["clusters_excluding_noise"])),
            "noise_percent": metric.get("noise_percent", row["noise_percent"]),
            "silhouette": metric.get("silhouette", row["silhouette_excluding_noise"]),
            "davies_bouldin": metric.get("davies_bouldin", np.nan),
            "calinski_harabasz": metric.get("calinski_harabasz", np.nan), "inertia": np.nan,
            "tradeoff": "DBSCAN phát hiện điểm nhiễu nhưng số cụm/noise khác nhau mạnh; silhouette cao khi loại nhiều khách không đồng nghĩa nghiệm tốt hơn.",
            "selection_note": "Metric được tính trên cùng 1.000 điểm đánh giá rồi loại nhãn -1; số/tỷ lệ noise báo trên 2.000 điểm fit.",
        })
    decision = pd.DataFrame(decisions)
    decision.to_csv(TABLES / "model_decision_exp034_exp036.csv", index=False, encoding="utf-8-sig")
    combined_metrics = pd.concat([exp36.assign(experiment_id="EXP-036"), ward, dbscan], ignore_index=True, sort=False)
    combined_metrics.to_csv(TABLES / "exp036_all_algorithms_multi_metrics.csv", index=False, encoding="utf-8-sig")

    # The highest-silhouette candidate among the tested scalers is RobustScaler k=2.
    # Check its seed sensitivity on the same five seeds used by EXP-034.
    robust_X = RobustScaler().fit_transform(np.log1p(sample[FEATURES].astype(float)))
    stability_seeds = (42, 7, 21, 123, 2026)
    robust_labels = {}
    robust_rows = []
    for seed in stability_seeds:
        model = KMeans(n_clusters=2, init="k-means++", n_init=20, random_state=seed)
        labels = model.fit_predict(robust_X)
        robust_labels[seed] = labels
        robust_rows.append({
            "experiment_id": "EXP-036", "scaler": "RobustScaler", "algorithm": "KMeans", "k": 2,
            "seed": seed, "sample_n": len(sample), "n_init": 20,
            "silhouette": float(silhouette_score(robust_X[:eval_n], labels[:eval_n])),
            "davies_bouldin": float(davies_bouldin_score(robust_X[:eval_n], labels[:eval_n])),
            "calinski_harabasz": float(calinski_harabasz_score(robust_X[:eval_n], labels[:eval_n])),
            "inertia": float(model.inertia_),
            "evaluation_sample_n": eval_n,
            "metric_note": "Silhouette/DBI/CHI trên 1.000 điểm đầu dùng chung; fit/inertia trên mẫu cố định 2.000 khách.",
            "cluster_sizes": json.dumps({str(int(c)): int(n) for c, n in pd.Series(labels).value_counts().sort_index().items()}),
        })
    for row in robust_rows:
        seed = row["seed"]
        pair_scores = [adjusted_rand_score(robust_labels[seed], robust_labels[other])
                       for other in stability_seeds if other != seed]
        row["ari_to_seed42"] = float(adjusted_rand_score(robust_labels[42], robust_labels[seed]))
        row["mean_pairwise_ari"] = float(np.mean(pair_scores)) if pair_scores else 1.0
        row["min_pairwise_ari"] = float(min(pair_scores)) if pair_scores else 1.0
    robust_stability = pd.DataFrame(robust_rows)
    robust_stability.to_csv(TABLES / "exp036_robust_stability.csv", index=False, encoding="utf-8-sig")

    chosen = next(r for r in exp35.to_dict("records") if r["scaler"] == "RobustScaler" and int(r["k"]) == 2)
    selected_labels = robust_labels[42]
    selected_profiles = sample.assign(cluster=selected_labels).groupby("cluster").agg(
        customers=("CustomerID", "nunique"), Recency_median=("Recency", "median"), Recency_mean=("Recency", "mean"),
        Frequency_median=("Frequency", "median"), Frequency_mean=("Frequency", "mean"),
        Monetary_median=("Monetary", "median"), Monetary_mean=("Monetary", "mean"), Monetary_sum=("Monetary", "sum"),
    ).reset_index()
    selected_profiles.to_csv(TABLES / "selected_model_cluster_profiles.csv", index=False, encoding="utf-8-sig")
    selected_sample = sample.assign(cluster=selected_labels)
    selected_sample.to_csv(TABLES / "selected_model_customer_labels.csv", index=False, encoding="utf-8-sig")

    # Refresh the interpretation table and text with the final RobustScaler labels.
    overall_medians = sample[FEATURES].median()
    interpretation = selected_profiles.copy()
    for feature in FEATURES:
        interpretation[f"{feature}_vs_sample_median"] = np.where(
            interpretation[f"{feature}_median"] < overall_medians[feature], "thấp hơn trung vị mẫu",
            np.where(interpretation[f"{feature}_median"] > overall_medians[feature], "cao hơn trung vị mẫu",
                     "bằng trung vị mẫu"),
        )
    interpretation.to_csv(TABLES / "cluster_interpretation.csv", index=False, encoding="utf-8-sig")
    interpretation_notes = [
        "# Diễn giải cụm từ mẫu RFM",
        "",
        "Mô hình được chọn: **K-Means + log1p + RobustScaler + k=2**, `n_init=20`, `random_state=42`.",
        f"Silhouette={chosen['silhouette']:.4f}; Davies–Bouldin={chosen['davies_bouldin']:.4f}; ",
        f"Calinski–Harabasz={chosen['calinski_harabasz']:.2f}; noise=0%.",
        "Nhãn cụm được tạo lại bằng RobustScaler; phần diễn giải dưới đây dùng trung vị của cùng mẫu 2.000 khách.",
        f"Trung vị toàn mẫu: Recency={overall_medians['Recency']:.2f} ngày, ",
        f"Frequency={overall_medians['Frequency']:.2f} hóa đơn, Monetary={overall_medians['Monetary']:.2f} GBP.",
        "",
    ]
    for _, row in interpretation.iterrows():
        interpretation_notes.append(
            f"- **Cụm {int(row['cluster'])}** ({int(row['customers']):,} khách): "
            f"Recency trung vị {row['Recency_median']:.2f} ngày ({row['Recency_vs_sample_median']}), "
            f"Frequency {row['Frequency_median']:.2f} ({row['Frequency_vs_sample_median']}), "
            f"Monetary {row['Monetary_median']:.2f} GBP ({row['Monetary_vs_sample_median']}); "
            f"tổng Monetary {row['Monetary_sum']:.2f} GBP."
        )
    interpretation_notes.extend([
        "",
        "## Giới hạn",
        "",
        "Đây là mô tả trên mẫu cố định, không phải nhãn chuẩn hay bằng chứng nhân quả; cần kiểm tra ý nghĩa kinh doanh và xác nhận thêm trên toàn bộ dữ liệu.",
    ])
    (TABLES / "cluster_interpretation.md").write_text("\n".join(interpretation_notes) + "\n", encoding="utf-8")

    # Regenerate the selected-profile chart so it follows the final model rather
    # than the earlier StandardScaler sweep.
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    for ax, feature in zip(axes, FEATURES):
        cluster_ids = sorted(selected_sample["cluster"].unique())
        values = [selected_sample.loc[selected_sample["cluster"] == cluster, feature].values
                  for cluster in cluster_ids]
        ax.boxplot(values, tick_labels=[str(cluster) for cluster in cluster_ids], showfliers=False)
        ax.set_title(f"{feature} theo cụm")
        ax.set_xlabel("Cụm")
        ax.set_ylabel(feature)
    fig.suptitle("Hồ sơ RFM theo cụm – K-Means RobustScaler (k=2)")
    fig.tight_layout()
    fig.savefig(FIGURES / "08_selected_cluster_rfm_profiles.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    legacy_labels_path = TABLES / "customer_clusters_sample.csv"
    if legacy_labels_path.is_file():
        legacy = pd.read_csv(legacy_labels_path)
        if "CustomerID" in legacy.columns:
            legacy = legacy.drop(columns=["cluster"], errors="ignore").merge(
                sample[["CustomerID"]].assign(cluster=selected_labels), on="CustomerID", how="left", validate="one_to_one"
            )
            legacy.to_csv(legacy_labels_path, index=False, encoding="utf-8-sig")
    stability_min_ari = float(robust_stability["min_pairwise_ari"].min())
    stability_silhouette_range = float(robust_stability["silhouette"].max() - robust_stability["silhouette"].min())
    stability_inertia_range = float(robust_stability["inertia"].max() - robust_stability["inertia"].min())
    selected = pd.DataFrame([{
        "model": "KMeans", "scaler": "RobustScaler", "k": 2, "init": "k-means++", "n_init": 20,
        "random_state": SEED, "sample_n": len(sample), "sampling": "Fixed 2,000 CustomerID sample; random_state=42",
        "preprocessing": "log1p(Recency, Frequency, Monetary) -> RobustScaler fit on fixed sample",
        "silhouette": chosen["silhouette"], "davies_bouldin": chosen["davies_bouldin"],
        "calinski_harabasz": chosen["calinski_harabasz"], "noise_points": 0, "noise_percent": 0.0,
        "seed_stability_seeds": ",".join(map(str, stability_seeds)), "seed_stability_min_pairwise_ari": stability_min_ari,
        "seed_silhouette_range": stability_silhouette_range, "seed_inertia_range": stability_inertia_range,
        "decision": "Chọn RobustScaler k=2 theo quy tắc Silhouette cao nhất và noise <=20%; EXP-035 cho Silhouette/DBI/CHI tốt hơn StandardScaler cùng k. Độ ổn định qua 5 seed được lưu riêng.",
        "limitations": "Đánh giá không giám sát trên mẫu cố định, không có nhãn chuẩn/test split; kết quả chưa đại diện toàn bộ khách hàng. Diễn giải hồ sơ theo nhãn RobustScaler.",
    }])
    selected.to_csv(TABLES / "selected_clustering_model.csv", index=False, encoding="utf-8-sig")

    print("Wrote", TABLES / "exp036_dbscan_multi_metrics.csv")
    print("Wrote", TABLES / "exp036_ward_multi_metrics.csv")
    print("Wrote", TABLES / "exp036_all_algorithms_multi_metrics.csv")
    print("Wrote", TABLES / "model_decision_exp034_exp036.csv")
    print("Wrote", TABLES / "selected_clustering_model.csv")
    print("Wrote", TABLES / "exp036_robust_stability.csv")
    print("Wrote", TABLES / "selected_model_cluster_profiles.csv")
    print("Wrote", TABLES / "selected_model_customer_labels.csv")
    if legacy_labels_path.is_file():
        print("Updated", legacy_labels_path)


if __name__ == "__main__":
    main()
