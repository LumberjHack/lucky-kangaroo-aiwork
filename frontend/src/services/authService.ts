import api from './api';
import { 
  LoginCredentials, 
  RegisterData, 
  AuthTokens, 
  User, 
  ApiResponse,
  UserProfile 
} from '../types';

export class AuthService {
  // Connexion utilisateur
  static async login(credentials: LoginCredentials): Promise<{ user: User; tokens: AuthTokens }> {
    try {
      const response = await api.post<ApiResponse<{ user: User; tokens: AuthTokens }>>('/auth/login', credentials);
      
      if (response.data.success && response.data.data) {
        const { user, tokens } = response.data.data;
        
        // Stockage des tokens et informations utilisateur
        localStorage.setItem('access_token', tokens.access_token);
        localStorage.setItem('refresh_token', tokens.refresh_token);
        localStorage.setItem('user', JSON.stringify(user));
        
        return { user, tokens };
      } else {
        throw new Error(response.data.message || 'Échec de la connexion');
      }
    } catch (error) {
      throw error;
    }
  }

  // Inscription utilisateur
  static async register(data: RegisterData): Promise<{ user: User; tokens: AuthTokens }> {
    try {
      const response = await api.post<ApiResponse<{ user: User; tokens: AuthTokens }>>('/auth/register', data);
      
      if (response.data.success && response.data.data) {
        const { user, tokens } = response.data.data;
        
        // Stockage des tokens et informations utilisateur
        localStorage.setItem('access_token', tokens.access_token);
        localStorage.setItem('refresh_token', tokens.refresh_token);
        localStorage.setItem('user', JSON.stringify(user));
        
        return { user, tokens };
      } else {
        throw new Error(response.data.message || 'Échec de l\'inscription');
      }
    } catch (error) {
      throw error;
    }
  }

  // Déconnexion utilisateur
  static async logout(): Promise<void> {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('Erreur lors de la déconnexion:', error);
    } finally {
      // Nettoyage du stockage local
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    }
  }

  // Rafraîchissement du token
  static async refreshToken(): Promise<{ access_token: string }> {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        throw new Error('Token de rafraîchissement non trouvé');
      }

      const response = await api.post<ApiResponse<{ access_token: string }>>('/auth/refresh', {
        refresh_token: refreshToken,
      });

      if (response.data.success && response.data.data) {
        const { access_token } = response.data.data;
        localStorage.setItem('access_token', access_token);
        return { access_token };
      } else {
        throw new Error(response.data.message || 'Échec du rafraîchissement du token');
      }
    } catch (error) {
      // En cas d'échec, déconnexion
      this.logout();
      throw error;
    }
  }

  // Vérification de l'email
  static async verifyEmail(token: string): Promise<void> {
    try {
      const response = await api.post<ApiResponse>('/auth/verify-email', { token });
      
      if (!response.data.success) {
        throw new Error(response.data.message || 'Échec de la vérification de l\'email');
      }
    } catch (error) {
      throw error;
    }
  }

  // Demande de réinitialisation du mot de passe
  static async forgotPassword(email: string): Promise<void> {
    try {
      const response = await api.post<ApiResponse>('/auth/forgot-password', { email });
      
      if (!response.data.success) {
        throw new Error(response.data.message || 'Échec de l\'envoi de l\'email de réinitialisation');
      }
    } catch (error) {
      throw error;
    }
  }

  // Réinitialisation du mot de passe
  static async resetPassword(token: string, newPassword: string): Promise<void> {
    try {
      const response = await api.post<ApiResponse>('/auth/reset-password', {
        token,
        new_password: newPassword,
      });
      
      if (!response.data.success) {
        throw new Error(response.data.message || 'Échec de la réinitialisation du mot de passe');
      }
    } catch (error) {
      throw error;
    }
  }

  // Changement de mot de passe
  static async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    try {
      const response = await api.post<ApiResponse>('/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
      });
      
      if (!response.data.success) {
        throw new Error(response.data.message || 'Échec du changement de mot de passe');
      }
    } catch (error) {
      throw error;
    }
  }

  // Mise à jour du profil utilisateur
  static async updateProfile(profileData: Partial<User>): Promise<User> {
    try {
      const response = await api.put<ApiResponse<User>>('/auth/profile', profileData);
      
      if (response.data.success && response.data.data) {
        const updatedUser = response.data.data;
        
        // Mise à jour du stockage local
        localStorage.setItem('user', JSON.stringify(updatedUser));
        
        return updatedUser;
      } else {
        throw new Error(response.data.message || 'Échec de la mise à jour du profil');
      }
    } catch (error) {
      throw error;
    }
  }

  // Récupération du profil utilisateur
  static async getProfile(): Promise<UserProfile> {
    try {
      const response = await api.get<ApiResponse<UserProfile>>('/auth/profile');
      
      if (response.data.success && response.data.data) {
        return response.data.data;
      } else {
        throw new Error(response.data.message || 'Échec de la récupération du profil');
      }
    } catch (error) {
      throw error;
    }
  }

  // Suppression du compte
  static async deleteAccount(password: string): Promise<void> {
    try {
      const response = await api.delete<ApiResponse>('/auth/account', {
        data: { password },
      });
      
      if (!response.data.success) {
        throw new Error(response.data.message || 'Échec de la suppression du compte');
      }
      
      // Nettoyage du stockage local
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    } catch (error) {
      throw error;
    }
  }

  // Vérification de l'état de l'authentification
  static isAuthenticated(): boolean {
    const token = localStorage.getItem('access_token');
    const user = localStorage.getItem('user');
    return !!(token && user);
  }

  // Récupération de l'utilisateur depuis le stockage local
  static getCurrentUser(): User | null {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        return JSON.parse(userStr);
      } catch (error) {
        console.error('Erreur lors du parsing de l\'utilisateur:', error);
        return null;
      }
    }
    return null;
  }

  // Récupération du token d'accès
  static getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  // Vérification de l'expiration du token
  static isTokenExpired(): boolean {
    const token = localStorage.getItem('access_token');
    if (!token) return true;

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Date.now() / 1000;
      return payload.exp < currentTime;
    } catch (error) {
      return true;
    }
  }

  // Envoi de la vérification de l'email
  static async resendVerificationEmail(): Promise<void> {
    try {
      const response = await api.post<ApiResponse>('/auth/resend-verification');
      
      if (!response.data.success) {
        throw new Error(response.data.message || 'Échec de l\'envoi de l\'email de vérification');
      }
    } catch (error) {
      throw error;
    }
  }

  // Mise à jour des préférences de notification
  static async updateNotificationPreferences(preferences: {
    email_notifications?: boolean;
    push_notifications?: boolean;
    sms_notifications?: boolean;
    whatsapp_notifications?: boolean;
  }): Promise<void> {
    try {
      const response = await api.put<ApiResponse>('/auth/notification-preferences', preferences);
      
      if (!response.data.success) {
        throw new Error(response.data.message || 'Échec de la mise à jour des préférences');
      }
    } catch (error) {
      throw error;
    }
  }

  // Mise à jour des préférences de géolocalisation
  static async updateLocationPreferences(preferences: {
    max_distance_km?: number;
    preferred_language?: string;
    preferred_currency?: string;
  }): Promise<void> {
    try {
      const response = await api.put<ApiResponse>('/auth/location-preferences', preferences);
      
      if (!response.data.success) {
        throw new Error(response.data.message || 'Échec de la mise à jour des préférences de localisation');
      }
    } catch (error) {
      throw error;
    }
  }
}

export default AuthService;
