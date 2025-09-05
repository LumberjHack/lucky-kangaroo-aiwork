import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { motion } from 'framer-motion';

// Store
import { RootState } from '../../store';
import { selectIsAuthenticated, selectUser } from '../../store/slices/authSlice';

interface PublicRouteProps {
  children: React.ReactNode;
  redirectTo?: string;
  allowAuthenticated?: boolean;
}

const PublicRoute: React.FC<PublicRouteProps> = ({
  children,
  redirectTo = '/dashboard',
  allowAuthenticated = false
}) => {
  const location = useLocation();
  const isAuthenticated = useSelector(selectIsAuthenticated);
  const user = useSelector(selectUser);

  // Redirection si déjà authentifié et que l'authentification n'est pas autorisée
  if (isAuthenticated && !allowAuthenticated) {
    // Vérifier s'il y a une route de destination spécifique
    const from = location.state?.from?.pathname;
    const redirectPath = from || redirectTo;

    return (
      <Navigate
        to={redirectPath}
        replace
      />
    );
  }

  // Affichage du contenu public avec animation
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

export default PublicRoute;
