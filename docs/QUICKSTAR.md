# 快速开始指南

## 安装步骤

1. **安装 Python 依赖**
   ```bash
   .\venv\Scripts\pip install -r requirements.txt
   ```

2. **安装前端依赖**
   ```bash
   cd frontend
   npm install
   ```

3. **配置 API Key**
   
   编辑 `backend/config.py`:
   ```python
   DEEPSEEK_API_KEY = "your-api-key-here"
   ```

## 启动服务

### 一键启动 (推荐)

双击 `scripts/start.bat`

### 手动启动

**终端 1 - 启动后端:**
```bash
.\venv\Scripts\python backend\api.py
```

**终端 2 - 启动前端:**
```bash
cd frontend
npm run dev
```

## 访问应用

- 前端: http://localhost:5173
- API 文档: http://127.0.0.1:8000/docs

## 停止服务

双击 `scripts/stop.bat`

