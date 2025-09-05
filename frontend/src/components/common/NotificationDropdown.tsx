import React from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Bell, 
  MessageSquare, 
  Package, 
  RefreshCw, 
  Star, 
  AlertTriangle,
  CheckCircle,
  Info,
  X,
  Settings
} from 'lucide-react';

// Types
import { Notification as NotificationType } from '../../types';

interface NotificationDropdownProps {
  notifications: NotificationType[];
  onClose: () => void;
}

const NotificationDropdown: React.FC<NotificationDropdownProps> = ({ 
  notifications, 
  onClose 
}) => {
  // Fonction pour obtenir l'icône selon le type de notification
  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'exchange_request':
        return <RefreshCw className="w-5 h-5 text-blue-600" />;
      case 'exchange_accepted':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'exchange_rejected':
        return <X className="w-5 h-5 text-red-600" />;
      case 'message_received':
        return <MessageSquare className="w-5 h-5 text-purple-600" />;
      case 'listing_viewed':
        return <Package className="w-5 h-5 text-orange-600" />;
      case 'listing_liked':
        return <Star className="w-5 h-5 text-yellow-600" />;
      case 'system_update':
        return <Info className="w-5 h-5 text-gray-600" />;
      case 'payment_success':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'payment_failed':
        return <AlertTriangle className="w-5 h-5 text-red-600" />;
      default:
        return <Bell className="w-5 h-5 text-gray-600" />;
    }
  };

  // Fonction pour obtenir la couleur de fond selon le type
  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'exchange_accepted':
      case 'payment_success':
        return 'bg-green-50 border-green-200';
      case 'exchange_rejected':
      case 'payment_failed':
        return 'bg-red-50 border-red-200';
      case 'exchange_request':
        return 'bg-blue-50 border-blue-200';
      case 'message_received':
        return 'bg-purple-50 border-purple-200';
      case 'listing_viewed':
      case 'listing_liked':
        return 'bg-orange-50 border-orange-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  // Fonction pour formater la date
  const formatNotificationDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) {
      return 'À l\'instant';
    } else if (diffInHours < 24) {
      return `Il y a ${diffInHours}h`;
    } else {
      const diffInDays = Math.floor(diffInHours / 24);
      return `Il y a ${diffInDays}j`;
    }
  };

  // Notifications non lues
  const unreadNotifications = notifications.filter(n => !n.is_read);
  const readNotifications = notifications.filter(n => n.is_read);

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: -10 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: -10 }}
        transition={{ duration: 0.15 }}
        className="absolute right-0 mt-2 w-96 bg-white rounded-xl shadow-xl border border-gray-200 py-2 z-50"
      >
        {/* Header */}
        <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-gray-900">Notifications</h3>
            <p className="text-xs text-gray-500">
              {unreadNotifications.length} non lue{unreadNotifications.length > 1 ? 's' : ''}
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <Link
              to="/notifications"
              onClick={onClose}
              className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
              title="Voir toutes les notifications"
            >
              <Settings className="w-4 h-4" />
            </Link>
            <button
              onClick={onClose}
              className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
              title="Fermer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Notifications non lues */}
        {unreadNotifications.length > 0 && (
          <div className="py-2">
            <div className="px-4 py-2">
              <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                Non lues
              </h4>
            </div>
            {unreadNotifications.slice(0, 3).map((notification) => (
              <motion.div
                key={notification.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className={`mx-4 mb-2 p-3 rounded-lg border ${getNotificationColor(notification.notification_type)}`}
              >
                <div className="flex items-start space-x-3">
                  {getNotificationIcon(notification.notification_type)}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 mb-1">
                      {notification.title}
                    </p>
                    <p className="text-xs text-gray-600 mb-2">
                      {notification.message}
                    </p>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-500">
                        {formatNotificationDate(notification.created_at)}
                      </span>
                      <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {/* Notifications récentes lues */}
        {readNotifications.length > 0 && (
          <div className="py-2">
            <div className="px-4 py-2">
              <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                Récentes
              </h4>
            </div>
            {readNotifications.slice(0, 2).map((notification) => (
              <motion.div
                key={notification.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="mx-4 mb-2 p-3 rounded-lg border border-gray-200 bg-white hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-start space-x-3">
                  {getNotificationIcon(notification.notification_type)}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-700 mb-1">
                      {notification.title}
                    </p>
                    <p className="text-xs text-gray-500 mb-2">
                      {notification.message}
                    </p>
                    <span className="text-xs text-gray-400">
                      {formatNotificationDate(notification.created_at)}
                    </span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {/* Aucune notification */}
        {notifications.length === 0 && (
          <div className="px-4 py-8 text-center">
            <Bell className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-sm text-gray-500">Aucune notification</p>
            <p className="text-xs text-gray-400">Vous serez notifié des nouvelles activités</p>
          </div>
        )}

        {/* Footer */}
        {notifications.length > 0 && (
          <div className="px-4 py-3 border-t border-gray-100">
            <Link
              to="/notifications"
              onClick={onClose}
              className="block w-full text-center text-sm text-primary-600 hover:text-primary-700 font-medium py-2 rounded-lg hover:bg-primary-50 transition-colors"
            >
              Voir toutes les notifications
            </Link>
          </div>
        )}
      </motion.div>
    </AnimatePresence>
  );
};

export default NotificationDropdown;
