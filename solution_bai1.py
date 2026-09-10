"""
Chương trình xử lý báo cáo doanh thu giao hàng cho RikkeiExpress.
Lọc bỏ các đơn hàng không hợp lệ (CANCELLED, RETURNED, v.v.),
chỉ tính toán trên các đơn hàng giao thành công (DELIVERED).
"""

def process_revenue_report(order_list):
    """
    Xử lý danh sách đơn hàng thô và trả về các chỉ số tổng hợp:
    1. Tổng doanh thu thực tế
    2. Số đơn giao thành công
    3. Doanh thu trung bình trên mỗi đơn thành công
    """
    total_revenue = 0
    successful_orders_count = 0

    for order in order_list:
        # Quy tắc nghiệp vụ: Chỉ xử lý các đơn giao thành công (DELIVERED)
        if order.get("status") == "DELIVERED":
            fee = order.get("fee", 0)
            # Đảm bảo loại bỏ bẫy phí âm hoặc bất thường nếu có
            if fee > 0:
                total_revenue += fee
                successful_orders_count += 1

    # Tính doanh thu trung bình trên mỗi đơn thành công
    if successful_orders_count > 0:
        avg_revenue = total_revenue / successful_orders_count
    else:
        avg_revenue = 0.0

    return {
        "total_revenue": total_revenue,
        "successful_orders_count": successful_orders_count,
        "avg_revenue": avg_revenue
    }

def display_dashboard_report(branch_name, report_data):
    """
    Hiển thị báo cáo tổng hợp lên màn hình điều hành cho Giám đốc Vùng.
    """
    print(f"==================================================")
    print(f"   MÀN HÌNH ĐIỀU HÀNH DOANH THU - {branch_name.upper()}")
    print(f"==================================================")
    print(f"1. Tổng doanh thu thực tế : {report_data['total_revenue']:,} VNĐ")
    print(f"2. Số đơn giao thành công : {report_data['successful_orders_count']} đơn")
    print(f"3. Doanh thu trung bình/đơn: {report_data['avg_revenue']:,.2f} VNĐ/đơn")
    print(f"==================================================\n")

if __name__ == "__main__":
    # Dữ liệu thử nghiệm từ máy chủ (Bao gồm bẫy dữ liệu)
    order_data = [
        {"order_id": "01", "fee": 15000, "status": "DELIVERED"},
        {"order_id": "02", "fee": 20000, "status": "DELIVERED"},
        {"order_id": "03", "fee": 0, "status": "CANCELLED"},       # Đơn bị khách hủy
        {"order_id": "04", "fee": -5000, "status": "RETURNED"},    # Đơn hoàn phát sinh phí
        {"order_id": "05", "fee": 25000, "status": "DELIVERED"}
    ]

    # Xử lý báo cáo cho chi nhánh
    report = process_revenue_report(order_data)
    display_dashboard_report("Chi nhánh Hà Nội", report)
