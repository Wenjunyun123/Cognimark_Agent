# 通用 RAG 系统使用指南

## 📖 系统概述

通用 RAG 系统是一个**最小化、可配置**的检索增强生成系统。通过修改一个配置文件，即可适配任意数据表的检索需求。

### 核心特性

- ✅ **一个配置文件控制一切** - 所有配置都在 `rag_config.py`
- ✅ **混合检索** - 关键词精确匹配 + 向量语义搜索
- ✅ **自动数据源检测** - 根据用户问题自动选择合适的数据源
- ✅ **支持多数据源** - 可同时配置多个数据表

---

## 🚀 快速开始

### 1. 文件结构

```
backend/
├── rag/
│   ├── rag_config.py         # ⭐ 配置文件（主要修改这个）
│   ├── universal_rag.py       # 通用RAG引擎
│   ├── embeddings.py          # 向量嵌入生成
│   └── __init__.py
├── api.py                     # 已集成通用RAG
└── ...
```

### 2. 基本使用

```python
# 在代码中使用
from rag.universal_rag import get_universal_rag

# 获取单例
rag = get_universal_rag()

# 执行检索
result = rag.search("查找Java课程", top_k=10)

# 格式化给LLM
context = rag.format_for_llm(result)
```

---

## ⚙️ 配置说明

### 配置文件位置

[backend/rag/rag_config.py](rag/rag_config.py)

### 数据源配置模板

```python
DATA_SOURCE_CONFIGS = {
    "数据源名称": {
        # 触发关键词：用户问题包含这些词时会检索此数据源
        "keywords": ["关键词1", "关键词2"],

        # 关键词匹配字段（精确搜索用）
        "search_fields": ["title_zh", "category"],

        # 向量索引字段（语义搜索用）- 会合并这些字段生成向量
        "index_fields": ["title_zh", "title_en", "description"],

        # 显示字段（返回给用户看的）
        "display_fields": {
            "id": "product_id",           # 唯一标识
            "title": "title_zh",          # 标题
            "title_fallback": "title_en", # 标题备用字段
            "description": "description",  # 描述
            "url": "resource_url",        # 链接
        },

        # 数据库表模型
        "db_model": "ProductDB",

        # 向量集合名称
        "collection_name": "my_data_vector",

        # 默认返回数量
        "default_limit": 10,
    },
}
```

---

## 📋 添加新数据源的步骤

### 步骤 1: 修改配置文件

编辑 [backend/rag/rag_config.py](rag/rag_config.py)，添加你的数据源配置：

```python
DATA_SOURCE_CONFIGS = {
    # ... 其他配置 ...

    # ==================== 你的数据源 ====================
    "my_data": {
        "keywords": ["数据", "记录", "信息"],  # 用户说这些词时触发检索

        "search_fields": ["name", "title"],  # 用于关键词匹配的字段

        "index_fields": ["name", "description", "category"],  # 用于向量索引的字段

        "display_fields": {
            "id": "id",
            "title": "name",
            "description": "description",
            "url": "link",
        },

        "db_model": "ProductDB",  # 或你的自定义模型名
        "collection_name": "my_data_vector",
        "default_limit": 10,
    },
}
```

### 步骤 2: 重建索引

当数据更新后，需要重建向量索引：

```bash
# 方法1: 调用API
curl -X POST http://localhost:8000/rag/universal/rebuild

# 方法2: 只重建指定数据源
curl -X POST http://localhost:8000/rag/universal/rebuild \
  -H "Content-Type: application/json" \
  -d '{"source": "my_data"}'
```

### 步骤 3: 测试检索

```bash
# 测试检索效果
curl -X POST "http://localhost:8000/rag/universal/search?query=查找数据&top_k=5"
```

---

## 🔧 常用配置场景

### 场景 1: 中文数据为主

```python
"my_chinese_data": {
    "keywords": ["中文", "数据"],
    "search_fields": ["title_zh", "name_zh"],  # 只用中文字段
    "index_fields": ["title_zh", "description_zh"],
    "display_fields": {
        "id": "id",
        "title": "title_zh",
        "description": "description_zh",
    },
    # ...
}
```

### 场景 2: 中英文混合

```python
"mixed_data": {
    "keywords": ["data", "数据"],
    "search_fields": ["title_zh", "title_en", "name"],
    "index_fields": ["title_zh", "title_en", "description"],
    "display_fields": {
        "id": "id",
        "title": "title_zh",
        "title_fallback": "title_en",  # 中文没有时用英文
    },
    # ...
}
```

### 场景 3: 多个数据源

```python
DATA_SOURCE_CONFIGS = {
    "products": { ... },    # 商品数据
    "courses": { ... },     # 课程数据
    "news": { ... },        # 新闻数据
    "users": { ... },       # 用户数据
}
```

系统会自动根据用户问题匹配合适的数据源。

---

## 🌐 API 接口

### 1. 查看系统状态

```bash
GET /rag/universal/status
```

返回：
```json
{
  "enabled": true,
  "sources": [
    {
      "name": "products",
      "collection_name": "products_vector",
      "indexed_count": 100,
      "keywords": ["商品", "产品"]
    }
  ]
}
```

### 2. 重建索引

```bash
POST /rag/universal/rebuild
Content-Type: application/json

{
  "source": "products"  // 可选，不填则重建所有
}
```

### 3. 测试检索

```bash
POST /rag/universal/search?query=查找Java课程&source=courses&top_k=10
```

---

## 📊 工作原理

```
用户问题: "查找Java课程"
    ↓
1. 关键词检测 → 匹配到 "courses" 数据源
    ↓
2. 并行检索:
   ├─ 关键词精确匹配 (title_zh contains "Java")
   └─ 向量语义搜索 (embedding similarity)
    ↓
3. 结果合并去重 (关键词结果 * 2.0 倍权重)
    ↓
4. 返回 Top-K 结果
```

---

## ⚙️ 全局配置

在 `rag_config.py` 中的全局配置：

```python
# 是否启用关键词匹配
ENABLE_KEYWORD_SEARCH = True

# 是否启用向量搜索
ENABLE_VECTOR_SEARCH = True

# 关键词权重倍数
KEYWORD_BOOST_SCORE = 2.0

# 向量存储目录
VECTOR_DB_DIR = "./chroma_db_universal"

# 嵌入模型
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"  # 支持中英文
```

---

## 🐛 常见问题

### Q1: 检索不到结果？

**检查清单：**
1. 数据库中是否有数据？
2. 配置的字段名是否正确？
3. 关键词是否匹配？
4. 是否重建了索引？

```bash
# 检查索引状态
curl http://localhost:8000/rag/universal/status

# 重建索引
curl -X POST http://localhost:8000/rag/universal/rebuild
```

### Q2: 如何添加新的数据库表？

1. 在 `models.py` 定义表模型
2. 在 `rag_config.py` 添加数据源配置，指定 `db_model`
3. 在 `universal_rag.py` 的 `_build_index` 方法中添加表查询逻辑

### Q3: 向量索引需要多久？

- 100条数据: ~10秒
- 1000条数据: ~30秒
- 10000条数据: ~2分钟

### Q4: 支持哪些嵌入模型？

- `all-MiniLM-L6-v2` - 英文，速度快
- `paraphrase-multilingual-MiniLM-L12-v2` - 多语言（推荐）
- 其他 sentence-transformers 模型

---

## 📝 示例：配置飞书表格数据

假设你的飞书表格有以下字段：`标题`, `描述`, `链接`, `分类`

```python
"feishu_data": {
    "keywords": ["飞书", "表格", "数据"],
    "search_fields": ["title", "category"],
    "index_fields": ["title", "description", "category"],
    "display_fields": {
        "id": "id",
        "title": "title",
        "description": "description",
        "url": "link",
        "category": "category",
    },
    "db_model": "ProductDB",  # 假设数据存在 ProductDB
    "collection_name": "feishu_vector",
    "default_limit": 10,
},
```

---

## 🎯 最佳实践

1. **关键词选择**: 选择 3-5 个最能代表数据源的词
2. **索引字段**: 包含主要信息字段，不要太多（3-5个最佳）
3. **定期重建**: 数据更新后记得重建索引
4. **测试检索**: 使用 `/rag/universal/search` 测试效果
5. **权重调整**: 根据效果调整 `KEYWORD_BOOST_SCORE`

---

## 📚 相关文件

- [rag_config.py](rag/rag_config.py) - 配置文件
- [universal_rag.py](rag/universal_rag.py) - RAG引擎
- [api.py](api.py) - API接口（已集成）
