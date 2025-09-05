import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Star, Quote, ChevronLeft, ChevronRight, MapPin, Calendar } from 'lucide-react';

interface Testimonial {
  id: string;
  name: string;
  location: string;
  avatar: string;
  rating: number;
  content: string;
  date: string;
  category: string;
  exchange: string;
}

const TestimonialsSection: React.FC = () => {
  const [currentIndex, setCurrentIndex] = useState(0);

  const testimonials: Testimonial[] = [
    {
      id: '1',
      name: 'Marie Dubois',
      location: 'Genève',
      avatar: '/avatars/marie.jpg',
      rating: 5,
      content: 'Lucky Kangaroo a révolutionné ma façon de consommer ! J\'ai échangé mon vélo contre un skateboard, puis le skateboard contre des cours de guitare. C\'est incroyable de voir comment un objet peut se transformer en expérience.',
      date: 'Il y a 2 semaines',
      category: 'Véhicules → Sport → Services',
      exchange: 'Vélo vintage → Skateboard → Cours de guitare'
    },
    {
      id: '2',
      name: 'Thomas Müller',
      location: 'Zurich',
      avatar: '/avatars/thomas.jpg',
      rating: 5,
      content: 'En tant que développeur, j\'ai pu échanger mes compétences contre des services de design. La plateforme est intuitive et sécurisée. J\'ai rencontré des personnes formidables et créé de vrais partenariats.',
      date: 'Il y a 1 mois',
      category: 'Services → Services',
      exchange: 'Développement web → Design graphique'
    },
    {
      id: '3',
      name: 'Sophie Laurent',
      location: 'Lausanne',
      avatar: '/avatars/sophie.jpg',
      rating: 5,
      content: 'J\'ai trouvé exactement ce que je cherchais pour ma chambre d\'enfant. L\'échange s\'est fait en toute simplicité et j\'ai même fait une nouvelle amie ! La communauté est vraiment bienveillante.',
      date: 'Il y a 3 semaines',
      category: 'Maison & Jardin',
      exchange: 'Lampe de bureau → Table de chevet + coussins'
    },
    {
      id: '4',
      name: 'Lucas Rossi',
      location: 'Berne',
      avatar: '/avatars/lucas.jpg',
      rating: 4,
      content: 'Excellente expérience ! J\'ai pu me débarrasser de mon ancien iPhone et obtenir un MacBook en échange. Le processus de vérification est rassurant et le support client est très réactif.',
      date: 'Il y a 2 mois',
      category: 'Électronique',
      exchange: 'iPhone 11 → MacBook Air 2019'
    },
    {
      id: '5',
      name: 'Emma Schneider',
      location: 'Bâle',
      avatar: '/avatars/emma.jpg',
      rating: 5,
      content: 'J\'utilise Lucky Kangaroo depuis le début et je suis impressionnée par l\'évolution de la plateforme. L\'IA qui aide à créer les annonces est géniale et j\'ai gagné plein de badges !',
      date: 'Il y a 1 semaine',
      category: 'Multiples',
      exchange: 'Plus de 15 échanges réussis'
    },
    {
      id: '6',
      name: 'Pierre Moreau',
      location: 'Lugano',
      avatar: '/avatars/pierre.jpg',
      rating: 5,
      content: 'Parfait pour les étudiants ! J\'ai pu échanger mes livres de cours contre des équipements de sport, puis contre des cours de langue. C\'est économique et écologique !',
      date: 'Il y a 1 mois',
      category: 'Livres → Sport → Services',
      exchange: 'Livres universitaires → Équipement fitness → Cours d\'italien'
    }
  ];

  const nextTestimonial = () => {
    setCurrentIndex((prev) => (prev + 1) % testimonials.length);
  };

  const prevTestimonial = () => {
    setCurrentIndex((prev) => (prev - 1 + testimonials.length) % testimonials.length);
  };

  const goToTestimonial = (index: number) => {
    setCurrentIndex(index);
  };

  const currentTestimonial = testimonials[currentIndex];

  return (
    <section className="py-20 bg-gradient-to-br from-indigo-50 to-purple-50">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Ce que disent nos utilisateurs
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Découvrez les expériences de notre communauté et comment Lucky Kangaroo transforme leur quotidien
          </p>
        </motion.div>

        <div className="max-w-6xl mx-auto">
          <motion.div
            key={currentIndex}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.5 }}
            className="bg-white rounded-3xl p-8 md:p-12 shadow-2xl relative"
          >
            <Quote className="absolute top-6 right-8 w-16 h-16 text-blue-100" />
            
            <div className="flex flex-col lg:flex-row items-start space-y-8 lg:space-y-0 lg:space-x-8">
              <div className="flex-shrink-0">
                <div className="w-24 h-24 bg-gradient-to-br from-blue-400 to-indigo-500 rounded-full flex items-center justify-center text-white text-2xl font-bold">
                  {currentTestimonial.name.charAt(0)}
                </div>
              </div>
              
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-4">
                  {[...Array(currentTestimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                
                <blockquote className="text-xl text-gray-700 leading-relaxed mb-6 italic">
                  "{currentTestimonial.content}"
                </blockquote>
                
                <div className="space-y-3">
                  <div className="flex items-center space-x-4 text-sm text-gray-600">
                    <div className="flex items-center space-x-2">
                      <MapPin className="w-4 h-4" />
                      <span>{currentTestimonial.location}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Calendar className="w-4 h-4" />
                      <span>{currentTestimonial.date}</span>
                    </div>
                  </div>
                  
                  <div className="bg-blue-50 rounded-lg p-3">
                    <div className="text-sm font-medium text-blue-800 mb-1">
                      Échange réalisé :
                    </div>
                    <div className="text-sm text-blue-700">
                      {currentTestimonial.exchange}
                    </div>
                  </div>
                  
                  <div className="text-sm text-gray-500">
                    Catégorie : {currentTestimonial.category}
                  </div>
                </div>
                
                <div className="mt-6">
                  <span className="text-lg font-semibold text-gray-900">
                    {currentTestimonial.name}
                  </span>
                </div>
              </div>
            </div>
          </motion.div>

          <div className="flex items-center justify-center space-x-4 mt-8">
            <button
              onClick={prevTestimonial}
              className="p-3 bg-white rounded-full shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-110"
            >
              <ChevronLeft className="w-6 h-6 text-gray-600" />
            </button>
            
            <div className="flex space-x-2">
              {testimonials.map((_, index) => (
                <button
                  key={index}
                  onClick={() => goToTestimonial(index)}
                  className={`w-3 h-3 rounded-full transition-all duration-300 ${
                    index === currentIndex
                      ? 'bg-blue-600 scale-125'
                      : 'bg-gray-300 hover:bg-gray-400'
                  }`}
                />
              ))}
            </div>
            
            <button
              onClick={nextTestimonial}
              className="p-3 bg-white rounded-full shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-110"
            >
              <ChevronRight className="w-6 h-6 text-gray-600" />
            </button>
          </div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="text-center mt-16"
        >
          <div className="bg-white rounded-3xl p-8 shadow-xl max-w-4xl mx-auto">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Rejoignez notre communauté satisfaite
            </h3>
            <p className="text-gray-600 mb-6">
              Plus de 95% de nos utilisateurs recommandent Lucky Kangaroo à leurs amis
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-8 py-4 rounded-full text-lg font-semibold hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 transform hover:scale-105 shadow-lg">
                Commencer à échanger
              </button>
              <button className="border-2 border-blue-600 text-blue-600 px-8 py-4 rounded-full text-lg font-semibold hover:bg-blue-600 hover:text-white transition-all duration-300">
                Lire plus de témoignages
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default TestimonialsSection;
