import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import { cn } from '../../utils/cn';

const PAGE_TITLES: Record<string, string> = {
  '/': 'CogniMark',
  '/products': '智能选品',
  '/marketing': '智能营销文案',
  '/settings': '系统设置'
};

export default function Layout() {
  const location = useLocation();
  const currentPath = location.pathname;
  const title = PAGE_TITLES[currentPath] || '跨境电商智能系统';

  const isMarketingPage = currentPath === '/marketing';

  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-gray-900 font-sans text-gray-900 dark:text-gray-100 transition-colors duration-300">
      <Sidebar />
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden bg-white dark:bg-gray-900 transition-colors duration-300">
        <Header title={title} />
        <div className={cn("flex-1 overflow-y-auto scroll-smooth", isMarketingPage ? "p-0" : "p-6 sm:p-8")}>
          <div className={cn("mx-auto w-full animate-fadeIn h-full", isMarketingPage ? "max-w-full" : "max-w-7xl")}>
            <Outlet />
          </div>
        </div>
      </main>
    </div>
  );
}
