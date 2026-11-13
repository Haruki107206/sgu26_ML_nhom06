# -*- coding: utf-8 -*-
"""Rebuild Daily_Journal.xlsx from the project's verified activity records."""
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
import pandas as pd
from pathlib import Path

root = Path("Online_Retail_II_GiaiDoan1")
journal_file = root / "logs" / "Daily_Journal.xlsx"
log_xlsx     = root / "logs" / "experiment_log.xlsx"

records = [
    {
        "STT": 1,
        "Ngay_Gio": "2026-10-13 17:45",
        "Thanh_vien": "Nguyễn Hoàng Quy",
        "Git_Username": "HoangQuy",
        "Ma_Commit": "c8e8ed6",
        "Tieu_de_commit": "Initial commit",
        "Files_thay_doi": "README.md (1 file, 1 deletion)",
        "Nhiem_vu": (
            "Khởi tạo repository dự án máy học SGU Nhóm 06 trên GitHub."
        ),
        "Kho_khan_van_de": (
            "Phát hiện không thể dùng chung 1 environment Python trên máy của từng thành viên vì mỗi máy có phiên bản Python và thư viện cài khác nhau, không chạy lại được notebook trên máy khác."
        ),
        "Giai_phap_khac_phuc": (
            "Thống nhất tạo file requirements.txt chia sẻ chung; mỗi thành viên tự cài bằng lệnh: python -m pip install -r requirements.txt."
        ),
        "Ket_qua": "Repository GitHub được khởi tạo, các thành viên clone về máy thành công.",
        "Trang_thai": "HOÀN THÀNH",
        "Minh_chung": "Git commit c8e8ed6",
    },
    {
        "STT": 2,
        "Ngay_Gio": "2026-10-28 20:24",
        "Thanh_vien": "Nguyễn Hoàng Quy",
        "Git_Username": "Haruki107206",
        "Ma_Commit": "b9db6cc",
        "Tieu_de_commit": "Đưa các file đầu tiên của dự án lên",
        "Files_thay_doi": (
            "01_Kham_pha_du_lieu_va_RFM.ipynb, .gitignore, README.md, "
            "requirements.txt, src/download_dataset.py, docs/Ke_hoach_trien_khai.md, "
            "logs/experiment_log_template.csv "
            "(11 files, 2316 insertions)"
        ),
        "Nhiem_vu": (
            "Đưa khung dự án lên GitHub: Notebook 01 EDA, script tải dữ liệu từ UCI, cấu trúc thư mục data/raw, outputs, logs, docs và requirements."
        ),
        "Kho_khan_van_de": (
            "File Excel gốc online_retail_II.xlsx nặng ~45MB vi phạm giới hạn push của GitHub (100 MB hard limit), gây cảnh báo và làm repo phồng to, tốn băng thông khi clone cho các thành viên."
        ),
        "Giai_phap_khac_phuc": (
            "Thêm data/raw/ vào .gitignore để không bao giờ commit dữ liệu gốc. Viết script src/download_dataset.py tự động tải dataset từ UCI API khi cần thiết."
        ),
        "Ket_qua": (
            "Khung thư mục chuẩn (data, docs, logs, outputs/figures, outputs/tables, src), README và hướng dẫn môi trường đầy đủ."
        ),
        "Trang_thai": "HOÀN THÀNH",
        "Minh_chung": "Git commit b9db6cc, .gitignore, README.md",
    },
    {
        "STT": 3,
        "Ngay_Gio": "2026-11-04 14:07",
        "Thanh_vien": "Nguyễn Hoàng Quy",
        "Git_Username": "Haruki107206",
        "Ma_Commit": "32a15c7",
        "Tieu_de_commit": "kết quả phân tích dữ liệu và biểu đồ EDA",
        "Files_thay_doi": (
            "01_Kham_pha_du_lieu_va_RFM.ipynb, 7 biểu đồ PNG (01-07), eda_summary.csv, missing_values_summary.csv, preprocessing_summary.csv, rfm_table.csv (13 files, 5922 insertions)"
        ),
        "Nhiem_vu": (
            "Hoàn thiện Notebook 01: Phân tích khám phá dữ liệu (EDA), xây dựng quy tắc làm sạch và tạo bảng RFM 5878 khách hàng."
        ),
        "Kho_khan_van_de": (
            "PHÁT HIỆN LỖI DỮ LIỆU NGHIÊM TRỌNG: Khi tính Monetary = Quantity x UnitPrice và gọi np.log1p(), script vẫn lỗi ValueError với 320 khách hàng có Monetary âm. Nguyên nhân: hóa đơn hủy (mã bắt đầu bằng 'C') có Quantity âm làm tổng chi tiêu âm. Ngoài ra phát hiện 243.007 dòng (22.77%) thiếu CustomerID và 34.335 bản ghi trùng hoàn toàn."
        ),
        "Giai_phap_khac_phuc": (
            "Bổ sung 4 bước lọc nghiêm ngặt theo thứ tự: (1) Loại 34.335 bản ghi trùng; (2) Loại 235.151 dòng thiếu CustomerID; (3) Loại 18.390 hóa đơn hủy mã C; (4) Loại 70 dòng Quantity<=0 hoặc UnitPrice<=0. Thêm assert (rfm['Monetary'] > 0).all() để bảo vệ pipeline."
        ),
        "Ket_qua": (
            "Bảng RFM sạch 5.878 khách hàng, 0 giá trị âm, 0 null. 7 biểu đồ EDA (01-07) và 3 bảng tóm tắt đã xuất thành công."
        ),
        "Trang_thai": "HOÀN THÀNH",
        "Minh_chung": "outputs/tables/rfm_table.csv, outputs/figures/01-07, preprocessing_summary.csv",
    },
    {
        "STT": 4,
        "Ngay_Gio": "2026-11-06 16:10",
        "Thanh_vien": "Trần Thiên Hùng",
        "Git_Username": "hung",
        "Ma_Commit": "0409e57",
        "Tieu_de_commit": "Thực nghiệm phân cụm",
        "Files_thay_doi": (
            "02_Thuc_nghiem_phan_cum.ipynb (mới, 1112 insertions), src/run_clustering_experiments.py (mới, 241 insertions), experiment_log.csv (+34 dòng), 7 biểu đồ EDA cập nhật, 8 bảng đầu ra phân cụm (22 files, 3559 insertions)"
        ),
        "Nhiem_vu": (
            "Xây dựng Notebook 02 và script thực nghiệm: chạy baseline K-Means k=3, K-Means k=2..8, Hierarchical Ward k=2..8 và DBSCAN grid search. Ghi 33 cấu hình vào experiment log. Chọn K-Means k=2 (Silhouette 0.4246)."
        ),
        "Kho_khan_van_de": (
            "PHÁT HIỆN LỖI TIỀN XỬ LÝ: Chạy DBSCAN trên dữ liệu RFM thô (chưa chuẩn hóa) với eps=50.0: 99.8% điểm bị gán là nhiễu (-1), không tìm ra cụm nào có ý nghĩa. Nguyên nhân: Monetary (hàng nghìn GBP) lấn át Recency (ngày) và Frequency (số đơn) trong không gian Euclidean vì sự chênh lệch thang đo quá lớn."
        ),
        "Giai_phap_khac_phuc": (
            "Bắt buộc áp dụng log1p(x) để nén phân phối lệch phải của Frequency và Monetary, sau đó StandardScaler đưa về mean=0, std=1. Điều chỉnh eps DBSCAN về khoảng 0.25-1.0. Dùng mẫu cố định 2000 khách hàng (seed=42) để so sánh công bằng giữa các thuật toán."
        ),
        "Ket_qua": (
            "33 cấu hình được ghi đầy đủ vào experiment_log.csv (CL-001 đến CL-033). K-Means k=2 đạt Silhouette cao nhất (0.4246), 0% nhiễu. Biểu đồ 08 và 09 xuất thành công."
        ),
        "Trang_thai": "HOÀN THÀNH",
        "Minh_chung": "02_Thuc_nghiem_phan_cum.ipynb, clustering_model_comparison.csv, Git commit 0409e57",
    },
    {
        "STT": 5,
        "Ngay_Gio": "2026-11-08 03:00",
        "Thanh_vien": "Võ Thuận Thiên",
        "Git_Username": "vothuanthien",
        "Ma_Commit": "a3754d7",
        "Tieu_de_commit": "Bổ sung thực nghiệm phân cụm RFM",
        "Files_thay_doi": (
            "experiment_log.csv (cập nhật 66 dòng), 08_selected_cluster_rfm_profiles.png, 09_clustering_silhouette_comparison.png, cluster_interpretation.csv/.md, clustering_model_comparison.csv, clustering_preprocessing.csv, customer_clusters_sample.csv, selected_model_cluster_profiles.csv, src/run_clustering_experiments.py (10 files, 171 insertions)"
        ),
        "Nhiem_vu": (
            "Chạy lại và chỉnh sửa kết quả phân cụm: cập nhật bảng tổ hợp cấu hình, biểu đồ so sánh và diễn giải hồ sơ cụm theo trung vị vs trung vị mẫu."
        ),
        "Kho_khan_van_de": (
            "PHÁT HIỆN MÂU THUẪN DỮ LIỆU: Khi đối chiếu bảng selected_model_cluster_profiles.csv với rfm_table.csv toàn bộ, nhận ra Monetary_sum của Cụm 1 (4.908.320 GBP) chỉ là trên 838 khách trong mẫu 2000, không đại diện cho tổng thể 5.878 khách hàng. Nếu báo cáo chỉ dùng con số này để nói về 'tổng doanh thu phân khúc' sẽ bị sai về bản chất - đây là thống kê mẫu, không phải tổng thể."
        ),
        "Giai_phap_khac_phuc": (
            "Thêm chú thích rõ ràng trong cluster_interpretation.md và báo cáo: Kết quả và hồ sơ chỉ đại diện cho mẫu ngẫu nhiên cố định tối đa 2.000 khách hàng. Cần phân tích trên toàn bộ 5.878 khách hàng (EXP-037) trước khi kết luận về tỷ lệ phân khúc và đóng góp doanh thu thực tế."
        ),
        "Ket_qua": (
            "Cập nhật đầy đủ 10 bảng đầu ra và 2 biểu đồ. Ghi chú giới hạn mẫu được thêm vào cluster_interpretation.md."
        ),
        "Trang_thai": "HOÀN THÀNH",
        "Minh_chung": "cluster_interpretation.md, selected_model_cluster_profiles.csv, Git commit a3754d7",
    },
    {
        "STT": 6,
        "Ngay_Gio": "2026-11-11 21:55",
        "Thanh_vien": "Nguyễn Hoàng Quy",
        "Git_Username": "Haruki107206",
        "Ma_Commit": "1279a70",
        "Tieu_de_commit": "Sửa lỗi ghi đè nhật ký thực nghiệm và bổ sung thông tin quản lý lần chạy",
        "Files_thay_doi": (
            "src/run_clustering_experiments.py "
            "(1 file, 95 insertions / 9 deletions)"
        ),
        "Nhiem_vu": (
            "Phát hiện và sửa lỗi nghiêm trọng trong cơ chế lưu trữ nhật ký thực nghiệm. Bổ sung trường Run_ID và thông tin quản lý phiên chạy."
        ),
        "Kho_khan_van_de": (
            "SỰ CỐ NGHIÊM TRỌNG VỀ DỮ LIỆU: Script cũ sử dụng df.to_csv(path, mode='w') khiến mỗi lần chạy lại đều GHI ĐÈ hoàn toàn nhật ký, xóa sạch lịch sử 33 lần chạy trước. Vi phạm nguyên tắc bất biến của nhật ký nghiên cứu khoa học - không thể truy nguyên kết quả."
        ),
        "Giai_phap_khac_phuc": (
            "Viết lại hàm append_experiment_log(): đọc log cũ -> nối thêm dòng mới -> ghi vào file tạm .tmp -> thay thế nguyên tử (atomic replace). Cấp Run_ID = timestamp + UUID_8ky_tu để phân biệt mỗi phiên chạy."
        ),
        "Ket_qua": (
            "Chạy lại nhiều lần, nhật ký tích lũy đúng (không mất dữ liệu). 33 bản ghi CL-001 đến CL-033 được bảo toàn."
        ),
        "Trang_thai": "HOÀN THÀNH",
        "Minh_chung": "src/run_clustering_experiments.py, Git commit 1279a70",
    },
    {
        "STT": 7,
        "Ngay_Gio": "2026-11-12 20:19",
        "Thanh_vien": "Nguyễn Hoàng Quy",
        "Git_Username": "Haruki107206",
        "Ma_Commit": "374a588",
        "Tieu_de_commit": "Thêm kiểm tra chất lượng RFM và mẫu khách hàng EXP-034",
        "Files_thay_doi": (
            "outputs/tables/exp034_fixed_customer_sample.csv (mới, 2001 dòng), outputs/tables/rfm_validation_report.csv (mới, 11 dòng), src/validate_rfm_data.py (mới, 105 dòng) (3 files, 2117 insertions)"
        ),
        "Nhiem_vu": (
            "Xây dựng module kiểm định chất lượng RFM độc lập (validate_rfm_data.py) với 10 tiêu chí nghiêm ngặt. Khóa danh sách 2.000 CustomerID cố định cho EXP-034."
        ),
        "Kho_khan_van_de": (
            "PHÁT HIỆN RỦI RO TIỀM ẨN TRONG DỮ LIỆU: Lo ngại rằng một số CustomerID trong rfm_table.csv có thể bị trùng (do merge nhiều sheet Excel khi đọc file gốc) hoặc Frequency không nguyên (do làm tròn khi tính toán), dẫn đến kết quả phân cụm không tin cậy nếu không kiểm tra trước."
        ),
        "Giai_phap_khac_phuc": (
            "Viết validate_rfm_data.py kiểm tra 10 tiêu chí: file tồn tại, cột đầy đủ, CustomerID không null/không trùng, RFM hữu hạn, không âm, Frequency nguyên dương, Monetary dương, Recency >= 0. Chạy thử và xác nhận: PASS 10/10."
        ),
        "Ket_qua": (
            "Báo cáo kiểm định PASS 10/10 tiêu chí. File mẫu cố định exp034_fixed_customer_sample.csv sẵn sàng cho EXP-034."
        ),
        "Trang_thai": "HOÀN THÀNH",
        "Minh_chung": "src/validate_rfm_data.py, rfm_validation_report.csv, Git commit 374a588",
    },
    {
        "STT": 8,
        "Ngay_Gio": "2026-11-13 14:00",
        "Thanh_vien": "Nguyễn Hoàng Quy",
        "Git_Username": "HoangQuy",
        "Ma_Commit": "đang tiến hành",
        "Tieu_de_commit": "Xác nhận mẫu cố định EXP-034 và kiểm định dữ liệu",
        "Files_thay_doi": (
            "outputs/tables/exp034_fixed_customer_sample.csv (xác nhận, mẫu tạo từ 12/11), outputs/tables/rfm_validation_report.csv (kết quả kiểm định)"
        ),
        "Nhiem_vu": (
            "Xác nhận và sử dụng mẫu cố định 2.000 khách hàng đã khóa cho EXP-034; chạy lại kiểm định RFM trước khi phân cụm."
        ),
        "Kho_khan_van_de": (
            "Cần đảm bảo danh sách CustomerID cố định đúng 2.000 khách hàng, không trùng lặp và khớp với bảng RFM trước khi chạy EXP-034."
        ),
        "Giai_phap_khac_phuc": (
            "Sử dụng outputs/tables/exp034_fixed_customer_sample.csv đã được khóa từ 12/11; chạy src/validate_rfm_data.py và đối chiếu báo cáo kiểm định."
        ),
        "Ket_qua": (
            "Xác nhận mẫu EXP-034 có 2.000 CustomerID duy nhất; kiểm định RFM PASS 10/10 tiêu chí, sẵn sàng cho 5 seed."
        ),
        "Trang_thai": "HOÀN THÀNH",
        "Minh_chung": (
            "outputs/tables/exp034_fixed_customer_sample.csv, "
            "outputs/tables/rfm_validation_report.csv, src/validate_rfm_data.py"
        ),
    },
    {
        "STT": 9,
        "Ngay_Gio": "2026-11-13 15:35",
        "Thanh_vien": "Trần Thiên Hùng",
        "Git_Username": "hung",
        "Ma_Commit": "đang tiến hành",
        "Tieu_de_commit": "EXP-034: Kiểm tra độ ổn định K-Means 5 seed",
        "Files_thay_doi": (
            "src/run_exp034_stability.py (mới), outputs/tables/exp034_seed_stability.csv, exp034_pairwise_ari.csv, exp034_customer_labels.csv, outputs/figures/10_exp034_seed_stability.png"
        ),
        "Nhiem_vu": (
            "Chạy EXP-034: K-Means k=2 với 5 seed (42, 7, 21, 123, 2026) trên mẫu cố định 2000 khách. Đo độ ổn định bằng ARI. Xử lý hiện tượng Label Switching."
        ),
        "Kho_khan_van_de": (
            "PHÁT HIỆN CẠM BẪY TRONG PHÂN TÍCH DỮ LIỆU: Khi so sánh trực tiếp raw label Cluster 0 giữa seed 42 (Monetary median = 411 GBP) và seed 7 (Monetary median = 2919 GBP), kết luận sai rằng thuật toán bất ổn định. Thực chất là các tâm cụm bị đảo thứ tự ngẫu nhiên (Label Switching) do khởi tạo centroid khác nhau - không phải thuật toán sai."
        ),
        "Giai_phap_khac_phuc": (
            "(1) Dùng Adjusted Rand Index (ARI) đo tương đồng khách quan giữa 2 kết quả phân cụm (ARI không phụ thuộc thứ tự nhãn). (2) Viết hàm align_labels_by_monetary(): sắp xếp lại nhãn tăng dần theo Monetary median trước khi so sánh hồ sơ cụm."
        ),
        "Ket_qua": (
            "ARI min = 0.9741 (seed 42 vs seed 7), các cặp khác đạt 0.9960-1.000. K-Means k=2 xác nhận rất ổn định. Biểu đồ 10_exp034_seed_stability.png đã xuất."
        ),
        "Trang_thai": "HOÀN THÀNH",
        "Minh_chung": "exp034_seed_stability.csv, exp034_pairwise_ari.csv, 10_exp034_seed_stability.png",
    },
    {
        "STT": 10,
        "Ngay_Gio": "2026-11-13 16:08",
        "Thanh_vien": "Võ Thuận Thiên",
        "Git_Username": "vothuanthien",
        "Ma_Commit": "đang tiến hành",
        "Tieu_de_commit": "Tổng hợp số liệu EXP-034 và chuẩn hóa hệ thống nhật ký Excel",
        "Files_thay_doi": (
            "logs/Daily_Journal.xlsx (mới), logs/experiment_log.xlsx (cập nhật 7 sheets), docs/Nhat_ky_thuc_nghiem.md (mới)"
        ),
        "Nhiem_vu": (
            "Tổng hợp số liệu EXP-034, vẽ biểu đồ, lập nhật ký thực nghiệm chính thức và chuẩn hóa hệ thống lưu trữ sang file Excel đa trang tính."
        ),
        "Kho_khan_van_de": (
            "PHÁT HIỆN MÂU THUẪN TRONG XỬ LÝ DỮ LIỆU: Silhouette score phải được tính trên raw labels (đúng về toán học) nhưng nếu áp dụng nhầm hàm align_labels_by_monetary() TRƯỚC khi tính Silhouette, giá trị metric sẽ bị sai do thứ tự gán nhãn thay đổi. Chú ý: Silhouette chỉ đo chất lượng phân cụm hình học, không phụ thuộc tên nhãn."
        ),
        "Giai_phap_khac_phuc": (
            "Giữ nguyên việc tính Silhouette trên raw labels. Chỉ áp dụng align_labels_by_monetary() khi cần diễn giải và so sánh hồ sơ cụm giữa các seed. Ghi chú rõ ràng sự khác biệt này trong nhật ký thực nghiệm."
        ),
        "Ket_qua": (
            "logs/Daily_Journal.xlsx (10 bản ghi thực tế theo lịch sử git), logs/experiment_log.xlsx (7 sheets, 75 dòng), docs/Nhat_ky_thuc_nghiem.md hoàn chỉnh."
        ),
        "Trang_thai": "HOÀN THÀNH",
        "Minh_chung": "logs/Daily_Journal.xlsx, logs/experiment_log.xlsx, docs/Nhat_ky_thuc_nghiem.md",
    },
]

df = pd.DataFrame(records)

# Vietnamese display labels; retain stable record keys for processing.
headers = {'STT': 'STT', 'Ngay_Gio': 'Ngày giờ', 'Thanh_vien': 'Thành viên', 'Git_Username': 'Tên người dùng Git', 'Ma_Commit': 'Mã commit', 'Tieu_de_commit': 'Tiêu đề commit', 'Files_thay_doi': 'File thay đổi', 'Nhiem_vu': 'Nhiệm vụ', 'Kho_khan_van_de': 'Khó khăn, vấn đề', 'Giai_phap_khac_phuc': 'Giải pháp khắc phục', 'Ket_qua': 'Kết quả', 'Trang_thai': 'Trạng thái', 'Minh_chung': 'Minh chứng'}

# ---- Build Excel with a plain white background and black text ----
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Nhat_Ky_Cong_Viec"

plain_font   = Font(name="Times New Roman", size=11, color="000000")
white_fill   = PatternFill(fill_type="solid", fgColor="FFFFFF")
center_align = Alignment(horizontal="center", vertical="top", wrap_text=True)
left_align   = Alignment(horizontal="left",   vertical="top", wrap_text=True)

# Header row
for c_idx, col in enumerate(df.columns, 1):
    cell = ws.cell(row=1, column=c_idx, value=headers[col])
    cell.font      = plain_font
    cell.fill      = white_fill
    cell.alignment = center_align
ws.row_dimensions[1].height = 30

# Data rows
for r_idx, row_data in enumerate(df.itertuples(index=False), 2):
    for c_idx, val in enumerate(row_data, 1):
        cell = ws.cell(row=r_idx, column=c_idx, value=val)
        cell.font   = plain_font
        cell.fill   = white_fill
        col_name = df.columns[c_idx - 1]
        if col_name in ("STT", "Ngay_Gio", "Ma_Commit", "Git_Username", "Trang_thai"):
            cell.alignment = center_align
        else:
            cell.alignment = left_align
    ws.row_dimensions[r_idx].height = 95

# Column widths (in characters)
col_widths = {
    "A":  6,   # STT
    "B": 18,   # Ngay_Gio
    "C": 24,   # Thanh_vien
    "D": 17,   # Git_Username
    "E": 16,   # Ma_Commit
    "F": 35,   # Tieu_de_commit
    "G": 38,   # Files_thay_doi
    "H": 40,   # Nhiem_vu
    "I": 52,   # Kho_khan_van_de
    "J": 52,   # Giai_phap_khac_phuc
    "K": 40,   # Ket_qua
    "L": 15,   # Trang_thai
    "M": 42,   # Minh_chung
}
for col_letter, width in col_widths.items():
    ws.column_dimensions[col_letter].width = width

wb.save(journal_file)
print(f"Da tao Daily_Journal.xlsx: {journal_file}")

# Sync into experiment_log.xlsx
if log_xlsx.exists():
    with pd.ExcelWriter(log_xlsx, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        df.rename(columns=headers).to_excel(writer, sheet_name="Daily_Journal", index=False)
    synced_wb = openpyxl.load_workbook(log_xlsx)
    synced_ws = synced_wb["Daily_Journal"]
    for row in synced_ws.iter_rows():
        for cell in row:
            cell.font = plain_font
            cell.fill = white_fill
    synced_wb.save(log_xlsx)
    print(f"Da dong bo Daily_Journal vao {log_xlsx}")
