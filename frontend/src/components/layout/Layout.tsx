import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { motion, AnimatePresence } from 'framer-motion';
import { RootState } from '../../store';
import { selectIsAuthenticated, selectUser } from '../../store/slices/authSlice';

// Composants
import Header from './Header';
import Sidebar from './Sidebar';
import Footer from './Footer';
import MobileMenu from './MobileMenu';

// Types
interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  
  const isAuthenticated = useSelector(selectIsAuthenticated);
  const user = useSelector(selectUser);

  // Gestion du scroll pour l'effet de transparence du header
  useEffect(() => {
    const handleScroll = () => {
      const isScrolled = window.scrollY > 10;
      setScrolled(isScrolled);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Fermeture automatique du menu mobile lors du changement de route
  useEffect(() => {
    setMobileMenuOpen(false);
    setSidebarOpen(false);
  }, [window.location.pathname]);

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);
  const toggleMobileMenu = () => setMobileMenuOpen(!mobileMenuOpen);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <Header
        isAuthenticated={isAuthenticated}
        user={user}
        scrolled={scrolled}
        onMenuToggle={toggleMobileMenu}
        onSidebarToggle={toggleSidebar}
      />

      {/* Menu mobile */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <MobileMenu
            isAuthenticated={isAuthenticated}
            user={user}
            onClose={() => setMobileMenuOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Contenu principal */}
      <div className="flex flex-1">
        {/* Sidebar (desktop) */}
        {isAuthenticated && (
          <Sidebar
            isOpen={sidebarOpen}
            onToggle={toggleSidebar}
            user={user}
          />
        )}

        {/* Contenu principal */}
        <main className={`flex-1 transition-all duration-300 ${
          isAuthenticated && sidebarOpen ? 'ml-64' : 'ml-0'
        }`}>
          <div className="container mx-auto px-4 py-6 max-w-7xl">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              {children}
            </motion.div>
          </div>
        </main>
      </div>

      {/* Footer */}
      <Footer />
    </div>
  );
};

export default Layout;
