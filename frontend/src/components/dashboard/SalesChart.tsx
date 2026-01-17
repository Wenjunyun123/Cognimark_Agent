import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { SalesTrend } from '../../types';

interface SalesChartProps {
  data: SalesTrend[];
}

export default function SalesChart({ data }: SalesChartProps) {
  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm h-[400px] transition-colors duration-300">
      <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-6">销售趋势分析</h3>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" className="dark:stroke-gray-700" />
          <XAxis 
            dataKey="month" 
            axisLine={false} 
            tickLine={false} 
            tick={{ fill: '#6b7280', fontSize: 12 }} 
            dy={10}
          />
          <YAxis 
            axisLine={false} 
            tickLine={false} 
            tick={{ fill: '#6b7280', fontSize: 12 }}
            tickFormatter={(value) => `$${value / 1000}k`}
          />
          <Tooltip 
            cursor={{ fill: 'transparent' }}
            contentStyle={{ 
              borderRadius: '8px', 
              border: 'none', 
              boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
              backgroundColor: 'var(--tooltip-bg, #fff)',
              color: 'var(--tooltip-text, #000)'
            }}
            // Recharts doesn't support CSS variables easily in contentStyle object directly for dynamic theme without forcing update,
            // but we can use simple hardcoded style or just let it be light for now as it's a popup.
            // A better way is a custom content component. For now, let's keep it simple.
          />
          <Legend iconType="circle" wrapperStyle={{ paddingTop: '20px' }} />
          <Bar 
            dataKey="sales" 
            name="销售额 (Sales)" 
            fill="#4f46e5" 
            radius={[4, 4, 0, 0]} 
            maxBarSize={50}
          />
          <Bar 
            dataKey="profit" 
            name="净利润 (Profit)" 
            fill="#c7d2fe" 
            radius={[4, 4, 0, 0]} 
            maxBarSize={50}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
