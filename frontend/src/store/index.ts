import { configureStore } from '@reduxjs/toolkit';
import { persistStore, persistReducer } from 'redux-persist';
import storage from 'redux-persist/lib/storage';
import { combineReducers } from 'redux';

// Reducers
import authReducer from './slices/authSlice';
import listingsReducer from './slices/listingsSlice';
import exchangesReducer from './slices/exchangesSlice';
import chatReducer from './slices/chatSlice';
import notificationsReducer from './slices/notificationsSlice';
import uiReducer from './slices/uiSlice';

// Configuration de la persistance
const persistConfig = {
  key: 'lucky-kangaroo-root',
  storage,
  whitelist: ['auth', 'ui'], // Seuls auth et ui sont persistés
  blacklist: ['listings', 'exchanges', 'chat', 'notifications'], // Les autres ne sont pas persistés
};

// Combinaison des reducers
const rootReducer = combineReducers({
  auth: authReducer,
  listings: listingsReducer,
  exchanges: exchangesReducer,
  chat: chatReducer,
  notifications: notificationsReducer,
  ui: uiReducer,
});

// Reducer persistant
const persistedReducer = persistReducer(persistConfig, rootReducer);

// Configuration du store
export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
        ignoredPaths: ['auth.tokens'], // Les tokens JWT ne sont pas sérialisables
      },
      thunk: true,
    }),
  devTools: process.env.NODE_ENV !== 'production',
});

// Store persistant
export const persistor = persistStore(store);

// Types
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// Hooks typés
export type AppThunk<ReturnType = void> = import('@reduxjs/toolkit').ThunkAction<
  ReturnType,
  RootState,
  unknown,
  import('@reduxjs/toolkit').AnyAction
>;

export type AppThunkDispatch = import('@reduxjs/toolkit').ThunkDispatch<
  RootState,
  unknown,
  import('@reduxjs/toolkit').AnyAction
>;
