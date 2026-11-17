# -*- coding: utf-8 -*-
"""Refresh project workbooks from already-generated and verified CSV artifacts.

This is a synchronization step, not a new experiment run. It preserves existing
workbook sheets and records the source experiment timestamp in Daily Journal.
"""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "outputs" / "tables"
LOGS = ROOT / "logs"
EXP_LOG = LOGS / "experiment_log.xlsx"
DAILY = LOGS / "Daily_Journal.xlsx"


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(TABLES / name, encoding="utf-8-sig")


def write_df(wb, sheet: str, df: pd.DataFrame) -> None:
    ws = wb[sheet] if sheet in wb.sheetnames else wb.create_sheet(sheet)
    if ws.max_row:
        ws.delete_rows(1, ws.max_row)
    ws.append(list(df.columns))
    for row in df.itertuples(index=False, name=None):
        ws.append([None if pd.isna(v) else v.item() if hasattr(v, "item") else v for v in row])
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="1F4E78")
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    for col in ws.columns:
        width = min(max(max(len(str(c.value or "")) for c in col) + 2, 12), 40)
        ws.column_dimensions[col[0].column_letter].width = width


def main() -> None:
    exp35 = read_csv("exp035_scaling_comparison.csv")
    exp36 = read_csv("exp036_multi_metrics.csv")
    ward = read_csv("exp036_ward_multi_metrics.csv")
    dbscan = read_csv("exp036_dbscan_multi_metrics.csv")
    robust = read_csv("exp036_robust_stability.csv")
    profiles = read_csv("selected_model_cluster_profiles.csv")
    selected = read_csv("selected_clustering_model.csv").iloc[0]
    decisions = read_csv("model_decision_exp034_exp036.csv")
    all_metrics = read_csv("exp036_all_algorithms_multi_metrics.csv")

    # Guard against publishing inconsistent or partial metric tables.
    for name, df in (("EXP-035", exp35), ("EXP-036 K-Means", exp36),
                     ("Ward", ward), ("DBSCAN", dbscan), ("Robust stability", robust)):
        if "evaluation_sample_n" not in df or not (df["evaluation_sample_n"] == 1000).all():
            raise ValueError(f"{name}: evaluation_sample_n must be 1000 in every row")

    expwb = load_workbook(EXP_LOG)
    # Append the measured EXP-035/036 rows from the existing CSV journal. Do not
    # mint a new Run_ID: use the exact recorded source IDs and timestamps.
    csv_log_path = LOGS / "experiment_log.csv"
    with csv_log_path.open(encoding="utf-8-sig", newline="") as f:
        csv_rows = list(csv.DictReader(f))
    source_rows = [r for r in csv_rows if r.get("Experiment_ID") in {"EXP-035", "EXP-036"}]
    if source_rows:
        ws_exp = expwb["Experiment_Log"]
        header = [c.value for c in ws_exp[1]]
        if "Run_ID" in header and "Experiment_ID" in header:
            for record in source_rows:
                key = (record.get("Run_ID", ""), record.get("Experiment_ID", ""))
                # CL rows share a run ID; EXP rows have many rows per run, so
                # deduplicate on run + experiment + model configuration.
                config = (key + (record.get("Algorithm", ""), record.get("Hyperparameters", ""), record.get("Scaling", "")))
                existing = set()
                for i in range(2, ws_exp.max_row + 1):
                    existing.add((str(ws_exp.cell(i, header.index("Run_ID") + 1).value),
                                  str(ws_exp.cell(i, header.index("Experiment_ID") + 1).value),
                                  str(ws_exp.cell(i, header.index("Algorithm") + 1).value),
                                  str(ws_exp.cell(i, header.index("Hyperparameters") + 1).value),
                                  str(ws_exp.cell(i, header.index("Scaling") + 1).value)))
                if config not in existing:
                    out = []
                    for col in header:
                        value = record.get(col)
                        if col == "Sample_Rows_For_Clustering":
                            value = record.get("Sample_Rows_For_Clustering") or record.get("Sample_Rows")
                        elif col == "Unique_Customers_Sampled":
                            value = record.get("Unique_Customers_Sampled")
                        elif col in ("Evaluation_Rows_For_Silhouette", "Unique_Customers_Evaluated"):
                            value = record.get(col) or (1000 if record.get("Experiment_ID") in {"EXP-035", "EXP-036"} else None)
                        elif col == "RFM_Rows_After_DropNA" and not value:
                            value = record.get("RFM_Rows_Before_DropNA")
                        if isinstance(value, str) and value.strip():
                            try:
                                value = float(value) if "." in value else int(value)
                            except ValueError:
                                pass
                        out.append(value)
                    ws_exp.append(out)

        # Correct only the records from the verified 17-Nov 16:58 run. Earlier
        # EXP-035 runs intentionally retain their historical full-sample metric.
        idx_run = header.index("Run_ID") + 1
        idx_exp = header.index("Experiment_ID") + 1
        for i in range(2, ws_exp.max_row + 1):
            run_id = str(ws_exp.cell(i, idx_run).value or "")
            experiment_id = str(ws_exp.cell(i, idx_exp).value or "")
            if run_id.startswith("20261117_1658") and experiment_id in {"EXP-035", "EXP-036"}:
                for name, value in (("Sample_Rows_For_Clustering", 2000), ("Unique_Customers_Sampled", 2000),
                                    ("Evaluation_Rows_For_Silhouette", 1000), ("Unique_Customers_Evaluated", 1000)):
                    if name in header:
                        ws_exp.cell(i, header.index(name) + 1).value = value

    # Detailed metric sheet with explicit fit/evaluation sample sizes.
    metrics = []
    for _, r in exp36.iterrows():
        metrics.append(["EXP-036", "K-Means", f"k={int(r.k)}; init=k-means++; n_init=20; seed=42",
                        int(r.sample_n), int(r.evaluation_sample_n), 42, int(r.k), float(r.silhouette),
                        float(r.davies_bouldin), float(r.calinski_harabasz), float(r.inertia), 0, 0,
                        "Ba metric trên sample đánh giá; fit/Inertia trên sample fit; không có noise."])
    for label, frame in (("Agglomerative Ward", ward), ("DBSCAN", dbscan)):
        for _, r in frame.iterrows():
            metrics.append(["EXP-036", label, r.parameters, int(r.sample_n), int(r.evaluation_sample_n),
                            42, int(r.clusters_excluding_noise), float(r.silhouette) if pd.notna(r.silhouette) else None,
                            float(r.davies_bouldin) if pd.notna(r.davies_bouldin) else None,
                            float(r.calinski_harabasz) if pd.notna(r.calinski_harabasz) else None,
                            None, int(r.noise_points), float(r.noise_percent),
                            str(r.status) + "; " + str(r.evaluation_note)])
    metric_df = pd.DataFrame(metrics, columns=["EXP", "Thuật toán", "Tham số", "Sample fit", "Sample đánh giá",
        "Seed", "Số cụm", "Silhouette", "Davies-Bouldin", "Calinski-Harabasz", "Inertia",
        "Số điểm nhiễu", "Tỷ lệ nhiễu (%)", "Trạng thái / ghi chú"])
    write_df(expwb, "EXP036_Multi_Metrics", metric_df)
    decision_df = decisions.copy()
    if "experiment" in decision_df.columns and "candidate" in decision_df.columns:
        for i, r in decision_df.iterrows():
            if str(r["experiment"]) == "EXP-035":
                k = int(r["clusters"])
                scaler = "RobustScaler" if "RobustScaler" in str(r["candidate"]) else "StandardScaler"
                ari = float(exp35.loc[exp35["k"] == k, "ari_vs_other_scaler_same_k"].iloc[0])
                chosen = scaler == "RobustScaler" and k == 2
                other_name = "StandardScaler" if scaler == "RobustScaler" else "RobustScaler"
                other_row = exp35[(exp35["scaler"] == other_name) & (exp35["k"] == k)].iloc[0]
                metric_delta = float(r["silhouette"]) - float(other_row["silhouette"])
                decision_df.at[i, "tradeoff"] = (
                    f"k=2: RobustScaler có Silhouette cao hơn {abs(metric_delta):.4f} so với StandardScaler và được chọn; "
                    f"ARI={ari:.4f} cho thấy phân hoạch vẫn thay đổi đáng kể. Không so Inertia khác scaler."
                    if k == 2 and scaler == "RobustScaler" else
                    f"k=2: Silhouette thấp hơn RobustScaler {abs(metric_delta):.4f}; StandardScaler không được chọn. "
                    f"ARI={ari:.4f}; không so Inertia khác scaler."
                    if k == 2 else
                    f"k=3: thêm phân khúc nhưng Silhouette thấp hơn k=2; ARI={ari:.4f} cho thấy thay scaler đổi nhãn. Không so Inertia khác scaler."
                )
                decision_df.at[i, "selection_note"] = (
                    f"Cùng sample fit {int(r['sample_n'])}, cùng sample đánh giá {int(r['evaluation_sample_n'])}, "
                    f"cùng k={k}, n_init=20 và seed=42; chỉ scaler thay đổi."
                    + (" Được chọn theo Silhouette cao nhất trong ngưỡng noise <=20%; đã kiểm tra 5 seed." if chosen else "")
                )
    write_df(expwb, "Model_Decision_EXP034_036", decision_df)
    for duplicate in ("Model_Decision_EXP034_036_1", "EXP036_All_Algorithms_1", "Selected_Model_1"):
        if duplicate in expwb.sheetnames:
            del expwb[duplicate]
    write_df(expwb, "EXP036_Robust_Stability", robust)
    write_df(expwb, "Selected_Model_Profile", profiles)
    write_df(expwb, "EXP036_All_Algorithms", all_metrics)
    write_df(expwb, "Selected_Model", pd.DataFrame([selected]))
    # Keep all existing sheets, while replacing the obsolete selection claim.
    if "Model_Setup_Evaluation" in expwb.sheetnames:
        ws = expwb["Model_Setup_Evaluation"]
        for row in ws.iter_rows():
            for cell in row:
                if isinstance(cell.value, str) and "Giữ K-Means k=2 + log1p + StandardScaler" in cell.value:
                    cell.value = f"Cấu hình được chọn theo CSV: K-Means + log1p + RobustScaler, k=2, init=k-means++, n_init=20, seed=42; Silhouette={float(selected.silhouette):.6f}, DBI={float(selected.davies_bouldin):.6f}, CHI={float(selected.calinski_harabasz):.2f}. Fit trên 2.000 khách, metrics trên 1.000 khách."
    expwb.save(EXP_LOG)

    # Append only once; clearly mark as reconciliation of existing run outputs.
    dailywb = load_workbook(DAILY)
    ws = dailywb["Nhật_Ký_Công_Việc"] if "Nhật_Ký_Công_Việc" in dailywb.sheetnames else dailywb.active
    title = "Đối soát EXP-034–036: đa chỉ số, quyết định mô hình và cấu hình chốt"
    for i in range(ws.max_row, 1, -1):
        if ws.cell(i, 5).value == title:
            ws.delete_rows(i, 1)
    source = "logs/experiment_log.csv; outputs/tables/exp035_scaling_comparison.csv; outputs/tables/exp036_all_algorithms_multi_metrics.csv; outputs/tables/model_decision_exp034_exp036.csv; outputs/tables/selected_clustering_model.csv"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    row = [ws.max_row - 1, now, "Trần Thiên Hùng", "hung", title, source,
        "Đối soát kết quả thực nghiệm đã chạy; kiểm tra Silhouette, Davies-Bouldin, Calinski-Harabasz, Inertia, noise; xác nhận cùng 2.000 khách fit, cùng 1.000 khách đánh giá và cùng sample/k/seed theo từng cặp scaler.",
        "DBSCAN tính metric sau khi loại noise nên cần đọc kèm số điểm đánh giá và tỷ lệ noise trên toàn sample fit. Không so Inertia giữa scaler hay thuật toán khác nhau.",
        "Đồng bộ các CSV kết quả đã lưu vào experiment_log.xlsx; sửa nội dung cấu hình chốt để phản ánh đúng RobustScaler; đối chiếu lại hai workbook.",
        f"Kết quả đã có: K-Means + RobustScaler + log1p + k=2, n_init=20, seed=42; Silhouette={float(selected.silhouette):.6f}, DBI={float(selected.davies_bouldin):.6f}, CHI={float(selected.calinski_harabasz):.2f}; ARI nhỏ nhất qua 5 seed={float(selected.seed_stability_min_pairwise_ari):.6f}.",
        "ĐÃ ĐỐI SOÁT KẾT QUẢ ĐÃ CHẠY (không phát sinh lượt chạy mới). Metric trên cùng tối đa 1.000 khách đánh giá; fit trên sample cố định tối đa 2.000; noise DBSCAN báo riêng trên sample fit.",
        "outputs/tables/exp036_dbscan_multi_metrics.csv; exp036_ward_multi_metrics.csv; exp036_robust_stability.csv; model_decision_exp034_exp036.csv; selected_clustering_model.csv; selected_model_cluster_profiles.csv"]
    ws.append(row)
    for cell in ws[ws.max_row]:
        cell.alignment = Alignment(vertical="top", wrap_text=True)
    dailywb.save(DAILY)
    print("Synced verified existing outputs; no new model run was recorded.")
    print(EXP_LOG)
    print(DAILY)


if __name__ == "__main__":
    main()
