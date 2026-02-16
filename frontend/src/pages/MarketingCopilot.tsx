import { useState, useRef, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Send, Copy, ThumbsUp, Sparkles, ChevronDown } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { getProducts, chatWithAgentStream } from '../services/api';
import { cn } from '../utils/cn';
import { SessionManager, ChatSession } from '../utils/sessionManager';

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

export default function MarketingCopilot() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [greeting, setGreeting] = useState('');
  const [products, setProducts] = useState<Array<{ product_id: string; title_en: string }>>([]);
  const [selectedProduct, setSelectedProduct] = useState('');
  const [targetLanguage, setTargetLanguage] = useState('Chinese');
  const [channel, setChannel] = useState('Facebook Ads');
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const location = useLocation();
  const navigate = useNavigate();

  const isNewSession = new URLSearchParams(location.search).get('action') === 'new' || 
                       new URLSearchParams(location.search).get('new') !== null;

  useEffect(() => {
    const hour = new Date().getHours();
    if (hour >= 11 && hour < 13) setGreeting('中午好');
    else if (hour < 11) setGreeting('上午好');
    else if (hour < 18) setGreeting('下午好');
    else setGreeting('晚上好');
    
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      const data = await getProducts();
      setProducts(data);
      if (data.length > 0) {
        setSelectedProduct(data[0].product_id);
      }
    } catch (error) {
      console.error('Failed to load products:', error);
    }
  };

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const sessionId = params.get('session');
    const action = params.get('action');

    if (action === 'new' || action === 'temp') {
      SessionManager.clearMarketingCurrentSession();
      setMessages([]);
      setInputValue('');
      setCurrentSession(null);
      if (action === 'new') {
        navigate('/marketing', { replace: true });
      }
    } else if (sessionId) {
      const session = SessionManager.getSession(sessionId);
      if (session) {
        setCurrentSession(session);
        setMessages(session.messages as Message[]);
        SessionManager.setMarketingCurrentSession(session.id);
      }
    } else {
      const marketingSession = SessionManager.getMarketingCurrentSession();
      if (marketingSession && marketingSession.messages.length > 0) {
        setCurrentSession(marketingSession);
        setMessages(marketingSession.messages as Message[]);
      }
    }
  }, [location.search, location.pathname, navigate]);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }, [messages]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 120) + 'px';
    }
  }, [inputValue]);

  const handleGenerate = async (customPrompt?: string) => {
    const promptText = customPrompt || inputValue;
    if (!promptText.trim() && !selectedProduct) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: customPrompt || `为产品 ${selectedProduct} 生成 ${channel} 的 ${targetLanguage} 营销文案`
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsGenerating(true);

      const loadingId = (Date.now() + 1).toString();
    setMessages(prev => [...prev, { id: loadingId, role: 'assistant', content: '', thinking: '', isLoading: true, isThinking: false, thinkingCollapsed: false }]);

    try {
      let thinkingText = '';
      let responseText = '';
      let thinkingStartTime = 0;
      let thinkingEndTime = 0;

      // 统一使用流式聊天API，确保与Dashboard一致的体验
      const promptMessage = customPrompt
        ? `我正在使用产品 ${selectedProduct}（${products.find(p => p.product_id === selectedProduct)?.title_en}），请帮我：${customPrompt}`
        : `请为产品 ${selectedProduct}（${products.find(p => p.product_id === selectedProduct)?.title_en}）生成 ${channel} 的 ${targetLanguage} 营销文案`;

      await chatWithAgentStream(
        {
          message: promptMessage,
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
          thinkingStartTime = Date.now();
          setMessages(prev => prev.map(msg =>
            msg.id === loadingId ? { ...msg, isThinking: true, isLoading: false, thinkingStartTime } : msg
          ));
        },
        // onThinkingEnd
        () => {
          thinkingEndTime = Date.now();
          setMessages(prev => prev.map(msg =>
            msg.id === loadingId ? { ...msg, isThinking: false, thinkingCollapsed: true, thinkingEndTime } : msg
          ));
        },
        // onComplete
        () => {
          setIsGenerating(false);

          if (!thinkingEndTime) {
            thinkingEndTime = Date.now();
          }

          const finalAssistantMessage: Message = {
            id: loadingId,
            role: 'assistant',
            content: responseText,
            thinking: thinkingText,
            isLoading: false,
            isThinking: false,
            thinkingCollapsed: true,
            thinkingStartTime,
            thinkingEndTime
          };

          const updatedMessages = [...messages.filter(m => m.id !== loadingId), userMessage, finalAssistantMessage];

          const session = SessionManager.createSession('营销文案对话');
          session.isMarketing = true;
          
          session.messages = updatedMessages.map(m => ({
            id: m.id,
            role: m.role,
            content: m.content,
            thinking: m.thinking,
            thinkingStartTime: m.thinkingStartTime,
            thinkingEndTime: m.thinkingEndTime
          }));
          session.productId = selectedProduct;
          session.targetLanguage = targetLanguage;
          session.channel = channel;
          session.updatedAt = Date.now();
          SessionManager.updateSessionTitle(session);
          SessionManager.saveSession(session);
          
          setCurrentSession(session);
          SessionManager.setMarketingCurrentSession(session.id);
          setMessages(updatedMessages);
          
          navigate(`/marketing?session=${session.id}`, { replace: true });
        },
        // onError
        (error) => {
          console.error('Stream error:', error);
          setMessages(prev => prev.map(msg =>
            msg.id === loadingId ? { ...msg, isLoading: false, isThinking: false, content: '连接后端失败，请确保 API 服务正在运行 (http://127.0.0.1:8000)' } : msg
          ));
          setIsGenerating(false);
        }
      );

    } catch (error) {
      console.error('Generate error:', error);
      setMessages(prev => prev.map(msg =>
        msg.id === loadingId ? { ...msg, isLoading: false, isThinking: false, content: '连接后端失败，请确保 API 服务正在运行 (http://127.0.0.1:8000)' } : msg
      ));
      setIsGenerating(false);
    }
  };

  const handleGenerateWithTimeout = async () => {
    setTimeout(() => {
      if (isGenerating) {
        console.log('Request timeout, forcing reset...');
        setMessages(prev => prev.map(msg =>
          msg.isLoading ? { ...msg, isLoading: false, isThinking: false, content: '请求超时，请重试' } : msg
        ));
        setIsGenerating(false);
      }
    }, 30000);
    
    await handleGenerate();
  };

  // Welcome UI - 保留原来的营销文案配置界面
  if (isNewSession || messages.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full bg-white dark:bg-gray-900 p-4 animate-fadeIn transition-colors duration-300">
        <div className="max-w-3xl w-full flex flex-col items-center space-y-6 relative -mt-32">
          <div className="text-center space-y-2 mb-4">
            <h1 className="text-3xl font-bold text-gray-800 dark:text-white transition-colors duration-300">{greeting}</h1>
            <p className="text-gray-500 dark:text-gray-400">智能营销文案生成器</p>
          </div>

          {/* Configuration Panel */}
          <div className="w-full max-w-2xl bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                选择产品
              </label>
              <select
                value={selectedProduct}
                onChange={(e) => setSelectedProduct(e.target.value)}
                className="w-full px-4 py-2 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                {products.map((p) => (
                  <option key={p.product_id} value={p.product_id}>
                    {p.product_id} - {p.title_en}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  目标语言
                </label>
                <select
                  value={targetLanguage}
                  onChange={(e) => setTargetLanguage(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option>English</option>
                  <option>Chinese</option>
                  <option>Spanish</option>
                  <option>French</option>
                  <option>German</option>
                  <option>Japanese</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  投放渠道
                </label>
                <select
                  value={channel}
                  onChange={(e) => setChannel(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option>Amazon Listing</option>
                  <option>Facebook Ads</option>
                  <option>TikTok Ads</option>
                  <option>Email Campaign</option>
                </select>
              </div>
            </div>

            <button
              onClick={() => handleGenerate()}
              disabled={!selectedProduct}
              className="w-full py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 font-medium"
            >
              <Sparkles className="w-5 h-5" />
              生成营销文案
            </button>
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
                  msg.isThinking ? "text-indigo-700 dark:text-indigo-500 animate-pulse" : "text-green-600 dark:text-green-400"
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

              {(msg.content || msg.isLoading) && (
                <div className={cn(
                "p-4 rounded-2xl text-sm leading-relaxed shadow-sm transition-colors duration-300",
                msg.role === 'user'
                  ? "bg-[#F4F4F4] dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-tr-none whitespace-pre-wrap"
                  : "bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 text-gray-800 dark:text-gray-200 rounded-tl-none prose prose-sm dark:prose-invert max-w-none"
              )}>
                 {msg.isLoading ? (
                   <div className="flex gap-1 h-6 items-center">
                     <span className="w-2 h-2 bg-green-400 rounded-full animate-bounce" style={{ animationDelay: '0s' }}></span>
                     <span className="w-2 h-2 bg-green-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
                     <span className="w-2 h-2 bg-green-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></span>
                   </div>
                 ) : msg.role === 'assistant' ? (
                   <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                 ) : (
                   msg.content
                 )}
              </div>
              )}

              {msg.role === 'assistant' && !msg.isLoading && msg.content && (
                <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={() => navigator.clipboard.writeText(msg.content)}
                    className="p-1.5 text-gray-400 dark:text-gray-500 hover:text-green-600 dark:hover:text-green-400 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-md transition-colors text-xs flex items-center gap-1"
                    title="复制"
                  >
                    <Copy className="w-4 h-4" />
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

      {/* Bottom Input Bar */}
      <div className="absolute bottom-6 left-0 right-0 px-6 z-20 pointer-events-none">
        <div className="max-w-3xl mx-auto relative group pointer-events-auto">
           <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-full opacity-20 group-hover:opacity-30 blur-md transition-opacity duration-500" />
           
            <div className="relative bg-white/95 dark:bg-gray-800/95 backdrop-blur-md rounded-2xl border border-gray-200 dark:border-gray-700 shadow-xl flex items-end p-2 transition-all duration-300 hover:shadow-2xl">
               <div className="pl-2 pb-2 text-green-600 dark:text-green-400">
                 <Sparkles className={cn("w-5 h-5", isGenerating && "animate-pulse")} />
               </div>

               <textarea
                 ref={textareaRef}
                 className="flex-1 bg-transparent border-none focus:ring-0 focus:outline-none resize-none text-gray-700 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 min-h-[40px] max-h-[120px] py-2.5 px-2"
                 placeholder="发送消息..."
                 value={inputValue}
                 onChange={(e) => setInputValue(e.target.value)}
                 onKeyDown={(e) => {
                   if (e.key === 'Enter' && !e.shiftKey) {
                     e.preventDefault();
                     handleGenerate();
                   }
                 }}
                 rows={1}
               />

               <button
                 onClick={() => handleGenerate()}
                 disabled={isGenerating || !inputValue.trim()}
                 className="p-2.5 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white rounded-full transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 shadow-sm hover:shadow-md hover:scale-105"
               >
                  <Send className="w-4 h-4" />
               </button>
            </div>
           
           <p className="text-[10px] text-center text-gray-400 dark:text-gray-500 mt-2 opacity-70">
            AI 生成内容仅供参考
           </p>
        </div>
      </div>
    </div>
  );
}
