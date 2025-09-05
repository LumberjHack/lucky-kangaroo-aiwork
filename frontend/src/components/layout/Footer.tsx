import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Heart, 
  Mail, 
  Phone, 
  MapPin, 
  Facebook, 
  Twitter, 
  Instagram, 
  Linkedin,
  Github,
  Globe
} from 'lucide-react';

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  const footerSections = [
    {
      title: 'Lucky Kangaroo',
      links: [
        { name: 'À propos', href: '/about' },
        { name: 'Comment ça marche', href: '/how-it-works' },
        { name: 'Notre équipe', href: '/team' },
        { name: 'Carrières', href: '/careers' },
        { name: 'Presse', href: '/press' }
      ]
    },
    {
      title: 'Services',
      links: [
        { name: 'Créer une annonce', href: '/listings/create' },
        { name: 'Rechercher', href: '/search' },
        { name: 'Chat en temps réel', href: '/chat' },
        { name: 'IA & Matching', href: '/ai-features' },
        { name: 'Géolocalisation', href: '/geolocation' }
      ]
    },
    {
      title: 'Support',
      links: [
        { name: 'Centre d\'aide', href: '/help' },
        { name: 'FAQ', href: '/faq' },
        { name: 'Contact', href: '/contact' },
        { name: 'Signalements', href: '/reports' },
        { name: 'Sécurité', href: '/security' }
      ]
    },
    {
      title: 'Légal',
      links: [
        { name: 'Conditions d\'utilisation', href: '/terms' },
        { name: 'Politique de confidentialité', href: '/privacy' },
        { name: 'Cookies', href: '/cookies' },
        { name: 'RGPD', href: '/gdpr' },
        { name: 'Mentions légales', href: '/legal' }
      ]
    }
  ];

  const socialLinks = [
    { name: 'Facebook', icon: Facebook, href: 'https://facebook.com/luckykangaroo', color: 'hover:text-blue-600' },
    { name: 'Twitter', icon: Twitter, href: 'https://twitter.com/luckykangaroo', color: 'hover:text-blue-400' },
    { name: 'Instagram', icon: Instagram, href: 'https://instagram.com/luckykangaroo', color: 'hover:text-pink-600' },
    { name: 'LinkedIn', icon: Linkedin, href: 'https://linkedin.com/company/luckykangaroo', color: 'hover:text-blue-700' },
    { name: 'GitHub', icon: Github, href: 'https://github.com/luckykangaroo', color: 'hover:text-gray-700' }
  ];

  return (
    <footer className="bg-gray-900 text-white">
      {/* Contenu principal */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-8">
          {/* Logo et description */}
          <div className="lg:col-span-2">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              viewport={{ once: true }}
              className="mb-6"
            >
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-secondary-600 rounded-full flex items-center justify-center">
                  <span className="text-white text-lg font-bold">🦘</span>
                </div>
                <div>
                  <h3 className="text-xl font-bold">Lucky Kangaroo</h3>
                  <p className="text-sm text-gray-400">Échange Collaboratif</p>
                </div>
              </div>
              <p className="text-gray-300 text-sm leading-relaxed mb-6">
                La première plateforme d'échange collaborative avec IA avancée, 
                géolocalisation intelligente et chaînes d'échange révolutionnaires.
              </p>
            </motion.div>

            {/* Contact */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              viewport={{ once: true }}
              className="space-y-3"
            >
              <div className="flex items-center space-x-3 text-gray-300">
                <Mail className="w-4 h-4 text-primary-400" />
                <span className="text-sm">contact@luckykangaroo.com</span>
              </div>
              <div className="flex items-center space-x-3 text-gray-300">
                <Phone className="w-4 h-4 text-primary-400" />
                <span className="text-sm">+33 1 23 45 67 89</span>
              </div>
              <div className="flex items-center space-x-3 text-gray-300">
                <MapPin className="w-4 h-4 text-primary-400" />
                <span className="text-sm">Paris, France</span>
              </div>
            </motion.div>
          </div>

          {/* Sections de liens */}
          {footerSections.map((section, index) => (
            <motion.div
              key={section.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 + index * 0.05 }}
              viewport={{ once: true }}
            >
              <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">
                {section.title}
              </h4>
              <ul className="space-y-3">
                {section.links.map((link) => (
                  <li key={link.name}>
                    <Link
                      to={link.href}
                      className="text-sm text-gray-300 hover:text-white transition-colors duration-200"
                    >
                      {link.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>

        {/* Séparateur */}
        <motion.div
          initial={{ opacity: 0, scaleX: 0 }}
          whileInView={{ opacity: 1, scaleX: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          viewport={{ once: true }}
          className="border-t border-gray-800 my-8"
        />

        {/* Bas de page */}
        <div className="flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0">
          {/* Copyright */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            viewport={{ once: true }}
            className="text-sm text-gray-400"
          >
            <p>
              © {currentYear} Lucky Kangaroo. Tous droits réservés.
            </p>
            <p className="mt-1">
              Fait avec <Heart className="inline w-4 h-4 text-red-500" /> en France
            </p>
          </motion.div>

          {/* Liens sociaux */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            viewport={{ once: true }}
            className="flex items-center space-x-6"
          >
            {socialLinks.map((social) => (
              <a
                key={social.name}
                href={social.href}
                target="_blank"
                rel="noopener noreferrer"
                className={`text-gray-400 transition-colors duration-200 ${social.color}`}
                aria-label={social.name}
              >
                <social.icon className="w-5 h-5" />
              </a>
            ))}
          </motion.div>
        </div>
      </div>

      {/* Barre de statut */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.5 }}
        viewport={{ once: true }}
        className="bg-gray-800 border-t border-gray-700"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col md:flex-row items-center justify-between space-y-2 md:space-y-0">
            <div className="flex items-center space-x-6 text-xs text-gray-400">
              <span className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>Système opérationnel</span>
              </span>
              <span>•</span>
              <span>v1.0.0</span>
              <span>•</span>
              <span>Dernière mise à jour: {new Date().toLocaleDateString('fr-FR')}</span>
            </div>
            
            <div className="flex items-center space-x-4 text-xs text-gray-400">
              <a href="/status" className="hover:text-white transition-colors">
                Statut du service
              </a>
              <span>•</span>
              <a href="/api" className="hover:text-white transition-colors">
                API
              </a>
              <span>•</span>
              <a href="/developers" className="hover:text-white transition-colors">
                Développeurs
              </a>
            </div>
          </div>
        </div>
      </motion.div>
    </footer>
  );
};

export default Footer;
