// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export interface Product {
  product_id: string;
  title_en: string;
  category: string;
  price_usd: number;
  avg_rating: number;
  monthly_sales: number;
  main_market: string;
  tags: string;
}

export interface SelectionRequest {
  campaign_description: string;
  target_market?: string;
  top_k: number;
}

export interface SelectionResponse {
  products: Product[];
  explanation: string;
}

export interface CopyRequest {
  product_id: string;
  target_language: string;
  channel: string;
}

export interface CopyResponse {
  copy_text: string;
}

export interface ChatMessage {
  role: string;
  content: string;
}

export interface ChatRequest {
  message: string;
  context?: string;
  history?: ChatMessage[];
  session_id?: string;
}

export interface ChatResponse {
  response: string;
}

export interface FileAnalysisResponse {
  summary: string;
  data_preview: {
    rows: any[];
  };
  column_info: Record<string, any>;
}

export interface UploadedFile {
  filename: string;
  rows: number;
  columns: number;
  column_names: string[];
}

/**
 * 获取所有产品列表
 */
export async function getProducts(): Promise<{ product_id: string; title_en: string }[]> {
  const response = await fetch(`${API_BASE_URL}/products`);
  if (!response.ok) {
    throw new Error('Failed to fetch products');
  }
  return response.json();
}

/**
 * 智能选品推荐
 */
export async function recommendProducts(request: SelectionRequest): Promise<SelectionResponse> {
  const response = await fetch(`${API_BASE_URL}/selection/recommend`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error('Failed to get recommendations');
  }

  return response.json();
}

/**
 * 生成营销文案
 */
export async function generateMarketingCopy(request: CopyRequest): Promise<CopyResponse> {
  const response = await fetch(`${API_BASE_URL}/marketing/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error('Failed to generate marketing copy');
  }

  return response.json();
}

/**
 * 通用智能体对话
 */
export async function chatWithAgent(request: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/agent/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error('Failed to chat with agent');
  }

  return response.json();
}

/**
 * 获取聊天历史
 */
export async function getChatHistory(sessionId?: string): Promise<ChatMessage[]> {
  const url = sessionId 
    ? `${API_BASE_URL}/agent/history?session_id=${sessionId}`
    : `${API_BASE_URL}/agent/history`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error('Failed to fetch chat history');
  }
  return response.json();
}

/**
 * 流式聊天接口 - 返回thinking和回复
 */
export async function chatWithAgentStream(
  request: ChatRequest,
  onThinking: (content: string) => void,
  onResponse: (content: string) => void,
  onThinkingStart: () => void,
  onThinkingEnd: () => void,
  onComplete: () => void,
  onError: (error: string) => void
): Promise<() => void> {
  const controller = new AbortController();

  fetch(`${API_BASE_URL}/agent/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
    signal: controller.signal,
  }).then(async (response) => {
    if (!response.ok) {
      throw new Error('Failed to chat with agent');
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body');
    }

    const decoder = new TextDecoder();
    let buffer = '';
    let inThinking = false;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('event:')) {
          const event = line.slice(6).trim();

          if (event === 'thinking_start') {
            inThinking = true;
            onThinkingStart();
          } else if (event === 'thinking_done') {
            inThinking = false;
            onThinkingEnd();
          } else if (event === 'done') {
            onComplete();
          } else if (event === 'error') {
            onError('Stream error occurred');
          }
        } else if (line.startsWith('data:')) {
          const data = line.slice(5).trim();
          if (data) {
            try {
              const parsed = JSON.parse(data);
              if (parsed.content) {
                if (inThinking) {
                  onThinking(parsed.content);
                } else {
                  onResponse(parsed.content);
                }
              }
            } catch (e) {
              // Ignore parse errors for non-JSON data
            }
          }
        }
      }
    }
  }).catch((error) => {
    if (error.name !== 'AbortError') {
      onError(error.message);
    }
  });

  return () => controller.abort();
}


/**
 * 上传 Excel 文件
 */
export async function uploadExcel(file: File): Promise<FileAnalysisResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/upload/excel`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to upload file');
  }

  return response.json();
}

/**
 * 获取已上传文件列表
 */
export async function getUploadedFiles(): Promise<{ files: UploadedFile[] }> {
  const response = await fetch(`${API_BASE_URL}/upload/files`);
  
  if (!response.ok) {
    throw new Error('Failed to get uploaded files');
  }

  return response.json();
}

/**
 * 删除已上传文件
 */
export async function deleteUploadedFile(filename: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/upload/file/${encodeURIComponent(filename)}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    throw new Error('Failed to delete file');
  }
}
