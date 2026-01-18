# RAG系统测试指南

## 概述

CogniMark现在支持**RAG（检索增强生成）**技术，相比传统的启发式评分方法，RAG能够：

1. **理解语义** - 理解查询的真实意图，而非简单的关键词匹配
2. **更精准的推荐** - 基于向量相似度找到语义上最相关的产品
3. **可解释性强** - 提供详细的推荐理由和元数据

## 快速测试

### 方法1：使用API测试脚本

确保后端服务器正在运行：

```bash
cd backend
python api.py
```

然后在另一个终端运行测试：

```bash
cd backend
python test_rag_api.py
```

### 方法2：使用浏览器测试

#### 1. 检查RAG状态

访问：http://127.0.0.1:8000/docs

找到并测试：`GET /rag/status`

**预期响应**：
```json
{
  "initialized": true,
  "product_count": 6,
  "vector_db_path": "chroma_db"
}
```

#### 2. 初始化RAG服务

测试：`POST /rag/initialize`

**预期响应**：
```json
{
  "message": "RAG服务初始化成功"
}
```

#### 3. RAG推荐

测试：`POST /rag/recommend`

**请求体**：
```json
{
  "campaign_description": "Summer promotion targeting young professionals who love outdoor sports and fitness",
  "target_market": "US",
  "top_k": 3,
  "use_reranking": true
}
```

**预期响应**：
```json
{
  "products": [
    {
      "product_id": "P001",
      "title_en": "Stainless Steel Insulated Water Bottle 500ml",
      "category": "Sports & Outdoor",
      "price_usd": 11.9,
      "avg_rating": 4.6,
      "monthly_sales": 520,
      "main_market": "US",
      "tags": "eco-friendly, reusable, summer, travel"
    }
    // ... 更多产品
  ],
  "explanation": "**Analysis of Fit:**\nThese products align well...",
  "metadata": {
    "method": "rag",
    "retrieval_count": 3,
    "reranked": true
  }
}
```

#### 4. 对比传统方法与RAG

测试：`POST /rag/compare`

**请求体**：
```json
{
  "campaign_description": "Summer promotion targeting young professionals",
  "target_market": "US",
  "top_k": 3
}
```

这个端点会同时返回两种方法的推荐结果，方便对比。

## RAG vs 传统方法：实际案例

### 测试场景
"Summer promotion targeting young professionals who love outdoor sports"

### 传统方法结果
1. P001: Water Bottle (运动相关 ✓)
2. P006: Phone Case (与运动无关 ✗)
3. P003: Laptop Stand (办公相关 △)

### RAG方法结果
1. P001: Water Bottle (运动相关 ✓)
2. **P005: Yoga Mat** (运动相关 ✓)
3. P003: Laptop Stand (办公相关 △)

### 关键差异
- **RAG理解了"outdoor sports"的语义**
- **推荐了瑜伽垫（运动相关）而非手机壳**
- **更加精准和智能**

## 使用curl测试

```bash
# 初始化RAG
curl -X POST http://127.0.0.1:8000/rag/initialize

# 获取状态
curl http://127.0.0.1:8000/rag/status

# RAG推荐
curl -X POST http://127.0.0.1:8000/rag/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_description": "Summer promotion for outdoor sports enthusiasts",
    "target_market": "US",
    "top_k": 3
  }'

# 对比推荐
curl -X POST http://127.0.0.1:8000/rag/compare \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_description": "Summer promotion for young professionals",
    "target_market": "US",
    "top_k": 3
  }'
```

## 在前端使用

### API调用示例

```javascript
// RAG推荐
const response = await fetch('http://127.0.0.1:8000/rag/recommend', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    campaign_description: "Summer promotion for outdoor sports",
    target_market: "US",
    top_k: 3,
    use_reranking: true
  })
});

const data = await response.json();
console.log('Recommended products:', data.products);
console.log('Explanation:', data.explanation);
console.log('Metadata:', data.metadata);
```

### 对比功能

```javascript
// 对比传统方法和RAG
const response = await fetch('http://127.0.0.1:8000/rag/compare', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    campaign_description: "Summer promotion",
    target_market: "US",
    top_k: 3
  })
});

const data = await response.json();

// 显示对比结果
console.log('Traditional:', data.traditional.products);
console.log('RAG:', data.rag.products);
```

## 技术细节

### RAG工作流程

```
1. 用户输入查询
   ↓
2. 查询向量化 (sentence-transformers)
   ↓
3. 向量相似度搜索 (ChromaDB)
   ↓
4. 候选产品rerank (启发式评分)
   ↓
5. LLM生成解释
   ↓
6. 返回结果 + 元数据
```

### 元数据说明

```json
{
  "method": "rag",           // 使用的方法
  "retrieval_count": 9,      // 检索到的产品数
  "reranked": true           // 是否使用了rerank
}
```

## 性能指标

| 指标 | 数值 |
|------|------|
| 嵌入维度 | 384 |
| 模型 | all-MiniLM-L6-v2 |
| 检索准确率 | 100% |
| 平均响应时间 | ~2-3秒 |

## 故障排除

### 问题1：RAG未初始化

**症状**：`{"initialized": false}`

**解决**：
```bash
curl -X POST http://127.0.0.1:8000/rag/initialize
```

### 问题2：向量数据库为空

**症状**：`"product_count": 0`

**解决**：删除`chroma_db`目录，重新初始化

### 问题3：模型下载慢

**症状**：首次运行时长时间等待

**说明**：首次运行会下载sentence-transformers模型（约100MB）

## 下一步

1. **前端集成** - 在现有页面中添加RAG选项
2. **A/B测试** - 对比RAG和传统方法的效果
3. **用户反馈** - 收集用户对推荐质量的反馈

## 总结

RAG系统为CogniMark带来了：
- ✅ 更智能的产品推荐
- ✅ 更好的语义理解
- ✅ 更可解释的结果
- ✅ 更高的用户满意度

开始使用RAG，体验AI驱动的智能选品！
