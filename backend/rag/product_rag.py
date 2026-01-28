# -*- coding: utf-8 -*-
"""
通用 RAG 检索系统

通过配置文件控制一切，支持任意数据表的检索
"""
import re
from typing import List, Dict, Optional
from pathlib import Path

from database.db_manager import get_db_context
from database.models import ProductDB
from .rag_config import (
    DATA_SOURCE_CONFIGS,
    detect_data_source,
    get_config,
    ENABLE_KEYWORD_SEARCH,
    ENABLE_VECTOR_SEARCH,
    VECTOR_DB_DIR,
    EMBEDDING_MODEL,
    KEYWORD_BOOST_SCORE,
)


class ProductRAG:
    """
    商品检索系统

    用于检索商品信息，支持关键词匹配和向量语义搜索

    使用方式：
        rag = ProductRAG()
        results = rag.search("查找便宜的商品")

    配置方式：修改 rag_config.py 文件
    """

    def __init__(self):
        """初始化商品检索系统"""
        self.vector_stores = {}  # 缓存向量存储
        self._init_vector_stores()

    def _init_vector_stores(self):
        """延迟初始化向量存储"""
        if not ENABLE_VECTOR_SEARCH:
            return

        try:
            from .embeddings import EmbeddingGenerator
            import chromadb

            # 创建向量数据库目录
            Path(VECTOR_DB_DIR).mkdir(parents=True, exist_ok=True)
            self._chroma_client = chromadb.PersistentClient(path=VECTOR_DB_DIR)
            self._embedding_generator = EmbeddingGenerator(EMBEDDING_MODEL)

            # 为每个数据源创建或获取集合
            for source_name, config in DATA_SOURCE_CONFIGS.items():
                collection_name = config.get("collection_name", f"{source_name}_vector")
                collection = self._chroma_client.get_or_create_collection(name=collection_name)
                self.vector_stores[source_name] = collection

                # 检查是否需要重建索引
                count = collection.count()
                if count == 0:
                    self._build_index(source_name)

        except ImportError:
            print("[ProductRAG] 警告: chromadb 未安装，向量搜索功能不可用")

    def _build_index(self, source_name: str):
        """为指定数据源构建向量索引"""
        config = get_config(source_name)
        if not config:
            return

        try:
            from database.models import ProductDB

            # 获取数据库数据
            with get_db_context() as session:
                # 从 ProductDB 表获取所有产品数据
                if config.get("db_model") == "ProductDB":
                    records = session.query(ProductDB).all()
                else:
                    records = []

                if not records:
                    print(f"[ProductRAG] 数据源 {source_name} 没有数据")
                    return

                # 准备索引数据
                ids = []
                documents = []
                metadatas = []

                index_fields = config.get("index_fields", [])
                numeric_fields = config.get("numeric_fields", {})

                for record in records:
                    rid = str(getattr(record, config["display_fields"]["id"]))
                    ids.append(rid)

                    # 合并索引字段生成文档
                    text_parts = []
                    for field in index_fields:
                        value = getattr(record, field, None)
                        if value:
                            text_parts.append(str(value))

                    # 添加数值字段的文本表示
                    for field, template in numeric_fields.items():
                        value = getattr(record, field, None)
                        if value is not None:
                            text_parts.append(template.format(value=value))

                    documents.append(" ".join(text_parts).strip())

                    # 元数据
                    metadata = {}
                    for key, field in config["display_fields"].items():
                        value = getattr(record, field, None)
                        if value and key not in ["id", "title_fallback"]:
                            metadata[key] = str(value)
                    metadatas.append(metadata)

                # 生成嵌入并添加到向量库
                print(f"[ProductRAG] 正在为 {source_name} 生成向量索引 ({len(documents)} 条)...")
                embeddings = self._embedding_generator.generate_batch(documents)

                collection = self.vector_stores.get(source_name)
                if collection:
                    collection.add(
                        ids=ids,
                        documents=documents,
                        metadatas=metadatas,
                        embeddings=embeddings.tolist(),
                    )
                    print(f"[ProductRAG] {source_name} 索引构建完成")

        except Exception as e:
            print(f"[ProductRAG] 索引构建失败: {e}")

    def search(
        self,
        query: str,
        source_name: Optional[str] = None,
        top_k: int = 10,
    ) -> Dict:
        """
        通用检索接口

        Args:
            query: 用户查询
            source_name: 指定数据源（不指定则自动检测）
            top_k: 返回结果数量

        Returns:
            检索结果字典
        """
        # 自动检测数据源
        if source_name is None:
            detected_sources = detect_data_source(query)
            # 如果检测到多个，使用第一个
            source_name = detected_sources[0] if detected_sources else "products"

        config = get_config(source_name)
        if not config:
            return {"query": query, "total": 0, "results": [], "source": None}

        results = []

        # 1. 关键词精确匹配
        if ENABLE_KEYWORD_SEARCH:
            keyword_results = self._keyword_search(query, config)
            results.extend(keyword_results)

        # 2. 向量语义搜索
        if ENABLE_VECTOR_SEARCH and source_name in self.vector_stores:
            vector_results = self._vector_search(query, config, top_k * 2)
            # 合并去重
            results = self._merge_results(results, vector_results, top_k)

        return {
            "query": query,
            "source": source_name,
            "total": len(results),
            "results": results[:top_k],
        }

    def _keyword_search(self, query: str, config: Dict) -> List[Dict]:
        """关键词精确匹配搜索"""
        results = []
        seen_ids = set()

        try:
            from database.models import ProductDB

            with get_db_context() as session:
                search_fields = config.get("search_fields", [])
                display_fields = config.get("display_fields", {})

                # 策略1: 精确匹配整个查询
                for field in search_fields:
                    matches = session.query(ProductDB).filter(
                        getattr(ProductDB, field).contains(query)
                    ).limit(50).all()

                    for record in matches:
                        rid = str(getattr(record, display_fields["id"]))
                        if rid in seen_ids:
                            continue
                        seen_ids.add(rid)

                        # 构建元数据
                        metadata = {}
                        for key, field_name in display_fields.items():
                            if key not in ["id", "title_fallback"]:
                                value = getattr(record, field_name, None)
                                if value is not None:
                                    metadata[key] = str(value)

                        results.append({
                            "id": rid,
                            "title": self._get_display_title(record, config),
                            "url": str(getattr(record, display_fields.get("url", ""), "")),
                            "score": 1.0 * KEYWORD_BOOST_SCORE,  # 精确匹配高分
                            "source": "keyword_exact",
                            "metadata": metadata,  # 添加元数据
                        })

                # 策略2: 分词匹配（如果精确匹配结果少）
                if len(results) < 10:
                    keywords = self._tokenize_query(query)
                    for keyword in keywords:
                        if len(keyword) < 2:
                            continue

                        for field in search_fields:
                            matches = session.query(ProductDB).filter(
                                getattr(ProductDB, field).contains(keyword)
                            ).limit(50).all()

                            for record in matches:
                                rid = str(getattr(record, display_fields["id"]))
                                if rid in seen_ids:
                                    continue
                                seen_ids.add(rid)

                                # 构建元数据
                                metadata = {}
                                for key, field_name in display_fields.items():
                                    if key not in ["id", "title_fallback"]:
                                        value = getattr(record, field_name, None)
                                        if value is not None:
                                            metadata[key] = str(value)

                                results.append({
                                    "id": rid,
                                    "title": self._get_display_title(record, config),
                                    "url": str(getattr(record, display_fields.get("url", ""), "")),
                                    "score": 0.8 * KEYWORD_BOOST_SCORE,
                                    "source": "keyword_partial",
                                    "metadata": metadata,  # 添加元数据
                                })

        except Exception as e:
            print(f"[ProductRAG] 关键词搜索错误: {e}")

        return results

    def _vector_search(self, query: str, config: Dict, top_k: int) -> List[Dict]:
        """向量语义搜索"""
        results = []

        try:
            source_name = list(DATA_SOURCE_CONFIGS.keys())[
                list(DATA_SOURCE_CONFIGS.values()).index(config)
            ]
            collection = self.vector_stores.get(source_name)
            if not collection:
                return results

            # 生成查询向量
            query_embedding = self._embedding_generator.generate(query)

            # 搜索
            search_results = collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k,
            )

            # 格式化结果
            if search_results["ids"] and search_results["ids"][0]:
                for i, rid in enumerate(search_results["ids"][0]):
                    # 获取完整元数据
                    metadata = search_results["metadatas"][0][i]
                    result_item = {
                        "id": rid,
                        "title": search_results["documents"][0][i],
                        "url": metadata.get("url", ""),
                        "score": 1 - search_results["distances"][0][i],  # 转换为相似度
                        "source": "vector",
                        "metadata": metadata,  # 保存完整元数据
                    }
                    results.append(result_item)

        except Exception as e:
            print(f"[ProductRAG] 向量搜索错误: {e}")

        return results

    def _merge_results(
        self,
        keyword_results: List[Dict],
        vector_results: List[Dict],
        top_k: int,
    ) -> List[Dict]:
        """合并关键词和向量搜索结果"""
        seen = {}

        # 先添加关键词结果（优先级高）
        for r in keyword_results:
            rid = r["id"]
            if rid not in seen:
                seen[rid] = r

        # 再添加向量结果
        for r in vector_results:
            rid = r["id"]
            if rid not in seen:
                seen[rid] = r

        # 按分数排序
        all_results = list(seen.values())
        all_results.sort(key=lambda x: x["score"], reverse=True)

        return all_results[:top_k]

    def _tokenize_query(self, query: str) -> List[str]:
        """智能分词"""
        keywords = []

        # 按分隔符拆分
        parts = re.split(r'[\s、，,]+', query)

        # 对每个部分提取中英文关键词
        for part in parts:
            # 提取连续的中文字符、英文字符、数字
            sub_keywords = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z0-9]+', part)
            keywords.extend(sub_keywords)

        return keywords

    def _get_display_title(self, record, config: Dict) -> str:
        """获取显示标题"""
        title_field = config["display_fields"].get("title")
        fallback_field = config["display_fields"].get("title_fallback")

        title = getattr(record, title_field, None) or ""
        if not title and fallback_field:
            title = getattr(record, fallback_field, "") or ""

        return str(title) if title else "未知标题"

    def format_for_llm(self, result: Dict) -> str:
        """格式化结果为 LLM 可理解的文本"""
        if result["total"] == 0:
            return f"\n\n【未找到与 \"{result['query']}\" 相关的结果】"

        source_name = result.get("source", "")
        config = get_config(source_name)
        source_label = "数据" if not config else config.get("keywords", ["数据"])[0]

        lines = [
            f"\n\n【找到 {result['total']} 个与 \"{result['query']}\" 相关的{source_label}】\n"
        ]

        for i, item in enumerate(result["results"], 1):
            # 基础信息
            lines.append(f"{i}. {item['title']}")

            # 添加元数据中的详细信息
            metadata = item.get("metadata", {})
            if metadata:
                # 价格
                if "price" in metadata:
                    lines.append(f"   价格: ${metadata['price']}")
                # 评分
                if "rating" in metadata:
                    lines.append(f"   评分: {metadata['rating']}/5")
                # 销量
                if "sales" in metadata:
                    lines.append(f"   销量: {metadata['sales']}/月")
                # 市场
                if "market" in metadata:
                    lines.append(f"   市场: {metadata['market']}")
                # 标签
                if "tags" in metadata:
                    lines.append(f"   标签: {metadata['tags']}")
                # URL
                if item.get('url'):
                    lines.append(f"   链接: {item['url']}")

        return "\n".join(lines)

    def rebuild_all_indexes(self):
        """重建所有数据源的索引（用于数据更新后）"""
        for source_name in DATA_SOURCE_CONFIGS.keys():
            # 清空现有集合
            if source_name in self.vector_stores:
                collection = self.vector_stores[source_name]
                # 删除并重建
                self._chroma_client.delete_collection(
                    name=DATA_SOURCE_CONFIGS[source_name]["collection_name"]
                )
                # 重新创建
                collection_name = DATA_SOURCE_CONFIGS[source_name]["collection_name"]
                collection = self._chroma_client.get_or_create_collection(name=collection_name)
                self.vector_stores[source_name] = collection

            # 重建索引
            self._build_index(source_name)


# ==================== 全局单例 ====================
_product_rag_instance = None


def get_product_rag() -> ProductRAG:
    """获取商品检索系统单例"""
    global _product_rag_instance
    if _product_rag_instance is None:
        _product_rag_instance = ProductRAG()
    return _product_rag_instance
