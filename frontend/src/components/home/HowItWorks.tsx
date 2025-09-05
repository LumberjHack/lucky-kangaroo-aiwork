import React from 'react';
import { motion } from 'framer-motion';
import { Upload, Search, MessageCircle, Handshake, Star, Gift } from 'lucide-react';

const HowItWorks: React.FC = () => {
  const steps = [
    {
      icon: Upload,
      title: '1. Publiez votre annonce',
      description: 'Prenez une photo de votre objet ou décrivez votre service. Notre IA vous aide à créer une annonce optimale.',
      features: ['Reconnaissance d\'objets automatique', 'Estimation de valeur intelligente', 'Génération de tags optimisés']
    },
    {
      icon: Search,
      title: '2. Découvrez des opportunités',
      description: 'Trouvez des objets et services qui vous intéressent grâce à notre moteur de recherche intelligent.',
      features: ['Recherche sémantique avancée', 'Filtres géolocalisés', 'Suggestions personnalisées']
    },
    {
      icon: MessageCircle,
      title: '3. Négociez en toute sécurité',
      description: 'Échangez avec les autres utilisateurs via notre chat sécurisé avec traduction automatique.',
      features: ['Chat en temps réel', 'Traduction automatique', 'Chiffrement de bout en bout']
    },
    {
      icon: Handshake,
      title: '4. Finalisez l\'échange',
      description: 'Planifiez votre rencontre et échangez vos objets ou services en toute sécurité.',
      features: ['Points de rencontre sécurisés', 'Système d\'évaluation mutuelle', 'Support en cas de litige']
    },
    {
      icon: Star,
      title: '5. Évaluez et progressez',
      description: 'Donnez votre avis et gagnez des points pour débloquer des fonctionnalités premium.',
      features: ['Système de notation', 'Badges et récompenses', 'Score de confiance']
    },
    {
      icon: Gift,
      title: '6. Profitez des avantages',
      description: 'Accédez à des fonctionnalités exclusives et profitez de la communauté Lucky Kangaroo.',
      features: ['Accès prioritaire aux annonces', 'Boosts gratuits', 'Statistiques détaillées']
    }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { y: 30, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.6
      }
    }
  };

  return (
    <section className="py-20 bg-gradient-to-br from-gray-50 to-blue-50">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-20"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Comment ça marche ?
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Lucky Kangaroo simplifie l'échange d'objets et de services en 6 étapes simples et sécurisées
          </p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
        >
          {steps.map((step, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2 border border-gray-100"
            >
              <div className="flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full mb-6 mx-auto">
                <step.icon className="w-10 h-10 text-white" />
              </div>
              
              <h3 className="text-2xl font-bold text-gray-900 mb-4 text-center">
                {step.title}
              </h3>
              
              <p className="text-gray-600 mb-6 text-center leading-relaxed">
                {step.description}
              </p>

              <ul className="space-y-3">
                {step.features.map((feature, featureIndex) => (
                  <li key={featureIndex} className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                    <span className="text-sm text-gray-700">{feature}</span>
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-20 text-center"
        >
          <div className="bg-white rounded-3xl p-8 shadow-xl max-w-4xl mx-auto">
            <h3 className="text-3xl font-bold text-gray-900 mb-6">
              Prêt à commencer ?
            </h3>
            <p className="text-lg text-gray-600 mb-8">
              Rejoignez des milliers d'utilisateurs qui échangent déjà sur Lucky Kangaroo
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-8 py-4 rounded-full text-lg font-semibold hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 transform hover:scale-105 shadow-lg">
                Créer mon compte gratuitement
              </button>
              <button className="border-2 border-blue-600 text-blue-600 px-8 py-4 rounded-full text-lg font-semibold hover:bg-blue-600 hover:text-white transition-all duration-300">
                Voir la démo
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default HowItWorks;
