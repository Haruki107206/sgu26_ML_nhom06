# Kế hoạch triển khai đồ án

## Tên đề tài
Phân khúc khách hàng bằng RFM và hành vi mua hàng trên bộ dữ liệu Online Retail II.

## Câu hỏi nghiên cứu dự kiến
Có thể chia khách hàng thành những nhóm có hành vi mua hàng khác nhau dựa trên Recency, Frequency và Monetary hay không? Các thuật toán phân cụm cho ra cấu trúc cụm khác nhau như thế nào, và nhóm nào có thể diễn giải được về mặt kinh doanh?

## Các mốc thực hiện

1. **Dữ liệu và EDA:** lấy dữ liệu chính thức, kiểm tra chất lượng, khám phá giao dịch, ghi nhận các quy tắc xử lý và tạo bảng RFM.
2. **Tiền xử lý và baseline:** lựa chọn tập đặc trưng, xử lý độ lệch phân phối nếu hợp lý, chuẩn hóa đặc trưng và xác định baseline.
3. **Mô hình hóa:** K-Means, Hierarchical Clustering và DBSCAN; lựa chọn tham số dựa trên tập/thiết kế đánh giá phù hợp, không dùng kết quả test để tinh chỉnh.
4. **Đánh giá:** Silhouette Score, Inertia khi phù hợp, kích thước và đặc trưng từng cụm; xem xét độ nhạy tham số và khả năng diễn giải.
5. **Hoàn thiện:** thảo luận kết quả, hạn chế, nhật ký thực nghiệm, báo cáo, slide, README và demo nếu khả thi.
