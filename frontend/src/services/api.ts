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
export async function getChatHistory(): Promise<ChatMessage[]> {
  const response = await fetch(`${API_BASE_URL}/agent/history`);
  if (!response.ok) {
    throw new Error('Failed to fetch chat history');
  }
  return response.json();
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
