import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  Search, 
  Plus, 
  MessageCircle, 
  User, 
  X
} from 'lucide-react';
import { useSelector, useDispatch } from 'react-redux';
import { selectIsAuthenticated, selectUser, logout } from '../../store/slices/authSlice';

interface MobileMenuProps {
  isAuthenticated: boolean;
  user?: any;
  onClose: () => void;
}

export default function MobileMenu({ isAuthenticated, user, onClose }: MobileMenuProps) {
  const location = useLocation();
  const dispatch = useDispatch();
  const currentUser = user || useSelector(selectUser);

  const handleLogout = () => {
    dispatch(logout());
    onClose();
  };

  const navigationItems = [
    { path: '/', icon: Home, label: 'Accueil' },
    { path: '/search', icon: Search, label: 'Rechercher' },
    { path: '/create-listing', icon: Plus, label: 'Créer' },
    { path: '/chat', icon: MessageCircle, label: 'Messages' },
  ];

  const userItems = [
    { path: '/profile', icon: User, label: 'Profil' },
  ];

  return (
    <div className="lg:hidden">
      {/* Overlay */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 z-40"
        onClick={onClose}
      />
      
      {/* Menu */}
      <div className="fixed top-0 right-0 h-full w-80 max-w-[85vw] bg-white dark:bg-gray-800 shadow-xl z-50 transform transition-transform duration-300 ease-in-out">
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Menu
            </h2>
            <button
              onClick={onClose}
              className="p-1 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={onClose}
                  className={`
                    flex items-center space-x-3 px-3 py-3 rounded-lg transition-colors
                    ${isActive 
                      ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300' 
                      : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
                    }
                  `}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* Section utilisateur */}
          {isAuthenticated && currentUser && (
            <div className="border-t border-gray-200 dark:border-gray-700 p-4 space-y-2">
              <div className="flex items-center space-x-3 px-3 py-2">
                <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-medium">
                    {currentUser.first_name?.[0] || currentUser.email[0].toUpperCase()}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                    {currentUser.first_name ? `${currentUser.first_name} ${currentUser.last_name || ''}`.trim() : currentUser.email}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                    {currentUser.email}
                  </p>
                </div>
              </div>

              {userItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={onClose}
                    className={`
                      flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors
                      ${isActive 
                        ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300' 
                        : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
                      }
                    `}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="font-medium">{item.label}</span>
                  </Link>
                );
              })}

              <button
                onClick={handleLogout}
                className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900 transition-colors"
              >
                <User className="w-5 h-5" />
                <span className="font-medium">Déconnexion</span>
              </button>
            </div>
          )}

          {/* Actions pour utilisateurs non connectés */}
          {!isAuthenticated && (
            <div className="border-t border-gray-200 dark:border-gray-700 p-4 space-y-2">
              <Link
                to="/login"
                onClick={onClose}
                className="block w-full text-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                Se connecter
              </Link>
              <Link
                to="/register"
                onClick={onClose}
                className="block w-full text-center px-4 py-2 border border-green-600 text-green-600 rounded-lg hover:bg-green-50 dark:hover:bg-green-900 transition-colors"
              >
                S'inscrire
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}