import React from 'react';
import { motion } from 'framer-motion';
import { Users, Package, MapPin, TrendingUp, Heart, Shield } from 'lucide-react';

const StatisticsSection: React.FC = () => {
  const stats = [
    {
      icon: Users,
      value: '50,000+',
      label: 'Utilisateurs actifs',
      description: 'Communauté en pleine croissance'
    },
    {
      icon: Package,
      value: '25,000+',
      label: 'Annonces publiées',
      description: 'Objets et services variés'
    },
    {
      icon: MapPin,
      value: '150+',
      label: 'Villes couvertes',
      description: 'Présence nationale'
    },
    {
      icon: TrendingUp,
      value: '95%',
      label: 'Taux de satisfaction',
      description: 'Échanges réussis'
    },
    {
      icon: Heart,
      value: '10,000+',
      label: 'Échanges réalisés',
      description: 'Économie circulaire'
    },
    {
      icon: Shield,
      value: '99.9%',
      label: 'Sécurité garantie',
      description: 'Protection des utilisateurs'
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
    <section className="py-20 bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Lucky Kangaroo en chiffres
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Découvrez l'impact de notre plateforme d'échange et la croissance de notre communauté
          </p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
        >
          {stats.map((stat, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2"
            >
              <div className="flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full mb-6 mx-auto">
                <stat.icon className="w-8 h-8 text-white" />
              </div>
              
              <div className="text-center">
                <div className="text-4xl font-bold text-gray-900 mb-2">
                  {stat.value}
                </div>
                <h3 className="text-xl font-semibold text-gray-800 mb-2">
                  {stat.label}
                </h3>
                <p className="text-gray-600">
                  {stat.description}
                </p>
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
          <div className="inline-flex items-center space-x-4 bg-white rounded-full px-8 py-4 shadow-lg">
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-gray-700 font-medium">
              Plateforme en croissance continue
            </span>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default StatisticsSection;
