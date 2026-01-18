"""
原始产品选择Agent（向后兼容）

从agents.py迁移过来，保持原有实现
"""
import math
from typing import List, Optional, Tuple
from data_model import Product, ProductStore
from llm_service import DeepSeekLLM


class ProductSelectionAgent:
    """
    功能 1: 选品智能体 (Product Selection Agent)
    - 感知: Campaign 描述 + 目标市场
    - 知识: 产品库
    - 决策: 启发式打分 + LLM 解释
    """

    def __init__(self, store: ProductStore, llm: DeepSeekLLM):
        self.store = store
        self.llm = llm

    def _heuristic_score(self, p: Product, target_market: Optional[str]) -> float:
        """
        简单打分逻辑：
        score = rating^2 * log(1+sales) / log(2+price)
        如果主市场匹配，给予加成。
        """
        score = (p.avg_rating ** 2) * math.log(1 + p.monthly_sales)
        score = score / math.log(2 + p.price_usd)
        if target_market and target_market.lower() in p.main_market.lower():
            score *= 1.15
        return score

    def recommend_products(
        self,
        campaign_description: str,
        target_market: Optional[str],
        top_k: int = 3,
    ) -> Tuple[List[Product], str]:
        products = self.store.list_products()
        # 1. 计算分数
        scored = [(p, self._heuristic_score(p, target_market)) for p in products]
        # 2. 排序
        scored.sort(key=lambda x: x[1], reverse=True)
        top_products = [p for p, s in scored[:top_k]]

        # 3. 准备 Prompt 给 LLM 解释
        lines = []
        for p, s in scored[:top_k]:
            lines.append(
                f"- **{p.product_id}**: {p.title_en}  "
                f"(cat={p.category}, price=${p.price_usd}, "
                f"rating={p.avg_rating}, sales={p.monthly_sales}, "
                f"market={p.main_market}, score={s:.2f})"
            )
        table_md = "\n".join(lines)

        system_prompt = (
            "You are a product selection expert for cross-border e-commerce."
        )
        user_prompt = f"""
We are planning a new marketing campaign.

Campaign description:
\"\"\"{campaign_description}\"\"\"

Target market (if specified): {target_market or "N/A"}.

Here are candidate products with heuristic scores (top-{top_k}):
{table_md}

1. Briefly explain which products are most suitable and why.
2. Consider price level, rating, sales and market fit.
3. Answer in a concise analytical paragraph in English.
"""
        # 4. 调用 LLM
        explanation = self.llm.chat(system_prompt, user_prompt)
        return top_products, explanation
