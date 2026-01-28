"""
SQLAlchemy数据库模型定义
"""
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class ProductDB(Base):
    """产品表

    用于存储电商商品信息
    包含基础商品字段：ID、标题、分类、价格、评分、销量、市场、标签
    """
    __tablename__ = "products"

    # ==================== 基础字段（必需） ====================
    product_id = Column(String(50), primary_key=True)
    title_en = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    price_usd = Column(Float, nullable=False)
    avg_rating = Column(Float, nullable=False)
    monthly_sales = Column(Integer, nullable=False)
    main_market = Column(String(50), nullable=False, index=True)
    tags = Column(Text)

    # ==================== 可选扩展字段 ====================
    # 以下字段为可选，用于未来扩展（如添加中文支持、描述、链接等）
    # 当前商品数据不使用这些字段，但保留以备将来需要
    title_zh = Column(String(500), nullable=True, comment="中文名称（可选）")
    description = Column(Text, nullable=True, comment="商品描述（可选）")
    resource_url = Column(String(1000), nullable=True, comment="商品链接（可选）")
    resource_type = Column(String(50), nullable=True, comment="资源类型（可选）")
    external_id = Column(String(100), unique=True, nullable=True, comment="外部系统ID（可选，用于去重）")

    # ==================== 时间戳 ====================
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ==================== 索引 ====================
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
            # 可选字段（可能为None）
            "title_zh": self.title_zh,
            "description": self.description,
            "resource_url": self.resource_url,
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


class ImportBatchDB(Base):
    """导入批次记录表"""
    __tablename__ = "import_batches"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_name = Column(String(200), comment="批次名称")
    source_file = Column(String(500), comment="来源文件名")
    total_records = Column(Integer, default=0, comment="总记录数")
    success_count = Column(Integer, default=0, comment="成功数量")
    failed_count = Column(Integer, default=0, comment="失败数量")
    skipped_count = Column(Integer, default=0, comment="跳过数量（已存在）")
    status = Column(String(50), default="pending", comment="状态: pending, processing, completed, failed")
    error_message = Column(Text, comment="错误信息")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, comment="完成时间")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "batch_name": self.batch_name,
            "source_file": self.source_file,
            "total_records": self.total_records,
            "success_count": self.success_count,
            "failed_count": self.failed_count,
            "skipped_count": self.skipped_count,
            "status": self.status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class RawProductDataDB(Base):
    """原始商品信息表 - 存储完整原始数据"""
    __tablename__ = "raw_product_data"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    external_id = Column(String(100), nullable=False, index=True, comment="关联ProductDB.external_id")
    raw_data = Column(Text, nullable=False, comment="JSON格式存储完整原始数据")
    source_file = Column(String(500), comment="来源文件名")
    source_row = Column(Integer, comment="原始行号")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 添加索引优化查询
    __table_args__ = (
        Index('idx_raw_external_id', 'external_id'),
    )

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "external_id": self.external_id,
            "raw_data": self.raw_data,
            "source_file": self.source_file,
            "source_row": self.source_row,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
