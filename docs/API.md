# API 接口文档

## 基础信息

- **Base URL**: `http://127.0.0.1:8000`
- **格式**: JSON
- **文档**: http://127.0.0.1:8000/docs (Swagger UI)

## 接口列表

### 1. 获取产品列表

**请求**
```
GET /products
```

**响应**
```json
[
  {
    "product_id": "P001",
    "title_en": "Stainless Steel Insulated Water Bottle 500ml"
  },
  ...
]
```

### 2. 智能选品推荐

**请求**
```
POST /selection/recommend
Content-Type: application/json

{
  "campaign_description": "Summer promotion for young professionals",
  "target_market": "US",
  "top_k": 3
}
```

**响应**
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
  ],
  "explanation": "AI 分析推荐理由..."
}
```

### 3. 生成营销文案

**请求**
```
POST /marketing/generate
Content-Type: application/json

{
  "product_id": "P001",
  "target_language": "Chinese",
  "channel": "Facebook Ads"
}
```

**响应**
```json
{
  "copy_text": "生成的营销文案内容..."
}
```

## 错误码

- `400` - 请求参数错误
- `404` - 资源不存在
- `500` - 服务器内部错误














