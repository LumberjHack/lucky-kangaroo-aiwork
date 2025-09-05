import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import api from '../../services/api';

// Types
export interface Listing {
  id: string;
  title: string;
  description: string;
  price: number;
  currency: string;
  condition: 'new' | 'like_new' | 'good' | 'fair' | 'poor';
  category_id: string;
  category?: {
    id: string;
    name: string;
    slug: string;
  };
  user_id: string;
  user?: {
    id: string;
    first_name: string;
    last_name: string;
    email: string;
  };
  status: 'draft' | 'active' | 'paused' | 'sold' | 'expired';
  type: 'good' | 'service';
  images: string[];
  location?: {
    id: string;
    latitude: number;
    longitude: number;
    address: string;
    city: string;
    country: string;
  };
  created_at: string;
  updated_at: string;
  boosted_until?: string;
  view_count: number;
  favorite_count: number;
  is_favorited?: boolean;
}

export interface ListingFilters {
  search?: string;
  category_id?: string;
  min_price?: number;
  max_price?: number;
  condition?: string;
  type?: 'good' | 'service';
  location?: {
    latitude: number;
    longitude: number;
    radius: number;
  };
  sort_by?: 'created_at' | 'price' | 'distance' | 'relevance';
  sort_order?: 'asc' | 'desc';
  page?: number;
  limit?: number;
}

export interface ListingsState {
  listings: Listing[];
  currentListing: Listing | null;
  filters: ListingFilters;
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
  loading: boolean;
  error: string | null;
  favorites: string[];
  myListings: Listing[];
  myListingsLoading: boolean;
}

const initialState: ListingsState = {
  listings: [],
  currentListing: null,
  filters: {
    page: 1,
    limit: 20,
    sort_by: 'created_at',
    sort_order: 'desc'
  },
  pagination: {
    page: 1,
    limit: 20,
    total: 0,
    totalPages: 0
  },
  loading: false,
  error: null,
  favorites: [],
  myListings: [],
  myListingsLoading: false
};

// Async thunks
export const fetchListings = createAsyncThunk(
  'listings/fetchListings',
  async (filters: ListingFilters = {}, { rejectWithValue }) => {
    try {
      const response = await api.get('/listings', { params: filters });
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Erreur lors du chargement des annonces');
    }
  }
);

export const fetchListingById = createAsyncThunk(
  'listings/fetchListingById',
  async (id: string, { rejectWithValue }) => {
    try {
      const response = await api.get(`/listings/${id}`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Erreur lors du chargement de l\'annonce');
    }
  }
);

export const createListing = createAsyncThunk(
  'listings/createListing',
  async (listingData: Partial<Listing>, { rejectWithValue }) => {
    try {
      const response = await api.post('/listings', listingData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Erreur lors de la création de l\'annonce');
    }
  }
);

export const updateListing = createAsyncThunk(
  'listings/updateListing',
  async ({ id, data }: { id: string; data: Partial<Listing> }, { rejectWithValue }) => {
    try {
      const response = await api.put(`/listings/${id}`, data);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Erreur lors de la mise à jour de l\'annonce');
    }
  }
);

export const deleteListing = createAsyncThunk(
  'listings/deleteListing',
  async (id: string, { rejectWithValue }) => {
    try {
      await api.delete(`/listings/${id}`);
      return id;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Erreur lors de la suppression de l\'annonce');
    }
  }
);

export const toggleFavorite = createAsyncThunk(
  'listings/toggleFavorite',
  async (listingId: string, { rejectWithValue }) => {
    try {
      const response = await api.post(`/listings/${listingId}/favorite`);
      return { listingId, isFavorited: response.data.is_favorited };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Erreur lors de la mise à jour des favoris');
    }
  }
);

export const fetchMyListings = createAsyncThunk(
  'listings/fetchMyListings',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/listings/my');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Erreur lors du chargement de vos annonces');
    }
  }
);

export const fetchFavorites = createAsyncThunk(
  'listings/fetchFavorites',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/listings/favorites');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Erreur lors du chargement des favoris');
    }
  }
);

// Slice
const listingsSlice = createSlice({
  name: 'listings',
  initialState,
  reducers: {
    setFilters: (state, action: PayloadAction<ListingFilters>) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearFilters: (state) => {
      state.filters = {
        page: 1,
        limit: 20,
        sort_by: 'created_at',
        sort_order: 'desc'
      };
    },
    setCurrentListing: (state, action: PayloadAction<Listing | null>) => {
      state.currentListing = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    incrementViewCount: (state, action: PayloadAction<string>) => {
      const listing = state.listings.find(l => l.id === action.payload);
      if (listing) {
        listing.view_count += 1;
      }
      if (state.currentListing?.id === action.payload) {
        state.currentListing.view_count += 1;
      }
    }
  },
  extraReducers: (builder) => {
    builder
      // Fetch listings
      .addCase(fetchListings.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchListings.fulfilled, (state, action) => {
        state.loading = false;
        state.listings = action.payload.listings || action.payload;
        state.pagination = action.payload.pagination || {
          page: 1,
          limit: 20,
          total: action.payload.length || 0,
          totalPages: 1
        };
      })
      .addCase(fetchListings.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Fetch listing by ID
      .addCase(fetchListingById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchListingById.fulfilled, (state, action) => {
        state.loading = false;
        state.currentListing = action.payload;
      })
      .addCase(fetchListingById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Create listing
      .addCase(createListing.fulfilled, (state, action) => {
        state.myListings.unshift(action.payload);
      })
      
      // Update listing
      .addCase(updateListing.fulfilled, (state, action) => {
        const index = state.myListings.findIndex(l => l.id === action.payload.id);
        if (index !== -1) {
          state.myListings[index] = action.payload;
        }
        if (state.currentListing?.id === action.payload.id) {
          state.currentListing = action.payload;
        }
      })
      
      // Delete listing
      .addCase(deleteListing.fulfilled, (state, action) => {
        state.myListings = state.myListings.filter(l => l.id !== action.payload);
        state.listings = state.listings.filter(l => l.id !== action.payload);
        if (state.currentListing?.id === action.payload) {
          state.currentListing = null;
        }
      })
      
      // Toggle favorite
      .addCase(toggleFavorite.fulfilled, (state, action) => {
        const { listingId, isFavorited } = action.payload;
        const listing = state.listings.find(l => l.id === listingId);
        if (listing) {
          listing.is_favorited = isFavorited;
          listing.favorite_count += isFavorited ? 1 : -1;
        }
        if (state.currentListing?.id === listingId) {
          state.currentListing.is_favorited = isFavorited;
          state.currentListing.favorite_count += isFavorited ? 1 : -1;
        }
        if (isFavorited) {
          state.favorites.push(listingId);
        } else {
          state.favorites = state.favorites.filter(id => id !== listingId);
        }
      })
      
      // Fetch my listings
      .addCase(fetchMyListings.pending, (state) => {
        state.myListingsLoading = true;
      })
      .addCase(fetchMyListings.fulfilled, (state, action) => {
        state.myListingsLoading = false;
        state.myListings = action.payload;
      })
      .addCase(fetchMyListings.rejected, (state, action) => {
        state.myListingsLoading = false;
        state.error = action.payload as string;
      })
      
      // Fetch favorites
      .addCase(fetchFavorites.fulfilled, (state, action) => {
        state.favorites = action.payload.map((listing: Listing) => listing.id);
      });
  }
});

export const {
  setFilters,
  clearFilters,
  setCurrentListing,
  clearError,
  incrementViewCount
} = listingsSlice.actions;

export default listingsSlice.reducer;
