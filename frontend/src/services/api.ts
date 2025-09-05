import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { toast } from 'react-hot-toast';

// Configuration de base
const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:5000/api/v1';

// Types
export interface ApiError {
  message: string;
  errors?: Record<string, string[]>;
  status?: number;
}

// Instance axios avec configuration de base
export const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Intercepteur pour ajouter le token d'authentification
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Intercepteur pour gérer les réponses et erreurs
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Gestion du token expiré
    if (error.response?.status === 401 && !(originalRequest as any)._retry) {
      (originalRequest as any)._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);

          // Retry de la requête originale
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Échec du refresh, déconnexion
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    // Gestion des erreurs communes
    if (error.response?.status === 422) {
      const errorMessage = error.response.data?.message || 'Données invalides';
      toast.error(errorMessage);
    } else if (error.response?.status === 403) {
      toast.error('Accès refusé');
    } else if (error.response?.status === 404) {
      toast.error('Ressource non trouvée');
    } else if (error.response?.status >= 500) {
      toast.error('Erreur serveur. Veuillez réessayer plus tard.');
    } else if (error.code === 'ECONNABORTED') {
      toast.error('Délai d\'attente dépassé. Vérifiez votre connexion.');
    } else if (!error.response) {
      toast.error('Erreur de connexion. Vérifiez votre connexion internet.');
    }

    return Promise.reject(error);
  }
);

// Fonctions utilitaires
export const handleApiError = (error: any): ApiError => {
  if (error.response) {
    return {
      message: error.response.data?.message || 'Une erreur est survenue',
      errors: error.response.data?.errors,
      status: error.response.status,
    };
  } else if (error.request) {
    return {
      message: 'Erreur de connexion au serveur',
      status: 0,
    };
  } else {
    return {
      message: error.message || 'Une erreur inattendue est survenue',
    };
  }
};

export const isNetworkError = (error: any): boolean => {
  return !error.response && error.request;
};

export const isServerError = (error: any): boolean => {
  return error.response?.status >= 500;
};

export const isClientError = (error: any): boolean => {
  return error.response?.status >= 400 && error.response?.status < 500;
};

// Configuration des requêtes
export const apiConfig = {
  timeout: 30000,
  retries: 3,
  retryDelay: 1000,
};

// Fonction pour retry automatique
export const withRetry = async <T>(
  fn: () => Promise<T>,
  retries: number = apiConfig.retries,
  delay: number = apiConfig.retryDelay
): Promise<T> => {
  try {
    return await fn();
  } catch (error) {
    if (retries > 0 && (isNetworkError(error) || isServerError(error))) {
      await new Promise(resolve => setTimeout(resolve, delay));
      return withRetry(fn, retries - 1, delay * 2);
    }
    throw error;
  }
};

// Export de l'instance configurée
export default api;

// Export des types
export type { AxiosInstance, AxiosRequestConfig, AxiosResponse };
