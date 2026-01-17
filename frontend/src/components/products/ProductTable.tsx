import { Star, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { Product } from '../../types';
import { cn } from '../../utils/cn';

interface ProductTableProps {
  products: Product[];
}

export default function ProductTable({ products }: ProductTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm text-left">
        <thead className="text-xs text-gray-500 dark:text-gray-400 uppercase bg-gray-50 dark:bg-gray-900/50 transition-colors duration-300">
          <tr>
            <th className="px-6 py-3">产品名称</th>
            <th className="px-6 py-3">分类</th>
            <th className="px-6 py-3">售价 / 成本</th>
            <th className="px-6 py-3">月销量</th>
            <th className="px-6 py-3">竞争度</th>
            <th className="px-6 py-3">评分</th>
            <th className="px-6 py-3">趋势</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
          {products.map((product) => (
            <tr key={product.id} className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors duration-300">
              <td className="px-6 py-4 font-medium text-gray-900 dark:text-white">{product.name}</td>
              <td className="px-6 py-4 text-gray-500 dark:text-gray-400">{product.category}</td>
              <td className="px-6 py-4">
                <div className="flex flex-col">
                  <span className="text-gray-900 dark:text-white font-medium">${product.price}</span>
                  <span className="text-xs text-gray-400 dark:text-gray-500">Cost: ${product.cost}</span>
                </div>
              </td>
              <td className="px-6 py-4 text-gray-900 dark:text-white">{product.sales.toLocaleString()}</td>
              <td className="px-6 py-4">
                <span className={cn(
                  "px-2.5 py-0.5 rounded-full text-xs font-medium",
                  product.competition === 'High' ? "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300" :
                  product.competition === 'Medium' ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300" :
                  "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300"
                )}>
                  {product.competition}
                </span>
              </td>
              <td className="px-6 py-4">
                <div className="flex items-center gap-1 text-gray-900 dark:text-white">
                  <Star className="w-4 h-4 text-yellow-400 fill-current" />
                  <span>{product.rating}</span>
                </div>
              </td>
              <td className="px-6 py-4">
                {product.trend === 'Up' && <TrendingUp className="w-4 h-4 text-green-500" />}
                {product.trend === 'Down' && <TrendingDown className="w-4 h-4 text-red-500" />}
                {product.trend === 'Stable' && <Minus className="w-4 h-4 text-gray-400" />}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
