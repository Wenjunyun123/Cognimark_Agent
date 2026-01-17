from dataclasses import dataclass
from typing import List, Optional
import pandas as pd

@dataclass
class Product:
    product_id: str
    title_en: str
    category: str
    price_usd: float
    avg_rating: float
    monthly_sales: int
    main_market: str
    tags: str


class ProductStore:
    """产品知识库封装 (Knowledge Module)"""

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def list_products(self) -> List[Product]:
        return [Product(**row._asdict()) for row in self.df.itertuples(index=False)]

    def get_product(self, product_id: str) -> Optional[Product]:
        sub = self.df[self.df["product_id"] == product_id]
        if sub.empty:
            return None
        row = sub.iloc[0]
        return Product(
            product_id=row["product_id"],
            title_en=row["title_en"],
            category=row["category"],
            price_usd=float(row["price_usd"]),
            avg_rating=float(row["avg_rating"]),
            monthly_sales=int(row["monthly_sales"]),
            main_market=row["main_market"],
            tags=row["tags"],
        )

# -----------------------------
# Demo 数据
# -----------------------------
_products_data = [
    {
        "product_id": "P001",
        "title_en": "Stainless Steel Insulated Water Bottle 500ml",
        "category": "Sports & Outdoor",
        "price_usd": 11.9,
        "avg_rating": 4.6,
        "monthly_sales": 520,
        "main_market": "US",
        "tags": "eco-friendly, reusable, summer, travel",
    },
    {
        "product_id": "P002",
        "title_en": "Wireless Bluetooth Over-Ear Headphones",
        "category": "Consumer Electronics",
        "price_usd": 32.5,
        "avg_rating": 4.4,
        "monthly_sales": 310,
        "main_market": "EU",
        "tags": "music, commuting, noise-cancelling",
    },
    {
        "product_id": "P003",
        "title_en": "Ergonomic Adjustable Laptop Stand",
        "category": "Office Supplies",
        "price_usd": 18.0,
        "avg_rating": 4.5,
        "monthly_sales": 460,
        "main_market": "US",
        "tags": "work-from-home, posture, aluminum",
    },
    {
        "product_id": "P004",
        "title_en": "Travel Universal Power Adapter with USB Ports",
        "category": "Travel Accessories",
        "price_usd": 15.9,
        "avg_rating": 4.2,
        "monthly_sales": 390,
        "main_market": "Global",
        "tags": "travel, universal, compact",
    },
    {
        "product_id": "P005",
        "title_en": "Non-Slip Yoga Mat with Carrying Strap",
        "category": "Sports & Fitness",
        "price_usd": 19.9,
        "avg_rating": 4.3,
        "monthly_sales": 280,
        "main_market": "US",
        "tags": "fitness, yoga, home-workout",
    },
    {
        "product_id": "P006",
        "title_en": "Minimalist Clear Phone Case for iPhone",
        "category": "Mobile Accessories",
        "price_usd": 6.5,
        "avg_rating": 4.1,
        "monthly_sales": 800,
        "main_market": "SEA",
        "tags": "phone, protective, transparent, budget",
    },
]

# 初始化默认 Store 实例
df_products = pd.DataFrame(_products_data)
default_store = ProductStore(df_products)


