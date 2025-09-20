import React, { useState, useEffect, createContext, useContext } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// ========== CONTEXT ==========
const AppContext = createContext();

const AppProvider = ({ children }) => {
  const [userLocation, setUserLocation] = useState(null);
  // 🛒 CORRECTION PANIER - Initialisation CORRECTE depuis localStorage
  const [cart, setCart] = useState(() => {
    try {
      const savedCart = localStorage.getItem('josmoze_cart');
      return savedCart ? JSON.parse(savedCart) : [];
    } catch (error) {
      console.error('Error loading cart from localStorage:', error);
      return [];
    }
  });
  
  const [customerType, setCustomerType] = useState('B2C');
  
  // 🎯 QUESTIONNAIRE - Initialisation avec vérification localStorage (PHASE 8 - Optimisé pour chatbot)
  const [showQuestionnaire, setShowQuestionnaire] = useState(() => {
    // 🚀 PHASE 8 - Désactiver temporairement pour tests Thomas Chatbot
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('phase8')) {
      console.log('🚀 PHASE 8 Testing mode activated - Questionnaire disabled');
      return false;
    }
    
    const hasSeenQuestionnaire = localStorage.getItem('hasSeenQuestionnaire');
    return !hasSeenQuestionnaire;
  });

  const [recommendations, setRecommendations] = useState([]);

  // 🛒 SAUVEGARDE AUTOMATIQUE PANIER
  useEffect(() => {
    try {
      console.log('🛒 Sauvegarde panier:', cart.length, 'articles');
      localStorage.setItem('josmoze_cart', JSON.stringify(cart));
    } catch (error) {
      console.error('Error saving cart to localStorage:', error);
    }
  }, [cart]);

  // 🛒 AJOUT AU PANIER AMÉLIORÉ
  const addToCart = (product) => {
    try {
      console.log('🛒 AJOUT PANIER - Produit:', product.name, '- Quantité:', product.quantity || 1);
      
      const existingItem = cart.find(item => item.id === product.id);
      
      if (existingItem) {
        // Augmenter quantité si produit existe
        const updatedCart = cart.map(item =>
          item.id === product.id
            ? { ...item, quantity: item.quantity + (product.quantity || 1) }
            : item
        );
        setCart(updatedCart);
        console.log('🛒 QUANTITÉ MISE À JOUR:', existingItem.quantity + 1);
      } else {
        // Ajouter nouveau produit
        const newItem = {
          id: product.id,
          name: product.name,
          price: product.price,
          image: product.image,
          quantity: product.quantity || 1
        };
        const updatedCart = [...cart, newItem];
        setCart(updatedCart);
        console.log('🛒 NOUVEL ARTICLE AJOUTÉ:', cart.length + 1, 'articles');
      }
      
      console.log('🛒 Panier sauvegardé:', cart.length + 1, 'articles');
    } catch (error) {
      console.error('🛒 Erreur ajout panier:', error);
    }
  };

  // 🛒 SUPPRESSION DU PANIER
  const removeFromCart = (productId) => {
    const updatedCart = cart.filter(item => item.id !== productId);
    setCart(updatedCart);
  };

  // 🛒 MISE À JOUR QUANTITÉ
  const updateQuantity = (productId, quantity) => {
    if (quantity <= 0) {
      removeFromCart(productId);
      return;
    }
    
    const updatedCart = cart.map(item =>
      item.id === productId ? { ...item, quantity } : item
    );
    setCart(updatedCart);
  };

  // 🛒 VIDER LE PANIER
  const clearCart = () => {
    setCart([]);
    localStorage.removeItem('josmoze_cart');
  };

  // 💰 CALCUL TOTAL PANIER
  const getCartTotal = () => {
    return cart.reduce((total, item) => total + (item.price * item.quantity), 0);
  };

  // 💰 FORMATAGE PRIX
  const formatPrice = (price) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR'
    }).format(price);
  };

  // 🎯 GESTION QUESTIONNAIRE
  const handleQuestionnaireClose = () => {
    setShowQuestionnaire(false);
    localStorage.setItem('hasSeenQuestionnaire', 'true');
  };
  
  const openQuestionnaire = () => {
    setShowQuestionnaire(true);
  };

  const handleQuestionnaireRecommendation = (recommendation) => {
    console.log('🎯 Recommandation reçue:', recommendation);
    setRecommendations(prev => [...prev, recommendation]);
    handleQuestionnaireClose();
  };

  // Missing properties that App.js components expect
  const updateCartQuantity = updateQuantity; // Alias for compatibility
  const loading = false; // Add loading state

  return (
    <AppContext.Provider value={{
      userLocation,
      cart,
      customerType,
      showQuestionnaire,
      recommendations,
      addToCart,
      removeFromCart,
      updateQuantity,
      clearCart,
      getCartTotal,
      formatPrice,
      setCustomerType,
      handleQuestionnaireClose,
      handleQuestionnaireRecommendation
    }}>
      {children}
    </AppContext.Provider>
  );
};

const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
};

export { AppProvider, useApp, AppContext };