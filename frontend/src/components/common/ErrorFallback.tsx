import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, RefreshCw, Home, Bug, MessageCircle } from 'lucide-react';

interface ErrorFallbackProps {
  error: Error;
  resetErrorBoundary: () => void;
}

const ErrorFallback: React.FC<ErrorFallbackProps> = ({ error, resetErrorBoundary }) => {
  const handleReset = () => {
    resetErrorBoundary();
  };

  const handleGoHome = () => {
    window.location.href = '/';
  };

  const handleReportBug = () => {
    // Envoyer le rapport d'erreur
    const errorReport = {
      message: error.message,
      stack: error.stack,
      url: window.location.href,
      userAgent: navigator.userAgent,
      timestamp: new Date().toISOString()
    };
    
    console.error('Error Report:', errorReport);
    
    // Ici, vous pourriez envoyer le rapport à un service comme Sentry
    // ou à votre backend pour analyse
    
    alert('Rapport d\'erreur envoyé. Merci de votre patience.');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-orange-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-2xl w-full bg-white rounded-2xl shadow-2xl border border-red-200 overflow-hidden"
      >
        {/* Header avec icône d'erreur */}
        <div className="bg-gradient-to-r from-red-500 to-orange-500 p-8 text-center text-white">
          <motion.div
            animate={{ 
              rotate: [0, -10, 10, -10, 0],
              scale: [1, 1.1, 1]
            }}
            transition={{ 
              duration: 2,
              repeat: Infinity,
              repeatDelay: 3
            }}
            className="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-4"
          >
            <AlertTriangle size={40} />
          </motion.div>
          <h1 className="text-3xl font-bold mb-2">Oups ! Une erreur est survenue</h1>
          <p className="text-red-100 text-lg">
            Nous nous excusons pour ce désagrément
          </p>
        </div>

        {/* Contenu de l'erreur */}
        <div className="p-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <h2 className="text-lg font-semibold text-red-800 mb-2">
              Détails de l'erreur
            </h2>
            <p className="text-red-700 text-sm font-mono break-all">
              {error.message}
            </p>
            {process.env.NODE_ENV === 'development' && error.stack && (
              <details className="mt-3">
                <summary className="text-red-600 text-sm cursor-pointer hover:text-red-800">
                  Voir la stack trace
                </summary>
                <pre className="text-red-600 text-xs mt-2 whitespace-pre-wrap overflow-auto max-h-32">
                  {error.stack}
                </pre>
              </details>
            )}
          </div>

          {/* Actions */}
          <div className="space-y-4">
            <button
              onClick={handleReset}
              className="w-full flex items-center justify-center space-x-3 bg-primary-600 text-white py-3 px-6 rounded-lg hover:bg-primary-700 transition-colors font-medium"
            >
              <RefreshCw size={20} />
              <span>Réessayer</span>
            </button>

            <button
              onClick={handleGoHome}
              className="w-full flex items-center justify-center space-x-3 bg-gray-100 text-gray-700 py-3 px-6 rounded-lg hover:bg-gray-200 transition-colors font-medium"
            >
              <Home size={20} />
              <span>Retour à l'accueil</span>
            </button>

            <button
              onClick={handleReportBug}
              className="w-full flex items-center justify-center space-x-3 bg-orange-100 text-orange-700 py-3 px-6 rounded-lg hover:bg-orange-200 transition-colors font-medium"
            >
              <Bug size={20} />
              <span>Signaler le problème</span>
            </button>
          </div>

          {/* Informations supplémentaires */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
              <div className="flex items-center space-x-2">
                <MessageCircle size={16} />
                <span>Contactez le support si le problème persiste</span>
              </div>
              <div className="flex items-center space-x-2">
                <RefreshCw size={16} />
                <span>Essayez de rafraîchir la page</span>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="mt-8 pt-6 border-t border-gray-200 text-center">
            <p className="text-xs text-gray-500">
              Lucky Kangaroo v1.0.0 • Erreur #{Math.random().toString(36).substr(2, 9)}
            </p>
            <p className="text-xs text-gray-400 mt-1">
              Si ce problème persiste, contactez notre équipe technique
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default ErrorFallback;
