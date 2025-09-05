import React, { useState, useEffect } from 'react';
import { Search, MapPin, Filter, X, SlidersHorizontal } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface SearchFilters {
  query: string;
  category_id?: string;
  listing_type?: 'exchange' | 'sale' | 'both';
  condition?: 'new' | 'excellent' | 'good' | 'fair' | 'poor';
  price_min?: number;
  price_max?: number;
  currency?: string;
  location?: {
    latitude: number;
    longitude: number;
    radius: number; // en km
  };
  tags?: string[];
  sort_by?: 'relevance' | 'price_asc' | 'price_desc' | 'date_desc' | 'distance';
  radius?: number;
}

interface Category {
  id: string;
  name: string;
  icon: string;
  description: string;
}

interface AdvancedSearchProps {
  onSearch: (filters: SearchFilters) => void;
  onLocationChange?: (location: { latitude: number; longitude: number }) => void;
  initialFilters?: Partial<SearchFilters>;
  className?: string;
}

const AdvancedSearch: React.FC<AdvancedSearchProps> = ({
  onSearch,
  onLocationChange,
  initialFilters = {},
  className = ''
}) => {
  const [filters, setFilters] = useState<SearchFilters>({
    query: '',
    currency: 'CHF',
    radius: 10,
    sort_by: 'relevance',
    ...initialFilters
  });
  
  const [categories, setCategories] = useState<Category[]>([]);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [locationPermission, setLocationPermission] = useState<'granted' | 'denied' | 'prompt'>('prompt');
  const [userLocation, setUserLocation] = useState<{ latitude: number; longitude: number } | null>(null);

  useEffect(() => {
    fetchCategories();
    checkLocationPermission();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/listings/categories');
      if (response.ok) {
        const data = await response.json();
        setCategories(data.categories || []);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des catégories:', error);
    }
  };

  const checkLocationPermission = async () => {
    if (!navigator.geolocation) {
      setLocationPermission('denied');
      return;
    }

    try {
      const permission = await navigator.permissions.query({ name: 'geolocation' as PermissionName });
      setLocationPermission(permission.state);
    } catch (error) {
      console.log('Permission API not supported');
    }
  };

  const getCurrentLocation = () => {
    if (!navigator.geolocation) {
      alert('La géolocalisation n\'est pas supportée par ce navigateur');
      return;
    }

    setIsLoading(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const location = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude
        };
        
        setUserLocation(location);
        setFilters(prev => ({
          ...prev,
          location: {
            ...location,
            radius: prev.radius || 10
          }
        }));
        
        onLocationChange?.(location);
        setLocationPermission('granted');
        setIsLoading(false);
      },
      (error) => {
        console.error('Erreur de géolocalisation:', error);
        setLocationPermission('denied');
        setIsLoading(false);
        
        switch (error.code) {
          case error.PERMISSION_DENIED:
            alert('Accès à la localisation refusé. Veuillez autoriser l\'accès dans les paramètres de votre navigateur.');
            break;
          case error.POSITION_UNAVAILABLE:
            alert('Position indisponible.');
            break;
          case error.TIMEOUT:
            alert('Délai d\'attente dépassé.');
            break;
        }
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000 // 5 minutes
      }
    );
  };

  const handleInputChange = (field: keyof SearchFilters, value: any) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleLocationChange = (field: 'latitude' | 'longitude' | 'radius', value: number) => {
    setFilters(prev => ({
      ...prev,
      location: {
        ...prev.location!,
        [field]: value
      }
    }));
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(filters);
  };

  const clearFilters = () => {
    setFilters({
      query: '',
      currency: 'CHF',
      radius: 10,
      sort_by: 'relevance'
    });
    setUserLocation(null);
  };

  const hasActiveFilters = () => {
    return !!(
      filters.query ||
      filters.category_id ||
      filters.listing_type ||
      filters.condition ||
      filters.price_min ||
      filters.price_max ||
      filters.location ||
      filters.tags?.length
    );
  };

  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 ${className}`}>
      <form onSubmit={handleSearch} className="p-6">
        {/* Barre de recherche principale */}
        <div className="flex gap-3 mb-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              value={filters.query}
              onChange={(e) => handleInputChange('query', e.target.value)}
              placeholder="Rechercher des objets, services..."
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className={`px-4 py-3 border rounded-lg flex items-center gap-2 transition-colors ${
              showAdvanced || hasActiveFilters()
                ? 'border-blue-500 bg-blue-50 text-blue-700'
                : 'border-gray-300 text-gray-700 hover:bg-gray-50'
            }`}
          >
            <SlidersHorizontal className="w-5 h-5" />
            <span className="hidden sm:inline">Filtres</span>
            {hasActiveFilters() && (
              <span className="bg-blue-500 text-white text-xs rounded-full px-2 py-1">
                {Object.values(filters).filter(v => v && v !== 'CHF' && v !== 10 && v !== 'relevance').length}
              </span>
            )}
          </button>
          
          <button
            type="submit"
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Rechercher
          </button>
        </div>

        {/* Filtres avancés */}
        <AnimatePresence>
          {showAdvanced && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="border-t border-gray-200 pt-4"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* Catégorie */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Catégorie
                  </label>
                  <select
                    value={filters.category_id || ''}
                    onChange={(e) => handleInputChange('category_id', e.target.value || undefined)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Toutes les catégories</option>
                    {categories.map(category => (
                      <option key={category.id} value={category.id}>
                        {category.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Type d'annonce */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Type
                  </label>
                  <select
                    value={filters.listing_type || ''}
                    onChange={(e) => handleInputChange('listing_type', e.target.value || undefined)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Tous les types</option>
                    <option value="exchange">Échange</option>
                    <option value="sale">Vente</option>
                    <option value="both">Les deux</option>
                  </select>
                </div>

                {/* État */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    État
                  </label>
                  <select
                    value={filters.condition || ''}
                    onChange={(e) => handleInputChange('condition', e.target.value || undefined)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Tous les états</option>
                    <option value="new">Neuf</option>
                    <option value="excellent">Excellent</option>
                    <option value="good">Bon</option>
                    <option value="fair">Correct</option>
                    <option value="poor">Usé</option>
                  </select>
                </div>

                {/* Prix minimum */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Prix minimum
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="number"
                      value={filters.price_min || ''}
                      onChange={(e) => handleInputChange('price_min', e.target.value ? Number(e.target.value) : undefined)}
                      placeholder="0"
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <select
                      value={filters.currency || 'CHF'}
                      onChange={(e) => handleInputChange('currency', e.target.value)}
                      className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="CHF">CHF</option>
                      <option value="EUR">EUR</option>
                      <option value="USD">USD</option>
                    </select>
                  </div>
                </div>

                {/* Prix maximum */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Prix maximum
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="number"
                      value={filters.price_max || ''}
                      onChange={(e) => handleInputChange('price_max', e.target.value ? Number(e.target.value) : undefined)}
                      placeholder="∞"
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <select
                      value={filters.currency || 'CHF'}
                      onChange={(e) => handleInputChange('currency', e.target.value)}
                      className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="CHF">CHF</option>
                      <option value="EUR">EUR</option>
                      <option value="USD">USD</option>
                    </select>
                  </div>
                </div>

                {/* Tri */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Trier par
                  </label>
                  <select
                    value={filters.sort_by || 'relevance'}
                    onChange={(e) => handleInputChange('sort_by', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="relevance">Pertinence</option>
                    <option value="price_asc">Prix croissant</option>
                    <option value="price_desc">Prix décroissant</option>
                    <option value="date_desc">Plus récent</option>
                    <option value="distance">Distance</option>
                  </select>
                </div>
              </div>

              {/* Géolocalisation */}
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-medium text-gray-700 flex items-center gap-2">
                    <MapPin className="w-4 h-4" />
                    Localisation
                  </h3>
                  
                  {!userLocation && (
                    <button
                      type="button"
                      onClick={getCurrentLocation}
                      disabled={isLoading}
                      className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
                    >
                      {isLoading ? 'Localisation...' : 'Utiliser ma position'}
                    </button>
                  )}
                </div>

                {userLocation ? (
                  <div className="space-y-3">
                    <div className="flex items-center gap-2 text-sm text-green-600">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span>Position détectée: {userLocation.latitude.toFixed(4)}, {userLocation.longitude.toFixed(4)}</span>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <label className="text-sm text-gray-600">Rayon:</label>
                      <input
                        type="range"
                        min="1"
                        max="100"
                        value={filters.location?.radius || 10}
                        onChange={(e) => handleLocationChange('radius', Number(e.target.value))}
                        className="flex-1"
                      />
                      <span className="text-sm text-gray-600 w-12">
                        {filters.location?.radius || 10} km
                      </span>
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">
                    Activez la géolocalisation pour rechercher près de chez vous
                  </p>
                )}
              </div>

              {/* Actions */}
              <div className="flex justify-between items-center mt-4 pt-4 border-t border-gray-200">
                <button
                  type="button"
                  onClick={clearFilters}
                  className="text-sm text-gray-600 hover:text-gray-800 flex items-center gap-1"
                >
                  <X className="w-4 h-4" />
                  Effacer tous les filtres
                </button>
                
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => setShowAdvanced(false)}
                    className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    Fermer
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Rechercher
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </form>
    </div>
  );
};

export default AdvancedSearch;
