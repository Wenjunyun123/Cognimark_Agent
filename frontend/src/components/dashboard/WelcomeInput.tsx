import { memo, useRef } from 'react';
import {
  Send,
  Sparkles,
  Globe,
  TrendingUp,
  Package,
  BarChart3,
  Upload,
  ChevronDown,
  X,
  Loader2,
  FileSpreadsheet
} from 'lucide-react';
import { cn } from '../../utils/cn';
import { UploadedFile } from '../../services/api';

export interface WelcomeInputProps {
  greeting: string;
  inputValue: string;
  isGenerating: boolean;
  isUploading: boolean;
  currentUploadingFile: { name: string; size: number } | null;
  uploadedFiles: UploadedFile[];
  selectedMode: string;
  showModeMenu: boolean;
  onInputChange: (value: string) => void;
  onGenerate: () => void;
  onFileUpload: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onRemoveFile: (filename: string) => void;
  onModeChange: (mode: string) => void;
  onToggleModeMenu: () => void;
  modeMenuRef: React.RefObject<HTMLDivElement>;
  fileInputRef: React.RefObject<HTMLInputElement>;
}

// OPTIMIZATION: 使用 React.memo 并提取静态配置 (rendering-hoist-jsx, rerender-memo)
const MODE_CONFIG = {
  normal: { icon: Sparkles, label: '普通模式', color: 'gray' },
  market: { icon: TrendingUp, label: '市场分析', color: 'blue' },
  selection: { icon: Package, label: '选品策略', color: 'green' },
  ads: { icon: BarChart3, label: '广告优化', color: 'purple' },
  conversion: { icon: Sparkles, label: '转化优化', color: 'orange' },
} as const;

export const WelcomeInput = memo<WelcomeInputProps>(({
  greeting,
  inputValue,
  isGenerating,
  isUploading,
  currentUploadingFile,
  uploadedFiles,
  selectedMode,
  showModeMenu,
  onInputChange,
  onGenerate,
  onFileUpload,
  onRemoveFile,
  onModeChange,
  onToggleModeMenu,
  modeMenuRef,
  fileInputRef,
}) => {
  const currentMode = MODE_CONFIG[selectedMode as keyof typeof MODE_CONFIG];
  const ModeIcon = currentMode.icon;

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

          {/* 上传的文件显示 */}
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
                    onClick={() => onRemoveFile(file.filename)}
                    className="w-5 h-5 flex items-center justify-center bg-gray-400 dark:bg-gray-600 hover:bg-gray-500 dark:hover:bg-gray-500 rounded-full transition-colors flex-shrink-0"
                  >
                    <X className="w-3 h-3 text-white" />
                  </button>
                </div>
              ))}
            </div>
          )}

          <textarea
            className="w-full bg-transparent border-none focus:ring-0 focus:outline-none resize-none text-lg placeholder-gray-400 dark:placeholder-gray-500 text-gray-700 dark:text-gray-200 transition-colors h-16 relative z-10"
            placeholder="和 CogniMark 说点什么"
            value={inputValue}
            onChange={(e) => onInputChange(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                onGenerate();
              }
            }}
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
                onChange={onFileUpload}
                className="hidden"
                disabled={isUploading}
              />

              {/* 功能模式选择器 */}
              <div className="relative" ref={modeMenuRef}>
                <button
                  onClick={onToggleModeMenu}
                  className="flex items-center gap-2 px-3 py-1.5 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-full cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors shadow-sm"
                >
                  <ModeIcon className={cn("w-4 h-4", selectedMode === 'normal' ? "text-gray-900 dark:text-white" : `text-${currentMode.color}-500`)} />
                  <span className={cn("text-sm font-medium", selectedMode === 'normal' ? "text-gray-700 dark:text-gray-200" : `text-${currentMode.color}-600 dark:text-${currentMode.color}-400`)}>
                    {currentMode.label}
                  </span>
                  <ChevronDown className={cn("w-3 h-3 text-gray-500 transition-transform", showModeMenu && "rotate-180")} />
                </button>

                {/* 下拉菜单 */}
                {showModeMenu && (
                  <div className="absolute top-full mt-2 left-0 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-lg overflow-hidden z-50 min-w-[180px]">
                    {Object.entries(MODE_CONFIG).map(([key, config]) => {
                      const Icon = config.icon;
                      return (
                        <button
                          key={key}
                          onClick={() => {
                            onModeChange(key);
                            onToggleModeMenu();
                          }}
                          className={cn(
                            "w-full flex items-center gap-2 px-4 py-2.5 hover:bg-gray-50 dark:hover:bg-gray-700 text-sm transition-colors text-left",
                            selectedMode === key
                              ? `bg-indigo-50 dark:bg-indigo-900/20 text-${config.color}-600 dark:text-${config.color}-400`
                              : "text-gray-700 dark:text-gray-200"
                          )}
                        >
                          <Icon className={cn("w-4 h-4", key === 'normal' ? "" : `text-${config.color}-500`)} />
                          {config.label}
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>

              <div className="flex items-center gap-2 px-3 py-1.5 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-full cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors shadow-sm">
                <Globe className="w-4 h-4 text-gray-900 dark:text-white" />
                <span className="text-sm font-medium text-gray-700 dark:text-gray-200">搜索</span>
              </div>
            </div>

            {/* Right Actions: Send/Stop Button */}
            {isGenerating ? (
              <button
                className="w-10 h-10 flex items-center justify-center bg-red-600 text-white rounded-full hover:bg-red-700 transition-all"
                title="停止生成"
              >
                <X className="w-5 h-5" />
              </button>
            ) : (
              <button
                onClick={onGenerate}
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
});

WelcomeInput.displayName = 'WelcomeInput';
