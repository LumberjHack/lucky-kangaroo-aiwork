import React from 'react';
import { motion } from 'framer-motion';
import { 
  CheckCircle, 
  Users, 
  Shield, 
  Zap, 
  Globe, 
  Heart,
  ArrowRight,
  Download,
  Smartphone
} from 'lucide-react';

const CTASection: React.FC = () => {
  const benefits = [
    {
      icon: CheckCircle,
      title: 'Gratuit à vie',
      description: 'Aucun frais d\'inscription ni d\'abonnement mensuel'
    },
    {
      icon: Shield,
      title: '100% sécurisé',
      description: 'Protection des données et transactions sécurisées'
    },
    {
      icon: Zap,
      title: 'IA intelligente',
      description: 'Reconnaissance d\'objets et suggestions automatiques'
    },
    {
      icon: Globe,
      title: 'Communauté active',
      description: 'Plus de 50,000 utilisateurs dans toute la Suisse'
    },
    {
      icon: Heart,
      title: 'Écologique',
      description: 'Réduisez votre empreinte carbone en échangeant'
    },
    {
      icon: Users,
      title: 'Support 24/7',
      description: 'Assistance disponible en français, allemand et italien'
    }
  ];

  const stats = [
    { value: '50,000+', label: 'Utilisateurs actifs' },
    { value: '25,000+', label: 'Annonces publiées' },
    { value: '10,000+', label: 'Échanges réussis' },
    { value: '95%', label: 'Taux de satisfaction' }
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
    <section className="py-20 bg-gradient-to-br from-blue-900 via-indigo-900 to-purple-900 text-white relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 bg-black opacity-20"></div>
      <div className="absolute top-0 left-0 w-full h-full">
        <div className="absolute top-20 left-10 w-72 h-72 bg-blue-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
        <div className="absolute top-40 right-10 w-72 h-72 bg-purple-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
        <div className="absolute -bottom-8 left-20 w-72 h-72 bg-pink-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
      </div>

      <div className="container mx-auto px-4 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-6xl font-bold mb-6">
            Prêt à révolutionner
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
              votre façon d'échanger ?
            </span>
          </h2>
          <p className="text-xl md:text-2xl text-blue-100 max-w-4xl mx-auto leading-relaxed">
            Rejoignez la communauté Lucky Kangaroo et découvrez un monde d'opportunités 
            où chaque objet peut se transformer en expérience inoubliable
          </p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16"
        >
          {benefits.map((benefit, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20 hover:bg-white/20 transition-all duration-300"
            >
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-purple-400 rounded-xl flex items-center justify-center">
                  <benefit.icon className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white mb-1">
                    {benefit.title}
                  </h3>
                  <p className="text-blue-100 text-sm">
                    {benefit.description}
                  </p>
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
          className="text-center mb-16"
        >
          <div className="bg-white/10 backdrop-blur-sm rounded-3xl p-8 border border-white/20 max-w-4xl mx-auto">
            <h3 className="text-3xl font-bold text-white mb-6">
              Commencez dès aujourd'hui
            </h3>
            <p className="text-xl text-blue-100 mb-8">
              Créez votre compte en moins de 2 minutes et publiez votre première annonce
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
              <button className="bg-gradient-to-r from-blue-500 to-purple-500 text-white px-8 py-4 rounded-full text-lg font-semibold hover:from-blue-600 hover:to-purple-600 transition-all duration-300 transform hover:scale-105 shadow-lg flex items-center justify-center space-x-2">
                <span>Créer mon compte gratuitement</span>
                <ArrowRight className="w-5 h-5" />
              </button>
              <button className="border-2 border-white text-white px-8 py-4 rounded-full text-lg font-semibold hover:bg-white hover:text-blue-900 transition-all duration-300 flex items-center justify-center space-x-2">
                <span>Voir la démo</span>
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>

            <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-8">
              <div className="flex items-center space-x-3">
                <Download className="w-5 h-5 text-blue-300" />
                <span className="text-blue-100">Disponible sur tous les navigateurs</span>
              </div>
              <div className="flex items-center space-x-3">
                <Smartphone className="w-5 h-5 text-blue-300" />
                <span className="text-blue-100">Application mobile bientôt disponible</span>
              </div>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="text-center"
        >
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
            {stats.map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="text-center"
              >
                <div className="text-3xl md:text-4xl font-bold text-white mb-2">
                  {stat.value}
                </div>
                <div className="text-blue-200 text-sm md:text-base">
                  {stat.label}
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default CTASection;
