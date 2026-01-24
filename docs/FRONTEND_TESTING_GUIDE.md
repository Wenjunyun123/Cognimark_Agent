# CogniMark 前端功能测试指南

## 🚀 启动服务

### 1. 启动后端服务器

```bash
cd backend
python api.py
```

**预期输出**:
```
INFO:     Started server process number
INFO:     Waiting for application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 2. 启动前端开发服务器

```bash
cd frontend
npm run dev
```

**预期输出**:
```
VITE v5.x.x ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

### 3. 打开浏览器

访问: **http://localhost:5173/**

---

## 📋 功能测试清单

### ✅ 功能1: 产品智能选品

**路径**: 点击侧边栏 "Product Intelligence" 或访问 `/#/product-intelligence`

**测试步骤**:
1. 在 "Campaign Description" 输入框填写：
   ```
   Summer promotion targeting young professionals who love outdoor sports
   ```
2. 选择 Target Market: `US`
3. 设置推荐数量: `3`
4. 点击 **"Get Recommendations"** 按钮

**预期结果**:
- 显示3个推荐产品卡片
- 每个卡片包含产品信息（名称、价格、评分、销量）
- 下方显示AI分析理由

**检查点**:
- [ ] 按钮点击后loading状态正常
- [ ] 产品卡片正确显示
- [ ] AI分析文本显示（可能需要几秒钟）

---

### ✅ 功能2: 营销文案生成

**路径**: 点击侧边栏 "Marketing Copilot" 或访问 `/#/marketing-copilot`

**测试步骤**:
1. 选择产品: 从下拉菜单选择 `P001 - Stainless Steel Insulated Water Bottle`
2. 选择目标语言: `English`
3. 选择投放渠道: `Facebook Ads`
4. 点击 **"Generate Copy"** 按钮

**预期结果**:
- 生成标题（≤80字符）
- 3个核心卖点
- 广告正文（100-150字）

**检查点**:
- [ ] 生成的文案包含产品相关信息
- [ ] 文案语言正确（根据选择的语言）
- [ ] 格式化显示（标题、列表、段落）

---

### ✅ 功能3: RAG智能推荐（新功能🌟）

**路径**: Dashboard页面对话模式

**测试步骤**:
1. 在Dashboard的聊天输入框输入：
   ```
   使用RAG向量搜索推荐适合夏季户外运动的产品
   ```
2. 点击 **发送** 按钮

**预期结果**:
- 系统会使用RAG进行语义搜索
- 推荐结果应该比传统方法更精准
- 例如：查询"outdoor sports"应该推荐Yoga Mat而非Phone Case

**如何验证RAG工作**:
1. 打开浏览器开发者工具（F12）
2. 切换到Network标签
3. 发送聊天消息后，观察API调用
4. 应该看到 `/rag/recommend` 或 `/rag/compare` 请求

---

### ✅ 功能4: 多LLM切换（新功能🌟）

**测试方式1: Swagger UI**
1. 访问: `http://127.0.0.1:8000/docs`
2. 找到 `POST /rag/compare` 端点
3. 点击 "Try it out"
4. 执行请求

**预期结果**:
- 返回两个结果：`traditional` 和 `rag`
- 可以对比两种方法的差异

**测试方式2: API调用**
```bash
curl -X POST http://127.0.0.1:8000/rag/compare \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_description": "Summer promotion for outdoor sports",
    "target_market": "US",
    "top_k": 3
  }'
```

---

### ✅ 功能5: 文件上传与分析

**路径**: Dashboard页面

**测试步骤**:
1. 点击聊天框上方的 📎 图标
2. 选择一个Excel/CSV文件（如果没有，可以创建一个简单的测试文件）
3. 上传文件

**预期结果**:
- 显示文件基本信息（行数、列数）
- 显示列名和数据预览
- 文件数据会被注入到对话上下文中

---

### ✅ 功能6: 会话历史管理

**路径**: Dashboard页面侧边栏

**测试步骤**:
1. 发送几条消息
2. 观察侧边栏会话历史
3. 点击 "+" 新建会话
4. 点击历史会话切换

**预期结果**:
- 会话历史自动保存
- 可以切换会话
- 新会话有默认标题

---

### ✅ 功能7: 多模式对话

**路径**: Dashboard页面

**测试步骤**:
1. 在输入框输入以下任一模式：
   - `[市场趋势分析模式] 分析美国市场的电子产品趋势`
   - `[选品策略建议模式] 推荐适合年轻人的产品`
   - `[广告优化建议模式] 优化我的Facebook广告`
   - `[转化率优化模式] 提高产品页转化率`

**预期结果**:
- AI会以该专家模式回复
- 回复内容符合模式设定

---

## 🔧 高级测试：API端点

### Swagger UI测试

**访问**: `http://127.0.0.1:8000/docs`

**推荐测试的端点**:

#### 1. GET /rag/status
检查RAG服务状态

#### 2. POST /rag/recommend
RAG智能推荐

**请求体**:
```json
{
  "campaign_description": "Summer promotion for outdoor sports",
  "target_market": "US",
  "top_k": 3,
  "use_reranking": true
}
```

#### 3. POST /rag/compare
对比传统方法与RAG方法

#### 4. GET /products
获取所有产品列表

#### 5. POST /selection/recommend
使用传统启发式方法推荐

---

## 🐛 故障排查

### 问题1: 后端连接失败

**症状**: 前端显示网络错误

**检查**:
```bash
# 检查后端是否运行
curl http://127.0.0.1:8000/products
```

**解决**: 启动后端服务器 `python backend/api.py`

### 问题2: RAG功能不工作

**症状**: `/rag/recommend` 返回错误

**检查**:
1. 后端控制台是否有错误
2. 是否已初始化向量数据库

**解决**:
```bash
# 手动初始化RAG
curl -X POST http://127.0.0.1:8000/rag/initialize
```

### 问题3: 数据库为空

**症状**: 产品列表为空

**检查**:
```bash
cd backend
python database/db_init.py
```

### 问题4: 前端页面空白

**症状**: 页面加载后白屏

**检查**:
1. 浏览器控制台是否有错误（F12 → Console）
2. 网络请求是否成功（F12 → Network）

**解决**: 重新安装前端依赖 `npm install`

---

## 📊 功能对比测试

### 传统方法 vs RAG方法

**测试场景**: "Summer promotion for outdoor sports"

**传统方法**:
- 使用启发式评分（价格×销量÷对数）
- 可能推荐：Phone Case（不相关）
- 基于：评分公式

**RAG方法**:
- 使用语义向量搜索
- 可能推荐：Yoga Mat（相关）
- 基于：语义理解

**对比方式**:
1. 使用相同查询测试两种方法
2. 观察推荐结果的差异
3. 验证RAG是否更智能

---

## 🎯 核心功能验证清单

### 基础功能
- [ ] 页面加载正常
- [ ] 侧边栏导航可用
- [ ] 路由切换正常

### 产品选品功能
- [ ] 输入描述后能推荐产品
- [ ] 显示产品详情
- [ ] AI分析文本生成

### 营销文案功能
- [ ] 选择产品后能生成文案
- [ ] 支持多语言
- [ ] 支持多渠道

### RAG增强功能（重点）
- [ ] RAG服务状态正常
- [ ] RAG推荐结果准确
- [ ] 与传统方法有差异

### 数据管理
- [ ] 文件上传功能
- [ ] 会话历史保存
- [ ] 数据持久化

---

## 💡 提示

1. **首次运行**: 首次运行需要下载embedding模型（~100MB），可能较慢
2. **API Key**: 需要在环境变量中设置 `DEEPSEEK_API_KEY`
3. **数据库**: 首次运行会自动创建SQLite数据库
4. **向量数据库**: RAG功能需要ChromaDB，首次会自动初始化

---

## 📝 测试笔记

建议按以下顺序测试：
1. ✅ 基础页面加载
2. ✅ 产品选品（传统方法）
3. ✅ 营销文案生成
4. ✅ **RAG增强功能**（重点）
5. ✅ 文件上传
6. ✅ 会话管理

---

**祝测试顺利！**
如有问题，检查后端控制台输出和浏览器开发者工具。
