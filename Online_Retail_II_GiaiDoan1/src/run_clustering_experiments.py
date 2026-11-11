"""Run reproducible RFM clustering experiments and save tables/figures/logs."""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
import uuid

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering, DBSCAN, KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "outputs" / "tables"
FIGURES = ROOT / "outputs" / "figures"
LOG = ROOT / "logs" / "experiment_log.csv"
RFM_FILE = TABLES / "rfm_table.csv"
FEATURES = ["Recency", "Frequency", "Monetary"]
SEED = 42
SAMPLE_SIZE = 2000
SILHOUETTE_SAMPLE_SIZE = 1000


def append_experiment_log(new_rows: pd.DataFrame, log_path: Path) -> None:
    """Append new experiment rows while preserving all previous runs.

    Older versions stored the sampled row count in `Rows_After_Preprocessing`.
    Migrate that column to the explicit `Sample_Rows_For_Clustering` name.
    """
    log_path.parent.mkdir(parents=True, exist_ok=True)

    if log_path.exists():
        try:
            old_log = pd.read_csv(log_path)
        except Exception as exc:
            # Fail safely: never replace a history file that cannot be read.
            raise RuntimeError(
                f"Không đọc được nhật ký cũ {log_path}; đã dừng để tránh ghi đè/mất dữ liệu."
            ) from exc

        if "Rows_After_Preprocessing" in old_log.columns:
            old_sample_rows = old_log.pop("Rows_After_Preprocessing")
            if "Sample_Rows_For_Clustering" in old_log.columns:
                old_log["Sample_Rows_For_Clustering"] = (
                    old_log["Sample_Rows_For_Clustering"].fillna(old_sample_rows)
                )
            else:
                # In the previous script this field was assigned `sample_n`.
                old_log["Sample_Rows_For_Clustering"] = old_sample_rows

        if "Run_ID" not in old_log.columns:
            old_log.insert(0, "Run_ID", "LEGACY_UNKNOWN")
        else:
            old_log["Run_ID"] = old_log["Run_ID"].fillna("LEGACY_UNKNOWN")
    else:
        old_log = pd.DataFrame()

    combined = pd.concat([old_log, new_rows], ignore_index=True, sort=False)

    # Write to a temporary file first, then replace the log atomically.
    temp_path = log_path.with_name(f"{log_path.stem}.tmp{log_path.suffix}")
    try:
        combined.to_csv(temp_path, index=False, encoding="utf-8-sig")
        temp_path.replace(log_path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def main() -> None:
    run_started_at = datetime.now().astimezone()
    run_id = f"{run_started_at.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    if not RFM_FILE.exists():
        raise FileNotFoundError(f"Không tìm thấy {RFM_FILE}; hãy chạy Notebook 01 trước.")

    rfm = pd.read_csv(RFM_FILE)
    missing = sorted(set(FEATURES) - set(rfm.columns))
    if missing:
        raise ValueError(f"Thiếu các đặc trưng RFM bắt buộc: {missing}")

    rfm_rows_before_dropna = len(rfm)
    rfm = rfm.dropna(subset=FEATURES).copy()
    rfm_rows_after_dropna = len(rfm)
    unique_customers_after_cleaning = (
        int(rfm["CustomerID"].nunique()) if "CustomerID" in rfm.columns else rfm_rows_after_dropna
    )
    if (rfm[FEATURES] < 0).any().any():
        raise ValueError("RFM có giá trị âm; kiểm tra lại quy tắc tạo bảng RFM trước khi log1p.")

    # Fixed sample: every candidate model is evaluated on exactly the same customers.
    sample_n = min(SAMPLE_SIZE, len(rfm))
    sample = rfm.sample(n=sample_n, random_state=SEED).reset_index(drop=True)
    transformed = np.log1p(sample[FEATURES].astype(float))
    scaler = StandardScaler()
    X = scaler.fit_transform(transformed)
    eval_n = min(SILHOUETTE_SAMPLE_SIZE, sample_n)
    sampled_unique_customers = (
        int(sample["CustomerID"].nunique()) if "CustomerID" in sample.columns else sample_n
    )
    evaluation_sample = sample.iloc[:eval_n]
    evaluated_unique_customers = (
        int(evaluation_sample["CustomerID"].nunique())
        if "CustomerID" in evaluation_sample.columns else eval_n
    )
    X_eval = X[:eval_n]
    pd.DataFrame({"feature": FEATURES, "mean_after_log1p": transformed.mean().values,
                  "std_after_log1p": transformed.std(ddof=0).values,
                  "mean_after_scaling": X.mean(axis=0), "std_after_scaling": X.std(axis=0)}).to_csv(
        TABLES / "clustering_preprocessing.csv", index=False, encoding="utf-8-sig")

    rows: list[dict] = []
    def record(name: str, labels: np.ndarray, model: object, params: str) -> None:
        clusters = sorted(set(labels) - {-1})
        noise = int(np.sum(labels == -1))
        valid = len(clusters) >= 2 and (len(labels) - noise) > len(clusters)
        # Evaluate on the exact same first eval_n sampled customers for every model.
        eval_labels = labels[:eval_n]
        eval_non_noise = eval_labels != -1
        eval_classes = np.unique(eval_labels[eval_non_noise])
        score = silhouette_score(X_eval[eval_non_noise], eval_labels[eval_non_noise]) \
            if len(eval_classes) >= 2 and eval_non_noise.sum() > len(eval_classes) else np.nan
        sizes = pd.Series(labels).value_counts().sort_index()
        rows.append({"model": name, "parameters": params, "clusters_excluding_noise": len(clusters),
                     "noise_points": noise, "noise_percent": noise / len(labels) * 100,
                     "silhouette_excluding_noise": score, "inertia": getattr(model, "inertia_", np.nan),
                     "cluster_sizes": json.dumps({str(k): int(v) for k, v in sizes.items()}),
                     "evaluated_customers": len(labels),
                     "evaluation_note": "Silhouette trên điểm không nhiễu; không tính được nếu <2 cụm." if valid else
                     "Không có ít nhất 2 cụm hợp lệ; silhouette không xác định."})

    # Baseline is pre-declared: K-Means k=3, fixed seed, k-means++.
    baseline = KMeans(n_clusters=3, init="k-means++", n_init=20, random_state=SEED)
    record("KMeans_baseline", baseline.fit_predict(X), baseline,
           "n_clusters=3; init=k-means++; n_init=20; random_state=42")

    # K-Means parameter selection on candidate k values, same sample and features.
    for k in range(2, 9):
        model = KMeans(n_clusters=k, init="k-means++", n_init=20, random_state=SEED)
        record("KMeans_tuned", model.fit_predict(X), model,
               f"n_clusters={k}; init=k-means++; n_init=20; random_state=42")

    # Ward hierarchical clustering; candidate cluster counts match K-Means search.
    for k in range(2, 9):
        model = AgglomerativeClustering(n_clusters=k, linkage="ward")
        record("Hierarchical_Ward", model.fit_predict(X), model, f"n_clusters={k}; linkage=ward")

    # DBSCAN grid; preserve noise as label -1 and never silently treat it as a cluster.
    for eps in (0.25, 0.35, 0.45, 0.6, 0.8, 1.0):
        for min_samples in (5, 10, 20):
            model = DBSCAN(eps=eps, min_samples=min_samples, n_jobs=-1)
            record("DBSCAN", model.fit_predict(X), model,
                   f"eps={eps}; min_samples={min_samples}; metric=euclidean")

    scores = pd.DataFrame(rows)
    scores.to_csv(TABLES / "clustering_model_comparison.csv", index=False, encoding="utf-8-sig")
    usable = scores[(scores["clusters_excluding_noise"] >= 2) & scores["silhouette_excluding_noise"].notna()]
    if usable.empty:
        raise RuntimeError("Không mô hình nào tạo ít nhất 2 cụm hợp lệ; xem clustering_model_comparison.csv.")

    # Select using silhouette only among solutions with 2..8 clusters and <=20% noise.
    eligible = usable[usable["clusters_excluding_noise"].between(2, 8) & (usable["noise_percent"] <= 20)]
    selection_pool = eligible if not eligible.empty else usable[usable["clusters_excluding_noise"].between(2, 8)]
    if selection_pool.empty:
        selection_pool = usable
    winner_row = selection_pool.sort_values(
        ["silhouette_excluding_noise", "noise_percent"], ascending=[False, True]).iloc[0]
    winner_name = str(winner_row["model"])
    # Re-identify duplicate configurations via model and the exact serialized parameters.
    if winner_name == "KMeans_tuned":
        k = int(winner_row["parameters"].split("n_clusters=")[1].split(";")[0])
        model = KMeans(n_clusters=k, init="k-means++", n_init=20, random_state=SEED)
        labels = model.fit_predict(X)
    elif winner_name == "Hierarchical_Ward":
        k = int(winner_row["parameters"].split("n_clusters=")[1].split(";")[0])
        model = AgglomerativeClustering(n_clusters=k, linkage="ward")
        labels = model.fit_predict(X)
    elif winner_name == "DBSCAN":
        parts = dict(item.split("=") for item in str(winner_row["parameters"]).split("; "))
        model = DBSCAN(eps=float(parts["eps"]), min_samples=int(parts["min_samples"]), n_jobs=-1)
        labels = model.fit_predict(X)
    else:
        model = KMeans(n_clusters=3, init="k-means++", n_init=20, random_state=SEED)
        labels = model.fit_predict(X)

    sample["cluster"] = labels
    sample.to_csv(TABLES / "customer_clusters_sample.csv", index=False, encoding="utf-8-sig")
    valid_customer = sample[sample["cluster"] != -1]
    profile = valid_customer.groupby("cluster").agg(
        customers=("CustomerID", "nunique") if "CustomerID" in valid_customer else ("cluster", "size"),
        Recency_median=("Recency", "median"), Recency_mean=("Recency", "mean"),
        Frequency_median=("Frequency", "median"), Frequency_mean=("Frequency", "mean"),
        Monetary_median=("Monetary", "median"), Monetary_mean=("Monetary", "mean"),
        Monetary_sum=("Monetary", "sum"),
    ).reset_index()
    profile.to_csv(TABLES / "selected_model_cluster_profiles.csv", index=False, encoding="utf-8-sig")

    overall_medians = sample[FEATURES].median()
    interpretation = profile.copy()
    for feature in FEATURES:
        interpretation[f"{feature}_vs_sample_median"] = np.where(
            interpretation[f"{feature}_median"] < overall_medians[feature], "thấp hơn trung vị mẫu",
            np.where(interpretation[f"{feature}_median"] > overall_medians[feature], "cao hơn trung vị mẫu",
                     "bằng trung vị mẫu"))
    interpretation.to_csv(TABLES / "cluster_interpretation.csv", index=False, encoding="utf-8-sig")
    notes = [
        "# Diễn giải cụm từ mẫu RFM",
        "",
        f"Mô hình được chọn theo silhouette: **{winner_name}** ({winner_row['parameters']}).",
        f"Silhouette trên tập đánh giá cố định: **{winner_row['silhouette_excluding_noise']:.4f}**; "
        f"{int(winner_row['clusters_excluding_noise'])} cụm; noise DBSCAN {winner_row['noise_percent']:.2f}%.",
        f"Trung vị toàn mẫu: Recency={overall_medians['Recency']:.2f} ngày, "
        f"Frequency={overall_medians['Frequency']:.2f} hóa đơn, "
        f"Monetary={overall_medians['Monetary']:.2f} GBP.",
        "",
        "Các mô tả dưới đây so sánh trung vị của từng cụm với trung vị mẫu chung; đây là diễn giải mô tả, "
        "không phải nhãn chân lý hay bằng chứng nhân quả.",
        "",
    ]
    for _, row in interpretation.iterrows():
        notes.append(
            f"- **Cụm {int(row['cluster'])}** ({int(row['customers']):,} khách hàng trong mẫu): "
            f"Recency {row['Recency_median']:.2f} ngày ({row['Recency_vs_sample_median']}), "
            f"Frequency {row['Frequency_median']:.2f} hóa đơn ({row['Frequency_vs_sample_median']}), "
            f"Monetary {row['Monetary_median']:.2f} GBP ({row['Monetary_vs_sample_median']}); "
            f"doanh thu gộp trong cụm {row['Monetary_sum']:.2f} GBP."
        )
    if winner_row["noise_percent"] > 0:
        notes.extend(["", f"DBSCAN gán {winner_row['noise_percent']:.2f}% khách hàng mẫu là nhiễu; "
                      "những điểm này không thuộc hồ sơ cụm ở trên."])
    notes.extend(["", "## Giới hạn", "",
                  "Kết quả và hồ sơ chỉ đại diện cho mẫu ngẫu nhiên cố định tối đa 2.000 khách hàng. "
                  "Cần kiểm tra độ ổn định trên nhiều seed/bootstrap và xem ý nghĩa kinh doanh trước khi dùng làm kết luận cuối."])
    (TABLES / "cluster_interpretation.md").write_text("\n".join(notes) + "\n", encoding="utf-8")

    # Explain the selected result with robust medians and full-customer labels where model supports predict.
    model_spec = str(winner_row["parameters"])
    selection = pd.DataFrame([{
        "selected_model": winner_name, "parameters": model_spec,
        "selection_metric": "silhouette_excluding_noise",
        "selection_score": float(winner_row["silhouette_excluding_noise"]),
        "clusters_excluding_noise": int(winner_row["clusters_excluding_noise"]),
        "noise_percent": float(winner_row["noise_percent"]), "sample_size": sample_n,
        "sampling": f"Simple random sample without replacement; random_state={SEED}",
        "preprocessing": "log1p(Recency, Frequency, Monetary), then StandardScaler fit on the fixed sample",
        "selection_rule": "Highest silhouette among 2-8 clusters and <=20% noise when available; otherwise relax noise threshold, then cluster-count range.",
        "caveat": "Exploratory model selection on a fixed evaluation sample; no supervised target/test split. Reassess stability with repeated seeds/bootstraps before final claims."
    }])
    selection.to_csv(TABLES / "selected_clustering_model.csv", index=False, encoding="utf-8-sig")

    # Stable clusters versus noise; selected sample only.
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    for ax, feature in zip(axes, FEATURES):
        data = [valid_customer.loc[valid_customer.cluster == c, feature].values
                for c in sorted(valid_customer.cluster.unique())]
        labels_order = [str(c) for c in sorted(valid_customer.cluster.unique())]
        if data:
            ax.boxplot(data, tick_labels=labels_order, showfliers=False)
        ax.set_title(f"{feature} theo cụm")
        ax.set_xlabel("Cụm")
        ax.set_ylabel(feature)
    fig.suptitle(f"Hồ sơ RFM theo cụm – {winner_name}")
    fig.tight_layout()
    fig.savefig(FIGURES / "08_selected_cluster_rfm_profiles.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    # Comparison plot includes only valid silhouettes; keeps model families/configs explicit.
    plot = usable.sort_values("silhouette_excluding_noise", ascending=True).tail(20)
    fig, ax = plt.subplots(figsize=(10, max(5, len(plot) * 0.28)))
    ax.barh(plot.apply(lambda x: f"{x['model']} | {x['parameters']}", axis=1),
            plot["silhouette_excluding_noise"], color="#3478a8")
    ax.set_xlabel("Silhouette (điểm không nhiễu)")
    ax.set_title("So sánh tối đa 20 cấu hình có silhouette hợp lệ")
    fig.tight_layout()
    fig.savefig(FIGURES / "09_clustering_silhouette_comparison.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    log_rows = []
    for i, row in scores.iterrows():
        log_rows.append({
            "Run_ID": run_id,
            "Experiment_ID": f"CL-{i+1:03d}",
            "Run_Started_At": run_started_at.isoformat(timespec="seconds"),
            "Date": run_started_at.date().isoformat(),
            "Research_Question": "Các phương pháp phân cụm phân biệt hành vi khách hàng RFM ra sao?",
            "Dataset_Version": "Online Retail II UCI; outputs/tables/rfm_table.csv",
            "RFM_Rows_Before_DropNA": rfm_rows_before_dropna,
            "RFM_Rows_After_DropNA": rfm_rows_after_dropna,
            "Unique_Customers_After_RFM_Cleaning": unique_customers_after_cleaning,
            "Sample_Rows_For_Clustering": sample_n,
            "Unique_Customers_Sampled": sampled_unique_customers,
            "Evaluation_Rows_For_Silhouette": eval_n,
            "Unique_Customers_Evaluated": evaluated_unique_customers,
            "Feature_Set": "Recency, Frequency, Monetary",
            "Algorithm": row["model"],
            "Hyperparameters": row["parameters"],
            "Validation_Strategy": (
                f"Mẫu ngẫu nhiên cố định n={sample_n}; cùng {eval_n} dòng đánh giá; "
                f"seed={SEED}; silhouette không giám sát"
            ),
            "Scaling": "log1p + StandardScaler fit trên mẫu cố định",
            "Metric_Name": "Silhouette (excluding DBSCAN noise); inertia for KMeans",
            "Metric_Value": row["silhouette_excluding_noise"],
            "Random_State": SEED,
            "Observation": (
                f"k={row['clusters_excluding_noise']}; "
                f"noise={row['noise_percent']:.2f}%; sizes={row['cluster_sizes']}"
            ),
            "Next_Action": (
                "So sánh hồ sơ cụm; đánh giá độ ổn định bằng nhiều seed/bootstraps "
                "trước khi kết luận cuối."
            ),
        })

    append_experiment_log(pd.DataFrame(log_rows), LOG)
    print(f"Đã lưu {len(scores)} cấu hình, mô hình chọn: {winner_name}")
    print(f"Silhouette={winner_row['silhouette_excluding_noise']:.4f}; số cụm={int(winner_row['clusters_excluding_noise'])}; noise={winner_row['noise_percent']:.2f}%")
    print(f"Bảng: {TABLES}; hình: {FIGURES}; experiment log: {LOG}")


if __name__ == "__main__":
    main()
