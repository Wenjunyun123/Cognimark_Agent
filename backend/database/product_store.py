"""
基于数据库的产品知识库
替代原有的DataFrame实现
"""
from typing import List, Optional
from dataclasses import dataclass

from database.db_manager import get_db_context
from database.crud import ProductCRUD
from database.models import ProductDB


@dataclass
class Product:
    """产品数据类（保持与原API兼容）"""
    product_id: str
    title_en: str
    category: str
    price_usd: float
    avg_rating: float
    monthly_sales: int
    main_market: str
    tags: str

    @classmethod
    def from_db(cls, db_product: ProductDB) -> "Product":
        """从数据库模型转换为Product"""
        return cls(
            product_id=db_product.product_id,
            title_en=db_product.title_en,
            category=db_product.category,
            price_usd=db_product.price_usd,
            avg_rating=db_product.avg_rating,
            monthly_sales=db_product.monthly_sales,
            main_market=db_product.main_market,
            tags=db_product.tags or "",
        )


class ProductStore:
    """产品知识库封装 - 使用数据库"""

    def __init__(self):
        """初始化产品存储"""
        pass

    def list_products(self) -> List[Product]:
        """获取所有产品"""
        with get_db_context() as db:
            product_crud = ProductCRUD(db)
            db_products = product_crud.list_products()
            return [Product.from_db(p) for p in db_products]

    def get_product(self, product_id: str) -> Optional[Product]:
        """根据ID获取产品"""
        with get_db_context() as db:
            product_crud = ProductCRUD(db)
            db_product = product_crud.get_product(product_id)
            if db_product:
                return Product.from_db(db_product)
            return None

    def get_products_by_category(self, category: str) -> List[Product]:
        """根据类别获取产品"""
        with get_db_context() as db:
            product_crud = ProductCRUD(db)
            db_products = product_crud.get_products_by_category(category)
            return [Product.from_db(p) for p in db_products]

    def get_products_by_market(self, market: str) -> List[Product]:
        """根据市场获取产品"""
        with get_db_context() as db:
            product_crud = ProductCRUD(db)
            db_products = product_crud.get_products_by_market(market)
            return [Product.from_db(p) for p in db_products]


# 创建默认实例
default_store = ProductStore()
