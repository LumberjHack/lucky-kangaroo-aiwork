import { createSlice, PayloadAction } from '@reduxjs/toolkit';

// Types
export interface UIState {
  theme: 'light' | 'dark' | 'system';
  sidebarOpen: boolean;
  mobileMenuOpen: boolean;
  searchModalOpen: boolean;
  filtersModalOpen: boolean;
  notificationsPanelOpen: boolean;
  loading: {
    global: boolean;
    search: boolean;
    listings: boolean;
    chat: boolean;
  };
  toast: {
    show: boolean;
    type: 'success' | 'error' | 'warning' | 'info';
    message: string;
    duration: number;
  };
  modals: {
    createListing: boolean;
    editListing: boolean;
    deleteListing: boolean;
    reportListing: boolean;
    contactUser: boolean;
    exchangeProposal: boolean;
  };
  search: {
    query: string;
    filters: any;
    results: any[];
    totalResults: number;
    currentPage: number;
    isLoading: boolean;
  };
  map: {
    center: {
      lat: number;
      lng: number;
    };
    zoom: number;
    markers: any[];
    selectedMarker: string | null;
  };
  preferences: {
    language: string;
    currency: string;
    distanceUnit: 'km' | 'miles';
    notifications: {
      email: boolean;
      push: boolean;
      sms: boolean;
    };
    privacy: {
      showEmail: boolean;
      showPhone: boolean;
      showLocation: boolean;
    };
  };
}

const initialState: UIState = {
  theme: 'system',
  sidebarOpen: false,
  mobileMenuOpen: false,
  searchModalOpen: false,
  filtersModalOpen: false,
  notificationsPanelOpen: false,
  loading: {
    global: false,
    search: false,
    listings: false,
    chat: false
  },
  toast: {
    show: false,
    type: 'info',
    message: '',
    duration: 5000
  },
  modals: {
    createListing: false,
    editListing: false,
    deleteListing: false,
    reportListing: false,
    contactUser: false,
    exchangeProposal: false
  },
  search: {
    query: '',
    filters: {},
    results: [],
    totalResults: 0,
    currentPage: 1,
    isLoading: false
  },
  map: {
    center: {
      lat: 48.8566, // Paris par défaut
      lng: 2.3522
    },
    zoom: 10,
    markers: [],
    selectedMarker: null
  },
  preferences: {
    language: 'fr',
    currency: 'EUR',
    distanceUnit: 'km',
    notifications: {
      email: true,
      push: true,
      sms: false
    },
    privacy: {
      showEmail: false,
      showPhone: false,
      showLocation: true
    }
  }
};

// Slice
const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    // Theme
    setTheme: (state, action: PayloadAction<'light' | 'dark' | 'system'>) => {
      state.theme = action.payload;
    },
    
    // Sidebar
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebarOpen = action.payload;
    },
    
    // Mobile menu
    toggleMobileMenu: (state) => {
      state.mobileMenuOpen = !state.mobileMenuOpen;
    },
    setMobileMenuOpen: (state, action: PayloadAction<boolean>) => {
      state.mobileMenuOpen = action.payload;
    },
    
    // Modals
    toggleModal: (state, action: PayloadAction<keyof UIState['modals']>) => {
      state.modals[action.payload] = !state.modals[action.payload];
    },
    setModalOpen: (state, action: PayloadAction<{ modal: keyof UIState['modals']; open: boolean }>) => {
      state.modals[action.payload.modal] = action.payload.open;
    },
    closeAllModals: (state) => {
      Object.keys(state.modals).forEach(key => {
        state.modals[key as keyof UIState['modals']] = false;
      });
    },
    
    // Panels
    toggleSearchModal: (state) => {
      state.searchModalOpen = !state.searchModalOpen;
    },
    setSearchModalOpen: (state, action: PayloadAction<boolean>) => {
      state.searchModalOpen = action.payload;
    },
    
    toggleFiltersModal: (state) => {
      state.filtersModalOpen = !state.filtersModalOpen;
    },
    setFiltersModalOpen: (state, action: PayloadAction<boolean>) => {
      state.filtersModalOpen = action.payload;
    },
    
    toggleNotificationsPanel: (state) => {
      state.notificationsPanelOpen = !state.notificationsPanelOpen;
    },
    setNotificationsPanelOpen: (state, action: PayloadAction<boolean>) => {
      state.notificationsPanelOpen = action.payload;
    },
    
    // Loading states
    setLoading: (state, action: PayloadAction<{ type: keyof UIState['loading']; loading: boolean }>) => {
      state.loading[action.payload.type] = action.payload.loading;
    },
    setGlobalLoading: (state, action: PayloadAction<boolean>) => {
      state.loading.global = action.payload;
    },
    
    // Toast notifications
    showToast: (state, action: PayloadAction<{ type: UIState['toast']['type']; message: string; duration?: number }>) => {
      state.toast = {
        show: true,
        type: action.payload.type,
        message: action.payload.message,
        duration: action.payload.duration || 5000
      };
    },
    hideToast: (state) => {
      state.toast.show = false;
    },
    
    // Search
    setSearchQuery: (state, action: PayloadAction<string>) => {
      state.search.query = action.payload;
    },
    setSearchFilters: (state, action: PayloadAction<any>) => {
      state.search.filters = action.payload;
    },
    setSearchResults: (state, action: PayloadAction<{ results: any[]; totalResults: number }>) => {
      state.search.results = action.payload.results;
      state.search.totalResults = action.payload.totalResults;
    },
    setSearchLoading: (state, action: PayloadAction<boolean>) => {
      state.search.isLoading = action.payload;
    },
    setSearchPage: (state, action: PayloadAction<number>) => {
      state.search.currentPage = action.payload;
    },
    clearSearch: (state) => {
      state.search.query = '';
      state.search.filters = {};
      state.search.results = [];
      state.search.totalResults = 0;
      state.search.currentPage = 1;
      state.search.isLoading = false;
    },
    
    // Map
    setMapCenter: (state, action: PayloadAction<{ lat: number; lng: number }>) => {
      state.map.center = action.payload;
    },
    setMapZoom: (state, action: PayloadAction<number>) => {
      state.map.zoom = action.payload;
    },
    setMapMarkers: (state, action: PayloadAction<any[]>) => {
      state.map.markers = action.payload;
    },
    setSelectedMarker: (state, action: PayloadAction<string | null>) => {
      state.map.selectedMarker = action.payload;
    },
    
    // Preferences
    setLanguage: (state, action: PayloadAction<string>) => {
      state.preferences.language = action.payload;
    },
    setCurrency: (state, action: PayloadAction<string>) => {
      state.preferences.currency = action.payload;
    },
    setDistanceUnit: (state, action: PayloadAction<'km' | 'miles'>) => {
      state.preferences.distanceUnit = action.payload;
    },
    setNotificationPreference: (state, action: PayloadAction<{ type: keyof UIState['preferences']['notifications']; enabled: boolean }>) => {
      state.preferences.notifications[action.payload.type] = action.payload.enabled;
    },
    setPrivacyPreference: (state, action: PayloadAction<{ type: keyof UIState['preferences']['privacy']; enabled: boolean }>) => {
      state.preferences.privacy[action.payload.type] = action.payload.enabled;
    },
    
    // Reset
    resetUI: (state) => {
      return { ...initialState, theme: state.theme, preferences: state.preferences };
    }
  }
});

export const {
  setTheme,
  toggleSidebar,
  setSidebarOpen,
  toggleMobileMenu,
  setMobileMenuOpen,
  toggleModal,
  setModalOpen,
  closeAllModals,
  toggleSearchModal,
  setSearchModalOpen,
  toggleFiltersModal,
  setFiltersModalOpen,
  toggleNotificationsPanel,
  setNotificationsPanelOpen,
  setLoading,
  setGlobalLoading,
  showToast,
  hideToast,
  setSearchQuery,
  setSearchFilters,
  setSearchResults,
  setSearchLoading,
  setSearchPage,
  clearSearch,
  setMapCenter,
  setMapZoom,
  setMapMarkers,
  setSelectedMarker,
  setLanguage,
  setCurrency,
  setDistanceUnit,
  setNotificationPreference,
  setPrivacyPreference,
  resetUI
} = uiSlice.actions;

export default uiSlice.reducer;
