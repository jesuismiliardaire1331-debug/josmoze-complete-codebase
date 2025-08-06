import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';

const LanguageSelector = () => {
  const { i18n, t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [availableLanguages, setAvailableLanguages] = useState({});
  const [currentCurrency, setCurrentCurrency] = useState({ code: 'EUR', symbol: '€' });
  const [loading, setLoading] = useState(false);
  
  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  // Charger les langues disponibles et détecter automatiquement
  useEffect(() => {
    detectUserLocalization();
    loadAvailableLanguages();
  }, []);

  const detectUserLocalization = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${backendUrl}/api/localization/detect`);
      const { detected_language, currency, available_languages } = response.data;
      
      console.log('Détection automatique:', { detected_language, currency });
      
      // Changer automatiquement la langue si différente
      if (detected_language && detected_language !== i18n.language) {
        await i18n.changeLanguage(detected_language);
        localStorage.setItem('i18nextLng', detected_language);
      }
      
      // Mettre à jour la devise
      if (currency) {
        setCurrentCurrency(currency);
        localStorage.setItem('userCurrency', JSON.stringify(currency));
      }
      
      // Mettre à jour les langues disponibles
      if (available_languages) {
        setAvailableLanguages(available_languages);
      }
      
    } catch (error) {
      console.error('Erreur détection localization:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadAvailableLanguages = async () => {
    try {
      const response = await axios.get(`${backendUrl}/api/localization/languages`);
      setAvailableLanguages(response.data);
    } catch (error) {
      console.error('Erreur chargement langues:', error);
      // Fallback vers les langues par défaut
      setAvailableLanguages({
        'FR': { name: 'Français', native_name: 'Français', flag: '🇫🇷' },
        'EN-GB': { name: 'English', native_name: 'English', flag: '🇬🇧' },
        'ES': { name: 'Español', native_name: 'Español', flag: '🇪🇸' },
        'IT': { name: 'Italiano', native_name: 'Italiano', flag: '🇮🇹' },
        'DE': { name: 'Deutsch', native_name: 'Deutsch', flag: '🇩🇪' },
        'NL': { name: 'Nederlands', native_name: 'Nederlands', flag: '🇳🇱' },
        'PT-PT': { name: 'Português', native_name: 'Português', flag: '🇵🇹' },
        'PL': { name: 'Polski', native_name: 'Polski', flag: '🇵🇱' }
      });
    }
  };

  const changeLanguage = async (languageCode) => {
    try {
      setLoading(true);
      
      // Changer la langue dans i18next
      await i18n.changeLanguage(languageCode);
      
      // Sauvegarder dans localStorage
      localStorage.setItem('i18nextLng', languageCode);
      
      // Mettre à jour la devise selon la langue/pays
      const currencyMap = {
        'FR': { code: 'EUR', symbol: '€', name: 'Euro' },
        'EN-GB': { code: 'GBP', symbol: '£', name: 'Livre Sterling' },
        'EN-US': { code: 'USD', symbol: '$', name: 'Dollar US' },
        'ES': { code: 'EUR', symbol: '€', name: 'Euro' },
        'IT': { code: 'EUR', symbol: '€', name: 'Euro' },
        'DE': { code: 'EUR', symbol: '€', name: 'Euro' },
        'NL': { code: 'EUR', symbol: '€', name: 'Euro' },
        'PT-PT': { code: 'EUR', symbol: '€', name: 'Euro' },
        'PL': { code: 'PLN', symbol: 'zł', name: 'Złoty' }
      };
      
      const newCurrency = currencyMap[languageCode] || { code: 'EUR', symbol: '€', name: 'Euro' };
      setCurrentCurrency(newCurrency);
      localStorage.setItem('userCurrency', JSON.stringify(newCurrency));
      
      // Fermer le dropdown
      setIsOpen(false);
      
      // Trigger un event personnalisé pour que d'autres composants réagissent
      const event = new CustomEvent('languageChanged', {
        detail: { language: languageCode, currency: newCurrency }
      });
      window.dispatchEvent(event);
      
      console.log(`Langue changée vers: ${languageCode}, Devise: ${newCurrency.code}`);
      
    } catch (error) {
      console.error('Erreur changement de langue:', error);
    } finally {
      setLoading(false);
    }
  };

  const currentLanguage = i18n.language || 'FR';
  const currentLanguageData = availableLanguages[currentLanguage] || { 
    name: 'Français', 
    native_name: 'Français', 
    flag: '🇫🇷' 
  };

  return (
    <div className="relative inline-block text-left">
      {/* Bouton de sélection de langue */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="inline-flex items-center justify-center w-full rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        disabled={loading}
      >
        <span className="mr-2 text-lg">{currentLanguageData.flag}</span>
        <span className="mr-2">{currentLanguageData.native_name}</span>
        <span className="ml-2 text-xs text-gray-500">({currentCurrency.symbol})</span>
        {loading ? (
          <svg className="ml-2 h-4 w-4 animate-spin" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" className="opacity-25" fill="none"/>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
          </svg>
        ) : (
          <svg className="ml-2 h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        )}
      </button>

      {/* Dropdown menu */}
      {isOpen && (
        <div className="absolute right-0 z-50 mt-2 w-72 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
          <div className="py-1">
            <div className="px-4 py-2 text-sm text-gray-500 border-b border-gray-200">
              {t('language.selector', 'Choisir la langue')}
            </div>
            {Object.entries(availableLanguages).map(([code, data]) => (
              <button
                key={code}
                onClick={() => changeLanguage(code)}
                className={`block w-full text-left px-4 py-3 text-sm hover:bg-gray-100 transition-colors duration-150 ${
                  currentLanguage === code 
                    ? 'bg-blue-50 text-blue-700 font-medium' 
                    : 'text-gray-700'
                }`}
                disabled={loading}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <span className="mr-3 text-lg">{data.flag}</span>
                    <div>
                      <div className="font-medium">{data.native_name}</div>
                      <div className="text-xs text-gray-500">{data.name}</div>
                    </div>
                  </div>
                  {currentLanguage === code && (
                    <svg className="h-4 w-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  )}
                </div>
              </button>
            ))}
          </div>
          
          {/* Section informations */}
          <div className="border-t border-gray-200 px-4 py-3">
            <div className="text-xs text-gray-500">
              Devise actuelle: <span className="font-medium text-gray-700">{currentCurrency.name} ({currentCurrency.symbol})</span>
            </div>
            <div className="text-xs text-gray-400 mt-1">
              La devise change automatiquement selon votre région
            </div>
          </div>
        </div>
      )}
      
      {/* Overlay pour fermer le dropdown */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};

export default LanguageSelector;