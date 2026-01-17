import { ArrowUpRight, ArrowDownRight, LucideIcon } from 'lucide-react';
import { cn } from '../../utils/cn';

interface StatCardProps {
  title: string;
  value: string | number;
  trend: number; // Percentage
  icon: LucideIcon;
  trendLabel?: string;
}

export default function StatCard({ title, value, trend, icon: Icon, trendLabel = "vs last month" }: StatCardProps) {
  const isPositive = trend >= 0;

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm hover:shadow-md transition-all duration-300">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{title}</p>
          <h3 className="text-2xl font-bold text-gray-900 dark:text-white mt-2">{value}</h3>
        </div>
        <div className="p-2 bg-indigo-50 dark:bg-indigo-900/50 rounded-lg">
          <Icon className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
        </div>
      </div>
      
      <div className="mt-4 flex items-center gap-2">
        <span className={cn(
          "flex items-center text-sm font-medium",
          isPositive ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"
        )}>
          {isPositive ? <ArrowUpRight className="w-4 h-4 mr-1" /> : <ArrowDownRight className="w-4 h-4 mr-1" />}
          {Math.abs(trend)}%
        </span>
        <span className="text-sm text-gray-400 dark:text-gray-500">{trendLabel}</span>
      </div>
    </div>
  );
}
