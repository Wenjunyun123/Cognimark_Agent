// 会话管理工具
export interface ChatSession {
  id: string;
  title: string;
  messages: Array<{
    id: string;
    role: 'user' | 'assistant';
    content: string;
    thinking?: string; // 添加thinking字段
  }>;
  createdAt: number;
  updatedAt: number;
  isTemporary?: boolean;
}

const STORAGE_KEY = 'cognimark_sessions';
const CURRENT_SESSION_KEY = 'cognimark_current_session';

export class SessionManager {
  // 获取所有会话（按时间倒序）
  static getAllSessions(): ChatSession[] {
    const data = localStorage.getItem(STORAGE_KEY);
    if (!data) return [];
    try {
      const sessions = JSON.parse(data);
      // 过滤掉临时会话，并按更新时间倒序排列
      return sessions
        .filter((s: ChatSession) => !s.isTemporary)
        .sort((a: ChatSession, b: ChatSession) => b.updatedAt - a.updatedAt);
    } catch {
      return [];
    }
  }

  // 获取单个会话
  static getSession(id: string): ChatSession | null {
    const sessions = this.getAllSessions();
    return sessions.find(s => s.id === id) || null;
  }

  // 保存会话
  static saveSession(session: ChatSession): void {
    if (session.isTemporary) return; // 临时会话不保存
    
    const sessions = this.getAllSessions();
    const index = sessions.findIndex(s => s.id === session.id);
    
    if (index >= 0) {
      sessions[index] = session;
    } else {
      sessions.unshift(session);
    }
    
    // 最多保存 50 个会话
    if (sessions.length > 50) {
      sessions.splice(50);
    }
    
    localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
  }

  // 删除会话
  static deleteSession(id: string): void {
    const sessions = this.getAllSessions();
    const filtered = sessions.filter(s => s.id !== id);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
  }

  // 创建新会话
  static createSession(title: string = '新对话', isTemporary: boolean = false): ChatSession {
    const id = isTemporary 
      ? `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      : `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
    return {
      id,
      title,
      messages: [],
      createdAt: Date.now(),
      updatedAt: Date.now(),
      isTemporary,
    };
  }

  // 更新会话标题（根据第一条消息或手动修改）
  static updateSessionTitle(session: ChatSession, newTitle?: string): ChatSession {
    if (newTitle) {
      session.title = newTitle;
    } else if (session.messages.length > 0 && (session.title === '新对话' || session.title.startsWith('New Chat'))) {
      const firstUserMsg = session.messages.find(m => m.role === 'user');
      if (firstUserMsg) {
        // 截取前 20 个字符作为标题
        session.title = firstUserMsg.content.slice(0, 20).trim() || '新对话';
      }
    }
    return session;
  }

  // 获取或创建当前会话
  static getCurrentSession(): ChatSession | null {
    const currentId = localStorage.getItem(CURRENT_SESSION_KEY);
    if (currentId) {
      return this.getSession(currentId);
    }
    return null;
  }

  // 设置当前会话
  static setCurrentSession(id: string): void {
    localStorage.setItem(CURRENT_SESSION_KEY, id);
  }

  // 清除当前会话
  static clearCurrentSession(): void {
    localStorage.removeItem(CURRENT_SESSION_KEY);
  }
}


