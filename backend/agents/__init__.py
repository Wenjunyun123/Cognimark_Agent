"""
Agent模块 - 智能体实现

包含原有Agent和新的RAG增强Agent
"""
from data_model import ProductStore
from llm_service import DeepSeekLLM

# 导入原有Agent（向后兼容）
from agents.product_selection import ProductSelectionAgent
from agents.marketing_copy import MarketingCopyAgent

# 导入新的RAG增强Agent
from agents.rag_product_selection import RAGProductSelectionAgent

__all__ = [
    "ProductSelectionAgent",
    "MarketingCopyAgent",
    "RAGProductSelectionAgent",
]
