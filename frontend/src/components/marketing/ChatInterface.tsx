import { useState, useRef, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Send, Copy, ThumbsUp, ThumbsDown, Loader2, Sparkles, Search, Image as ImageIcon, FileText, Plus, ChevronDown, Globe } from 'lucide-react';
import { getProducts, generateMarketingCopy, getChatHistory } from '../../services/api';
import { cn } from '../../utils/cn';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  isLoading?: boolean;
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]); 
  const [isGenerating, setIsGenerating] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [greeting, setGreeting] = useState('');
  const [products, setProducts] = useState<Array<{ product_id: string; title_en: string }>>([]);
  const [selectedProduct, setSelectedProduct] = useState('');
  const [targetLanguage, setTargetLanguage] = useState('Chinese');
  const [channel, setChannel] = useState('Facebook Ads');
  const scrollRef = useRef<HTMLDivElement>(null);
  const location = useLocation();

  useEffect(() => {
    const hour = new Date().getHours();
    if (hour >= 11 && hour < 13) setGreeting('中午好');
    else if (hour < 11) setGreeting('上午好');
    else if (hour < 18) setGreeting('下午好');
    else setGreeting('晚上好');
    
    // Load products
    loadProducts();
    // Load history
    loadChatHistory();
  }, []);

  const loadChatHistory = async () => {
    try {
      const history = await getChatHistory();
      if (history && history.length > 0) {
        setMessages(history.map((msg, index) => ({
          id: `history-${index}-${Date.now()}`,
          role: msg.role as 'user' | 'assistant',
          content: msg.content
        })));
      }
    } catch (error) {
      console.error('Failed to load chat history:', error);
    }
  };

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
    if (params.get('new')) {
      setMessages([]);
      setInputValue('');
    }
  }, [location.search]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleGenerate = async (text?: string) => {
    const promptText = text || inputValue;
    if (!promptText.trim() && !selectedProduct) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: promptText || `为产品 ${selectedProduct} 生成 ${channel} 的 ${targetLanguage} 营销文案`
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsGenerating(true);

    const loadingId = (Date.now() + 1).toString();
    setMessages(prev => [...prev, { id: loadingId, role: 'assistant', content: '', isLoading: true }]);

    try {
      const response = await generateMarketingCopy({
        product_id: selectedProduct,
        target_language: targetLanguage,
        channel: channel
      });
      
      setMessages(prev => prev.map(msg => 
        msg.id === loadingId ? { ...msg, isLoading: false, content: '' } : msg
      ));

      // Simulate streaming effect
      let currentText = '';
      const text = response.copy_text;
      for (let i = 0; i < text.length; i += 5) {
        const chunk = text.slice(i, i + 5);
        currentText += chunk;
        setMessages(prev => prev.map(msg => 
          msg.id === loadingId ? { ...msg, content: currentText } : msg
        ));
        await new Promise(resolve => setTimeout(resolve, 10));
      }

    } catch (error) {
      console.error(error);
      setMessages(prev => prev.map(msg => 
        msg.id === loadingId ? { ...msg, isLoading: false, content: '连接后端失败，请确保 API 服务正在运行 (http://127.0.0.1:8000)' } : msg
      ));
    } finally {
      setIsGenerating(false);
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
            <p className="text-gray-500 dark:text-gray-400">选择产品并生成营销文案</p>
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
                className="w-full px-4 py-2 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
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
                  className="w-full px-4 py-2 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
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
                  className="w-full px-4 py-2 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
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
              className="w-full py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 font-medium"
            >
              <Sparkles className="w-5 h-5" />
              生成营销文案
            </button>
          </div>

          {/* Quick Actions */}
          <div className="flex flex-wrap justify-center gap-3">
            <button 
              onClick={() => handleGenerate("分析一下这个产品的竞品情况和市场竞争格局")}
              className="flex items-center gap-2 px-4 py-2 bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full text-sm text-gray-600 dark:text-gray-300 transition-colors border border-transparent hover:border-gray-200 dark:hover:border-gray-600"
            >
              <Search className="w-4 h-4 text-blue-500" />
              竞品分析
            </button>
            <button 
              onClick={() => handleGenerate("为这个产品生成 5 个高转化的 SEO 标题，包含核心关键词")}
              className="flex items-center gap-2 px-4 py-2 bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full text-sm text-gray-600 dark:text-gray-300 transition-colors border border-transparent hover:border-gray-200 dark:hover:border-gray-600"
            >
              <FileText className="w-4 h-4 text-green-500" />
              生成 SEO 标题
            </button>
            <button 
              onClick={() => handleGenerate("为这个产品写一段 Instagram 推广文案，语气轻松活泼，带 Emoji")}
              className="flex items-center gap-2 px-4 py-2 bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full text-sm text-gray-600 dark:text-gray-300 transition-colors border border-transparent hover:border-gray-200 dark:hover:border-gray-600"
            >
              <ImageIcon className="w-4 h-4 text-pink-500" />
              社媒推广文案
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
                <Sparkles className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
              </div>
            )}
            
            <div className="space-y-2">
              <div className={cn(
                "p-4 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap shadow-sm transition-colors duration-300",
                msg.role === 'user' 
                  ? "bg-[#F4F4F4] dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-tr-none" 
                  : "bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 text-gray-800 dark:text-gray-200 rounded-tl-none"
              )}>
                 {msg.isLoading ? (
                   <div className="flex gap-1 h-6 items-center">
                     <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0s' }}></span>
                     <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
                     <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></span>
                   </div>
                 ) : (
                   msg.content
                 )}
              </div>
              
              {msg.role === 'assistant' && !msg.isLoading && (
                <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button 
                    onClick={() => navigator.clipboard.writeText(msg.content)}
                    className="p-1.5 text-gray-400 dark:text-gray-500 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-md transition-colors text-xs flex items-center gap-1"
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
      </div>

      {/* Bottom Input Bar */}
      <div className="absolute bottom-6 left-0 right-0 px-6 z-20 pointer-events-none">
        <div className="max-w-3xl mx-auto relative group pointer-events-auto">
           <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-full opacity-20 group-hover:opacity-30 blur-md transition-opacity duration-500" />
           
           <div className="relative bg-white dark:bg-gray-800 backdrop-blur-md rounded-full border border-gray-200 dark:border-gray-700 shadow-xl flex items-center p-1.5 transition-colors">
              <div className="pl-3 pr-2 text-indigo-600 dark:text-indigo-400">
                <Sparkles className="w-5 h-5 animate-pulse" />
              </div>

              <input
                type="text"
                className="flex-1 bg-transparent border-none focus:ring-0 focus:outline-none text-gray-700 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 h-10"
                placeholder="发送消息..."
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
              />

              <button 
                onClick={() => handleGenerate()}
                disabled={isGenerating || !inputValue.trim()}
                className="p-2 bg-indigo-600 text-white rounded-full hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
              >
                 {isGenerating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
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
