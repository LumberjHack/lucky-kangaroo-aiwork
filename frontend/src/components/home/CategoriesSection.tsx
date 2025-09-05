import React from 'react';
import { motion } from 'framer-motion';
import { 
  Car, 
  Home, 
  Smartphone, 
  BookOpen, 
  Heart, 
  Palette, 
  Dumbbell, 
  Utensils,
  Camera,
  Music,
  Gamepad2,
  Baby,
  Dog,
  Wrench,
  GraduationCap,
  Briefcase,
  Plane,
  TreePine
} from 'lucide-react';

const CategoriesSection: React.FC = () => {
  const categories = [
    {
      icon: Car,
      name: 'Véhicules',
      description: 'Voitures, motos, vélos, pièces détachées',
      count: '2,500+',
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      icon: Home,
      name: 'Maison & Jardin',
      description: 'Meubles, décoration, outils, plantes',
      count: '8,200+',
      color: 'from-green-500 to-green-600',
      bgColor: 'bg-green-50'
    },
    {
      icon: Smartphone,
      name: 'Électronique',
      description: 'Téléphones, ordinateurs, accessoires',
      count: '6,800+',
      color: 'from-purple-500 to-purple-600',
      bgColor: 'bg-purple-50'
    },
    {
      icon: BookOpen,
      name: 'Livres & Médias',
      description: 'Livres, films, musique, jeux vidéo',
      count: '4,100+',
      color: 'from-orange-500 to-orange-600',
      bgColor: 'bg-orange-50'
    },
    {
      icon: Heart,
      name: 'Mode & Beauté',
      description: 'Vêtements, chaussures, cosmétiques',
      count: '5,600+',
      color: 'from-pink-500 to-pink-600',
      bgColor: 'bg-pink-50'
    },
    {
      icon: Palette,
      name: 'Art & Collection',
      description: 'Tableaux, sculptures, objets de collection',
      count: '1,900+',
      color: 'from-yellow-500 to-yellow-600',
      bgColor: 'bg-yellow-50'
    },
    {
      icon: Dumbbell,
      name: 'Sport & Loisirs',
      description: 'Équipements sportifs, instruments de musique',
      count: '3,400+',
      color: 'from-red-500 to-red-600',
      bgColor: 'bg-red-50'
    },
    {
      icon: Utensils,
      name: 'Cuisine & Gastronomie',
      description: 'Appareils de cuisine, ustensiles, recettes',
      count: '2,800+',
      color: 'from-amber-500 to-amber-600',
      bgColor: 'bg-amber-50'
    },
    {
      icon: Camera,
      name: 'Photo & Vidéo',
      description: 'Appareils photo, caméras, accessoires',
      count: '1,600+',
      color: 'from-indigo-500 to-indigo-600',
      bgColor: 'bg-indigo-50'
    },
    {
      icon: Music,
      name: 'Musique & Instruments',
      description: 'Instruments, équipements audio, partitions',
      count: '2,200+',
      color: 'from-teal-500 to-teal-600',
      bgColor: 'bg-teal-50'
    },
    {
      icon: Gamepad2,
      name: 'Jeux & Jouets',
      description: 'Jeux de société, consoles, jouets',
      count: '3,100+',
      color: 'from-cyan-500 to-cyan-600',
      bgColor: 'bg-cyan-50'
    },
    {
      icon: Baby,
      name: 'Bébé & Enfant',
      description: 'Vêtements, jouets, équipements',
      count: '2,700+',
      color: 'from-rose-500 to-rose-600',
      bgColor: 'bg-rose-50'
    },
    {
      icon: Dog,
      name: 'Animaux & Accessoires',
      description: 'Animaux, nourriture, accessoires',
      count: '1,800+',
      color: 'from-emerald-500 to-emerald-600',
      bgColor: 'bg-emerald-50'
    },
    {
      icon: Wrench,
      name: 'Bricolage & Jardinage',
      description: 'Outils, machines, matériaux',
      count: '3,900+',
      color: 'from-slate-500 to-slate-600',
      bgColor: 'bg-slate-50'
    },
    {
      icon: GraduationCap,
      name: 'Formation & Éducation',
      description: 'Cours, tutorat, matériel scolaire',
      count: '1,500+',
      color: 'from-violet-500 to-violet-600',
      bgColor: 'bg-violet-50'
    },
    {
      icon: Briefcase,
      name: 'Services Professionnels',
      description: 'Conseil, design, développement, marketing',
      count: '2,300+',
      color: 'from-sky-500 to-sky-600',
      bgColor: 'bg-sky-50'
    },
    {
      icon: Plane,
      name: 'Voyage & Transport',
      description: 'Billets, hébergements, services touristiques',
      count: '1,200+',
      color: 'from-fuchsia-500 to-fuchsia-600',
      bgColor: 'bg-fuchsia-50'
    },
    {
      icon: TreePine,
      name: 'Écologie & Durabilité',
      description: 'Produits bio, recyclage, énergies vertes',
      count: '900+',
      color: 'from-lime-500 to-lime-600',
      bgColor: 'bg-lime-50'
    }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.05
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.4
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
            Explorez par catégorie
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Trouvez facilement ce que vous cherchez parmi nos 18 catégories principales
          </p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
        >
          {categories.map((category, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              className={`${category.bgColor} rounded-2xl p-6 hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 cursor-pointer group`}
            >
              <div className="flex items-center space-x-4">
                <div className={`w-12 h-12 bg-gradient-to-br ${category.color} rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300`}>
                  <category.icon className="w-6 h-6 text-white" />
                </div>
                
                <div className="flex-1 min-w-0">
                  <h3 className="text-lg font-semibold text-gray-900 mb-1 truncate">
                    {category.name}
                  </h3>
                  <p className="text-sm text-gray-600 mb-2 line-clamp-2">
                    {category.description}
                  </p>
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium text-gray-500">
                      {category.count} annonces
                    </span>
                    <div className="w-2 h-2 bg-gray-300 rounded-full group-hover:bg-gray-400 transition-colors"></div>
                  </div>
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
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-3xl p-8 max-w-4xl mx-auto">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Vous ne trouvez pas votre catégorie ?
            </h3>
            <p className="text-gray-600 mb-6">
              Proposez une nouvelle catégorie et aidez-nous à enrichir la plateforme
            </p>
            <button className="bg-blue-600 text-white px-6 py-3 rounded-full font-medium hover:bg-blue-700 transition-colors">
              Suggérer une catégorie
            </button>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default CategoriesSection;
