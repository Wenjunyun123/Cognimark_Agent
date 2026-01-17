# 前端应用

SmartCross 跨境电商智能选品与营销平台的前端应用。

## 技术栈

- **React 18**: 现代化的UI框架
- **TypeScript**: 类型安全
- **Vite**: 快速的构建工具
- **Tailwind CSS**: 实用优先的CSS框架
- **React Router DOM**: 路由管理
- **Recharts**: 数据可视化
- **Lucide React**: 图标库

## 项目结构

```
frontend/src/
├── assets/           # 静态资源
├── components/       # 可复用组件
│   ├── dashboard/   # 仪表盘组件
│   ├── layout/      # 布局组件
│   ├── marketing/   # 营销相关组件
│   └── products/    # 产品相关组件
├── pages/           # 页面组件
├── services/        # API服务
├── types/           # TypeScript类型定义
├── utils/           # 工具函数
├── App.tsx          # 应用根组件
└── main.tsx         # 入口文件
```

## 开发指南

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

应用将在 http://localhost:5173 运行

### 构建生产版本

```bash
npm run build
```

构建产物将输出到 `dist/` 目录

### 预览生产构建

```bash
npm run preview
```

## 环境变量

创建 `.env` 文件并配置以下变量：

```env
VITE_ALI_API_KEY=your_api_key_here
VITE_API_BASE_URL=http://localhost:3000/api
```

## 页面路由

- `/` - 运营仪表盘
- `/products` - 智能选品分析
- `/marketing` - 智能营销 Copilot
- `/settings` - 设置（开发中）

## 代码规范

- 使用 TypeScript 进行类型检查
- 组件使用函数式组件和 Hooks
- 样式使用 Tailwind CSS
- 遵循 ESLint 规则

## 主要功能

### 1. 运营仪表盘
- 实时销售数据展示
- 订单趋势分析
- 分类销售占比
- 核心业务指标

### 2. 智能选品分析
- 产品数据表格
- AI 驱动的产品分析
- 市场趋势洞察
- 竞品对比

### 3. 智能营销 Copilot
- AI 营销文案生成
- 多平台适配
- 目标受众定制
- 实时对话交互



