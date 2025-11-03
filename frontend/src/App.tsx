import { Routes, Route } from 'react-router-dom';
import MainLayout from './components/layout/MainLayout';
import DashboardPage from './pages/DashboardPage';
import MachinesPage from './pages/MachinesPage';
import AlertsPage from './pages/AlertsPage';
import ChatPage from './pages/ChatPage';
import './App.css';

/**
 * Main Application Component for Factory Agent
 *
 * PR12: Added routing infrastructure with MainLayout and page components
 * - React Router v6 with BrowserRouter (configured in main.tsx)
 * - MainLayout with responsive AppBar and Drawer navigation
 * - Route definitions for Dashboard, Machines, Alerts, and Chat pages
 * - Placeholder pages for future feature implementation
 *
 * Future PRs will enhance pages with:
 * - PR13: Dashboard visualizations (metrics, charts, OEE gauges)
 * - PR14: Machine status cards and alert management
 * - PR15: AI Chat interface with Azure OpenAI integration
 * - PR16: Authentication with Azure AD
 * - PR17: Deployment and CI/CD
 */
function App() {
  return (
    <Routes>
      {/* Main layout route with nested child routes */}
      <Route path="/" element={<MainLayout />}>
        {/* Index route - Dashboard */}
        <Route index element={<DashboardPage />} />

        {/* Machines route */}
        <Route path="machines" element={<MachinesPage />} />

        {/* Alerts route */}
        <Route path="alerts" element={<AlertsPage />} />

        {/* AI Chat route */}
        <Route path="chat" element={<ChatPage />} />
      </Route>
    </Routes>
  );
}

export default App;
