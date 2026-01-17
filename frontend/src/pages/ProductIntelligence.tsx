import { useState } from 'react';
import { Search, Filter, Sparkles, Loader2, TrendingUp, DollarSign, Star, ShoppingCart } from 'lucide-react';
import AIInsightCard from '../components/products/AIInsightCard';
import { Product, recommendProducts } from '../services/api';

export default function ProductIntelligence() {
  const [campaignText, setCampaignText] = useState('Summer promotion targeting young professionals in the US. Prefer mid-price, eco-friendly products.');
  const [targetMarket, setTargetMarket] = useState('US');
  const [topK, setTopK] = useState(3);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [products, setProducts] = useState<Product[]>([]);
  const [aiInsight, setAiInsight] = useState<string | null>(null);

  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    setAiInsight(null);
    setProducts([]);
    
    try {
      const result = await recommendProducts({
        campaign_description: campaignText,
        target_market: targetMarket || undefined,
        top_k: topK,
      });
      
      setProducts(result.products);
      setAiInsight(result.explanation);
    } catch (error) {
      console.error('Error:', error);
      setAiInsight('❌ 连接后端失败，请确保 API 服务正在运行 (http://127.0.0.1:8000)');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Campaign Input Section */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm p-6 transition-colors duration-300">
        <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">
          🎯 营销活动描述
        </h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Campaign Description
            </label>
            <textarea
              value={campaignText}
              onChange={(e) => setCampaignText(e.target.value)}
              rows={4}
              className="w-full px-4 py-3 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors duration-300 resize-none"
              placeholder="描述您的营销活动目标、季节、偏好..."
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                目标市场
              </label>
              <select
                value={targetMarket}
                onChange={(e) => setTargetMarket(e.target.value)}
                className="w-full px-4 py-2 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors"
              >
                <option value="">All Markets</option>
                <option value="US">US</option>
                <option value="EU">EU</option>
                <option value="SEA">SEA</option>
                <option value="Global">Global</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                推荐数量: {topK}
              </label>
              <input
                type="range"
                min="1"
                max="5"
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
              />
            </div>

            <div className="flex items-end">
              <button 
                onClick={handleAnalyze}
                disabled={isAnalyzing}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-70 disabled:cursor-not-allowed"
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    分析中...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    AI 智能选品
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* AI Insight */}
      {aiInsight && (
        <AIInsightCard 
          content={aiInsight} 
          onClose={() => setAiInsight(null)} 
        />
      )}

      {/* Products Display */}
      {products.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden transition-colors duration-300">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100">
              ✨ 推荐产品 ({products.length})
            </h3>
          </div>

          <div className="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {products.map((product) => (
              <div
                key={product.product_id}
                className="bg-gradient-to-br from-white to-gray-50 dark:from-gray-800 dark:to-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl p-5 hover:shadow-lg transition-all duration-300 hover:-translate-y-1"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900 dark:text-gray-100 text-sm mb-1">
                      {product.product_id}
                    </h4>
                    <p className="text-xs text-gray-600 dark:text-gray-400 line-clamp-2">
                      {product.title_en}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2 mb-3">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200">
                    {product.category}
                  </span>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                    {product.main_market}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div className="flex items-center gap-1.5 text-gray-700 dark:text-gray-300">
                    <DollarSign className="w-4 h-4 text-green-600" />
                    <span className="font-semibold">${product.price_usd}</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-gray-700 dark:text-gray-300">
                    <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                    <span className="font-semibold">{product.avg_rating}</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-gray-700 dark:text-gray-300">
                    <ShoppingCart className="w-4 h-4 text-blue-600" />
                    <span className="text-xs">{product.monthly_sales}/mo</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-gray-700 dark:text-gray-300">
                    <TrendingUp className="w-4 h-4 text-indigo-600" />
                    <span className="text-xs">Hot</span>
                  </div>
                </div>

                <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                  <p className="text-xs text-gray-500 dark:text-gray-400 line-clamp-2">
                    🏷️ {product.tags}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {!isAnalyzing && products.length === 0 && !aiInsight && (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm p-12 text-center transition-colors duration-300">
          <Sparkles className="w-16 h-16 text-gray-400 dark:text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2">
            开始智能选品
          </h3>
          <p className="text-gray-500 dark:text-gray-400 text-sm">
            输入您的营销活动描述，让 AI 为您推荐最合适的产品
          </p>
        </div>
      )}
    </div>
  );
}
