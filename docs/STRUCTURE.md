# 项目文件结构

```
ai_agent_demo/
│
├── 📁 backend/                    # 后端服务 (Python)
│   ├── api.py                    # FastAPI 主服务器
│   ├── agents.py                 # AI Agent 业务逻辑
│   ├── data_model.py             # 数据模型和产品库
│   ├── llm_service.py            # LLM 服务封装
│   ├── config.py                 # 配置文件
│   └── README.md                 # 后端说明文档
│
├── 📁 frontend/                   # 前端应用 (React + TypeScript)
│   ├── 📁 src/
│   │   ├── 📁 pages/             # 页面组件
│   │   │   ├── ProductIntelligence.tsx    # 智能选品页面
│   │   │   ├── MarketingCopilot.tsx       # 营销文案页面
│   │   │   └── Dashboard.tsx              # 仪表盘页面
│   │   │
│   │   ├── 📁 components/        # UI 组件
│   │   │   ├── 📁 layout/        # 布局组件
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── Layout.tsx
│   │   │   ├── 📁 products/      # 产品相关组件
│   │   │   │   ├── ProductTable.tsx
│   │   │   │   └── AIInsightCard.tsx
│   │   │   ├── 📁 marketing/     # 营销相关组件
│   │   │   │   ├── ChatInterface.tsx
│   │   │   │   └── MarketingConfig.tsx
│   │   │   └── 📁 dashboard/     # 仪表盘组件
│   │   │       ├── StatCard.tsx
│   │   │       ├── SalesChart.tsx
│   │   │       └── CategoryChart.tsx
│   │   │
│   │   ├── 📁 services/          # API 服务
│   │   │   ├── api.ts           # API 调用封装
│   │   │   └── mockData.ts      # Mock 数据
│   │   │
│   │   ├── 📁 types/             # TypeScript 类型定义
│   │   │   └── index.ts
│   │   │
│   │   ├── 📁 utils/             # 工具函数
│   │   │   └── cn.ts            # className 工具
│   │   │
│   │   ├── App.tsx              # 应用主组件
│   │   ├── main.tsx             # 应用入口
│   │   └── index.css            # 全局样式
│   │
│   ├── index.html               # HTML 模板
│   ├── package.json             # 前端依赖配置
│   ├── vite.config.ts           # Vite 配置
│   ├── tailwind.config.js       # TailwindCSS 配置
│   ├── tsconfig.json            # TypeScript 配置
│   └── README.md                # 前端说明
│
├── 📁 scripts/                    # 脚本文件
│   ├── start.bat                # 启动脚本
│   └── stop.bat                 # 停止脚本
│
├── 📁 docs/                       # 文档
│   ├── QUICKSTART.md            # 快速开始
│   ├── API.md                   # API 文档
│   ├── ARCHITECTURE.md          # 架构说明
│   └── STRUCTURE.md             # 本文件 - 项目结构
│
├── 📁 venv/                       # Python 虚拟环境
│
├── START.bat                     # 一键启动 (根目录)
├── STOP.bat                      # 一键停止 (根目录)
├── requirements.txt              # Python 依赖列表
├── .gitignore                    # Git 忽略文件
└── README.md                     # 项目主说明文档

```

## 文件说明

### 核心文件

| 文件 | 说明 |
|------|------|
| `backend/api.py` | FastAPI 路由定义，提供 RESTful API |
| `backend/agents.py` | AI Agent 核心逻辑，选品和文案生成 |
| `backend/llm_service.py` | DeepSeek LLM 调用封装 |
| `frontend/src/pages/` | React 页面组件 |
| `frontend/src/services/api.ts` | 前端 API 调用服务 |

### 配置文件

| 文件 | 说明 |
|------|------|
| `backend/config.py` | 后端配置（API Key 等） |
| `frontend/.env.local` | 前端环境变量 |
| `requirements.txt` | Python 依赖 |
| `frontend/package.json` | Node.js 依赖 |

### 文档文件

| 文件 | 说明 |
|------|------|
| `README.md` | 项目总览和快速开始 |
| `docs/QUICKSTART.md` | 详细安装和启动指南 |
| `docs/API.md` | API 接口文档 |
| `docs/ARCHITECTURE.md` | 系统架构说明 |
| `docs/STRUCTURE.md` | 项目结构说明（本文件） |

### 脚本文件

| 文件 | 说明 |
|------|------|
| `START.bat` | 一键启动前后端服务 |
| `STOP.bat` | 一键停止所有服务 |
| `scripts/start.bat` | 实际启动脚本 |
| `scripts/stop.bat` | 实际停止脚本 |

## 代码组织原则

### 后端 (Python)
- **单一职责**: 每个模块负责特定功能
- **依赖注入**: Agent 通过构造函数接收依赖
- **类型提示**: 使用 Type Hints 提高代码可读性

### 前端 (React)
- **组件化**: UI 拆分为可复用组件
- **类型安全**: TypeScript 类型定义
- **关注点分离**: Pages, Components, Services 分层

## 添加新功能

### 1. 添加新的 API 接口

在 `backend/api.py` 中添加路由:
```python
@app.post("/your/new/endpoint")
def your_function():
    # 实现逻辑
    pass
```

### 2. 添加新的页面

在 `frontend/src/pages/` 中创建新组件:
```typescript
export default function YourPage() {
    return <div>Your Content</div>;
}
```

### 3. 添加新的 Agent

在 `backend/agents.py` 中创建新类:
```python
class YourAgent:
    def __init__(self, llm: DeepSeekLLM):
        self.llm = llm
    
    def your_method(self):
        # 实现逻辑
        pass
```














