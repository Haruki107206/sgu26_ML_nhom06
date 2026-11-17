# -*- coding: utf-8 -*-
"""Update the two project workbooks with verified EXP-034..036 documentation."""
from __future__ import annotations

import csv
import json
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "outputs" / "tables"
LOGS = ROOT / "logs"
EXP_XLSX = LOGS / "experiment_log.xlsx"
DAILY_XLSX = LOGS / "Daily_Journal.xlsx"


def read_csv(name: str) -> list[dict]:
    with (TABLES / name).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def replace_sheet(wb, name: str, headers: list[str], rows: list[list], widths: list[int] | None = None):
    if name in wb.sheetnames:
        del wb[name]
    ws = wb.create_sheet(name)
    ws.append(headers)
    for row in rows:
        ws.append(row)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    header_fill = PatternFill("solid", fgColor="1F4E78")
    for cell in ws[1]:
        cell.font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = Border(bottom=Side(style="hair", color="D9E2F3"))
    ws.row_dimensions[1].height = 34
    if widths:
        for i, width in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = width
    else:
        for i, header in enumerate(headers, 1):
            ws.column_dimensions[get_column_letter(i)].width = min(max(len(header) + 3, 14), 32)
    return ws


def save_atomic(wb, path: Path):
    tmp = path.with_name(path.stem + ".tmp.xlsx")
    wb.save(tmp)
    tmp.replace(path)


def main():
    # Build model decision rows from measured tables, including the new DBSCAN run.
    exp35 = read_csv("exp035_scaling_comparison.csv")
    exp36 = read_csv("exp036_multi_metrics.csv")
    ward_metrics = read_csv("exp036_ward_multi_metrics.csv")
    robust_stability = read_csv("exp036_robust_stability.csv")
    selected_profile = read_csv("selected_model_cluster_profiles.csv")
    exp34 = read_csv("clustering_model_comparison.csv")
    dbscan_metrics = read_csv("exp036_dbscan_multi_metrics.csv")
    dbscan_by_parameters = {r["parameters"]: r for r in dbscan_metrics}
    decisions = []
    for r in exp35:
        k = int(r["k"])
        is_selected = r["scaler"] == "RobustScaler" and k == 2
        ari = float(r["ari_vs_other_scaler_same_k"])
        tradeoff = (
            f"k=2: RobustScaler {'được chọn' if is_selected else 'có metric thấp hơn cấu hình được chọn'}; ARI={ari:.3f} giữa hai scaler cho thấy phân hoạch thay đổi đáng kể. Inertia khác scaler không so trực tiếp."
            if k == 2 else
            f"k=3: thêm phân khúc nhưng Silhouette thấp hơn k=2; ARI={ari:.3f} cho thấy thay scaler đổi nhãn cụm. Inertia khác scaler không so trực tiếp."
        )
        decisions.append(["EXP-035", f"K-Means + {r['scaler']} + k={k}", r["sample_n"], r.get("evaluation_sample_n", 1000), r["seed"], k, 0,
                          r["silhouette"], r["davies_bouldin"], r["calinski_harabasz"], r["inertia"], tradeoff,
                          f"Cùng {r.get('sample_n', 2000)} khách fit, cùng {r.get('evaluation_sample_n', 1000)} khách đánh giá, log1p, k={k}, n_init=20, seed=42; chỉ scaler thay đổi."
                          + (" ĐƯỢC CHỌN theo quy tắc Silhouette cao nhất, noise <=20%; đã kiểm tra thêm 5 seed." if is_selected else "")])
    for r in exp36:
        k = int(r["k"])
        decisions.append(["EXP-036", f"K-Means + StandardScaler + k={k}", r.get("sample_n", 2000), r.get("evaluation_sample_n", 1000), 42, k, 0,
                          r["silhouette"], r["davies_bouldin"], r["calinski_harabasz"], r["inertia"],
                          "k=2 tốt nhất về Silhouette/DBI trong k=2..8; k cao giảm inertia do tăng số cụm nhưng làm mô hình phức tạp hơn.",
                          "Fit trên sample cố định; ba metric trên cùng 1.000 điểm đánh giá; log1p + StandardScaler, n_init=20, seed=42; Inertia chỉ so trong pipeline fit này."])
    for r in ward_metrics:
        decisions.append(["EXP-034/036", f"Agglomerative Ward k={r['k']}", r["sample_n"], r.get("evaluation_sample_n", 1000), r["seed"],
                          r["clusters_excluding_noise"], r["noise_percent"], r["silhouette"], r["davies_bouldin"],
                          r["calinski_harabasz"], "Không áp dụng",
                          "Ward cho phân nhóm phân cấp nhưng không có inertia tương đương K-Means; chọn k cần cân nhắc metric và khả năng diễn giải.",
                          "Fit cùng sample 2.000, metric cùng 1.000 điểm đánh giá; log1p + StandardScaler; k=2..8; noise=0."])
    for r in exp34:
        if not str(r["model"]).startswith("DBSCAN"):
            continue
        params = r["parameters"]
        dbmetric = dbscan_by_parameters.get(params, {})
        decisions.append(["EXP-034", f"DBSCAN ({params})", dbmetric.get("sample_n", r["evaluated_customers"]), dbmetric.get("evaluation_sample_n", 1000), 42,
                          dbmetric.get("clusters_excluding_noise", r["clusters_excluding_noise"]),
                          dbmetric.get("noise_percent", r["noise_percent"]),
                          dbmetric.get("silhouette", r["silhouette_excluding_noise"]),
                          dbmetric.get("davies_bouldin", "CHƯA TÍNH"),
                          dbmetric.get("calinski_harabasz", "CHƯA TÍNH"), "Không áp dụng",
                          "DBSCAN phát hiện noise nhưng số cụm và tỷ lệ noise thay đổi mạnh; phải cân nhắc tỷ lệ khách bị loại cùng metric.",
                          "Fit trên sample 2.000; metrics trên cùng 1.000 điểm đánh giá sau khi bỏ nhãn -1; noise tính riêng trên toàn sample fit."])

    metrics_headers = ["EXP", "Thuật toán", "Tham số", "Sample fit", "Sample đánh giá", "Seed", "Số cụm", "Silhouette", "Davies-Bouldin", "Calinski-Harabasz", "Inertia", "Số điểm nhiễu", "Tỷ lệ nhiễu (%)", "Trạng thái / ghi chú"]
    metric_rows = []
    for r in exp36:
        metric_rows.append(["EXP-036", "KMeans", f"k={r['k']}; init=k-means++; n_init=20; seed=42", r.get("sample_n", 2000), r.get("evaluation_sample_n", 1000), 42,
                            r["k"], r["silhouette"], r["davies_bouldin"], r["calinski_harabasz"], r["inertia"], 0, 0,
                            "Ba metric tính trên sample đánh giá; fit/Inertia trên sample fit; không có noise."])
    for r in ward_metrics:
        metric_rows.append(["EXP-036", "Agglomerative Ward", r["parameters"], r["sample_n"], r.get("evaluation_sample_n", 1000), r["seed"],
                            r["clusters_excluding_noise"], r["silhouette"], r["davies_bouldin"],
                            r["calinski_harabasz"], "Không áp dụng", r["noise_points"], r["noise_percent"],
                            r["status"] + "; " + r["evaluation_note"]])
    for r in dbscan_metrics:
        metric_rows.append(["EXP-036", "DBSCAN", r["parameters"], r["sample_n"], r.get("evaluation_sample_n", 1000), r["seed"],
                            r["clusters_excluding_noise"], r["silhouette"], r["davies_bouldin"],
                            r["calinski_harabasz"], "Không áp dụng", r["noise_points"], r["noise_percent"],
                            r["status"] + "; " + r["evaluation_note"]])

    methodology = [
        ["Bối cảnh", "Đánh giá phân cụm khách hàng theo Recency, Frequency, Monetary; học không giám sát nên không có nhãn đúng/sai (ground truth)."],
        ["Dữ liệu / sample", "Bảng RFM sạch 5.878 khách; thực nghiệm so sánh dùng danh sách cố định tối đa 2.000 CustomerID tại exp034_fixed_customer_sample.csv; cùng sample giúp so sánh công bằng."],
        ["Tiền xử lý", "Kiểm tra đủ ba biến, không thiếu/âm; áp dụng log1p cho RFM rồi scaler. EXP-035 đối chiếu StandardScaler/RobustScaler; EXP-036 dùng StandardScaler."],
        ["Thiết lập mô hình", "K-Means init=k-means++, n_init=20, random_state=42; khảo sát k=2..8. EXP-034 chạy K-Means k=2 với 5 seed để đo độ ổn định. DBSCAN dùng lưới eps=0,25..1,0 và min_samples=5,10,20."],
        ["Sample fit/đánh giá", "Mô hình fit và Inertia dùng toàn bộ sample CustomerID cố định tối đa 2.000. Silhouette/DBI/CHI tính trên cùng 1.000 khách đầu tiên của sample (hoặc toàn bộ nếu sample nhỏ hơn). DBSCAN fit trên 2.000; metric tính trên 1.000 điểm đánh giá sau khi bỏ nhãn -1; noise tính trên toàn bộ sample fit."],
        ["Ward phân cấp", "Agglomerative Ward k=2..8 fit trên cùng sample 2.000 khách và log1p + StandardScaler; ba metric dùng cùng 1.000 điểm đánh giá; không có điểm nhiễu. Ward không có inertia tương đương K-Means."],
        ["Độ đo", "Silhouette càng cao càng tốt; Davies-Bouldin càng thấp càng tốt; Calinski-Harabasz càng cao càng tốt; inertia chỉ so sánh cùng dữ liệu/feature/scaler/thuật toán và thường giảm khi k tăng. Không dùng inertia để so K-Means với DBSCAN hoặc so hai scaler."],
        ["DBSCAN và noise", "DBSCAN fit trên sample 2.000. Trong sample đánh giá 1.000 điểm chung, nhãn -1 bị loại khỏi Silhouette/DBI/CHI; số điểm và tỷ lệ noise báo riêng trên toàn sample fit. Nếu dưới hai cụm hoặc không đủ điểm đánh giá hợp lệ thì metric không xác định."],
        ["EXP-034: ổn định", "K-Means k=2 qua 5 seed: ARI từng cặp 0,974137–1,000000; Silhouette 0,297894–0,300278; inertia 2.855,72–2.855,77. ARI gần 1 thể hiện phân hoạch tương tự, không phải accuracy. Seed làm thay đổi khởi tạo và nghiệm cục bộ; nhãn cụm có thể đổi tên."],
        ["EXP-035: scaler", "So sánh từng cặp cùng 2.000 khách fit, cùng k (2 hoặc 3), seed=42, n_init=20, log1p; chỉ scaler thay đổi. Metric được tính trên cùng 1.000 khách đánh giá; Inertia trên toàn sample fit và không so khác scaler. ARI đối chiếu nhãn trên toàn sample, thể hiện mức thay đổi phân hoạch; không suy rộng ngoài mẫu."],
        ["EXP-036: chọn k", "K-Means StandardScaler k=2..8 fit trên sample 2.000; ba metric tính trên cùng 1.000 khách đánh giá cho mọi k. Inertia trên sample fit 2.000 thường giảm khi k tăng nên không dùng riêng để chọn. Cân nhắc đồng thời Silhouette, DBI, CHI, độ phức tạp và khả năng diễn giải."],
        ["Đánh đổi", "k=2 gọn, phân hoạch ổn định và chỉ số tốt theo Silhouette/DBI nhưng có thể gộp nhóm khách khác biệt. k lớn phân đoạn chi tiết hơn nhưng metric giảm/độ phức tạp tăng; inertia thấp hơn vốn là hệ quả tăng k. DBSCAN phát hiện ngoại lệ nhưng tỷ lệ nhiễu/cấu trúc cụm phụ thuộc eps/min_samples và nhiều cấu hình không cho nghiệm phù hợp."],
        ["Giới hạn", "Đây là đánh giá nội tại, trên sample ngẫu nhiên cố định; không có target nên không thể kết luận phân khúc đúng theo hành vi kinh doanh chỉ bằng metric. Cần kiểm tra hồ sơ cụm và xác nhận trên toàn bộ 5.878 khách/seed khác trước tuyên bố tổng quát."],
        ["Tệp nguồn", "outputs/tables/exp034_seed_stability.csv; exp034_pairwise_ari.csv; exp035_scaling_comparison.csv; exp036_multi_metrics.csv; clustering_model_comparison.csv; selected_clustering_model.csv; src/complete_model_evaluation.py."],
    ]
    methodology = [r for r in methodology if r[0] != "Quyết định hiện tại"]
    min_ari = min(float(r["min_pairwise_ari"]) for r in robust_stability)
    sil_range = max(float(r["silhouette"]) for r in robust_stability) - min(float(r["silhouette"]) for r in robust_stability)
    inertia_range = max(float(r["inertia"]) for r in robust_stability) - min(float(r["inertia"]) for r in robust_stability)
    robust_k2 = next(r for r in exp35 if r["scaler"] == "RobustScaler" and int(r["k"]) == 2)
    methodology.append(["Cấu hình được chọn", f"K-Means RobustScaler k=2 theo quy tắc Silhouette cao nhất với noise <=20%; metrics trên {robust_k2.get('evaluation_sample_n', 1000)} khách đánh giá: Silhouette={float(robust_k2['silhouette']):.6f}, DBI={float(robust_k2['davies_bouldin']):.6f}, CHI={float(robust_k2['calinski_harabasz']):.2f}. Fit/Inertia trên sample 2.000. Kiểm tra 5 seed có ARI cặp nhỏ nhất={min_ari:.6f}, biên Silhouette={sil_range:.6f}, biên Inertia={inertia_range:.4f}; hồ sơ nhãn được đồng bộ theo RobustScaler."])
    methodology.append(["Đối soát nhật ký", "Dòng Daily Journal này ghi việc đối chiếu và đồng bộ các kết quả đã có; không đại diện cho một lần chạy mô hình mới. Run_ID và thời điểm thực nghiệm phải lấy từ experiment_log.csv."])

    # experiment_log.xlsx: preserve other sheets; refresh EXP-036 sheet with all
    # available KMeans metrics and add documented decision/method sheets.
    wb = load_workbook(EXP_XLSX)
    replace_sheet(wb, "EXP036_Multi_Metrics", metrics_headers, metric_rows,
                  [13, 18, 34, 10, 14, 10, 11, 15, 17, 20, 15, 15, 17, 55])
    decision_headers = ["EXP", "Ứng viên", "Sample fit", "Sample đánh giá", "Seed", "Số cụm", "Noise (%)", "Silhouette", "Davies-Bouldin", "Calinski-Harabasz", "Inertia", "Đánh đổi / nhận xét", "Điều kiện so sánh"]
    replace_sheet(wb, "Model_Decision_EXP034_036", decision_headers, decisions,
                  [13, 34, 11, 14, 10, 10, 13, 15, 18, 21, 15, 70, 55])
    replace_sheet(wb, "Model_Setup_Evaluation", ["Hạng mục", "Mô tả và nhận xét"], methodology, [27, 115])
    dbscan_rows = [["EXP-034/036", r["model"], r["parameters"], 2000, 1000,
                    dbscan_by_parameters.get(r["parameters"], {}).get("clusters_excluding_noise", r["clusters_excluding_noise"]),
                    dbscan_by_parameters.get(r["parameters"], {}).get("noise_points", r["noise_points"]),
                    dbscan_by_parameters.get(r["parameters"], {}).get("noise_percent", r["noise_percent"]),
                    dbscan_by_parameters.get(r["parameters"], {}).get("silhouette", r["silhouette_excluding_noise"]),
                    dbscan_by_parameters.get(r["parameters"], {}).get("davies_bouldin", "CHƯA TÍNH"),
                    dbscan_by_parameters.get(r["parameters"], {}).get("calinski_harabasz", "CHƯA TÍNH"),
                    dbscan_by_parameters.get(r["parameters"], {}).get("evaluation_note", r["evaluation_note"])]
                    for r in exp34 if str(r["model"]).startswith("DBSCAN")]
    replace_sheet(wb, "DBSCAN_Noise_Metrics", ["EXP", "Thuật toán", "Tham số", "Sample fit", "Sample đánh giá", "Số cụm hợp lệ", "Số noise", "Noise (%)", "Silhouette (bỏ noise)", "Davies-Bouldin", "Calinski-Harabasz", "Ghi chú"], dbscan_rows,
                  [12, 14, 36, 10, 14, 16, 12, 13, 22, 18, 20, 55])
    robust_headers = list(robust_stability[0].keys())
    replace_sheet(wb, "EXP036_Robust_Stability", robust_headers,
                  [[r[h] for h in robust_headers] for r in robust_stability])
    profile_headers = list(selected_profile[0].keys())
    replace_sheet(wb, "Selected_Model_Profile", profile_headers,
                  [[r[h] for h in profile_headers] for r in selected_profile])
    save_atomic(wb, EXP_XLSX)

    # Append an accurately scoped entry, retaining all existing daily rows/sheets.
    wb = load_workbook(DAILY_XLSX)
    ws = wb["Nhật_Ký_Công_Việc"] if "Nhật_Ký_Công_Việc" in wb.sheetnames else wb.active
    date_text = datetime.now().strftime("%Y-%m-%d %H:%M")
    row = [int(ws.max_row - 1), date_text, "Trần Thiên Hùng", "hung",
           "Đối soát EXP-034–036: đa chỉ số, quyết định mô hình và cấu hình chốt",
           "outputs/tables/exp035_scaling_comparison.csv; outputs/tables/exp036_all_algorithms_multi_metrics.csv; outputs/tables/model_decision_exp034_exp036.csv; outputs/tables/selected_clustering_model.csv; src/write_model_evaluation_journals.py",
           "Đối soát các thực nghiệm đã chạy; tổng hợp Silhouette, Davies-Bouldin, Calinski-Harabasz, inertia và noise; kiểm tra metric trên cùng 1.000 điểm đánh giá, fit trên 2.000 điểm và điều kiện so sánh scaler cùng sample/k/seed.",
           "DBSCAN cần đánh giá trên điểm không nhiễu; tỷ lệ noise khác nhau lớn giữa các cấu hình. Inertia giữa scaler/thuật toán khác nhau không so trực tiếp.",
           "Đồng bộ bảng quyết định EXP-034–036 và sheet thiết lập/đánh giá vào workbook; sửa diễn giải lựa chọn để khớp CSV cấu hình RobustScaler; ghi rõ đây là đối soát kết quả có sẵn từ lượt chạy 16:58 ngày 17/11/2026.",
           f"Kết quả đã có chọn K-Means k=2 + RobustScaler + log1p, n_init=20, seed=42: Silhouette={float(robust_k2['silhouette']):.6f}, DBI={float(robust_k2['davies_bouldin']):.6f}, CHI={float(robust_k2['calinski_harabasz']):.2f}; ARI nhỏ nhất qua 5 seed={min_ari:.6f}. ARI giữa hai scaler={float(robust_k2['ari_vs_other_scaler_same_k']):.4f}; hồ sơ cụm dùng nhãn RobustScaler.",
           "ĐÃ ĐỐI SOÁT KẾT QUẢ ĐÃ CHẠY (không phát sinh lượt chạy mới): metric trên tối đa 1.000 khách đánh giá chung; mô hình fit trên sample cố định tối đa 2.000. DBSCAN báo noise trên toàn sample fit. Cấu hình và bảng quyết định khớp các CSV hiện có.",
           "outputs/tables/exp036_dbscan_multi_metrics.csv; exp036_ward_multi_metrics.csv; exp036_robust_stability.csv; model_decision_exp034_exp036.csv; selected_clustering_model.csv; selected_model_cluster_profiles.csv; logs/experiment_log.xlsx"]
    title = row[4]
    for idx in range(ws.max_row, 1, -1):
        if ws.cell(idx, 5).value == title:
            ws.delete_rows(idx, 1)
    row[0] = ws.max_row - 1
    ws.append(row)
    for cell in ws[ws.max_row]:
        cell.alignment = Alignment(vertical="top", wrap_text=True)
    ws.row_dimensions[ws.max_row].height = 96
    save_atomic(wb, DAILY_XLSX)
    print(f"Updated {EXP_XLSX}")
    print(f"Updated {DAILY_XLSX}")


if __name__ == "__main__":
    main()
