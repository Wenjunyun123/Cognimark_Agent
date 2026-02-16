import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import ProductIntelligence from './pages/ProductIntelligence';
import MarketingCopilot from './pages/MarketingCopilot';
import { AuthProvider } from './contexts/AuthContext';

// Placeholder for Settings page
const Settings = () => <div className="p-4">Settings Page (Coming Soon)</div>;

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="products" element={<ProductIntelligence />} />
            <Route path="marketing" element={<MarketingCopilot />} />
            <Route path="settings" element={<Settings />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
