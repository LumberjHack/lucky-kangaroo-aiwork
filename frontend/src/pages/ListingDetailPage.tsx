import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ArrowLeft, 
  MapPin, 
  Calendar, 
  Eye, 
  Heart, 
  Share2, 
  MessageCircle,
  User,
  Shield,
  Star,
  Clock,
  Package,
  DollarSign,
  Tag,
  AlertTriangle,
  CheckCircle,
  X
} from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import api from '../services/api';

interface Listing {
  id: string;
  title: string;
  description: string;
  category_id: string;
  category_name?: string;
  listing_type: 'exchange' | 'sale' | 'both';
  condition: 'new' | 'excellent' | 'good' | 'fair' | 'poor';
  brand?: string;
  model?: string;
  year?: number;
  estimated_value?: number;
  price_range_min?: number;
  price_range_max?: number;
  currency: string;
  location_name?: string;
  latitude?: number;
  longitude?: number;
  city?: string;
  postal_code?: string;
  country: string;
  exchange_type: 'direct' | 'shipping' | 'both';
  desired_items: string[];
  excluded_items: string[];
  tags: string[];
  status: string;
  views_count: number;
  likes_count: number;
  created_at: string;
  published_at?: string;
  expires_at?: string;
  user: {
    id: string;
    username: string;
    first_name: string;
    last_name: string;
    profile_picture?: string;
    trust_score: number;
    total_exchanges: number;
    successful_exchanges: number;
    created_at: string;
  };
  images: Array<{
    id: string;
    filename: string;
    file_path: string;
    is_main: boolean;
    sort_order: number;
  }>;
}

const ListingDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();
  const [listing, setListing] = useState<Listing | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [showImageModal, setShowImageModal] = useState(false);
  const [liked, setLiked] = useState(false);
  const [showContactModal, setShowContactModal] = useState(false);

  useEffect(() => {
    if (id) {
      fetchListing();
    }
  }, [id]);

  useEffect(() => {
    if (location.state?.message) {
      // Afficher un message de succès si présent
      setTimeout(() => {
        // Le message sera affiché par le composant parent
      }, 100);
    }
  }, [location.state]);

  const fetchListing = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/listings/${id}`);
      setListing(response.data.listing);
    } catch (error: any) {
      console.error('Erreur lors du chargement de l\'annonce:', error);
      setError(error.response?.data?.error || 'Erreur lors du chargement de l\'annonce');
    } finally {
      setLoading(false);
    }
  };

  const handleLike = async () => {
    if (!user) {
      navigate('/auth/login');
      return;
    }

    try {
      await api.post(`/listings/${id}/like`);
      setLiked(true);
      if (listing) {
        setListing({
          ...listing,
          likes_count: listing.likes_count + 1
        });
      }
    } catch (error) {
      console.error('Erreur lors du like:', error);
    }
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: listing?.title,
          text: listing?.description,
          url: window.location.href
        });
      } catch (error) {
        console.error('Erreur lors du partage:', error);
      }
    } else {
      // Fallback: copier l'URL dans le presse-papiers
      navigator.clipboard.writeText(window.location.href);
      // Afficher une notification de succès
    }
  };

  const handleContact = () => {
    if (!user) {
      navigate('/auth/login');
      return;
    }
    setShowContactModal(true);
  };

  const getConditionLabel = (condition: string) => {
    const labels = {
      'new': 'Neuf',
      'excellent': 'Excellent',
      'good': 'Bon',
      'fair': 'Correct',
      'poor': 'Usé'
    };
    return labels[condition as keyof typeof labels] || condition;
  };

  const getConditionColor = (condition: string) => {
    const colors = {
      'new': 'bg-green-100 text-green-800',
      'excellent': 'bg-blue-100 text-blue-800',
      'good': 'bg-yellow-100 text-yellow-800',
      'fair': 'bg-orange-100 text-orange-800',
      'poor': 'bg-red-100 text-red-800'
    };
    return colors[condition as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  const getListingTypeIcon = (type: string) => {
    switch (type) {
      case 'exchange': return '🔄';
      case 'sale': return '💰';
      case 'both': return '🔄💰';
      default: return '📦';
    }
  };

  const getExchangeTypeIcon = (type: string) => {
    switch (type) {
      case 'direct': return '🤝';
      case 'shipping': return '📦';
      case 'both': return '🤝📦';
      default: return '📦';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatPrice = (price: number, currency: string) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: currency
    }).format(price);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement de l'annonce...</p>
        </div>
      </div>
    );
  }

  if (error || !listing) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="mx-auto h-12 w-12 text-red-500 mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Erreur
          </h2>
          <p className="text-gray-600 mb-4">
            {error || 'Annonce non trouvée'}
          </p>
          <button
            onClick={() => navigate('/')}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
          >
            Retour à l'accueil
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="h-5 w-5 mr-2" />
            Retour
          </button>
          <div className="flex items-center space-x-4">
            <button
              onClick={handleLike}
              className={`flex items-center px-4 py-2 rounded-lg border ${
                liked 
                  ? 'bg-red-50 border-red-200 text-red-600' 
                  : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
              }`}
            >
              <Heart className={`h-4 w-4 mr-2 ${liked ? 'fill-current' : ''}`} />
              {listing.likes_count}
            </button>
            <button
              onClick={handleShare}
              className="flex items-center px-4 py-2 bg-white border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50"
            >
              <Share2 className="h-4 w-4 mr-2" />
              Partager
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Images */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm overflow-hidden">
              {listing.images && listing.images.length > 0 ? (
                <div className="relative">
                  <img
                    src={listing.images[selectedImageIndex]?.file_path}
                    alt={listing.title}
                    className="w-full h-96 object-cover cursor-pointer"
                    onClick={() => setShowImageModal(true)}
                  />
                  
                  {listing.images.length > 1 && (
                    <div className="absolute bottom-4 left-4 right-4">
                      <div className="flex space-x-2 overflow-x-auto">
                        {listing.images.map((image, index) => (
                          <button
                            key={image.id}
                            onClick={() => setSelectedImageIndex(index)}
                            className={`flex-shrink-0 w-16 h-16 rounded-lg overflow-hidden border-2 ${
                              index === selectedImageIndex 
                                ? 'border-blue-500' 
                                : 'border-white'
                            }`}
                          >
                            <img
                              src={image.file_path}
                              alt={`${listing.title} ${index + 1}`}
                              className="w-full h-full object-cover"
                            />
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="w-full h-96 bg-gray-200 flex items-center justify-center">
                  <Package className="h-16 w-16 text-gray-400" />
                </div>
              )}
            </div>
          </div>

          {/* Informations principales */}
          <div className="space-y-6">
            {/* Titre et prix */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-start justify-between mb-4">
                <h1 className="text-2xl font-bold text-gray-900 flex-1">
                  {listing.title}
                </h1>
                <span className="text-2xl ml-4">
                  {getListingTypeIcon(listing.listing_type)}
                </span>
              </div>

              {listing.estimated_value && (
                <div className="text-3xl font-bold text-green-600 mb-4">
                  {formatPrice(listing.estimated_value, listing.currency)}
                </div>
              )}

              <div className="flex items-center space-x-4 text-sm text-gray-500 mb-4">
                <div className="flex items-center">
                  <Eye className="h-4 w-4 mr-1" />
                  {listing.views_count} vues
                </div>
                <div className="flex items-center">
                  <Calendar className="h-4 w-4 mr-1" />
                  {formatDate(listing.created_at)}
                </div>
              </div>

              <div className="flex items-center space-x-2 mb-4">
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getConditionColor(listing.condition)}`}>
                  {getConditionLabel(listing.condition)}
                </span>
                {listing.brand && (
                  <span className="px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-sm">
                    {listing.brand}
                  </span>
                )}
                {listing.model && (
                  <span className="px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-sm">
                    {listing.model}
                  </span>
                )}
              </div>

              <button
                onClick={handleContact}
                className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
              >
                <MessageCircle className="h-5 w-5 inline mr-2" />
                Contacter le vendeur
              </button>
            </div>

            {/* Informations du vendeur */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Vendeur
              </h3>
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center">
                  {listing.user.profile_picture ? (
                    <img
                      src={listing.user.profile_picture}
                      alt={listing.user.username}
                      className="w-12 h-12 rounded-full object-cover"
                    />
                  ) : (
                    <User className="h-6 w-6 text-gray-400" />
                  )}
                </div>
                <div className="flex-1">
                  <p className="font-medium text-gray-900">
                    {listing.user.first_name} {listing.user.last_name}
                  </p>
                  <p className="text-sm text-gray-500">
                    @{listing.user.username}
                  </p>
                  <div className="flex items-center mt-1">
                    <Shield className="h-4 w-4 text-green-500 mr-1" />
                    <span className="text-sm text-gray-600">
                      Score de confiance: {listing.user.trust_score}/100
                    </span>
                  </div>
                </div>
              </div>
              <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-500">Échanges totaux</p>
                  <p className="font-medium">{listing.user.total_exchanges}</p>
                </div>
                <div>
                  <p className="text-gray-500">Échanges réussis</p>
                  <p className="font-medium">{listing.user.successful_exchanges}</p>
                </div>
              </div>
            </div>

            {/* Localisation */}
            {(listing.city || listing.location_name) && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Localisation
                </h3>
                <div className="flex items-start space-x-3">
                  <MapPin className="h-5 w-5 text-gray-400 mt-0.5" />
                  <div>
                    {listing.location_name && (
                      <p className="font-medium text-gray-900">
                        {listing.location_name}
                      </p>
                    )}
                    {listing.city && (
                      <p className="text-gray-600">
                        {listing.city}
                        {listing.postal_code && `, ${listing.postal_code}`}
                      </p>
                    )}
                    <div className="flex items-center mt-2">
                      <span className="text-sm text-gray-500 mr-2">
                        {getExchangeTypeIcon(listing.exchange_type)}
                      </span>
                      <span className="text-sm text-gray-600">
                        {listing.exchange_type === 'direct' && 'En main propre'}
                        {listing.exchange_type === 'shipping' && 'Envoi possible'}
                        {listing.exchange_type === 'both' && 'En main propre ou envoi'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Description et détails */}
        <div className="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Description
              </h3>
              <div className="prose max-w-none">
                <p className="text-gray-700 whitespace-pre-wrap">
                  {listing.description}
                </p>
              </div>
            </div>

            {/* Tags */}
            {listing.tags && listing.tags.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm p-6 mt-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Tags
                </h3>
                <div className="flex flex-wrap gap-2">
                  {listing.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-sm"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Objets recherchés */}
            {listing.desired_items && listing.desired_items.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm p-6 mt-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Objets/services recherchés
                </h3>
                <div className="flex flex-wrap gap-2">
                  {listing.desired_items.map((item, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                    >
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Objets exclus */}
            {listing.excluded_items && listing.excluded_items.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm p-6 mt-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Objets/services exclus
                </h3>
                <div className="flex flex-wrap gap-2">
                  {listing.excluded_items.map((item, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm"
                    >
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Informations supplémentaires */}
          <div className="space-y-6">
            {/* Détails techniques */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Détails
              </h3>
              <div className="space-y-3">
                {listing.year && (
                  <div className="flex justify-between">
                    <span className="text-gray-500">Année</span>
                    <span className="font-medium">{listing.year}</span>
                  </div>
                )}
                {listing.price_range_min && listing.price_range_max && (
                  <div className="flex justify-between">
                    <span className="text-gray-500">Fourchette de prix</span>
                    <span className="font-medium">
                      {formatPrice(listing.price_range_min, listing.currency)} - {formatPrice(listing.price_range_max, listing.currency)}
                    </span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-gray-500">Type</span>
                  <span className="font-medium">
                    {listing.listing_type === 'exchange' && 'Échange'}
                    {listing.listing_type === 'sale' && 'Vente'}
                    {listing.listing_type === 'both' && 'Échange ou vente'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Statut</span>
                  <span className="font-medium capitalize">{listing.status}</span>
                </div>
              </div>
            </div>

            {/* Sécurité */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Sécurité
              </h3>
              <div className="space-y-3">
                <div className="flex items-center text-sm text-gray-600">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                  Vendeur vérifié
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <Shield className="h-4 w-4 text-green-500 mr-2" />
                  Score de confiance élevé
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <Clock className="h-4 w-4 text-green-500 mr-2" />
                  Membre depuis {formatDate(listing.user.created_at)}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Modal d'image */}
      {showImageModal && listing.images && listing.images.length > 0 && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
          <div className="relative max-w-4xl max-h-full p-4">
            <button
              onClick={() => setShowImageModal(false)}
              className="absolute top-4 right-4 text-white hover:text-gray-300 z-10"
            >
              <X className="h-8 w-8" />
            </button>
            <img
              src={listing.images[selectedImageIndex]?.file_path}
              alt={listing.title}
              className="max-w-full max-h-full object-contain"
            />
            {listing.images.length > 1 && (
              <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2">
                <div className="flex space-x-2">
                  {listing.images.map((_, index) => (
                    <button
                      key={index}
                      onClick={() => setSelectedImageIndex(index)}
                      className={`w-3 h-3 rounded-full ${
                        index === selectedImageIndex ? 'bg-white' : 'bg-white bg-opacity-50'
                      }`}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ListingDetailPage;
