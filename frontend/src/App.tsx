import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { useSelector } from 'react-redux';
import { Toaster } from 'react-hot-toast';
import { RootState } from './store';

// Layout
import Layout from './components/layout/Layout';

// Pages
import HomePage from './pages/HomePage';
import SearchPage from './pages/SearchPage';
import AdvancedSearchPage from './pages/AdvancedSearchPage';
import CreateListingPage from './pages/CreateListingPage';
import ListingDetailPage from './pages/ListingDetailPage';
import ChatPage from './pages/ChatPage';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import VerifyEmailPage from './pages/auth/VerifyEmailPage';
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage';
import ResetPasswordPage from './pages/auth/ResetPasswordPage';

// Components
import ProtectedRoute from './components/auth/ProtectedRoute';
import PublicRoute from './components/auth/PublicRoute';
import ErrorBoundary from './components/common/ErrorFallback';

// Hooks
import { useAuth } from './hooks/useAuth';

const App: React.FC = () => {
  const { isAuthenticated, isLoading, checkAuthStatus } = useAuth();

  useEffect(() => {
    // Vérifier le statut d'authentification au chargement de l'app
    checkAuthStatus();
  }, [checkAuthStatus]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement de Lucky Kangaroo...</p>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <Helmet>
        <title>Lucky Kangaroo - Plateforme d'échange d'objets et services</title>
        <meta name="description" content="Lucky Kangaroo est la première plateforme suisse d'échange d'objets et de services. Échangez, partagez et découvrez en toute sécurité." />
        <meta name="keywords" content="échange, objets, services, Suisse, plateforme, communauté, écologie, durabilité" />
        <meta name="author" content="Lucky Kangaroo" />
        
        {/* Open Graph */}
        <meta property="og:title" content="Lucky Kangaroo - Plateforme d'échange" />
        <meta property="og:description" content="La première plateforme suisse d'échange d'objets et de services" />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://luckykangaroo.ch" />
        <meta property="og:image" content="https://luckykangaroo.ch/og-image.jpg" />
        
        {/* Twitter */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="Lucky Kangaroo - Plateforme d'échange" />
        <meta name="twitter:description" content="La première plateforme suisse d'échange d'objets et de services" />
        <meta name="twitter:image" content="https://luckykangaroo.ch/twitter-image.jpg" />
        
        {/* Favicon */}
        <link rel="icon" type="image/x-icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
        
        {/* Preconnect */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </Helmet>

      <Router>
        <Layout>
          <Routes>
                                    {/* Routes publiques */}
                        <Route path="/" element={<HomePage />} />
                        <Route path="/search" element={<AdvancedSearchPage />} />
                        <Route path="/listings" element={<AdvancedSearchPage />} />
                        <Route path="/listings/:id" element={<ListingDetailPage />} />
            
            {/* Routes d'authentification - accessibles uniquement aux utilisateurs non connectés */}
            <Route
              path="/auth/login"
              element={
                <PublicRoute redirectTo="/dashboard">
                  <LoginPage />
                </PublicRoute>
              }
            />
            <Route
              path="/auth/register"
              element={
                <PublicRoute redirectTo="/dashboard">
                  <RegisterPage />
                </PublicRoute>
              }
            />
            <Route
              path="/auth/verify-email"
              element={
                <PublicRoute redirectTo="/dashboard">
                  <VerifyEmailPage />
                </PublicRoute>
              }
            />
            <Route
              path="/auth/forgot-password"
              element={
                <PublicRoute redirectTo="/dashboard">
                  <ForgotPasswordPage />
                </PublicRoute>
              }
            />
            <Route
              path="/auth/reset-password"
              element={
                <PublicRoute redirectTo="/dashboard">
                  <ResetPasswordPage />
                </PublicRoute>
              }
            />

            {/* Routes protégées - accessibles uniquement aux utilisateurs connectés */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <div className="min-h-screen flex items-center justify-center">
                    <div className="text-center">
                      <h1 className="text-3xl font-bold text-gray-900 mb-4">
                        Tableau de bord
                      </h1>
                      <p className="text-gray-600">
                        Bienvenue sur votre tableau de bord Lucky Kangaroo !
                      </p>
                      <p className="text-sm text-gray-500 mt-2">
                        Cette page est en cours de développement.
                      </p>
                    </div>
                  </div>
                </ProtectedRoute>
              }
            />

            {/* Routes pour les annonces */}
            <Route
              path="/listings"
              element={
                <div className="min-h-screen flex items-center justify-center">
                  <div className="text-center">
                    <h1 className="text-3xl font-bold text-gray-900 mb-4">
                      Annonces
                    </h1>
                    <p className="text-gray-600">
                      Découvrez toutes les annonces disponibles sur Lucky Kangaroo.
                    </p>
                    <p className="text-sm text-gray-500 mt-2">
                      Cette page est en cours de développement.
                    </p>
                  </div>
                </div>
              }
            />

                                    <Route
                          path="/listings/create"
                          element={
                            <ProtectedRoute>
                              <CreateListingPage />
                            </ProtectedRoute>
                          }
                        />

                        <Route
                          path="/chat"
                          element={
                            <ProtectedRoute>
                              <ChatPage />
                            </ProtectedRoute>
                          }
                        />

            {/* Routes pour les échanges */}
            <Route
              path="/exchanges"
              element={
                <ProtectedRoute>
                  <div className="min-h-screen flex items-center justify-center">
                    <div className="text-center">
                      <h1 className="text-3xl font-bold text-gray-900 mb-4">
                        Mes échanges
                      </h1>
                      <p className="text-gray-600">
                        Gérez vos échanges et négociations en cours.
                      </p>
                      <p className="text-sm text-gray-500 mt-2">
                        Cette page est en cours de développement.
                      </p>
                    </div>
                  </div>
                </ProtectedRoute>
              }
            />

            {/* Routes pour le chat */}
            <Route
              path="/chat"
              element={
                <ProtectedRoute>
                  <div className="min-h-screen flex items-center justify-center">
                    <div className="text-center">
                      <h1 className="text-3xl font-bold text-gray-900 mb-4">
                        Messages
                      </h1>
                      <p className="text-gray-600">
                        Communiquez avec les autres utilisateurs de Lucky Kangaroo.
                      </p>
                      <p className="text-sm text-gray-500 mt-2">
                        Cette page est en cours de développement.
                      </p>
                    </div>
                  </div>
                </ProtectedRoute>
              }
            />

            {/* Routes pour le profil utilisateur */}
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <div className="min-h-screen flex items-center justify-center">
                    <div className="text-center">
                      <h1 className="text-3xl font-bold text-gray-900 mb-4">
                        Mon profil
                      </h1>
                      <p className="text-gray-600">
                        Gérez vos informations personnelles et paramètres.
                      </p>
                      <p className="text-sm text-gray-500 mt-2">
                        Cette page est en cours de développement.
                      </p>
                    </div>
                  </div>
                </ProtectedRoute>
              }
            />

            {/* Routes pour les notifications */}
            <Route
              path="/notifications"
              element={
                <ProtectedRoute>
                  <div className="min-h-screen flex items-center justify-center">
                    <div className="text-center">
                      <h1 className="text-3xl font-bold text-gray-900 mb-4">
                        Notifications
                      </h1>
                      <p className="text-gray-600">
                        Consultez toutes vos notifications et alertes.
                      </p>
                      <p className="text-sm text-gray-500 mt-2">
                        Cette page est en cours de développement.
                      </p>
                    </div>
                  </div>
                </ProtectedRoute>
              }
            />

            {/* Routes pour les pages statiques */}
            <Route
              path="/about"
              element={
                <div className="min-h-screen flex items-center justify-center">
                  <div className="text-center">
                    <h1 className="text-3xl font-bold text-gray-900 mb-4">
                      À propos
                    </h1>
                    <p className="text-gray-600">
                      Découvrez l'histoire et la mission de Lucky Kangaroo.
                    </p>
                    <p className="text-sm text-gray-500 mt-2">
                      Cette page est en cours de développement.
                    </p>
                  </div>
                </div>
              }
            />

            <Route
              path="/contact"
              element={
                <div className="min-h-screen flex items-center justify-center">
                  <div className="text-center">
                    <h1 className="text-3xl font-bold text-gray-900 mb-4">
                      Contact
                    </h1>
                    <p className="text-gray-600">
                      Contactez l'équipe Lucky Kangaroo pour toute question.
                    </p>
                    <p className="text-sm text-gray-500 mt-2">
                      Cette page est en cours de développement.
                    </p>
                  </div>
                </div>
              }
            />

            <Route
              path="/terms"
              element={
                <div className="min-h-screen flex items-center justify-center">
                  <div className="text-center">
                    <h1 className="text-3xl font-bold text-gray-900 mb-4">
                      Conditions d'utilisation
                    </h1>
                    <p className="text-gray-600">
                      Consultez nos conditions d'utilisation et règles de la plateforme.
                    </p>
                    <p className="text-sm text-gray-500 mt-2">
                      Cette page est en cours de développement.
                    </p>
                  </div>
                </div>
              }
            />

            <Route
              path="/privacy"
              element={
                <div className="min-h-screen flex items-center justify-center">
                  <div className="text-center">
                    <h1 className="text-3xl font-bold text-gray-900 mb-4">
                      Politique de confidentialité
                    </h1>
                    <p className="text-gray-600">
                      Découvrez comment nous protégeons vos données personnelles.
                    </p>
                    <p className="text-sm text-gray-500 mt-2">
                      Cette page est en cours de développement.
                    </p>
                  </div>
                </div>
              }
            />

            {/* Route par défaut - redirige vers la page d'accueil */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Layout>
      </Router>
      
      {/* Toaster pour les notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: 3000,
            iconTheme: {
              primary: '#10B981',
              secondary: '#fff',
            },
          },
          error: {
            duration: 5000,
            iconTheme: {
              primary: '#EF4444',
              secondary: '#fff',
            },
          },
        }}
      />
    </ErrorBoundary>
  );
};

export default App;
