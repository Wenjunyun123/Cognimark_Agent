import { useState } from 'react';
import { X, Lock, User, ArrowRight, Smartphone, Mail, QrCode } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
}

type AuthMode = 'login' | 'register';
type RegisterMethod = 'phone' | 'wechat' | 'qq' | 'google';

export default function LoginModal({ isOpen, onClose }: LoginModalProps) {
  const [mode, setMode] = useState<AuthMode>('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const { login, register } = useAuth();

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    // Simulate network delay
    setTimeout(() => {
      try {
        if (mode === 'register') {
          if (username.length < 3) {
            throw new Error('用户名至少需要3个字符');
          }
          if (password.length < 6) {
            throw new Error('密码至少需要6个字符');
          }
          if (password !== confirmPassword) {
            throw new Error('两次输入的密码不一致');
          }
          register(username);
        } else {
          login(username);
        }
        
        setIsLoading(false);
        onClose();
      } catch (err: any) {
        setError(err.message);
        setIsLoading(false);
      }
    }, 1000);
  };

  const handleSocialLogin = (platform: string) => {
    // Mock social login
    setIsLoading(true);
    setTimeout(() => {
      try {
        const socialUser = `${platform}_user_${Math.floor(Math.random() * 1000)}`;
        // For demo, we just register them if not exists, or login
        try {
          login(socialUser);
        } catch {
          register(socialUser);
        }
        onClose();
      } finally {
        setIsLoading(false);
      }
    }, 1500);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-fadeIn">
      <div className="bg-white dark:bg-gray-900 rounded-2xl w-full max-w-md shadow-2xl overflow-hidden animate-scaleIn relative">
        <button 
          onClick={onClose}
          className="absolute right-4 top-4 p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors z-10"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="p-8">
          <div className="text-center mb-8">
            <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 rounded-xl flex items-center justify-center mx-auto mb-4">
              <User className="w-6 h-6" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              {mode === 'login' ? '欢迎回来' : '创建账号'}
            </h2>
            <p className="text-gray-500 dark:text-gray-400 text-sm">
              {mode === 'login' ? '登录您的 CogniMark 账号' : '注册 CogniMark 开启智能营销之旅'}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm rounded-lg text-center animate-fadeIn">
                {error}
              </div>
            )}

            <div className="space-y-1">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300 ml-1">用户名/手机号</label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg pl-10 pr-4 py-2.5 text-gray-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition-all"
                  placeholder="请输入用户名"
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300 ml-1">密码</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg pl-10 pr-4 py-2.5 text-gray-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition-all"
                  placeholder="请输入密码"
                />
              </div>
            </div>

            {mode === 'register' && (
              <div className="space-y-1 animate-fadeIn">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300 ml-1">确认密码</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg pl-10 pr-4 py-2.5 text-gray-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition-all"
                    placeholder="请再次输入密码"
                  />
                </div>
              </div>
            )}

            {mode === 'login' && (
              <div className="flex items-center justify-between text-sm pt-2">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" className="rounded text-green-600 focus:ring-green-500 border-gray-300 dark:border-gray-600 dark:bg-gray-700" />
                  <span className="text-gray-600 dark:text-gray-400">记住我</span>
                </label>
                <button type="button" className="text-green-600 dark:text-green-400 hover:underline">
                  忘记密码？
                </button>
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-2.5 rounded-lg flex items-center justify-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed mt-6"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  {mode === 'login' ? '登录' : '注册'}
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-8 relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200 dark:border-gray-700"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white dark:bg-gray-900 text-gray-500">
                其他登录方式
              </span>
            </div>
          </div>

          <div className="mt-6 grid grid-cols-4 gap-4">
            <button 
              onClick={() => handleSocialLogin('wechat')}
              className="flex items-center justify-center p-2.5 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              title="微信登录"
            >
              <div className="w-5 h-5 text-green-600">
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M17.49 10.43c0-3.13-2.88-5.68-6.43-5.68-3.54 0-6.42 2.55-6.42 5.68 0 3.13 2.88 5.68 6.42 5.68.8 0 1.56-.13 2.27-.37l.48.27 1.83 1 .25-.13-.53-1.63.13-.23c1.32-1.28 2-2.9 2-4.59zM6.92 8.76c-.39 0-.71-.32-.71-.71 0-.39.32-.71.71-.71s.71.32.71.71c0 .39-.32.71-.71.71zm6.2 0c-.39 0-.71-.32-.71-.71 0-.39.32-.71.71-.71.39 0 .71.32.71.71 0 .39-.32.71-.71.71zM24 14.93c0-2.58-2.58-4.68-5.74-4.68-.44 0-.87.05-1.28.13.25.64.38 1.33.38 2.05 0 3.32-3.03 6.02-6.76 6.02-.32 0-.64-.02-.95-.06-.52 1.58-1.93 2.76-3.66 3.03.38.16.78.27 1.2.27.7 0 1.38-.13 2.02-.34l.41.24 1.59.88.22-.12-.46-1.42.12-.2c1.15-1.12 1.76-2.52 1.76-3.99l.01-.01.14.2z"/></svg>
              </div>
            </button>
            <button 
              onClick={() => handleSocialLogin('qq')}
              className="flex items-center justify-center p-2.5 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              title="QQ登录"
            >
              <div className="w-5 h-5 text-[#12B7F5]">
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm2.65-11.49c-.56-.16-1.15-.26-1.75-.29.17-.67.42-1.31.75-1.91.33-.6.74-1.14 1.2-1.61.35-.35.59-.79.67-1.28.08-.49-.03-.99-.32-1.39-.29-.4-.73-.67-1.22-.75-.49-.08-.99.03-1.39.32-.4.29-.67.73-.75 1.22-.08.49.03.99.32 1.39.29.4.73.67 1.22.75.14.02.28.03.42.03.35 0 .69-.09.99-.26-.35.35-.65.75-.9 1.18-.25.43-.45.89-.59 1.37-.46.03-.92.1-1.36.22-.44.12-.86.29-1.25.5-.39.21-.75.47-1.08.77-.33.3-.61.64-.84 1.01-.23.37-.41.77-.53 1.19-.12.42-.18.86-.18 1.3 0 1.66.67 3.16 1.76 4.24 1.09 1.09 2.59 1.76 4.24 1.76 1.66 0 3.16-.67 4.24-1.76 1.09-1.09 1.76-2.59 1.76-4.24 0-.44-.06-.88-.18-1.3-.12-.42-.3-.82-.53-1.19-.23-.37-.51-.71-.84-1.01-.33-.3-.69-.56-1.08-.77-.39-.21-.81-.38-1.25-.5z"/></svg>
              </div>
            </button>
            <button 
              onClick={() => handleSocialLogin('google')}
              className="flex items-center justify-center p-2.5 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              title="Google登录"
            >
              <div className="w-5 h-5 text-red-500">
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12.48 10.92v3.28h7.84c-.24 1.84-.853 3.187-1.787 4.133-1.147 1.147-2.933 2.4-6.053 2.4-4.827 0-8.6-3.893-8.6-8.72s3.773-8.72 8.6-8.72c2.6 0 4.507 1.027 5.907 2.347l2.307-2.307C18.747 1.44 16.133 0 12.48 0 5.867 0 .533 5.347.533 12S5.867 24 12.48 24c3.44 0 6.013-1.147 8.027-3.24 2.053-2.053 2.627-5.053 2.627-7.44 0-.52-.053-1.04-.147-1.547h-10.507z"/></svg>
              </div>
            </button>
            <button 
              onClick={() => handleSocialLogin('mobile')}
              className="flex items-center justify-center p-2.5 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              title="手机号登录"
            >
              <Smartphone className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            </button>
          </div>

          <div className="mt-6 text-center text-sm text-gray-500 dark:text-gray-400">
            {mode === 'login' ? (
              <>
                还没有账号？{' '}
                <button 
                  onClick={() => {
                    setMode('register');
                    setError('');
                  }}
                  className="text-green-600 dark:text-green-400 hover:underline font-medium"
                >
                  立即注册
                </button>
              </>
            ) : (
              <>
                已有账号？{' '}
                <button 
                  onClick={() => {
                    setMode('login');
                    setError('');
                  }}
                  className="text-green-600 dark:text-green-400 hover:underline font-medium"
                >
                  直接登录
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
