"""
向量存储模块

使用ChromaDB实现向量存储和相似度搜索
"""
from typing import List, Dict, Optional, Tuple
import os
from pathlib import Path

from .embeddings import EmbeddingGenerator


class VectorStore:
    """
    向量存储类

    使用ChromaDB存储和检索文本向量
    """

    def __init__(
        self,
        collection_name: str = "products",
        persist_dir: str = "./chroma_db",
        embedding_model: str = "all-MiniLM-L6-v2",
    ):
        """
        初始化向量存储

        Args:
            collection_name: 集合名称
            persist_dir: 持久化目录
            embedding_model: 嵌入模型名称
        """
        self.collection_name = collection_name
        self.persist_dir = Path(persist_dir)
        self.embedding_model = embedding_model

        # 初始化嵌入生成器
        self.embedding_generator = EmbeddingGenerator(embedding_model)

        # 延迟初始化ChromaDB客户端
        self._client = None
        self._collection = None

    def _init_client(self):
        """初始化ChromaDB客户端"""
        if self._client is None:
            try:
                import chromadb

                # 创建持久化目录
                self.persist_dir.mkdir(parents=True, exist_ok=True)

                # 使用新版ChromaDB客户端配置
                self._client = chromadb.PersistentClient(
                    path=str(self.persist_dir),
                )

                print(f"ChromaDB initialized at: {self.persist_dir}")

            except ImportError:
                raise ImportError(
                    "chromadb is not installed. "
                    "Run: pip install chromadb"
                )

    def _get_collection(self):
        """获取或创建集合"""
        self._init_client()

        if self._collection is None:
            # 获取或创建集合
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
            )

        return self._collection

    def add_products(
        self,
        products: List[Dict],
        id_field: str = "product_id",
        text_fields: List[str] = None,
    ):
        """
        添加产品到向量存储

        Args:
            products: 产品列表，每个产品是字典
            id_field: ID字段名
            text_fields: 用于生成嵌入的文本字段列表
                默认: ["title_en", "category", "tags"]
        """
        if text_fields is None:
            text_fields = ["title_en", "category", "tags"]

        collection = self._get_collection()

        # 准备数据
        ids = []
        documents = []
        metadatas = []

        for product in products:
            # 提取ID
            pid = str(product.get(id_field, ""))
            ids.append(pid)

            # 构建文档文本（用于语义搜索）
            text_parts = []
            for field in text_fields:
                value = product.get(field, "")
                if value:
                    text_parts.append(str(value))

            document = " ".join(text_parts)
            documents.append(document)

            # 元数据（用于过滤）
            metadata = {
                "category": product.get("category", ""),
                "price_usd": float(product.get("price_usd", 0)),
                "avg_rating": float(product.get("avg_rating", 0)),
                "main_market": product.get("main_market", ""),
            }
            metadatas.append(metadata)

        # 生成嵌入
        print(f"Generating embeddings for {len(documents)} products...")
        embeddings = self.embedding_generator.generate_batch(documents)

        # 添加到ChromaDB
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings.tolist(),
        )

        print(f"Added {len(ids)} products to vector store")

    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        语义搜索

        Args:
            query: 查询文本
            n_results: 返回结果数量
            where: 元数据过滤条件
                例如: {"category": "Electronics"}

        Returns:
            List[Dict]: 搜索结果，每个结果包含:
                - id: 产品ID
                - document: 文档文本
                - metadata: 元数据
                - score: 相似度分数（距离，越小越相似）
        """
        collection = self._get_collection()

        # 生成查询嵌入
        query_embedding = self.embedding_generator.generate(query)

        # 搜索
        results = collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results,
            where=where,
        )

        # 格式化结果
        formatted_results = []
        if results["ids"] and results["ids"][0]:
            for i, pid in enumerate(results["ids"][0]):
                formatted_results.append({
                    "id": pid,
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "score": 1 - results["distances"][0][i],  # 转换为相似度
                })

        return formatted_results

    def search_with_filters(
        self,
        query: str,
        category: Optional[str] = None,
        market: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        n_results: int = 5,
    ) -> List[Dict]:
        """
        带过滤条件的语义搜索

        Args:
            query: 查询文本
            category: 类别过滤
            market: 市场过滤
            min_price: 最低价格
            max_price: 最高价格
            n_results: 返回结果数量

        Returns:
            List[Dict]: 搜索结果
        """
        # 构建过滤条件
        where = {}
        if category:
            where["category"] = category
        if market:
            where["main_market"] = market

        # 价格范围需要特殊的过滤逻辑
        # ChromaDB不支持范围查询，需要后处理过滤

        # 执行搜索
        results = self.search(
            query=query,
            n_results=n_results * 2,  # 获取更多结果用于过滤
            where=where if where else None,
        )

        # 后处理价格过滤
        if min_price is not None or max_price is not None:
            filtered_results = []
            for result in results:
                price = result["metadata"]["price_usd"]
                if min_price is not None and price < min_price:
                    continue
                if max_price is not None and price > max_price:
                    continue
                filtered_results.append(result)

            results = filtered_results[:n_results]

        return results

    def get_product_count(self) -> int:
        """获取向量存储中的产品数量"""
        collection = self._get_collection()
        return collection.count()

    def delete_product(self, product_id: str):
        """从向量存储中删除产品"""
        collection = self._get_collection()
        collection.delete(ids=[product_id])

    def clear_collection(self):
        """清空集合"""
        collection = self._get_collection()
        # 删除并重新创建集合
        self._client.delete_collection(name=self.collection_name)
        self._collection = None
        print(f"Cleared collection: {self.collection_name}")

    def persist(self):
        """持久化数据到磁盘"""
        if self._client:
            # ChromaDB会自动持久化，这里可以触发显式持久化
            pass


def create_product_vector_store(products: List[Dict]) -> VectorStore:
    """
    创建并初始化产品向量存储

    Args:
        products: 产品列表

    Returns:
        VectorStore: 初始化后的向量存储
    """
    vector_store = VectorStore()
    vector_store.add_products(products)
    return vector_store
