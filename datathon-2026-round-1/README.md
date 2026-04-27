# **Data Schema - Hệ Thống Cơ Sở Dữ Liệu Thương Mại Điện Tử**

## 1. Tổng quan bộ dữ liệu

Bộ dữ liệu mô phỏng hoạt động của một nền tảng **thương mại điện tử** tại Việt Nam trong giai đoạn **2012 – 2022** (khoảng 10.5 năm).

| Bảng                  | Số dòng      | Số cột | Ý nghĩa chính                          | Loại bảng          |
|-----------------------|--------------|--------|----------------------------------------|--------------------|
| `products`            | 2,412        | 8      | Danh mục sản phẩm                      | **Dimension**      |
| `customers`           | 121,930      | 7      | Thông tin khách hàng                   | **Dimension**      |
| `geography`           | 39,948       | 4      | Thông tin địa lý (zip, thành phố, quận) | **Dimension**      |
| `promotions`          | 50           | 10     | Các chương trình khuyến mãi            | **Dimension**      |
| `orders`              | 646,945      | 8      | Đơn hàng chính                         | **Fact**           |
| `order_items`         | 714,669      | 7      | Chi tiết sản phẩm trong từng đơn hàng  | **Fact** (Bridge)  |
| `payments`            | 646,945      | 4      | Thông tin thanh toán                   | **Fact**           |
| `shipments`           | 566,067      | 4      | Thông tin vận chuyển & giao hàng       | **Fact**           |
| `returns`             | 39,939       | 7      | Đơn hàng hoàn trả                      | **Fact**           |
| `reviews`             | 113,551      | 7      | Đánh giá sản phẩm                      | **Fact**           |
| `inventory`           | 60,247       | 17     | Tồn kho theo ngày (snapshot)           | **Fact** (Snapshot)|
| `sales`               | 3,833        | 3      | Doanh thu & COGS theo ngày             | **Fact** (Aggregate)|
| `web_traffic`         | 3,652        | 7      | Lượng truy cập website                 | **Fact**           |

**Tổng số bản ghi**: hơn **1.7 triệu dòng**


## 2. Entity Relationship Diagram (Mô tả quan hệ)

![Profile Picture](./mermaid-diagram.svg)

## 3. Chi tiết Schema các bảng (Database Schema)

### **Dimension Tables**

#### **products**
```sql
CREATE TABLE products (
    product_id      INT PRIMARY KEY,
    product_name    VARCHAR(255),
    category        VARCHAR(100),
    segment         VARCHAR(100),
    size            VARCHAR(50),
    color           VARCHAR(50),
    price           DECIMAL(10,2),
    cogs            DECIMAL(10,2)      -- Cost of Goods Sold
);
```

#### **customers**
```sql
CREATE TABLE customers (
    customer_id         INT PRIMARY KEY,
    zip                 INT,
    city                VARCHAR(100),
    signup_date         DATE,
    gender              VARCHAR(20),
    age_group           VARCHAR(30),
    acquisition_channel VARCHAR(50)
);
```

#### **geography**
```sql
CREATE TABLE geography (
    zip         INT PRIMARY KEY,
    city        VARCHAR(100),
    region      VARCHAR(100),
    district    VARCHAR(100)
);
```

#### **promotions**
```sql
CREATE TABLE promotions (
    promo_id            VARCHAR(50) PRIMARY KEY,
    promo_name          VARCHAR(255),
    promo_type          VARCHAR(100),
    discount_value      DECIMAL(10,2),
    start_date          DATE,
    end_date            DATE,
    applicable_category VARCHAR(100),
    promo_channel       VARCHAR(100),
    stackable_flag      TINYINT(1),
    min_order_value     INT
);
```

### **Fact Tables**

#### **orders** (Fact trung tâm)
```sql
CREATE TABLE orders (
    order_id        INT PRIMARY KEY,
    order_date      DATE,
    customer_id     INT,
    zip             INT,
    order_status    VARCHAR(50),
    payment_method  VARCHAR(50),
    device_type     VARCHAR(50),
    order_source    VARCHAR(50),
    
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (zip) REFERENCES geography(zip)
);
```

#### **order_items**
```sql
CREATE TABLE order_items (
    order_id         INT,
    product_id       INT,
    quantity         INT,
    unit_price       DECIMAL(10,2),
    discount_amount  DECIMAL(10,2),
    promo_id         VARCHAR(50),
    promo_id_2       VARCHAR(50),
    
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id)   REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (promo_id)   REFERENCES promotions(promo_id)
);
```

#### **payments**
```sql
CREATE TABLE payments (
    order_id         INT PRIMARY KEY,
    payment_method   VARCHAR(50),
    payment_value    DECIMAL(12,2),
    installments     INT,
    
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
```

#### **shipments**
```sql
CREATE TABLE shipments (
    order_id        INT PRIMARY KEY,
    ship_date       DATE,
    delivery_date   DATE,
    shipping_fee    DECIMAL(10,2),
    
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
```

#### **returns**
```sql
CREATE TABLE returns (
    return_id        VARCHAR(50) PRIMARY KEY,
    order_id         INT,
    product_id       INT,
    return_date      DATE,
    return_reason    VARCHAR(255),
    return_quantity  INT,
    refund_amount    DECIMAL(10,2),
    
    FOREIGN KEY (order_id)   REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
```

#### **reviews**
```sql
CREATE TABLE reviews (
    review_id    VARCHAR(50) PRIMARY KEY,
    order_id     INT,
    product_id   INT,
    customer_id  INT,
    review_date  DATE,
    rating       TINYINT(1) CHECK (rating BETWEEN 1 AND 5),
    review_title VARCHAR(255),
    
    FOREIGN KEY (order_id)    REFERENCES orders(order_id),
    FOREIGN KEY (product_id)  REFERENCES products(product_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
```

#### **inventory** (Snapshot table)
```sql
CREATE TABLE inventory (
    snapshot_date      DATE,
    product_id         INT,
    stock_on_hand      INT,
    units_received     INT,
    units_sold         INT,
    stockout_days      INT,
    days_of_supply     DECIMAL(6,2),
    fill_rate          DECIMAL(5,2),
    stockout_flag      TINYINT(1),
    overstock_flag     TINYINT(1),
    reorder_flag       TINYINT(1),
    sell_through_rate  DECIMAL(5,2),
    product_name       VARCHAR(255),
    category           VARCHAR(100),
    segment            VARCHAR(100),
    year               INT,
    month              INT,
    
    PRIMARY KEY (snapshot_date, product_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
```

#### **sales** (Daily aggregate)
```sql
CREATE TABLE sales (
    Date     DATE PRIMARY KEY,
    Revenue  DECIMAL(15,2),
    COGS     DECIMAL(15,2)
);
```

#### **web_traffic**
```sql
CREATE TABLE web_traffic (
    date                    DATE,
    sessions                INT,
    unique_visitors         INT,
    page_views              INT,
    bounce_rate             DECIMAL(5,2),
    avg_session_duration_sec DECIMAL(10,2),
    traffic_source          VARCHAR(100),
    
    PRIMARY KEY (date, traffic_source)
);
```

## 4. Tính chất của bộ dữ liệu đã thỏa mãn

- **Referential Integrity**: Hoàn toàn tốt (0% orphan keys ở tất cả các quan hệ chính). Nhu cầu kiểm tra tính nhất quán của dữ liệu nhằm đảm bảo không có sai lệch trong phân tích business fact.
- **Thời gian**: Dữ liệu lịch sử rõ ràng từ 2012-07 đến 2022-12
- **Grain phù hợp**:
  - `orders` + `order_items`: Transaction grain
  - `inventory`: Daily snapshot grain
  - `sales`: Daily aggregate grain
- **Star Schema gần hoàn chỉnh**: Các bảng Dimension (products, customers, geography, promotions) liên kết tốt với Fact tables
- **Khả năng phân tích cao**: Có thể tính được:
  - Doanh thu, lợi nhuận theo sản phẩm/khách hàng/khu vực/thời gian
  - Tỷ lệ hoàn trả, đánh giá sản phẩm
  - Hiệu quả khuyến mãi
  - Tồn kho & chuỗi cung ứng
  - Hành vi truy cập website

## 5. Ý nghĩa kiến trúc hệ dữ liệu

Bộ dữ liệu này được thiết kế theo hướng **Data Warehouse / Business Intelligence** điển hình cho thương mại điện tử với các đặc điểm:

- **Customer-centric & Product-centric**: Tập trung mạnh vào trải nghiệm khách hàng và quản lý sản phẩm.
- **Full customer journey coverage**: Từ Traffic → Order → Payment → Shipment → Return/Review.
- **Supply chain visibility**: Có bảng `inventory` chi tiết với các chỉ số stockout, fill rate, reorder.
- **Promotion effectiveness**: Có thể phân tích tác động của khuyến mãi (dù `promo_id_2` có nhiều missing).
- **Geographic analysis**: Hỗ trợ phân tích theo vùng miền, thành phố, quận/huyện.

**Điểm mạnh**:
- Referential integrity rất cao → Dễ join, ít lỗi khi phân tích.
- Có cả transactional data lẫn snapshot data → Hỗ trợ nhiều loại báo cáo (historical + point-in-time).
- Dữ liệu sạch, ít missing values (trừ một số trường hợp hợp lý như `promo_id` và `applicable_category`).

**Điểm cần lưu ý**:
- `promo_id_2` có đến 99.97% missing → gần như không sử dụng được.
- `applicable_category` trong promotions missing 80% → cần xử lý khi phân tích khuyến mãi.
- Một số bảng (`sales`, `web_traffic`) là dữ liệu tổng hợp sẵn.
