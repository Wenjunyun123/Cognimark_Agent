import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import io
import json
import os
import uuid
from typing import List, Optional, Dict
from datetime import datetime

from llm_service import DeepSeekLLM
from data_model import default_store, Product
from agents import ProductSelectionAgent, MarketingCopyAgent

# 初始化 FastAPI
app = FastAPI(title="AI Agent E-Commerce API", version="1.0")

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
            # 只有非临时会话（不以 'temp_' 开头）才保存到文件
            is_temp_session = session_id.startswith('temp_')
            
            if not is_temp_session and session_id not in CHAT_SESSIONS:
                CHAT_SESSIONS[session_id] = []
                current_history = CHAT_SESSIONS[session_id]
            elif not is_temp_session:
                current_history = CHAT_SESSIONS[session_id]
            else:
                # 临时会话使用内存中的临时存储，不持久化
                # 这里我们简单处理：临时会话也用 current_history 暂存，但不写入文件
                # 或者，如果前端每次都发完整 history，这里甚至可以不需要 current_history
                pass
        
        # 2. 如果有 session_id 且非临时，保存用户消息到后端历史
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
        
        # 检查是否使用特定模式
        system_prompt = "You are CogniMark, a helpful AI assistant specialized in cross-border e-commerce, product selection, and marketing. You provide professional, actionable advice. Maintain conversation context and refer to previous messages when relevant."
        user_message = req.message
        
        for mode_key, mode_system in mode_prompts.items():
            if user_message.startswith(mode_key):
                system_prompt = mode_system + " Maintain conversation context and refer to previous messages when relevant."
                user_message = user_message.replace(mode_key, '').strip()
                break
        
        # 检查是否有上传的数据
        uploaded_data_context = ""
        if uploaded_data_store:
            uploaded_data_context = "\n\n已上传的外部数据摘要:\n"
            for filename, data_info in uploaded_data_store.items():
                uploaded_data_context += f"- {filename}: {data_info['rows']} 行, {data_info['columns']} 列\n"
                uploaded_data_context += f"  列名: {', '.join(data_info['column_names'])}\n"
                
                # 如果有数据，提供更详细的上下文
                df = data_info.get('dataframe')
                if df is not None:
                    uploaded_data_context += f"  数据预览（前3行）:\n{df.head(3).to_string()}\n"
        
        # 构建最终的用户提示
        final_prompt = ""
        if req.context:
            final_prompt += f"Context: {req.context}\n"
        if uploaded_data_context:
            final_prompt += uploaded_data_context
        final_prompt += f"\nUser question: {user_message}"
        
        # 3. 准备 LLM 历史上下文
        llm_history = []
        
        if session_id and not session_id.startswith('temp_'):
            # 使用后端存储的历史（排除刚刚加入的当前消息）
            # 注意：current_history 可能是引用，修改它会影响全局
            if current_history:
                for msg in current_history[:-1]:
                    llm_history.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
        elif req.history:
            # 如果没有 session_id 或为临时会话，使用前端传来的 history
            for msg in req.history:
                llm_history.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        response_text = llm.chat(system_prompt, final_prompt, history=llm_history)
        
        # 4. 如果有 session_id 且非临时，保存助手回复到后端历史
        if session_id and not session_id.startswith('temp_'):
            assistant_msg_entry = {
                "role": "assistant",
                "content": response_text,
                "timestamp": datetime.now().isoformat()
            }
            if current_history is not None:
                current_history.append(assistant_msg_entry)
                save_history()
        
        return ChatResponse(response=response_text, message_id=str(uuid.uuid4()))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        summary = f"文件已成功加载！\n\n📊 数据规模: {rows} 行 × {cols} 列\n📋 列名: {', '.join(column_names[:5])}{'...' if len(column_names) > 5 else ''}"
        
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

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

