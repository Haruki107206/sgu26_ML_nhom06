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
            "Khoi tao repository du an may hoc SGU Nhom 06 tren GitHub."
        ),
        "Kho_khan_van_de": (
            "Phat hien khong the dung chung 1 environment Python tren may cua tung thanh vien "
            "vi moi may co phien ban Python va thu vien cai khac nhau, "
            "khong chay lai duoc notebook tren may khac."
        ),
        "Giai_phap_khac_phuc": (
            "Thong nhat tao file requirements.txt chia se chung; "
            "moi thanh vien tu cai bang lenh: python -m pip install -r requirements.txt."
        ),
        "Ket_qua": "Repository GitHub duoc khoi tao, cac thanh vien clone ve may thanh cong.",
        "Trang_thai": "HOAN THANH",
        "Minh_chung": "Git commit c8e8ed6",
    },
    {
        "STT": 2,
        "Ngay_Gio": "2026-10-28 20:24",
        "Thanh_vien": "Nguyễn Hoàng Quy",
        "Git_Username": "Haruki107206",
        "Ma_Commit": "b9db6cc",
        "Tieu_de_commit": "Up cac file dau tien cua du an",
        "Files_thay_doi": (
            "01_Kham_pha_du_lieu_va_RFM.ipynb, .gitignore, README.md, "
            "requirements.txt, src/download_dataset.py, docs/Ke_hoach_trien_khai.md, "
            "logs/experiment_log_template.csv "
            "(11 files, 2316 insertions)"
        ),
        "Nhiem_vu": (
            "Dua khung du an len GitHub: Notebook 01 EDA, script tai du lieu tu UCI, "
            "cau truc thu muc data/raw, outputs, logs, docs va requirements."
        ),
        "Kho_khan_van_de": (
            "File Excel goc online_retail_II.xlsx nang ~45MB vi pham gioi han push cua GitHub "
            "(100 MB hard limit), gay canh bao va lam repo phong to, "
            "ton bang thong khi clone cho cac thanh vien."
        ),
        "Giai_phap_khac_phuc": (
            "Them data/raw/ vao .gitignore de khong bao gio commit du lieu goc. "
            "Viet script src/download_dataset.py tu dong tai dataset tu UCI API khi can thiet."
        ),
        "Ket_qua": (
            "Khung thu muc chuan (data, docs, logs, outputs/figures, outputs/tables, src), "
            "README va huong dan mo truong day du."
        ),
        "Trang_thai": "HOAN THANH",
        "Minh_chung": "Git commit b9db6cc, .gitignore, README.md",
    },
    {
        "STT": 3,
        "Ngay_Gio": "2026-11-04 14:07",
        "Thanh_vien": "Nguyễn Hoàng Quy",
        "Git_Username": "Haruki107206",
        "Ma_Commit": "32a15c7",
        "Tieu_de_commit": "ket qua phan tich du lieu va bieu do EDA",
        "Files_thay_doi": (
            "01_Kham_pha_du_lieu_va_RFM.ipynb, "
            "7 bieu do PNG (01-07), eda_summary.csv, missing_values_summary.csv, "
            "preprocessing_summary.csv, rfm_table.csv "
            "(13 files, 5922 insertions)"
        ),
        "Nhiem_vu": (
            "Hoan thien Notebook 01: Phan tich kham pha du lieu (EDA), "
            "xay dung quy tac lam sach va tao bang RFM 5878 khach hang."
        ),
        "Kho_khan_van_de": (
            "PHAT HIEN LOI DU LIEU NGHIEM TRONG: Khi tinh Monetary = Quantity x UnitPrice "
            "va goi np.log1p(), script van loi ValueError voi 320 khach hang co Monetary am. "
            "Nguyen nhan: hoa don huy (ma bat dau bang 'C') co Quantity am lam tong chi tieu am. "
            "Ngoai ra phat hien 243.007 dong (22.77%) thieu CustomerID "
            "va 34.335 ban ghi trung hoan toan."
        ),
        "Giai_phap_khac_phuc": (
            "Bo sung 4 buoc loc nghiem ngat theo thu tu: "
            "(1) Loai 34.335 ban ghi trung; "
            "(2) Loai 235.151 dong thieu CustomerID; "
            "(3) Loai 18.390 hoa don huy ma C; "
            "(4) Loai 70 dong Quantity<=0 hoac UnitPrice<=0. "
            "Them assert (rfm['Monetary'] > 0).all() de bao ve pipeline."
        ),
        "Ket_qua": (
            "Bang RFM sach 5.878 khach hang, 0 gia tri am, 0 null. "
            "7 bieu do EDA (01-07) va 3 bang tom tat da xuat thanh cong."
        ),
        "Trang_thai": "HOAN THANH",
        "Minh_chung": "outputs/tables/rfm_table.csv, outputs/figures/01-07, preprocessing_summary.csv",
    },
    {
        "STT": 4,
        "Ngay_Gio": "2026-11-06 16:10",
        "Thanh_vien": "Trần Thiên Hùng",
        "Git_Username": "hung",
        "Ma_Commit": "0409e57",
        "Tieu_de_commit": "Thuc nghiem phan cum",
        "Files_thay_doi": (
            "02_Thuc_nghiem_phan_cum.ipynb (moi, 1112 insertions), "
            "src/run_clustering_experiments.py (moi, 241 insertions), "
            "experiment_log.csv (+34 dong), 7 bieu do EDA cap nhat, "
            "8 bang dau ra phan cum "
            "(22 files, 3559 insertions)"
        ),
        "Nhiem_vu": (
            "Xay dung Notebook 02 va script thuc nghiem: chay baseline K-Means k=3, "
            "K-Means k=2..8, Hierarchical Ward k=2..8 va DBSCAN grid search. "
            "Ghi 33 cau hinh vao experiment log. Chon K-Means k=2 (Silhouette 0.4246)."
        ),
        "Kho_khan_van_de": (
            "PHAT HIEN LOI TIEN XU LY: Chay DBSCAN tren du lieu RFM tho (chua chuan hoa) "
            "voi eps=50.0: 99.8% diem bi gan la nhieu (-1), khong tim ra cum nao co y nghia. "
            "Nguyen nhan: Monetary (hang nghin GBP) lan at Recency (ngay) va Frequency (so don) "
            "trong khong gian Euclidean vi su chenh lech thang do qua lon."
        ),
        "Giai_phap_khac_phuc": (
            "Bat buoc ap dung log1p(x) de nen phan phoi lech phai cua Frequency va Monetary, "
            "sau do StandardScaler dua ve mean=0, std=1. "
            "Dieu chinh eps DBSCAN ve khoang 0.25-1.0. "
            "Dung mau co dinh 2000 khach hang (seed=42) de so sanh cong bang giua cac thuat toan."
        ),
        "Ket_qua": (
            "33 cau hinh duoc ghi day du vao experiment_log.csv (CL-001 den CL-033). "
            "K-Means k=2 dat Silhouette cao nhat (0.4246), 0% nhieu. "
            "Bieu do 08 va 09 xuat thanh cong."
        ),
        "Trang_thai": "HOAN THANH",
        "Minh_chung": "02_Thuc_nghiem_phan_cum.ipynb, clustering_model_comparison.csv, Git commit 0409e57",
    },
    {
        "STT": 5,
        "Ngay_Gio": "2026-11-08 03:00",
        "Thanh_vien": "Võ Thuận Thiên",
        "Git_Username": "vothuanthien",
        "Ma_Commit": "a3754d7",
        "Tieu_de_commit": "Bo sung thuc nghiem phan cum RFM",
        "Files_thay_doi": (
            "experiment_log.csv (cap nhat 66 dong), "
            "08_selected_cluster_rfm_profiles.png, 09_clustering_silhouette_comparison.png, "
            "cluster_interpretation.csv/.md, clustering_model_comparison.csv, "
            "clustering_preprocessing.csv, customer_clusters_sample.csv, "
            "selected_model_cluster_profiles.csv, src/run_clustering_experiments.py "
            "(10 files, 171 insertions)"
        ),
        "Nhiem_vu": (
            "Chay lai va chinh sua ket qua phan cum: cap nhat ban to hop cau hinh, "
            "bieu do so sanh va dien giai ho so cum theo trung vi vs trung vi mau."
        ),
        "Kho_khan_van_de": (
            "PHAT HIEN MAU THUAN DU LIEU: Khi doi chieu bang selected_model_cluster_profiles.csv "
            "voi rfm_table.csv toan bo, nhan ra Monetary_sum cua Cum 1 "
            "(4.908.320 GBP) chi la tren 838 khach trong mau 2000, "
            "khong dai dien cho tong the 5.878 khach hang. "
            "Neu bao cao chi dung con so nay de noi ve 'tong doanh thu phan khuc' "
            "se bi sai ve ban chat - day la thong ke mau, khong phai tong the."
        ),
        "Giai_phap_khac_phuc": (
            "Them chu thich ro rang trong cluster_interpretation.md va bao cao: "
            "Ket qua va ho so chi dai dien cho mau ngau nhien co dinh toi da 2.000 khach hang. "
            "Can phan tich tren toan bo 5.878 khach hang (EXP-037) truoc khi ket luan ve "
            "ty le phan khuc va dong gop doanh thu thuc te."
        ),
        "Ket_qua": (
            "Cap nhat day du 10 bang dau ra va 2 bieu do. "
            "Ghi chu gioi han mau duoc them vao cluster_interpretation.md."
        ),
        "Trang_thai": "HOAN THANH",
        "Minh_chung": "cluster_interpretation.md, selected_model_cluster_profiles.csv, Git commit a3754d7",
    },
    {
        "STT": 6,
        "Ngay_Gio": "2026-11-11 21:55",
        "Thanh_vien": "Nguyễn Hoàng Quy",
        "Git_Username": "Haruki107206",
        "Ma_Commit": "1279a70",
        "Tieu_de_commit": "Sua loi ghi de nhat ky thuc nghiem va bo sung thong tin quan ly lan chay",
        "Files_thay_doi": (
            "src/run_clustering_experiments.py "
            "(1 file, 95 insertions / 9 deletions)"
        ),
        "Nhiem_vu": (
            "Phat hien va sua loi nghiem trong trong co che luu tru nhat ky thuc nghiem. "
            "Bo sung truong Run_ID va thong tin quan ly phien chay."
        ),
        "Kho_khan_van_de": (
            "SU CO NGHIEM TRONG VE DU LIEU: Script cu su dung df.to_csv(path, mode='w') "
            "khien moi lan chay lai deu GHI DE hoan toan nhat ky, "
            "xoa sach lich su 33 lan chay truoc. "
            "Vi pham nguyen tac bat bien cua nhat ky nghien cuu khoa hoc - "
            "khong the truy nguyen ket qua."
        ),
        "Giai_phap_khac_phuc": (
            "Viet lai ham append_experiment_log(): doc log cu -> noi them dong moi -> "
            "ghi vao file tam .tmp -> thay the nguyen tu (atomic replace). "
            "Cap Run_ID = timestamp + UUID_8ky_tu de phan biet moi phien chay."
        ),
        "Ket_qua": (
            "Chay lai nhieu lan, nhat ky tich luy dung (khong mat du lieu). "
            "33 ban ghi CL-001 den CL-033 duoc bao toan."
        ),
        "Trang_thai": "HOAN THANH",
        "Minh_chung": "src/run_clustering_experiments.py, Git commit 1279a70",
    },
    {
        "STT": 7,
        "Ngay_Gio": "2026-11-12 20:19",
        "Thanh_vien": "Nguyễn Hoàng Quy",
        "Git_Username": "Haruki107206",
        "Ma_Commit": "374a588",
        "Tieu_de_commit": "Them kiem tra chat luong RFM va mau khach hang EXP-034",
        "Files_thay_doi": (
            "outputs/tables/exp034_fixed_customer_sample.csv (moi, 2001 dong), "
            "outputs/tables/rfm_validation_report.csv (moi, 11 dong), "
            "src/validate_rfm_data.py (moi, 105 dong) "
            "(3 files, 2117 insertions)"
        ),
        "Nhiem_vu": (
            "Xay dung module kiem dinh chat luong RFM doc lap (validate_rfm_data.py) "
            "voi 10 tieu chi nghiem ngat. Khoa danh sach 2.000 CustomerID co dinh cho EXP-034."
        ),
        "Kho_khan_van_de": (
            "PHAT HIEN RUI RO TIEM AN TRONG DU LIEU: Lo ngai rang mot so CustomerID trong rfm_table.csv "
            "co the bi trung (do merge nhieu sheet Excel khi doc file goc) "
            "hoac Frequency khong nguyen (do lam tron khi tinh toan), "
            "dan den ket qua phan cum khong tin cay neu khong kiem tra truoc."
        ),
        "Giai_phap_khac_phuc": (
            "Viet validate_rfm_data.py kiem tra 10 tieu chi: file ton tai, cot day du, "
            "CustomerID khong null/khong trung, RFM huu han, khong am, "
            "Frequency nguyen duong, Monetary duong, Recency >= 0. "
            "Chay thu va xac nhan: PASS 10/10."
        ),
        "Ket_qua": (
            "Bao cao kiem dinh PASS 10/10 tieu chi. "
            "File mau co dinh exp034_fixed_customer_sample.csv san sang cho EXP-034."
        ),
        "Trang_thai": "HOAN THANH",
        "Minh_chung": "src/validate_rfm_data.py, rfm_validation_report.csv, Git commit 374a588",
    },
    {
        "STT": 8,
        "Ngay_Gio": "2026-11-13 14:00",
        "Thanh_vien": "Nguyễn Hoàng Quy",
        "Git_Username": "HoangQuy",
        "Ma_Commit": "dang tien hanh",
        "Tieu_de_commit": "Xac nhan mau co dinh EXP-034 va kiem dinh du lieu",
        "Files_thay_doi": (
            "outputs/tables/exp034_fixed_customer_sample.csv (xac nhan, mau tao tu 12/11), "
            "outputs/tables/rfm_validation_report.csv (ket qua kiem dinh)"
        ),
        "Nhiem_vu": (
            "Xac nhan va su dung mau co dinh 2.000 khach hang da khoa cho EXP-034; "
            "chay lai kiem dinh RFM truoc khi phan cum."
        ),
        "Kho_khan_van_de": (
            "Can dam bao danh sach CustomerID co dinh dung 2.000 khach hang, "
            "khong trung lap va khop voi bang RFM truoc khi chay EXP-034."
        ),
        "Giai_phap_khac_phuc": (
            "Su dung outputs/tables/exp034_fixed_customer_sample.csv da duoc khoa tu 12/11; "
            "chay src/validate_rfm_data.py va doi chieu bao cao kiem dinh."
        ),
        "Ket_qua": (
            "Xac nhan mau EXP-034 co 2.000 CustomerID duy nhat; "
            "kiem dinh RFM PASS 10/10 tieu chi, san sang cho 5 seed."
        ),
        "Trang_thai": "HOAN THANH",
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
        "Ma_Commit": "dang tien hanh",
        "Tieu_de_commit": "EXP-034: Kiem tra do on dinh K-Means 5 seed",
        "Files_thay_doi": (
            "src/run_exp034_stability.py (moi), "
            "outputs/tables/exp034_seed_stability.csv, exp034_pairwise_ari.csv, "
            "exp034_customer_labels.csv, "
            "outputs/figures/10_exp034_seed_stability.png"
        ),
        "Nhiem_vu": (
            "Chay EXP-034: K-Means k=2 voi 5 seed (42, 7, 21, 123, 2026) tren mau co dinh 2000 khach. "
            "Do do on dinh bang ARI. Xu ly hien tuong Label Switching."
        ),
        "Kho_khan_van_de": (
            "PHAT HIEN CAM BAY TRONG PHAN TICH DU LIEU: Khi so sanh truc tiep raw label "
            "Cluster 0 giua seed 42 (Monetary median = 411 GBP) va seed 7 (Monetary median = 2919 GBP), "
            "ket luan sai rang thuat toan bat on dinh. "
            "Thuc chat la cac tam cum bi dao thu tu ngau nhien (Label Switching) "
            "do khoi tao centroid khac nhau - khong phai thuat toan sai."
        ),
        "Giai_phap_khac_phuc": (
            "(1) Dung Adjusted Rand Index (ARI) do tuong dong khach quan "
            "giua 2 ket qua phan cum (ARI khong phu thuoc thu tu nhan). "
            "(2) Viet ham align_labels_by_monetary(): sap xep lai nhan tang dan "
            "theo Monetary median truoc khi so sanh ho so cum."
        ),
        "Ket_qua": (
            "ARI min = 0.9741 (seed 42 vs seed 7), cac cap khac dat 0.9960-1.000. "
            "K-Means k=2 xac nhan rat on dinh. "
            "Bieu do 10_exp034_seed_stability.png da xuat."
        ),
        "Trang_thai": "HOAN THANH",
        "Minh_chung": "exp034_seed_stability.csv, exp034_pairwise_ari.csv, 10_exp034_seed_stability.png",
    },
    {
        "STT": 10,
        "Ngay_Gio": "2026-11-13 16:08",
        "Thanh_vien": "Võ Thuận Thiên",
        "Git_Username": "vothuanthien",
        "Ma_Commit": "dang tien hanh",
        "Tieu_de_commit": "Tong hop so lieu EXP-034 va chuan hoa he thong nhat ky Excel",
        "Files_thay_doi": (
            "logs/Daily_Journal.xlsx (moi), "
            "logs/experiment_log.xlsx (cap nhat 7 sheets), "
            "docs/Nhat_ky_thuc_nghiem.md (moi)"
        ),
        "Nhiem_vu": (
            "Tong hop so lieu EXP-034, ve bieu do, lap nhat ky thuc nghiem chinh thuc "
            "va chuan hoa he thong luu tru sang file Excel da trang tinh."
        ),
        "Kho_khan_van_de": (
            "PHAT HIEN MAU THUAN TRONG XU LY DU LIEU: Silhouette score phai duoc tinh "
            "tren raw labels (dung ve toan hoc) nhung neu ap dung nham "
            "ham align_labels_by_monetary() TRUOC khi tinh Silhouette, "
            "gia tri metric se bi sai do thu tu gan nhan thay doi. "
            "Chu y: Silhouette chi do chat luong phan cum hinh hoc, khong phu thuoc ten nhan."
        ),
        "Giai_phap_khac_phuc": (
            "Giu nguyen viec tinh Silhouette tren raw labels. "
            "Chi ap dung align_labels_by_monetary() khi can dien giai "
            "va so sanh ho so cum giua cac seed. "
            "Ghi chu ro rang su khac biet nay trong nhat ky thuc nghiem."
        ),
        "Ket_qua": (
            "logs/Daily_Journal.xlsx (10 ban ghi thuc te theo lich su git), "
            "logs/experiment_log.xlsx (7 sheets, 75 dong), "
            "docs/Nhat_ky_thuc_nghiem.md hoan chinh."
        ),
        "Trang_thai": "HOAN THANH",
        "Minh_chung": "logs/Daily_Journal.xlsx, logs/experiment_log.xlsx, docs/Nhat_ky_thuc_nghiem.md",
    },
]

df = pd.DataFrame(records)

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
    cell = ws.cell(row=1, column=c_idx, value=col)
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
        df.to_excel(writer, sheet_name="Daily_Journal", index=False)
    synced_wb = openpyxl.load_workbook(log_xlsx)
    synced_ws = synced_wb["Daily_Journal"]
    for row in synced_ws.iter_rows():
        for cell in row:
            cell.font = plain_font
            cell.fill = white_fill
    synced_wb.save(log_xlsx)
    print(f"Da dong bo Daily_Journal vao {log_xlsx}")
