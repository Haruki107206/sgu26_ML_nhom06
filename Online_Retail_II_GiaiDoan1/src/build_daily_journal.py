# -*- coding: utf-8 -*-
"""Rebuild Daily_Journal.xlsx with proper Vietnamese Unicode and add 15/11 entry."""
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side
import pandas as pd
from pathlib import Path

root = Path("Online_Retail_II_GiaiDoan1")
journal_file = root / "logs" / "Daily_Journal.xlsx"
log_xlsx     = root / "logs" / "experiment_log.xlsx"

records = [{'STT': 1,
  'Ngày_Giờ': '2026-10-13 17:45',
  'Thành_viên': 'Nguyễn Hoàng Quy',
  'Git_Username': 'HoangQuy',
  'Tiêu_đề_commit': 'Initial commit',
  'Files_thay_đổi': 'README.md (1 file, 1 deletion)',
  'Nhiệm_vụ': 'Khởi tạo repository đồ án Máy học SGU Nhóm 06 trên GitHub.',
  'Khó_khăn_vấn_đề': 'Phát hiện không thể dùng chung 1 environment Python trên máy của từng thành '
                     'viên vì mỗi máy có phiên bản Python và thư viện cài khác nhau, khiến '
                     'notebook không chạy lại được trên máy khác.',
  'Giải_pháp_khắc_phục': 'Thống nhất tạo file requirements.txt chia sẻ chung; mỗi thành viên tự '
                         'cài bằng lệnh: python -m pip install -r requirements.txt.',
  'Kết_quả': 'Repository GitHub được khởi tạo, các thành viên clone về máy thành công.',
  'Trạng_thái': 'HOÀN THÀNH',
  'Minh_chứng': 'Git commit c8e8ed6'},
 {'STT': 2,
  'Ngày_Giờ': '2026-10-28 20:24',
  'Thành_viên': 'Nguyễn Hoàng Quy',
  'Git_Username': 'Haruki107206',
  'Tiêu_đề_commit': 'Up các file đầu tiên của dự án',
  'Files_thay_đổi': '01_Kham_pha_du_lieu_va_RFM.ipynb, .gitignore, README.md, requirements.txt, '
                    'src/download_dataset.py, docs/Ke_hoach_trien_khai.md, '
                    'logs/experiment_log_template.csv (11 files, 2316 insertions)',
  'Nhiệm_vụ': 'Đưa khung dự án lên GitHub: Notebook 01 EDA, script tải dữ liệu từ UCI, cấu trúc '
              'thư mục data/raw, outputs, logs, docs và requirements.',
  'Khó_khăn_vấn_đề': 'File Excel gốc online_retail_II.xlsx nặng ~45MB vi phạm giới hạn push của '
                     'GitHub (100 MB hard limit), gây cảnh báo và làm repo phình to, tốn băng '
                     'thông khi clone cho các thành viên.',
  'Giải_pháp_khắc_phục': 'Thêm data/raw/ vào .gitignore để không bao giờ commit dữ liệu gốc. Viết '
                         'script src/download_dataset.py tự động tải dataset từ UCI API khi cần.',
  'Kết_quả': 'Khung thư mục chuẩn (data, docs, logs, outputs/figures, outputs/tables, src), README '
             'và hướng dẫn môi trường đầy đủ.',
  'Trạng_thái': 'HOÀN THÀNH',
  'Minh_chứng': 'Git commit b9db6cc, .gitignore, README.md'},
 {'STT': 3,
  'Ngày_Giờ': '2026-11-04 14:07',
  'Thành_viên': 'Nguyễn Hoàng Quy',
  'Git_Username': 'Haruki107206',
  'Tiêu_đề_commit': 'kết quả phân tích dữ liệu và biểu đồ EDA',
  'Files_thay_đổi': '01_Kham_pha_du_lieu_va_RFM.ipynb, 7 biểu đồ PNG (01-07), eda_summary.csv, '
                    'missing_values_summary.csv, preprocessing_summary.csv, rfm_table.csv (13 '
                    'files, 5922 insertions)',
  'Nhiệm_vụ': 'Hoàn thiện Notebook 01: Phân tích khám phá dữ liệu (EDA), xây dựng quy tắc làm sạch '
              'và tạo bảng RFM 5.878 khách hàng.',
  'Khó_khăn_vấn_đề': 'PHÁT HIỆN LỖI DỮ LIỆU NGHIÊM TRỌNG: Khi tính Monetary = Quantity × UnitPrice '
                     'và gọi np.log1p(), script văng lỗi ValueError với 320 khách hàng có Monetary '
                     "âm. Nguyên nhân: hóa đơn hủy (mã bắt đầu bằng 'C') có Quantity âm làm tổng "
                     'chi tiêu âm. Ngoài ra phát hiện 243.007 dòng (22,77%) thiếu CustomerID và '
                     '34.335 bản ghi trùng hoàn toàn.',
  'Giải_pháp_khắc_phục': 'Bổ sung 4 bước lọc nghiêm ngặt theo thứ tự: (1) Loại 34.335 bản ghi '
                         'trùng; (2) Loại 235.151 dòng thiếu CustomerID; (3) Loại 18.390 hóa đơn '
                         'hủy mã C; (4) Loại 70 dòng Quantity≤0 hoặc UnitPrice≤0. Thêm assert '
                         "(rfm['Monetary'] > 0).all() để bảo vệ pipeline.",
  'Kết_quả': 'Bảng RFM sạch 5.878 khách hàng, 0 giá trị âm, 0 null. 7 biểu đồ EDA (01-07) và 3 '
             'bảng tóm tắt đã xuất thành công.',
  'Trạng_thái': 'HOÀN THÀNH',
  'Minh_chứng': 'outputs/tables/rfm_table.csv, outputs/figures/01-07, preprocessing_summary.csv'},
 {'STT': 4,
  'Ngày_Giờ': '2026-11-06 16:10',
  'Thành_viên': 'Trần Thiên Hùng',
  'Git_Username': 'hung',
  'Tiêu_đề_commit': 'Thực nghiệm phân cụm',
  'Files_thay_đổi': '02_Thuc_nghiem_phan_cum.ipynb (mới, 1112 insertions), '
                    'src/run_clustering_experiments.py (mới, 241 insertions), experiment_log.csv '
                    '(+34 dòng), 7 biểu đồ EDA cập nhật, 8 bảng đầu ra phân cụm (22 files, 3559 '
                    'insertions)',
  'Nhiệm_vụ': 'Xây dựng Notebook 02 và script thực nghiệm: chạy baseline K-Means k=3, K-Means '
              'k=2..8, Hierarchical Ward k=2..8 và DBSCAN grid search. Ghi 33 cấu hình vào '
              'experiment log. Chọn K-Means k=2 (Silhouette 0,4246).',
  'Khó_khăn_vấn_đề': 'PHÁT HIỆN LỖI TIỀN XỬ LÝ: Chạy DBSCAN trên dữ liệu RFM thô (chưa chuẩn hóa) '
                     'với eps=50,0: 99,8% điểm bị gán là nhiễu (−1), không tìm ra cụm nào có ý '
                     'nghĩa. Nguyên nhân: Monetary (hàng nghìn GBP) lấn át Recency (ngày) và '
                     'Frequency (số đơn) trong không gian Euclidean vì sự chênh lệch thang đo quá '
                     'lớn.',
  'Giải_pháp_khắc_phục': 'Bắt buộc áp dụng log1p(x) để nén phân phối lệch phải của Frequency và '
                         'Monetary, sau đó StandardScaler đưa về mean=0, std=1. Điều chỉnh eps '
                         'DBSCAN về khoảng 0,25–1,0. Dùng mẫu cố định 2.000 khách hàng (seed=42) '
                         'để so sánh công bằng.',
  'Kết_quả': '33 cấu hình được ghi đầy đủ vào experiment_log.csv (CL-001 đến CL-033). K-Means k=2 '
             'đạt Silhouette cao nhất (0,4246), 0% nhiễu.',
  'Trạng_thái': 'HOÀN THÀNH',
  'Minh_chứng': '02_Thuc_nghiem_phan_cum.ipynb, clustering_model_comparison.csv, Git commit '
                '0409e57'},
 {'STT': 5,
  'Ngày_Giờ': '2026-11-08 03:00',
  'Thành_viên': 'Võ Thuận Thiên',
  'Git_Username': 'vothuanthien',
  'Tiêu_đề_commit': 'Bổ sung thực nghiệm phân cụm RFM',
  'Files_thay_đổi': 'experiment_log.csv (cập nhật 66 dòng), 08_selected_cluster_rfm_profiles.png, '
                    '09_clustering_silhouette_comparison.png, cluster_interpretation.csv/.md, '
                    'clustering_model_comparison.csv, clustering_preprocessing.csv, '
                    'customer_clusters_sample.csv, selected_model_cluster_profiles.csv, '
                    'src/run_clustering_experiments.py (10 files, 171 insertions)',
  'Nhiệm_vụ': 'Chạy lại và chỉnh sửa kết quả phân cụm: cập nhật bảng tổ hợp cấu hình, biểu đồ so '
              'sánh và diễn giải hồ sơ cụm theo trung vị so với trung vị mẫu.',
  'Khó_khăn_vấn_đề': 'PHÁT HIỆN MÂU THUẪN DỮ LIỆU: Khi đối chiếu bảng '
                     'selected_model_cluster_profiles.csv với rfm_table.csv toàn bộ, nhận ra '
                     'Monetary_sum của Cụm 1 (4.908.320 GBP) chỉ là thống kê trên 838 khách trong '
                     'mẫu 2.000, không đại diện cho tổng thể 5.878 khách hàng. Nếu báo cáo dùng '
                     "con số này để nói về 'tổng doanh thu phân khúc' sẽ sai về bản chất.",
  'Giải_pháp_khắc_phục': "Thêm chú thích rõ ràng trong cluster_interpretation.md: 'Kết quả và hồ "
                         'sơ chỉ đại diện cho mẫu ngẫu nhiên cố định tối đa 2.000 khách hàng. Cần '
                         'phân tích trên toàn bộ 5.878 khách hàng (EXP-037) trước khi kết luận về '
                         "tỷ lệ phân khúc và đóng góp doanh thu thực tế.'",
  'Kết_quả': 'Cập nhật đầy đủ 10 bảng đầu ra và 2 biểu đồ. Ghi chú giới hạn mẫu được thêm vào '
             'cluster_interpretation.md.',
  'Trạng_thái': 'HOÀN THÀNH',
  'Minh_chứng': 'cluster_interpretation.md, selected_model_cluster_profiles.csv, Git commit '
                'a3754d7'},
 {'STT': 6,
  'Ngày_Giờ': '2026-11-11 21:55',
  'Thành_viên': 'Nguyễn Hoàng Quy',
  'Git_Username': 'Haruki107206',
  'Tiêu_đề_commit': 'Sửa lỗi ghi đè nhật ký thực nghiệm và bổ sung thông tin quản lý lần chạy',
  'Files_thay_đổi': 'src/run_clustering_experiments.py (1 file, 95 insertions / 9 deletions)',
  'Nhiệm_vụ': 'Phát hiện và sửa lỗi nghiêm trọng trong cơ chế lưu trữ nhật ký thực nghiệm. Bổ sung '
              'trường Run_ID và thông tin quản lý phiên chạy.',
  'Khó_khăn_vấn_đề': "SỰ CỐ NGHIÊM TRỌNG VỀ DỮ LIỆU: Script cũ sử dụng df.to_csv(path, mode='w') "
                     'khiến mỗi lần chạy lại đều GHI ĐÈ hoàn toàn nhật ký, xóa sạch lịch sử 33 lần '
                     'chạy trước. Vi phạm nguyên tắc bất biến của nhật ký nghiên cứu khoa học − '
                     'không thể truy nguyên kết quả.',
  'Giải_pháp_khắc_phục': 'Viết lại hàm append_experiment_log(): đọc log cũ → nối thêm dòng mới → '
                         'ghi vào file tạm .tmp → thay thế nguyên tử (atomic replace). Cấp Run_ID '
                         '= timestamp + UUID_8 ký tự để phân biệt mỗi phiên chạy.',
  'Kết_quả': 'Chạy lại nhiều lần, nhật ký tích lũy đúng (không mất dữ liệu). 33 bản ghi CL-001 đến '
             'CL-033 được bảo toàn.',
  'Trạng_thái': 'HOÀN THÀNH',
  'Minh_chứng': 'src/run_clustering_experiments.py, Git commit 1279a70'},
 {'STT': 7,
  'Ngày_Giờ': '2026-11-12 20:19',
  'Thành_viên': 'Nguyễn Hoàng Quy',
  'Git_Username': 'Haruki107206',
  'Tiêu_đề_commit': 'Thêm kiểm tra chất lượng RFM và mẫu khách hàng EXP-034',
  'Files_thay_đổi': 'outputs/tables/exp034_fixed_customer_sample.csv (mới, 2.001 dòng), '
                    'outputs/tables/rfm_validation_report.csv (mới, 11 dòng), '
                    'src/validate_rfm_data.py (mới, 105 dòng) (3 files, 2117 insertions)',
  'Nhiệm_vụ': 'Xây dựng module kiểm định chất lượng RFM độc lập (validate_rfm_data.py) với 10 tiêu '
              'chí nghiêm ngặt. Khóa danh sách 2.000 CustomerID cố định cho EXP-034.',
  'Khó_khăn_vấn_đề': 'PHÁT HIỆN RỦI RO TIỀM ẨN TRONG DỮ LIỆU: Lo ngại rằng một số CustomerID trong '
                     'rfm_table.csv có thể bị trùng (do merge nhiều sheet Excel khi đọc file gốc) '
                     'hoặc Frequency không nguyên (do làm tròn khi tính toán), dẫn đến kết quả '
                     'phân cụm không tin cậy nếu không kiểm tra trước.',
  'Giải_pháp_khắc_phục': 'Viết validate_rfm_data.py kiểm tra 10 tiêu chí: file tồn tại, cột đầy '
                         'đủ, CustomerID không null/không trùng, RFM hữu hạn, không âm, Frequency '
                         'nguyên dương, Monetary dương, Recency ≥ 0. Chạy thử và xác nhận: PASS '
                         '10/10.',
  'Kết_quả': 'Báo cáo kiểm định PASS 10/10 tiêu chí. File mẫu cố định '
             'exp034_fixed_customer_sample.csv sẵn sàng cho EXP-034.',
  'Trạng_thái': 'HOÀN THÀNH',
  'Minh_chứng': 'src/validate_rfm_data.py, rfm_validation_report.csv, Git commit 374a588'},
 {'STT': 8,
  'Ngày_Giờ': '2026-11-13 14:00',
  'Thành_viên': 'Nguyễn Hoàng Quy',
  'Git_Username': 'HoangQuy',
  'Tiêu_đề_commit': 'Kiểm thử toàn diện giai đoạn nền tảng 11/11−12/11',
  'Files_thay_đổi': 'docs/Bao_cao_kiem_thu_11_12_11.md (mới)',
  'Nhiệm_vụ': 'Chạy kiểm định validate_rfm_data.py, rà soát 7 biểu đồ EDA và 33 mô hình ban đầu. '
              'Lập biên bản kiểm thử chính thức giai đoạn 11/11−12/11.',
  'Khó_khăn_vấn_đề': 'PHÁT HIỆN LỖI MÔI TRƯỜNG CHẠY: Môi trường WindowsApps python.exe (Microsoft '
                     'Store) bị chặn quyền truy cập khi chạy tự động trong một số bối cảnh, gây '
                     "lỗi 'Permission denied'. Không thể chạy script trực tiếp từ công cụ tự động "
                     'hóa.',
  'Giải_pháp_khắc_phục': 'Xác định và sử dụng Python 3.11 chính thức (được cài qua '
                         'PythonSoftwareFoundation) thay vì phiên bản WindowsApps để chạy được '
                         'script.',
  'Kết_quả': 'Biên bản kiểm thử PASS 100% (10/10 tiêu chí RFM, 7 biểu đồ, 33 mô hình).',
  'Trạng_thái': 'HOÀN THÀNH',
  'Minh_chứng': 'docs/Bao_cao_kiem_thu_11_12_11.md, rfm_validation_report.csv'},
 {'STT': 9,
  'Ngày_Giờ': '2026-11-13 15:35',
  'Thành_viên': 'Trần Thiên Hùng',
  'Git_Username': 'hung',
  'Tiêu_đề_commit': 'EXP-034: Kiểm tra độ ổn định K-Means 5 seed',
  'Files_thay_đổi': 'src/run_exp034_stability.py (mới), outputs/tables/exp034_seed_stability.csv, '
                    'exp034_pairwise_ari.csv, exp034_customer_labels.csv, '
                    'outputs/figures/10_exp034_seed_stability.png',
  'Nhiệm_vụ': 'Chạy EXP-034: K-Means k=2 với 5 seed (42, 7, 21, 123, 2026) trên mẫu cố định 2.000 '
              'khách. Đo độ ổn định bằng ARI. Xử lý hiện tượng Label Switching.',
  'Khó_khăn_vấn_đề': 'PHÁT HIỆN CẠM BẪY TRONG PHÂN TÍCH DỮ LIỆU (Label Switching): Khi so sánh '
                     'trực tiếp raw label Cụm 0 giữa seed 42 (Monetary median = 411 GBP) và seed 7 '
                     '(Monetary median = 2.919 GBP), kết luận sai rằng thuật toán bất ổn định. '
                     'Thực chất là các tâm cụm bị đảo thứ tự ngẫu nhiên do khởi tạo centroid khác '
                     'nhau.',
  'Giải_pháp_khắc_phục': '(1) Dùng Adjusted Rand Index (ARI) đo tương đồng khách quan giữa 2 kết '
                         'quả phân cụm (ARI không phụ thuộc thứ tự nhãn). (2) Viết hàm '
                         'align_labels_by_monetary(): sắp xếp lại nhãn tăng dần theo Monetary '
                         'median trước khi so sánh hồ sơ cụm.',
  'Kết_quả': 'ARI min = 0,9741 (seed 42 vs seed 7), các cặp khác đạt 0,9960−1,000. K-Means k=2 xác '
             'nhận rất ổn định. Biểu đồ 10_exp034_seed_stability.png đã xuất.',
  'Trạng_thái': 'HOÀN THÀNH',
  'Minh_chứng': 'exp034_seed_stability.csv, exp034_pairwise_ari.csv, 10_exp034_seed_stability.png'},
 {'STT': 10,
  'Ngày_Giờ': '2026-11-13 16:08',
  'Thành_viên': 'Võ Thuận Thiên',
  'Git_Username': 'vothuanthien',
  'Tiêu_đề_commit': 'Tổng hợp số liệu EXP-034 và chuẩn hóa hệ thống nhật ký Excel',
  'Files_thay_đổi': 'logs/Daily_Journal.xlsx (mới), logs/experiment_log.xlsx (cập nhật 7 sheets), '
                    'docs/Nhat_ky_thuc_nghiem.md (mới)',
  'Nhiệm_vụ': 'Tổng hợp số liệu EXP-034, vẽ biểu đồ, lập nhật ký thực nghiệm chính thức và chuẩn '
              'hóa hệ thống lưu trữ sang file Excel đa trang tính.',
  'Khó_khăn_vấn_đề': 'PHÁT HIỆN MÂU THUẪN TRONG XỬ LÝ DỮ LIỆU: Silhouette score phải được tính '
                     'trên raw labels (đúng về toán học) nhưng nếu áp dụng nhầm hàm '
                     'align_labels_by_monetary() TRƯỚC khi tính Silhouette, giá trị metric sẽ bị '
                     'sai do thứ tự gán nhãn thay đổi. Silhouette chỉ đo chất lượng phân cụm hình '
                     'học, không phụ thuộc tên nhãn.',
  'Giải_pháp_khắc_phục': 'Giữ nguyên việc tính Silhouette trên raw labels. Chỉ áp dụng '
                         'align_labels_by_monetary() khi cần diễn giải và so sánh hồ sơ cụm giữa '
                         'các seed. Ghi chú rõ ràng sự khác biệt này trong nhật ký thực nghiệm.',
  'Kết_quả': 'logs/Daily_Journal.xlsx (10 bản ghi thực tế theo lịch sử git), '
             'logs/experiment_log.xlsx (7 sheets, 75 dòng), docs/Nhat_ky_thuc_nghiem.md hoàn '
             'chỉnh.',
  'Trạng_thái': 'HOÀN THÀNH',
  'Minh_chứng': 'logs/Daily_Journal.xlsx, logs/experiment_log.xlsx, docs/Nhat_ky_thuc_nghiem.md'},
 {'STT': 11,
  'Ng??y_Gi???': '2026-11-14 15:15',
  'Th??nh_vi??n': 'Tr?n Thi?n H?ng',
  'Git_Username': 'hung',
  'M??_Commit': '062dfd7',
  'Ti??u_?????_commit': 'EXP-035: Kiem tra dieu kien so sanh scaler (cung sample, cung k, cung '
                        'seed)',
  'Files_thay_?????i': 'src/run_exp035_scalers.py; outputs/tables/exp035_comparison_conditions.csv',
  'Nhi???m_v???': 'Doi chieu StandardScaler va RobustScaler de xac nhan cung sample 2.000 khach, '
                  'cung k (k=2 va k=3 duoc doi chieu rieng), cung random_state=42.',
  'Kh??_kh??n_v???n_?????': 'Khong thay doi dong thoi sample, k hoac seed vi se khong the tach '
                            'rieng anh huong cua scaler.',
  'Gi???i_ph??p_kh???c_ph???c': 'Kiem tra cau hinh trong script va bang ket qua; xac nhan tung cap '
                                'scaler co cung sample, k va seed.',
  'K???t_qu???': 'Dieu kien so sanh dat: hai scaler dung cung danh sach 2.000 CustomerID, cung k '
                 'trong tung cap va cung seed 42; scaler la yeu to duy nhat thay doi.',
  'Tr???ng_th??i': 'HO?N TH?NH',
  'Minh_ch???ng': 'outputs/tables/exp035_comparison_conditions.csv; src/run_exp035_scalers.py'},
 {'STT': '11',
  'Ngày_Giờ': '2026-11-14 15:15',
  'Thành_viên': 'Tran Thien Hung',
  'Git_Username': 'hung',
  'Tiêu_đề_commit': 'Da tinh ARI giua cac lan chay; giai thich dao dong Silhouette/Inertia',
  'Files_thay_đổi': 'docs/Nhat_ky_thuc_nghiem.md; logs/experiment_log.xlsx',
  'Nhiệm_vụ': 'Tinh Adjusted Rand Index (ARI) giua cac lan chay K-Means k=2 voi 5 seed; phan tich '
              'dao dong Silhouette va Inertia tren cung mau khach hang co dinh.',
  'Khó_khăn_vấn_đề': 'Doi nhan cluster co the chi la label switching; ARI khong phai accuracy.',
  'Giải_pháp_khắc_phục': 'So sanh nhan tren cung CustomerID bang ARI; tinh Silhouette tren raw '
                         'labels, chi can chinh nhan khi dien giai ho so cum.',
  'Kết_quả': 'ARI theo cap 0.974137-1.000000; Silhouette dao dong 0.297894-0.300278; Inertia dao '
             'dong 2855.72-2855.77. Phan nhom on dinh cao tren 5 seed.',
  'Trạng_thái': 'HOAN THANH',
  'Minh_chứng': 'Git commit 062dfd7; outputs/tables/exp034_seed_stability.csv; '
                'outputs/tables/exp034_pairwise_ari.csv; experiment_log.xlsx'},
 {'STT': 12,
  'Ngày_Giờ': '2026-11-15 16:24',
  'Thành_viên': 'Nguyễn Hoàng Quy',
  'Git_Username': 'HoangQuy / Haruki107206',
  'Tiêu_đề_commit': 'EXP-035: Kiểm tra điều kiện so sánh − cùng sample, cùng k, cùng seed',
  'Files_thay_đổi': 'src/run_exp035_scalers.py (mới), outputs/tables/exp035_scaling_comparison.csv '
                    '(4 bản ghi), outputs/tables/exp035_scaling_diagnostics.csv (6 bản ghi), '
                    'outputs/tables/exp035_cluster_profiles.csv, '
                    'outputs/figures/11_exp035_scaler_feature_distributions.png, '
                    'outputs/figures/11b_exp035_silhouette_comparison.png',
  'Nhiệm_vụ': 'Thực hiện EXP-035: Kiểm tra xem việc thay đổi phương pháp chuẩn hóa (StandardScaler '
              'vs RobustScaler) có ảnh hưởng đến chất lượng phân cụm không, trong điều kiện kiểm '
              'soát nghiêm ngặt: cùng mẫu 2.000 khách hàng cố định, cùng k=2 và k=3, cùng seed=42, '
              'cùng đặc trưng log1p(R, F, M).',
  'Khó_khăn_vấn_đề': 'PHÁT HIỆN LỖI SO SÁNH KHÔNG CÔNG BẰNG GIỮA CÁC SCALER: Lần chạy đầu tiên '
                     'dùng mẫu ngẫu nhiên khác nhau cho StandardScaler và RobustScaler (do quên '
                     'fix seed khi sample), dẫn đến kết quả Silhouette khác nhau không phản ánh '
                     'thực sự tác động của scaler mà do sự khác biệt trong dữ liệu đầu vào. Ngoài '
                     'ra phát hiện khoảng tứ phân vị (IQR) của Frequency sau log1p rất hẹp (Q1 ≈ '
                     'Q3), khiến RobustScaler chia cho IQR ≈ 0 gây giá trị vô cực (inf).',
  'Giải_pháp_khắc_phục': 'Khắc phục điều kiện so sánh: cố định cùng mẫu '
                         '(exp034_fixed_customer_sample.csv), cùng k, cùng seed=42 cho cả hai '
                         'scaler. Thêm kiểm tra: nếu IQR của bất kỳ đặc trưng nào = 0 sau log1p, '
                         'thay thế bằng std (fallback sang StandardScaler cho đặc trưng đó) và ghi '
                         'nhận trong nhật ký. In bảng thống kê phương sai và min/max sau scale để '
                         'đối chiếu.',
  'Kết_quả': 'IQR sau log1p an toàn (Recency=2.67, Frequency=1.39, Monetary=1.92) − không có nguy '
             'cơ chia 0. RobustScaler k=2: Silhouette=0.4457 (cao hơn StandardScaler=0.4433), '
             'DBI=0.843, CHI=2253.9. ARI giữa hai scaler cùng k=2: 0.8684 → kết quả phân cụm tương '
             'đồng cao. Kết luận: cả hai scaler cho chất lượng tương đương; StandardScaler được '
             'chọn vì dễ diễn giải hơn.',
  'Trạng_thái': 'HOÀN THÀNH',
  'Minh_chứng': 'src/run_exp035_scalers.py, outputs/tables/exp035_scaling_comparison.csv, '
                'outputs/tables/exp035_scaling_diagnostics.csv, '
                'outputs/figures/11_exp035_scaler_feature_distributions.png, '
                'outputs/figures/11b_exp035_silhouette_comparison.png'}]

df = pd.DataFrame(records)

# ============================================================
# Build Excel – white background, black text, Times New Roman
# ============================================================
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Nhật_Ký_Công_Việc"

thin_border = Border(
    left=Side(style="thin",   color="000000"),
    right=Side(style="thin",  color="000000"),
    top=Side(style="thin",    color="000000"),
    bottom=Side(style="thin", color="000000"),
)
header_font  = Font(name="Times New Roman", size=11, bold=True)
normal_font  = Font(name="Times New Roman", size=11)
center_align = Alignment(horizontal="center", vertical="top", wrap_text=True)
left_align   = Alignment(horizontal="left",   vertical="top", wrap_text=True)

# Header row
for c_idx, col in enumerate(df.columns, 1):
    cell = ws.cell(row=1, column=c_idx, value=col)
    cell.font      = header_font
    cell.alignment = center_align
    cell.border    = thin_border
ws.row_dimensions[1].height = 30

# Data rows
CENTER_COLS = {"STT", "Ngày_Giờ", "Git_Username", "Trạng_thái"}
for r_idx, row_data in enumerate(df.itertuples(index=False), 2):
    for c_idx, val in enumerate(row_data, 1):
        col_name = df.columns[c_idx - 1]
        cell = ws.cell(row=r_idx, column=c_idx, value=val)
        cell.font      = normal_font
        cell.border    = thin_border
        cell.alignment = center_align if col_name in CENTER_COLS else left_align
    ws.row_dimensions[r_idx].height = 95

# Column widths
col_widths = {
    "A":  5,   # STT
    "B": 18,   # Ngày_Giờ
    "C": 24,   # Thành_viên
    "D": 20,   # Git_Username
    "E": 18,   # Mã_Commit
    "F": 35,   # Tiêu_đề_commit
    "G": 38,   # Files_thay_đổi
    "H": 40,   # Nhiệm_vụ
    "I": 52,   # Khó_khăn_vấn_đề
    "J": 52,   # Giải_pháp_khắc_phục
    "K": 40,   # Kết_quả
    "L": 18,   # Trạng_thái
    "M": 42,   # Minh_chứng
}
for col_letter, width in col_widths.items():
    ws.column_dimensions[col_letter].width = width

ws.freeze_panes = "A2"

wb.save(journal_file)
print(f"Đã tạo Daily_Journal.xlsx: {journal_file}")

# ============================================================
# Sync Daily_Journal sheet into experiment_log.xlsx
# ============================================================
if log_xlsx.exists():
    with pd.ExcelWriter(log_xlsx, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name="Daily_Journal", index=False)
    print(f"Đã đồng bộ Daily_Journal vào {log_xlsx}")
