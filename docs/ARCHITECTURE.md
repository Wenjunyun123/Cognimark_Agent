# 项目架构说明

## 整体架构

```
┌─────────────────┐      HTTP/REST     ┌─────────────────┐
│                 │ ←─────────────────→ │                 │
│  React Frontend │                     │  FastAPI Backend│
│  (TypeScript)   │                     │    (Python)     │
│                 │                     │                 │
└─────────────────┘                     └─────────────────┘
        │                                       │
        │                                       │
        ├─ Pages                                ├─ API Router
        │  ├─ ProductIntelligence               │  ├─ /products
        │  └─ MarketingCopilot                  │  ├─ /selection/recommend
        │                                       │  └─ /marketing/generate
        ├─ Components                           │
        │  ├─ Layout                           ├─ Agents
        │  ├─ Products                         │  ├─ ProductSelectionAgent
        │  └─ Marketing                        │  └─ MarketingCopyAgent
        │                                       │
        └─ Services                            ├─ LLM Service
           └─ API Client                       │  └─ DeepSeekLLM
                                               │
                                               └─ Data Model
                                                  └─ ProductStore
```

## 后端模块

### 1. api.py (API 路由层)
- FastAPI 应用入口
- 定义 RESTful 接口
- 请求/响应数据验证
- CORS 配置

### 2. agents.py (业务逻辑层)
- `ProductSelectionAgent`: 选品推荐逻辑
  - 启发式评分算法
  - 市场匹配度计算
  - LLM 解释生成
  
- `MarketingCopyAgent`: 文案生成逻辑
  - 多语言支持
  - 多渠道适配
  - Prompt 工程

### 3. llm_service.py (LLM 服务层)
- 统一 LLM 调用接口
- DeepSeek API 封装
- 错误处理
- 参数配置

### 4. data_model.py (数据层)
- Product 数据模型
- ProductStore 知识库
- 数据访问接口

### 5. config.py (配置层)
- API Key 管理
- 环境配置
- 常量定义

## 前端模块

### Pages (页面层)
- `ProductIntelligence.tsx`: 智能选品页面
- `MarketingCopilot.tsx`: 营销文案页面

### Components (组件层)
- `Layout/`: 布局组件
  - Header, Sidebar, Layout
- `Products/`: 产品相关组件
  - ProductTable, AIInsightCard
- `Marketing/`: 营销相关组件
  - ChatInterface, MarketingConfig

### Services (服务层)
- `api.ts`: API 调用封装
- HTTP 请求管理
- 类型定义

### Types (类型定义)
- TypeScript 接口定义
- 数据模型类型

## 数据流

### 选品推荐流程
```
用户输入活动描述
    ↓
前端调用 POST /selection/recommend
    ↓
ProductSelectionAgent 接收请求
    ↓
计算产品评分 (启发式算法)
    ↓
排序并选取 Top K
    ↓
LLM 生成推荐理由
    ↓
返回结果给前端
    ↓
前端展示产品卡片 + AI 分析
```

### 文案生成流程
```
用户选择产品、语言、渠道
    ↓
前端调用 POST /marketing/generate
    ↓
MarketingCopyAgent 接收请求
    ↓
构建 Prompt (产品信息 + 要求)
    ↓
调用 LLM Service
    ↓
LLM 生成文案
    ↓
返回结果给前端
    ↓
前端流式展示文案内容
```

## 扩展点

1. **数据源扩展**
   - 替换 `data_model.py` 中的硬编码数据
   - 支持数据库、CSV、API 等多种数据源

2. **评分算法扩展**
   - 修改 `agents.py` 中的 `_heuristic_score`
   - 增加更多维度的评分因子

3. **LLM 服务扩展**
   - 在 `llm_service.py` 中添加其他 LLM 支持
   - 实现统一的 LLM 接口

4. **前端功能扩展**
   - 添加新页面到 `src/pages/`
   - 开发新组件到 `src/components/`














