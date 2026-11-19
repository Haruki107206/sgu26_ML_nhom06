from pathlib import Path
import argparse
import json

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, RobustScaler

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ["Recency", "Frequency", "Monetary"]


def run(source):
    data = pd.read_csv(source)
    x = data[FEATURES].astype(float)
    if data.CustomerID.isna().any() or not data.CustomerID.is_unique or not np.isfinite(x).all().all() or (x < 0).any().any() or x.Monetary.sum() <= 0:
        raise ValueError("Bảng RFM có ID hoặc giá trị RFM không hợp lệ.")
    model = make_pipeline(FunctionTransformer(np.log1p), RobustScaler(),
                          KMeans(n_clusters=2, init="k-means++", n_init=20, random_state=42))
    raw = model.fit_predict(x)
    order = x.assign(raw=raw).groupby("raw").Monetary.median().sort_values().index
    mapping = {int(label): rank for rank, label in enumerate(order)}
    data["cluster"] = pd.Series(raw).map(mapping).to_numpy()
    assert len(mapping) == 2
    profiles = data.groupby("cluster").agg(customers=("CustomerID", "size"),
        Recency_median=("Recency", "median"), Frequency_median=("Frequency", "median"),
        Monetary_median=("Monetary", "median"), Monetary_sum=("Monetary", "sum")).reset_index()
    profiles["customer_pct"] = profiles.customers / len(data) * 100
    profiles["monetary_pct"] = profiles.Monetary_sum / data.Monetary.sum() * 100
    pca = PCA(n_components=2)
    data[["PC1", "PC2"]] = pca.fit_transform(model[:-1].transform(x))
    centers = pca.transform(model[-1].cluster_centers_)
    tables = ROOT / "outputs/tables"
    figures = ROOT / "outputs/figures"
    models = ROOT / "models"
    for directory in (tables, figures, models):
        directory.mkdir(parents=True, exist_ok=True)
    data.to_csv(tables / "customer_clusters_full.csv", index=False)
    profiles.to_csv(tables / "final_cluster_profiles.csv", index=False)
    joblib.dump({"pipeline": model, "label_map": mapping}, models / "customer_clustering_pipeline.joblib")
    ratios = pca.explained_variance_ratio_
    (tables / "final_model_config.json").write_text(json.dumps(dict(
        experiment="EXP-037", source=source.name, customers=len(data), features=FEATURES,
        pipeline=["log1p", "RobustScaler", "KMeans"], k=2, init="k-means++", n_init=20,
        random_state=42, pca_variance_ratio=ratios.tolist(), label_map=mapping), indent=2))
    fig, ax = plt.subplots(figsize=(9, 6), layout="constrained")
    for label, group in data.groupby("cluster"):
        ax.scatter(group.PC1, group.PC2, s=8, alpha=.35, label=f"Cụm {label} · {len(group):,} khách")
    ax.scatter(*centers.T, marker="X", color="black", s=95, label="Tâm cụm chiếu lên PCA")
    ax.set(title="EXP-037 · Phân cụm khách hàng Online Retail II",
           xlabel=f"PC1 ({ratios[0]:.1%} phương sai)", ylabel=f"PC2 ({ratios[1]:.1%} phương sai)")
    ax.legend()
    fig.savefig(figures / "pca_2d_clusters.png", dpi=170)
    plt.close(fig)
    print(profiles.to_string(index=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("rfm", type=Path, nargs="?", default=ROOT / "outputs/tables/rfm_table.csv")
    run(parser.parse_args().rfm)

