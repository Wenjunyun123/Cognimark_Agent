"""
文本向量化模块

使用sentence-transformers生成文本嵌入
"""
from typing import List, Union
import numpy as np


class EmbeddingGenerator:
    """
    文本嵌入生成器

    使用sentence-transformers模型生成文本向量
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        初始化嵌入生成器

        Args:
            model_name: 模型名称
                - "all-MiniLM-L6-v2": 快速，质量好（默认）
                - "all-mpnet-base-v2": 质量更高，速度较慢
                - "paraphrase-multilingual-MiniLM-L12-v2": 支持多语言
        """
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        """延迟加载模型"""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                print(f"Loading embedding model: {self.model_name}")
                self._model = SentenceTransformer(self.model_name)
                print(f"Model loaded successfully")
            except ImportError:
                raise ImportError(
                    "sentence-transformers is not installed. "
                    "Run: pip install sentence-transformers"
                )

    def generate(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        生成文本嵌入

        Args:
            texts: 单个文本或文本列表

        Returns:
            np.ndarray: 文本嵌入向量
                - 单个文本: shape=(embedding_dim,)
                - 文本列表: shape=(n_texts, embedding_dim)
        """
        self._load_model()

        # 确保是列表格式
        single_input = isinstance(texts, str)
        if single_input:
            texts = [texts]

        # 生成嵌入
        embeddings = self._model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        # 如果是单个输入，返回一维数组
        if single_input:
            return embeddings[0]

        return embeddings

    def generate_batch(
        self,
        texts: List[str],
        batch_size: int = 32
    ) -> np.ndarray:
        """
        批量生成嵌入（优化大数据集）

        Args:
            texts: 文本列表
            batch_size: 批大小

        Returns:
            np.ndarray: 嵌入向量，shape=(n_texts, embedding_dim)
        """
        self._load_model()

        return self._model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=True,
        )

    def get_embedding_dim(self) -> int:
        """获取嵌入向量维度"""
        self._load_model()
        return self._model.get_sentence_embedding_dimension()

    def compute_similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> float:
        """
        计算两个嵌入向量的余弦相似度

        Args:
            embedding1: 向量1
            embedding2: 向量2

        Returns:
            float: 相似度分数（0-1之间）
        """
        # 确保是numpy数组
        if not isinstance(embedding1, np.ndarray):
            embedding1 = np.array(embedding1)
        if not isinstance(embedding2, np.ndarray):
            embedding2 = np.array(embedding2)

        # 计算余弦相似度
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def compute_top_k_similarities(
        self,
        query_embedding: np.ndarray,
        corpus_embeddings: np.ndarray,
        k: int = 5
    ) -> List[tuple]:
        """
        计算查询向量与语料库的前K个最相似项

        Args:
            query_embedding: 查询向量
            corpus_embeddings: 语料库向量矩阵
            k: 返回前K个结果

        Returns:
            List[(index, score)]: 索引和相似度分数的列表
        """
        # 确保是numpy数组
        if not isinstance(query_embedding, np.ndarray):
            query_embedding = np.array(query_embedding)
        if not isinstance(corpus_embeddings, np.ndarray):
            corpus_embeddings = np.array(corpus_embeddings)

        # 计算相似度
        similarities = np.dot(corpus_embeddings, query_embedding)
        norms = np.linalg.norm(corpus_embeddings, axis=1) * np.linalg.norm(query_embedding)
        similarities = similarities / (norms + 1e-8)  # 避免除零

        # 获取top-k
        top_k_indices = np.argsort(similarities)[::-1][:k]
        top_k_scores = similarities[top_k_indices]

        return list(zip(top_k_indices, top_k_scores))


# 全局单例（可选）
_default_generator = None


def get_default_generator() -> EmbeddingGenerator:
    """获取默认的嵌入生成器（单例）"""
    global _default_generator
    if _default_generator is None:
        _default_generator = EmbeddingGenerator()
    return _default_generator
