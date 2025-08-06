import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { convertDeepLToI18n } from './i18n';
import axios from 'axios';

const AutoLanguageDetector = () => {
  const { i18n } = useTranslation();
  const [detectionComplete, setDetectionComplete] = useState(false);
  const [debugInfo, setDebugInfo] = useState(null);
  
  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    const detectAndChangeLanguage = async () => {
      try {
        console.log('🔍 Détection automatique de la langue en cours...');
        
        // Appel à l'API de détection
        const response = await axios.get(`${backendUrl}/api/localization/detect`);
        const { detected_language, detected_country, currency } = response.data;
        
        console.log('🌍 Détection réussie:', {
          detected_language,
          detected_country,
          currency,
          current_i18n_language: i18n.language
        });
        
        // Mettre à jour les infos de debug pour affichage
        setDebugInfo({
          detected_language,
          detected_country,
          currency,
          current_language: i18n.language,
          ip_address: response.data.ip_address
        });
        
        // Forcer le changement de langue si différente
        if (detected_language && detected_language !== i18n.language) {
          console.log(`🔄 Changement de langue: ${i18n.language} → ${detected_language}`);
          
          // Changer la langue dans i18next
          await i18n.changeLanguage(detected_language);
          
          // Sauvegarder dans localStorage
          localStorage.setItem('i18nextLng', detected_language);
          localStorage.setItem('userCurrency', JSON.stringify(currency));
          
          // Déclencher un événement personnalisé pour d'autres composants
          const event = new CustomEvent('autoLanguageChanged', {
            detail: { 
              language: detected_language, 
              country: detected_country,
              currency: currency 
            }
          });
          window.dispatchEvent(event);
          
          console.log('✅ Langue changée automatiquement vers:', detected_language);
        } else {
          console.log('ℹ️ Langue détectée identique à la langue actuelle:', detected_language);
        }
        
      } catch (error) {
        console.error('❌ Erreur détection automatique langue:', error);
        
        // Essayer avec l'ancien endpoint en fallback
        try {
          console.log('🔄 Tentative avec l\'ancien endpoint...');
          const fallbackResponse = await axios.get(`${backendUrl}/api/detect-location`);
          const { language: fallbackLang, country_code } = fallbackResponse.data;
          
          if (fallbackLang && fallbackLang !== i18n.language) {
            console.log(`🔄 Fallback: changement de langue vers ${fallbackLang}`);
            await i18n.changeLanguage(fallbackLang);
            localStorage.setItem('i18nextLng', fallbackLang);
          }
          
          setDebugInfo({
            detected_language: fallbackLang,
            detected_country: country_code,
            current_language: i18n.language,
            fallback_used: true
          });
          
        } catch (fallbackError) {
          console.error('❌ Fallback également échoué:', fallbackError);
          setDebugInfo({ error: 'Detection failed' });
        }
      } finally {
        setDetectionComplete(true);
      }
    };

    // Attendre un petit délai pour que i18n soit complètement initialisé
    const timer = setTimeout(() => {
      detectAndChangeLanguage();
    }, 100);

    return () => clearTimeout(timer);
  }, []); // Exécuter seulement au montage

  // Composant de debug (visible seulement en dev)
  if (process.env.NODE_ENV === 'development' && debugInfo) {
    return (
      <div className="fixed bottom-4 right-4 bg-black bg-opacity-80 text-white p-3 rounded-lg text-xs z-50 max-w-sm">
        <div className="font-bold mb-2">🔍 Debug: Détection automatique</div>
        <div>IP: {debugInfo.ip_address || 'N/A'}</div>
        <div>Pays détecté: {debugInfo.detected_country}</div>
        <div>Langue détectée: {debugInfo.detected_language}</div>
        <div>Langue actuelle: {debugInfo.current_language}</div>
        <div>Devise: {debugInfo.currency?.code || 'N/A'}</div>
        {debugInfo.fallback_used && <div className="text-yellow-300">⚠️ Fallback utilisé</div>}
        {debugInfo.error && <div className="text-red-300">❌ {debugInfo.error}</div>}
        <div className="text-gray-300 mt-1">
          {detectionComplete ? '✅ Détection terminée' : '⏳ En cours...'}
        </div>
      </div>
    );
  }

  // En production, ne rien afficher
  return null;
};

export default AutoLanguageDetector;