import { useEffect, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';

// Store
import { AppDispatch, RootState } from '../store';
import { 
  selectIsAuthenticated, 
  selectUser, 
  selectTokens,
  selectError,
  selectIsLoading,
  loginUser,
  registerUser,
  logoutUser,
  refreshUserToken,
  fetchUserProfile,
  clearError
} from '../store/slices/authSlice';

// Services
import AuthService from '../services/authService';

export const useAuth = () => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  
  // Sélecteurs du store
  const isAuthenticated = useSelector(selectIsAuthenticated);
  const user = useSelector(selectUser);
  const tokens = useSelector(selectTokens);
  const error = useSelector(selectError);
  const isLoading = useSelector(selectIsLoading);

  // Vérification de l'état d'authentification au chargement
  const checkAuthStatus = useCallback(() => {
    const token = AuthService.getAccessToken();
    const currentUser = AuthService.getCurrentUser();
    
    if (token && currentUser && !AuthService.isTokenExpired()) {
      // Token valide, récupérer le profil complet
      dispatch(fetchUserProfile());
    } else if (token && AuthService.isTokenExpired()) {
      // Token expiré, essayer de le rafraîchir
      dispatch(refreshUserToken());
    }
  }, [dispatch]);

  // Connexion
  const login = useCallback(async (credentials: { email: string; password: string }) => {
    try {
      await dispatch(loginUser(credentials)).unwrap();
      toast.success('Connexion réussie !');
      navigate('/dashboard');
    } catch (error: any) {
      toast.error(error.message || 'Échec de la connexion');
    }
  }, [dispatch, navigate]);

  // Inscription
  const register = useCallback(async (userData: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    phone_number?: string;
    accept_terms: boolean;
  }) => {
    try {
      await dispatch(registerUser(userData)).unwrap();
      toast.success('Inscription réussie ! Vérifiez votre email.');
      navigate('/dashboard');
    } catch (error: any) {
      toast.error(error.message || 'Échec de l\'inscription');
    }
  }, [dispatch, navigate]);

  // Déconnexion
  const logout = useCallback(async () => {
    try {
      await dispatch(logoutUser()).unwrap();
      toast.success('Déconnexion réussie');
      navigate('/');
    } catch (error: any) {
      console.error('Erreur lors de la déconnexion:', error);
      // Forcer la déconnexion même en cas d'erreur
      AuthService.logout();
      navigate('/');
    }
  }, [dispatch, navigate]);

  // Rafraîchissement du token
  const refreshToken = useCallback(async () => {
    try {
      await dispatch(refreshUserToken()).unwrap();
    } catch (error: any) {
      console.error('Erreur lors du rafraîchissement du token:', error);
      // Token invalide, déconnexion
      logout();
    }
  }, [dispatch, logout]);

  // Récupération du profil
  const fetchProfile = useCallback(async () => {
    if (isAuthenticated && user) {
      try {
        await dispatch(fetchUserProfile()).unwrap();
      } catch (error: any) {
        console.error('Erreur lors de la récupération du profil:', error);
      }
    }
  }, [dispatch, isAuthenticated, user]);

  // Nettoyage des erreurs
  const clearAuthError = useCallback(() => {
    dispatch(clearError());
  }, [dispatch]);

  // Vérification des permissions
  const hasPermission = useCallback((permission: string) => {
    if (!user) return false;
    
    // Logique de vérification des permissions
    switch (permission) {
      case 'admin':
        return user.is_premium || user.trust_score >= 90;
      case 'verified':
        return user.is_verified;
      case 'premium':
        return user.is_premium;
      default:
        return false;
    }
  }, [user]);

  // Vérification de la vérification email
  const isEmailVerified = useCallback(() => {
    return user?.email_verified || false;
  }, [user]);

  // Vérification de la vérification téléphone
  const isPhoneVerified = useCallback(() => {
    return user?.phone_verified || false;
  }, [user]);

  // Vérification du score de confiance
  const getTrustScore = useCallback(() => {
    return user?.trust_score || 0;
  }, [user]);

  // Vérification du statut premium
  const isPremium = useCallback(() => {
    return user?.is_premium || false;
  }, [user]);

  // Vérification de l'expiration premium
  const getPremiumExpiry = useCallback(() => {
    if (!user?.premium_expires_at) return null;
    return new Date(user.premium_expires_at);
  }, [user]);

  // Vérification si le premium a expiré
  const isPremiumExpired = useCallback(() => {
    const expiry = getPremiumExpiry();
    if (!expiry) return false;
    return expiry < new Date();
  }, [getPremiumExpiry]);

  // Vérification de la localisation
  const getUserLocation = useCallback(() => {
    if (!user) return null;
    
    return {
      latitude: user.latitude,
      longitude: user.longitude,
      city: user.city,
      country: user.country,
      postal_code: user.postal_code,
      address: user.address
    };
  }, [user]);

  // Vérification des préférences de notification
  const getNotificationPreferences = useCallback(() => {
    if (!user) return null;
    
    return {
      email: user.email_notifications,
      push: user.push_notifications,
      sms: user.sms_notifications,
      whatsapp: user.whatsapp_notifications
    };
  }, [user]);

  // Vérification des préférences de langue et devise
  const getPreferences = useCallback(() => {
    if (!user) return null;
    
    return {
      language: user.preferred_language,
      currency: user.preferred_currency,
      maxDistance: user.max_distance_km
    };
  }, [user]);

  // Vérification des statistiques
  const getUserStats = useCallback(() => {
    if (!user) return null;
    
    return {
      totalExchanges: user.total_exchanges,
      successfulExchanges: user.successful_exchanges,
      reputationScore: user.reputation_score,
      loginCount: user.login_count
    };
  }, [user]);

  // Vérification de la dernière activité
  const getLastActivity = useCallback(() => {
    if (!user?.last_activity_at) return null;
    return new Date(user.last_activity_at);
  }, [user]);

  // Vérification si l'utilisateur est actif
  const isUserActive = useCallback(() => {
    const lastActivity = getLastActivity();
    if (!lastActivity) return false;
    
    // Considérer l'utilisateur comme actif s'il s'est connecté dans les 30 derniers jours
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    
    return lastActivity > thirtyDaysAgo;
  }, [getLastActivity]);

  // Vérification de la sécurité
  const getSecurityStatus = useCallback(() => {
    if (!user) return null;
    
    return {
      isLocked: !!user.account_locked_until,
      lockUntil: user.account_locked_until ? new Date(user.account_locked_until) : null,
      failedLoginAttempts: user.failed_login_attempts,
      isLockedNow: user.account_locked_until ? new Date(user.account_locked_until) > new Date() : false
    };
  }, [user]);

  // Vérification si l'utilisateur est verrouillé
  const isAccountLocked = useCallback(() => {
    const security = getSecurityStatus();
    return security?.isLockedNow || false;
  }, [getSecurityStatus]);

  // Vérification du verrouillage
  const getLockRemainingTime = useCallback(() => {
    const security = getSecurityStatus();
    if (!security?.lockUntil) return null;
    
    const now = new Date();
    const lockTime = security.lockUntil;
    
    if (lockTime <= now) return null;
    
    return lockTime.getTime() - now.getTime();
  }, [getSecurityStatus]);

  // Formatage du temps de verrouillage restant
  const getLockRemainingTimeFormatted = useCallback(() => {
    const remaining = getLockRemainingTime();
    if (!remaining) return null;
    
    const minutes = Math.ceil(remaining / (1000 * 60));
    if (minutes < 60) {
      return `${minutes} minute${minutes > 1 ? 's' : ''}`;
    }
    
    const hours = Math.ceil(minutes / 60);
    if (hours < 24) {
      return `${hours} heure${hours > 1 ? 's' : ''}`;
    }
    
    const days = Math.ceil(hours / 24);
    return `${days} jour${days > 1 ? 's' : ''}`;
  }, [getLockRemainingTime]);

  return {
    // État
    isAuthenticated,
    user,
    tokens,
    error,
    isLoading,
    
    // Actions
    login,
    register,
    logout,
    refreshToken,
    fetchProfile,
    clearAuthError,
    checkAuthStatus,
    
    // Vérifications
    hasPermission,
    isEmailVerified,
    isPhoneVerified,
    getTrustScore,
    isPremium,
    getPremiumExpiry,
    isPremiumExpired,
    getUserLocation,
    getNotificationPreferences,
    getPreferences,
    getUserStats,
    getLastActivity,
    isUserActive,
    getSecurityStatus,
    isAccountLocked,
    getLockRemainingTime,
    getLockRemainingTimeFormatted
  };
};
