import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';

const useTranslationService = () => {
  const { i18n } = useTranslation();
  const [translationCache, setTranslationCache] = useState(new Map());
  const [isTranslating, setIsTranslating] = useState(false);
  const [currentCurrency, setCurrentCurrency] = useState(() => {
    // FORCE EUR par défaut pour site français Josmose.com
    const eurDefault = { code: 'EUR', symbol: '€', name: 'Euro' };
    
    // Vérifier localStorage et nettoyer si CAD détecté
    const saved = localStorage.getItem('userCurrency');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (parsed.code === 'CAD' || parsed.code === 'USD' || parsed.symbol === 'C$' || parsed.symbol === '$') {
          console.log('🧹 Nettoyage devise incorrecte:', parsed.code);
          localStorage.setItem('userCurrency', JSON.stringify(eurDefault));
          return eurDefault;
        }
        return parsed;
      } catch (e) {
        console.log('🧹 Erreur parse devise, forçage EUR');
        localStorage.setItem('userCurrency', JSON.stringify(eurDefault));
        return eurDefault;
      }
    }
    
    // Sauvegarder EUR par défaut
    localStorage.setItem('userCurrency', JSON.stringify(eurDefault));
    return eurDefault;
  });
  
  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  // Écouter les changements de devise
  useEffect(() => {
    const handleLanguageChange = (event) => {
      if (event.detail && event.detail.currency) {
        setCurrentCurrency(event.detail.currency);
      }
    };

    window.addEventListener('languageChanged', handleLanguageChange);
    return () => window.removeEventListener('languageChanged', handleLanguageChange);
  }, []);

  // Fonction pour traduire un texte individuel
  const translateText = useCallback(async (text, targetLanguage = null) => {
    if (!text || typeof text !== 'string') return text;
    
    const target = targetLanguage || i18n.language || 'FR';
    
    // Si c'est déjà en français, pas besoin de traduire
    if (target === 'FR') return text;
    
    // Vérifier le cache
    const cacheKey = `${text}_${target}`;
    if (translationCache.has(cacheKey)) {
      return translationCache.get(cacheKey);
    }

    try {
      setIsTranslating(true);
      
      const response = await axios.post(`${backendUrl}/api/localization/translate`, {
        text: text,
        target_language: target,
        source_language: 'FR'
      });
      
      const translatedText = response.data.translated_text;
      
      // Mettre en cache
      setTranslationCache(prev => new Map(prev.set(cacheKey, translatedText)));
      
      return translatedText;
      
    } catch (error) {
      console.error('Erreur traduction:', error);
      return text; // Fallback vers le texte original
    } finally {
      setIsTranslating(false);
    }
  }, [i18n.language, translationCache, backendUrl]);

  // Fonction pour traduire un objet complet
  const translateObject = useCallback(async (obj, targetLanguage = null) => {
    if (!obj || typeof obj !== 'object') return obj;
    
    const target = targetLanguage || i18n.language || 'FR';
    
    // Si c'est déjà en français, pas besoin de traduire
    if (target === 'FR') return obj;

    try {
      setIsTranslating(true);
      
      const response = await axios.post(`${backendUrl}/api/localization/translate-bulk`, {
        content: obj,
        target_language: target,
        source_language: 'FR'
      });
      
      return response.data.translated;
      
    } catch (error) {
      console.error('Erreur traduction objet:', error);
      return obj; // Fallback vers l'objet original
    } finally {
      setIsTranslating(false);
    }
  }, [i18n.language, backendUrl]);

  // Fonction pour récupérer les produits traduits
  const getTranslatedProducts = useCallback(async (customerType = 'B2C') => {
    try {
      setIsTranslating(true);
      
      const response = await axios.get(`${backendUrl}/api/products/translated`, {
        params: {
          customer_type: customerType,
          language: i18n.language || 'FR'
        }
      });
      
      return response.data;
      
    } catch (error) {
      console.error('Erreur récupération produits traduits:', error);
      // Fallback vers l'endpoint normal
      const fallbackResponse = await axios.get(`${backendUrl}/api/products`, {
        params: { customer_type: customerType }
      });
      return { products: fallbackResponse.data, language: 'FR', customer_type: customerType };
    } finally {
      setIsTranslating(false);
    }
  }, [i18n.language, backendUrl]);

  // Fonction pour formater les prix avec la devise actuelle
  const formatPrice = useCallback((price, showSymbol = true) => {
    if (!price || isNaN(price)) return price;
    
    const formattedPrice = parseFloat(price).toLocaleString(i18n.language, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
    
    if (showSymbol) {
      return `${formattedPrice}${currentCurrency.symbol}`;
    }
    
    return formattedPrice;
  }, [i18n.language, currentCurrency]);

  // Fonction pour vider le cache de traduction
  const clearTranslationCache = useCallback(() => {
    setTranslationCache(new Map());
  }, []);

  // Fonction pour obtenir les statistiques du cache
  const getCacheStats = useCallback(() => {
    return {
      size: translationCache.size,
      keys: Array.from(translationCache.keys())
    };
  }, [translationCache]);

  return {
    translateText,
    translateObject,
    getTranslatedProducts,
    formatPrice,
    currentCurrency,
    isTranslating,
    clearTranslationCache,
    getCacheStats,
    currentLanguage: i18n.language || 'FR'
  };
};

export default useTranslationService;