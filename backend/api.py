import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import io
import json
import os
import uuid
from typing import List, Optional, Dict
from datetime import datetime

from llm_service import DeepSeekLLM, LLMService
from data_model import default_store, Product
from agents import ProductSelectionAgent, MarketingCopyAgent

# 初始化 FastAPI
app = FastAPI(title="AI Agent E-Commerce API", version="2.0")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源访问，生产环境请指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务
llm = DeepSeekLLM()
selection_agent = ProductSelectionAgent(default_store, llm)
copy_agent = MarketingCopyAgent(llm)

# --- Pydantic Models ---

class ProductSimple(BaseModel):
    product_id: str
    title_en: str

class ProductDetail(BaseModel):
    product_id: str
    title_en: str
    category: str
    price_usd: float
    avg_rating: float
    monthly_sales: int
    main_market: str
    tags: str

class SelectionRequest(BaseModel):
    campaign_description: str
    target_market: Optional[str] = None
    top_k: int = 3

class SelectionResponse(BaseModel):
    products: List[ProductDetail]
    explanation: str

class CopyRequest(BaseModel):
    product_id: str
    target_language: str
    channel: str

class CopyResponse(BaseModel):
    copy_text: str

class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None
    history: Optional[List[ChatMessage]] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    message_id: str
    thinking: Optional[str] = None  # Agent 的思考过程


class FileAnalysisResponse(BaseModel):
    summary: str
    data_preview: dict
    column_info: dict

# --- 存储上传的数据（临时，实际应用中应使用数据库或缓存）
uploaded_data_store = {}

# --- 聊天历史持久化 ---
HISTORY_FILE = "chat_history.json"
# 结构: { session_id: [messages] }
CHAT_SESSIONS: Dict[str, List[Dict]] = {}

def load_history():
    """从文件加载聊天历史"""
    global CHAT_SESSIONS
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                CHAT_SESSIONS = json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")
            CHAT_SESSIONS = {}

def save_history():
    """保存聊天历史到文件"""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(CHAT_SESSIONS, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving history: {e}")

# 初始化时加载历史
load_history()

# --- Endpoints ---

@app.get("/products", response_model=List[ProductSimple])
def list_products():
    """获取所有可用产品列表 (ID + Title)"""
    products = default_store.list_products()
    return [
        ProductSimple(product_id=p.product_id, title_en=p.title_en)
        for p in products
    ]

@app.post("/selection/recommend", response_model=SelectionResponse)
def recommend_products(req: SelectionRequest):
    """根据 Campaign 描述推荐产品"""
    try:
        top_products, explanation = selection_agent.recommend_products(
            campaign_description=req.campaign_description,
            target_market=req.target_market,
            top_k=req.top_k
        )
        
        # Convert data_model.Product objects to Pydantic models
        product_details = []
        for p in top_products:
            product_details.append(ProductDetail(
                product_id=p.product_id,
                title_en=p.title_en,
                category=p.category,
                price_usd=p.price_usd,
                avg_rating=p.avg_rating,
                monthly_sales=p.monthly_sales,
                main_market=p.main_market,
                tags=p.tags
            ))
            
        return SelectionResponse(products=product_details, explanation=explanation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/marketing/generate", response_model=CopyResponse)
def generate_copy(req: CopyRequest):
    """生成营销文案"""
    product = default_store.get_product(req.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    try:
        result = copy_agent.generate_copy(
            product=product,
            target_language=req.target_language,
            channel=req.channel
        )
        return CopyResponse(copy_text=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent/history", response_model=List[ChatMessage])
def get_chat_history(session_id: Optional[str] = None):
    """获取历史对话记录"""
    if session_id and session_id in CHAT_SESSIONS:
        return [
            ChatMessage(role=msg["role"], content=msg["content"])
            for msg in CHAT_SESSIONS[session_id]
        ]
    return []

@app.post("/agent/chat", response_model=ChatResponse)
def chat_with_agent(req: ChatRequest):
    """通用智能体对话接口（支持多轮对话）"""
    try:
        # 1. 确定会话上下文
        session_id = req.session_id
        current_history = []

        if session_id:
            is_temp_session = session_id.startswith('temp_')
            if not is_temp_session and session_id not in CHAT_SESSIONS:
                CHAT_SESSIONS[session_id] = []
                current_history = CHAT_SESSIONS[session_id]
            elif not is_temp_session:
                current_history = CHAT_SESSIONS[session_id]

        # 2. 保存用户消息到历史
        if session_id and not session_id.startswith('temp_'):
            user_msg_entry = {
                "role": "user",
                "content": req.message,
                "timestamp": datetime.now().isoformat()
            }
            if current_history is not None:
                current_history.append(user_msg_entry)
                save_history()

        # 检测分析模式
        mode_prompts = {
            '[市场趋势分析模式]': "You are a market analysis expert. Focus on market trends, opportunities, competitive landscape, and data-driven insights. Provide actionable recommendations based on data.",
            '[选品策略建议模式]': "You are a product selection strategist. Focus on product recommendations, category analysis, profit potential, and market fit. Use data to support your suggestions.",
            '[广告优化建议模式]': "You are an advertising optimization expert. Focus on ad performance, ROI improvement, targeting strategies, and campaign optimization. Provide specific, measurable advice.",
            '[转化率优化模式]': "You are a conversion rate optimization specialist. Focus on user experience, funnel optimization, A/B testing, and conversion tactics. Give practical improvement steps."
        }

        system_prompt = "You are CogniMark, a helpful AI assistant specialized in cross-border e-commerce, product selection, and marketing. You provide professional, actionable advice. Maintain conversation context and refer to previous messages when relevant."
        user_message = req.message
        detected_mode = "普通模式"

        for mode_key, mode_system in mode_prompts.items():
            if user_message.startswith(mode_key):
                system_prompt = mode_system + " Maintain conversation context and refer to previous messages when relevant."
                user_message = user_message.replace(mode_key, '').strip()
                detected_mode = mode_key.replace('[', '').replace(']', '')
                break

        # 收集上传数据上下文
        uploaded_data_context = ""
        if uploaded_data_store:
            uploaded_data_context = "\n\n【已上传的外部数据】\n"
            for filename, data_info in uploaded_data_store.items():
                uploaded_data_context += f"- {filename}: {data_info['rows']}行 × {data_info['columns']}列 | 列名: {', '.join(data_info['column_names'])}\n"
                # 添加数据预览（关键修复：让 AI 能看到文件内容）
                if 'dataframe' in data_info:
                    try:
                        df = data_info['dataframe']
                        # 预览前 10 行，使用 CSV 格式
                        preview = df.head(10).to_csv(index=False)
                        uploaded_data_context += f"\n[数据预览 - 前10行]:\n{preview}\n\n"
                    except Exception as e:
                        print(f"Error generating preview for {filename}: {e}")

        # 收集历史对话上下文
        history_context = ""
        if current_history and len(current_history) > 1:
            history_context = "\n\n【历史对话摘要】\n"
            for msg in current_history[-3:-1]:  # 只取最近3条
                role = "用户" if msg["role"] == "user" else "助手"
                history_context += f"- {role}: {msg['content'][:100]}{'...' if len(msg['content']) > 100 else ''}\n"

        # 构建 LLM 历史上下文
        llm_history = []
        if session_id and not session_id.startswith('temp_'):
            if current_history:
                for msg in current_history[:-1]:
                    llm_history.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
        elif req.history:
            for msg in req.history:
                llm_history.append({
                    "role": msg.role,
                    "content": msg.content
                })

        # 生成深度思考过程
        thinking_prompt = f"""你是一个专业的 AI 助手 CogniMark。现在请你分析用户的问题，并展示你的思考过程。

【用户问题】
{req.message}

【当前模式】
{detected_mode}

【可用上下文】
{uploaded_data_context if uploaded_data_context else "无额外数据"}
{history_context if history_context else "无历史对话"}

【你的任务】
请按以下结构展示你的深度思考过程：

## 用户输入分析
- 分析用户的问题类型、核心诉求、潜在需求
- 识别关键信息和背景

## 问题理解
- 从专业角度解读问题的本质
- 判断需要哪些知识或工具来回答

## 思考路径
- 展示你的推理逻辑
- 说明为什么选择这种回答方式
- 如果有多个可能的解决方案，说明你选择的理由

## 回答策略
- 说明你将如何组织回答
- 强调回答的重点和结构

请用中文回答，语言要自然流畅，展示真实的思考过程。"""

        # 调用 LLM 生成思考过程
        thinking_content = llm.chat(
            "你是 CogniMark 的思考模块。请展示你的深度思考过程，帮助用户理解你的分析逻辑。",
            thinking_prompt,
            history=[]  # 思考过程不需要历史
        )

        # 构建最终提示
        final_prompt = ""
        if req.context:
            final_prompt += f"Context: {req.context}\n"
        if uploaded_data_context:
            final_prompt += uploaded_data_context + "\n"
        final_prompt += f"User question: {user_message}"

        # 生成最终回答
        response_text = llm.chat(system_prompt, final_prompt, history=llm_history)

        # 保存助手回复
        if session_id and not session_id.startswith('temp_'):
            assistant_msg_entry = {
                "role": "assistant",
                "content": response_text,
                "timestamp": datetime.now().isoformat()
            }
            if current_history is not None:
                current_history.append(assistant_msg_entry)
                save_history()

        return ChatResponse(
            response=response_text,
            message_id=str(uuid.uuid4()),
            thinking=thinking_content
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/chat/stream")
async def chat_with_agent_stream(req: ChatRequest):
    """
    流式聊天接口 - 实时展示思考过程和回答

    使用 Chain of Thought (CoT) 让模型展示真实推理过程
    """
    async def generate_stream():
        try:
            import asyncio

            # 【方案 A：流式骨架预响应】立即发送状态通知，减少用户感知等待时间
            yield f"event: status\ndata: {{\"message\": \"正在分析您的需求...\"}}\n\n"

            # 1. 确定会话上下文
            session_id = req.session_id
            current_history = []

            if session_id:
                is_temp_session = session_id.startswith('temp_')
                if not is_temp_session and session_id not in CHAT_SESSIONS:
                    CHAT_SESSIONS[session_id] = []
                    current_history = CHAT_SESSIONS[session_id]
                elif not is_temp_session:
                    current_history = CHAT_SESSIONS[session_id]

            # 2. 保存用户消息
            if session_id and not session_id.startswith('temp_'):
                user_msg_entry = {
                    "role": "user",
                    "content": req.message,
                    "timestamp": datetime.now().isoformat()
                }
                if current_history is not None:
                    current_history.append(user_msg_entry)
                    save_history()

            # 检测分析模式
            mode_prompts = {
                '[市场趋势分析模式]': "You are a market analysis expert. Focus on market trends, opportunities, competitive landscape, and data-driven insights. Provide actionable recommendations based on data.",
                '[选品策略建议模式]': "You are a product selection strategist. Focus on product recommendations, category analysis, profit potential, and market fit. Use data to support your suggestions.",
                '[广告优化建议模式]': "You are an advertising optimization expert. Focus on ad performance, ROI improvement, targeting strategies, and campaign optimization. Provide specific, measurable advice.",
                '[转化率优化模式]': "You are a conversion rate optimization specialist. Focus on user experience, funnel optimization, A/B testing, and conversion tactics. Give practical improvement steps."
            }

            system_prompt = "You are CogniMark, a helpful AI assistant specialized in cross-border e-commerce, product selection, and marketing. You provide professional, actionable advice. Maintain conversation context and refer to previous messages when relevant."
            user_message = req.message

            for mode_key, mode_system in mode_prompts.items():
                if user_message.startswith(mode_key):
                    system_prompt = mode_system + " Maintain conversation context and refer to previous messages when relevant."
                    user_message = user_message.replace(mode_key, '').strip()
                    break

            # 收集上下文
            uploaded_data_context = ""
            if uploaded_data_store:
                uploaded_data_context = "\n\n【已上传的外部数据】\n"
                for filename, data_info in uploaded_data_store.items():
                    uploaded_data_context += f"- {filename}: {data_info['rows']}行 × {data_info['columns']}列\n"
                    # 添加数据预览（关键修复：让 AI 能看到文件内容）
                    if 'dataframe' in data_info:
                        try:
                            df = data_info['dataframe']
                            # 预览前 10 行，使用 CSV 格式
                            preview = df.head(10).to_csv(index=False)
                            uploaded_data_context += f"\n[数据预览 - 前10行]:\n{preview}\n\n"
                        except Exception as e:
                            print(f"Error generating preview for {filename}: {e}")

            # 📚 使用商品检索系统查询数据
            database_context = ""
            try:
                from rag.product_rag import get_product_rag

                # 获取商品检索实例
                product_rag = get_product_rag()

                # 发送检索状态通知
                yield f"event: status\ndata: {{\"message\": \"正在检索商品数据库...\"}}\n\n"

                # 执行检索
                search_result = product_rag.search(
                    query=user_message,
                    top_k=20  # 返回最多20条结果
                )

                # 格式化结果
                if search_result["total"] > 0:
                    database_context = product_rag.format_for_llm(search_result, compact=True)

                    # 发送检索完成通知，显示找到多少结果
                    yield f"event: status\ndata: {{\"message\": \"已找到 {search_result['total']} 条相关商品，正在生成回答...\"}}\n\n"

            except Exception as e:
                # 如果查询失败，不影响正常对话
                import traceback
                print(f"产品RAG查询错误: {e}")
                traceback.print_exc()

            # 构建 LLM 历史上下文
            llm_history = []
            if session_id and not session_id.startswith('temp_'):
                if current_history:
                    for msg in current_history[:-1]:
                        llm_history.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
            elif req.history:
                for msg in req.history:
                    llm_history.append({
                        "role": msg.role,
                        "content": msg.content
                    })

            # 使用 CoT prompting 让模型展示真实思考过程（中文）
            # 使用特殊分隔符
            cot_system_prompt = system_prompt + "\n\n重要提示：在回答之前，你必须展示你的思考过程。请严格按照以下格式：\n\n[深度思考]\n首先，分析用户的问题...\n然后，考虑上下文信息...\n最后，确定回答方案...\n\n[回答]\n现在提供你的清晰、简洁的回答。"

            # 构建最终提示，强制要求显示思考过程（中文）
            final_prompt = f"""请逐步展示你的思考过程，然后给出最终回答。

"""
            if req.context:
                final_prompt += f"上下文: {req.context}\n\n"
            if uploaded_data_context:
                final_prompt += f"可用数据: {uploaded_data_context}\n\n"
            if database_context:
                final_prompt += f"{database_context}\n\n"
            final_prompt += f"用户问题: {user_message}\n\n"""

            final_prompt += """重要格式要求：
你必须按照以下结构回答：

[深度思考]
[在此处逐步展示你的推理过程 - 分析问题、考虑可用信息、规划回答策略]

[回答]
[在此处给出你的清晰回答]

思考过程应该详细，展示你的真实推理逻辑。请用中文进行思考。"""

            # 流式调用，使用延迟发送策略检测分隔符
            in_thinking = False
            thinking_buffer = ""
            response_buffer = ""

            # 分隔符模式（中文）
            thinking_start_pattern = "[深度思考]"
            answer_start_pattern = "[回答]"

            # 延迟缓冲区 - 保存可能包含分隔符的内容
            # 缓冲区大小设置为50，确保能容纳分隔符（最长约21字符）
            pending_buffer = ""
            BUFFER_SIZE = 50

            def send_content(content: str, is_thinking: bool):
                """发送内容的辅助函数"""
                if not content:
                    return
                escaped = content.replace('\n', '\\n').replace('"', '\\"')
                event_type = "thinking" if is_thinking else "response"
                return f"event: {event_type}\ndata: {{\"content\": \"{escaped}\"}}\n\n"

            for chunk in llm.stream_chat(cot_system_prompt, final_prompt, history=llm_history):
                if not chunk:
                    continue

                # 将chunk添加到待处理缓冲区
                pending_buffer += chunk

                # 在非思考状态下检测思考开始标记
                if not in_thinking and thinking_start_pattern in pending_buffer:
                    # 发送标记之前的内容（如果有）
                    parts = pending_buffer.split(thinking_start_pattern, 1)
                    if parts[0].strip():
                        yield send_content(parts[0], False)
                    # 标记思考开始
                    yield f"event: thinking_start\ndata: {{}}\n\n"
                    in_thinking = True
                    # 保留标记之后的内容
                    pending_buffer = parts[1] if len(parts) > 1 else ""
                    continue

                # 在思考状态下检测答案开始标记
                if in_thinking and answer_start_pattern in pending_buffer:
                    # 发送答案标记之前的思考内容
                    parts = pending_buffer.split(answer_start_pattern, 1)
                    if parts[0].strip():
                        yield send_content(parts[0], True)
                    # 标记思考完成
                    yield f"event: thinking_done\ndata: {{}}\n\n"
                    in_thinking = False
                    # 保留标记之后的内容
                    pending_buffer = parts[1] if len(parts) > 1 else ""
                    continue

                # 如果缓冲区太长，且没有检测到分隔符，则发送内容
                # 保留最后BUFFER_SIZE个字符用于跨chunk检测
                if len(pending_buffer) > BUFFER_SIZE:
                    send_now = pending_buffer[:-BUFFER_SIZE]
                    pending_buffer = pending_buffer[-BUFFER_SIZE:]

                    if send_now:
                        thinking_buffer += send_now
                        response_buffer += send_now
                        yield send_content(send_now, in_thinking)
                        await asyncio.sleep(0.01)

            # 发送剩余的待处理内容
            if pending_buffer.strip():
                pending_escaped = pending_buffer.replace('\n', '\\n').replace('"', '\\"')
                event_type = "thinking" if in_thinking else "response"
                yield f"event: {event_type}\ndata: {{\"content\": \"{pending_escaped}\"}}\n\n"

            # 如果仍在思考中，发送思考完成事件
            if in_thinking:
                yield f"event: thinking_done\ndata: {{}}\n\n"

            # 保存完整对话到历史
            if session_id and not session_id.startswith('temp_'):
                full_response = thinking_buffer + response_buffer
                assistant_msg_entry = {
                    "role": "assistant",
                    "content": full_response,
                    "timestamp": datetime.now().isoformat()
                }
                if current_history is not None:
                    current_history.append(assistant_msg_entry)
                    save_history()

            yield f"event: done\ndata: {{}}\n\n"

        except Exception as e:
            error_msg = str(e).replace('"', '\\"')
            yield f"event: error\ndata: {{\"message\": \"{error_msg}\"}}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

@app.post("/upload/excel", response_model=FileAnalysisResponse)
async def upload_excel(file: UploadFile = File(...)):
    """上传 Excel/CSV 文件（仅加载，不分析）"""
    try:
        # 检查文件类型
        is_csv = file.filename.endswith('.csv')
        is_excel = file.filename.endswith('.xlsx') or file.filename.endswith('.xls')
        
        if not (is_csv or is_excel):
            raise HTTPException(status_code=400, detail="只支持 Excel (.xlsx, .xls) 或 CSV (.csv) 文件")
        
        # 读取文件
        contents = await file.read()
        
        if is_csv:
            # 尝试不同的编码
            try:
                df = pd.read_csv(io.BytesIO(contents), encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(io.BytesIO(contents), encoding='gbk')
                except UnicodeDecodeError:
                    df = pd.read_csv(io.BytesIO(contents), encoding='latin1')
        else:
            df = pd.read_excel(io.BytesIO(contents))
        
        # 基本信息
        rows, cols = df.shape
        column_names = df.columns.tolist()
        
        # 数据预览（前5行）
        preview = df.head(5).to_dict(orient='records')
        
        # 列信息（数据类型、非空数量等）
        column_info = {}
        for col in df.columns:
            column_info[col] = {
                'dtype': str(df[col].dtype),
                'non_null_count': int(df[col].count()),
                'null_count': int(df[col].isnull().sum()),
                'unique_count': int(df[col].nunique())
            }
            
            # 如果是数值型，添加统计信息
            if pd.api.types.is_numeric_dtype(df[col]):
                column_info[col]['mean'] = float(df[col].mean()) if not df[col].isnull().all() else None
                column_info[col]['min'] = float(df[col].min()) if not df[col].isnull().all() else None
                column_info[col]['max'] = float(df[col].max()) if not df[col].isnull().all() else None
        
        # 存储数据信息（用于后续分析）
        uploaded_data_store[file.filename] = {
            'dataframe': df,
            'rows': rows,
            'columns': cols,
            'column_names': column_names
        }
        
        # 只返回基本信息，不进行 AI 分析
        summary = f"文件已成功加载！\n\n数据规模: {rows} 行 × {cols} 列\n列名: {', '.join(column_names[:5])}{'...' if len(column_names) > 5 else ''}"
        
        return FileAnalysisResponse(
            summary=summary,
            data_preview={'rows': preview[:5]},
            column_info=column_info
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件处理失败: {str(e)}")

@app.get("/upload/files")
def list_uploaded_files():
    """获取已上传文件列表"""
    return {
        "files": [
            {
                "filename": filename,
                "rows": info['rows'],
                "columns": info['columns'],
                "column_names": info['column_names']
            }
            for filename, info in uploaded_data_store.items()
        ]
    }

@app.delete("/upload/file/{filename}")
def delete_uploaded_file(filename: str):
    """删除已上传的文件"""
    if filename in uploaded_data_store:
        del uploaded_data_store[filename]
        return {"message": f"文件 {filename} 已删除"}
    else:
        raise HTTPException(status_code=404, detail="文件不存在")



# ==================== 数据导入接口 ====================

class ColumnMapping(BaseModel):
    """列名映射"""
    external_id: Optional[str] = None
    title_zh: Optional[str] = None
    resource_url: Optional[str] = None
    created_at: Optional[str] = None


class ImportRequest(BaseModel):
    """导入请求"""
    batch_name: Optional[str] = None
    column_mapping: Optional[Dict[str, str]] = None
    skip_duplicates: bool = True
    update_existing: bool = False


class ImportResponse(BaseModel):
    """导入响应"""
    batch_id: str
    total_records: int
    success_count: int
    failed_count: int
    skipped_count: int
    status: str
    errors: List[str] = []


@app.post("/import/data", response_model=ImportResponse)
async def import_data(
    file: UploadFile = File(...),
    skip_duplicates: bool = Form(True),
    update_existing: bool = Form(False),
    batch_name: Optional[str] = Form(None),
    column_mapping: Optional[str] = Form(None)
):
    """
    导入Excel/CSV数据到数据库

    支持自动检测列名，也可手动指定列映射：
    - external_id: 外部ID（用于去重）
    - title_zh: 商品名称
    - resource_url: 资源链接
    - created_at: 创建时间

    返回导入结果统计
    """
    import tempfile
    import os
    import json
    from services.import_service import DataImportService

    try:
        # 检查文件类型
        is_csv = file.filename.endswith('.csv')
        is_excel = file.filename.endswith('.xlsx') or file.filename.endswith('.xls')

        if not (is_csv or is_excel):
            raise HTTPException(status_code=400, detail="只支持 Excel (.xlsx, .xls) 或 CSV (.csv) 文件")

        # 保存到临时文件
        suffix = '.csv' if is_csv else '.xlsx'
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        try:
            # 解析列映射
            mapping = None
            if column_mapping:
                try:
                    mapping = json.loads(column_mapping)
                except:
                    pass

            # 执行导入
            service = DataImportService()
            if is_excel:
                result = service.import_from_excel(
                    file_path=tmp_path,
                    column_mapping=mapping,
                    batch_name=batch_name,
                    skip_duplicates=skip_duplicates,
                    update_existing=update_existing
                )
            else:
                result = service.import_from_csv(
                    file_path=tmp_path,
                    column_mapping=mapping,
                    batch_name=batch_name,
                    skip_duplicates=skip_duplicates,
                    update_existing=update_existing
                )

            return ImportResponse(**result)

        finally:
            # 删除临时文件
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@app.get("/import/batches", response_model=List[Dict])
async def list_import_batches(limit: int = 50):
    """获取导入批次列表"""
    from database.db_manager import get_db_context
    from database.crud import ImportBatchCRUD

    try:
        with get_db_context() as session:
            crud = ImportBatchCRUD(session)
            batches = crud.list_batches(limit=limit)
            return [batch.to_dict() for batch in batches]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/import/batch/{batch_id}", response_model=Dict)
async def get_import_batch(batch_id: str):
    """获取导入批次详情"""
    from database.db_manager import get_db_context
    from database.crud import ImportBatchCRUD

    try:
        with get_db_context() as session:
            crud = ImportBatchCRUD(session)
            batch = crud.get_batch(batch_id)
            if not batch:
                raise HTTPException(status_code=404, detail="批次不存在")
            return batch.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 课程/商品查询接口 ====================

class CourseSearchRequest(BaseModel):
    """课程搜索请求"""
    keyword: Optional[str] = None
    resource_type: Optional[str] = None
    limit: int = 20
    offset: int = 0


class CourseItem(BaseModel):
    """课程项"""
    product_id: str
    title_zh: Optional[str] = None
    resource_url: Optional[str] = None
    resource_type: Optional[str] = None
    external_id: Optional[str] = None
    created_at: Optional[str] = None


@app.post("/courses/search", response_model=List[CourseItem])
async def search_courses(req: CourseSearchRequest):
    """搜索课程"""
    from database.db_manager import get_db_context
    from database.models import ProductDB

    try:
        with get_db_context() as session:
            query = session.query(ProductDB).filter(
                ProductDB.external_id.isnot(None)
            )

            # 关键词搜索
            if req.keyword:
                query = query.filter(ProductDB.title_zh.contains(req.keyword))

            # 资源类型筛选
            if req.resource_type:
                query = query.filter(ProductDB.resource_type == req.resource_type)

            # 分页
            courses = query.order_by(ProductDB.created_at.desc()).offset(req.offset).limit(req.limit).all()

            return [
                CourseItem(
                    product_id=c.product_id,
                    title_zh=c.title_zh,
                    resource_url=c.resource_url,
                    resource_type=c.resource_type,
                    external_id=c.external_id,
                    created_at=c.created_at.isoformat() if c.created_at else None
                )
                for c in courses
            ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/courses/stats")
async def get_courses_stats():
    """获取课程统计信息"""
    from database.db_manager import get_db_context
    from database.models import ProductDB

    try:
        with get_db_context() as session:
            total = session.query(ProductDB).filter(
                ProductDB.external_id.isnot(None)
            ).count()

            # 按类型统计
            from sqlalchemy import func
            type_stats = session.query(
                ProductDB.resource_type,
                func.count(ProductDB.product_id)
            ).filter(
                ProductDB.external_id.isnot(None)
            ).group_by(ProductDB.resource_type).all()

            return {
                "total": total,
                "by_type": {t or "unknown": c for t, c in type_stats}
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/courses/{course_id}")
async def get_course(course_id: str):
    """获取单个课程详情"""
    from database.db_manager import get_db_context
    from database.models import ProductDB, RawProductDataDB
    from database.crud import RawProductDataCRUD
    import json

    try:
        with get_db_context() as session:
            course = session.query(ProductDB).filter(
                ProductDB.product_id == course_id
            ).first()

            if not course:
                raise HTTPException(status_code=404, detail="课程不存在")

            # 获取原始数据
            raw_data = None
            if course.external_id:
                raw_data_crud = RawProductDataCRUD(session)
                raw_record = raw_data_crud.get_raw_data_by_external_id(course.external_id)
                if raw_record:
                    try:
                        raw_data = json.loads(raw_record.raw_data)
                    except:
                        raw_data = raw_record.raw_data

            return {
                "standard": {
                    "product_id": course.product_id,
                    "title_zh": course.title_zh,
                    "resource_url": course.resource_url,
                    "resource_type": course.resource_type,
                    "external_id": course.external_id,
                    "description": course.description,
                    "created_at": course.created_at.isoformat() if course.created_at else None,
                    "updated_at": course.updated_at.isoformat() if course.updated_at else None,
                },
                "raw_data": raw_data
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 产品RAG管理接口 ====================

class RAGRebuildRequest(BaseModel):
    """RAG重建请求"""
    source: Optional[str] = None  # 指定数据源，None表示全部重建


@app.get("/rag/product/status")
def get_product_rag_status():
    """获取产品RAG系统状态"""
    from rag.product_rag import get_product_rag
    from rag.rag_config import DATA_SOURCE_CONFIGS

    try:
        rag = get_product_rag()

        status = {
            "enabled": True,
            "sources": []
        }

        for source_name, config in DATA_SOURCE_CONFIGS.items():
            collection = rag.vector_stores.get(source_name)
            status["sources"].append({
                "name": source_name,
                "collection_name": config.get("collection_name"),
                "indexed_count": collection.count() if collection else 0,
                "keywords": config.get("keywords", []),
            })

        return status

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rag/product/rebuild")
def rebuild_product_rag(req: RAGRebuildRequest):
    """
    重建产品RAG索引

    当数据库数据更新后，需要调用此接口重建向量索引
    """
    from rag.product_rag import get_product_rag

    try:
        rag = get_product_rag()

        if req.source:
            # 重建指定数据源
            if req.source in rag.vector_stores:
                collection = rag.vector_stores[req.source]
                rag._chroma_client.delete_collection(
                    name=rag.rag_config.DATA_SOURCE_CONFIGS[req.source]["collection_name"]
                )
                # 重新创建
                collection_name = rag.rag_config.DATA_SOURCE_CONFIGS[req.source]["collection_name"]
                collection = rag._chroma_client.get_or_create_collection(name=collection_name)
                rag.vector_stores[req.source] = collection
                rag._build_index(req.source)
                return {"message": f"数据源 {req.source} 索引重建成功"}
            else:
                raise HTTPException(status_code=404, detail=f"数据源 {req.source} 不存在")
        else:
            # 重建所有数据源
            rag.rebuild_all_indexes()
            return {"message": "所有数据源索引重建成功"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rag/product/search")
def product_rag_search(query: str, source: Optional[str] = None, top_k: int = 10):
    """
    直接测试产品RAG检索

    用于调试和测试检索效果
    """
    from rag.product_rag import get_product_rag

    try:
        rag = get_product_rag()
        result = rag.search(query=query, source_name=source, top_k=top_k)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

