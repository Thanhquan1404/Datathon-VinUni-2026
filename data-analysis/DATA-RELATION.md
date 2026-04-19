# Nhóm 1: Customer Journey (Hành trình khách hàng)

**Các bảng:**

* `web_traffic`
* `customers`
* `orders`
* `order_items`
* `reviews`
* `returns`
* `geography`
* `sample_submission` (thường không thuộc vận hành thực tế, có thể là bảng dự đoán)

## Quan hệ chính

```
web_traffic → customers → orders → order_items
                             ↓
                         reviews
                             ↓
                          returns
```

## Ý nghĩa nghiệp vụ

Đây là **toàn bộ vòng đời khách hàng**:

1. **Thu hút (Attraction)**

   * `web_traffic`: khách truy cập từ đâu, hành vi click

2. **Chuyển đổi (Conversion)**

   * `customers`: thông tin người dùng
   * `orders`: đơn hàng

3. **Chi tiết giao dịch**

   * `order_items`: sản phẩm trong từng đơn

4. **Sau mua (Post-purchase)**

   * `reviews`: đánh giá
   * `returns`: hoàn trả

5. **Phân tích địa lý**

   * `geography`: vùng miền → insight thị trường

=> Nhóm này phản ánh:

* Funnel bán hàng
* Trải nghiệm khách hàng
* Tỷ lệ chuyển đổi & giữ chân

# Nhóm 2: Internal Operations (Vận hành nội bộ)

**Các bảng:**

* `inventory`
* `shipments`
* `promotions`

## Quan hệ chính

```
    products → inventory → shipments → orders
                    ↑
                promotions
```

## Ý nghĩa nghiệp vụ

Đây là **hệ thống vận hành phía sau**:

1. **Quản lý hàng hóa**

   * `inventory`: tồn kho

2. **Giao hàng**

   * `shipments`: vận chuyển đơn hàng

3. **Kích cầu**

   * `promotions`: giảm giá, chiến dịch marketing

# Nhóm 3: Financial & Profit (Tài chính – lợi nhuận)

**Các bảng:**

* `payments`
* `sales`
* `products`

## Quan hệ chính

```
orders → payments
      → sales
      ↑
   products
```

## Ý nghĩa nghiệp vụ

Đây là **dòng tiền và lợi nhuận**:

1. **Doanh thu**

   * `sales`: doanh thu theo đơn/sản phẩm

2. **Thanh toán**

   * `payments`: phương thức, trạng thái thanh toán

3. **Sản phẩm**

   * `products`: giá, cost, margin

👉 Nhóm này phản ánh:

* Lợi nhuận (profit margin)
* Dòng tiền (cash flow)
* Hiệu quả sản phẩm

# Sơ đồ tổng thể

```
          (Customer Journey)
web_traffic → customers → orders → order_items → reviews/returns
                                        ↓
                                (---Financial---)
                                      payments
                                      sales
                                        ↑
                                     products
                                        ↑
                                (---Operations---)
                                    inventory → shipments
                                        ↑
                                    promotions
```