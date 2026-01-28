# -*- coding: utf-8 -*-
"""
数据库重置脚本

简化数据库结构，只保留必要的 products 表
"""
import os
import shutil
import sys
from datetime import datetime

# 设置输出编码
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 备份当前数据库
def backup_database():
    """备份当前数据库"""
    db_path = "cognimark.db"
    if os.path.exists(db_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"cognimark.db.backup_{timestamp}"
        shutil.copy2(db_path, backup_path)
        print(f"[OK] Database backed up to: {backup_path}")
        return backup_path
    return None


def reset_database():
    """重置数据库为简化版本"""
    from database.db_manager import engine
    from database.models import Base, ProductDB
    import sqlalchemy

    print("=" * 60)
    print("Database Reset Script")
    print("=" * 60)

    # 1. Backup
    backup_path = backup_database()

    # 2. Drop all tables
    print("\n[Dropping all tables...]")
    Base.metadata.drop_all(bind=engine)
    print("[OK] All tables dropped")

    # 3. Create only products table
    print("\n[Creating simplified products table...]")
    ProductDB.__table__.create(bind=engine, checkfirst=True)
    print("[OK] products table created")

    # 4. Insert sample data
    print("\n[Inserting sample data...]")
    from database.db_manager import get_db_context

    sample_products = [
        ProductDB(
            product_id="P001",
            title_en="Stainless Steel Insulated Water Bottle 500ml",
            category="Sports & Outdoor",
            price_usd=11.9,
            avg_rating=4.5,
            monthly_sales=2500,
            main_market="US",
            tags="eco-friendly,reusable,summer,travel"
        ),
        ProductDB(
            product_id="P002",
            title_en="Wireless Bluetooth Over-Ear Headphones",
            category="Consumer Electronics",
            price_usd=32.5,
            avg_rating=4.2,
            monthly_sales=1800,
            main_market="EU",
            tags="wireless,bluetooth,noise-canceling"
        ),
        ProductDB(
            product_id="P003",
            title_en="Ergonomic Adjustable Laptop Stand",
            category="Office Supplies",
            price_usd=18.0,
            avg_rating=4.7,
            monthly_sales=3200,
            main_market="US",
            tags="work-from-home,posture,aluminum"
        ),
        ProductDB(
            product_id="P004",
            title_en="Travel Universal Power Adapter with USB Ports",
            category="Travel Accessories",
            price_usd=15.9,
            avg_rating=4.3,
            monthly_sales=2100,
            main_market="Global",
            tags="travel,adapter,usb,universal"
        ),
        ProductDB(
            product_id="P005",
            title_en="Non-Slip Yoga Mat with Carrying Strap",
            category="Sports & Fitness",
            price_usd=19.9,
            avg_rating=4.6,
            monthly_sales=2800,
            main_market="US",
            tags="yoga,fitness,non-slip,eco-friendly"
        ),
        ProductDB(
            product_id="P006",
            title_en="Minimalist Clear Phone Case for iPhone",
            category="Mobile Accessories",
            price_usd=6.5,
            avg_rating=4.1,
            monthly_sales=4500,
            main_market="SEA",
            tags="phone,protective,transparent,budget"
        ),
    ]

    with get_db_context() as session:
        for product in sample_products:
            session.add(product)
        session.commit()
        print(f"[OK] Inserted {len(sample_products)} sample records")

    # 5. Verification
    print("\n" + "=" * 60)
    print("Verification:")
    print("=" * 60)

    with get_db_context() as session:
        inspector = sqlalchemy.inspect(session.bind)
        tables = inspector.get_table_names()

        print(f"\nCurrent tables: {', '.join(tables)}")

        count = session.query(ProductDB).count()
        print(f"products table records: {count}")

    print("\n" + "=" * 60)
    print("[OK] Database reset completed!")
    print("=" * 60)

    return True


if __name__ == "__main__":
    print("WARNING: This will delete all data and rebuild the database!")
    print("Type 'yes' to continue:")

    confirm = input("> ").strip()
    if confirm.lower() == "yes":
        reset_database()
    else:
        print("Operation cancelled")
