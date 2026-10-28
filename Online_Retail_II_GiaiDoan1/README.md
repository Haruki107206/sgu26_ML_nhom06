# Online Retail II – Giai đoạn 1: Khám phá dữ liệu và RFM

## Mục tiêu của giai đoạn này

Đây là phần khởi đầu của đồ án Machine Learning **“Phân khúc khách hàng bằng RFM và hành vi mua hàng”**. Notebook tập trung vào:

1. Đọc dữ liệu giao dịch gốc từ UCI Machine Learning Repository.
2. Kiểm tra cấu trúc, kiểu dữ liệu, giá trị thiếu, dữ liệu trùng, hóa đơn hủy và giao dịch bất thường.
3. Trực quan hóa một số đặc điểm giao dịch.
4. Nêu rõ quy tắc lọc dữ liệu phục vụ phân tích hành vi mua hàng.
5. Tạo bảng RFM ở mức khách hàng và lưu bảng này để sử dụng ở giai đoạn phân cụm.

**Lưu ý:** Gói khởi đầu không đóng gói dataset gốc vì file Excel lớn khoảng 43.5 MB. Chạy script tải dữ liệu từ nguồn chính thức; không dùng dữ liệu giả để thay thế kết quả thực nghiệm.

## Nguồn dữ liệu

- Dataset: [Online Retail II – UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/502/online+retail+ii)
- Tác giả: Daqing Chen.
- DOI: https://doi.org/10.24432/C5CG6D
- Giấy phép: CC BY 4.0; khi sử dụng cần ghi công nguồn dữ liệu.
- Dữ liệu giao dịch của một nhà bán lẻ trực tuyến tại Anh, từ 01/12/2009 đến 09/12/2011 theo mô tả của UCI.
