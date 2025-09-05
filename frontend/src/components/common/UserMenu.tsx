import React from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  User, 
  Settings, 
  LogOut, 
  Heart, 
  Package, 
  MessageCircle, 
  Bell,
  Shield,
  Crown,
  HelpCircle
} from 'lucide-react';

// Types
import { User as UserType } from '../../types';

interface UserMenuProps {
  user: UserType | null;
  onClose: () => void;
  onLogout: () => void;
}

const UserMenu: React.FC<UserMenuProps> = ({ user, onClose, onLogout }) => {
  const menuItems = [
    {
      icon: User,
      label: 'Mon Profil',
      href: '/profile',
      description: 'Gérer vos informations'
    },
    {
      icon: Package,
      label: 'Mes Annonces',
      href: '/my-listings',
      description: 'Voir et modifier vos annonces'
    },
    {
      icon: Heart,
      label: 'Favoris',
      href: '/favorites',
      description: 'Vos objets favoris'
    },
    {
      icon: MessageCircle,
      label: 'Messages',
      href: '/chat',
      description: 'Conversations en cours'
    },
    {
      icon: Bell,
      label: 'Notifications',
      href: '/notifications',
      description: 'Paramètres de notification'
    },
    {
      icon: Settings,
      label: 'Paramètres',
      href: '/settings',
      description: 'Configuration du compte'
    },
    {
      icon: Shield,
      label: 'Sécurité',
      href: '/security',
      description: 'Sécurité et confidentialité'
    },
    {
      icon: HelpCircle,
      label: 'Aide',
      href: '/help',
      description: 'Support et FAQ'
    }
  ];

  const handleLogout = () => {
    onLogout();
    onClose();
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: -10 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: -10 }}
        transition={{ duration: 0.15 }}
        className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-xl border border-gray-200 py-2 z-50"
      >
        {/* Header utilisateur */}
        <div className="px-4 py-3 border-b border-gray-100">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-br from-primary-400 to-secondary-500 rounded-full flex items-center justify-center text-white font-semibold text-lg">
              {user?.first_name?.[0] || user?.username?.[0] || 'U'}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-gray-900 truncate">
                {user?.first_name && user?.last_name 
                  ? `${user.first_name} ${user.last_name}`
                  : user?.username || 'Utilisateur'
                }
              </p>
              <p className="text-xs text-gray-500 truncate">
                {user?.email}
              </p>
            </div>
          </div>
          
          {/* Score de confiance */}
          <div className="mt-3 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Shield className="w-4 h-4 text-primary-600" />
              <span className="text-xs text-gray-600">Score de confiance</span>
            </div>
            <div className="flex items-center space-x-1">
              <span className="text-sm font-semibold text-primary-600">
                {user?.trust_score || 0}%
              </span>
              {user?.is_premium && (
                <Crown className="w-4 h-4 text-accent-500" />
              )}
            </div>
          </div>
        </div>

        {/* Menu items */}
        <div className="py-2">
          {menuItems.map((item, index) => (
            <motion.div
              key={item.label}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.2, delay: index * 0.05 }}
            >
              <Link
                to={item.href}
                onClick={onClose}
                className="flex items-center space-x-3 px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 hover:text-primary-600 transition-colors group"
              >
                <div className="w-5 h-5 text-gray-400 group-hover:text-primary-600 transition-colors">
                  <item.icon size={20} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium">{item.label}</p>
                  <p className="text-xs text-gray-500 truncate">{item.description}</p>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>

        {/* Footer avec déconnexion */}
        <div className="border-t border-gray-100 pt-2">
          <button
            onClick={handleLogout}
            className="flex items-center space-x-3 w-full px-4 py-3 text-sm text-red-600 hover:bg-red-50 transition-colors group"
          >
            <div className="w-5 h-5 text-red-400 group-hover:text-red-600 transition-colors">
              <LogOut size={20} />
            </div>
            <span className="font-medium">Se déconnecter</span>
          </button>
        </div>

        {/* Version et info */}
        <div className="px-4 py-2 border-t border-gray-100">
          <div className="flex items-center justify-between text-xs text-gray-400">
            <span>Lucky Kangaroo v1.0.0</span>
            <span>© 2024</span>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

export default UserMenu;
