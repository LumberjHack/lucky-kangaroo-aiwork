import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Mail, CheckCircle, AlertCircle, RefreshCw, ArrowLeft } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { toast } from 'react-hot-toast';

const VerifyEmailPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { verifyEmail, resendVerificationEmail } = useAuth();

  const token = searchParams.get('token');
  const email = searchParams.get('email');

  useEffect(() => {
    if (token && email) {
      handleVerification();
    }
  }, [token, email]);

  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [countdown]);

  const handleVerification = async () => {
    if (!token || !email) return;

    setIsLoading(true);
    try {
      await verifyEmail(token);
      toast.success('Email vérifié avec succès ! Vous pouvez maintenant vous connecter.');
      navigate('/auth/login');
    } catch (error: any) {
      toast.error(error.message || 'Erreur lors de la vérification de l\'email');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResendEmail = async () => {
    if (!email) {
      toast.error('Email non trouvé. Veuillez vous inscrire à nouveau.');
      return;
    }

    setIsResending(true);
    try {
      await resendVerificationEmail(email);
      toast.success('Email de vérification renvoyé !');
      setCountdown(60);
    } catch (error: any) {
      toast.error(error.message || 'Erreur lors de l\'envoi de l\'email');
    } finally {
      setIsResending(false);
    }
  };

  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  if (token && email) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="max-w-md w-full space-y-8"
        >
          <motion.div variants={itemVariants} className="text-center">
            <div className="flex justify-center mb-6">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
                <span className="text-white text-2xl font-bold">L</span>
              </div>
            </div>
            
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              Vérification en cours...
            </h2>
            <p className="text-gray-600">
              Nous vérifions votre email, veuillez patienter.
            </p>
          </motion.div>

          <motion.div variants={itemVariants} className="bg-white rounded-2xl shadow-xl p-8 text-center">
            {isLoading ? (
              <div className="space-y-4">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                <p className="text-gray-600">Vérification de votre email...</p>
              </div>
            ) : (
              <div className="space-y-4">
                <CheckCircle className="w-16 h-16 text-green-500 mx-auto" />
                <h3 className="text-xl font-semibold text-gray-900">
                  Email vérifié !
                </h3>
                <p className="text-gray-600">
                  Votre compte a été vérifié avec succès.
                </p>
                <Link
                  to="/auth/login"
                  className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
                >
                  Se connecter
                </Link>
              </div>
            )}
          </motion.div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="max-w-md w-full space-y-8"
      >
        {/* Header */}
        <motion.div variants={itemVariants} className="text-center">
          <Link
            to="/"
            className="inline-flex items-center text-blue-600 hover:text-blue-700 mb-6"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Retour à l'accueil
          </Link>
          
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
              <span className="text-white text-2xl font-bold">L</span>
            </div>
          </div>
          
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Vérifiez votre email
          </h2>
          <p className="text-gray-600">
            Nous avons envoyé un lien de vérification à votre adresse email
          </p>
        </motion.div>

        {/* Main Content */}
        <motion.div variants={itemVariants} className="bg-white rounded-2xl shadow-xl p-8 space-y-6">
          <div className="text-center">
            <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Mail className="w-10 h-10 text-blue-600" />
            </div>
            
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Vérifiez votre boîte mail
            </h3>
            
            <p className="text-gray-600 mb-6">
              Cliquez sur le lien de vérification que nous avons envoyé à votre adresse email pour activer votre compte.
            </p>

            <div className="bg-blue-50 rounded-lg p-4 mb-6">
              <p className="text-sm text-blue-800">
                <strong>Conseil :</strong> Vérifiez également votre dossier spam si vous ne trouvez pas l'email.
              </p>
            </div>
          </div>

          {/* Resend Email Section */}
          <div className="border-t pt-6">
            <h4 className="text-lg font-medium text-gray-900 mb-3">
              Vous n'avez pas reçu l'email ?
            </h4>
            
            <p className="text-sm text-gray-600 mb-4">
              Vérifiez que l'adresse email est correcte et cliquez sur le bouton ci-dessous pour recevoir un nouveau lien.
            </p>

            <button
              onClick={handleResendEmail}
              disabled={isResending || countdown > 0}
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
            >
              {isResending ? (
                <div className="flex items-center justify-center">
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  Envoi en cours...
                </div>
              ) : countdown > 0 ? (
                `Renvoyer dans ${countdown}s`
              ) : (
                'Renvoyer l\'email de vérification'
              )}
            </button>

            {countdown > 0 && (
              <p className="text-xs text-gray-500 text-center mt-2">
                Vous pourrez demander un nouvel email dans {countdown} seconde{countdown > 1 ? 's' : ''}
              </p>
            )}
          </div>

          {/* Help Section */}
          <div className="border-t pt-6">
            <h4 className="text-lg font-medium text-gray-900 mb-3">
              Besoin d'aide ?
            </h4>
            
            <div className="space-y-3 text-sm text-gray-600">
              <div className="flex items-start space-x-3">
                <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                <span>Vérifiez que l'adresse email est correcte</span>
              </div>
              <div className="flex items-start space-x-3">
                <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                <span>Regardez dans votre dossier spam</span>
              </div>
              <div className="flex items-start space-x-3">
                <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                <span>Attendez quelques minutes avant de redemander</span>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Footer Actions */}
        <motion.div variants={itemVariants} className="text-center space-y-4">
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg">
            <p className="text-sm text-gray-600 mb-4">
              Vous avez des problèmes avec la vérification ?
            </p>
            <div className="space-y-3">
              <Link
                to="/auth/login"
                className="block text-blue-600 hover:text-blue-700 font-medium"
              >
                Retour à la connexion
              </Link>
              <Link
                to="/auth/register"
                className="block text-blue-600 hover:text-blue-700 font-medium"
              >
                Créer un nouveau compte
              </Link>
              <Link
                to="/contact"
                className="block text-blue-600 hover:text-blue-700 font-medium"
              >
                Contacter le support
              </Link>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default VerifyEmailPage;
