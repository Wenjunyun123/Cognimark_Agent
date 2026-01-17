import { ScatterChart, Scatter, XAxis, YAxis, ZAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { MarketingRequest } from '../../types';

interface MarketingConfigProps {
  config: MarketingRequest;
  onChange: (config: MarketingRequest) => void;
}

const CUSTOMER_CLUSTERS = [
  { x: 10, y: 300, z: 200, name: '高价值客群', fill: '#4f46e5' },
  { x: 12, y: 280, z: 220, name: '高价值客群', fill: '#4f46e5' },
  { x: 15, y: 250, z: 180, name: '高价值客群', fill: '#4f46e5' },
  { x: 2, y: 50, z: 20, name: '价格敏感客群', fill: '#ef4444' },
  { x: 3, y: 60, z: 25, name: '价格敏感客群', fill: '#ef4444' },
  { x: 1, y: 40, z: 15, name: '价格敏感客群', fill: '#ef4444' },
  { x: 6, y: 150, z: 100, name: '潜力客群', fill: '#f59e0b' },
  { x: 7, y: 160, z: 110, name: '潜力客群', fill: '#f59e0b' },
];

export default function MarketingConfig({ config, onChange }: MarketingConfigProps) {
  
  const handleChange = (field: keyof MarketingRequest, value: string) => {
    onChange({ ...config, [field]: value });
  };

  return (
    <div className="h-full flex flex-col gap-6 overflow-y-auto pr-2">
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
        <h3 className="text-lg font-bold text-gray-900 mb-4">营销参数配置</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">产品名称</label>
            <input
              type="text"
              value={config.productName}
              onChange={(e) => handleChange('productName', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="例如：无线降噪耳机 Pro"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">目标受众特征</label>
            <textarea
              value={config.targetAudience}
              onChange={(e) => handleChange('targetAudience', e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="例如：25-35岁，注重生活品质，经常通勤的白领..."
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">目标语言</label>
              <select
                value={config.language}
                onChange={(e) => handleChange('language', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="zh-CN">简体中文</option>
                <option value="en-US">English</option>
                <option value="es-ES">Español</option>
                <option value="fr-FR">Français</option>
                <option value="de-DE">Deutsch</option>
                <option value="ja-JP">日本語</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">投放平台</label>
              <select
                value={config.platform}
                onChange={(e) => handleChange('platform', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="Instagram">Instagram</option>
                <option value="Facebook">Facebook</option>
                <option value="TikTok">TikTok</option>
                <option value="Email">Email Marketing</option>
                <option value="Amazon">Amazon Listing</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex-1 min-h-[300px]">
        <h3 className="text-lg font-bold text-gray-900 mb-4">客户聚类分析 (K-Means)</h3>
        <div className="h-[250px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" dataKey="x" name="购买频率" unit="次/年" tick={{ fontSize: 12 }} />
              <YAxis type="number" dataKey="y" name="客单价" unit="$" tick={{ fontSize: 12 }} />
              <ZAxis type="number" dataKey="z" range={[60, 400]} name="CLV" unit="$" />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Legend verticalAlign="top" height={36} />
              <Scatter name="高价值客群" data={CUSTOMER_CLUSTERS.filter(c => c.name === '高价值客群')} fill="#4f46e5" />
              <Scatter name="价格敏感客群" data={CUSTOMER_CLUSTERS.filter(c => c.name === '价格敏感客群')} fill="#ef4444" />
              <Scatter name="潜力客群" data={CUSTOMER_CLUSTERS.filter(c => c.name === '潜力客群')} fill="#f59e0b" />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

