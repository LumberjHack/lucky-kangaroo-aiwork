// Types principaux pour Lucky Kangaroo

export interface User {
  id: number;
  uuid: string;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  bio?: string;
  phone?: string;
  date_of_birth?: string;
  profile_photo_url?: string;
  profile_photo_id?: number;
  
  // Géolocalisation
  latitude?: number;
  longitude?: number;
  address?: string;
  city?: string;
  postal_code?: string;
  country?: string;
  
  // Système de confiance
  trust_score: number;
  reputation_score: number;
  total_exchanges: number;
  successful_exchanges: number;
  
  // Préférences
  preferred_language: string;
  preferred_currency: string;
  max_distance_km: number;
  
  // Notifications
  email_notifications: boolean;
  push_notifications: boolean;
  sms_notifications: boolean;
  whatsapp_notifications: boolean;
  
  // Compte premium
  is_premium: boolean;
  premium_expires_at?: string;
  
  // Statut
  is_active: boolean;
  is_verified: boolean;
  email_verified: boolean;
  phone_verified: boolean;
  
  // Sécurité
  last_login_at?: string;
  login_count: number;
  failed_login_attempts: number;
  account_locked_until?: string;
  
  // Timestamps
  created_at: string;
  updated_at: string;
  last_activity_at?: string;
}

export interface Listing {
  id: number;
  uuid: string;
  user_id: number;
  user?: User;
  
  // Informations de base
  title: string;
  description: string;
  category: string;
  subcategory?: string;
  
  // Détails de l'objet
  brand?: string;
  model?: string;
  color?: string;
  size?: string;
  condition: ListingCondition;
  condition_details?: string;
  
  // Valeur et échange
  estimated_value?: number;
  min_exchange_value?: number;
  max_exchange_value?: number;
  currency: string;
  
  // Préférences d'échange
  desired_items?: string;
  desired_categories?: string;
  exchange_type: string;
  
  // Géolocalisation
  latitude?: number;
  longitude?: number;
  address?: string;
  city?: string;
  postal_code?: string;
  country?: string;
  max_distance_km: number;
  
  // Photos
  main_photo_url?: string;
  main_photo_id?: number;
  photo_count: number;
  images?: Image[];
  
  // Statut et visibilité
  status: ListingStatus;
  is_featured: boolean;
  is_urgent: boolean;
  is_negotiable: boolean;
  
  // Statistiques
  view_count: number;
  like_count: number;
  contact_count: number;
  exchange_requests_count: number;
  
  // IA et matching
  ai_tags?: string;
  ai_category_confidence?: number;
  ai_value_estimate?: number;
  ai_condition_assessment?: string;
  matching_keywords?: string;
  
  // Dates importantes
  created_at: string;
  updated_at: string;
  published_at?: string;
  expires_at?: string;
  last_activity_at?: string;
}

export enum ListingStatus {
  DRAFT = "draft",
  ACTIVE = "active",
  PAUSED = "paused",
  EXCHANGED = "exchanged",
  EXPIRED = "expired",
  DELETED = "deleted"
}

export enum ListingCondition {
  EXCELLENT = "excellent",
  VERY_GOOD = "very_good",
  GOOD = "good",
  FAIR = "fair",
  POOR = "poor"
}

export interface Image {
  id: number;
  uuid: string;
  filename: string;
  original_filename: string;
  file_path: string;
  file_url: string;
  file_size: number;
  mime_type: string;
  width?: number;
  height?: number;
  alt_text?: string;
  is_primary: boolean;
  uploaded_by: number;
  uploaded_at: string;
  metadata?: Record<string, any>;
}

export interface Exchange {
  id: number;
  uuid: string;
  requester_id: number;
  owner_id: number;
  requester?: User;
  owner?: User;
  
  // Objets de l'échange
  requested_listing_id: number;
  offered_listing_id: number;
  requested_listing?: Listing;
  offered_listing?: Listing;
  
  // Détails de l'échange
  exchange_type: ExchangeType;
  status: ExchangeStatus;
  message?: string;
  
  // Compensation monétaire
  compensation_amount?: number;
  compensation_currency: string;
  compensation_type: CompensationType;
  
  // Planification de la rencontre
  meeting_date?: string;
  meeting_time?: string;
  meeting_location?: string;
  meeting_latitude?: number;
  meeting_longitude?: number;
  meeting_address?: string;
  
  // Évaluation mutuelle
  requester_rating?: number;
  requester_comment?: string;
  owner_rating?: number;
  owner_comment?: string;
  
  // Statut et suivi
  is_urgent: boolean;
  expires_at?: string;
  completed_at?: string;
  cancelled_at?: string;
  cancellation_reason?: string;
  
  // Timestamps
  created_at: string;
  updated_at: string;
  last_activity_at?: string;
}

export enum ExchangeType {
  DIRECT = "direct",
  CHAIN = "chain",
  BOTH = "both"
}

export enum ExchangeStatus {
  PENDING = "pending",
  ACCEPTED = "accepted",
  REJECTED = "rejected",
  COUNTER_OFFER = "counter_offer",
  MEETING_SCHEDULED = "meeting_scheduled",
  COMPLETED = "completed",
  CANCELLED = "cancelled",
  EXPIRED = "expired"
}

export enum CompensationType {
  NONE = "none",
  CASH = "cash",
  BANK_TRANSFER = "bank_transfer",
  PAYPAL = "paypal",
  OTHER = "other"
}

export interface ChatMessage {
  id: number;
  uuid: string;
  chat_room_id: number;
  sender_id: number;
  sender?: User;
  
  // Contenu du message
  content: string;
  message_type: MessageType;
  media_url?: string;
  media_type?: string;
  media_size?: number;
  
  // Statut du message
  is_read: boolean;
  read_at?: string;
  is_edited: boolean;
  edited_at?: string;
  is_deleted: boolean;
  deleted_at?: string;
  
  // Réactions
  reactions?: ChatReaction[];
  
  // Timestamps
  created_at: string;
  updated_at: string;
}

export enum MessageType {
  TEXT = "text",
  IMAGE = "image",
  VIDEO = "video",
  AUDIO = "audio",
  FILE = "file",
  LOCATION = "location",
  SYSTEM = "system"
}

export interface ChatRoom {
  id: number;
  uuid: string;
  name?: string;
  room_type: RoomType;
  
  // Participants
  participants: User[];
  last_message?: ChatMessage;
  
  // Métadonnées
  is_active: boolean;
  created_at: string;
  updated_at: string;
  last_activity_at?: string;
}

export enum RoomType {
  DIRECT = "direct",
  GROUP = "group",
  EXCHANGE = "exchange"
}

export interface ChatReaction {
  id: number;
  message_id: number;
  user_id: number;
  user?: User;
  emoji: string;
  created_at: string;
}

export interface Notification {
  id: number;
  uuid: string;
  user_id: number;
  user?: User;
  
  // Contenu de la notification
  title: string;
  message: string;
  notification_type: NotificationType;
  
  // Données associées
  data?: Record<string, any>;
  related_id?: number;
  related_type?: string;
  
  // Statut
  is_read: boolean;
  read_at?: string;
  is_sent: boolean;
  sent_at?: string;
  
  // Canaux
  email_sent: boolean;
  push_sent: boolean;
  sms_sent: boolean;
  whatsapp_sent: boolean;
  
  // Timestamps
  created_at: string;
  scheduled_for?: string;
}

export enum NotificationType {
  EXCHANGE_REQUEST = "exchange_request",
  EXCHANGE_ACCEPTED = "exchange_accepted",
  EXCHANGE_REJECTED = "exchange_rejected",
  MESSAGE_RECEIVED = "message_received",
  LISTING_VIEWED = "listing_viewed",
  LISTING_LIKED = "listing_liked",
  SYSTEM_UPDATE = "system_update",
  PAYMENT_SUCCESS = "payment_success",
  PAYMENT_FAILED = "payment_failed"
}

export interface Payment {
  id: number;
  uuid: string;
  user_id: number;
  user?: User;
  
  // Détails du paiement
  amount: number;
  currency: string;
  description: string;
  payment_method: PaymentMethod;
  
  // Statut
  status: PaymentStatus;
  transaction_id?: string;
  error_message?: string;
  
  // Métadonnées
  metadata?: Record<string, any>;
  
  // Timestamps
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

export enum PaymentMethod {
  CREDIT_CARD = "credit_card",
  DEBIT_CARD = "debit_card",
  BANK_TRANSFER = "bank_transfer",
  PAYPAL = "paypal",
  APPLE_PAY = "apple_pay",
  GOOGLE_PAY = "google_pay",
  CRYPTO = "crypto"
}

export enum PaymentStatus {
  PENDING = "pending",
  PROCESSING = "processing",
  COMPLETED = "completed",
  FAILED = "failed",
  CANCELLED = "cancelled",
  REFUNDED = "refunded"
}

export interface SearchFilters {
  query?: string;
  category?: string;
  subcategory?: string;
  condition?: ListingCondition[];
  min_price?: number;
  max_price?: number;
  currency?: string;
  location?: string;
  latitude?: number;
  longitude?: number;
  max_distance_km?: number;
  exchange_type?: ExchangeType[];
  is_negotiable?: boolean;
  is_urgent?: boolean;
  is_featured?: boolean;
  brand?: string;
  model?: string;
  color?: string;
  size?: string;
  sort_by?: 'relevance' | 'price_low' | 'price_high' | 'date_new' | 'date_old' | 'distance' | 'trust_score';
  sort_order?: 'asc' | 'desc';
  page?: number;
  per_page?: number;
}

export interface SearchResult {
  listings: Listing[];
  total_count: number;
  page: number;
  per_page: number;
  total_pages: number;
  filters: SearchFilters;
  suggestions?: string[];
  related_categories?: string[];
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  errors?: Record<string, string[]>;
  pagination?: {
    page: number;
    per_page: number;
    total_count: number;
    total_pages: number;
  };
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  token_type: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
  device_id?: string;
  device_info?: Record<string, any>;
}

export interface RegisterData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
  accept_terms: boolean;
}

export interface UserProfile {
  user: User;
  stats: {
    total_listings: number;
    active_listings: number;
    total_exchanges: number;
    successful_exchanges: number;
    total_likes: number;
    total_views: number;
  };
  recent_activity: Array<{
    type: string;
    description: string;
    timestamp: string;
    related_id?: number;
  }>;
}

export interface ListingFormData {
  title: string;
  description: string;
  category: string;
  subcategory?: string;
  brand?: string;
  model?: string;
  color?: string;
  size?: string;
  condition: ListingCondition;
  condition_details?: string;
  estimated_value?: number;
  min_exchange_value?: number;
  max_exchange_value?: number;
  currency: string;
  desired_items?: string;
  desired_categories?: string;
  exchange_type: string;
  address?: string;
  city?: string;
  postal_code?: string;
  country?: string;
  max_distance_km: number;
  is_negotiable: boolean;
  is_urgent: boolean;
  images: File[];
}

export interface ExchangeFormData {
  requested_listing_id: number;
  offered_listing_id: number;
  message: string;
  compensation_amount?: number;
  compensation_currency: string;
  compensation_type: CompensationType;
}

export interface ChatFormData {
  content: string;
  message_type: MessageType;
  media_file?: File;
}

export interface GeolocationData {
  latitude: number;
  longitude: number;
  address: string;
  city: string;
  postal_code: string;
  country: string;
  formatted_address: string;
}

export interface Currency {
  code: string;
  symbol: string;
  name: string;
  rate: number;
}

export interface AppState {
  auth: {
    user: User | null;
    tokens: AuthTokens | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    error: string | null;
  };
  listings: {
    items: Listing[];
    currentListing: Listing | null;
    isLoading: boolean;
    error: string | null;
    filters: SearchFilters;
    pagination: {
      page: number;
      per_page: number;
      total_count: number;
      total_pages: number;
    };
  };
  exchanges: {
    items: Exchange[];
    currentExchange: Exchange | null;
    isLoading: boolean;
    error: string | null;
  };
  chat: {
    rooms: ChatRoom[];
    currentRoom: ChatRoom | null;
    messages: ChatMessage[];
    isLoading: boolean;
    error: string | null;
  };
  notifications: {
    items: Notification[];
    unreadCount: number;
    isLoading: boolean;
    error: string | null;
  };
  ui: {
    currentView: string;
    sidebarOpen: boolean;
    modalOpen: boolean;
    modalType: string | null;
    theme: 'light' | 'dark';
    language: string;
    currency: string;
  };
}
