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
        console.log('🔍 Langue française forcée par défaut - détection automatique désactivée');
        
        // FORCER LE FRANÇAIS PAR DÉFAUT - Exigence client
        if (i18n.language !== 'FR') {
          console.log(`🔄 Forçage du français: ${i18n.language} → FR`);
          await i18n.changeLanguage('FR');
          localStorage.setItem('i18nextLng', 'FR');
          console.log('✅ Langue forcée vers le français');
        } else {
          console.log('✅ Langue déjà en français');
        }
        
        setDebugInfo({
          detected_language: 'FR',
          detected_country: 'FR', 
          currency: { symbol: '€', code: 'EUR' },
          current_language: 'FR',
          forced_french: true
        });
        
      } catch (error) {
        console.error('❌ Erreur forçage français:', error);
        setDebugInfo({ error: 'French forcing failed' });
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

  // Debug complètement supprimé en production

  // En production, ne rien afficher
  return null;
};

export default AutoLanguageDetector;