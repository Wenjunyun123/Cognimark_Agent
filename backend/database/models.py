"""
SQLAlchemy数据库模型定义
"""
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class ProductDB(Base):
    """产品表"""
    __tablename__ = "products"

    # 主键使用字符串ID，与原有系统保持一致
    product_id = Column(String(50), primary_key=True)
    title_en = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    price_usd = Column(Float, nullable=False)
    avg_rating = Column(Float, nullable=False)
    monthly_sales = Column(Integer, nullable=False)
    main_market = Column(String(50), nullable=False, index=True)
    tags = Column(Text)

    # 添加时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 添加索引优化查询
    __table_args__ = (
        Index('idx_category_market', 'category', 'main_market'),
        Index('idx_price_rating', 'price_usd', 'avg_rating'),
    )

    def to_dict(self):
        """转换为字典"""
        return {
            "product_id": self.product_id,
            "title_en": self.title_en,
            "category": self.category,
            "price_usd": self.price_usd,
            "avg_rating": self.avg_rating,
            "monthly_sales": self.monthly_sales,
            "main_market": self.main_market,
            "tags": self.tags,
        }


class ChatHistoryDB(Base):
    """聊天历史表"""
    __tablename__ = "chat_history"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(100), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # 添加复合索引优化查询
    __table_args__ = (
        Index('idx_session_timestamp', 'session_id', 'timestamp'),
    )

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


class UserDB(Base):
    """用户表（预留，用于未来扩展）"""
    __tablename__ = "users"

    user_id = Column(String(50), primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

    def to_dict(self):
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }
