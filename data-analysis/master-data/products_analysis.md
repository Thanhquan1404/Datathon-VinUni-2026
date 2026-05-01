# Các nhận xét trong quá trình phân tích

* Quá trình phân tích cho thấy các mối quan hệ nhất định giữa category, segment, price và cogs. Đối với loại dữ liệu category, các cột dữ liệu đặc biệt phân bố trên từng segment khác nhau, không tồn tại một loại category nào mà xuất hiện ở tất cả segment. Đối với segmet và price có mối quan hệ phức tạp hơn; khi giá price thấp, cogs được kiểm soát tốt hơn ở hiệu xuất bán hàng thông qua slope và interception thể hiện biên ngày càng giảm; doanh nghiệp đang `gặp khó khăn trong vấn đề tiêu thụ sản phẩm highend` vì biên lợi nhuận giữa price và cogs gần như bằng nhau.
      
> ✔ Slope tăng theo quantile → cost structure thay đổi theo price \
> ✔ High price → biên lợi nhuận giảm \
> ✔ Data có heteroscedasticity \
> ✔ Model OLS sẽ che mất insight quan trọng 

# Báo Cáo Phân Tích Dữ Liệu — Bảng `products`

> **Analyst:** Data Analysis Division  
> **Scope:** EDA · Statistical Testing · Feature Engineering Roadmap  
> **Status:** Draft v1.0 — dựa trên kết quả thực nghiệm từ pipeline phân tích


## Mục Lục

1. [Tổng Quan Dữ Liệu](#1-tổng-quan-dữ-liệu)
2. [Normalize & Data Quality](#2-normalize--data-quality)
3. [Phân Tích Cấu Trúc Categorical](#3-phân-tích-cấu-trúc-categorical)
4. [Phân Tích Price & COGS](#4-phân-tích-price--cogs)
5. [Kiểm Định Thống Kê](#5-kiểm-định-thống-kê)
6. [Nhận Xét & Phản Biện Lập Luận](#6-nhận-xét--phản-biện-lập-luận)
7. [Feature Engineering Roadmap](#7-feature-engineering-roadmap)
8. [Định Hướng Mở Rộng Analysis](#8-định-hướng-mở-rộng-analysis)
9. [Gợi ý mở rộng Feature Engineer](#9-gợi-ý-mở-rộng-feature-engineering)


## 1. Tổng Quan Dữ Liệu

| Thuộc tính | Chi tiết |
|---|---|
| **Bảng** | `products` |
| **Cột phân tích** | `product_id`, `product_name`, `category`, `segment`, `size`, `color`, `price`, `cogs` |
| **Kiểu dữ liệu** | 6 categorical/str + 2 numeric (float64) |
| **Vấn đề phát hiện** | Whitespace thừa trong cột categorical → đã xử lý bằng `trim()` |

### 1.1 Cardinality Tổng Hợp

| Cột | # Unique Values | Giá trị |
|---|---|---|
| `category` | 4 | Streetwear, Casual, Outdoor, GenZ |
| `segment` | 8 | Everyday, Performance, Balanced, Standard, All-weather, Premium, Trendy, Activewear |
| `size` | 4 | S, M, L, XL |
| `color` | 10 | green, silver, pink, yellow, red, black, orange, blue, white, purple |


## 2. Normalize & Data Quality

### Kết Quả Trim Whitespace

Pipeline `normalize_string_columns()` phát hiện và loại bỏ khoảng trắng không đồng nhất trên toàn bộ cột categorical. Đây là bước **bắt buộc** trước mọi phân tích groupby hoặc crosstab — một ký tự space thừa đủ làm tách đôi một nhóm và sinh ra phantom categories trong downstream models.

> **Gợi mở:** Nếu dữ liệu đến từ nhiều nguồn nhập liệu (form, ETL, API), hãy kiểm tra thêm case sensitivity (`"streetwear"` vs `"Streetwear"`), encoding ký tự đặc biệt, và NULL representation (`"N/A"` vs `None` vs `""`). Một pipeline cleaning đúng nghĩa không dừng lại ở trim.


## 3. Phân Tích Cấu Trúc Categorical

### 3.1 Phân Bổ Revenue theo Category

| Category | Total Revenue (price) |
|---|---|
| **Streetwear** | 6,765.11 |
| Casual | 3,910.09 |
| Outdoor | 2,481.15 |
| GenZ | 2,212.79 |

→ Streetwear chiếm tỷ trọng lớn nhất (~44%). Đây là **dominant category** cần được ưu tiên trong mọi mô hình dự báo.

### 3.2 Phân Bổ Revenue theo Segment

| Segment | Total Revenue |
|---|---|
| Balanced | 9,230.24 |
| Everyday | 7,549.19 |
| Performance | 6,572.85 |
| All-weather | 3,864.75 |
| Standard | 2,928.59 |
| Activewear | 2,598.10 |
| Premium | 2,387.67 |
| Trendy | 2,212.79 |

→ Balanced + Everyday chiếm tổng ~47% revenue — hai segment này định hình phần lớn cấu trúc giá của toàn bộ catalog.

### 3.3 Cross-Tab: Category × Segment

```
segment     Activewear  All-weather  Balanced  Everyday  Performance  Premium  Standard  Trendy
category
Casual              32          169         0         0            0        0         0       0
GenZ                 0            0         0         0            0        0         0     148
Outdoor            566            0         0         0            0      177         0       0
Streetwear           0            0       306       405          347        0       262       0
```

**Nhận xét cấu trúc:**

- **Streetwear** phân phối trải dài qua 4 segments (Balanced, Everyday, Performance, Standard) → đây là category có chiều rộng thị trường nhất.
- **GenZ** chỉ xuất hiện trong một segment duy nhất (Trendy) → identity rất rõ ràng, hoặc là dữ liệu bị truncated.
- **Outdoor** tập trung vào Activewear (566) và Premium (177) → chiến lược định vị high-performance.
- **Casual** gần như độc quyền ở All-weather (169) + một phần nhỏ Activewear (32).

> **Gợi mở:** Sự phân tách gần như tuyệt đối giữa category và segment (không có category nào xuất hiện ở tất cả segments) đặt ra câu hỏi: đây là *design decision* trong catalog hay là *artifact* của cách dữ liệu được nhập? Nếu là design decision, thì mỗi cặp (category, segment) có thể được coi là một **product line** độc lập — và một mô hình pricing nên được fit riêng biệt cho từng line.

## 4. Phân Tích Price & COGS

### 4.1 Thống Kê Mô Tả

| Metric | Price | COGS |
|---|---|---|
| **Mean** | 4,928.22 | 3,868.35 |
| **Std** | 4,776.74 | 3,878.58 |
| **Min** | 9.06 | 5.18 |
| **Max** | 40,950.00 | 38,902.50 |
| **Chênh lệch mean (Gross Profit avg)** | **1,059.87** | — |

**Gross Margin trung bình ước tính:** `1,059.87 / 4,928.22 ≈ 21.5%`

> **Gợi mở:** Std ≈ Mean (hệ số biến thiên ~97%) là một tín hiệu mạnh của **right-skewed distribution** — có thể một số SKU premium đang kéo mean lên đáng kể. Hãy tự hỏi: giá trị mean có còn là đại lượng đại diện có ý nghĩa cho bài toán pricing không, hay median/percentile sẽ kể câu chuyện trung thực hơn?

### 4.2 Tương Quan Price ↔ COGS

| Phương pháp | Hệ số | p-value |
|---|---|---|
| **Pearson r** | **0.967** | 0.00 |
| **Spearman ρ** | **0.981** | 0.00 |

- Pearson và Spearman **hội tụ** (chênh lệch 0.014) → quan hệ vừa tuyến tính vừa đơn điệu mạnh.
- Không có bằng chứng về quan hệ phi tuyến đáng kể ở dạng gross (trước log-transform).

### 4.3 Kiểm Tra Homoscedasticity — Breusch-Pagan Test

| Chỉ số | Giá trị |
|---|---|
| LM statistic | **939.635** |
| p-value | **2.38e-206** |
| Kết luận | **Phương sai thay đổi (Heteroscedasticity)** |

→ Residuals KHÔNG đồng nhất phương sai. Điều này có nghĩa: **sai số của mô hình tuyến tính thô sẽ lớn hơn ở vùng giá cao** — đây là đặc điểm phổ biến với dữ liệu giá theo dạng multiplicative.

**Giải pháp khuyến nghị:**
- Log-transform cả `price` và `cogs` trước khi fit linear model
- Hoặc sử dụng **Weighted Least Squares (WLS)** / **Robust Regression (Huber, MM-estimator)**
- Kiểm tra liệu slope log-log có gần 1.0 không → nếu có, đây là **proportional margin model**

## 5. Kiểm Định Thống Kê

### 5.1 ANOVA — Price theo Category

| Chỉ số | Giá trị |
|---|---|
| F-statistic | **182.76** |
| p-value | **0.00000** |
| Kết luận | Có sự khác biệt giá có ý nghĩa giữa các category ✅ |

→ F = 182.76 là một giá trị rất cao — category là một **strong predictor** của price. Điều này ủng hộ việc đưa category vào bất kỳ mô hình hồi quy nào của price/cogs.

> **Gợi mở:** ANOVA xác nhận có *ít nhất một cặp* categories khác nhau — nhưng cặp nào? Post-hoc test (Tukey HSD hoặc Bonferroni) sẽ cho biết chính xác. Và quan trọng hơn: sự khác biệt đó có *business-meaningful* không? Streetwear đắt hơn GenZ vì cost of materials hay vì brand positioning?

### 5.2 Chi-Square (nếu áp dụng với dữ liệu thực)

Với cross-tab hiện tại, sự phân tách category × segment gần như deterministic (nhiều ô = 0) → Chi-Square test có thể không phản ánh đúng independence vì **expected frequencies** sẽ vi phạm điều kiện (< 5). Cần xem xét Fisher's Exact Test cho các cặp nhỏ.

## 6. Nhận Xét & Phản Biện Lập Luận

### Những điểm lập luận đúng hướng

✅ **"Dữ liệu sạch, có ý nghĩa"** — Sau normalize, dữ liệu đủ điều kiện phân tích. Tuy nhiên "sạch" ở đây mới ở mức syntactic (format), chưa phải semantic (ý nghĩa nghiệp vụ của từng giá trị).

✅ **"Tồn tại quan hệ ngầm định tuyến tính giữa price và cogs"** — Đúng, và được xác nhận bởi cả Pearson và Spearman ở mức r > 0.96. Đây là nền tảng hợp lý để xây dựng cost estimation model.

✅ **"Sử dụng residuals làm feature engineer"** — Đây là một insight có chiều sâu. Residual `e = cogs - (α·price + β)` encode phần COGS không được giải thích bởi price — có thể là margin exception, product-specific overhead, hoặc seasonal cost fluctuation.

### Những điểm cần đặt câu hỏi thêm

⚠️ **"Phân bổ thống kê đảm bảo an toàn cho hồi quy"** — Phát biểu này cần thận trọng hơn. Breusch-Pagan test cho thấy **homoscedasticity bị vi phạm** với LM = 939.6 — đây là vi phạm nghiêm trọng đối với OLS. "An toàn cho hồi quy" chỉ đúng nếu sử dụng log-transform hoặc robust estimator, không phải OLS thô.

> **Câu hỏi tự đặt:** Khi bạn nói "an toàn cho hồi quy", bạn đang đảm bảo điều kiện nào? Linearity, independence, normality của residuals, hay homoscedasticity? Mỗi điều kiện có một test riêng — và bỏ sót một điều kiện có thể làm confidence interval của mô hình trở nên vô nghĩa.

⚠️ **"Residuals giữa price và cogs làm feature cho order analysis"** — Đây là hướng đi đúng nhưng cần xác định rõ hơn: residual này được tính từ mô hình nào? OLS thô hay log-log? Nếu mô hình base bị bias do heteroscedasticity, residuals sinh ra cũng mang bias đó và downstream model sẽ học sai signal.

> **Câu hỏi tự đặt:** Residual của bạn đang đo "sự lệch so với quy luật chung", nhưng quy luật chung đó có phải là một hay nhiều đường? Nếu Outdoor và Streetwear có margin structure khác nhau, một mô hình global sẽ tạo ra residuals mang thông tin của category mixing — không phải cost anomaly.


## 7. Feature Engineering Roadmap

### 7.1 Features Từ Quan Hệ Price–COGS (Hiện Tại)

| Feature | Công thức | Ý nghĩa |
|---|---|---|
| `gross_margin` | `(price - cogs) / price` | Tỷ suất lợi nhuận gộp theo SKU |
| `gross_profit_abs` | `price - cogs` | Lợi nhuận gộp tuyệt đối |
| `cogs_price_ratio` | `cogs / price` | Tỷ lệ chi phí — nghịch đảo của margin |
| `log_price` | `log(price + 1)` | Stabilize variance, chuẩn bị cho log-linear model |
| `log_cogs` | `log(cogs + 1)` | Pair với log_price |
| `residual_cogs_ols` | `cogs - (α·price + β)` từ OLS | Deviation khỏi global cost rule |
| `residual_cogs_loglog` | Residual từ log-log model | Cleaner version sau khi xử lý heteroscedasticity |
| `margin_tier` | Phân bin `gross_margin` thành Low/Mid/High | Categorical signal cho classifier |

### 7.2 Features Mở Rộng từ Categorical Context

| Feature | Cách tạo | Ý nghĩa |
|---|---|---|
| `category_avg_price` | `groupby('category')['price'].transform('mean')` | Định vị SKU so với mean category |
| `segment_avg_margin` | `groupby('segment')['gross_margin'].transform('mean')` | Margin benchmark theo segment |
| `price_vs_cat_mean` | `price / category_avg_price` | Premium/discount so với category baseline |
| `is_outlier_margin` | IQR rule trên `gross_margin` | Flag SKUs có margin bất thường |
| `category_segment_combo` | Label encoding của `(category, segment)` | Capture interaction effect |

### 7.3 Features Khi Kết Hợp Bảng `orders`

| Feature | Logic | Phục vụ bài toán |
|---|---|---|
| `order_frequency` | Count orders per product_id | Demand proxy |
| `avg_order_qty` | Mean quantity per order | Batch sizing |
| `revenue_velocity` | `price × order_frequency` | High-value + high-demand detection |
| `cost_exposure` | `cogs × avg_order_qty` | Total cost per fulfillment cycle |
| `realized_margin` | `(price - cogs) × qty` | True profitability per order |
| `demand_tier` | Phân bin `order_frequency` | Segment products by demand level |

---

## 8. Định Hướng Mở Rộng Analysis

### 8.1 Từ Linear Analysis → Forecasting Analysis

**Bước đi khuyến nghị:**

```
EDA (hiện tại)
    ↓
Log-linear model: log(cogs) ~ log(price) + category + segment
    ↓
Residual analysis → residual_cogs feature
    ↓
Join với orders → time-series dimension
    ↓
Rolling cost estimation: cost_t = f(price_t, qty_t, segment, season)
    ↓
Forecasting model: LightGBM / Prophet / ARIMA-X
```

**Key considerations:**
- Cần time dimension trong bảng orders để đưa vào forecasting
- Nếu `cogs` thay đổi theo thời gian (inflation, supply chain), cần thiết kế lag features
- Target variable cho forecasting có thể là `total_cost_per_period = cogs × qty_ordered`

### 8.2 Từ Linear Analysis → High-Demand Product Group Analysis

**Khi mở rộng dimension sang orders:**

```
products ──join──> orders
                      ↓
           (category, segment, size, color) × demand_metrics
                      ↓
           Clustering: K-Means / DBSCAN trên [price, cogs, margin, frequency]
                      ↓
           Cluster profiles: High-demand-High-margin / High-demand-Low-margin / etc.
                      ↓
           Business action: inventory priority, pricing adjustment, promotion targeting
```

**Features đề xuất cho clustering:**

| Feature | Lý do |
|---|---|
| `log_price` | Normalize price scale |
| `gross_margin` | Profitability axis |
| `demand_tier` | Volume axis |
| `residual_cogs_loglog` | Cost efficiency signal |
| `price_vs_cat_mean` | Relative positioning |

### 8.3 Câu Hỏi Dẫn Hướng Cho Analyst

Trước khi mở rộng model, hãy tự đặt và trả lời các câu hỏi sau:

1. **"Đơn vị phân tích của tôi là SKU hay product line?"** — Câu trả lời sẽ quyết định granularity của feature engineering.
2. **"COGS trong bảng này là fixed hay variable?"** — Nếu variable theo quantity, bài toán trở thành cost curve estimation, không phải single-point regression.
3. **"Khi tôi nói 'dự đoán cost', tôi đang dự đoán cho một order đơn lẻ hay aggregate theo period?"** — Hai bài toán này cần architecture hoàn toàn khác nhau.
4. **"Residual COGS có phân phối gì? Có pattern theo category không?"** — Nếu có, đây là tín hiệu rằng nên fit model riêng biệt theo category.
5. **"Tôi sẽ validate mô hình forecasting với metric nào — MAPE, MAE hay RMSE?"** — Với dữ liệu có outliers lớn (max price 40,950 vs min 9.06), MAPE có thể misleading; MAE hoặc Quantile Loss thường robust hơn.

## Phụ Lục: Checklist Trước Khi Tiến Vào Modeling

- [ ] Xác nhận `cogs` là fully-loaded cost hay chỉ material cost
- [ ] Kiểm tra NULL và outliers trên `price` và `cogs` (min = 9.06 đáng ngờ cho một số categories)
- [ ] Fit log-log model và so sánh với OLS — chọn model có residuals đồng nhất phương sai hơn
- [ ] Join thử nghiệm với `orders` để kiểm tra có product_id nào trong `products` không có order không
- [ ] Xác định business definition của "high demand" — by count, by revenue, hay by margin contribution

## 9. Gợi ý mở rộng Feature Engineering


### 9.1. Chuyển sang **Forecasting Analysis** (dự báo chi phí / giá bán theo thời gian)

*Giả sử bảng `products` sẽ được join với các đơn hàng (orders) có timestamp.*

- **Tạo features dạng lag & rolling:**  
  - Nhóm theo `category` + `segment`, tính `cogs` trung bình động 7, 30 ngày.  
  - Phần dư `(cogs - rolling_mean_cogs)` làm feature đo lường biến động bất thường ngắn hạn.

- **Biến đổi log cho price & cogs** → sau đó mới tính residual log.  
  - Residual log = `log(cogs) - log(predicted_cogs)` ≈ **tỉ lệ chênh lệch phần trăm**, có tính ổn định phương sai hơn.

- **Thêm features ngoại sinh (exogenous):**  
  - Nếu có data về giá nguyên vật liệu thô, tỷ giá, mùa vụ → tạo `interaction` với residual để dự báo biến động chi phí.

- **Mô hình gợi ý:**  
  - Dùng **GARCH** (cho chuỗi residual có phương sai thay đổi) hoặc **Random Forest với quantile loss** để dự báo khoảng.

### 9.2. Chuyển sang **Group of High Demand Products Analysis** (phân tích nhóm sản phẩm có nhu cầu cao)

*Khi có thêm cột `sales_quantity` hoặc `order_frequency` (giả định bạn sẽ bổ sung).*

- **Xác định nhóm high‑demand:**  
  - Dùng phân phối `sales_quantity` theo từng `category` – top 20% sản phẩm có doanh số cao nhất.

- **Feature engineering đặc thù cho nhóm high‑demand:**  
  - **Margin ratio** = `(price - cogs) / price`  
  - **Residual phân cụm**: Huấn luyện riêng một mô hình hồi quy `price ~ cogs` **chỉ trên nhóm high‑demand**. Phần dư của mô hình này (gọi là `residual_high_demand`) thể hiện **lợi thế định giá** của sản phẩm bán chạy so với xu hướng chung.  
  - **Tương tác:** `category_Streetwear * residual_high_demand` có thể dự báo khả năng tăng giá mà không làm giảm nhu cầu.

- **Ứng dụng:**  
  - Phân tích nhóm này giúp trả lời: “Những sản phẩm bán chạy có mức chênh lệch price - cogs cao hơn hay thấp hơn trung bình? Có nên điều chỉnh giá vốn cho các đơn hàng lớn không?”

*Báo cáo được tổng hợp từ kết quả phân tích thực nghiệm. Mọi kết luận cần được đối chiếu với domain knowledge của team nghiệp vụ trước khi đưa vào production pipeline.*
