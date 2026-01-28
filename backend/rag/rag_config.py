# -*- coding: utf-8 -*-
"""
通用 RAG 配置文件

用于配置产品检索系统的数据源和字段映射
修改此文件即可适配不同的数据表和检索需求
"""

# ==================== 配置说明 ====================
# keywords: 触发检索的关键词列表
# search_fields: 用于关键词精确匹配的字段
# index_fields: 用于向量语义搜索的字段
# numeric_fields: 数值字段（会转换为文本加入向量索引）
# display_fields: 返回给用户看的显示字段
# collection_name: 向量数据库中的集合名称

# ==================== 数据源配置 ====================

DATA_SOURCE_CONFIGS = {
    # 商品/产品数据
    "products": {
        # 触发关键词
        "keywords": [
            "商品", "产品", "product", "有哪些", "推荐",
            "搜索", "查找", "选品", "库存", "价格", "便宜", "贵",
            "便宜", "优惠", "性价比"
        ],

        # 关键词匹配字段
        "search_fields": ["title_en", "category", "tags"],

        # 向量索引字段
        "index_fields": ["title_en", "category", "tags"],

        # 数值字段（转为文本索引）
        "numeric_fields": {
            "price_usd": "price{value}USD",
            "avg_rating": "rating{value}",
            "monthly_sales": "sales{value}",
        },

        # 显示字段
        "display_fields": {
            "id": "product_id",
            "title": "title_en",
            "category": "category",
            "price": "price_usd",
            "rating": "avg_rating",
            "sales": "monthly_sales",
            "market": "main_market",
            "tags": "tags",
        },

        # 数据库表
        "db_model": "ProductDB",

        # 向量集合名
        "collection_name": "products_vector",

        # 默认返回数量
        "default_limit": 10,
    },
}

# ==================== 全局配置 ====================

# 是否启用关键词匹配（精确搜索）
ENABLE_KEYWORD_SEARCH = True

# 是否启用向量语义搜索
ENABLE_VECTOR_SEARCH = True

# 混合检索时关键词的权重倍数（关键词匹配结果 * 这个倍数）
KEYWORD_BOOST_SCORE = 2.0

# 向量存储目录
VECTOR_DB_DIR = "./chroma_db_universal"

# 嵌入模型（可选: "all-MiniLM-L6-v2", "paraphrase-multilingual-MiniLM-L12-v2"支持中文）
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"  # 支持中英文

# ==================== 辅助函数 ====================

def get_all_keywords():
    """获取所有数据源的关键词（用于快速检测）"""
    all_keywords = set()
    for config in DATA_SOURCE_CONFIGS.values():
        all_keywords.update(config.get("keywords", []))
    return list(all_keywords)

def detect_data_source(user_query: str):
    """
    根据用户查询检测应该使用哪个数据源

    Returns:
        list: 匹配的数据源名称列表（可能多个）
    """
    detected = []
    query_lower = user_query.lower()

    for source_name, config in DATA_SOURCE_CONFIGS.items():
        keywords = config.get("keywords", [])
        if any(kw in query_lower for kw in keywords):
            detected.append(source_name)

    # 如果没有匹配，返回所有数据源（兜底）
    return detected if detected else list(DATA_SOURCE_CONFIGS.keys())

def get_config(source_name: str):
    """获取指定数据源的配置"""
    return DATA_SOURCE_CONFIGS.get(source_name)
