# BÁO CÁO PHÂN TÍCH HỆ THỐNG THÔNG TIN VÀ XỬ LÝ DỮ LIỆU RIKKEIEXPRESS
**Môn học:** Phân tích & Thiết kế Hệ thống Thông tin (IT105)  
**Bài tập:** Session 02 - Bài 1 (Vận dụng cơ bản)  

---

## PHẦN 1: PHÂN TÍCH LOGIC HỆ THỐNG THÔNG TIN

### 1. Phân tích 5 thành phần chính của HTTT đối với Phân hệ Báo cáo
Một Hệ thống thông tin (HTTT) hoàn chỉnh để hỗ trợ ra quyết định kinh doanh được cấu thành từ 5 thành phần:

1. **Phần cứng (Hardware):**
   * **Vai trò:** Máy chủ (Server) lưu trữ cơ sở dữ liệu giao dịch, thiết bị di động (PDA/Smartphone) của tài xế giao hàng, và máy tính/màn hình hiển thị báo cáo của Giám đốc Vùng.
   * **Tác động:** Đảm bảo tốc độ truyền tải dữ liệu realtime và độ ổn định của màn hình điều hành.
2. **Phần mềm (Software):**
   * **Vai trò:** Ứng dụng quản lý giao vận, module thu thập dữ liệu giao dịch, thuật toán/chương trình tính toán tổng hợp báo cáo (`process_revenue_report`) và giao diện hiển thị (Dashboard UI).
   * **Tác động:** Chuyển đổi dữ liệu thô từ máy chủ thành thông tin có ý nghĩa chỉ dẫn kinh doanh.
3. **Dữ liệu (Data):**
   * **Vai trò:** Danh sách các giao dịch phát sinh (`order_id`, `fee`, `status`).
   * **Tác động:** Là nguyên liệu đầu vào. Dữ liệu cần phản ánh chính xác trạng thái thực tế của đơn hàng (DELIVERED, CANCELLED, RETURNED).
4. **Quy trình (Procedures):**
   * **Vai trò:** Quy định nghiệp vụ giao vận và báo cáo: Quy trình xác nhận đơn hoàn thành, quy trình đối soát đơn bom/hoàn, quy trình tổng hợp số liệu cuối ngày, và quy định xét thưởng cho tài xế dựa trên KPI thành công.
   * **Tác động:** Định hình logic xử lý dữ liệu và xác định chuẩn mực đánh giá hiệu quả hoạt động.
5. **Con người (People):**
   * **Vai trò:** Tài xế (người cập nhật trạng thái đơn), Nhân viên đối soát, và Giám đốc Vùng (người sử dụng thông tin đầu ra).
   * **Tác động:** Giám đốc Vùng ra quyết định thưởng nóng và điều phối nhân sự; độ chính xác của quyết định phụ thuộc hoàn toàn vào chất lượng thông tin nhận được.

---

### 2. Dữ liệu thô (Data) vs Thông tin (Information) & Hậu quả đối với Giám đốc

* **Bản chất của luồng hiển thị hiện tại:**
  * Luồng legacy code chỉ hiển thị **Dữ liệu thô (Raw Data)** — những con số, chuỗi ký tự đơn lẻ chưa qua sàng lọc, phân loại hay tổng hợp (`"Đơn 01 - 15.000đ"`, `"Đơn 04 - -5.000đ"`...).
  * Dữ liệu thô **thiếu ngữ cảnh (Context)** và **chưa có ý nghĩa giá trị (Meaningful Insight)** đối với cấp quản lý.
* **Tầm quan trọng của Thông tin (Information):**
  * **Thông tin** là dữ liệu đã qua xử lý, tính toán, tổng hợp theo các chỉ số quản trị (KPIs) rõ ràng.
* **Hậu quả đối với việc ra quyết định của Giám đốc:**
  1. **Quá tải thông tin (Information Overload):** Giám đốc bị ngợp bởi hàng ngàn dòng chữ liên tục chạy trên màn hình, gây tốn thời gian và mệt mỏi.
  2. **Sai lệch thông số:** Dữ liệu thô chứa các đơn bị hủy (CANCELLED = 0đ) hoặc đơn hoàn (RETURNED = -5.000đ). Nếu không lọc, Giám đốc sẽ tính sai tổng doanh thu và đánh giá sai năng lực chi nhánh/tài xế.
  3. **Tê liệt khả năng ra quyết định (Decision Paralysis):** Giám đốc không thể so sánh hiệu quả giữa các chi nhánh, không biết chi nhánh nào hoạt động tốt để đưa ra chính xác quyết định thưởng nóng hay điều phối nhân sự.

---

## PHẦN 2: THIẾT KẾ GIẢI PHÁP VÀ MÃ NGUỒN PYTHON

### 1. Xác định Input và Output mong đợi

* **Dữ liệu đầu vào (Input):**
  * Danh sách giao dịch thô đẩy về từ máy chủ: `raw_orders` chứa danh sách dictionary với các trường `order_id`, `fee`, và `status`.
* **Thông tin đầu ra (Output):**
  * Báo cáo tổng hợp kinh doanh thể hiện 3 chỉ số chính:
    1. **Tổng doanh thu thực tế (Total Revenue):** Tổng tiền thu được từ các đơn giao thành công.
    2. **Số đơn giao thành công (Successful Orders Count):** Số lượng đơn hàng có trạng thái `DELIVERED`.
    3. **Doanh thu trung bình / đơn thành công (Average Revenue per Successful Order):** Giá trị trung bình mỗi đơn hoàn tất.

---

### 2. Quy tắc lọc bỏ bẫy đơn bom/đơn hoàn (Corrupted Transaction Trap)

* **Điều kiện hợp lệ:** Chỉ ghi nhận đơn hàng có `status == "DELIVERED"` và `fee > 0`.
* **Loại bỏ bẫy dữ liệu:**
  * Đơn hàng `CANCELLED` (phí 0đ): Loại bỏ hoàn toàn khỏi tổng doanh thu và tổng số đơn thành công.
  * Đơn hàng `RETURNED` (phí âm `-5.000đ` do chi phí hoàn kho): Không trừ trực tiếp vào doanh thu giao hàng thành công (hoặc xử lý riêng ở phân hệ chi phí vận hành), loại khỏi tính toán số đơn giao thành công để tránh làm méo mó đơn giá trung bình/đơn.

---

### 3. Mã nguồn Python đã tối ưu (`solution_bai1.py`)

```python
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
            # Loại bỏ bẫy phí âm hoặc không hợp lệ
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
```

---

### 4. Kết quả chạy thử nghiệm

Dữ liệu đầu vào gồm 5 đơn (3 đơn `DELIVERED`, 1 đơn `CANCELLED`, 1 đơn `RETURNED`).  
Kết quả hiển thị trên Dashboard:

```text
==================================================
   MÀN HÌNH ĐIỀU HÀNH DOANH THU - CHI NHÁNH HÀ NỘI
==================================================
1. Tổng doanh thu thực tế : 60,000 VNĐ
2. Số đơn giao thành công : 3 đơn
3. Doanh thu trung bình/đơn: 20,000.00 VNĐ/đơn
==================================================
```
