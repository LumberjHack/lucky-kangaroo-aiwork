import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { User, AuthTokens, LoginCredentials, RegisterData, UserProfile } from '../../types';
import AuthService from '../../services/authService';

// Types pour le state
interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  profile: UserProfile | null;
}

// State initial
const initialState: AuthState = {
  user: null,
  tokens: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  profile: null,
};

// Thunks asynchrones
export const loginUser = createAsyncThunk(
  'auth/login',
  async (credentials: LoginCredentials, { rejectWithValue }) => {
    try {
      const result = await AuthService.login(credentials);
      return result;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Échec de la connexion');
    }
  }
);

export const registerUser = createAsyncThunk(
  'auth/register',
  async (data: RegisterData, { rejectWithValue }) => {
    try {
      const result = await AuthService.register(data);
      return result;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Échec de l\'inscription');
    }
  }
);

export const logoutUser = createAsyncThunk(
  'auth/logout',
  async (_, { rejectWithValue }) => {
    try {
      await AuthService.logout();
      return true;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Échec de la déconnexion');
    }
  }
);

export const refreshUserToken = createAsyncThunk(
  'auth/refreshToken',
  async (_, { rejectWithValue }) => {
    try {
      const result = await AuthService.refreshToken();
      return result;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Échec du rafraîchissement du token');
    }
  }
);

export const fetchUserProfile = createAsyncThunk(
  'auth/fetchProfile',
  async (_, { rejectWithValue }) => {
    try {
      const profile = await AuthService.getProfile();
      return profile;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Échec de la récupération du profil');
    }
  }
);

export const updateUserProfile = createAsyncThunk(
  'auth/updateProfile',
  async (profileData: Partial<User>, { rejectWithValue }) => {
    try {
      const updatedUser = await AuthService.updateProfile(profileData);
      return updatedUser;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Échec de la mise à jour du profil');
    }
  }
);

export const changeUserPassword = createAsyncThunk(
  'auth/changePassword',
  async (
    { currentPassword, newPassword }: { currentPassword: string; newPassword: string },
    { rejectWithValue }
  ) => {
    try {
      await AuthService.changePassword(currentPassword, newPassword);
      return true;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Échec du changement de mot de passe');
    }
  }
);

export const deleteUserAccount = createAsyncThunk(
  'auth/deleteAccount',
  async (password: string, { rejectWithValue }) => {
    try {
      await AuthService.deleteAccount(password);
      return true;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Échec de la suppression du compte');
    }
  }
);

export const verifyUserEmail = createAsyncThunk(
  'auth/verifyEmail',
  async (token: string, { rejectWithValue }) => {
    try {
      await AuthService.verifyEmail(token);
      return true;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Échec de la vérification de l\'email');
    }
  }
);

export const forgotUserPassword = createAsyncThunk(
  'auth/forgotPassword',
  async (email: string, { rejectWithValue }) => {
    try {
      await AuthService.forgotPassword(email);
      return true;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Échec de l\'envoi de l\'email de réinitialisation');
    }
  }
);

export const resetUserPassword = createAsyncThunk(
  'auth/resetPassword',
  async (
    { token, newPassword }: { token: string; newPassword: string },
    { rejectWithValue }
  ) => {
    try {
      await AuthService.resetPassword(token, newPassword);
      return true;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Échec de la réinitialisation du mot de passe');
    }
  }
);

// Slice
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    // Actions synchrones
    clearError: (state) => {
      state.error = null;
    },
    
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
      state.isAuthenticated = true;
    },
    
    setTokens: (state, action: PayloadAction<AuthTokens>) => {
      state.tokens = action.payload;
    },
    
    updateUser: (state, action: PayloadAction<Partial<User>>) => {
      if (state.user) {
        state.user = { ...state.user, ...action.payload };
      }
    },
    
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    
    // Réinitialisation du state
    resetAuth: (state) => {
      state.user = null;
      state.tokens = null;
      state.isAuthenticated = false;
      state.profile = null;
      state.error = null;
    },
    
    // Mise à jour des préférences
    updateNotificationPreferences: (state, action: PayloadAction<Partial<User>>) => {
      if (state.user) {
        state.user = { ...state.user, ...action.payload };
      }
    },
    
    updateLocationPreferences: (state, action: PayloadAction<Partial<User>>) => {
      if (state.user) {
        state.user = { ...state.user, ...action.payload };
      }
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(loginUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = action.payload.user;
        state.tokens = action.payload.tokens;
        state.isAuthenticated = true;
        state.error = null;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      
      // Register
      .addCase(registerUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(registerUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = action.payload.user;
        state.tokens = action.payload.tokens;
        state.isAuthenticated = true;
        state.error = null;
      })
      .addCase(registerUser.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      
      // Logout
      .addCase(logoutUser.fulfilled, (state) => {
        state.user = null;
        state.tokens = null;
        state.isAuthenticated = false;
        state.profile = null;
        state.error = null;
      })
      
      // Refresh Token
      .addCase(refreshUserToken.fulfilled, (state, action) => {
        if (state.tokens) {
          state.tokens.access_token = action.payload.access_token;
        }
      })
      
      // Fetch Profile
      .addCase(fetchUserProfile.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchUserProfile.fulfilled, (state, action) => {
        state.isLoading = false;
        state.profile = action.payload;
        state.error = null;
      })
      .addCase(fetchUserProfile.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      
      // Update Profile
      .addCase(updateUserProfile.fulfilled, (state, action) => {
        state.user = action.payload;
        if (state.profile) {
          state.profile.user = action.payload;
        }
      })
      
      // Change Password
      .addCase(changeUserPassword.rejected, (state, action) => {
        state.error = action.payload as string;
      })
      
      // Delete Account
      .addCase(deleteUserAccount.fulfilled, (state) => {
        state.user = null;
        state.tokens = null;
        state.isAuthenticated = false;
        state.profile = null;
        state.error = null;
      })
      
      // Verify Email
      .addCase(verifyUserEmail.rejected, (state, action) => {
        state.error = action.payload as string;
      })
      
      // Forgot Password
      .addCase(forgotUserPassword.rejected, (state, action) => {
        state.error = action.payload as string;
      })
      
      // Reset Password
      .addCase(resetUserPassword.rejected, (state, action) => {
        state.error = action.payload as string;
      });
  },
});

// Actions
export const {
  clearError,
  setUser,
  setTokens,
  updateUser,
  setLoading,
  resetAuth,
  updateNotificationPreferences,
  updateLocationPreferences,
} = authSlice.actions;

// Selecteurs
export const selectAuth = (state: { auth: AuthState }) => state.auth;
export const selectUser = (state: { auth: AuthState }) => state.auth.user;
export const selectTokens = (state: { auth: AuthState }) => state.auth.tokens;
export const selectIsAuthenticated = (state: { auth: AuthState }) => state.auth.isAuthenticated;
export const selectIsLoading = (state: { auth: AuthState }) => state.auth.isLoading;
export const selectError = (state: { auth: AuthState }) => state.auth.error;
export const selectProfile = (state: { auth: AuthState }) => state.auth.profile;
export const selectTrustScore = (state: { auth: AuthState }) => state.auth.user?.trust_score || 0;
export const selectUserLocation = (state: { auth: AuthState }) => ({
  latitude: state.auth.user?.latitude,
  longitude: state.auth.user?.longitude,
  city: state.auth.user?.city,
  country: state.auth.user?.country,
});

// Export logout action
export const logout = logoutUser;

// Reducer
export default authSlice.reducer;
