import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
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
  ChevronUp
} from 'lucide-react';
import AdvancedSearch from '../components/search/AdvancedSearch';

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
    radius: number;
  };
  tags?: string[];
  sort_by?: 'relevance' | 'price_asc' | 'price_desc' | 'date_desc' | 'distance';
  radius?: number;
}

interface SearchResult {
  id: string;
  title: string;
  description: string;
  image: string;
  category: string;
  subcategory: string;
  condition: string;
  location: string;
  distance: number;
  rating: number;
  views: number;
  likes: number;
  price?: number;
  exchangeFor?: string;
  isService: boolean;
  isFeatured: boolean;
  isUrgent: boolean;
  createdAt: string;
  user: {
    name: string;
    avatar: string;
    trustScore: number;
    totalExchanges: number;
  };
}

const SearchPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [filters, setFilters] = useState<SearchFilters>({
    query: searchParams.get('q') || '',
    currency: 'CHF',
    radius: 10,
    sort_by: 'relevance'
  });

  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [showFilters, setShowFilters] = useState(false);
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [totalResults, setTotalResults] = useState(0);

  // Données mockées pour la démo
  const mockResults: SearchResult[] = [
    {
      id: '1',
      title: 'iPhone 13 Pro - Excellent état',
      description: 'iPhone 13 Pro 128GB en excellent état, boîte et accessoires inclus. Échange possible contre MacBook ou iPad.',
      image: '/images/iphone-13.jpg',
      category: 'Électronique',
      subcategory: 'Smartphones',
      condition: 'excellent',
      location: 'Genève',
      distance: 2.5,
      rating: 4.8,
      views: 156,
      likes: 23,
      exchangeFor: 'MacBook Air ou iPad Pro',
      isService: false,
      isFeatured: true,
      isUrgent: false,
      createdAt: '2024-01-15T10:00:00Z',
      user: {
        name: 'Marie D.',
        avatar: '/avatars/marie.jpg',
        trustScore: 95,
        totalExchanges: 23
      }
    },
    {
      id: '2',
      title: 'Cours de guitare à domicile',
      description: 'Cours de guitare pour débutants et intermédiaires, à domicile ou en ligne. Professeur expérimenté.',
      image: '/images/guitar-lessons.jpg',
      category: 'Services',
      subcategory: 'Musique',
      condition: 'new',
      location: 'Lausanne',
      distance: 8.2,
      rating: 4.9,
      views: 89,
      likes: 31,
      price: 45,
      isService: true,
      isFeatured: false,
      isUrgent: true,
      createdAt: '2024-01-14T14:30:00Z',
      user: {
        name: 'Thomas M.',
        avatar: '/avatars/thomas.jpg',
        trustScore: 92,
        totalExchanges: 18
      }
    },
    {
      id: '3',
      title: 'Vélo de ville vintage',
      description: 'Magnifique vélo vintage en excellent état, parfait pour les déplacements urbains.',
      image: '/images/bike-vintage.jpg',
      category: 'Véhicules',
      subcategory: 'Vélos',
      condition: 'very_good',
      location: 'Zurich',
      distance: 15.7,
      rating: 4.7,
      views: 234,
      likes: 45,
      exchangeFor: 'Skateboard ou patins à roues alignées',
      isService: false,
      isFeatured: true,
      isUrgent: false,
      createdAt: '2024-01-13T09:15:00Z',
      user: {
        name: 'Sophie L.',
        avatar: '/avatars/sophie.jpg',
        trustScore: 88,
        totalExchanges: 12
      }
    }
  ];

  const categories = [
    { name: 'Véhicules', subcategories: ['Voitures', 'Motos', 'Vélos', 'Pièces détachées'] },
    { name: 'Maison & Jardin', subcategories: ['Meubles', 'Décoration', 'Outils', 'Plantes'] },
    { name: 'Électronique', subcategories: ['Téléphones', 'Ordinateurs', 'Accessoires', 'Gaming'] },
    { name: 'Livres & Médias', subcategories: ['Livres', 'Films', 'Musique', 'Jeux vidéo'] },
    { name: 'Mode & Beauté', subcategories: ['Vêtements', 'Chaussures', 'Cosmétiques', 'Accessoires'] },
    { name: 'Sport & Loisirs', subcategories: ['Équipements sportifs', 'Instruments de musique', 'Jeux', 'Hobbies'] },
    { name: 'Services', subcategories: ['Formation', 'Conseil', 'Design', 'Maintenance'] }
  ];

  const conditions = [
    { value: 'new', label: 'Neuf' },
    { value: 'excellent', label: 'Excellent' },
    { value: 'very_good', label: 'Très bon' },
    { value: 'good', label: 'Bon' },
    { value: 'fair', label: 'Correct' }
  ];

  const exchangeTypes = [
    { value: 'direct', label: 'Échange direct' },
    { value: 'both', label: 'Échange ou vente' },
    { value: 'sale', label: 'Vente uniquement' }
  ];

  useEffect(() => {
    // Mettre à jour les paramètres d'URL quand les filtres changent
    const params = new URLSearchParams();
    if (filters.query) params.set('q', filters.query);
    if (filters.category) params.set('category', filters.category);
    if (filters.subcategory) params.set('subcategory', filters.subcategory);
    if (filters.condition) params.set('condition', filters.condition);
    if (filters.priceMin > 0) params.set('priceMin', filters.priceMin.toString());
    if (filters.priceMax < 1000) params.set('priceMax', filters.priceMax.toString());
    if (filters.location) params.set('location', filters.location);
    if (filters.distance !== 50) params.set('distance', filters.distance.toString());
    if (filters.exchangeType) params.set('exchangeType', filters.exchangeType);
    if (filters.isService) params.set('isService', 'true');

    setSearchParams(params);
  }, [filters, setSearchParams]);

  useEffect(() => {
    // Simuler la recherche
    setIsLoading(true);
    setTimeout(() => {
      setResults(mockResults);
      setTotalResults(mockResults.length);
      setIsLoading(false);
    }, 1000);
  }, [filters]);

  const handleFilterChange = (key: keyof SearchFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => {
    setFilters({
      query: '',
      category: '',
      subcategory: '',
      condition: '',
      priceMin: 0,
      priceMax: 1000,
      location: '',
      distance: 50,
      exchangeType: '',
      isService: false
    });
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // La recherche se fait automatiquement via useEffect
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header de recherche */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="container mx-auto px-4 py-6">
          <form onSubmit={handleSearch} className="max-w-4xl mx-auto">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Que cherchez-vous ? (objets, services, compétences...)"
                  value={filters.query}
                  onChange={(e) => handleFilterChange('query', e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div className="relative">
                <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Ville ou code postal"
                  value={filters.location}
                  onChange={(e) => handleFilterChange('location', e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <button
                type="submit"
                className="bg-blue-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2"
              >
                <Search className="w-5 h-5" />
                <span>Rechercher</span>
              </button>
            </div>
          </form>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Filtres */}
          <div className="lg:w-80 flex-shrink-0">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900 flex items-center">
                  <Filter className="w-5 h-5 mr-2" />
                  Filtres
                </h2>
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className="lg:hidden"
                >
                  {showFilters ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                </button>
              </div>

              <div className={`lg:block ${showFilters ? 'block' : 'hidden'}`}>
                {/* Catégorie */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Catégorie
                  </label>
                  <select
                    value={filters.category}
                    onChange={(e) => {
                      handleFilterChange('category', e.target.value);
                      handleFilterChange('subcategory', '');
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Toutes les catégories</option>
                    {categories.map((cat) => (
                      <option key={cat.name} value={cat.name}>
                        {cat.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Sous-catégorie */}
                {filters.category && (
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Sous-catégorie
                    </label>
                    <select
                      value={filters.subcategory}
                      onChange={(e) => handleFilterChange('subcategory', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="">Toutes les sous-catégories</option>
                      {categories
                        .find(cat => cat.name === filters.category)
                        ?.subcategories.map((sub) => (
                          <option key={sub} value={sub}>
                            {sub}
                          </option>
                        ))}
                    </select>
                  </div>
                )}

                {/* Type d'échange */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Type d'échange
                  </label>
                  <select
                    value={filters.exchangeType}
                    onChange={(e) => handleFilterChange('exchangeType', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Tous les types</option>
                    {exchangeTypes.map((type) => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Filtres avancés */}
                <div className="mb-6">
                  <button
                    type="button"
                    onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
                    className="flex items-center justify-between w-full text-sm font-medium text-gray-700 hover:text-gray-900"
                  >
                    <span>Filtres avancés</span>
                    {showAdvancedFilters ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </button>

                  {showAdvancedFilters && (
                    <div className="mt-4 space-y-4">
                      {/* Condition */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          État
                        </label>
                        <select
                          value={filters.condition}
                          onChange={(e) => handleFilterChange('condition', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                          <option value="">Tous les états</option>
                          {conditions.map((cond) => (
                            <option key={cond.value} value={cond.value}>
                              {cond.label}
                            </option>
                          ))}
                        </select>
                      </div>

                      {/* Prix */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Fourchette de prix (CHF)
                        </label>
                        <div className="grid grid-cols-2 gap-2">
                          <input
                            type="number"
                            placeholder="Min"
                            value={filters.priceMin || ''}
                            onChange={(e) => handleFilterChange('priceMin', Number(e.target.value) || 0)}
                            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          />
                          <input
                            type="number"
                            placeholder="Max"
                            value={filters.priceMax || ''}
                            onChange={(e) => handleFilterChange('priceMax', Number(e.target.value) || 1000)}
                            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          />
                        </div>
                      </div>

                      {/* Distance */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Distance maximale ({filters.distance} km)
                        </label>
                        <input
                          type="range"
                          min="1"
                          max="100"
                          value={filters.distance}
                          onChange={(e) => handleFilterChange('distance', Number(e.target.value))}
                          className="w-full"
                        />
                      </div>

                      {/* Service uniquement */}
                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id="isService"
                          checked={filters.isService}
                          onChange={(e) => handleFilterChange('isService', e.target.checked)}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <label htmlFor="isService" className="text-sm text-gray-700">
                          Services uniquement
                        </label>
                      </div>
                    </div>
                  )}
                </div>

                {/* Bouton réinitialiser */}
                <button
                  onClick={clearFilters}
                  className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-lg font-medium hover:bg-gray-200 transition-colors flex items-center justify-center space-x-2"
                >
                  <X className="w-4 h-4" />
                  <span>Réinitialiser</span>
                </button>
              </div>
            </div>
          </div>

          {/* Résultats */}
          <div className="flex-1">
            {/* En-tête des résultats */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6">
              <div>
                <h1 className="text-2xl font-bold text-gray-900 mb-2">
                  Résultats de recherche
                </h1>
                <p className="text-gray-600">
                  {totalResults} annonce{totalResults > 1 ? 's' : ''} trouvée{totalResults > 1 ? 's' : ''}
                  {filters.query && ` pour "${filters.query}"`}
                  {filters.location && ` près de ${filters.location}`}
                </p>
              </div>

              {/* Mode d'affichage */}
              <div className="flex items-center space-x-2 mt-4 sm:mt-0">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded-lg transition-colors ${
                    viewMode === 'grid'
                      ? 'bg-blue-100 text-blue-600'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  <Grid3X3 className="w-5 h-5" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded-lg transition-colors ${
                    viewMode === 'list'
                      ? 'bg-blue-100 text-blue-600'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  <List className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Résultats */}
            {isLoading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Recherche en cours...</p>
              </div>
            ) : results.length === 0 ? (
              <div className="text-center py-12">
                <Search className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Aucun résultat trouvé
                </h3>
                <p className="text-gray-600 mb-6">
                  Essayez de modifier vos critères de recherche ou de supprimer certains filtres.
                </p>
                <button
                  onClick={clearFilters}
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
                >
                  Réinitialiser les filtres
                </button>
              </div>
            ) : (
              <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' : 'space-y-4'}>
                {results.map((result) => (
                  <motion.div
                    key={result.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                    className={`bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow ${
                      viewMode === 'list' ? 'flex' : ''
                    }`}
                  >
                    {/* Image */}
                    <div className={`${viewMode === 'list' ? 'w-48 flex-shrink-0' : 'w-full'} h-48 bg-gradient-to-br from-blue-100 to-indigo-200 flex items-center justify-center`}>
                      <span className="text-gray-500 text-sm">Image: {result.title}</span>
                    </div>

                    {/* Contenu */}
                    <div className={`p-4 ${viewMode === 'list' ? 'flex-1' : ''}`}>
                      {/* En-tête */}
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          {result.isFeatured && (
                            <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full font-medium">
                              En vedette
                            </span>
                          )}
                          {result.isUrgent && (
                            <span className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full font-medium">
                              Urgent
                            </span>
                          )}
                          {result.isService && (
                            <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full font-medium">
                              Service
                            </span>
                          )}
                        </div>
                        <button className="p-1 hover:bg-gray-100 rounded transition-colors">
                          <Heart className="w-5 h-5 text-gray-400 hover:text-red-500" />
                        </button>
                      </div>

                      {/* Titre et description */}
                      <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">
                        {result.title}
                      </h3>
                      <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                        {result.description}
                      </p>

                      {/* Informations */}
                      <div className="space-y-2 mb-4">
                        <div className="flex items-center text-sm text-gray-500">
                          <MapPin className="w-4 h-4 mr-1" />
                          <span>{result.location} • {result.distance} km</span>
                        </div>
                        <div className="flex items-center text-sm text-gray-500">
                          <Star className="w-4 h-4 mr-1 text-yellow-400 fill-current" />
                          <span>{result.rating} • {result.user.totalExchanges} échanges</span>
                        </div>
                      </div>

                      {/* Prix ou échange */}
                      {result.isService ? (
                        <div className="text-lg font-bold text-green-600 mb-3">
                          CHF {result.price}/heure
                        </div>
                      ) : (
                        <div className="text-sm text-gray-600 mb-3">
                          <span className="font-medium">Échange contre:</span>
                          <div className="mt-1">{result.exchangeFor}</div>
                        </div>
                      )}

                      {/* Actions */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                          <div className="flex items-center space-x-1">
                            <Eye className="w-4 h-4" />
                            <span>{result.views}</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <Heart className="w-4 h-4" />
                            <span>{result.likes}</span>
                          </div>
                        </div>
                        
                        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors flex items-center space-x-2">
                          <MessageCircle className="w-4 h-4" />
                          <span>Contacter</span>
                        </button>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SearchPage;
