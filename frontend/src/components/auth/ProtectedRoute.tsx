import React, { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { motion } from 'framer-motion';

// Store
import { RootState } from '../../store';
import { selectIsAuthenticated, selectUser, selectIsLoading } from '../../store/slices/authSlice';

// Composants
import LoadingSpinner from '../common/LoadingSpinner';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAdmin?: boolean;
  requireVerified?: boolean;
  requirePremium?: boolean;
  redirectTo?: string;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requireAdmin = false,
  requireVerified = false,
  requirePremium = false,
  redirectTo = '/login'
}) => {
  const location = useLocation();
  const isAuthenticated = useSelector(selectIsAuthenticated);
  const user = useSelector(selectUser);
  const isLoading = useSelector(selectIsLoading);

  // Vérification des permissions
  const hasRequiredPermissions = () => {
    if (!user) return false;
    
    if (requireAdmin) {
      return user.is_premium || user.trust_score >= 90;
    }
    
    if (requireVerified) {
      return user.is_verified;
    }
    
    if (requirePremium) {
      return user.is_premium;
    }
    
    return true;
  };

  // Affichage du spinner de chargement
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" text="Vérification de l'authentification..." />
      </div>
    );
  }

  // Redirection si non authentifié
  if (!isAuthenticated) {
    return (
      <Navigate
        to={redirectTo}
        state={{ from: location }}
        replace
      />
    );
  }

  // Redirection si permissions insuffisantes
  if (!hasRequiredPermissions()) {
    let redirectPath = '/';
    let message = '';

    if (requireAdmin) {
      redirectPath = '/dashboard';
      message = 'Accès administrateur requis';
    } else if (requireVerified) {
      redirectPath = '/profile';
      message = 'Vérification du compte requise';
    } else if (requirePremium) {
      redirectPath = '/premium';
      message = 'Compte premium requis';
    }

    // Stocker le message d'erreur pour l'afficher sur la page de destination
    sessionStorage.setItem('accessDeniedMessage', message);

    return (
      <Navigate
        to={redirectPath}
        state={{ 
          from: location,
          accessDenied: true,
          message 
        }}
        replace
      />
    );
  }

  // Affichage du contenu protégé avec animation
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {children}
    </motion.div>
  );
};

export default ProtectedRoute;
