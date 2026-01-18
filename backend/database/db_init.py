"""
数据库初始化脚本
创建SQLite数据库并初始化数据
"""
import sys
import os

# 添加backend目录到Python路径
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, ProductDB
from database.crud import ProductCRUD

# 数据库配置
DATABASE_URL = "sqlite:///./cognimark.db"


def init_database():
    """初始化数据库"""
    print(f"正在创建数据库: {DATABASE_URL}")

    # 创建引擎
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # SQLite需要
        echo=True  # 打印SQL语句，便于调试
    )

    # 创建所有表
    Base.metadata.create_all(engine)
    print("[OK] Database tables created successfully")

    # 创建Session
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        # 初始化产品数据
        init_products(session)
        print("\n[OK] Data initialization completed")
        print(f"[OK] Database location: {os.path.abspath('./cognimark.db')}")

    except Exception as e:
        print(f"\n[ERROR] Data initialization failed: {e}")
        session.rollback()
        raise
    finally:
        session.close()

    return engine


def init_products(session):
    """初始化产品数据"""
    print("\n正在初始化产品数据...")

    # 检查是否已有数据
    existing = session.query(ProductDB).count()
    if existing > 0:
        print(f"Database already has {existing} products, skipping initialization")
        return

    # 产品数据（从data_model.py迁移）
    products_data = [
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

    # 批量创建产品
    product_crud = ProductCRUD(session)
    products = product_crud.bulk_create_products(products_data)

    print(f"[OK] Successfully created {len(products)} products:")
    for p in products:
        print(f"  - {p.product_id}: {p.title_en}")


if __name__ == "__main__":
    init_database()
