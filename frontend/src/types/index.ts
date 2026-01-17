export interface Product {
  id: number;
  name: string;
  category: string; // e.g., "电子产品"
  price: number;
  cost: number;
  sales: number;    // 月销量
  competition: 'High' | 'Medium' | 'Low';
  rating: number;   // 1.0 - 5.0
  trend: 'Up' | 'Stable' | 'Down';
}

export interface MarketingRequest {
  productName: string;
  targetAudience: string;
  language: string; // "English", "Spanish", etc.
  platform: string; // "Instagram", "Email", etc.
}

export interface SalesStats {
  totalGMV: number;
  activeProducts: number;
  marketingROI: number;
  potentialCustomers: number;
  gmvGrowth: number; // percentage
  activeProductsGrowth: number;
  roiGrowth: number;
  customersGrowth: number;
}

export interface SalesTrend {
  month: string;
  sales: number;
  profit: number;
}

export interface CategoryShare {
  name: string;
  value: number;
}

