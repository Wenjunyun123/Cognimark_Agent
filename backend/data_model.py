"""
数据模型 - 产品和产品存储

向后兼容层：新代码应使用 database.product_store
"""
from dataclasses import dataclass
from typing import List, Optional

# 导入基于数据库的实现
from database.product_store import Product, ProductStore, default_store

# 保持向后兼容的导出
__all__ = ["Product", "ProductStore", "default_store"]


