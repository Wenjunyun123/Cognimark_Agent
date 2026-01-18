"""
RAG增强的产品选择Agent

结合向量检索和启发式算法，提供更准确的推荐
"""
import math
from typing import List, Optional, Tuple, Dict
from data_model import Product, ProductStore
from llm_service import LLMService
from rag.vector_store import VectorStore


class RAGProductSelectionAgent:
    """
    RAG增强的产品选择Agent

    工作流程：
    1. 使用向量检索进行语义搜索
    2. 结合启发式评分进行rerank
    3. 使用LLM生成解释
    """

    def __init__(
        self,
        store: ProductStore,
        llm: LLMService,
        vector_store: Optional[VectorStore] = None,
        use_reranking: bool = True,
    ):
        """
        初始化RAG产品选择Agent

        Args:
            store: 产品存储
            llm: LLM服务
            vector_store: 向量存储（可选，如果为None则创建新的）
            use_reranking: 是否使用reranking（结合启发式评分）
        """
        self.store = store
        self.llm = llm
        self.vector_store = vector_store
        self.use_reranking = use_reranking

    def _heuristic_score(self, p: Product, target_market: Optional[str]) -> float:
        """
        启发式评分（用于reranking）
        """
        score = (p.avg_rating ** 2) * math.log(1 + p.monthly_sales)
        score = score / math.log(2 + p.price_usd)
        if target_market and target_market.lower() in p.main_market.lower():
            score *= 1.15
        return score

    def _rerank(
        self,
        products: List[Product],
        target_market: Optional[str],
        top_k: int,
    ) -> List[Product]:
        """
        使用启发式评分对向量检索结果进行rerank

        Args:
            products: 候选产品列表
            target_market: 目标市场
            top_k: 返回数量

        Returns:
            List[Product]: rerank后的产品列表
        """
        # 计算启发式分数
        scored = [(p, self._heuristic_score(p, target_market)) for p in products]
        # 按分数排序
        scored.sort(key=lambda x: x[1], reverse=True)
        # 返回top-k
        return [p for p, s in scored[:top_k]]

    def recommend_products(
        self,
        campaign_description: str,
        target_market: Optional[str] = None,
        top_k: int = 3,
        retrieval_k: Optional[int] = None,
    ) -> Tuple[List[Product], str, Dict]:
        """
        推荐产品（RAG增强）

        Args:
            campaign_description: 营销活动描述
            target_market: 目标市场
            top_k: 返回top-k结果
            retrieval_k: 向量检索数量（默认为top_k的3倍）

        Returns:
            Tuple[List[Product], str, Dict]:
                - 推荐产品列表
                - AI解释
                - 元数据（检索信息）
        """
        if retrieval_k is None:
            retrieval_k = top_k * 3

        metadata = {
            "method": "rag",
            "retrieval_count": 0,
            "reranked": self.use_reranking,
        }

        # 步骤1: 向量检索
        if self.vector_store:
            # 使用向量检索
            search_results = self.vector_store.search_with_filters(
                query=campaign_description,
                market=target_market,
                n_results=retrieval_k,
            )

            metadata["retrieval_count"] = len(search_results)

            # 提取产品ID并获取产品对象
            retrieved_products = []
            for result in search_results:
                product = self.store.get_product(result["id"])
                if product:
                    # 将相似度分数附加到产品对象
                    product._similarity_score = result["score"]
                    retrieved_products.append(product)

        else:
            # 降级到全量检索
            retrieved_products = self.store.list_products()
            metadata["method"] = "full_scan"

        # 步骤2: Reranking（可选）
        if self.use_reranking and len(retrieved_products) > top_k:
            final_products = self._rerank(
                retrieved_products,
                target_market,
                top_k
            )
            metadata["reranked"] = True
        else:
            final_products = retrieved_products[:top_k]
            metadata["reranked"] = False

        # 步骤3: 生成AI解释
        explanation = self._generate_explanation(
            campaign_description,
            target_market,
            final_products,
            metadata,
        )

        return final_products, explanation, metadata

    def _generate_explanation(
        self,
        campaign_description: str,
        target_market: Optional[str],
        products: List[Product],
        metadata: Dict,
    ) -> str:
        """
        生成推荐解释

        Args:
            campaign_description: 营销活动描述
            target_market: 目标市场
            products: 推荐产品列表
            metadata: 元数据

        Returns:
            str: AI生成的解释
        """
        # 构建产品信息表格
        lines = []
        for i, p in enumerate(products, 1):
            score_info = ""
            if hasattr(p, '_similarity_score'):
                score_info = f", similarity={p._similarity_score:.3f}"

            lines.append(
                f"{i}. **{p.product_id}**: {p.title_en}\n"
                f"   - Category: {p.category}\n"
                f"   - Price: ${p.price_usd}, Rating: {p.avg_rating}, Sales: {p.monthly_sales}\n"
                f"   - Market: {p.main_market}{score_info}"
            )

        products_md = "\n".join(lines)

        # 构建提示词
        system_prompt = (
            "You are a product selection expert for cross-border e-commerce. "
            "You use AI-powered semantic search combined with data-driven analysis "
            "to recommend the most suitable products for marketing campaigns."
        )

        user_prompt = f"""
We are planning a new marketing campaign.

**Campaign Description:**
{campaign_description}

**Target Market:** {target_market or "Global"}

**Retrieval Method:** {metadata.get('method', 'unknown')}
**Products Retrieved:** {metadata.get('retrieval_count', 'N/A')}
**Re-ranking Applied:** {metadata.get('reranked', False)}

**Recommended Products:**
{products_md}

Based on the campaign description and product information above, please:

1. **Analyze the fit**: Explain why these products are suitable for this campaign
2. **Highlight strengths**: Focus on 2-3 key strengths (price point, market alignment, ratings, etc.)
3. **Provide context**: Connect product features to campaign goals
4. **Be specific**: Reference actual product attributes

Keep your response concise (2-3 paragraphs) and professional.
"""

        # 调用LLM
        try:
            response = self.llm.chat([{"role": "user", "content": user_prompt}])
            return response
        except Exception as e:
            # 降级到简单解释
            return f"Error generating explanation: {str(e)}\n\n" \
                   f"Recommended {len(products)} products based on: {campaign_description}"


def create_rag_agent(
    store: ProductStore,
    llm: LLMService,
    vector_store: Optional[VectorStore] = None,
) -> RAGProductSelectionAgent:
    """
    创建RAG产品选择Agent的便捷函数

    Args:
        store: 产品存储
        llm: LLM服务
        vector_store: 向量存储（可选）

    Returns:
        RAGProductSelectionAgent: RAG增强的Agent
    """
    return RAGProductSelectionAgent(
        store=store,
        llm=llm,
        vector_store=vector_store,
    )
