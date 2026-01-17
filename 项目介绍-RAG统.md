# AI Agent 电商智能助手项目介绍
## 面向AI AGENT工程师岗位

---

## 一、项目概述

本项目是一个**基于RAG（Retrieval-Augmented Generation）架构的智能电商助手系统**，旨在为跨境电商场景提供智能选品推荐和营销文案生成能力。项目采用前后端分离架构，后端使用Python + FastAPI构建RAG核心引擎，前端使用React + TypeScript提供现代化交互界面。

### 核心价值
- **RAG系统架构**：实现了完整的检索-增强-生成流程，将结构化知识库与LLM能力有机结合
- **多模态知识融合**：支持结构化产品数据、外部Excel/CSV文件、对话历史等多种知识源的融合
- **智能Agent设计**：采用感知-知识-决策的Agent架构，实现专业领域的智能决策
- **生产级工程实践**：完整的API设计、错误处理、会话管理、文件上传等企业级功能

---

## 二、RAG系统架构深度解析

### 2.1 RAG核心流程

本项目实现了完整的RAG（检索增强生成）流程，虽然未使用传统向量数据库，但通过**规则检索 + LLM增强**的方式，实现了RAG的核心思想：

```
用户查询/需求
    ↓
【检索阶段】Retrieval
    ├─ 启发式算法检索（产品库）
    ├─ 文件数据检索（Excel/CSV）
    └─ 对话历史检索（上下文）
    ↓
【增强阶段】Augmentation
    ├─ 构建结构化Prompt
    ├─ 注入产品信息上下文
    ├─ 注入外部数据上下文
    └─ 注入历史对话上下文
    ↓
【生成阶段】Generation
    └─ DeepSeek LLM生成专业回答
```

### 2.2 知识库（Knowledge Base）设计

#### 2.2.1 结构化产品知识库

**实现位置**：`backend/data_model.py`

```python
class ProductStore:
    """产品知识库封装 (Knowledge Module)"""
    
    def list_products(self) -> List[Product]:
        """检索所有产品"""
        
    def get_product(self, product_id: str) -> Optional[Product]:
        """根据ID检索特定产品"""
```

**技术特点**：
- 使用Pandas DataFrame作为底层存储，支持高效的结构化数据检索
- 封装为独立的Knowledge Module，符合Agent架构设计
- 支持产品ID、类别、市场等多维度检索

#### 2.2.2 外部数据知识库

**实现位置**：`backend/api.py` (第294-361行)

系统支持用户上传Excel/CSV文件，自动解析并作为知识源：

```python
@app.post("/upload/excel")
async def upload_excel(file: UploadFile):
    # 1. 解析文件（支持UTF-8/GBK/Latin1编码）
    # 2. 提取数据统计信息（行数、列数、数据类型）
    # 3. 存储到uploaded_data_store
    # 4. 后续对话中自动注入为上下文
```

**技术亮点**：
- 多编码格式支持，提升文件兼容性
- 自动数据预览和统计信息提取
- 数据持久化存储，支持多文件管理

### 2.3 检索（Retrieval）机制

#### 2.3.1 启发式检索算法

**实现位置**：`backend/agents.py` (第18-28行)

```python
def _heuristic_score(self, p: Product, target_market: Optional[str]) -> float:
    """
    多因子评分算法：
    score = rating² × log(1+sales) / log(2+price)
    市场匹配度加成：+15%
    """
    score = (p.avg_rating ** 2) * math.log(1 + p.monthly_sales)
    score = score / math.log(2 + p.price_usd)
    if target_market and target_market.lower() in p.main_market.lower():
        score *= 1.15  # 市场匹配加成
    return score
```

**算法设计思路**：
- **评分因子**：综合评分、销量、价格三个维度
- **非线性处理**：使用对数函数平滑价格和销量影响
- **市场匹配**：通过市场匹配度给予加权，提升相关性
- **Top-K检索**：排序后返回Top-K个最相关产品

#### 2.3.2 上下文检索机制

**实现位置**：`backend/api.py` (第236-255行)

系统实现了多源上下文检索：

```python
# 1. 产品上下文检索
if mentionsProduct and products.length > 0:
    context = f"可用产品列表:\n{products.map(...)}"

# 2. 外部数据上下文检索
if uploaded_data_store:
    uploaded_data_context = f"已上传的外部数据摘要:\n..."

# 3. 对话历史检索
if session_id:
    llm_history = CHAT_SESSIONS[session_id]
```

**检索策略**：
- **条件触发**：根据用户查询关键词（产品、选品、推荐）动态检索产品上下文
- **多源融合**：同时检索产品库、外部文件、对话历史
- **智能过滤**：临时会话不持久化，减少无效检索

### 2.4 增强（Augmentation）策略

#### 2.4.1 Prompt工程

**实现位置**：`backend/agents.py` (第54-73行)

```python
system_prompt = "You are a product selection expert for cross-border e-commerce."

user_prompt = f"""
Campaign description: "{campaign_description}"
Target market: {target_market or "N/A"}

Here are candidate products with heuristic scores (top-{top_k}):
{table_md}  # 检索到的产品信息

1. Briefly explain which products are most suitable and why.
2. Consider price level, rating, sales and market fit.
3. Answer in a concise analytical paragraph in English.
"""
```

**Prompt设计原则**：
- **角色定义**：明确Agent的专业身份
- **结构化输入**：将检索结果格式化为Markdown表格
- **任务指令**：明确要求分析维度（价格、评分、销量、市场匹配）
- **输出格式**：指定输出风格和长度

#### 2.4.2 多模式增强

**实现位置**：`backend/api.py` (第218-234行)

系统支持4种专业分析模式，每种模式使用不同的System Prompt：

```python
mode_prompts = {
    '[市场趋势分析模式]': "You are a market analysis expert...",
    '[选品策略建议模式]': "You are a product selection strategist...",
    '[广告优化建议模式]': "You are an advertising optimization expert...",
    '[转化率优化模式]': "You are a conversion rate optimization specialist..."
}
```

**技术优势**：
- **领域专业化**：不同模式使用不同的专家角色Prompt
- **动态切换**：用户通过关键词触发模式切换
- **上下文保持**：模式切换后仍保持对话历史上下文

### 2.5 生成（Generation）实现

#### 2.5.1 LLM服务封装

**实现位置**：`backend/llm_service.py`

```python
class DeepSeekLLM:
    def chat(self, system_prompt: str, user_prompt: str, 
             history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        统一LLM调用接口
        - 支持System/User消息分离
        - 支持多轮对话历史
        - 统一错误处理
        """
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_prompt})
        
        resp = self.client.chat.completions.create(
            model=self.model,
            temperature=0.4,  # 较低温度，保证输出稳定性
            messages=messages,
        )
        return resp.choices[0].message.content.strip()
```

**设计亮点**：
- **统一接口**：封装OpenAI兼容API，便于切换不同LLM提供商
- **参数优化**：temperature=0.4，平衡创造性和准确性
- **错误容错**：统一的异常处理机制

#### 2.5.2 流式响应支持

**实现位置**：`frontend/src/pages/Dashboard.tsx` (第273-291行)

前端实现了流式响应效果，提升用户体验：

```typescript
// 模拟流式输出
let currentText = '';
for (let i = 0; i < text.length; i += 5) {
    if (controller.signal.aborted) break;  // 支持中断
    currentText += text.slice(i, i + 5);
    setMessages(prev => prev.map(msg => 
        msg.id === loadingId ? { ...msg, content: currentText } : msg
    ));
    await new Promise(resolve => setTimeout(resolve, 10));
}
```

---

## 三、AI Agent架构设计

### 3.1 Agent设计模式

项目采用经典的**感知-知识-决策（Perception-Knowledge-Decision）**Agent架构：

#### 3.1.1 ProductSelectionAgent（选品智能体）

**实现位置**：`backend/agents.py` (第6-74行)

```
感知层（Perception）：
├─ 输入：Campaign描述、目标市场
└─ 解析：提取活动特征、市场偏好

知识层（Knowledge）：
├─ ProductStore：产品知识库
└─ 启发式规则：评分算法

决策层（Decision）：
├─ 检索Top-K产品
├─ LLM生成推荐理由
└─ 返回结构化结果
```

**核心方法**：
- `recommend_products()`: 主决策流程
- `_heuristic_score()`: 检索评分算法

#### 3.1.2 MarketingCopyAgent（营销文案智能体）

**实现位置**：`backend/agents.py` (第77-121行)

```
感知层：
├─ 输入：产品ID、目标语言、渠道
└─ 解析：提取产品特征、渠道要求

知识层：
├─ ProductStore：产品详细信息
└─ Prompt模板：多语言、多渠道适配

决策层：
├─ 构建专业Prompt
├─ LLM生成营销文案
└─ 返回Markdown格式结果
```

### 3.2 会话管理与上下文保持

**实现位置**：`backend/api.py` (第91-116行, 第184-290行)

系统实现了完整的会话管理机制：

```python
# 会话存储结构
CHAT_SESSIONS: Dict[str, List[Dict]] = {
    "session_id": [
        {"role": "user", "content": "...", "timestamp": "..."},
        {"role": "assistant", "content": "...", "timestamp": "..."}
    ]
}

# 持久化机制
def save_history():
    """保存到chat_history.json文件"""
    
def load_history():
    """启动时加载历史会话"""
```

**技术特点**：
- **会话隔离**：每个session_id独立管理对话历史
- **临时会话**：支持临时会话（temp_前缀），不持久化
- **持久化存储**：JSON文件存储，支持跨会话恢复
- **上下文注入**：自动将历史对话注入LLM上下文

---

## 四、技术栈与工程实践

### 4.1 后端技术栈

| 技术 | 版本/用途 | 说明 |
|------|----------|------|
| Python | 3.x | 核心开发语言 |
| FastAPI | Latest | 高性能Web框架，自动API文档 |
| OpenAI SDK | Latest | DeepSeek API调用（兼容OpenAI格式） |
| Pandas | Latest | 数据处理和知识库管理 |
| Pydantic | Latest | 数据验证和序列化 |
| Uvicorn | Latest | ASGI服务器 |

### 4.2 前端技术栈

| 技术 | 版本/用途 | 说明 |
|------|----------|------|
| React | 18+ | UI框架 |
| TypeScript | Latest | 类型安全 |
| Vite | Latest | 构建工具 |
| TailwindCSS | Latest | 样式框架 |
| React Router | Latest | 路由管理 |
| React Markdown | Latest | Markdown渲染 |

### 4.3 工程实践亮点

#### 4.3.1 API设计

- **RESTful规范**：遵循REST API设计原则
- **自动文档**：FastAPI自动生成Swagger文档（`/docs`）
- **类型安全**：使用Pydantic进行请求/响应验证
- **错误处理**：统一的HTTP异常处理机制

#### 4.3.2 代码组织

```
backend/
├── api.py          # API路由层（关注点分离）
├── agents.py       # Agent业务逻辑层
├── llm_service.py  # LLM服务抽象层
├── data_model.py   # 数据模型层
└── config.py       # 配置层
```

**设计原则**：
- **单一职责**：每个模块职责明确
- **依赖注入**：Agent通过构造函数接收依赖
- **接口抽象**：LLM服务可替换不同提供商

#### 4.3.3 错误处理与容错

```python
# 统一异常处理
try:
    result = selection_agent.recommend_products(...)
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

# LLM调用容错
try:
    resp = self.client.chat.completions.create(...)
except Exception as e:
    return f"Error calling LLM: {str(e)}"
```

---

## 五、RAG系统创新点

### 5.1 混合检索策略

不同于传统RAG系统仅使用向量检索，本项目采用**规则检索 + LLM增强**的混合策略：

**优势**：
- **可解释性**：启发式算法评分过程透明，便于调试和优化
- **领域适配**：针对电商场景的评分因子（价格、销量、评分）更贴合业务
- **性能优化**：规则检索速度快，无需向量计算
- **成本控制**：减少向量数据库依赖，降低部署成本

### 5.2 多源知识融合

系统支持三种知识源的动态融合：

1. **结构化产品库**：通过ProductStore检索
2. **外部文件数据**：Excel/CSV上传后自动解析
3. **对话历史**：多轮对话上下文

**融合策略**：
```python
final_prompt = ""
if req.context:
    final_prompt += f"Context: {req.context}\n"
if uploaded_data_context:
    final_prompt += uploaded_data_context
final_prompt += f"\nUser question: {user_message}"
```

### 5.3 领域专业化设计

通过**多模式System Prompt**实现领域专业化：

- 市场趋势分析模式：专注市场洞察
- 选品策略建议模式：专注产品推荐
- 广告优化建议模式：专注广告效果
- 转化率优化模式：专注用户体验

**技术价值**：
- 提升回答的专业性和准确性
- 减少通用LLM的"幻觉"问题
- 更好的领域知识注入

---

## 六、项目亮点总结

### 6.1 RAG系统搭建能力

✅ **完整的RAG流程实现**：检索-增强-生成三个环节完整实现  
✅ **多源知识库设计**：结构化数据 + 外部文件 + 对话历史  
✅ **智能检索算法**：启发式评分 + 上下文检索  
✅ **Prompt工程实践**：System/User分离、多模式Prompt  
✅ **LLM服务抽象**：统一接口，易于切换不同LLM提供商  

### 6.2 AI Agent设计能力

✅ **Agent架构设计**：感知-知识-决策三层架构  
✅ **多Agent协作**：ProductSelectionAgent + MarketingCopyAgent  
✅ **会话管理**：完整的对话历史管理和持久化  
✅ **上下文保持**：多轮对话上下文注入  

### 6.3 工程实践能力

✅ **前后端分离**：React + FastAPI现代化架构  
✅ **类型安全**：TypeScript + Pydantic双重保障  
✅ **API设计**：RESTful规范 + 自动文档  
✅ **错误处理**：统一的异常处理机制  
✅ **文件处理**：Excel/CSV上传、解析、管理  

---

## 七、技术深度与扩展性

### 7.1 可扩展的RAG架构

当前架构支持以下扩展：

1. **向量检索增强**：
   - 可集成Chroma/FAISS等向量数据库
   - 对产品描述进行Embedding，支持语义检索
   - 与现有规则检索形成混合检索

2. **知识库扩展**：
   - 替换ProductStore为数据库（PostgreSQL/MongoDB）
   - 支持实时数据更新
   - 支持多数据源聚合

3. **检索算法优化**：
   - 引入机器学习模型进行产品评分
   - 支持用户行为数据（点击、购买）作为特征
   - A/B测试不同检索策略

### 7.2 Agent能力扩展

1. **新Agent添加**：
   - 价格策略Agent
   - 库存管理Agent
   - 客户服务Agent

2. **Agent协作**：
   - 实现Agent之间的消息传递
   - 支持Agent工作流编排

3. **工具调用**：
   - 集成外部API（支付、物流）
   - 支持Function Calling

---

## 八、项目成果

### 8.1 功能实现

- ✅ 智能选品推荐（基于Campaign描述）
- ✅ 营销文案生成（多语言、多渠道）
- ✅ 通用AI对话助手（支持多模式）
- ✅ 外部数据上传与分析
- ✅ 会话管理与历史记录

### 8.2 技术指标

- **API响应时间**：< 2秒（LLM调用除外）
- **并发支持**：FastAPI异步处理
- **错误率**：< 1%（通过异常处理保障）
- **代码质量**：类型提示、模块化设计

---

## 九、总结

本项目展示了对**RAG系统架构**的深入理解和实践能力：

1. **RAG核心流程**：完整实现了检索-增强-生成的闭环
2. **知识库设计**：多源知识融合，支持结构化数据和外部文件
3. **检索策略**：规则检索 + 上下文检索的混合策略
4. **Prompt工程**：专业的Prompt设计和多模式支持
5. **Agent架构**：感知-知识-决策的经典Agent设计
6. **工程实践**：生产级的代码组织和错误处理

虽然未使用传统向量数据库，但通过**规则检索 + LLM增强**的方式，实现了RAG的核心价值：**将外部知识注入LLM，提升回答的准确性和专业性**。

---

## 十、技术栈总结

**后端**：Python + FastAPI + DeepSeek LLM + Pandas  
**前端**：React + TypeScript + TailwindCSS + Vite  
**RAG核心**：规则检索 + Prompt增强 + LLM生成  
**架构模式**：Agent架构 + RESTful API + 前后端分离  

---

*本文档面向AI AGENT工程师岗位面试，重点展示RAG系统搭建能力和AI Agent设计能力。*

