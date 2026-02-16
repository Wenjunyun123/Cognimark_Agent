import { useState, useEffect, useRef } from 'react';
import { 
  X, 
  Settings, 
  Monitor, 
  Link as LinkIcon, 
  MessageSquare, 
  User, 
  Info, 
  Sun, 
  Moon, 
  MonitorSmartphone,
  Upload,
  Download,
  Archive,
  Trash2,
  ChevronRight,
  LogOut
} from 'lucide-react';
import { cn } from '../../utils/cn';
import { useAuth } from '../../contexts/AuthContext';
import { SessionManager } from '../../utils/sessionManager';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialTab?: string;
}

type TabId = 'general' | 'interface' | 'connections' | 'chat' | 'account' | 'about';

const TABS: { id: TabId; label: string; icon: any }[] = [
  { id: 'general', label: '通用', icon: Settings },
  { id: 'interface', label: '界面', icon: Monitor },
  { id: 'connections', label: '外部连接', icon: LinkIcon },
  { id: 'chat', label: '对话', icon: MessageSquare },
  { id: 'account', label: '账号', icon: User },
  { id: 'about', label: '介绍', icon: Info },
];

export default function SettingsModal({ isOpen, onClose, initialTab = 'general' }: SettingsModalProps) {
  const [activeTab, setActiveTab] = useState<TabId>(initialTab as TabId);
  const [theme, setTheme] = useState<'light' | 'dark' | 'system'>('system');
  const [improveModel, setImproveModel] = useState(false);
  const { user, logout } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setActiveTab(initialTab as TabId);
      // Initialize theme state from localStorage
      const storedTheme = localStorage.getItem('theme');
      if (storedTheme) {
        setTheme(storedTheme as 'light' | 'dark');
      } else {
        setTheme('system');
      }
    }
  }, [isOpen, initialTab]);

  const handleThemeChange = (newTheme: 'light' | 'dark' | 'system') => {
    setTheme(newTheme);
    if (newTheme === 'system') {
      localStorage.removeItem('theme');
      if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    } else {
      localStorage.setItem('theme', newTheme);
      if (newTheme === 'dark') {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    }
  };

  const handleExportChat = () => {
    const sessions = SessionManager.getAllSessions();
    const blob = new Blob([JSON.stringify(sessions, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `cognimark_chat_history_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleImportChat = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const content = e.target?.result as string;
        const sessions = JSON.parse(content);
        
        if (Array.isArray(sessions)) {
          // Merge logic: Add sessions that don't exist
          const currentSessions = SessionManager.getAllSessions();
          const currentIds = new Set(currentSessions.map(s => s.id));
          
          let addedCount = 0;
          sessions.forEach(session => {
            if (session.id && session.messages && !currentIds.has(session.id)) {
              SessionManager.saveSession(session);
              addedCount++;
            }
          });
          
          alert(`成功导入 ${addedCount} 个会话`);
          // Trigger storage event to update Sidebar
          window.dispatchEvent(new Event('storage'));
        } else {
          alert('无效的文件格式');
        }
      } catch (error) {
        console.error('Import failed:', error);
        alert('导入失败：文件格式错误');
      }
    };
    reader.readAsText(file);
    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleDeleteAllChats = () => {
    if (confirm('确定要删除所有对话记录吗？此操作无法撤销。')) {
      localStorage.removeItem('cognimark_sessions');
      window.dispatchEvent(new Event('storage'));
      alert('所有对话记录已删除');
    }
  };

  if (!isOpen) return null;

  const renderContent = () => {
    switch (activeTab) {
      case 'general':
        return (
          <div className="space-y-8">
            <section>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">主题</h3>
              <div className="grid grid-cols-3 gap-4">
                <button
                  onClick={() => handleThemeChange('system')}
                  className={cn(
                    "flex flex-col items-center justify-center p-4 rounded-xl border-2 transition-all",
                    theme === 'system'
                      ? "border-green-500 bg-green-50 dark:bg-green-900/20"
                      : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
                  )}
                >
                  <MonitorSmartphone className={cn("w-6 h-6 mb-2", theme === 'system' ? "text-green-600 dark:text-green-400" : "text-gray-500")} />
                  <span className={cn("text-sm", theme === 'system' ? "text-green-700 dark:text-green-300" : "text-gray-600 dark:text-gray-400")}>跟随系统</span>
                </button>
                <button
                  onClick={() => handleThemeChange('light')}
                  className={cn(
                    "flex flex-col items-center justify-center p-4 rounded-xl border-2 transition-all",
                    theme === 'light'
                      ? "border-green-500 bg-green-50 dark:bg-green-900/20"
                      : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
                  )}
                >
                  <Sun className={cn("w-6 h-6 mb-2", theme === 'light' ? "text-green-600 dark:text-green-400" : "text-gray-500")} />
                  <span className={cn("text-sm", theme === 'light' ? "text-green-700 dark:text-green-300" : "text-gray-600 dark:text-gray-400")}>日间模式</span>
                </button>
                <button
                  onClick={() => handleThemeChange('dark')}
                  className={cn(
                    "flex flex-col items-center justify-center p-4 rounded-xl border-2 transition-all",
                    theme === 'dark'
                      ? "border-green-500 bg-green-50 dark:bg-green-900/20"
                      : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
                  )}
                >
                  <Moon className={cn("w-6 h-6 mb-2", theme === 'dark' ? "text-green-600 dark:text-green-400" : "text-gray-500")} />
                  <span className={cn("text-sm", theme === 'dark' ? "text-green-700 dark:text-green-300" : "text-gray-600 dark:text-gray-400")}>夜间模式</span>
                </button>
              </div>
            </section>

            <section>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">语言设置</h3>
              <div className="relative">
                <select 
                  className="w-full appearance-none bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg px-4 py-3 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                  defaultValue="zh-CN"
                >
                  <option value="zh-CN">Chinese (简体中文)</option>
                  <option value="en-US">English (US)</option>
                </select>
                <ChevronRight className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 rotate-90" />
              </div>
            </section>
          </div>
        );

      case 'account':
        return (
          <div className="space-y-8">
            <div className="flex items-center gap-4">
              <div className="w-20 h-20 rounded-full bg-green-600 text-white flex items-center justify-center text-3xl font-bold">
                {user?.avatar || 'U'}
              </div>
              <div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">用户头像</h3>
                <div className="flex gap-4 mt-2">
                  <button className="px-4 py-1.5 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg text-sm hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors">
                    使用首个字符作为头像
                  </button>
                  <button className="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300">
                    移除
                  </button>
                </div>
              </div>
            </div>

            <section>
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">名称</h3>
              <input 
                type="text" 
                defaultValue={user?.name || ''}
                className="w-full bg-gray-50 dark:bg-gray-800 border border-transparent focus:bg-white dark:focus:bg-gray-900 border-gray-200 dark:border-gray-700 rounded-lg px-4 py-2.5 text-gray-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition-all"
              />
            </section>

            <section className="space-y-4 pt-4 border-t border-gray-100 dark:border-gray-800">
              <div className="flex items-center justify-between py-2">
                <span className="text-gray-700 dark:text-gray-300">更改密码</span>
                <button className="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                  显示
                </button>
              </div>
              <div className="flex items-center justify-between py-2">
                <span className="text-red-600 dark:text-red-400">退出登录</span>
                <button 
                  onClick={() => {
                    logout();
                    onClose();
                  }}
                  className="px-4 py-2 bg-red-50 dark:bg-red-900/20 border border-transparent rounded-lg text-sm text-red-600 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/40 transition-colors flex items-center gap-2"
                >
                  <LogOut className="w-4 h-4" />
                  <span>退出</span>
                </button>
              </div>
            </section>
          </div>
        );

      case 'chat':
        return (
          <div className="space-y-6">
            <section className="p-4 bg-red-50 dark:bg-red-900/10 border border-red-100 dark:border-red-900/20 rounded-xl">
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">改进模型</h3>
                <div 
                  className={cn(
                    "w-11 h-6 rounded-full p-1 cursor-pointer transition-colors duration-200 ease-in-out",
                    improveModel ? "bg-green-500" : "bg-gray-200 dark:bg-gray-700"
                  )}
                  onClick={() => setImproveModel(!improveModel)}
                >
                  <div 
                    className={cn(
                      "bg-white w-4 h-4 rounded-full shadow-sm transform transition-transform duration-200 ease-in-out",
                      improveModel ? "translate-x-5" : "translate-x-0"
                    )}
                  />
                </div>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                通过分享您的数据用于训练我们的模型，您可以帮助提升自身的体验，并改进所有用户的模型质量。我们已采取措施确保您的隐私在整个过程中得到保护。
              </p>
            </section>

            <section className="space-y-2">
              <input 
                type="file" 
                ref={fileInputRef}
                className="hidden" 
                accept=".json"
                onChange={handleImportChat}
              />
              <button 
                onClick={() => fileInputRef.current?.click()}
                className="w-full flex items-center gap-3 px-4 py-3 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-lg transition-colors text-left"
              >
                <Upload className="w-5 h-5 text-gray-500" />
                <span>导入对话记录</span>
              </button>
              <button 
                onClick={handleExportChat}
                className="w-full flex items-center gap-3 px-4 py-3 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-lg transition-colors text-left"
              >
                <Download className="w-5 h-5 text-gray-500" />
                <span>导出对话</span>
              </button>
            </section>

            <section className="pt-4 border-t border-gray-100 dark:border-gray-800 space-y-2">
              <button className="w-full flex items-center gap-3 px-4 py-3 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-lg transition-colors text-left">
                <Archive className="w-5 h-5 text-gray-500" />
                <span>归档所有对话记录</span>
              </button>
              <button 
                onClick={handleDeleteAllChats}
                className="w-full flex items-center gap-3 px-4 py-3 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors text-left"
              >
                <Trash2 className="w-5 h-5 text-red-500" />
                <span>删除所有对话记录</span>
              </button>
            </section>
          </div>
        );

      case 'about':
        return (
          <div className="space-y-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-gray-900 text-white rounded-lg flex items-center justify-center text-xl font-bold">C</div>
              <span className="text-2xl font-bold text-gray-900 dark:text-white">CogniMark</span>
            </div>

            <section className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">介绍</h3>
              <p className="text-gray-600 dark:text-gray-400 text-sm leading-relaxed">
                CogniMark 是一家专注于跨境营销的智能助手平台，致力于"让出海营销更简单"。依托先进的大语言模型（LLM）技术，CogniMark 为跨境电商卖家提供智能选品、多语言营销文案生成、市场趋势分析等核心功能。我们深度集成了 DeepSeek、OpenAI 等顶尖模型，通过精准的数据洞察和创意生成，帮助企业突破语言与文化壁垒，实现全球化业务增长。
              </p>
            </section>

            <section className="space-y-2">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">反馈渠道</h3>
              <a href="mailto:support@cognimark.ai" className="text-green-600 dark:text-green-400 hover:underline">
                support@cognimark.ai
              </a>
            </section>
          </div>
        );

      default:
        return (
          <div className="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
            此功能开发中...
          </div>
        );
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-fadeIn">
      <div className="bg-white dark:bg-gray-900 rounded-2xl w-full max-w-4xl h-[600px] flex shadow-2xl overflow-hidden animate-scaleIn">
        {/* Sidebar */}
        <div className="w-64 bg-gray-50 dark:bg-gray-900/50 border-r border-gray-100 dark:border-gray-800 p-4 flex flex-col">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white px-4 mb-6">系统设置</h2>
          <nav className="space-y-1 flex-1">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  "w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors",
                  activeTab === tab.id
                    ? "bg-gray-200 dark:bg-gray-800 text-gray-900 dark:text-white"
                    : "text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800/50 hover:text-gray-900 dark:hover:text-white"
                )}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1 flex flex-col min-w-0">
          <div className="flex justify-end p-4">
            <button 
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <div className="flex-1 overflow-y-auto px-8 pb-8 custom-scrollbar">
            <div className="max-w-2xl">
              {renderContent()}
            </div>
          </div>

          {/* Footer for Account tab (Save button) */}
          {activeTab === 'account' && (
             <div className="p-4 border-t border-gray-100 dark:border-gray-800 flex justify-end">
               <button 
                 onClick={onClose}
                 className="px-6 py-2 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-lg font-medium hover:opacity-90 transition-opacity"
               >
                 保存
               </button>
             </div>
          )}
        </div>
      </div>
    </div>
  );
}
