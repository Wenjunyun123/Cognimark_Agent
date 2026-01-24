"""
CRUD操作 - 数据库访问层
"""
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, desc
from typing import List, Optional
from datetime import datetime
import uuid

from .models import ProductDB, ChatHistoryDB, UserDB, ImportBatchDB, RawProductDataDB, Base


class ProductCRUD:
    """产品CRUD操作"""

    def __init__(self, session: Session):
        self.session = session

    def get_product(self, product_id: str) -> Optional[ProductDB]:
        """根据ID获取产品"""
        return self.session.query(ProductDB).filter(
            ProductDB.product_id == product_id
        ).first()

    def list_products(self) -> List[ProductDB]:
        """获取所有产品"""
        return self.session.query(ProductDB).all()

    def get_products_by_category(self, category: str) -> List[ProductDB]:
        """根据类别获取产品"""
        return self.session.query(ProductDB).filter(
            ProductDB.category == category
        ).all()

    def get_products_by_market(self, market: str) -> List[ProductDB]:
        """根据市场获取产品"""
        return self.session.query(ProductDB).filter(
            ProductDB.main_market == market
        ).all()

    def create_product(self, product_data: dict) -> ProductDB:
        """创建新产品"""
        product = ProductDB(**product_data)
        self.session.add(product)
        self.session.commit()
        self.session.refresh(product)
        return product

    def update_product(self, product_id: str, product_data: dict) -> Optional[ProductDB]:
        """更新产品"""
        product = self.get_product(product_id)
        if not product:
            return None

        for key, value in product_data.items():
            if hasattr(product, key):
                setattr(product, key, value)

        product.updated_at = datetime.utcnow()
        self.session.commit()
        self.session.refresh(product)
        return product

    def delete_product(self, product_id: str) -> bool:
        """删除产品"""
        product = self.get_product(product_id)
        if not product:
            return False

        self.session.delete(product)
        self.session.commit()
        return True

    def bulk_create_products(self, products_data: List[dict]) -> List[ProductDB]:
        """批量创建产品"""
        products = [ProductDB(**data) for data in products_data]
        self.session.add_all(products)
        self.session.commit()
        for product in products:
            self.session.refresh(product)
        return products


class ChatHistoryCRUD:
    """聊天历史CRUD操作"""

    def __init__(self, session: Session):
        self.session = session

    def create_message(
        self,
        session_id: str,
        role: str,
        content: str
    ) -> ChatHistoryDB:
        """创建新消息"""
        message = ChatHistoryDB(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role=role,
            content=content,
            timestamp=datetime.utcnow()
        )
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)
        return message

    def get_session_messages(self, session_id: str) -> List[ChatHistoryDB]:
        """获取会话的所有消息"""
        return self.session.query(ChatHistoryDB).filter(
            ChatHistoryDB.session_id == session_id
        ).order_by(ChatHistoryDB.timestamp).all()

    def get_recent_messages(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[ChatHistoryDB]:
        """获取最近的N条消息"""
        return self.session.query(ChatHistoryDB).filter(
            ChatHistoryDB.session_id == session_id
        ).order_by(desc(ChatHistoryDB.timestamp)).limit(limit).all()

    def delete_session(self, session_id: str) -> int:
        """删除整个会话"""
        count = self.session.query(ChatHistoryDB).filter(
            ChatHistoryDB.session_id == session_id
        ).delete()
        self.session.commit()
        return count

    def get_all_sessions(self) -> List[str]:
        """获取所有会话ID列表"""
        result = self.session.query(ChatHistoryDB.session_id).distinct().all()
        return [row[0] for row in result]

    def delete_message(self, message_id: str) -> bool:
        """删除单条消息"""
        message = self.session.query(ChatHistoryDB).filter(
            ChatHistoryDB.id == message_id
        ).first()
        if not message:
            return False

        self.session.delete(message)
        self.session.commit()
        return True


class UserCRUD:
    """用户CRUD操作"""

    def __init__(self, session: Session):
        self.session = session

    def get_user(self, user_id: str) -> Optional[UserDB]:
        """根据ID获取用户"""
        return self.session.query(UserDB).filter(
            UserDB.user_id == user_id
        ).first()

    def get_user_by_email(self, email: str) -> Optional[UserDB]:
        """根据邮箱获取用户"""
        return self.session.query(UserDB).filter(
            UserDB.email == email
        ).first()

    def create_user(self, user_data: dict) -> UserDB:
        """创建新用户"""
        user = UserDB(**user_data)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def update_last_login(self, user_id: str) -> bool:
        """更新最后登录时间"""
        user = self.get_user(user_id)
        if not user:
            return False

        user.last_login = datetime.utcnow()
        self.session.commit()
        return True

    def list_users(self) -> List[UserDB]:
        """获取所有用户"""
        return self.session.query(UserDB).all()


class ImportBatchCRUD:
    """导入批次CRUD操作"""

    def __init__(self, session: Session):
        self.session = session

    def create_batch(self, batch_data: dict) -> ImportBatchDB:
        """创建新导入批次"""
        batch = ImportBatchDB(**batch_data)
        self.session.add(batch)
        self.session.commit()
        self.session.refresh(batch)
        return batch

    def get_batch(self, batch_id: str) -> Optional[ImportBatchDB]:
        """根据ID获取批次"""
        return self.session.query(ImportBatchDB).filter(
            ImportBatchDB.id == batch_id
        ).first()

    def update_batch(self, batch_id: str, update_data: dict) -> Optional[ImportBatchDB]:
        """更新批次状态"""
        batch = self.get_batch(batch_id)
        if not batch:
            return None

        for key, value in update_data.items():
            if hasattr(batch, key):
                setattr(batch, key, value)

        self.session.commit()
        self.session.refresh(batch)
        return batch

    def list_batches(self, limit: int = 50) -> List[ImportBatchDB]:
        """获取导入批次列表"""
        return self.session.query(ImportBatchDB).order_by(
            desc(ImportBatchDB.created_at)
        ).limit(limit).all()

    def get_product_by_external_id(self, external_id: str) -> Optional[ProductDB]:
        """根据外部ID获取商品（用于去重检查）"""
        return self.session.query(ProductDB).filter(
            ProductDB.external_id == external_id
        ).first()


class RawProductDataCRUD:
    """原始商品数据CRUD操作"""

    def __init__(self, session: Session):
        self.session = session

    def create_raw_data(self, raw_data: dict) -> RawProductDataDB:
        """创建原始数据记录"""
        data = RawProductDataDB(**raw_data)
        self.session.add(data)
        self.session.commit()
        self.session.refresh(data)
        return data

    def get_raw_data_by_external_id(self, external_id: str) -> Optional[RawProductDataDB]:
        """根据external_id获取原始数据"""
        return self.session.query(RawProductDataDB).filter(
            RawProductDataDB.external_id == external_id
        ).first()

    def bulk_create_raw_data(self, raw_data_list: List[dict]) -> List[RawProductDataDB]:
        """批量创建原始数据记录"""
        raw_records = [RawProductDataDB(**data) for data in raw_data_list]
        self.session.add_all(raw_records)
        self.session.commit()
        for record in raw_records:
            self.session.refresh(record)
        return raw_records

    def update_raw_data(self, external_id: str, update_data: dict) -> Optional[RawProductDataDB]:
        """更新原始数据"""
        raw_data = self.get_raw_data_by_external_id(external_id)
        if not raw_data:
            return None

        for key, value in update_data.items():
            if hasattr(raw_data, key):
                setattr(raw_data, key, value)

        self.session.commit()
        self.session.refresh(raw_data)
        return raw_data

    def delete_raw_data(self, external_id: str) -> bool:
        """删除原始数据"""
        raw_data = self.get_raw_data_by_external_id(external_id)
        if not raw_data:
            return False

        self.session.delete(raw_data)
        self.session.commit()
        return True
