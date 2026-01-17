import { useState, useEffect } from 'react';
import { Sun, Moon } from 'lucide-react';

interface HeaderProps {
  title?: string;
}

export default function Header({ title = 'Dashboard' }: HeaderProps) {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    // Check localStorage or system preference
    const storedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (storedTheme === 'dark' || (!storedTheme && prefersDark)) {
      setIsDark(true);
      document.documentElement.classList.add('dark');
    } else {
      setIsDark(false);
      document.documentElement.classList.remove('dark');
    }
  }, []);

  const toggleTheme = () => {
    if (isDark) {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
      setIsDark(false);
    } else {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
      setIsDark(true);
    }
  };

  return (
    <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 h-16 px-8 flex items-center justify-between sticky top-0 z-10 transition-colors duration-300">
      <h1 className="text-xl font-bold text-gray-800 dark:text-white transition-colors duration-300">{title}</h1>
      
      <div className="flex items-center gap-6">
        <button
          onClick={toggleTheme}
          className="p-2 rounded-full text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800 transition-all duration-300 focus:outline-none"
          title={isDark ? "切换到白天模式" : "切换到夜间模式"}
        >
          {isDark ? <Sun className="w-5 h-5 fill-current" /> : <Moon className="w-5 h-5 fill-current" />}
        </button>
      </div>
    </header>
  );
}
