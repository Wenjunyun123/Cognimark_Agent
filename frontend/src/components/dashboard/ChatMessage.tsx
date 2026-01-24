import { memo } from 'react';
import { Copy, ThumbsUp, Loader2, Sparkles } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { cn } from '../../utils/cn';

export interface MessageProps {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  isLoading?: boolean;
  onCopy?: () => void;
  onRegenerate?: () => void;
  isRegenerating?: boolean;
}

// OPTIMIZATION: 使用 React.memo 避免不必要的重新渲染 (rerender-memo)
export const ChatMessage = memo<MessageProps>(({
  id,
  role,
  content,
  isLoading,
  onCopy,
  onRegenerate,
  isRegenerating
}) => {
  return (
    <div
      className={cn(
        "flex gap-3 max-w-[85%] mx-auto group",
        role === 'user' ? "ml-auto flex-row-reverse" : "mr-auto"
      )}
    >
      {role !== 'user' && (
        <div className="flex items-center justify-center flex-shrink-0 w-12 h-12 rounded-full bg-indigo-100 dark:bg-indigo-900">
          <Sparkles className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
        </div>
      )}

      <div className="space-y-2">
        <div className={cn(
          "p-4 rounded-2xl text-sm leading-relaxed shadow-sm transition-colors duration-300",
          role === 'user'
            ? "bg-[#F4F4F4] dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-tr-none whitespace-pre-wrap"
            : "bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 text-gray-800 dark:text-gray-200 rounded-tl-none prose prose-sm dark:prose-invert max-w-none"
        )}>
          {isLoading ? (
            <div className="flex gap-1 h-6 items-center">
              <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0s' }}></span>
              <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
              <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></span>
            </div>
          ) : role === 'assistant' ? (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
          ) : (
            content
          )}
        </div>

        {role === 'assistant' && !isLoading && (
          <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              onClick={onCopy}
              className="p-1.5 text-gray-400 dark:text-gray-500 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-md transition-colors text-xs flex items-center gap-1"
              title="复制"
            >
              <Copy className="w-4 h-4" />
            </button>
            <button
              onClick={onRegenerate}
              className="p-1.5 text-gray-400 dark:text-gray-500 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-md transition-colors text-xs flex items-center gap-1"
              title="重新生成"
              disabled={isRegenerating}
            >
              <Loader2 className={cn("w-4 h-4", isRegenerating && "animate-spin")} />
            </button>
            <button className="p-1.5 text-gray-400 dark:text-gray-500 hover:text-green-600 dark:hover:text-green-400 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-md transition-colors text-xs flex items-center gap-1" title="赞">
              <ThumbsUp className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
});

ChatMessage.displayName = 'ChatMessage';
