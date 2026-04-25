import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

class DataPipeline:
    def __init__(self, base_dir: str, table_map: dict, relationships: dict):
        self.base_dir = Path(base_dir)
        self.table_map = table_map  
        self.relationships = relationships
        self.data = {}
        self._load_all()

    def _load_all(self):
        for table_name, rel_path in self.table_map.items():
            file_path = self.base_dir / rel_path
            if file_path.exists():
                df = pd.read_csv(file_path)
                self.data[table_name] = df
                print(f"[LOAD] {table_name}: {df.shape[0]} rows x {df.shape[1]} cols")
            else:
                print(f"[WARNING] Missing file: {file_path}")

    def check_structure(self):
        print("\n===== STRUCTURE & DATA TYPES =====")
        for name, df in self.data.items():
            print(f"\n--- {name} ---")
            print(f"Shape: {df.shape}")
            # Đếm số cột theo kiểu
            dtype_counts = df.dtypes.value_counts()
            print("Data types distribution:")
            for dt, count in dtype_counts.items():
                print(f"  {dt}: {count} columns")
            # In chi tiết tên cột và dtype
            for col, dt in df.dtypes.items():
                print(f"  {col}: {dt}")

    def standardize_dates_and_numbers(self, date_cols_map=None, numeric_cols_map=None):
        """
        date_cols_map: dict {table_name: [list of col names]}
        numeric_cols_map: dict {table_name: [list of col names]}
        """
        print("\n===== DATE STANDARDIZATION =====")
        if date_cols_map:
            for tbl, cols in date_cols_map.items():
                df = self.data[tbl]
                for col in cols:
                    if col in df.columns:
                        original_nan = df[col].isna().sum()
                        # Cố gắng chuyển sang datetime, lỗi gán NaT
                        converted = pd.to_datetime(df[col], errors='coerce', dayfirst=False)
                        new_nan = converted.isna().sum()
                        bad_rows = new_nan - original_nan
                        if bad_rows > 0:
                            print(f"  [DATE] {tbl}.{col}: {bad_rows} invalid dates set to NaT")
                        df[col] = converted
                        # Kiểm tra khoảng ngày hợp lý
                        if not converted.dropna().empty:
                            min_date = converted.min()
                            max_date = converted.max()
                            print(f"  [DATE] {tbl}.{col}: range {min_date.date()} to {max_date.date()}")
                            if min_date < pd.Timestamp('2010-01-01') or max_date > pd.Timestamp('2023-01-01'):
                                print(f"     WARNING: Out-of-business-range dates detected!")
                    else:
                        print(f"  [WARN] Column {col} not found in {tbl}")

    def check_referential_integrity(self):
        print("\n===== REFERENTIAL INTEGRITY =====")
        for child_table, fk_map in self.relationships.items():
            if child_table not in self.data:
                continue
            child_df = self.data[child_table]
            for fk_col, parent_table in fk_map.items():
                if parent_table not in self.data:
                    print(f"  [SKIP] Parent table {parent_table} not loaded")
                    continue
                if fk_col not in child_df.columns:
                    print(f"  [SKIP] FK column {fk_col} not in {child_table}")
                    continue
                parent_df = self.data[parent_table]
                parent_keys = set(parent_df.iloc[:, 0].dropna())  # giả định cột đầu tiên là PK (thường là ID)
                fk_values = child_df[fk_col].dropna()
                orphan_count = (~fk_values.isin(parent_keys)).sum()
                total = len(fk_values)
                print(f"  {child_table}.{fk_col} -> {parent_table}: {orphan_count}/{total} orphan keys ({orphan_count/total*100:.2f}%)")
                if orphan_count > 0:
                    # In vài ID mồ côi mẫu
                    orphans = child_df.loc[fk_values[~fk_values.isin(parent_keys)].index, fk_col].unique()[:5]
                    print(f"     Sample orphan keys: {list(orphans)}")

    def count_missing(self):
        print("\n===== MISSING VALUES =====")
        for name, df in self.data.items():
            missing = df.isna().sum()
            missing_pct = (missing / len(df)) * 100
            missing_table = pd.DataFrame({
                'column': missing.index,
                'missing_count': missing.values,
                'missing_pct': missing_pct.values
            }).query('missing_count > 0')
            if not missing_table.empty:
                print(f"\n--- {name} ---")
                print(missing_table.sort_values('missing_pct', ascending=False).to_string(index=False))
            else:
                print(f"  {name}: no missing values")

    
    def detect_outliers(self, outlier_config: dict, output_dir="outlier_plots"):
        """
        outlier_config: {table_name: [list of numerical columns]}.
        Sử dụng IQR để đếm outlier, vẽ boxplot lưu vào thư mục.
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        print("\n===== OUTLIER DETECTION (IQR) =====")
        for tbl, cols in outlier_config.items():
            if tbl not in self.data:
                continue
            df = self.data[tbl]
            for col in cols:
                if col not in df.columns:
                    continue
                series = df[col].dropna()
                if series.empty:
                    print(f"  {tbl}.{col}: all NaN, skip")
                    continue
                Q1 = series.quantile(0.25)
                Q3 = series.quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
                outliers = series[(series < lower) | (series > upper)]
                total = len(series)
                print(f"  {tbl}.{col}: {len(outliers)} outliers out of {total} ({len(outliers)/total*100:.2f}%)")
                print(f"     IQR: {IQR:.4f}, lower bound: {lower:.4f}, upper bound: {upper:.4f}")
                if len(outliers) > 0:
                    print(f"     Min outlier: {outliers.min():.4f}, Max outlier: {outliers.max():.4f}")
                # Vẽ boxplot
                plt.figure(figsize=(6, 4))
                sns.boxplot(x=series, color='skyblue')
                plt.title(f'{tbl} - {col} Boxplot')
                plt.tight_layout()
                plot_path = Path(output_dir) / f"{tbl}_{col}_boxplot.png"
                plt.savefig(plot_path)
                plt.close()
                print(f"     Boxplot saved: {plot_path}")
    
    def check_unit_consistency(self, monetary_cols: list, threshold=1e6):
        """Phát hiện cột tiền tệ có giá trị quá lớn bất thường (đơn vị sai)"""
        print("\n===== UNIT CONSISTENCY CHECK =====")
        for col_spec in monetary_cols:
            tbl, col = col_spec  # tuple (table, column)
            series = self.data[tbl][col].dropna()
            huge = series > threshold
            if huge.any():
                print(f"  {tbl}.{col}: {huge.sum()} values > {threshold:,} (possible unit error, e.g., VND vs thousands)")
                print(f"     Max: {series.max():,.2f}, Min: {series.min():,.2f}")
    # Ngoài ra có thể thêm kiểm tra phân phối log-scale


DATA_DIR = ''
TABLE_RELATIONSHIPS = {
    "orders":            {"customer_id": "customers"},
    "order_items":       {"order_id": "orders", "product_id": "products"},
    "payments":          {"order_id": "orders"},
    "shipments":         {"order_id": "orders"},
    "returns":           {"order_id": "orders", "product_id": "products"},
    "reviews":           {"customer_id": "customers", "product_id": "products", "order_id": "orders"},
    "inventory":         {"product_id": "products"},
    "web_traffic":       {}   
    # geography, promotions ít phụ thuộc, có thể kiểm tra nếu cần
}

TABLE_MAP = {
    # Master
    "products":    "master/products.csv",
    "customers":   "master/customers.csv",
    "promotions":  "master/promotions.csv",
    "geography":   "master/geography.csv",
    # Transaction
    "orders":      "transaction/orders.csv",
    "order_items": "transaction/order_items.csv",
    "payments":    "transaction/payments.csv",
    "shipments":   "transaction/shipments.csv",
    "returns":     "transaction/returns.csv",
    "reviews":     "transaction/reviews.csv",
    # Analytical
    "sales":       "analytical/sales.csv",
    # Operational
    "inventory":   "operational/inventory.csv",
    "web_traffic": "operational/web_traffic.csv",
}

DATE_COLS = {
    "orders":      ["order_date"],
    "customers": ["signup_date"],
    "shipments":   ["ship_date", "delivery_date"],
    "returns":     ["return_date"],
    "sales":       ["Date"],
    "inventory":   ["snapshot_date"],
    "web_traffic": ["date"],
    "promotions": ["start_date", "end_date"],
    "reviews": ["review_date"],
}

# Cột cần kiểm tra outlier
OUTLIER_COLS = {
    "order_items": ["quantity", "unit_price"],
    "payments":    ["amount"],
    "sales":       ["revenue"],
    "web_traffic": ["visits", "page_views"],
}

pipeline = DataPipeline(DATA_DIR, TABLE_MAP, TABLE_RELATIONSHIPS)

pipeline.check_structure()

pipeline.standardize_dates_and_numbers(DATE_COLS)

pipeline.check_referential_integrity()

pipeline.count_missing()