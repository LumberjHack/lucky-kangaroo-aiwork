import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Search, 
  Filter, 
  MapPin, 
  Sliders, 
  Grid3X3, 
  List, 
  Star, 
  Heart, 
  Eye, 
  MessageCircle,
  X,
  ChevronDown,
  ChevronUp,
  Map,
  DollarSign,
  Tag,
  Calendar,
  User,
  TrendingUp,
  Sparkles
} from 'lucide-react';
import { toast } from 'react-hot-toast';

interface SearchFilters {
  query: string;
  category_id: string;
  listing_type: string;
  condition: string[];
  min_price: number | null;
  max_price: number | null;
  currency: string;
  city: string;
  postal_code: string;
  country: string;
  latitude: number | null;
  longitude: number | null;
  radius_km: number;
  exchange_type: string;
  brand: string;
  model: string;
  year_min: number | null;
  year_max: number | null;
  sort_by: string;
}

interface SearchResult {
  id: string;
  title: string;
  description: string;
  category: {
    id: string;
    name: string;
    slug: string;
    icon: string;
  };
  user: {
    id: string;
    username: string;
    trust_score: number;
    city: string;
  };
  listing_type: string;
  condition: string;
  brand: string;
  model: string;
  year: number;
  estimated_value: number;
  currency: string;
  city: string;
  postal_code: string;
  country: string;
  exchange_type: string;
  views_count: number;
  likes_count: number;
  created_at: string;
  images: Array<{
    id: string;
    url: string;
    alt: string;
    is_primary: boolean;
  }>;
  tags: string[];
  distance_km?: number;
}

interface SearchFiltersData {
  categories: Array<{
    id: string;
    name: string;
    slug: string;
    icon: string;
    description: string;
  }>;
  conditions: string[];
  price_ranges: Array<{
    label: string;
    min: number;
    max: number | null;
  }>;
  cities: string[];
  brands: string[];
  currencies: string[];
  exchange_types: string[];
}

const AdvancedSearchPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  
  // États
  const [filters, setFilters] = useState<SearchFilters>({
    query: searchParams.get('q') || '',
    category_id: searchParams.get('category') || '',
    listing_type: searchParams.get('type') || 'both',
    condition: searchParams.get('condition')?.split(',') || [],
    min_price: searchParams.get('min_price') ? Number(searchParams.get('min_price')) : null,
    max_price: searchParams.get('max_price') ? Number(searchParams.get('max_price')) : null,
    currency: searchParams.get('currency') || 'CHF',
    city: searchParams.get('city') || '',
    postal_code: searchParams.get('postal_code') || '',
    country: searchParams.get('country') || 'CH',
    latitude: searchParams.get('lat') ? Number(searchParams.get('lat')) : null,
    longitude: searchParams.get('lng') ? Number(searchParams.get('lng')) : null,
    radius_km: searchParams.get('radius') ? Number(searchParams.get('radius')) : 25,
    exchange_type: searchParams.get('exchange_type') || 'both',
    brand: searchParams.get('brand') || '',
    model: searchParams.get('model') || '',
    year_min: searchParams.get('year_min') ? Number(searchParams.get('year_min')) : null,
    year_max: searchParams.get('year_max') ? Number(searchParams.get('year_max')) : null,
    sort_by: searchParams.get('sort') || 'relevance'
  });

  const [results, setResults] = useState<SearchResult[]>([]);
  const [filtersData, setFiltersData] = useState<SearchFiltersData | null>(null);
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 20,
    total: 0,
    pages: 0,
    has_next: false,
    has_prev: false
  });

  // Charger les filtres disponibles
  useEffect(() => {
    const loadFiltersData = async () => {
      try {
        const response = await fetch('/api/search/filters');
        const data = await response.json();
        if (data.success) {
          setFiltersData(data.data);
        }
      } catch (error) {
        console.error('Erreur lors du chargement des filtres:', error);
      }
    };

    loadFiltersData();
  }, []);

  // Recherche avec debounce
  const searchWithDebounce = useCallback(
    debounce(async (searchFilters: SearchFilters) => {
      await performSearch(searchFilters);
    }, 500),
    []
  );

  // Effectuer la recherche
  const performSearch = async (searchFilters: SearchFilters) => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      
      // Ajouter tous les filtres non vides
      Object.entries(searchFilters).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '' && value !== 'both') {
          if (Array.isArray(value)) {
            if (value.length > 0) {
              params.append(key, value.join(','));
            }
          } else {
            params.append(key, value.toString());
          }
        }
      });

      const response = await fetch(`/api/search/search?${params.toString()}`);
      const data = await response.json();
      
      if (data.success) {
        setResults(data.data.listings);
        setPagination(data.data.pagination);
      } else {
        toast.error('Erreur lors de la recherche');
      }
    } catch (error) {
      console.error('Erreur lors de la recherche:', error);
      toast.error('Erreur lors de la recherche');
    } finally {
      setLoading(false);
    }
  };

  // Recherche initiale
  useEffect(() => {
    performSearch(filters);
  }, []);

  // Mettre à jour l'URL quand les filtres changent
  useEffect(() => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '' && value !== 'both') {
        if (Array.isArray(value)) {
          if (value.length > 0) {
            params.append(key, value.join(','));
          }
        } else {
          params.append(key, value.toString());
        }
      }
    });
    
    setSearchParams(params);
    searchWithDebounce(filters);
  }, [filters, searchWithDebounce, setSearchParams]);

  // Gestion des suggestions
  const handleInputChange = async (value: string) => {
    setFilters(prev => ({ ...prev, query: value }));
    
    if (value.length >= 2) {
      try {
        const response = await fetch(`/api/search/suggestions?q=${encodeURIComponent(value)}`);
        const data = await response.json();
        if (data.success) {
          setSuggestions(data.data.suggestions.map((s: any) => s.text));
        }
      } catch (error) {
        console.error('Erreur lors du chargement des suggestions:', error);
      }
    } else {
      setSuggestions([]);
    }
  };

  // Fonction de debounce
  function debounce<T extends (...args: any[]) => any>(
    func: T,
    wait: number
  ): (...args: Parameters<T>) => void {
    let timeout: NodeJS.Timeout;
    return (...args: Parameters<T>) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func(...args), wait);
    };
  }

  // Gestion des filtres
  const updateFilter = (key: keyof SearchFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => {
    setFilters({
      query: '',
      category_id: '',
      listing_type: 'both',
      condition: [],
      min_price: null,
      max_price: null,
      currency: 'CHF',
      city: '',
      postal_code: '',
      country: 'CH',
      latitude: null,
      longitude: null,
      radius_km: 25,
      exchange_type: 'both',
      brand: '',
      model: '',
      year_min: null,
      year_max: null,
      sort_by: 'relevance'
    });
  };

  const toggleCondition = (condition: string) => {
    setFilters(prev => ({
      ...prev,
      condition: prev.condition.includes(condition)
        ? prev.condition.filter(c => c !== condition)
        : [...prev.condition, condition]
    }));
  };

  // Géolocalisation
  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          updateFilter('latitude', position.coords.latitude);
          updateFilter('longitude', position.coords.longitude);
        },
        (error) => {
          toast.error('Impossible d\'obtenir votre position');
        }
      );
    } else {
      toast.error('Géolocalisation non supportée');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header de recherche */}
      <div className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-6">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Barre de recherche principale */}
            <div className="flex-1 relative">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="text"
                  placeholder="Rechercher des objets, services, marques..."
                  value={filters.query}
                  onChange={(e) => handleInputChange(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                {filters.query && (
                  <button
                    onClick={() => updateFilter('query', '')}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    <X size={20} />
                  </button>
                )}
              </div>
              
              {/* Suggestions */}
              <AnimatePresence>
                {suggestions.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="absolute top-full left-0 right-0 bg-white border border-gray-200 rounded-lg shadow-lg z-50 mt-1"
                  >
                    {suggestions.map((suggestion, index) => (
                      <button
                        key={index}
                        onClick={() => {
                          updateFilter('query', suggestion);
                          setSuggestions([]);
                        }}
                        className="w-full px-4 py-2 text-left hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
                      >
                        <Search size={16} className="inline mr-2 text-gray-400" />
                        {suggestion}
                      </button>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Boutons d'action */}
            <div className="flex gap-2">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`px-4 py-3 rounded-lg border flex items-center gap-2 ${
                  showFilters 
                    ? 'bg-blue-600 text-white border-blue-600' 
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                }`}
              >
                <Sliders size={20} />
                Filtres
                {Object.values(filters).some(v => 
                  v !== null && v !== undefined && v !== '' && v !== 'both' && 
                  (Array.isArray(v) ? v.length > 0 : true)
                ) && (
                  <span className="bg-red-500 text-white text-xs rounded-full px-2 py-1">
                    {Object.values(filters).filter(v => 
                      v !== null && v !== undefined && v !== '' && v !== 'both' && 
                      (Array.isArray(v) ? v.length > 0 : true)
                    ).length}
                  </span>
                )}
              </button>
              
              <button
                onClick={getCurrentLocation}
                className="px-4 py-3 rounded-lg border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 flex items-center gap-2"
              >
                <MapPin size={20} />
                Ma position
              </button>
            </div>
          </div>

          {/* Filtres rapides */}
          <div className="mt-4 flex flex-wrap gap-2">
            <button
              onClick={() => updateFilter('listing_type', 'good')}
              className={`px-3 py-1 rounded-full text-sm ${
                filters.listing_type === 'good'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Objets
            </button>
            <button
              onClick={() => updateFilter('listing_type', 'service')}
              className={`px-3 py-1 rounded-full text-sm ${
                filters.listing_type === 'service'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Services
            </button>
            <button
              onClick={() => updateFilter('exchange_type', 'direct')}
              className={`px-3 py-1 rounded-full text-sm ${
                filters.exchange_type === 'direct'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Échange direct
            </button>
            <button
              onClick={() => updateFilter('exchange_type', 'chain')}
              className={`px-3 py-1 rounded-full text-sm ${
                filters.exchange_type === 'chain'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Chaîne d'échange
            </button>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-6">
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Sidebar des filtres */}
          <AnimatePresence>
            {showFilters && (
              <motion.div
                initial={{ opacity: 0, x: -300 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -300 }}
                className="lg:w-80 bg-white rounded-lg shadow-sm border p-6 h-fit"
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold">Filtres</h3>
                  <button
                    onClick={clearFilters}
                    className="text-sm text-blue-600 hover:text-blue-800"
                  >
                    Effacer tout
                  </button>
                </div>

                {/* Catégories */}
                {filtersData && (
                  <div className="mb-6">
                    <h4 className="font-medium mb-3">Catégorie</h4>
                    <select
                      value={filters.category_id}
                      onChange={(e) => updateFilter('category_id', e.target.value)}
                      className="w-full p-2 border border-gray-300 rounded-lg"
                    >
                      <option value="">Toutes les catégories</option>
                      {filtersData.categories.map(category => (
                        <option key={category.id} value={category.id}>
                          {category.icon} {category.name}
                        </option>
                      ))}
                    </select>
                  </div>
                )}

                {/* Prix */}
                <div className="mb-6">
                  <h4 className="font-medium mb-3">Prix ({filters.currency})</h4>
                  <div className="grid grid-cols-2 gap-2">
                    <input
                      type="number"
                      placeholder="Min"
                      value={filters.min_price || ''}
                      onChange={(e) => updateFilter('min_price', e.target.value ? Number(e.target.value) : null)}
                      className="p-2 border border-gray-300 rounded-lg"
                    />
                    <input
                      type="number"
                      placeholder="Max"
                      value={filters.max_price || ''}
                      onChange={(e) => updateFilter('max_price', e.target.value ? Number(e.target.value) : null)}
                      className="p-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                </div>

                {/* Condition */}
                {filtersData && (
                  <div className="mb-6">
                    <h4 className="font-medium mb-3">État</h4>
                    <div className="space-y-2">
                      {filtersData.conditions.map(condition => (
                        <label key={condition} className="flex items-center">
                          <input
                            type="checkbox"
                            checked={filters.condition.includes(condition)}
                            onChange={() => toggleCondition(condition)}
                            className="mr-2"
                          />
                          <span className="text-sm capitalize">{condition}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                )}

                {/* Localisation */}
                <div className="mb-6">
                  <h4 className="font-medium mb-3">Localisation</h4>
                  <input
                    type="text"
                    placeholder="Ville"
                    value={filters.city}
                    onChange={(e) => updateFilter('city', e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded-lg mb-2"
                  />
                  <input
                    type="text"
                    placeholder="Code postal"
                    value={filters.postal_code}
                    onChange={(e) => updateFilter('postal_code', e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded-lg"
                  />
                </div>

                {/* Rayon de recherche */}
                {filters.latitude && filters.longitude && (
                  <div className="mb-6">
                    <h4 className="font-medium mb-3">Rayon de recherche</h4>
                    <input
                      type="range"
                      min="1"
                      max="100"
                      value={filters.radius_km}
                      onChange={(e) => updateFilter('radius_km', Number(e.target.value))}
                      className="w-full"
                    />
                    <div className="text-sm text-gray-600 mt-1">
                      {filters.radius_km} km
                    </div>
                  </div>
                )}

                {/* Marque et modèle */}
                <div className="mb-6">
                  <h4 className="font-medium mb-3">Marque</h4>
                  <input
                    type="text"
                    placeholder="Marque"
                    value={filters.brand}
                    onChange={(e) => updateFilter('brand', e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded-lg mb-2"
                  />
                  <input
                    type="text"
                    placeholder="Modèle"
                    value={filters.model}
                    onChange={(e) => updateFilter('model', e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded-lg"
                  />
                </div>

                {/* Année */}
                <div className="mb-6">
                  <h4 className="font-medium mb-3">Année</h4>
                  <div className="grid grid-cols-2 gap-2">
                    <input
                      type="number"
                      placeholder="Min"
                      value={filters.year_min || ''}
                      onChange={(e) => updateFilter('year_min', e.target.value ? Number(e.target.value) : null)}
                      className="p-2 border border-gray-300 rounded-lg"
                    />
                    <input
                      type="number"
                      placeholder="Max"
                      value={filters.year_max || ''}
                      onChange={(e) => updateFilter('year_max', e.target.value ? Number(e.target.value) : null)}
                      className="p-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Contenu principal */}
          <div className="flex-1">
            {/* En-tête des résultats */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">
                  {loading ? 'Recherche en cours...' : `${pagination.total} résultats`}
                </h2>
                {filters.query && (
                  <p className="text-gray-600 mt-1">
                    Résultats pour "{filters.query}"
                  </p>
                )}
              </div>

              <div className="flex items-center gap-4">
                {/* Tri */}
                <select
                  value={filters.sort_by}
                  onChange={(e) => updateFilter('sort_by', e.target.value)}
                  className="p-2 border border-gray-300 rounded-lg"
                >
                  <option value="relevance">Pertinence</option>
                  <option value="date">Plus récent</option>
                  <option value="price_asc">Prix croissant</option>
                  <option value="price_desc">Prix décroissant</option>
                  <option value="distance">Distance</option>
                </select>

                {/* Mode d'affichage */}
                <div className="flex border border-gray-300 rounded-lg">
                  <button
                    onClick={() => setViewMode('grid')}
                    className={`p-2 ${viewMode === 'grid' ? 'bg-blue-600 text-white' : 'text-gray-600'}`}
                  >
                    <Grid3X3 size={20} />
                  </button>
                  <button
                    onClick={() => setViewMode('list')}
                    className={`p-2 ${viewMode === 'list' ? 'bg-blue-600 text-white' : 'text-gray-600'}`}
                  >
                    <List size={20} />
                  </button>
                </div>
              </div>
            </div>

            {/* Résultats */}
            {loading ? (
              <div className="flex justify-center items-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              </div>
            ) : results.length === 0 ? (
              <div className="text-center py-12">
                <Search size={48} className="mx-auto text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Aucun résultat trouvé
                </h3>
                <p className="text-gray-600">
                  Essayez de modifier vos critères de recherche
                </p>
              </div>
            ) : (
              <div className={`grid gap-6 ${
                viewMode === 'grid' 
                  ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3' 
                  : 'grid-cols-1'
              }`}>
                {results.map((result) => (
                  <motion.div
                    key={result.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow cursor-pointer"
                    onClick={() => navigate(`/listings/${result.id}`)}
                  >
                    {/* Image */}
                    <div className="relative h-48 bg-gray-200 rounded-t-lg overflow-hidden">
                      {result.images.length > 0 ? (
                        <img
                          src={result.images[0].url}
                          alt={result.images[0].alt}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-gray-400">
                          <Tag size={48} />
                        </div>
                      )}
                      
                      {/* Badges */}
                      <div className="absolute top-2 left-2 flex gap-2">
                        {result.listing_type === 'service' && (
                          <span className="bg-blue-600 text-white text-xs px-2 py-1 rounded-full">
                            Service
                          </span>
                        )}
                        {result.distance_km && (
                          <span className="bg-green-600 text-white text-xs px-2 py-1 rounded-full">
                            {result.distance_km} km
                          </span>
                        )}
                      </div>

                      {/* Actions */}
                      <div className="absolute top-2 right-2 flex gap-2">
                        <button className="bg-white bg-opacity-80 p-2 rounded-full hover:bg-opacity-100 transition-all">
                          <Heart size={16} />
                        </button>
                        <button className="bg-white bg-opacity-80 p-2 rounded-full hover:bg-opacity-100 transition-all">
                          <MessageCircle size={16} />
                        </button>
                      </div>
                    </div>

                    {/* Contenu */}
                    <div className="p-4">
                      <div className="flex items-start justify-between mb-2">
                        <h3 className="font-semibold text-gray-900 line-clamp-2">
                          {result.title}
                        </h3>
                        <span className="text-lg font-bold text-blue-600">
                          {result.estimated_value} {result.currency}
                        </span>
                      </div>

                      <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                        {result.description}
                      </p>

                      <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
                        <div className="flex items-center gap-1">
                          <MapPin size={14} />
                          {result.city}
                        </div>
                        <div className="flex items-center gap-1">
                          <Eye size={14} />
                          {result.views_count}
                        </div>
                        <div className="flex items-center gap-1">
                          <Calendar size={14} />
                          {new Date(result.created_at).toLocaleDateString()}
                        </div>
                      </div>

                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <User size={16} className="text-gray-400" />
                          <span className="text-sm text-gray-600">
                            {result.user.username}
                          </span>
                          <div className="flex items-center gap-1">
                            <Star size={14} className="text-yellow-400" />
                            <span className="text-sm text-gray-600">
                              {result.user.trust_score}
                            </span>
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-1">
                          <span className="text-xs bg-gray-100 px-2 py-1 rounded-full">
                            {result.category.name}
                          </span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}

            {/* Pagination */}
            {pagination.pages > 1 && (
              <div className="flex justify-center mt-8">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => updateFilter('page', pagination.page - 1)}
                    disabled={!pagination.has_prev}
                    className="px-3 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Précédent
                  </button>
                  
                  {Array.from({ length: Math.min(5, pagination.pages) }, (_, i) => {
                    const page = i + 1;
                    return (
                      <button
                        key={page}
                        onClick={() => updateFilter('page', page)}
                        className={`px-3 py-2 border rounded-lg ${
                          page === pagination.page
                            ? 'bg-blue-600 text-white border-blue-600'
                            : 'border-gray-300 hover:bg-gray-50'
                        }`}
                      >
                        {page}
                      </button>
                    );
                  })}
                  
                  <button
                    onClick={() => updateFilter('page', pagination.page + 1)}
                    disabled={!pagination.has_next}
                    className="px-3 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Suivant
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdvancedSearchPage;
