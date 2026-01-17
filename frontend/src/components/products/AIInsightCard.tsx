import { Bot, Sparkles, X } from 'lucide-react';

interface AIInsightCardProps {
  content: string;
  onClose: () => void;
}

export default function AIInsightCard({ content, onClose }: AIInsightCardProps) {
  // Simple markdown parser for the demo
  const renderContent = (text: string) => {
    return text.split('\n').map((line, index) => {
      if (line.startsWith('### ')) {
        return <h3 key={index} className="text-lg font-bold text-indigo-900 dark:text-indigo-300 mt-4 mb-2">{line.replace('### ', '')}</h3>;
      }
      if (line.startsWith('**') && line.endsWith('**')) { // Simplified Line Header
          return <p key={index} className="font-bold mt-2 text-gray-900 dark:text-white">{line.replace(/\*\*/g, '')}</p>
      }
      
      // Process inline bolding for paragraphs
      const parts = line.split(/(\*\*.*?\*\*)/g);
      return (
        <p key={index} className="text-gray-700 dark:text-gray-300 leading-relaxed mb-1">
          {parts.map((part, i) => {
            if (part.startsWith('**') && part.endsWith('**')) {
              return <strong key={i} className="font-semibold text-indigo-700 dark:text-indigo-400">{part.replace(/\*\*/g, '')}</strong>;
            }
            return part;
          })}
        </p>
      );
    });
  };

  return (
    <div className="bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-800 rounded-xl p-6 mb-6 relative animate-fadeIn transition-colors duration-300">
      <button 
        onClick={onClose}
        className="absolute top-4 right-4 text-indigo-400 hover:text-indigo-600 dark:hover:text-indigo-300 transition-colors"
      >
        <X className="w-5 h-5" />
      </button>

      <div className="flex items-center gap-2 mb-4">
        <div className="bg-indigo-600 text-white p-2 rounded-lg">
          <Bot className="w-5 h-5" />
        </div>
        <div>
          <h3 className="font-bold text-indigo-900 dark:text-indigo-100 text-lg flex items-center gap-2">
            AI 深度选品建议
            <Sparkles className="w-4 h-4 text-yellow-500 animate-pulse" />
          </h3>
          <p className="text-xs text-indigo-600 dark:text-indigo-400">Powered by Qwen-Turbo</p>
        </div>
      </div>

      <div className="prose prose-indigo max-w-none bg-white/50 dark:bg-gray-800/50 p-4 rounded-lg border border-indigo-50 dark:border-indigo-900/30">
        {renderContent(content)}
      </div>
    </div>
  );
}
