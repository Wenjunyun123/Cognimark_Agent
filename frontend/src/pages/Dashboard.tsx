import { useState, useRef, useEffect, useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Send, Copy, ThumbsUp, Loader2, Sparkles, TrendingUp, Package, BarChart3, Upload, X, FileSpreadsheet, ArrowDown, ChevronDown } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { chatWithAgentStream, getProducts, uploadExcel, getUploadedFiles, deleteUploadedFile, getChatHistory, UploadedFile } from '../services/api';
import { SessionManager, ChatSession } from '../utils/sessionManager';
import { cn } from '../utils/cn';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  thinking?: string;
  isLoading?: boolean;
  isThinking?: boolean;
  thinkingCollapsed?: boolean;
  thinkingStartTime?: number;
  thinkingEndTime?: number;
}

export default function Dashboard() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [greeting, setGreeting] = useState('');
  const [products, setProducts] = useState<Array<{ product_id: string; title_en: string }>>([]);
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [currentUploadingFile, setCurrentUploadingFile] = useState<{name: string; size: number} | null>(null);
  const [selectedMode, setSelectedMode] = useState<string>('normal'); // normal, market, selection, ads, conversion
  const [showModeMenu, setShowModeMenu] = useState(false);
  const [abortController, setAbortController] = useState<AbortController | null>(null);
  const [regeneratingId, setRegeneratingId] = useState<string | null>(null);
  const [autoScroll, setAutoScroll] = useState(true); // 控制自动滚动
  const [showSlashMenu, setShowSlashMenu] = useState(false);
  const [slashCommandIndex, setSlashCommandIndex] = useState(0);
  const modeMenuRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null); // 新增：消息末尾引用
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const slashMenuRef = useRef<HTMLDivElement>(null);
  const location = useLocation();
  const navigate = useNavigate();

  // 斜杠命令定义
  const SLASH_COMMANDS = [
    { id: 'market', label: '市场趋势分析', icon: TrendingUp, desc: '分析市场动态和竞争格局', color: 'text-blue-500' },
    { id: 'selection', label: '选品策略建议', icon: Package, desc: '基于数据提供选品推荐', color: 'text-green-500' },
    { id: 'ads', label: '广告优化建议', icon: BarChart3, desc: '优化广告投放策略', color: 'text-purple-500' },
    { id: 'conversion', label: '转化率优化', icon: Sparkles, desc: '提升转化率和用户体验', color: 'text-orange-500' },
    { id: 'upload', label: '上传数据文件', icon: FileSpreadsheet, desc: '上传 Excel/CSV 进行分析', color: 'text-green-500' },
  ];

  useEffect(() => {
    const hour = new Date().getHours();
    if (hour >= 11 && hour < 13) setGreeting('中午好');
    else if (hour < 11) setGreeting('上午好');
    else if (hour < 18) setGreeting('下午好');
    else setGreeting('晚上好');

    // CRITICAL FIX: 并行执行异步操作，避免瀑布效应 (async-parallel)
    Promise.all([
      loadProducts(),
      loadUploadedFiles(),
      loadSession()
    ]).catch(err => {
      console.error('Error loading initial data:', err);
    });
  }, [location.search]);

  // 点击外部关闭模式菜单
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (modeMenuRef.current && !modeMenuRef.current.contains(event.target as Node)) {
        setShowModeMenu(false);
      }
      if (slashMenuRef.current && !slashMenuRef.current.contains(event.target as Node)) {
        setShowSlashMenu(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  // 自动调整 textarea 高度
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px';
    }
  }, [inputValue]);

  // 处理斜杠命令选择
  const handleSlashCommand = (commandId: string) => {
    setShowSlashMenu(false);
    if (commandId === 'upload') {
      fileInputRef.current?.click();
    } else {
      setSelectedMode(commandId);
      const command = SLASH_COMMANDS.find(c => c.id === commandId);
      if (command) {
        setInputValue(`[${command.label}] `);
        textareaRef.current?.focus();
      }
    }
  };

  // 处理输入变化，检测斜杠命令
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setInputValue(value);
    
    // 检测是否只输入了 "/" 或在开头输入 "/"
    if (value === '/' || (value.startsWith('/') && !value.includes(' '))) {
      setShowSlashMenu(true);
      setSlashCommandIndex(0);
    } else {
      setShowSlashMenu(false);
    }
  };

  // 处理键盘导航斜杠菜单
  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (showSlashMenu) {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSlashCommandIndex(prev => (prev + 1) % SLASH_COMMANDS.length);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSlashCommandIndex(prev => (prev - 1 + SLASH_COMMANDS.length) % SLASH_COMMANDS.length);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        handleSlashCommand(SLASH_COMMANDS[slashCommandIndex].id);
      } else if (e.key === 'Escape') {
        setShowSlashMenu(false);
      }
    } else if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleGenerate();
    }
  };

  const loadProducts = async () => {
    try {
      const data = await getProducts();
      setProducts(data);
    } catch (error) {
      console.error('Failed to load products:', error);
    }
  };

  const loadUploadedFiles = async () => {
    try {
      const result = await getUploadedFiles();
      setUploadedFiles(result.files);
    } catch (error) {
      console.error('Failed to load uploaded files:', error);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // 显示上传中的文件
    setCurrentUploadingFile({
      name: file.name,
      size: file.size
    });
    setIsUploading(true);

    try {
      const result = await uploadExcel(file);
      
      // 上传成功，保持文件显示在输入框上方
      await loadUploadedFiles();
      setCurrentUploadingFile(null);
      
      // 重置文件输入
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error: any) {
      alert(`上传失败: ${error.message}`);
      setCurrentUploadingFile(null);
    } finally {
      setIsUploading(false);
    }
  };

  const handleRemoveUploadedFile = async (filename: string) => {
    try {
      await deleteUploadedFile(filename);
      await loadUploadedFiles();
    } catch (error: any) {
      console.error('删除文件失败:', error);
    }
  };


  const loadSession = async () => {
    const params = new URLSearchParams(location.search);
    const action = params.get('action');
    const sessionId = params.get('session');

    // 清空服务器端的上传文件（新会话时）
    if (action === 'new' || action === 'temp' || sessionId) {
      await clearUploadedFiles();
    }

    if (action === 'new') {
      // 新建会话（保存到历史）
      const newSession = SessionManager.createSession('新对话', false);
      setCurrentSession(newSession);
      SessionManager.setCurrentSession(newSession.id);
      setMessages([]);
      setSelectedMode('normal'); // 重置为普通模式
      // 清除 URL 参数，避免重复触发
      navigate('/', { replace: true });
    } else if (action === 'temp') {
      // 临时会话（不保存）
      const tempSession = SessionManager.createSession('临时对话', true);
      setCurrentSession(tempSession);
      SessionManager.clearCurrentSession();
      setMessages([]);
      setSelectedMode('normal'); // 重置为普通模式
      // 清除 URL 参数
      navigate('/', { replace: true });
    } else if (sessionId) {
      // 加载指定会话（从后端同步历史）
      const session = SessionManager.getSession(sessionId);
      if (session) {
        // 从后端获取历史记录
        try {
          const backendHistory = await getChatHistory(sessionId);
          if (backendHistory && backendHistory.length > 0) {
            const existingMessages = session.messages || [];
            session.messages = backendHistory.map((msg: any, index: number) => ({
              id: Math.random().toString(36).substr(2, 9),
              role: msg.role,
              content: msg.content,
              thinking: msg.thinking || existingMessages[index]?.thinking
            }));
            SessionManager.saveSession(session);
          }
        } catch (error) {
          console.error('Failed to sync history from backend:', error);
        }
        setCurrentSession(session);
        setMessages(session.messages);
        SessionManager.setCurrentSession(session.id);
        setSelectedMode('normal'); // 重置为普通模式
      }
    } else {
      // 加载最后一次会话或创建新会话
      const lastSession = SessionManager.getCurrentSession();
      if (lastSession) {
        setCurrentSession(lastSession);
        setMessages(lastSession.messages);
      } else {
        const newSession = SessionManager.createSession('新对话', false);
        setCurrentSession(newSession);
        SessionManager.setCurrentSession(newSession.id);
        setMessages([]);
      }
      setSelectedMode('normal'); // 重置为普通模式
    }
  };

  const clearUploadedFiles = async () => {
    try {
      const result = await getUploadedFiles();
      for (const file of result.files) {
        await deleteUploadedFile(file.filename);
      }
      setUploadedFiles([]);
    } catch (error) {
      console.error('Failed to clear uploaded files:', error);
    }
  };

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    if (params.get('new')) {
      setMessages([]);
      setInputValue('');
    }
  }, [location.search]);

  // OPTIMIZATION: 改进的自动滚动逻辑，支持平滑滚动和用户手动控制
  useEffect(() => {
    if (!autoScroll) return;

    const scrollToBottom = () => {
      if (messagesEndRef.current) {
        messagesEndRef.current.scrollIntoView({
          behavior: 'smooth',
          block: 'end'
        });
      }
    };

    // 立即滚动
    scrollToBottom();

    // 如果正在生成，持续滚动以确保跟随
    if (isGenerating) {
      const interval = setInterval(scrollToBottom, 100);
      return () => clearInterval(interval);
    }
  }, [messages, isGenerating, autoScroll]);

  // 手动滚动到底部函数
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: 'smooth',
      block: 'end'
    });
    setAutoScroll(true);
  }, []);

  // 检测用户是否手动滚动，禁用自动滚动
  useEffect(() => {
    const scrollContainer = scrollRef.current;
    if (!scrollContainer) return;

    let isUserScrolling = false;
    let scrollTimeout: NodeJS.Timeout;

    const handleScroll = () => {
      // 检测是否在底部（允许 100px 误差）
      const isNearBottom = scrollContainer.scrollHeight - scrollContainer.scrollTop - scrollContainer.clientHeight < 100;

      if (!isNearBottom && isGenerating) {
        isUserScrolling = true;
        setAutoScroll(false);

        // 3秒后如果没有继续滚动，恢复自动滚动
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => {
          isUserScrolling = false;
          setAutoScroll(true);
        }, 3000);
      }
    };

    scrollContainer.addEventListener('scroll', handleScroll);
    return () => {
      scrollContainer.removeEventListener('scroll', handleScroll);
      clearTimeout(scrollTimeout);
    };
  }, [isGenerating]);

  const handleStopGenerating = () => {
    if (abortController) {
      abortController.abort();
      setAbortController(null);
      setIsGenerating(false);
      
      // 更新最后一条消息为中断状态
      setMessages(prev => prev.map((msg, idx) => 
        idx === prev.length - 1 && msg.isLoading
          ? { ...msg, content: '已中断生成', isLoading: false }
          : msg
      ));
    }
  };

  const handleGenerate = async (text?: string) => {
    let promptText = text || inputValue;
    if (!promptText.trim() || !currentSession) return;

    // 根据选择的模式添加功能前缀
    const modePrefix = {
      normal: '',
      market: '[市场趋势分析模式] ',
      selection: '[选品策略建议模式] ',
      ads: '[广告优化建议模式] ',
      conversion: '[转化率优化模式] '
    }[selectedMode] || '';

    const fullPrompt = modePrefix + promptText;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: promptText
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsGenerating(true);

    const loadingId = (Date.now() + 1).toString();
    setMessages(prev => [...prev, { id: loadingId, role: 'assistant', content: '', thinking: '', isLoading: true, isThinking: false, thinkingCollapsed: false }]);

    try {
      // 只在用户明确提及产品时添加产品上下文
      let context = '';
      const mentionsProduct = /产品|P\d{3}|选品|推荐/.test(promptText);
      if (mentionsProduct && products.length > 0) {
        context = `可用产品列表:\n${products.map(p => `- ${p.product_id}: ${p.title_en}`).join('\n')}`;
      }

      // 准备对话历史（只包含之前的消息，不包括当前正在发送的）
      const history = messages
        .filter(m => !m.isLoading)
        .map(m => ({
          role: m.role,
          content: m.content
        }));

      let thinkingText = '';
      let responseText = '';

      const abortStream = await chatWithAgentStream(
        {
          message: fullPrompt,
          context: context || undefined,
          history: history.length > 0 ? history : undefined,
          session_id: currentSession && !currentSession.isTemporary ? currentSession.id : undefined
        },
        // onThinking
        (content) => {
          thinkingText += content;
          setMessages(prev => prev.map(msg =>
            msg.id === loadingId ? { ...msg, thinking: thinkingText } : msg
          ));
        },
        // onResponse
        (content) => {
          responseText += content;
          setMessages(prev => prev.map(msg =>
            msg.id === loadingId ? { ...msg, content: responseText } : msg
          ));
        },
        // onThinkingStart
        () => {
          setMessages(prev => prev.map(msg =>
            msg.id === loadingId ? { ...msg, isThinking: true, isLoading: false, thinkingStartTime: Date.now() } : msg
          ));
        },
        // onThinkingEnd
        () => {
          setMessages(prev => prev.map(msg =>
            msg.id === loadingId ? { ...msg, isThinking: false, thinkingCollapsed: true, thinkingEndTime: Date.now() } : msg
          ));
        },
        // onComplete
        () => {
          setIsGenerating(false);
          setAbortController(null);

          // 保存会话
          const assistantMessage: Message = {
            id: loadingId,
            role: 'assistant',
            content: responseText,
            thinking: thinkingText
          };

          const updatedMessages = [...messages, userMessage, assistantMessage];

          if (currentSession && !currentSession.isTemporary) {
            currentSession.messages = updatedMessages.map(m => ({
              id: m.id,
              role: m.role,
              content: m.content,
              thinking: m.thinking,
              thinkingStartTime: m.thinkingStartTime,
              thinkingEndTime: m.thinkingEndTime
            }));
            currentSession.updatedAt = Date.now();

            SessionManager.updateSessionTitle(currentSession);
            SessionManager.saveSession(currentSession);
            setCurrentSession({...currentSession});
          }
        },
        // onError
        (error) => {
          console.error(error);
          setMessages(prev => prev.map(msg =>
            msg.id === loadingId ? { ...msg, isLoading: false, isThinking: false, content: '连接后端失败，请确保 API 服务正在运行 (http://127.0.0.1:8000)' } : msg
          ));
          setIsGenerating(false);
          setAbortController(null);
        }
      );

      // 保存abort函数以便手动停止
      setAbortController({ signal: { aborted: false }, abort: abortStream } as any);

    } catch (error: any) {
      console.error(error);
      setMessages(prev => prev.map(msg =>
        msg.id === loadingId ? { ...msg, isLoading: false, isThinking: false, content: '连接后端失败，请确保 API 服务正在运行 (http://127.0.0.1:8000)' } : msg
      ));
      setIsGenerating(false);
      setAbortController(null);
    }
  };

  // Welcome UI
  if (messages.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full bg-white dark:bg-gray-900 p-4 animate-fadeIn transition-colors duration-300">
        <div className="max-w-3xl w-full flex flex-col items-center space-y-6 relative -mt-32">
          {/* Headline */}
          <div className="text-center space-y-2 mb-4">
            <h1 className="text-3xl font-bold text-gray-800 dark:text-white transition-colors duration-300">{greeting}</h1>
            <p className="text-gray-500 dark:text-gray-400">我是 CogniMark，您的跨境电商智能助手</p>
          </div>

          {/* Main Input Bar */}
          <div className={cn(
            "w-full max-w-4xl rounded-[32px] p-4 relative group transition-all duration-300 min-h-[130px] flex flex-col justify-between",
            "bg-[#F9F9F9] dark:bg-gray-800",
            "border border-gray-200 dark:border-b-[3px] dark:border-t-0 dark:border-x-0 dark:border-indigo-500/50",
            "dark:animate-fluorescent"
          )}>
            <div className="absolute top-0 left-6 right-6 h-[1px] bg-gradient-to-r from-transparent via-white/80 to-transparent dark:via-white/20 pointer-events-none opacity-70" />

            {/* 上传的文件显示（极简版） */}
            {(currentUploadingFile || uploadedFiles.length > 0) && (
              <div className="mb-3 px-1">
                {currentUploadingFile && (
                  <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                    <div className="w-8 h-8 bg-green-100 dark:bg-green-900/40 rounded flex items-center justify-center flex-shrink-0">
                      <Loader2 className="w-4 h-4 text-green-600 dark:text-green-400 animate-spin" />
                    </div>
                    <div className="flex flex-col">
                      <span className="text-sm text-gray-800 dark:text-gray-200 font-medium">
                        {currentUploadingFile.name.length > 25 
                          ? currentUploadingFile.name.substring(0, 25) + '...' 
                          : currentUploadingFile.name}
                      </span>
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {(currentUploadingFile.size / 1024 / 1024).toFixed(1)} MB
                      </span>
                    </div>
                  </div>
                )}
                
                {!currentUploadingFile && uploadedFiles.map((file) => (
                  <div key={file.filename} className="inline-flex items-center gap-2 px-3 py-1.5 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                    <div className="w-8 h-8 bg-green-100 dark:bg-green-900/40 rounded flex items-center justify-center flex-shrink-0">
                      <FileSpreadsheet className="w-4 h-4 text-green-600 dark:text-green-400" />
                    </div>
                    <div className="flex flex-col">
                      <span className="text-sm text-gray-800 dark:text-gray-200 font-medium">
                        {file.filename.length > 25 
                          ? file.filename.substring(0, 25) + '...' 
                          : file.filename}
                      </span>
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        1.2 MB
                      </span>
                    </div>
                    <button
                      onClick={() => handleRemoveUploadedFile(file.filename)}
                      className="w-5 h-5 flex items-center justify-center bg-gray-400 dark:bg-gray-600 hover:bg-gray-500 dark:hover:bg-gray-500 rounded-full transition-colors flex-shrink-0"
                    >
                      <X className="w-3 h-3 text-white" />
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* 斜杠命令菜单 */}
            {showSlashMenu && (
              <div 
                ref={slashMenuRef}
                className="absolute bottom-full left-4 mb-2 w-80 bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden z-50 animate-fadeIn"
              >
                <div className="px-3 py-2 text-xs text-gray-500 dark:text-gray-400 border-b border-gray-100 dark:border-gray-700">
                  快捷命令
                </div>
                <div className="py-1">
                  {SLASH_COMMANDS.map((cmd, index) => {
                    const Icon = cmd.icon;
                    return (
                      <button
                        key={cmd.id}
                        onClick={() => handleSlashCommand(cmd.id)}
                        className={cn(
                          "w-full flex items-center gap-3 px-4 py-3 text-left transition-colors",
                          index === slashCommandIndex 
                            ? "bg-green-50 dark:bg-green-900/20" 
                            : "hover:bg-gray-50 dark:hover:bg-gray-700"
                        )}
                      >
                        <Icon className={cn("w-5 h-5", cmd.color)} />
                        <div className="flex-1">
                          <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                            {cmd.label}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {cmd.desc}
                          </p>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

            <textarea
              ref={textareaRef}
              className="w-full bg-transparent border-none focus:ring-0 focus:outline-none resize-none text-lg placeholder-gray-400 dark:placeholder-gray-500 text-gray-700 dark:text-gray-200 transition-colors min-h-[24px] max-h-[200px] relative z-10"
              placeholder="和 CogniMark 说点什么 (输入 / 查看快捷命令)"
              value={inputValue}
              onChange={handleInputChange}
              onKeyDown={handleInputKeyDown}
              rows={1}
            />
            
            <div className="flex justify-between items-center mt-4 px-1 relative z-10">
              {/* Left Actions */}
              <div className="flex items-center gap-3">
                 <button 
                   onClick={() => fileInputRef.current?.click()}
                   className="w-9 h-9 flex items-center justify-center rounded-full bg-gray-200 dark:bg-gray-700/80 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors text-gray-600 dark:text-gray-400"
                   title="上传 Excel/CSV 文件"
                   disabled={isUploading}
                 >
                    <Upload className="w-5 h-5" />
                 </button>
                 <input
                   ref={fileInputRef}
                   type="file"
                   accept=".xlsx,.xls,.csv"
                   onChange={handleFileUpload}
                   className="hidden"
                   disabled={isUploading}
                 />

                 {/* 功能模式选择器 */}
                 <div className="relative" ref={modeMenuRef}>
                   <button
                     onClick={() => setShowModeMenu(!showModeMenu)}
                     className="flex items-center gap-2 px-3 py-1.5 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-full cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors shadow-sm"
                   >
                      {selectedMode === 'normal' && (
                        <>
                          <Sparkles className="w-4 h-4 text-gray-900 dark:text-white" />
                          <span className="text-sm font-medium text-gray-700 dark:text-gray-200">普通模式</span>
                        </>
                      )}
                      {selectedMode === 'market' && (
                        <>
                          <TrendingUp className="w-4 h-4 text-blue-500" />
                          <span className="text-sm font-medium text-blue-600 dark:text-blue-400">市场分析</span>
                        </>
                      )}
                      {selectedMode === 'selection' && (
                        <>
                          <Package className="w-4 h-4 text-green-500" />
                          <span className="text-sm font-medium text-green-600 dark:text-green-400">选品策略</span>
                        </>
                      )}
                      {selectedMode === 'ads' && (
                        <>
                          <BarChart3 className="w-4 h-4 text-purple-500" />
                          <span className="text-sm font-medium text-purple-600 dark:text-purple-400">广告优化</span>
                        </>
                      )}
                      {selectedMode === 'conversion' && (
                        <>
                          <Sparkles className="w-4 h-4 text-orange-500" />
                          <span className="text-sm font-medium text-orange-600 dark:text-orange-400">转化优化</span>
                        </>
                      )}
                      <ChevronDown className={cn("w-3 h-3 text-gray-500 transition-transform", showModeMenu && "rotate-180")} />
                   </button>
                   
                   {/* 下拉菜单 */}
                   {showModeMenu && (
                     <div className="absolute top-full mt-2 left-0 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-lg overflow-hidden z-50 min-w-[180px]">
                       <button
                         onClick={() => {
                           setSelectedMode('normal');
                           setShowModeMenu(false);
                         }}
                         className={cn(
                           "w-full flex items-center gap-2 px-4 py-2.5 hover:bg-gray-50 dark:hover:bg-gray-700 text-sm transition-colors text-left",
                           selectedMode === 'normal' ? "bg-green-50 dark:bg-green-900/20 text-indigo-600 dark:text-indigo-400" : "text-gray-700 dark:text-gray-200"
                         )}
                       >
                         <Sparkles className="w-4 h-4" />
                         普通模式
                       </button>
                       <button
                         onClick={() => {
                           setSelectedMode('market');
                           setShowModeMenu(false);
                         }}
                         className={cn(
                           "w-full flex items-center gap-2 px-4 py-2.5 hover:bg-gray-50 dark:hover:bg-gray-700 text-sm transition-colors text-left",
                           selectedMode === 'market' ? "bg-green-50 dark:bg-green-900/20 text-blue-600 dark:text-blue-400" : "text-gray-700 dark:text-gray-200"
                         )}
                       >
                         <TrendingUp className="w-4 h-4 text-blue-500" />
                         市场趋势分析
                       </button>
                       <button
                         onClick={() => {
                           setSelectedMode('selection');
                           setShowModeMenu(false);
                         }}
                         className={cn(
                           "w-full flex items-center gap-2 px-4 py-2.5 hover:bg-gray-50 dark:hover:bg-gray-700 text-sm transition-colors text-left",
                           selectedMode === 'selection' ? "bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400" : "text-gray-700 dark:text-gray-200"
                         )}
                       >
                         <Package className="w-4 h-4 text-green-500" />
                         选品策略建议
                       </button>
                       <button
                         onClick={() => {
                           setSelectedMode('ads');
                           setShowModeMenu(false);
                         }}
                         className={cn(
                           "w-full flex items-center gap-2 px-4 py-2.5 hover:bg-gray-50 dark:hover:bg-gray-700 text-sm transition-colors text-left",
                           selectedMode === 'ads' ? "bg-green-50 dark:bg-green-900/20 text-purple-600 dark:text-purple-400" : "text-gray-700 dark:text-gray-200"
                         )}
                       >
                         <BarChart3 className="w-4 h-4 text-purple-500" />
                         广告优化建议
                       </button>
                       <button
                         onClick={() => {
                           setSelectedMode('conversion');
                           setShowModeMenu(false);
                         }}
                         className={cn(
                           "w-full flex items-center gap-2 px-4 py-2.5 hover:bg-gray-50 dark:hover:bg-gray-700 text-sm transition-colors text-left",
                           selectedMode === 'conversion' ? "bg-green-50 dark:bg-green-900/20 text-orange-600 dark:text-orange-400" : "text-gray-700 dark:text-gray-200"
                         )}
                       >
                         <Sparkles className="w-4 h-4 text-orange-500" />
                         转化率优化
                       </button>
                     </div>
                   )}
                 </div>
                 

              </div>

              {/* Right Actions: Send/Stop Button */}
              {isGenerating ? (
                <button 
                  onClick={handleStopGenerating}
                  className="w-10 h-10 flex items-center justify-center bg-red-600 text-white rounded-full hover:bg-red-700 transition-all"
                  title="停止生成"
                >
                  <X className="w-5 h-5" />
                </button>
              ) : (
                <button 
                  onClick={() => handleGenerate()}
                  disabled={!inputValue.trim()}
                  className="w-10 h-10 flex items-center justify-center bg-[#5865F2] text-white rounded-full hover:bg-[#4752C4] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send className="w-5 h-5" />
                </button>
              )}
            </div>
            
            <div className="absolute bottom-0 left-0 right-0 h-24 pointer-events-none overflow-hidden rounded-b-[32px] z-0">
               <div className="absolute bottom-0 left-0 right-0 h-full bg-gradient-to-t from-gray-100/80 via-gray-50/30 to-transparent dark:from-indigo-900/20 dark:via-indigo-900/5 dark:to-transparent" />
               <div className="absolute bottom-0 left-12 right-12 h-[1px] bg-gradient-to-r from-transparent via-indigo-200/50 to-transparent dark:via-indigo-400/30 shadow-[0_0_10px_rgba(99,102,241,0.2)]" />
            </div>
          </div>

        </div>
      </div>
    );
  }

  // Active Chat Interface
  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-900 overflow-hidden relative transition-colors duration-300">
      <div className="flex-1 overflow-y-auto p-4 space-y-6 pb-24" ref={scrollRef}>
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={cn(
              "flex gap-3 max-w-[85%] mx-auto group",
              msg.role === 'user' ? "ml-auto flex-row-reverse" : "mr-auto"
            )}
          >
            {msg.role !== 'user' && (
              <div className="flex items-center justify-center flex-shrink-0 w-12 h-12 rounded-full bg-indigo-100 dark:bg-indigo-900">
                <Sparkles className={cn(
                  "w-6 h-6",
                  msg.isThinking ? "text-indigo-700 dark:text-indigo-500 animate-pulse" : "text-indigo-600 dark:text-indigo-400"
                )} />
              </div>
            )}

            <div className="space-y-2">
              {(msg.thinking || msg.isThinking) && (
                <div className="text-xs">
                  <div
                    className="flex items-center gap-1.5 mb-1.5 cursor-pointer select-none"
                    onClick={() => {
                      if (!msg.isThinking) {
                        setMessages(prev => prev.map(m =>
                          m.id === msg.id ? { ...m, thinkingCollapsed: !m.thinkingCollapsed } : m
                        ));
                      }
                    }}
                  >
                    <Sparkles className={cn(
                      "w-3.5 h-3.5",
                      msg.isThinking
                        ? "text-green-400 animate-spin"
                        : "text-green-500/70 dark:text-green-400/70 animate-pulse"
                    )} />
                    <span className="font-medium text-gray-600 dark:text-gray-300">
                      {msg.isThinking ? 'thinking...' : msg.thinkingEndTime && msg.thinkingStartTime ? `Thought completed (${((msg.thinkingEndTime - msg.thinkingStartTime) / 1000).toFixed(1)}s)` : 'thinking'}
                    </span>
                    {!msg.isThinking && (
                      <ChevronDown className={cn(
                        "w-3 h-3 ml-auto transition-transform duration-200",
                        msg.thinkingCollapsed && "rotate-180"
                      )} />
                    )}
                  </div>
                  {(msg.isThinking || !msg.thinkingCollapsed) && (
                    <div className="animate-fadeIn px-3 text-gray-500/70 dark:text-gray-400/60">
                      {msg.thinking ? (
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.thinking}</ReactMarkdown>
                      ) : (
                        <div className="flex items-center gap-1 text-xs opacity-50 py-1">
                          <span className="flex gap-0.5">
                            <span className="w-1 h-1 bg-current rounded-full animate-bounce" style={{ animationDelay: '0s' }}></span>
                            <span className="w-1 h-1 bg-current rounded-full animate-bounce" style={{ animationDelay: '0.15s' }}></span>
                            <span className="w-1 h-1 bg-current rounded-full animate-bounce" style={{ animationDelay: '0.3s' }}></span>
                          </span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* 只在有正式内容或加载中时才显示白框 */}
              {(msg.content || msg.isLoading) && (
                <div className={cn(
                  "p-4 rounded-2xl text-sm leading-relaxed shadow-sm transition-colors duration-300",
                  msg.role === 'user'
                    ? "bg-[#F4F4F4] dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-tr-none whitespace-pre-wrap"
                    : "bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 text-gray-800 dark:text-gray-200 rounded-tl-none prose prose-sm dark:prose-invert max-w-none"
                )}>
                 {msg.isLoading ? (
                   <div className="flex gap-1 h-6 items-center">
                     <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0s' }}></span>
                     <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
                     <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></span>
                   </div>
                 ) : msg.role === 'assistant' ? (
                   <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                 ) : (
                   msg.content
                 )}
                </div>
              )}

              {/* 操作按钮 - 只在有内容时显示 */}
              {msg.role === 'assistant' && !msg.isLoading && msg.content && (
                <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button 
                    onClick={() => navigator.clipboard.writeText(msg.content)}
                    className="p-1.5 text-gray-400 dark:text-gray-500 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-md transition-colors text-xs flex items-center gap-1"
                    title="复制"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                  <button
                    onClick={async () => {
                      if (regeneratingId) return;

                      // 找到这条消息对应的用户消息
                      const msgIndex = messages.findIndex(m => m.id === msg.id);
                      if (msgIndex > 0) {
                        const userMsg = messages[msgIndex - 1];
                        if (userMsg.role === 'user') {
                          // 将当前回复设置为加载状态
                          setMessages(prev => prev.map(m =>
                            m.id === msg.id ? { ...m, content: '', thinking: '', isLoading: true, isThinking: false, thinkingCollapsed: false } : m
                          ));
                          setRegeneratingId(msg.id);

                          try {
                            // 检测是否需要产品上下文
                            let context = '';
                            const mentionsProduct = /产品|P\d{3}|选品|推荐/.test(userMsg.content);
                            if (mentionsProduct && products.length > 0) {
                              context = `可用产品列表:\n${products.map(p => `- ${p.product_id}: ${p.title_en}`).join('\n')}`;
                            }

                            // 准备历史（到重新生成的这条消息之前）
                            const historyUpToThis = messages
                              .slice(0, msgIndex)
                              .filter(m => !m.isLoading)
                              .map(m => ({
                                role: m.role,
                                content: m.content
                              }));

                            let thinkingText = '';
                            let responseText = '';

                            await chatWithAgentStream(
                              {
                                message: userMsg.content,
                                context: context || undefined,
                                history: historyUpToThis.length > 0 ? historyUpToThis : undefined,
                                session_id: currentSession && !currentSession.isTemporary ? currentSession.id : undefined
                              },
                              // onThinking
                              (content) => {
                                thinkingText += content;
                                setMessages(prev => prev.map(m =>
                                  m.id === msg.id ? { ...m, thinking: thinkingText } : m
                                ));
                              },
                              // onResponse
                              (content) => {
                                responseText += content;
                                setMessages(prev => prev.map(m =>
                                  m.id === msg.id ? { ...m, content: responseText } : m
                                ));
                              },
                              // onThinkingStart
                              () => {
                                setMessages(prev => prev.map(m =>
                                  m.id === msg.id ? { ...m, isThinking: true, isLoading: false } : m
                                ));
                              },
                              // onThinkingEnd
                              () => {
                                setMessages(prev => prev.map(m =>
                                  m.id === msg.id ? { ...m, isThinking: false, thinkingCollapsed: true } : m
                                ));
                              },
                              // onComplete
                              () => {
                                setRegeneratingId(null);

                                // 保存会话（临时会话不保存）
                                if (currentSession && !currentSession.isTemporary) {
                                  const msgIdx = currentSession.messages.findIndex(m => m.id === msg.id);
                                  if (msgIdx >= 0) {
                                    currentSession.messages[msgIdx].content = responseText;
                                    currentSession.messages[msgIdx].thinking = thinkingText; // 保存thinking
                                    currentSession.updatedAt = Date.now();
                                    SessionManager.saveSession(currentSession);
                                  }
                                }
                              },
                              // onError
                              (error) => {
                                setMessages(prev => prev.map(m =>
                                  m.id === msg.id ? { ...m, isLoading: false, isThinking: false, content: '重新生成失败' } : m
                                ));
                                setRegeneratingId(null);
                              }
                            );

                          } catch (error: any) {
                            if (error.name !== 'AbortError') {
                              setMessages(prev => prev.map(m =>
                                m.id === msg.id ? { ...m, isLoading: false, isThinking: false, content: '重新生成失败' } : m
                              ));
                            }
                            setRegeneratingId(null);
                          }
                        }
                      }
                    }}
                    className="p-1.5 text-gray-400 dark:text-gray-500 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-md transition-colors text-xs flex items-center gap-1"
                    title="重新生成"
                    disabled={regeneratingId !== null}
                  >
                    <Loader2 className={cn("w-4 h-4", regeneratingId === msg.id && "animate-spin")} />
                  </button>
                  <button className="p-1.5 text-gray-400 dark:text-gray-500 hover:text-green-600 dark:hover:text-green-400 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-md transition-colors text-xs flex items-center gap-1" title="赞">
                    <ThumbsUp className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}

        {/* 滚动锚点 */}
        <div ref={messagesEndRef} className="h-1" />
      </div>

      {/* 滚动控制按钮 - 当不在底部时显示 */}
      {!autoScroll && (
        <button
          onClick={scrollToBottom}
          className="fixed bottom-28 right-8 z-30 p-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-full shadow-lg transition-all duration-300 hover:scale-110 animate-bounce"
          title="回到底部"
        >
          <ArrowDown className="w-5 h-5" />
        </button>
      )}

      {/* Bottom Input Bar */}
      <div className="absolute bottom-6 left-0 right-0 px-6 z-20 pointer-events-none">
        <div className="max-w-3xl mx-auto relative group pointer-events-auto">
           <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-full opacity-20 group-hover:opacity-30 blur-md transition-opacity duration-500" />

           {/* 斜杠命令菜单 - 底部输入框 */}
           {showSlashMenu && (
              <div 
                ref={slashMenuRef}
                className="absolute bottom-full left-0 mb-2 w-72 bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden z-50 animate-fadeIn"
              >
                <div className="px-3 py-2 text-xs text-gray-500 dark:text-gray-400 border-b border-gray-100 dark:border-gray-700">
                  快捷命令
                </div>
                <div className="py-1 max-h-60 overflow-y-auto">
                  {SLASH_COMMANDS.map((cmd, index) => {
                    const Icon = cmd.icon;
                    return (
                      <button
                        key={cmd.id}
                        onClick={() => handleSlashCommand(cmd.id)}
                        className={cn(
                          "w-full flex items-center gap-3 px-4 py-2.5 text-left transition-colors",
                          index === slashCommandIndex 
                            ? "bg-green-50 dark:bg-green-900/20" 
                            : "hover:bg-gray-50 dark:hover:bg-gray-700"
                        )}
                      >
                        <Icon className={cn("w-4 h-4", cmd.color)} />
                        <div className="flex-1">
                          <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                            {cmd.label}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {cmd.desc}
                          </p>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

           <div className="relative bg-white/95 dark:bg-gray-800/95 backdrop-blur-md rounded-2xl border border-gray-200 dark:border-gray-700 shadow-xl flex items-end p-2 transition-all duration-300 hover:shadow-2xl">
              <div className="pl-2 pb-2 text-green-600 dark:text-green-400">
                <Sparkles className={cn("w-5 h-5", isGenerating && "animate-pulse")} />
              </div>

              <textarea
                ref={textareaRef}
                className="flex-1 bg-transparent border-none focus:ring-0 focus:outline-none resize-none text-gray-700 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 min-h-[40px] max-h-[120px] py-2.5 px-2"
                placeholder="发送消息... (输入 / 查看快捷命令)"
                value={inputValue}
                onChange={handleInputChange}
                onKeyDown={handleInputKeyDown}
                rows={1}
              />

              {isGenerating ? (
                <button
                  onClick={handleStopGenerating}
                  className="mb-1 p-2 bg-red-600 hover:bg-red-700 text-white rounded-full transition-all duration-300 shadow-sm hover:shadow-md hover:scale-105"
                  title="停止生成"
                >
                  <X className="w-4 h-4" />
                </button>
              ) : (
                <button
                  onClick={() => handleGenerate()}
                  disabled={!inputValue.trim()}
                  className="p-2.5 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white rounded-full transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 shadow-sm hover:shadow-md hover:scale-105"
                >
                  <Send className="w-4 h-4" />
                </button>
              )}
           </div>

           <p className="text-[10px] text-center text-gray-400 dark:text-gray-500 mt-2 opacity-70">
            AI 生成内容仅供参考
           </p>
        </div>
      </div>
    </div>
  );
}
