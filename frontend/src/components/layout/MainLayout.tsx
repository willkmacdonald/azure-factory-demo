import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  Settings,
  AlertTriangle,
  Truck,
  MessageSquare,
  Menu,
  X,
} from 'lucide-react';

interface NavigationItem {
  label: string;
  path: string;
  icon: React.ReactElement;
}

const navigationItems: NavigationItem[] = [
  { label: 'Dashboard', path: '/', icon: <LayoutDashboard className="w-5 h-5" /> },
  { label: 'Machines', path: '/machines', icon: <Settings className="w-5 h-5" /> },
  { label: 'Alerts', path: '/alerts', icon: <AlertTriangle className="w-5 h-5" /> },
  { label: 'Traceability', path: '/traceability', icon: <Truck className="w-5 h-5" /> },
  { label: 'AI Chat', path: '/chat', icon: <MessageSquare className="w-5 h-5" /> },
];

/**
 * MainLayout component - Modern layout with Tailwind CSS and Framer Motion
 *
 * Features:
 * - Responsive sidebar navigation
 * - Mobile hamburger menu
 * - Smooth animations
 * - Dark mode support
 * - Active route highlighting
 */
const MainLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const handleNavigate = (path: string) => {
    navigate(path);
    setIsMobileMenuOpen(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Mobile Menu Button */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-50 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between p-4">
          <h1 className="text-xl font-bold text-gray-900 dark:text-white">
            Factory Agent
          </h1>
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            aria-label="Toggle menu"
          >
            {isMobileMenuOpen ? (
              <X className="w-6 h-6 text-gray-700 dark:text-gray-300" />
            ) : (
              <Menu className="w-6 h-6 text-gray-700 dark:text-gray-300" />
            )}
          </button>
        </div>
      </div>

      {/* Mobile Menu Overlay */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="lg:hidden fixed inset-0 bg-black/50 z-40"
              onClick={() => setIsMobileMenuOpen(false)}
            />
            <motion.aside
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              className="lg:hidden fixed top-0 left-0 bottom-0 w-64 bg-white dark:bg-gray-800 shadow-xl z-50 overflow-y-auto"
            >
              <div className="p-6">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-8">
                  Factory Agent
                </h2>
                <nav className="space-y-2">
                  {navigationItems.map((item) => {
                    const isActive = location.pathname === item.path;
                    return (
                      <button
                        key={item.path}
                        onClick={() => handleNavigate(item.path)}
                        className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                          isActive
                            ? 'bg-blue-600 text-white'
                            : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                        }`}
                      >
                        {item.icon}
                        <span className="font-medium">{item.label}</span>
                      </button>
                    );
                  })}
                </nav>
              </div>
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      {/* Desktop Sidebar */}
      <aside className="hidden lg:block fixed top-0 left-0 bottom-0 w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 overflow-y-auto">
        <div className="p-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-8">
            Factory Agent
          </h2>
          <nav className="space-y-2">
            {navigationItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <motion.button
                  key={item.path}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => handleNavigate(item.path)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  {item.icon}
                  <span className="font-medium">{item.label}</span>
                </motion.button>
              );
            })}
          </nav>
        </div>
      </aside>

      {/* Main Content */}
      <div className="lg:ml-64">
        {/* Mobile top padding */}
        <div className="lg:hidden h-16" />

        {/* Page Content */}
        <Outlet />
      </div>
    </div>
  );
};

export default MainLayout;
