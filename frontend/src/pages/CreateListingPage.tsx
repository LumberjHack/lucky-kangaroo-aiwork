import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { motion } from 'framer-motion';
import { 
  ArrowLeft, 
  Upload, 
  MapPin, 
  Tag, 
  DollarSign, 
  Calendar,
  Package,
  AlertCircle,
  CheckCircle,
  Camera,
  X
} from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import api from '../services/api';
import ImageUpload from '../components/common/ImageUpload';

interface Category {
  id: string;
  name: string;
  icon: string;
  description: string;
}

interface UploadedImage {
  id: string;
  file: File;
  preview: string;
  url?: string;
  isUploading: boolean;
  isUploaded: boolean;
  error?: string;
}

interface CreateListingForm {
  title: string;
  description: string;
  category_id: string;
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
}

const CreateListingPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploadingImages, setUploadingImages] = useState(false);
  const [images, setImages] = useState<UploadedImage[]>([]);
  const [currentStep, setCurrentStep] = useState(1);
  const [errors, setErrors] = useState<string[]>([]);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors: formErrors }
  } = useForm<CreateListingForm>({
    defaultValues: {
      listing_type: 'exchange',
      condition: 'good',
      currency: 'CHF',
      country: 'CH',
      exchange_type: 'both',
      desired_items: [],
      excluded_items: [],
      tags: []
    }
  });

  const watchedValues = watch();

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await api.get('/listings/categories');
      setCategories(response.data.categories);
    } catch (error) {
      console.error('Erreur lors du chargement des catégories:', error);
    }
  };

  const handleImagesChange = (newImages: UploadedImage[]) => {
    setImages(newImages);
  };

  const onSubmit = async (data: CreateListingForm) => {
    setLoading(true);
    setErrors([]);

    try {
      // Créer l'annonce
      const response = await api.post('/listings', data);
      const listing = response.data.listing;

      // Uploader les images si il y en a
      if (images.length > 0) {
        setUploadingImages(true);
        const formData = new FormData();
        
        for (let i = 0; i < images.length; i++) {
          formData.append('image', images[i].file);
        }

        await api.post(`/listings/${listing.id}/images`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
      }

      // Publier l'annonce
      await api.post(`/listings/${listing.id}/publish`);

      navigate(`/listings/${listing.id}`, {
        state: { message: 'Annonce créée et publiée avec succès !' }
      });

    } catch (error: any) {
      console.error('Erreur lors de la création de l\'annonce:', error);
      setErrors([error.response?.data?.error || 'Erreur lors de la création de l\'annonce']);
    } finally {
      setLoading(false);
      setUploadingImages(false);
    }
  };

  const steps = [
    { number: 1, title: 'Informations de base', icon: Package },
    { number: 2, title: 'Détails et prix', icon: DollarSign },
    { number: 3, title: 'Localisation', icon: MapPin },
    { number: 4, title: 'Photos', icon: Camera },
    { number: 5, title: 'Préférences', icon: Tag }
  ];

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Titre de l'annonce *
              </label>
              <input
                {...register('title', { required: 'Le titre est requis' })}
                type="text"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Ex: iPhone 13 Pro Max 256GB"
              />
              {formErrors.title && (
                <p className="text-red-500 text-sm mt-1">{formErrors.title.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description *
              </label>
              <textarea
                {...register('description', { required: 'La description est requise' })}
                rows={6}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Décrivez votre objet en détail..."
              />
              {formErrors.description && (
                <p className="text-red-500 text-sm mt-1">{formErrors.description.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Catégorie *
              </label>
              <select
                {...register('category_id', { required: 'La catégorie est requise' })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Sélectionnez une catégorie</option>
                {categories.map(category => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
              {formErrors.category_id && (
                <p className="text-red-500 text-sm mt-1">{formErrors.category_id.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Type d'annonce *
              </label>
              <div className="grid grid-cols-3 gap-4">
                {[
                  { value: 'exchange', label: 'Échange', icon: '🔄' },
                  { value: 'sale', label: 'Vente', icon: '💰' },
                  { value: 'both', label: 'Les deux', icon: '🔄💰' }
                ].map(option => (
                  <label key={option.value} className="relative">
                    <input
                      {...register('listing_type')}
                      type="radio"
                      value={option.value}
                      className="sr-only"
                    />
                    <div className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                      watchedValues.listing_type === option.value
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}>
                      <div className="text-2xl mb-2">{option.icon}</div>
                      <div className="font-medium">{option.label}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                État de l'objet
              </label>
              <select
                {...register('condition')}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="new">Neuf</option>
                <option value="excellent">Excellent</option>
                <option value="good">Bon</option>
                <option value="fair">Correct</option>
                <option value="poor">Usé</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Marque
                </label>
                <input
                  {...register('brand')}
                  type="text"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ex: Apple, Samsung..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Modèle
                </label>
                <input
                  {...register('model')}
                  type="text"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ex: iPhone 13 Pro Max"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Année
              </label>
              <input
                {...register('year', { valueAsNumber: true })}
                type="number"
                min="1900"
                max="2030"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="2023"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Valeur estimée
              </label>
              <div className="flex gap-2">
                <input
                  {...register('estimated_value', { valueAsNumber: true })}
                  type="number"
                  min="0"
                  step="0.01"
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="500"
                />
                <select
                  {...register('currency')}
                  className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="CHF">CHF</option>
                  <option value="EUR">EUR</option>
                  <option value="USD">USD</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Prix minimum accepté
                </label>
                <input
                  {...register('price_range_min', { valueAsNumber: true })}
                  type="number"
                  min="0"
                  step="0.01"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="400"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Prix maximum accepté
                </label>
                <input
                  {...register('price_range_max', { valueAsNumber: true })}
                  type="number"
                  min="0"
                  step="0.01"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="600"
                />
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Type d'échange *
              </label>
              <div className="grid grid-cols-3 gap-4">
                {[
                  { value: 'direct', label: 'En main propre', icon: '🤝' },
                  { value: 'shipping', label: 'Envoi', icon: '📦' },
                  { value: 'both', label: 'Les deux', icon: '🤝📦' }
                ].map(option => (
                  <label key={option.value} className="relative">
                    <input
                      {...register('exchange_type')}
                      type="radio"
                      value={option.value}
                      className="sr-only"
                    />
                    <div className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                      watchedValues.exchange_type === option.value
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}>
                      <div className="text-2xl mb-2">{option.icon}</div>
                      <div className="font-medium">{option.label}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Ville
                </label>
                <input
                  {...register('city')}
                  type="text"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Genève"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Code postal
                </label>
                <input
                  {...register('postal_code')}
                  type="text"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="1200"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Lieu de rencontre
              </label>
              <input
                {...register('location_name')}
                type="text"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Ex: Gare Cornavin, Place du Molard..."
              />
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Photos de l'objet
              </label>
              <ImageUpload
                onImagesChange={handleImagesChange}
                maxImages={10}
                maxSize={5}
                className="w-full"
              />
            </div>
          </div>
        );

      case 5:
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Objets/services recherchés
              </label>
              <input
                type="text"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Ex: MacBook, vélo, services de jardinage..."
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    const value = e.currentTarget.value.trim();
                    if (value && !watchedValues.desired_items.includes(value)) {
                      setValue('desired_items', [...watchedValues.desired_items, value]);
                      e.currentTarget.value = '';
                    }
                  }
                }}
              />
              {watchedValues.desired_items.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {watchedValues.desired_items.map((item, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
                    >
                      {item}
                      <button
                        type="button"
                        onClick={() => {
                          setValue('desired_items', watchedValues.desired_items.filter((_, i) => i !== index));
                        }}
                        className="ml-2 text-blue-600 hover:text-blue-800"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Objets/services exclus
              </label>
              <input
                type="text"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Ex: vêtements, livres..."
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    const value = e.currentTarget.value.trim();
                    if (value && !watchedValues.excluded_items.includes(value)) {
                      setValue('excluded_items', [...watchedValues.excluded_items, value]);
                      e.currentTarget.value = '';
                    }
                  }
                }}
              />
              {watchedValues.excluded_items.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {watchedValues.excluded_items.map((item, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-red-100 text-red-800"
                    >
                      {item}
                      <button
                        type="button"
                        onClick={() => {
                          setValue('excluded_items', watchedValues.excluded_items.filter((_, i) => i !== index));
                        }}
                        className="ml-2 text-red-600 hover:text-red-800"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tags
              </label>
              <input
                type="text"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Ex: urgent, neuf, vintage..."
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    const value = e.currentTarget.value.trim();
                    if (value && !watchedValues.tags.includes(value)) {
                      setValue('tags', [...watchedValues.tags, value]);
                      e.currentTarget.value = '';
                    }
                  }
                }}
              />
              {watchedValues.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {watchedValues.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-gray-100 text-gray-800"
                    >
                      {tag}
                      <button
                        type="button"
                        onClick={() => {
                          setValue('tags', watchedValues.tags.filter((_, i) => i !== index));
                        }}
                        className="ml-2 text-gray-600 hover:text-gray-800"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="mx-auto h-12 w-12 text-red-500 mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Connexion requise
          </h2>
          <p className="text-gray-600 mb-4">
            Vous devez être connecté pour créer une annonce.
          </p>
          <button
            onClick={() => navigate('/auth/login')}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
          >
            Se connecter
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="h-5 w-5 mr-2" />
            Retour
          </button>
          <h1 className="text-2xl font-bold text-gray-900">
            Créer une annonce
          </h1>
          <div></div>
        </div>

        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => {
              const Icon = step.icon;
              const isActive = currentStep === step.number;
              const isCompleted = currentStep > step.number;
              
              return (
                <div key={step.number} className="flex items-center">
                  <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                    isActive 
                      ? 'border-blue-500 bg-blue-500 text-white' 
                      : isCompleted 
                        ? 'border-green-500 bg-green-500 text-white'
                        : 'border-gray-300 bg-white text-gray-500'
                  }`}>
                    {isCompleted ? (
                      <CheckCircle className="h-5 w-5" />
                    ) : (
                      <Icon className="h-5 w-5" />
                    )}
                  </div>
                  <div className="ml-3">
                    <p className={`text-sm font-medium ${
                      isActive ? 'text-blue-600' : 'text-gray-500'
                    }`}>
                      {step.title}
                    </p>
                  </div>
                  {index < steps.length - 1 && (
                    <div className={`w-16 h-0.5 mx-4 ${
                      isCompleted ? 'bg-green-500' : 'bg-gray-300'
                    }`} />
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Errors */}
        {errors.length > 0 && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex">
              <AlertCircle className="h-5 w-5 text-red-400 mr-2" />
              <div>
                <h3 className="text-sm font-medium text-red-800">
                  Erreurs
                </h3>
                <ul className="mt-1 text-sm text-red-700 list-disc list-inside">
                  {errors.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Form */}
        <motion.form
          onSubmit={handleSubmit(onSubmit)}
          className="bg-white rounded-lg shadow-sm p-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {renderStepContent()}

          {/* Navigation Buttons */}
          <div className="flex justify-between mt-8">
            <button
              type="button"
              onClick={() => setCurrentStep(Math.max(1, currentStep - 1))}
              disabled={currentStep === 1}
              className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Précédent
            </button>

            {currentStep < 5 ? (
              <button
                type="button"
                onClick={() => setCurrentStep(Math.min(5, currentStep + 1))}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Suivant
              </button>
            ) : (
              <button
                type="submit"
                disabled={loading || uploadingImages}
                className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  'Création...'
                ) : uploadingImages ? (
                  'Upload des images...'
                ) : (
                  'Créer et publier'
                )}
              </button>
            )}
          </div>
        </motion.form>
      </div>
    </div>
  );
};

export default CreateListingPage;
