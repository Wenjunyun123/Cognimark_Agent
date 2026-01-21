# AI Agent E-Commerce Demo

基于 AI Agent 的跨境电商智能选品与营销文案生成系统

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-ISC-green.svg)](LICENSE)

## 📋 项目简介.

这是一个展示 AI Agent 在跨境电商领域应用的完整系统，包含智能选品推荐和营销文案生成两大核心功能。

### 核心功能

- **智能选品推荐** 🎯
  - 根据营销活动描述和目标市场
  - AI 自动推荐最合适的产品
  - 提供详细的推荐理由分析

- **营销文案生成** ✍️
  - 支持多语言文案生成
  - 适配多种营销渠道
  - Chat 风格的交互体验

## 🏗️ 项目结构

```
ai_agent_demo/
├── backend/                 # 后端服务
│   ├── api.py              # FastAPI 主服务
│   ├── agents.py           # AI Agent 逻辑
│   ├── data_model.py       # 数据模型
│   ├── llm_service.py      # LLM 服务封装
│   └── config.py           # 配置文件
│
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── pages/         # 页面组件
│   │   ├── components/    # UI 组件
│   │   ├── services/      # API 服务
│   │   └── types/         # TypeScript 类型
│   └── package.json
│
├── scripts/               # 脚本文件
│   ├── start.bat         # 启动脚本
│   └── stop.bat          # 停止脚本
│
├── docs/                 # 文档
├── venv/                 # Python 虚拟环境
├── requirements.txt      # Python 依赖
└── README.md            # 项目说明
```

## 🚀 快速开始

### 前置要求

- Python 3.13+
- Node.js 18+
- npm 9+

### 1. 克隆项目

```bash
git clone <repository-url>
cd ai_agent_demo
```

### 2. 安装依赖

**后端依赖:**
```bash
.\venv\Scripts\pip install -r requirements.txt
```

**前端依赖:**
```bash
cd frontend
npm install
cd ..
```

### 3. 配置 API Key

编辑 `backend/config.py`，设置您的 DeepSeek API Key:

```python
DEEPSEEK_API_KEY = "your-api-key-here"
```

### 4. 启动服务

**方式一: 使用启动脚本 (推荐)**

双击运行 `scripts/start.bat`

**方式二: 手动启动**

启动后端:
```bash
.\venv\Scripts\python backend\api.py
```

启动前端 (新窗口):
```bash
cd frontend
npm run dev
```

### 5. 访问应用

- 🌐 **前端界面**: http://localhost:5173
- 📚 **API 文档**: http://127.0.0.1:8000/docs

## 💻 技术栈

### 后端
- **FastAPI** - 现代化的 Python Web 框架
- **DeepSeek API** - 大语言模型服务
- **Pandas** - 数据处理
- **Pydantic** - 数据验证

### 前端
- **React 18** - UI 框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **TailwindCSS** - 样式框架
- **Lucide Icons** - 图标库

## 📖 使用指南

### 智能选品

1. 访问"智能选品"页面
2. 输入营销活动描述（如：夏季促销、目标年轻专业人士）
3. 选择目标市场（US/EU/SEA/Global）
4. 设置推荐数量
5. 点击"AI 智能选品"按钮
6. 查看推荐结果和 AI 分析

### 营销文案生成

1. 访问"营销文案"页面
2. 选择产品
3. 选择目标语言
4. 选择投放渠道
5. 点击"生成营销文案"
6. 查看生成的文案内容
7. 可以继续对话进行优化

## 🔧 配置说明

### 后端配置

文件: `backend/config.py`

```python
DEEPSEEK_API_KEY = "your-api-key"  # DeepSeek API 密钥
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL = "deepseek-chat"
```

### 前端配置

文件: `frontend/.env.local`

```env
VITE_API_URL=http://127.0.0.1:8000
```

## 📊 数据说明

当前版本使用预设的 Demo 数据（6个产品），存储在 `backend/data_model.py` 中。

如需使用真实数据，可以：
- 从 CSV 文件导入
- 连接数据库
- 对接电商平台 API

## 🛠️ 开发指南

### 添加新产品

编辑 `backend/data_model.py`:

```python
_products_data = [
    {
        "product_id": "P007",
        "title_en": "New Product Name",
        "category": "Category",
        "price_usd": 29.9,
        "avg_rating": 4.5,
        "monthly_sales": 300,
        "main_market": "US",
        "tags": "tag1, tag2",
    },
    # ... 更多产品
]
```

### 自定义 Agent 逻辑

编辑 `backend/agents.py` 中的评分算法:

```python
def _heuristic_score(self, p: Product, target_market: Optional[str]) -> float:
    # 自定义您的评分逻辑
    score = custom_scoring_function(p)
    return score
```

## 📝 API 文档

启动服务后访问: http://127.0.0.1:8000/docs

主要接口:
- `GET /products` - 获取产品列表
- `POST /selection/recommend` - 智能选品推荐
- `POST /marketing/generate` - 生成营销文案

## 🐛 常见问题

### Q: 前端无法连接后端？
A: 确保后端服务已启动，并检查 `frontend/.env.local` 中的 API 地址配置。

### Q: API 调用失败？
A: 检查 `backend/config.py` 中的 API Key 是否正确配置。

### Q: 端口被占用？
A: 运行 `scripts/stop.bat` 停止所有服务，或手动修改端口配置。

## 📄 许可证

ISC License

## 👥 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题，请通过 Issue 联系。

---

**注意**: 这是一个演示项目，请勿在生产环境中直接使用。
