from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Phân khúc khách hàng RFM", layout="wide")
st.title("Phân khúc khách hàng Online Retail II")
try:
    profiles = pd.read_csv(ROOT / "outputs/tables/final_cluster_profiles.csv")
    bundle = joblib.load(ROOT / "models/customer_clustering_pipeline.joblib")
except FileNotFoundError:
    st.error("Chạy python run_exp037.py với đường dẫn bảng RFM để tạo đầu ra.")
    st.stop()

overview, prediction = st.tabs(["Tổng quan", "Phân nhóm khách hàng"])
with overview:
    st.metric("Khách hàng", f"{profiles.customers.sum():,}")
    st.dataframe(profiles.round(2), hide_index=True)
    st.image(str(ROOT / "outputs/figures/pca_2d_clusters.png"))
    st.caption("PCA hiển thị hai chiều. K-Means sử dụng cả ba biến RFM sau chuẩn hóa.")
with prediction:
    with st.form("rfm"):
        r = st.number_input("Recency (ngày)", min_value=0, value=30)
        f = st.number_input("Frequency (hóa đơn)", min_value=1, value=5)
        m = st.number_input("Monetary (GBP)", min_value=0.0, value=1000.0)
        submitted = st.form_submit_button("Xem phân khúc")
    if submitted:
        raw = int(bundle["pipeline"].predict(pd.DataFrame(
            [[r, f, m]], columns=["Recency", "Frequency", "Monetary"]))[0])
        label = bundle["label_map"][raw]
        st.success(f"Cụm {label} · Giá trị mua trung vị {'cao hơn' if label else 'thấp hơn'}")
        st.write("Gợi ý: thử ưu đãi giữ chân." if label else "Gợi ý: thử nhắc mua lại hoặc ưu đãi kích hoạt.")
