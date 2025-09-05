import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Globe } from 'lucide-react';

// Types
interface Currency {
  code: string;
  symbol: string;
  name: string;
  rate: number;
}

const CurrencySelector: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedCurrency, setSelectedCurrency] = useState<Currency>({
    code: 'EUR',
    symbol: '€',
    name: 'Euro',
    rate: 1.0
  });

  // Devises disponibles
  const currencies: Currency[] = [
    { code: 'EUR', symbol: '€', name: 'Euro', rate: 1.0 },
    { code: 'CHF', symbol: 'CHF', name: 'Franc Suisse', rate: 0.95 },
    { code: 'USD', symbol: '$', name: 'Dollar US', rate: 1.08 },
    { code: 'GBP', symbol: '£', name: 'Livre Sterling', rate: 0.86 },
    { code: 'JPY', symbol: '¥', name: 'Yen Japonais', rate: 158.0 },
    { code: 'CAD', symbol: 'C$', name: 'Dollar Canadien', rate: 1.47 },
    { code: 'AUD', symbol: 'A$', name: 'Dollar Australien', rate: 1.65 }
  ];

  // Détection automatique de la devise par géolocalisation
  useEffect(() => {
    const detectCurrencyByLocation = () => {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition((position) => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          
          // Détection géographique simple
          if (lat >= 45.8 && lat <= 47.8 && lng >= 5.9 && lng <= 10.5) {
            // Suisse
            const chfCurrency = currencies.find(c => c.code === 'CHF');
            if (chfCurrency) setSelectedCurrency(chfCurrency);
          } else if (lat >= 41.3 && lat <= 51.1 && lng >= -5.1 && lng <= 9.6) {
            // France/Europe
            const eurCurrency = currencies.find(c => c.code === 'EUR');
            if (eurCurrency) setSelectedCurrency(eurCurrency);
          } else if (lat >= 49.2 && lat <= 60.9 && lng >= -8.2 && lng <= 1.8) {
            // UK
            const gbpCurrency = currencies.find(c => c.code === 'GBP');
            if (gbpCurrency) setSelectedCurrency(gbpCurrency);
          } else if (lat >= 41.7 && lat <= 83.1 && lng >= -141.0 && lng <= -52.6) {
            // Amérique du Nord
            const usdCurrency = currencies.find(c => c.code === 'USD');
            if (usdCurrency) setSelectedCurrency(usdCurrency);
          }
        });
      }
    };

    // Charger la devise sauvegardée ou détecter par géolocalisation
    const savedCurrency = localStorage.getItem('preferredCurrency');
    if (savedCurrency) {
      const saved = currencies.find(c => c.code === savedCurrency);
      if (saved) {
        setSelectedCurrency(saved);
      }
    } else {
      detectCurrencyByLocation();
    }
  }, []);

  const handleCurrencyChange = (currency: Currency) => {
    setSelectedCurrency(currency);
    localStorage.setItem('preferredCurrency', currency.code);
    setIsOpen(false);
    
    // Émettre un événement personnalisé pour notifier le changement de devise
    window.dispatchEvent(new CustomEvent('currencyChanged', { detail: currency }));
  };

  const toggleDropdown = () => setIsOpen(!isOpen);

  return (
    <div className="relative">
      <button
        onClick={toggleDropdown}
        className="flex items-center space-x-2 px-3 py-2 bg-gray-50 hover:bg-gray-100 border border-gray-300 rounded-lg text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        aria-label="Sélectionner la devise"
      >
        <Globe className="w-4 h-4 text-gray-500" />
        <span className="font-medium text-gray-700">
          {selectedCurrency.symbol} {selectedCurrency.code}
        </span>
        <ChevronDown 
          className={`w-4 h-4 text-gray-500 transition-transform duration-200 ${
            isOpen ? 'rotate-180' : ''
          }`} 
        />
      </button>

      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-40"
              onClick={() => setIsOpen(false)}
            />
            
            {/* Dropdown */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: -10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -10 }}
              transition={{ duration: 0.15 }}
              className="absolute right-0 mt-2 w-64 bg-white rounded-xl shadow-xl border border-gray-200 py-2 z-50"
            >
              {/* Header */}
              <div className="px-4 py-2 border-b border-gray-100">
                <h3 className="text-sm font-semibold text-gray-900">Sélectionner la devise</h3>
                <p className="text-xs text-gray-500">Choisissez votre devise préférée</p>
              </div>

              {/* Liste des devises */}
              <div className="py-2 max-h-60 overflow-y-auto">
                {currencies.map((currency) => (
                  <button
                    key={currency.code}
                    onClick={() => handleCurrencyChange(currency)}
                    className={`w-full flex items-center justify-between px-4 py-3 text-left hover:bg-gray-50 transition-colors ${
                      selectedCurrency.code === currency.code 
                        ? 'bg-primary-50 text-primary-700' 
                        : 'text-gray-700'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                        <span className="text-sm font-medium text-gray-600">
                          {currency.symbol}
                        </span>
                      </div>
                      <div>
                        <div className="font-medium">{currency.name}</div>
                        <div className="text-xs text-gray-500">{currency.code}</div>
                      </div>
                    </div>
                    
                    {selectedCurrency.code === currency.code && (
                      <div className="w-5 h-5 bg-primary-600 rounded-full flex items-center justify-center">
                        <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      </div>
                    )}
                  </button>
                ))}
              </div>

              {/* Footer avec taux de change */}
              <div className="px-4 py-3 border-t border-gray-100 bg-gray-50 rounded-b-xl">
                <div className="text-xs text-gray-500">
                  <div className="flex justify-between">
                    <span>1 EUR = {selectedCurrency.rate.toFixed(2)} {selectedCurrency.code}</span>
                    <span className="text-xs text-gray-400">
                      Dernière mise à jour: {new Date().toLocaleDateString('fr-FR')}
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};

export default CurrencySelector;
