import { useState, useRef, useEffect } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  ShoppingBag,
  MessageSquareText,
  Settings,
  Search,
  User,
  Users,
  PanelLeftClose,
  PanelLeftOpen,
  MessageSquarePlus,
  MessageSquare,
  Clock,
  Trash2
} from 'lucide-react';
import { SessionManager, ChatSession } from '../../utils/sessionManager';
import { cn } from '../../utils/cn';

// OPTIMIZATION: 提升静态数据到组件外部，避免每次渲染时重新创建 (rendering-hoist-jsx)
const NAV_ITEMS = [
  { path: '/', icon: LayoutDashboard, label: 'CogniMark' },
  { path: '/products', icon: ShoppingBag, label: '智能选品' },
  { path: '/marketing', icon: MessageSquareText, label: '智能营销文案' },
] as const;

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const userMenuRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    loadSessions();
    
    // 监听存储变化
    const handleStorageChange = () => {
      loadSessions();
    };
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [location]);

  const loadSessions = () => {
    const allSessions = SessionManager.getAllSessions();
    setSessions(allSessions.slice(0, 10)); // 只显示最近 10 个
  };

  const deleteSession = (e: React.MouseEvent, sessionId: string) => {
    e.stopPropagation();
    SessionManager.deleteSession(sessionId);
    loadSessions();
  };

  // Close user menu when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setShowUserMenu(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  return (
    <aside 
      className={cn(
        "h-screen flex flex-col sticky top-0 left-0 bg-white dark:bg-gray-900 border-r border-transparent dark:border-gray-800 transition-all duration-300 z-50 shadow-sm",
        collapsed ? "w-[72px]" : "w-64"
      )}
    >
      {/* Logo Area */}
      <div className={cn("flex items-center transition-all duration-300 overflow-hidden", collapsed ? "h-16 justify-center px-2 mb-2" : "h-16 px-4 pt-4 mb-2 -ml-4 -mt-2")}>
         <div className="flex items-center gap-1 text-gray-800 font-bold text-xl overflow-hidden whitespace-nowrap">
           <div className={cn("flex-shrink-0 transition-all duration-300", collapsed ? "w-10 h-10" : "w-[4.25rem] h-[4.25rem]")}>
              <svg viewBox="0 0 800 800" className="w-full h-full fill-current text-black dark:text-white transition-colors duration-300" preserveAspectRatio="xMidYMid meet">
                <g transform="translate(-3.778020,837.600910) scale(0.105185,-0.105185)" stroke="none">
                  <path d="M3554 6009 c-39 -11 -62 -37 -116 -129 l-45 -75 -359 -5 c-368 -5 -380 -7 -415 -47 -9 -10 -132 -216 -273 -457 -215 -369 -256 -445 -256 -478 0 -39 30 -108 78 -180 31 -48 44 -18 -163 -373 -127 -216 -159 -279 -162 -315 -4 -43 3 -58 138 -290 355 -615 384 -663 412 -680 20 -12 58 -19 134 -23 85 -4 109 -9 123 -23 16 -18 55 -84 257 -439 84 -149 114 -181 175 -190 24 -3 269 -5 545 -3 584 3 527 -9 603 128 l47 85 359 5 c337 5 361 6 393 25 29 17 70 80 229 355 107 184 225 389 264 455 83 143 84 154 12 277 -26 46 -47 91 -46 101 0 10 28 62 60 115 33 53 93 156 134 227 42 72 93 159 114 195 45 75 51 137 19 187 -10 15 -121 208 -247 428 -125 220 -234 410 -243 423 -34 48 -60 56 -170 54 -81 -2 -106 0 -118 12 -8 9 -84 136 -167 283 -84 148 -164 283 -178 302 -46 62 -40 61 -599 60 -279 0 -522 -5 -539 -10z m69 -211 c14 -13 69 -99 122 -193 54 -93 205 -359 337 -589 l240 -419 -16 -35 c-10 -19 -63 -114 -120 -211 -159 -273 -206 -357 -206 -370 0 -7 11 -23 25 -36 l24 -25 454 0 c526 0 478 -10 547 115 62 112 67 109 175 -85 32 -58 91 -162 132 -231 40 -69 73 -135 73 -147 0 -12 -9 -31 -20 -42 -20 -20 -33 -20 -708 -20 -535 0 -692 3 -705 13 -9 6 -92 144 -184 306 -93 162 -176 299 -186 305 -21 14 -45 1 -71 -40 -56 -88 -447 -772 -452 -791 -4 -15 6 -41 30 -80 39 -64 44 -93 20 -117 -13 -14 -54 -16 -293 -16 -264 0 -279 1 -296 20 -27 30 -21 64 22 138 22 37 78 132 125 212 47 80 176 303 288 495 111 193 212 360 223 373 l20 22 352 0 c371 0 375 1 375 46 0 12 -91 179 -203 371 -112 191 -217 373 -235 404 -48 84 -54 88 -162 91 -77 2 -95 6 -98 19 -1 9 41 90 94 180 53 90 118 203 145 251 64 113 87 127 132 86z"/>
                  </g>
                </svg>
             </div>
             {/* Solid Font Style for CogniMark */}
               <span 
                 className={cn("font-black text-xl tracking-tight relative z-10 text-gray-900 dark:text-white transition-all duration-300", collapsed ? "opacity-0 w-0" : "opacity-100 w-auto")}
                 style={{ 
                   letterSpacing: '-0.5px',
                   marginLeft: collapsed ? '0' : '-10px', 
                 }}
               >
                 CogniMark
               </span>
           </div>
      </div>

      {/* Top Icons Row (Collapse, New Chat, Temp Chat) */}
      <div className={cn("flex transition-all duration-300", collapsed ? "flex-col items-center gap-6 pt-6" : "items-center gap-3 px-5 mb-2")}>
         <button
          onClick={() => setCollapsed(!collapsed)}
          className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors p-1 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800"
          title={collapsed ? "展开侧边栏" : "收起侧边栏"}
        >
          {collapsed ? <PanelLeftOpen className="w-5 h-5" /> : <PanelLeftClose className="w-5 h-5" />}
        </button>

        <button
           onClick={() => navigate('/?action=new')}
             className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors p-1 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800"
           title="新建会话"
        >
           <MessageSquarePlus className="w-5 h-5" />
        </button>

        {!collapsed && (
         <button
           onClick={() => navigate('/?action=temp')}
           className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors p-1 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800"
           title="临时对话"
        >
           <MessageSquare className="w-5 h-5 border-dashed border-gray-600 dark:border-gray-400 rounded-sm" /> 
        </button>
        )}
      </div>

      {/* Search Bar (Qwen Style) */}
      {!collapsed && (
        <div className="px-4 mb-2 mt-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input 
              type="text" 
              placeholder="搜索" 
              className="w-full bg-[#F2F2F2] dark:bg-gray-800 border-none text-sm placeholder-gray-500 dark:placeholder-gray-400 text-gray-700 dark:text-gray-200 rounded-lg focus:ring-0 pl-9 pr-2 py-2 transition-colors duration-300"
            />
          </div>
        </div>
      )}


      {/* Navigation */}
      <nav className={cn("flex-1 px-2 space-y-1 overflow-y-auto", collapsed ? "hidden" : "")}>
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => cn(
              "flex items-center gap-3 px-3 py-2 rounded-lg transition-colors duration-200 group min-h-[44px]",
              isActive && !location.search
                ? "bg-white dark:bg-gray-800 shadow-sm text-indigo-600 dark:text-indigo-400 font-medium"
                : "text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white"
            )}
          >
            <item.icon className="w-5 h-5 flex-shrink-0" />
            <span className="whitespace-nowrap overflow-hidden transition-all duration-300 text-sm">
              {item.label}
            </span>
          </NavLink>
        ))}

        {/* 历史会话分隔线 */}
        {sessions.length > 0 && (
          <>
            <div className="flex items-center gap-2 px-3 py-2 text-xs text-gray-500 dark:text-gray-400 mt-4">
              <Clock className="w-3 h-3" />
              <span>历史会话</span>
            </div>
            
            {sessions.map((session) => (
              <button
                key={session.id}
                onClick={() => navigate(`/?session=${session.id}`)}
                className={cn(
                  "flex items-center gap-2 px-3 py-2 rounded-lg transition-colors duration-200 group w-full text-left relative",
                  location.search.includes(session.id)
                    ? "bg-white dark:bg-gray-800 shadow-sm text-indigo-600 dark:text-indigo-400" 
                    : "text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white"
                )}
              >
                <MessageSquare className="w-4 h-4 flex-shrink-0" />
                <span className="text-xs truncate flex-1">{session.title}</span>
                <button
                  onClick={(e) => deleteSession(e, session.id)}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-100 dark:hover:bg-red-900/30 rounded transition-opacity"
                  title="删除会话"
                >
                  <Trash2 className="w-3 h-3 text-red-500" />
                </button>
              </button>
            ))}
          </>
        )}
      </nav>

      {/* Bottom User Profile & Menu */}
      <div className={cn("p-4 border-t border-gray-100 dark:border-gray-800 mt-auto relative transition-colors duration-300", collapsed ? "hidden" : "")} ref={userMenuRef}>
        
        {/* User Menu Popup */}
        {showUserMenu && (
          <div className="absolute bottom-full left-4 mb-2 w-56 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden z-30 animate-fadeIn origin-bottom-left">
            <div className="p-1">
              <button className="w-full text-left px-4 py-2.5 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg flex items-center gap-3 transition-colors duration-200">
                <User className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                我的账号
              </button>
              <NavLink 
                to="/settings" 
                className="w-full text-left px-4 py-2.5 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg flex items-center gap-3 transition-colors duration-200"
                onClick={() => setShowUserMenu(false)}
              >
                <Settings className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                设置
              </NavLink>
              <button className="w-full text-left px-4 py-2.5 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg flex items-center gap-3 transition-colors duration-200">
                <Users className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                创建团队
              </button>
            </div>
            <div className="border-t border-gray-100 dark:border-gray-700 p-1">
               <div className="px-4 py-2 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg cursor-pointer transition-colors duration-200">
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-[10px]">W</div>
                    <span className="text-sm text-gray-700 dark:text-gray-200">wenjun you</span>
                  </div>
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
             </div>
           </div>
          </div>
        )}

        {/* User Button */}
        <button 
          onClick={() => setShowUserMenu(!showUserMenu)}
          className="flex items-center gap-3 w-full hover:bg-gray-200 dark:hover:bg-gray-800 p-2 rounded-lg transition-colors duration-200"
        >
          <div className="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-xs flex-shrink-0">
            W
          </div>
            <div className="flex-1 overflow-hidden text-left">
            <p className="text-sm font-medium text-gray-900 dark:text-white truncate">wenjun you</p>
            </div>
        </button>
      </div>
    </aside>
  );
}
