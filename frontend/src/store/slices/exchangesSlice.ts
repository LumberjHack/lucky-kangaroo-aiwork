import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import api from '../../services/api';

// Types
export interface Exchange {
  id: string;
  status: 'pending' | 'accepted' | 'rejected' | 'completed' | 'cancelled';
  type: 'direct' | 'chain';
  initiator_id: string;
  initiator?: {
    id: string;
    first_name: string;
    last_name: string;
    email: string;
  };
  participants: Array<{
    id: string;
    user_id: string;
    listing_id: string;
    user?: {
      id: string;
      first_name: string;
      last_name: string;
      email: string;
    };
    listing?: {
      id: string;
      title: string;
      price: number;
      currency: string;
      images: string[];
    };
    status: 'pending' | 'accepted' | 'rejected';
  }>;
  messages: Array<{
    id: string;
    user_id: string;
    content: string;
    created_at: string;
    user?: {
      id: string;
      first_name: string;
      last_name: string;
    };
  }>;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

export interface ExchangeFilters {
  status?: string;
  type?: 'direct' | 'chain';
  page?: number;
  limit?: number;
}

export interface ExchangesState {
  exchanges: Exchange[];
  currentExchange: Exchange | null;
  filters: ExchangeFilters;
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
  loading: boolean;
  error: string | null;
  matchingSuggestions: any[];
  exchangeChains: any[];
}

const initialState: ExchangesState = {
  exchanges: [],
  currentExchange: null,
  filters: {
    page: 1,
    limit: 20
  },
  pagination: {
    page: 1,
    limit: 20,
    total: 0,
    totalPages: 0
  },
  loading: false,
  error: null,
  matchingSuggestions: [],
  exchangeChains: []
};

// Async thunks
export const fetchExchanges = createAsyncThunk(
  'exchanges/fetchExchanges',
  async (filters: ExchangeFilters = {}, { rejectWithValue }) => {
    try {
      const response = await api.get('/exchanges', { params: filters });
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Erreur lors du chargement des échanges');
    }
  }
);

export const fetchExchangeById = createAsyncThunk(
  'exchanges/fetchExchangeById',
  async (id: string, { rejectWithValue }) => {
    try {
      const response = await api.get(`/exchanges/${id}`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Erreur lors du chargement de l\'échange');
    }
  }
);

export const createExchange = createAsyncThunk(
  'exchanges/createExchange',
  async (exchangeData: Partial<Exchange>, { rejectWithValue }) => {
    try {
      const response = await api.post('/exchanges', exchangeData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Erreur lors de la création de l\'échange');
    }
  }
);

export const updateExchangeStatus = createAsyncThunk(
  'exchanges/updateExchangeStatus',
  async ({ id, status }: { id: string; status: string }, { rejectWithValue }) => {
    try {
      const response = await api.put(`/exchanges/${id}/status`, { status });
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Erreur lors de la mise à jour de l\'échange');
    }
  }
);

export const addExchangeMessage = createAsyncThunk(
  'exchanges/addExchangeMessage',
  async ({ exchangeId, content }: { exchangeId: string; content: string }, { rejectWithValue }) => {
    try {
      const response = await api.post(`/exchanges/${exchangeId}/messages`, { content });
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Erreur lors de l\'ajout du message');
    }
  }
);

export const fetchMatchingSuggestions = createAsyncThunk(
  'exchanges/fetchMatchingSuggestions',
  async (listingId: string, { rejectWithValue }) => {
    try {
      const response = await api.get(`/matching/suggestions/${listingId}`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Erreur lors du chargement des suggestions');
    }
  }
);

export const fetchExchangeChains = createAsyncThunk(
  'exchanges/fetchExchangeChains',
  async (listingId: string, { rejectWithValue }) => {
    try {
      const response = await api.get(`/matching/chains/${listingId}`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Erreur lors du chargement des chaînes d\'échange');
    }
  }
);

// Slice
const exchangesSlice = createSlice({
  name: 'exchanges',
  initialState,
  reducers: {
    setFilters: (state, action: PayloadAction<ExchangeFilters>) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearFilters: (state) => {
      state.filters = {
        page: 1,
        limit: 20
      };
    },
    setCurrentExchange: (state, action: PayloadAction<Exchange | null>) => {
      state.currentExchange = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    addMessage: (state, action: PayloadAction<{ exchangeId: string; message: any }>) => {
      const exchange = state.exchanges.find(e => e.id === action.payload.exchangeId);
      if (exchange) {
        exchange.messages.push(action.payload.message);
      }
      if (state.currentExchange?.id === action.payload.exchangeId) {
        state.currentExchange.messages.push(action.payload.message);
      }
    }
  },
  extraReducers: (builder) => {
    builder
      // Fetch exchanges
      .addCase(fetchExchanges.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchExchanges.fulfilled, (state, action) => {
        state.loading = false;
        state.exchanges = action.payload.exchanges || action.payload;
        state.pagination = action.payload.pagination || {
          page: 1,
          limit: 20,
          total: action.payload.length || 0,
          totalPages: 1
        };
      })
      .addCase(fetchExchanges.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Fetch exchange by ID
      .addCase(fetchExchangeById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchExchangeById.fulfilled, (state, action) => {
        state.loading = false;
        state.currentExchange = action.payload;
      })
      .addCase(fetchExchangeById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Create exchange
      .addCase(createExchange.fulfilled, (state, action) => {
        state.exchanges.unshift(action.payload);
      })
      
      // Update exchange status
      .addCase(updateExchangeStatus.fulfilled, (state, action) => {
        const index = state.exchanges.findIndex(e => e.id === action.payload.id);
        if (index !== -1) {
          state.exchanges[index] = action.payload;
        }
        if (state.currentExchange?.id === action.payload.id) {
          state.currentExchange = action.payload;
        }
      })
      
      // Add exchange message
      .addCase(addExchangeMessage.fulfilled, (state, action) => {
        const exchange = state.exchanges.find(e => e.id === action.payload.exchange_id);
        if (exchange) {
          exchange.messages.push(action.payload);
        }
        if (state.currentExchange?.id === action.payload.exchange_id) {
          state.currentExchange.messages.push(action.payload);
        }
      })
      
      // Fetch matching suggestions
      .addCase(fetchMatchingSuggestions.fulfilled, (state, action) => {
        state.matchingSuggestions = action.payload;
      })
      
      // Fetch exchange chains
      .addCase(fetchExchangeChains.fulfilled, (state, action) => {
        state.exchangeChains = action.payload;
      });
  }
});

export const {
  setFilters,
  clearFilters,
  setCurrentExchange,
  clearError,
  addMessage
} = exchangesSlice.actions;

export default exchangesSlice.reducer;
