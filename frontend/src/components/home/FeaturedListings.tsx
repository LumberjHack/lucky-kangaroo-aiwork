import React from 'react';
import { motion } from 'framer-motion';
import { Star, MapPin, Heart, Eye, MessageCircle } from 'lucide-react';

interface FeaturedListing {
  id: string;
  title: string;
  description: string;
  image: string;
  category: string;
  location: string;
  rating: number;
  views: number;
  likes: number;
  price?: string;
  exchangeFor?: string;
  isService: boolean;
}

const FeaturedListings: React.FC = () => {
  const featuredListings: FeaturedListing[] = [
    {
      id: '1',
      title: 'Vélo de ville vintage',
      description: 'Magnifique vélo vintage en excellent état, parfait pour les déplacements urbains',
      image: '/images/bike-vintage.jpg',
      category: 'Véhicules',
      location: 'Genève',
      rating: 4.8,
      views: 156,
      likes: 23,
      exchangeFor: 'Skateboard ou patins à roues alignées',
      isService: false
    },
    {
      id: '2',
      title: 'Cours de guitare',
      description: 'Cours de guitare pour débutants et intermédiaires, à domicile ou en ligne',
      image: '/images/guitar-lessons.jpg',
      category: 'Services',
      location: 'Lausanne',
      rating: 4.9,
      views: 89,
      likes: 31,
      isService: true,
      price: 'CHF 45/heure'
    },
    {
      id: '3',
      title: 'iPhone 12 Pro',
      description: 'iPhone 12 Pro 128GB en parfait état, avec coque et chargeur',
      image: '/images/iphone-12.jpg',
      category: 'Électronique',
      location: 'Zurich',
      rating: 4.7,
      views: 234,
      likes: 45,
      exchangeFor: 'MacBook Air ou iPad Pro',
      isService: false
    },
    {
      id: '4',
      title: 'Massage relaxant',
      description: 'Massage thérapeutique et relaxant, détente garantie',
      image: '/images/massage.jpg',
      category: 'Services médicaux & paramédicaux',
      location: 'Berne',
      rating: 5.0,
      views: 67,
      likes: 28,
      isService: true,
      price: 'CHF 80/session'
    },
    {
      id: '5',
      title: 'Canapé convertible',
      description: 'Canapé convertible en cuir, parfait pour petit espace',
      image: '/images/sofa.jpg',
      category: 'Maison & Jardin',
      location: 'Bâle',
      rating: 4.6,
      views: 123,
      likes: 19,
      exchangeFor: 'Table basse + chaises',
      isService: false
    },
    {
      id: '6',
      title: 'Cours de yoga',
      description: 'Cours de yoga pour tous niveaux, en groupe ou privé',
      image: '/images/yoga.jpg',
      category: 'Services',
      location: 'Lugano',
      rating: 4.8,
      views: 78,
      likes: 22,
      isService: true,
      price: 'CHF 25/cours'
    }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.5
      }
    }
  };

  return (
    <section className="py-20 bg-white">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Annonces en vedette
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Découvrez une sélection d'objets et services de qualité proposés par notre communauté
          </p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
        >
          {featuredListings.map((listing) => (
            <motion.div
              key={listing.id}
              variants={itemVariants}
              className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2 border border-gray-100"
            >
              <div className="relative">
                <div className="w-full h-48 bg-gradient-to-br from-blue-100 to-indigo-200 rounded-t-2xl flex items-center justify-center">
                  <span className="text-gray-500 text-sm">Image: {listing.title}</span>
                </div>
                
                {listing.isService && (
                  <div className="absolute top-4 left-4 bg-blue-500 text-white px-3 py-1 rounded-full text-sm font-medium">
                    Service
                  </div>
                )}
                
                <div className="absolute top-4 right-4">
                  <button className="p-2 bg-white rounded-full shadow-md hover:bg-gray-50 transition-colors">
                    <Heart className="w-5 h-5 text-gray-600" />
                  </button>
                </div>
              </div>

              <div className="p-6">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm font-medium text-blue-600 bg-blue-50 px-3 py-1 rounded-full">
                    {listing.category}
                  </span>
                  <div className="flex items-center space-x-1">
                    <Star className="w-4 h-4 text-yellow-400 fill-current" />
                    <span className="text-sm font-medium text-gray-700">
                      {listing.rating}
                    </span>
                  </div>
                </div>

                <h3 className="text-xl font-bold text-gray-900 mb-2 line-clamp-2">
                  {listing.title}
                </h3>
                
                <p className="text-gray-600 mb-4 line-clamp-2">
                  {listing.description}
                </p>

                <div className="flex items-center text-gray-500 mb-4">
                  <MapPin className="w-4 h-4 mr-2" />
                  <span className="text-sm">{listing.location}</span>
                </div>

                {listing.isService ? (
                  <div className="text-lg font-bold text-green-600 mb-4">
                    {listing.price}
                  </div>
                ) : (
                  <div className="text-sm text-gray-600 mb-4">
                    <span className="font-medium">Échange contre:</span>
                    <div className="mt-1">{listing.exchangeFor}</div>
                  </div>
                )}

                <div className="flex items-center justify-between text-sm text-gray-500">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-1">
                      <Eye className="w-4 h-4" />
                      <span>{listing.views}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Heart className="w-4 h-4" />
                      <span>{listing.likes}</span>
                    </div>
                  </div>
                  
                  <button className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                    <MessageCircle className="w-4 h-4" />
                    <span>Contacter</span>
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="text-center mt-16"
        >
          <button className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-8 py-4 rounded-full text-lg font-semibold hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 transform hover:scale-105 shadow-lg">
            Voir toutes les annonces
          </button>
        </motion.div>
      </div>
    </section>
  );
};

export default FeaturedListings;
