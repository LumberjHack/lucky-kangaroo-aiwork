import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Menu, 
  X, 
  Search, 
  Bell, 
  User, 
  LogOut, 
  Settings,
  Plus,
  Heart,
  MessageCircle,
  BarChart3
} from 'lucide-react';

// Store
import { AppDispatch, RootState } from '../../store';
import { logoutUser } from '../../store/slices/authSlice';
import { selectNotifications } from '../../store/slices/notificationsSlice';

// Composants
import UserMenu from '../common/UserMenu';
import NotificationDropdown from '../common/NotificationDropdown';
import CurrencySelector from '../common/CurrencySelector';

// Types
import { User as UserType } from '../../types';

interface HeaderProps {
  isAuthenticated: boolean;
  user: UserType | null;
  scrolled: boolean;
  onMenuToggle: () => void;
  onSidebarToggle: () => void;
}

const Header: React.FC<HeaderProps> = ({
  isAuthenticated,
  user,
  scrolled,
  onMenuToggle,
  onSidebarToggle
}) => {
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [notificationDropdownOpen, setNotificationDropdownOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const location = useLocation();
  
  const notifications = useSelector(selectNotifications);
  const unreadCount = notifications.items.filter(n => !n.is_read).length;

  // Navigation items
  const navigationItems = [
    { name: 'Accueil', path: '/', icon: '🏠' },
    { name: 'Rechercher', path: '/search', icon: '🔍' },
    { name: 'Annonces', path: '/listings', icon: '📋' },
    { name: 'Échanges', path: '/exchanges', icon: '🔄' },
    { name: 'Chat', path: '/chat', icon: '💬' },
  ];

  // Gestion de la recherche
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  // Gestion de la déconnexion
  const handleLogout = async () => {
    try {
      await dispatch(logoutUser()).unwrap();
      navigate('/');
      setUserMenuOpen(false);
    } catch (error) {
      console.error('Erreur lors de la déconnexion:', error);
    }
  };

  // Vérification si l'item est actif
  const isActiveRoute = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <header
      className={`sticky top-0 z-50 transition-all duration-300 ${
        scrolled
          ? 'bg-white/95 backdrop-blur-md shadow-lg border-b border-gray-200'
          : 'bg-white/80 backdrop-blur-sm'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo et navigation principale */}
          <div className="flex items-center space-x-8">
            {/* Bouton menu mobile */}
            <button
              onClick={onMenuToggle}
              className="lg:hidden p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors"
              aria-label="Menu principal"
            >
              <Menu size={20} />
            </button>

            {/* Logo */}
            <Link to="/" className="flex items-center space-x-3 group">
              <motion.div
                whileHover={{ scale: 1.05 }}
                className="w-10 h-10 bg-gradient-to-br from-primary-500 to-secondary-600 rounded-full flex items-center justify-center shadow-lg"
              >
                <span className="text-white text-xl font-bold">🦘</span>
              </motion.div>
              <div className="hidden sm:block">
                <h1 className="text-xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
                  Lucky Kangaroo
                </h1>
                <p className="text-xs text-gray-500">Échange Collaboratif</p>
              </div>
            </Link>

            {/* Navigation desktop */}
            <nav className="hidden lg:flex items-center space-x-1">
              {navigationItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 flex items-center space-x-2 ${
                    isActiveRoute(item.path)
                      ? 'bg-primary-100 text-primary-700 border-b-2 border-primary-500'
                      : 'text-gray-600 hover:text-primary-600 hover:bg-primary-50'
                  }`}
                >
                  <span>{item.icon}</span>
                  <span>{item.name}</span>
                </Link>
              ))}
            </nav>
          </div>

          {/* Barre de recherche */}
          <div className="hidden md:flex flex-1 max-w-md mx-8">
            <form onSubmit={handleSearch} className="w-full">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="text"
                  placeholder="Rechercher des objets..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
                />
              </div>
            </form>
          </div>

          {/* Actions utilisateur */}
          <div className="flex items-center space-x-4">
            {/* Sélecteur de devise */}
            <CurrencySelector />

            {isAuthenticated ? (
              <>
                {/* Bouton créer annonce */}
                <Link
                  to="/listings/create"
                  className="hidden sm:flex items-center space-x-2 px-4 py-2 bg-accent-500 text-gray-900 rounded-lg hover:bg-accent-600 transition-colors font-medium"
                >
                  <Plus size={16} />
                  <span>Créer</span>
                </Link>

                {/* Notifications */}
                <div className="relative">
                  <button
                    onClick={() => setNotificationDropdownOpen(!notificationDropdownOpen)}
                    className="relative p-2 text-gray-600 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                    aria-label="Notifications"
                  >
                    <Bell size={20} />
                    {unreadCount > 0 && (
                      <span className="absolute -top-1 -right-1 bg-error-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                        {unreadCount > 9 ? '9+' : unreadCount}
                      </span>
                    )}
                  </button>
                  
                  <AnimatePresence>
                    {notificationDropdownOpen && (
                      <NotificationDropdown
                        notifications={notifications.items}
                        onClose={() => setNotificationDropdownOpen(false)}
                      />
                    )}
                  </AnimatePresence>
                </div>

                {/* Menu utilisateur */}
                <div className="relative">
                  <button
                    onClick={() => setUserMenuOpen(!userMenuOpen)}
                    className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-100 transition-colors"
                    aria-label="Menu utilisateur"
                  >
                    <div className="w-8 h-8 bg-gradient-to-br from-primary-400 to-secondary-500 rounded-full flex items-center justify-center text-white font-semibold">
                      {user?.first_name?.[0] || user?.username?.[0] || 'U'}
                    </div>
                    <div className="hidden sm:block text-left">
                      <div className="text-sm font-medium text-gray-900">
                        {user?.first_name || user?.username || 'Utilisateur'}
                      </div>
                      <div className="text-xs text-gray-500">
                        Score: {user?.trust_score || 0}%
                      </div>
                    </div>
                  </button>

                  <AnimatePresence>
                    {userMenuOpen && (
                      <UserMenu
                        user={user}
                        onClose={() => setUserMenuOpen(false)}
                        onLogout={handleLogout}
                      />
                    )}
                  </AnimatePresence>
                </div>

                {/* Bouton sidebar pour desktop */}
                <button
                  onClick={onSidebarToggle}
                  className="hidden xl:block p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                  aria-label="Basculer la sidebar"
                >
                  <BarChart3 size={20} />
                </button>
              </>
            ) : (
              <>
                {/* Boutons de connexion/inscription */}
                <Link
                  to="/login"
                  className="px-4 py-2 text-primary-600 border border-primary-600 rounded-lg hover:bg-primary-50 transition-colors font-medium"
                >
                  Connexion
                </Link>
                <Link
                  to="/register"
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
                >
                  Inscription
                </Link>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Barre de recherche mobile */}
      <div className="md:hidden border-t border-gray-200 bg-white">
        <div className="px-4 py-3">
          <form onSubmit={handleSearch}>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Rechercher des objets..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </form>
        </div>
      </div>
    </header>
  );
};

export default Header;
