"""
营销文案Agent（向后兼容）

从agents.py迁移过来，保持原有实现
"""
from typing import List
from data_model import Product
from llm_service import DeepSeekLLM


class MarketingCopyAgent:
    """
    功能 2: 营销文案智能体 (Marketing Copy Agent)
    - 输入: 产品 + 目标语言 + 渠道
    - 输出: 标题 + 卖点 + 广告文案
    """

    def __init__(self, llm: DeepSeekLLM):
        self.llm = llm

    def generate_copy(
        self,
        product: Product,
        target_language: str = "English",
        channel: str = "Facebook Ads",
    ) -> str:
        system_prompt = (
            "You are a professional marketing copywriter for cross-border e-commerce."
        )

        user_prompt = f"""
Target language: {target_language}
Channel: {channel}

Product information (EN):
ID: {product.product_id}
Title: {product.title_en}
Category: {product.category}
Price (USD): ${product.price_usd}
Average rating: {product.avg_rating}
Monthly sales: {product.monthly_sales}
Main market: {product.main_market}
Tags: {product.tags}

Please generate marketing copy in the target language with the following structure:

1. A short, catchy headline (<= 80 characters).
2. 3 bullet points focusing on key selling points and benefits.
3. A persuasive ad paragraph of about 80-120 words, adapted to the specified channel
   (e.g., social media ad, product listing, email campaign).

Do NOT mix multiple languages. Use only the target language.
Return the result in markdown format.
"""
        return self.llm.chat(system_prompt, user_prompt)
