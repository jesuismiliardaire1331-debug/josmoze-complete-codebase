import React, { useState, useEffect, Suspense } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, useNavigate, useSearchParams, Link } from "react-router-dom";
import axios from "axios";

// Import traduction
import './i18n';
import { useTranslation } from 'react-i18next';
import LanguageSelector from './LanguageSelector';
import useTranslationService from './useTranslationService';
import AutoLanguageDetector from './AutoLanguageDetector';

// Import context
import { AppProvider, useApp } from './context/AppContext';

// Import CRM components
import CRMDashboard from "./CRM";
import AdminUploadImages from './AdminUploadImages';
import PromotionsManager from './PromotionsManager';
import EspaceClient from './EspaceClient';
import CheckoutWithPromo from './CheckoutWithPromo';
import { AuthProvider } from './UserAuth';
import { AuthProvider as CRMAuthProvider } from "./CRMLogin";
import CRMLogin from "./CRMLogin";
import ProductExplanation from "./ProductExplanation";
import { NotificationProvider } from "./NotificationSystem";
import ProductRecommendations from "./ProductRecommendations";

// Import ChatBot
import ChatBotV2 from "./ChatBot_V2";

// Import Translation Guardian  
import TranslationGuardian from "./TranslationGuardian";
import ProductQuestionnaire from "./ProductQuestionnaire";
import StripeCheckout from "./StripeCheckout";
import ProductDetail from "./ProductDetail";
import AdminUpload from "./AdminUpload";
import BlogPage from "./BlogPage";
import BlogArticle from "./BlogArticle";
import TestimonialsPage from "./TestimonialsPage";
import AdminLogin from "./AdminLogin";
import AIUploadAgent from "./AIUploadAgent";
import AdminDashboard from "./AdminDashboard";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// ========== UTILITY FUNCTIONS ==========

const getUrlParameter = (name) => {
  name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
  const regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
  const results = regex.exec(window.location.search);
  return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
};

// ========== PAYMENT FUNCTIONS ==========

const pollPaymentStatus = async (sessionId, attempts = 0) => {
  const maxAttempts = 10;
  const pollInterval = 2000; // 2 seconds

  if (attempts >= maxAttempts) {
    return { success: false, message: 'Vérification du paiement expirée. Veuillez consulter votre email de confirmation.' };
  }

  try {
    // 🔄 NOUVEAU SYSTÈME DE POLLING STRIPE
    const response = await fetch(`${API}/payments/checkout/status/${sessionId}`);
    if (!response.ok) {
      throw new Error('Erreur vérification paiement');
    }

    const data = await response.json();
    
    // Vérifier si paiement réussi
    if (data.payment_status === 'paid') {
      return { 
        success: true, 
        message: 'Paiement réussi ! Merci pour votre commande.', 
        data: data
      };
    } else if (data.status === 'expired') {
      return { 
        success: false, 
        message: 'Session de paiement expirée. Veuillez réessayer.' 
      };
    }

    // Si paiement en cours, continuer le polling
    console.log(`🔄 Polling paiement (${attempts + 1}/${maxAttempts}):`, data.payment_status);
    await new Promise(resolve => setTimeout(resolve, pollInterval));
    return await pollPaymentStatus(sessionId, attempts + 1);
    
  } catch (error) {
    console.error('Erreur vérification paiement:', error);
    return { success: false, message: 'Erreur lors de la vérification. Veuillez réessayer.' };
  }
};

// ========== COMPONENTS ==========

const Header = () => {
  const { cart, userLocation } = useApp();
  const { t } = useTranslation();
  const navigate = useNavigate();
  
  const cartItemsCount = cart.reduce((total, item) => total + item.quantity, 0);

  // Force domain display to josmoze.com even in development
  const displayDomain = "www.josmoze.com";

  return (
    <header className="bg-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex flex-col cursor-pointer" onClick={() => navigate('/')}>
            <div className="header-brand">
              <div className="site-name">
                <h1 className="text-2xl font-bold text-blue-600">
                  {displayDomain}
                </h1>
              </div>
              <div className="tagline">
                <span className="text-sm text-gray-600">
                  💧 {t('hero.subtitle', 'Filtration professionnelle')}
                </span>
              </div>
            </div>
          </div>
          
          <nav className="hidden md:flex items-center space-x-8">
            <Link to="/" className="text-gray-700 hover:text-blue-600 transition-colors">
              {t('nav.home', 'Accueil')}
            </Link>
            <Link to="/particuliers" className="text-gray-700 hover:text-blue-600 transition-colors">
              {t('nav.individuals', 'Particuliers')}
            </Link>
            <Link to="/professionnels" className="text-gray-700 hover:text-blue-600 transition-colors">
              {t('nav.professionals', 'Professionnels')}
            </Link>
            <Link to="/installation" className="text-gray-700 hover:text-blue-600 transition-colors">
              {t('nav.installation', 'Installation')}
            </Link>
            <Link to="/blog" className="text-gray-700 hover:text-blue-600 transition-colors">
              📚 Blog
            </Link>
            <Link to="/temoignages" className="text-gray-700 hover:text-blue-600 transition-colors">
              ⭐ Avis
            </Link>
            <Link to="/contact" className="text-gray-700 hover:text-blue-600 transition-colors">
              {t('nav.contact', 'Contact')}
            </Link>
            <Link to="/crm-login" className="text-gray-500 hover:text-blue-600 transition-colors text-sm">
              📊 CRM
            </Link>
          </nav>
          
          <div className="flex items-center space-x-4">
            {/* Sélecteur de langue */}
            <LanguageSelector />
            
            {/* Panier */}
            <button 
              onClick={() => navigate('/panier')}
              className="relative p-2 text-gray-600 hover:text-blue-600 transition-colors"
              title={t('nav.cart', 'Panier')}
            >
              🛒
              {cartItemsCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-6 w-6 flex items-center justify-center">
                  {cartItemsCount}
                </span>
              )}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

const Hero = () => {
  const { userLocation, formatPrice, customerType, openQuestionnaire } = useApp();
  const { t } = useTranslation();
  const navigate = useNavigate();

  const heroTitle = customerType === 'B2B' ? t('hero.title.b2b') : t('hero.title.b2c');
  const heroSubtitle = customerType === 'B2B' ? t('hero.subtitle.b2b') : t('hero.subtitle.b2c');
  
  const basePrice = customerType === 'B2B' ? 899 : 499;
  const originalPrice = customerType === 'B2B' ? 1199 : 599;

  return (
    <div className="relative bg-gradient-to-r from-blue-600 to-blue-800 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <div className="mb-4">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                customerType === 'B2B' 
                  ? 'bg-orange-500 bg-opacity-20 text-orange-200' 
                  : 'bg-green-500 bg-opacity-20 text-green-200'
              }`}>
                {customerType === 'B2B' ? '🏢 Solutions Professionnelles' : '🏠 Solutions Particuliers'}
              </span>
            </div>
            
            <h1 className="text-5xl font-bold mb-6 leading-tight">
              {heroTitle}
            </h1>
            <p className="text-xl mb-8 text-blue-100">
              {heroSubtitle}
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 mb-8">
              <div className="bg-white bg-opacity-20 rounded-lg p-4 text-center">
                <div className="text-3xl font-bold">{formatPrice(basePrice)}</div>
                <div className="text-sm line-through opacity-75">{formatPrice(originalPrice)}</div>
                <div className="text-sm">{customerType === 'B2B' ? 'Prix Pro HT' : t('hero.special_price')}</div>
              </div>
              
              <div className="bg-white bg-opacity-20 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold">99%</div>
                <div className="text-sm">Contaminants éliminés</div>
              </div>
              
              {customerType === 'B2B' && (
                <div className="bg-white bg-opacity-20 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold">500L+</div>
                  <div className="text-sm">Capacité journalière</div>
                </div>
              )}
            </div>
            
            <div className="flex flex-col sm:flex-row gap-4">
              <button
                onClick={() => {
                  document.querySelector('#products-section')?.scrollIntoView({ behavior: 'smooth' });
                }}
                className="bg-white text-blue-600 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-blue-50 transition-colors shadow-lg"
              >
                {customerType === 'B2B' ? t('hero.cta') + ' 🏢' : t('hero.cta') + ' 🏠'}
              </button>
              
              {customerType !== 'B2B' && (
                <button
                  onClick={openQuestionnaire}
                  className="bg-green-600 text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-green-700 transition-colors shadow-lg"
                >
                  🎯 Trouvez votre osmoseur
                </button>
              )}
              
              {customerType === 'B2B' && (
                <button 
                  onClick={() => navigate('/consultation')}
                  className="bg-green-600 text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-green-700 transition-colors shadow-lg"
                >
                  📞 Consultation Pro
                </button>
              )}
            </div>
            
            <div className="mt-8 text-sm text-blue-100">
              {t('hero.guarantee')}
            </div>
          </div>
          
          <div className="relative">
            <img
              src={customerType === 'B2B' 
                ? "https://www.josmoze.com/img/cms/fontaine_a_eau_entreprise%20-%20copie.jpg"
                : "https://static.wixstatic.com/media/6af6bd_d5ec79a577694414b12e794e8a30e3bb~mv2.png/v1/fill/w_558,h_684,al_c,q_90,usm_0.66_1.00_0.01,enc_avif,quality_auto/Hf8e72e690708417d8f7fae61845a5e804_png_720x720q50.png"
              }
              alt={customerType === 'B2B' ? "Fontaine à eau pour entreprise" : "Fontaine intelligente"}
              className="w-full h-auto rounded-lg shadow-2xl"
            />
            <div className="absolute inset-0 bg-blue-600 bg-opacity-20 rounded-lg"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

const ProductGrid = () => {
  const [products, setProducts] = useState([]);
  const { addToCart, formatPrice, customerType } = useApp();
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        // Utiliser l'endpoint standard des produits
        const response = await axios.get(`${API}/products?customer_type=${customerType}`);
        setProducts(response.data || []);
        console.log('✅ Produits chargés pour type client:', customerType);
        console.log('📦 Nombre de produits chargés:', (response.data || []).length);
        console.log('🏷️ Liste des produits:', (response.data || []).map(p => `${p.name} - ${p.price}€`));
      } catch (error) {
        console.error('Failed to fetch products:', error);
        setProducts([]);
      }
    };

    fetchProducts();

    // Écouter les changements de langue
    const handleLanguageChange = () => {
      console.log('🔄 Changement de langue détecté, rechargement des produits...');
      fetchProducts();
    };

    window.addEventListener('languageChanged', handleLanguageChange);
    window.addEventListener('autoLanguageChanged', handleLanguageChange);

    return () => {
      window.removeEventListener('languageChanged', handleLanguageChange);
      window.removeEventListener('autoLanguageChanged', handleLanguageChange);
    };
  }, [customerType, i18n.language]); // Utiliser i18n.language

  const handleAddToCart = (product) => {
    addToCart(product);
    // Show feedback (could use toast notification)
    alert(`${product.name} ajouté au panier!`);
  };

  return (
    <div id="products-section" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-12">
        <div className="flex justify-center mb-6">
          <div className="flex bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => window.dispatchEvent(new CustomEvent('changeCustomerType', { detail: 'B2C' }))}
              className={`px-6 py-2 rounded-md font-medium transition-colors ${
                customerType === 'B2C'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {t('customer.individuals')}
            </button>
            <button
              onClick={() => window.dispatchEvent(new CustomEvent('changeCustomerType', { detail: 'B2B' }))}
              className={`px-6 py-2 rounded-md font-medium transition-colors ${
                customerType === 'B2B'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {t('customer.professionals')}
            </button>
          </div>
        </div>
        
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          {customerType === 'B2B' ? t('products.title.b2b') : t('products.title.b2c')}
        </h2>
        
        <p className="text-gray-600">
          {customerType === 'B2B' ? t('products.subtitle.b2b') : t('products.subtitle.b2c')}
        </p>
      </div>
      
      <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
        {products.map(product => (
          <div key={product.id} className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
            <img
              src={product.image}
              alt={product.name}
              className="w-full h-48 object-cover"
            />
            
            <div className="p-6">
              {customerType === 'B2B' && product.target_audience === 'B2B' && (
                <div className="mb-2">
                  <span className="bg-orange-100 text-orange-800 text-xs font-medium px-2 py-1 rounded-full">
                    {t('products.professionalBadge')}
                  </span>
                </div>
              )}
              
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {product.name}
              </h3>
              
              <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                {product.description}
              </p>
              
              <div className="flex items-center justify-between mb-4">
                <div>
                  <span className="text-2xl font-bold text-blue-600">
                    {formatPrice(product.price)}
                  </span>
                  {product.original_price && (
                    <span className="ml-2 text-sm text-gray-500 line-through">
                      {formatPrice(product.original_price)}
                    </span>
                  )}
                  {customerType === 'B2B' && (
                    <div className="text-xs text-purple-600 font-medium">{t('products.professionalPrice')}</div>
                  )}
                </div>
                
                <div className="text-right">
                  {product.stock_info?.in_stock ? (
                    <div>
                      <span className="text-green-600 text-sm">{t('products.inStock')}</span>
                      {product.stock_info?.show_stock_warning && (
                        <div className="text-orange-600 text-xs font-semibold mt-1 bg-orange-50 px-2 py-1 rounded-full">
                          {t('products.stockLimited')}
                        </div>
                      )}
                    </div>
                  ) : (
                    <span className="text-red-600 text-sm">{t('products.outOfStockStatus')}</span>
                  )}
                </div>
              </div>

              <button
                onClick={() => navigate(`/produit/${product.id}`)}
                className="w-full mb-2 bg-gray-100 text-gray-700 py-2 px-4 rounded-lg font-medium hover:bg-gray-200 transition-colors text-sm"
              >
                📋 Voir les Détails
              </button>
              
              {product.features && product.features.length > 0 && (
                <ul className="text-xs text-gray-600 mb-4 space-y-1">
                  {product.features.slice(0, 3).map((feature, idx) => (
                    <li key={idx}>• {feature}</li>
                  ))}
                </ul>
              )}
              
              <button
                onClick={(event) => {
                  if (product.stock_info?.in_stock) {
                    addToCart(product, 1);
                    // Feedback visuel
                    const button = event.target;
                    const originalText = button.textContent;
                    button.textContent = '✅ Ajouté !';
                    button.style.backgroundColor = '#10B981';
                    setTimeout(() => {
                      button.textContent = originalText;
                      button.style.backgroundColor = '';
                    }, 1500);
                  }
                }}
                disabled={!product.stock_info?.in_stock}
                className={`w-full py-3 px-4 rounded-lg font-semibold transition-colors ${
                  product.stock_info?.in_stock
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                {product.stock_info?.in_stock 
                  ? (customerType === 'B2B' ? t('products.addToCart.b2b') : t('products.addToCart.b2c'))
                  : t('products.outOfStock')
                }
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Add customer type change listener
const CustomerTypeHandler = () => {
  const { setCustomerType } = useApp();
  
  useEffect(() => {
    const handleCustomerTypeChange = (event) => {
      setCustomerType(event.detail);
    };
    
    window.addEventListener('changeCustomerType', handleCustomerTypeChange);
    
    return () => {
      window.removeEventListener('changeCustomerType', handleCustomerTypeChange);
    };
  }, [setCustomerType]);
  
  return null;
};

const Features = () => {
  const { customerType } = useApp();
  const { t } = useTranslation();

  const b2cFeatures = [
    {
      icon: "🦠",
      title: t('features.elimination.title', "Élimination Totale"),
      description: t('features.elimination.description', "Supprime 99% des virus, bactéries, chlore et particules organiques grâce à notre système 4 étapes.")
    },
    {
      icon: "⚡",
      title: t('features.installation.title', "Installation Simple"),
      description: t('features.installation.description', "Aucun électricien nécessaire! Installation rapide sans électricité, utilise uniquement la pression du réseau.")
    },
    {
      icon: "💰", 
      title: t('features.savings.title', "Économies Garanties"),
      description: t('features.savings.description', "Économisez 500-700€ par an en supprimant l'achat de bouteilles d'eau. Rentabilité en moins d'un an.")
    }
  ];

  const b2bFeatures = [
    {
      icon: "🏭",
      title: t('features.b2b.capacity.title', "Capacité Industrielle"), 
      description: t('features.b2b.capacity.description', "Systèmes haute capacité pour restaurants, bureaux et commerces. Jusqu'à 500L/jour de production.")
    },
    {
      icon: "📊",
      title: t('features.b2b.monitoring.title', "Monitoring Avancé"),
      description: t('features.b2b.monitoring.description', "Surveillance en temps réel de la qualité, alerts automatiques et maintenance prédictive incluse.")
    },
    {
      icon: "🛠️",
      title: t('features.b2b.support.title', "Support Dédié"),
      description: t('features.b2b.support.description', "Installation professionnelle, formation personnel et maintenance 24/7 avec techniciens certifiés.")
    }
  ];

  const features = customerType === 'B2B' ? b2bFeatures : b2cFeatures;

  return (
    <div className="bg-gray-50 py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
          {customerType === 'B2B' 
            ? t('features.title.b2b', 'Pourquoi Choisir Nos Solutions Pro? 💼')
            : t('features.title.b2c', 'Pourquoi Choisir Nos Systèmes? 🌟')
          }
        </h2>
        
        <div className="grid md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="bg-white p-8 rounded-lg shadow-md text-center">
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold mb-4">{feature.title}</h3>
              <p className="text-gray-600">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const InstallationGuide = () => {
  return (
    <div className="bg-white py-16">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Installation Rapide et Simple 🔧
          </h2>
          <p className="text-gray-600 text-lg">
            Suivez notre guide étape par étape ou faites appel à nos experts
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <h3 className="text-2xl font-semibold mb-6">Vidéo d'Installation</h3>
            <div className="bg-gray-100 rounded-lg p-4">
              <div className="aspect-w-16 aspect-h-9">
                <iframe 
                  width="100%" 
                  height="300"
                  src="https://www.youtube.com/embed/jP8H2CfV2Z8"
                  title="Installation fontaine osmoseur OJA Mini Bluesea"
                  frameBorder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                  allowFullScreen
                  className="rounded-lg"
                ></iframe>
              </div>
              <div className="text-center mt-4">
                <h4 className="text-lg font-medium mb-2">Guide Vidéo Complet</h4>
                <p className="text-gray-600 text-sm">
                  Installation étape par étape de votre fontaine osmoseur en quelques minutes
                </p>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-2xl font-semibold mb-6">Étapes d'Installation</h3>
            <div className="space-y-4">
              {[
                { step: 1, title: "Préparation", desc: "Coupez l'arrivée d'eau et préparez les outils" },
                { step: 2, title: "Fixation", desc: "Fixez le système sous l'évier avec les supports" },
                { step: 3, title: "Raccordement", desc: "Connectez les tuyaux d'entrée et de sortie" },
                { step: 4, title: "Test", desc: "Ouvrez l'eau et vérifiez l'étanchéité" },
                { step: 5, title: "Rinçage", desc: "Laissez couler 10 minutes pour activer les filtres" }
              ].map((item) => (
                <div key={item.step} className="flex items-center space-x-4">
                  <div className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold text-sm">
                    {item.step}
                  </div>
                  <div>
                    <h4 className="font-semibold">{item.title}</h4>
                    <p className="text-gray-600 text-sm">{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-8 p-4 bg-blue-50 rounded-lg">
              <h4 className="font-semibold text-blue-800 mb-2">🛠️ Service d'Installation</h4>
              <p className="text-blue-700 text-sm mb-3">
                Préférez une installation professionnelle? Nos techniciens se déplacent chez vous!
              </p>
              <button className="bg-blue-600 text-white px-4 py-2 rounded font-medium text-sm hover:bg-blue-700 transition-colors">
                Réserver un Technicien (150€)
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const ConsultationExpert = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    company: '',
    consultation_type: 'diagnostic',
    preferred_time: '',
    notes: ''
  });
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // First create lead
      const leadResponse = await axios.post(`${API}/leads`, {
        name: formData.name,
        email: formData.email,
        phone: formData.phone,
        company: formData.company,
        lead_type: "consultation",
        customer_type: "B2B",
        consultation_requested: true,
        preferred_contact_time: formData.preferred_time,
        message: formData.notes,
        source: "consultation_form"
      });

      if (leadResponse.data.lead_id) {
        // Then create consultation request
        await axios.post(`${API}/consultation/request`, {
          lead_id: leadResponse.data.lead_id,
          consultation_type: formData.consultation_type,
          preferred_time: formData.preferred_time,
          notes: formData.notes
        });
      }

      setSubmitted(true);
    } catch (error) {
      console.error('Consultation request failed:', error);
      alert('Erreur lors de la demande. Veuillez réessayer.');
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center">
        <div className="text-6xl mb-6">✅</div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Consultation Programmée!</h2>
        <p className="text-gray-600 mb-8">
          Un expert vous contactera dans les prochaines heures pour programmer votre consultation gratuite.
        </p>
        <div className="bg-green-50 rounded-lg p-6 mb-8">
          <h3 className="text-lg font-semibold text-green-800 mb-2">Ce qui vous attend :</h3>
          <ul className="text-green-700 text-sm space-y-1">
            <li>📞 Appel de notre expert dans les 2h</li>
            <li>🔍 Diagnostic complet de vos besoins</li>
            <li>💡 Solution personnalisée et devis détaillé</li>
            <li>📊 Analyse ROI et recommandations</li>
          </ul>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-16">
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Consultation Gratuite avec un Expert 📞
        </h2>
        <p className="text-gray-600 text-lg">
          Obtenez un diagnostic complet et une solution adaptée à vos besoins professionnels
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-12">
        <div>
          <h3 className="text-xl font-semibold mb-6">Ce que vous obtiendrez :</h3>
          <div className="space-y-4">
            {[
              { icon: "🔍", title: "Analyse de vos besoins", desc: "Diagnostic précis de votre situation actuelle" },
              { icon: "💡", title: "Solution personnalisée", desc: "Recommandations adaptées à votre activité" },
              { icon: "📊", title: "Étude de rentabilité", desc: "Calcul du ROI et des économies réalisables" },
              { icon: "🎯", title: "Devis détaillé", desc: "Prix transparent avec options et garanties" },
              { icon: "📅", title: "Planning d'installation", desc: "Organisation de la mise en place" }
            ].map((item, index) => (
              <div key={index} className="flex items-start space-x-3">
                <div className="text-2xl">{item.icon}</div>
                <div>
                  <h4 className="font-semibold">{item.title}</h4>
                  <p className="text-gray-600 text-sm">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-8 p-4 bg-blue-50 rounded-lg">
            <h4 className="font-semibold text-blue-800 mb-2">🏆 Nos Experts</h4>
            <p className="text-blue-700 text-sm">
              Ingénieurs spécialisés avec +10 ans d'expérience dans le traitement de l'eau industriel.
              Certifications ISO et formations techniques continues.
            </p>
          </div>
        </div>

        <div>
          <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-8">
            <div className="grid md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nom complet *
                </label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email *
                </label>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
            
            <div className="grid md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Téléphone *
                </label>
                <input
                  type="tel"
                  required
                  value={formData.phone}
                  onChange={(e) => setFormData({...formData, phone: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Entreprise
                </label>
                <input
                  type="text"
                  value={formData.company}
                  onChange={(e) => setFormData({...formData, company: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
            
            <div className="grid md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Type de consultation
                </label>
                <select
                  value={formData.consultation_type}
                  onChange={(e) => setFormData({...formData, consultation_type: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="diagnostic">Diagnostic complet</option>
                  <option value="installation">Conseils installation</option>
                  <option value="maintenance">Maintenance préventive</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Horaire préféré
                </label>
                <select
                  value={formData.preferred_time}
                  onChange={(e) => setFormData({...formData, preferred_time: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Indifférent</option>
                  <option value="morning">Matin (9h-12h)</option>
                  <option value="afternoon">Après-midi (14h-17h)</option>
                  <option value="evening">Soir (17h-19h)</option>
                </select>
              </div>
            </div>
            
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Détails sur vos besoins
              </label>
              <textarea
                rows="4"
                value={formData.notes}
                onChange={(e) => setFormData({...formData, notes: e.target.value})}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Décrivez votre activité, vos besoins en eau, nombre d'employés..."
              />
            </div>
            
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
            >
              {loading ? 'Envoi en cours...' : 'Demander une Consultation Gratuite 📞'}
            </button>
            
            <div className="mt-4 text-xs text-gray-500">
              <p>🔒 Vos données sont protégées et ne seront jamais partagées</p>
              <p>⏰ Réponse garantie sous 2 heures en jour ouvré</p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

const CartSummary = () => {
  const { cart, getCartTotal, formatPrice, removeFromCart, updateCartQuantity, clearCart } = useApp();
  const { t } = useTranslation();
  const navigate = useNavigate();
  
  // 🛒 DEBUG PANIER - Console logs pour diagnostic
  console.log('🛒 CartSummary - Panier actuel:', cart);
  console.log('🛒 CartSummary - Longueur panier:', cart.length);
  console.log('🛒 CartSummary - localStorage direct:', localStorage.getItem('josmoze_cart'));
  
  if (cart.length === 0) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center">
        <div className="text-4xl mb-4">🛒</div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">{t('cart.empty')}</h2>
        <p className="text-gray-600 mb-6">{t('cart.emptySubtitle')}</p>
        <button
          onClick={() => navigate('/')}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
        >
          {t('cart.viewProducts')}
        </button>
      </div>
    );
  }

  const { subtotal, shipping, total } = getCartTotal();

  const handleCheckout = () => {
    navigate('/checkout');
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-16">
      <h2 className="text-3xl font-bold text-gray-900 mb-8">{t('cart.title')}</h2>
      
      <div className="grid lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          {cart.map(item => (
            <div key={item.id} className="bg-white rounded-lg shadow-md p-6 mb-4">
              <div className="flex items-center space-x-4">
                <img src={item.image} alt={item.name} className="w-16 h-16 object-cover rounded" />
                
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">{item.name}</h3>
                  <p className="text-gray-600">{formatPrice(item.price)}</p>
                </div>
                
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => updateCartQuantity(item.id, item.quantity - 1)}
                    className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center"
                  >
                    -
                  </button>
                  <span className="w-8 text-center">{item.quantity}</span>
                  <button
                    onClick={() => updateCartQuantity(item.id, item.quantity + 1)}
                    className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center"
                  >
                    +
                  </button>
                </div>
                
                <button
                  onClick={() => removeFromCart(item.id)}
                  className="text-red-600 hover:text-red-800 ml-4"
                >
                  🗑️
                </button>
              </div>
            </div>
          ))}
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-6 h-fit">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">{t('cart.summary')}</h3>
          
          <div className="space-y-2 mb-4">
            <div className="flex justify-between">
              <span>{t('cart.subtotal')}</span>
              <span>{formatPrice(subtotal)}</span>
            </div>
            <div className="flex justify-between">
              <span>{t('cart.shipping')}</span>
              <span>{formatPrice(shipping)}</span>
            </div>
            <hr />
            <div className="flex justify-between font-semibold text-lg">
              <span>{t('cart.total')}</span>
              <span>{formatPrice(total)}</span>
            </div>
          </div>
          
          <button 
            onClick={handleCheckout}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors mb-2"
          >
            {t('cart.checkout')}
          </button>
          
          <button
            onClick={clearCart}
            className="w-full bg-gray-300 text-gray-700 py-2 rounded-lg font-medium hover:bg-gray-400 transition-colors text-sm"
          >
            {t('cart.continueShop')}
          </button>
        </div>
      </div>
    </div>
  );
};

const CheckoutForm = () => {
  const { cart, getCartTotal, formatPrice, clearCart, customerType } = useApp();
  const [customerInfo, setCustomerInfo] = useState({
    name: '',
    email: '',
    phone: '',
    company: customerType === 'B2B' ? '' : undefined,
    // 🆕 ADRESSE OBLIGATOIRE
    address: {
      street: '',
      postal_code: '',
      city: '',
      country: 'France'
    }
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  if (cart.length === 0) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center">
        <div className="text-4xl mb-4">🛒</div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Votre panier est vide</h2>
        <button
          onClick={() => navigate('/')}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
        >
          Voir nos produits
        </button>
      </div>
    );
  }

  const { subtotal, shipping, total } = getCartTotal();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (!customerInfo.name || !customerInfo.email || !customerInfo.address.street || !customerInfo.address.postal_code || !customerInfo.address.city) {
      setError('Veuillez remplir tous les champs obligatoires, y compris l\'adresse de livraison');
      setLoading(false);
      return;
    }

    try {
      // 🛒 TRAQUER PANIER ABANDONNÉ avant checkout
      if (cart.length > 0) {
        const cartData = {
          customer_email: customerInfo.email,
          customer_name: customerInfo.name,
          customer_phone: customerInfo.phone,
          customer_address: customerInfo.address,
          items: cart.map(item => ({
            product_id: item.id,
            name: item.name,
            quantity: item.quantity,
            price: item.price
          })),
          total_value: total,
          currency: "EUR",
          source_page: "/checkout",
          browser_info: {
            userAgent: navigator.userAgent,
            timestamp: new Date().toISOString()
          }
        };
        
        // Enregistrer le panier abandonné
        try {
          await axios.post(`${API}/abandoned-carts/track`, cartData);
        } catch (abandonedCartError) {
          console.log('Could not track abandoned cart:', abandonedCartError);
          // Continue avec le checkout même si le tracking échoue
        }
      }

      // 💳 NOUVEAU FLUX DE PAIEMENT STRIPE INTÉGRÉ
      const cartItems = cart.map(item => ({
        product_id: item.id,
        quantity: item.quantity,
        price: item.price
      }));

      // Créer session de paiement avec le nouveau système
      const response = await axios.post(`${API}/checkout/session`, {
        cart_items: cartItems,
        customer_info: {
          ...customerInfo,
          customer_type: customerType // B2C ou B2B
        },
        origin_url: window.location.origin
      });

      if (response.data.url) {
        // Redirection vers Stripe Checkout
        console.log('🎯 Redirection vers Stripe:', response.data.session_id);
        window.location.href = response.data.url;
      } else {
        throw new Error('URL de paiement non reçue');
      }

    } catch (error) {
      console.error('Erreur checkout:', error);
      setError(error.response?.data?.detail || 'Erreur lors du paiement. Veuillez réessayer.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-16">
      <h2 className="text-3xl font-bold text-gray-900 mb-8">
        Finaliser la Commande {customerType === 'B2B' ? '🏢' : '💳'}
      </h2>
      
      <div className="grid lg:grid-cols-2 gap-8">
        <div>
          <h3 className="text-xl font-semibold mb-4">
            {customerType === 'B2B' ? 'Informations Entreprise' : 'Informations de Contact'}
          </h3>
          
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {customerType === 'B2B' ? 'Nom du contact' : 'Nom complet'} *
              </label>
              <input
                type="text"
                required
                value={customerInfo.name}
                onChange={(e) => setCustomerInfo({...customerInfo, name: e.target.value})}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email {customerType === 'B2B' ? 'professionnel' : ''} *
              </label>
              <input
                type="email"
                required
                value={customerInfo.email}
                onChange={(e) => setCustomerInfo({...customerInfo, email: e.target.value})}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Téléphone
              </label>
              <input
                type="tel"
                value={customerInfo.phone}
                onChange={(e) => setCustomerInfo({...customerInfo, phone: e.target.value})}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            {customerType === 'B2B' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Entreprise *
                </label>
                <input
                  type="text"
                  required
                  value={customerInfo.company || ''}
                  onChange={(e) => setCustomerInfo({...customerInfo, company: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            )}
            
            {/* 🆕 ADRESSE DE LIVRAISON OBLIGATOIRE */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-6">
              <h4 className="text-lg font-semibold text-blue-900 mb-4 flex items-center">
                🚚 Adresse de Livraison *
                <span className="text-sm font-normal text-blue-700 ml-2">(Obligatoire)</span>
              </h4>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-blue-900 mb-2">
                    Adresse complète *
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="123 Rue de la République"
                    value={customerInfo.address.street}
                    onChange={(e) => setCustomerInfo({
                      ...customerInfo, 
                      address: {...customerInfo.address, street: e.target.value}
                    })}
                    className="w-full px-4 py-3 border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-blue-900 mb-2">
                      Code Postal *
                    </label>
                    <input
                      type="text"
                      required
                      placeholder="75001"
                      value={customerInfo.address.postal_code}
                      onChange={(e) => setCustomerInfo({
                        ...customerInfo, 
                        address: {...customerInfo.address, postal_code: e.target.value}
                      })}
                      className="w-full px-4 py-3 border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-blue-900 mb-2">
                      Ville *
                    </label>
                    <input
                      type="text"
                      required
                      placeholder="Paris"
                      value={customerInfo.address.city}
                      onChange={(e) => setCustomerInfo({
                        ...customerInfo, 
                        address: {...customerInfo.address, city: e.target.value}
                      })}
                      className="w-full px-4 py-3 border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-blue-900 mb-2">
                    Pays
                  </label>
                  <select
                    value={customerInfo.address.country}
                    onChange={(e) => setCustomerInfo({
                      ...customerInfo, 
                      address: {...customerInfo.address, country: e.target.value}
                    })}
                    className="w-full px-4 py-3 border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="France">France</option>
                    <option value="Espagne">Espagne</option>
                    <option value="Italie">Italie</option>
                    <option value="Allemagne">Allemagne</option>
                    <option value="Belgique">Belgique</option>
                    <option value="Pays-Bas">Pays-Bas</option>
                  </select>
                </div>
              </div>
            </div>
            
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
            >
              {loading 
                ? 'Redirection vers le paiement...' 
                : (customerType === 'B2B' ? 'Finaliser la Commande Pro 🏢' : 'Payer maintenant 💳')
              }
            </button>
          </form>
          
          <div className="mt-4 text-xs text-gray-500">
            <p>🔒 Paiement sécurisé avec Stripe</p>
            <p>💳 Cartes acceptées, Apple Pay, Google Pay</p>
            {customerType === 'B2B' && <p>💼 Paiement en plusieurs fois disponible pour les professionnels</p>}
            {customerType === 'B2C' && <p>🏦 Paiement en plusieurs fois disponible</p>}
          </div>
        </div>
        
        <div className="bg-gray-50 rounded-lg p-6">
          <h3 className="text-xl font-semibold mb-4">Récapitulatif de la commande</h3>
          
          <div className="space-y-4 mb-4">
            {cart.map(item => (
              <div key={item.id} className="flex justify-between items-center">
                <div>
                  <div className="font-medium text-sm">{item.name}</div>
                  <div className="text-gray-600 text-xs">Quantité: {item.quantity}</div>
                </div>
                <div className="text-sm font-medium">
                  {formatPrice(item.price * item.quantity)}
                </div>
              </div>
            ))}
          </div>
          
          <hr className="mb-4" />
          
          <div className="space-y-2 mb-4">
            <div className="flex justify-between text-sm">
              <span>Sous-total:</span>
              <span>{formatPrice(subtotal)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Livraison:</span>
              <span>{formatPrice(shipping)}</span>
            </div>
            {customerType === 'B2B' && (
              <div className="flex justify-between text-sm text-gray-600">
                <span>TVA (20%):</span>
                <span>{formatPrice(total * 0.2)}</span>
              </div>
            )}
            <div className="flex justify-between font-semibold text-lg">
              <span>Total {customerType === 'B2B' ? 'TTC' : ''}:</span>
              <span>{formatPrice(customerType === 'B2B' ? total * 1.2 : total)}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const PaymentSuccess = () => {
  const [status, setStatus] = useState({ message: 'Vérification du paiement...', type: 'pending' });
  const { clearCart } = useApp();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const sessionId = searchParams.get('session_id');
    
    if (sessionId) {
      const checkPayment = async () => {
        const result = await pollPaymentStatus(sessionId);
        setStatus({
          message: result.message,
          type: result.success ? 'success' : 'error'
        });
        
        if (result.success) {
          // Clear cart on successful payment
          clearCart();
        }
      };
      
      checkPayment();
    } else {
      setStatus({
        message: 'Session de paiement non trouvée',
        type: 'error'
      });
    }
  }, [searchParams, clearCart]);

  return (
    <div className="max-w-2xl mx-auto px-4 py-16 text-center">
      <div className="text-6xl mb-6">
        {status.type === 'success' ? '✅' : status.type === 'error' ? '❌' : '⏳'}
      </div>
      
      <h2 className="text-2xl font-bold text-gray-900 mb-4">
        {status.type === 'success' ? 'Paiement Réussi!' : 
         status.type === 'error' ? 'Problème de Paiement' : 'Vérification...'}
      </h2>
      
      <p className={`text-lg mb-8 ${
        status.type === 'success' ? 'text-green-600' : 
        status.type === 'error' ? 'text-red-600' : 'text-gray-600'
      }`}>
        {status.message}
      </p>
      
      {status.type === 'success' && (
        <div className="bg-green-50 rounded-lg p-6 mb-8">
          <h3 className="text-lg font-semibold text-green-800 mb-2">Prochaines étapes:</h3>
          <ul className="text-green-700 text-sm space-y-1">
            <li>📧 Vous recevrez un email de confirmation</li>
            <li>📦 Votre commande sera préparée sous 24-48h</li>
            <li>🚚 Livraison gratuite à votre domicile</li>
            <li>🔧 Instructions d'installation incluses</li>
            <li>📞 Support technique disponible 7j/7</li>
          </ul>
        </div>
      )}
      
      <div className="space-x-4">
        <button
          onClick={() => navigate('/')}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
        >
          Retour à l'accueil
        </button>
        
        {status.type === 'error' && (
          <button
            onClick={() => navigate('/panier')}
            className="bg-gray-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-gray-700 transition-colors"
          >
            Retour au panier
          </button>
        )}
      </div>
    </div>
  );
};

const PaymentCancelled = () => {
  const navigate = useNavigate();
  
  return (
    <div className="max-w-2xl mx-auto px-4 py-16 text-center">
      <div className="text-6xl mb-6">😕</div>
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Paiement Annulé</h2>
      <p className="text-gray-600 mb-8">
        Votre paiement a été annulé. Vos articles sont toujours dans votre panier.
      </p>
      
      <div className="space-x-4">
        <button
          onClick={() => navigate('/panier')}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
        >
          Retour au panier
        </button>
        
        <button
          onClick={() => navigate('/')}
          className="bg-gray-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-gray-700 transition-colors"
        >
          Continuer les achats
        </button>
      </div>
    </div>
  );
};

const UnsubscribeHandler = () => {
  const [status, setStatus] = useState({ message: 'Traitement de votre désinscription...', type: 'pending' });
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const token = searchParams.get('token');
    
    if (!token) {
      setStatus({
        message: 'Token de désinscription manquant',
        type: 'error'
      });
      return;
    }

    const processUnsubscribe = async () => {
      try {
        // WORKAROUND: Appeler l'API backend directement
        const response = await axios.get(`${API}/public/unsubscribe?token=${token}`);
        
        setStatus({
          message: 'Désinscription réussie! Vous ne recevrez plus d\'emails de JOSMOSE.COM',
          type: 'success'
        });
      } catch (error) {
        console.error('Erreur désinscription:', error);
        setStatus({
          message: 'Erreur lors de la désinscription. Le lien peut être expiré.',
          type: 'error'
        });
      }
    };

    processUnsubscribe();
  }, [searchParams]);

  return (
    <div className="max-w-2xl mx-auto px-4 py-16 text-center">
      <div className="text-6xl mb-6">
        {status.type === 'success' ? '✅' : status.type === 'error' ? '❌' : '⏳'}
      </div>
      
      <h2 className="text-2xl font-bold text-gray-900 mb-4">
        {status.type === 'success' ? 'Désinscription Réussie' : 
         status.type === 'error' ? 'Erreur de Désinscription' : 'Traitement...'}
      </h2>
      
      <p className={`text-lg mb-8 ${
        status.type === 'success' ? 'text-green-600' : 
        status.type === 'error' ? 'text-red-600' : 'text-gray-600'
      }`}>
        {status.message}
      </p>
      
      {status.type === 'success' && (
        <div className="bg-green-50 rounded-lg p-6 mb-8">
          <h3 className="text-lg font-semibold text-green-800 mb-2">Conformité GDPR</h3>
          <ul className="text-green-700 text-sm space-y-1">
            <li>🛡️ Vos données ont été supprimées de nos listes</li>
            <li>📧 Vous ne recevrez plus d'emails marketing</li>
            <li>🔒 Action enregistrée dans notre journal de conformité</li>
            <li>📞 Pour toute question: contact@josmoze.com</li>
          </ul>
        </div>
      )}
      
      <button
        onClick={() => window.location.href = 'https://www.josmoze.com'}
        className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
      >
        Retour au site
      </button>
    </div>
  );
};

const ContactForm = () => {
  const { customerType } = useApp();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    company: customerType === 'B2B' ? '' : '',
    message: '',
    request_type: 'quote',
    consultation_requested: false,
    preferred_contact_time: ''
  });
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/contact`, {
        ...formData,
        customer_type: customerType
      });
      setSubmitted(true);
    } catch (error) {
      console.error('Contact form submission failed:', error);
      alert('Erreur lors de l\'envoi du formulaire');
    }
  };

  if (submitted) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center">
        <div className="text-4xl mb-4">✅</div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Message Envoyé!</h2>
        <p className="text-gray-600">
          {customerType === 'B2B' 
            ? 'Un expert commercial vous contactera sous 2 heures en jour ouvré.'
            : 'Nous vous répondrons dans les plus brefs délais.'
          }
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-16">
      <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">
        {customerType === 'B2B' ? 'Demande de Devis Professionnel 📋' : 'Demande de Devis 📋'}
      </h2>
      
      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-8">
        <div className="grid md:grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nom complet *
            </label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email *
            </label>
            <input
              type="email"
              required
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
        
        <div className="grid md:grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Téléphone
            </label>
            <input
              type="tel"
              value={formData.phone}
              onChange={(e) => setFormData({...formData, phone: e.target.value})}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          {customerType === 'B2B' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Entreprise *
              </label>
              <input
                type="text"
                required
                value={formData.company}
                onChange={(e) => setFormData({...formData, company: e.target.value})}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          )}
        </div>
        
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Type de demande
          </label>
          <select
            value={formData.request_type}
            onChange={(e) => setFormData({...formData, request_type: e.target.value})}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="quote">Demande de devis</option>
            <option value="consultation">Consultation technique</option>
            <option value="support">Support technique</option>
            <option value="general">Information générale</option>
          </select>
        </div>

        {customerType === 'B2B' && (
          <div className="mb-6">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={formData.consultation_requested}
                onChange={(e) => setFormData({...formData, consultation_requested: e.target.checked})}
                className="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <span className="text-sm text-gray-700">
                Je souhaite une consultation gratuite avec un expert
              </span>
            </label>
          </div>
        )}
        
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Message *
          </label>
          <textarea
            required
            rows="4"
            value={formData.message}
            onChange={(e) => setFormData({...formData, message: e.target.value})}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder={customerType === 'B2B' 
              ? "Décrivez vos besoins : nombre d'employés, type d'activité, consommation d'eau estimée..."
              : "Décrivez votre besoin en détail..."
            }
          />
        </div>
        
        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
        >
          {customerType === 'B2B' ? 'Envoyer ma Demande Pro 🏢' : 'Envoyer ma Demande 📤'}
        </button>
      </form>
    </div>
  );
};

const Footer = () => {
  const { userLocation, customerType } = useApp();

  return (
    <footer className="bg-gray-900 text-white py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-xl font-bold mb-4">Josmoze.com</h3>
            <p className="text-gray-300 text-sm">
              Spécialiste européen des systèmes d'osmose inverse. 
              Solutions pour particuliers et professionnels.
            </p>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Produits</h4>
            <ul className="text-gray-300 text-sm space-y-2">
              <li>Systèmes d'osmose domestiques</li>
              <li>Solutions professionnelles</li>
              <li>Filtres de rechange</li>
              <li>Extensions garantie</li>
              <li>Service d'installation</li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Support</h4>
            <ul className="text-gray-300 text-sm space-y-2">
              <li>Guide d'installation</li>
              <li>Maintenance</li>
              <li>Garantie</li>
              <li>Contact expert</li>
              {customerType === 'B2B' && <li>Consultation gratuite</li>}
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Europe 🇪🇺</h4>
            <p className="text-gray-300 text-sm mb-2">
              Livraison dans toute l'Europe
            </p>
            {userLocation && (
              <p className="text-blue-400 text-sm">
                📍 Actuellement: {userLocation.country_name}
              </p>
            )}
            <div className="mt-4">
              <p className="text-xs text-gray-400">
                🏠 Solutions Particuliers | 🏢 Solutions Pro
              </p>
            </div>
          </div>
        </div>
        
        <hr className="border-gray-700 my-8" />
        
        <div className="text-center text-gray-300 text-sm">
          <p>&copy; 2024 Josmoze.com - Eau pure pour l'Europe 💧</p>
        </div>
      </div>
    </footer>
  );
};

// ========== MAIN APP ==========

const Home = () => {
  const { cart, customerType } = useApp();
  
  const handleProductClick = (product) => {
    // Navigate to product or add to cart
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div>
      <Hero />
      <Features />
      <ProductGrid />
      
      {/* Recommandations intelligentes */}
      <div className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4">
          <ProductRecommendations
            customerId={null}
            currentCart={cart}
            customerType={customerType}
            context={{ page: 'home', section: 'recommendations' }}
            onProductClick={handleProductClick}
            maxRecommendations={4}
            title="🎯 Produits Recommandés pour Vous"
          />
        </div>
      </div>
      
      <InstallationGuide />
    </div>
  );
};

const BusinessHome = () => {
  const { cart, customerType } = useApp();
  
  const handleProductClick = (product) => {
    // Navigate to product or add to cart
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div>
      <Hero />
      <Features />
      <ProductGrid />
      
      {/* Recommandations B2B */}
      <div className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4">
          <ProductRecommendations
            customerId={null}
            currentCart={cart}
            customerType="B2B"
            context={{ page: 'business-home', section: 'b2b-recommendations' }}
            onProductClick={handleProductClick}
            maxRecommendations={4}
            title="🏢 Solutions Professionnelles Recommandées"
          />
        </div>
      </div>
      
      <ConsultationExpert />
    </div>
  );
};

const Cart = () => {
  return <CartSummary />;
};

const Checkout = () => {
  return <CheckoutForm />;
};

const Contact = () => {
  return <ContactForm />;
};

const Installation = () => {
  return <InstallationGuide />;
};

const Consultation = () => {
  return <ConsultationExpert />;
};

const QuestionnaireWrapper = () => {
  const { showQuestionnaire, closeQuestionnaire, handleQuestionnaireRecommendation, formatPrice } = useApp();
  
  return (
    <ProductQuestionnaire
      isOpen={showQuestionnaire}
      onClose={closeQuestionnaire}
      onRecommendation={handleQuestionnaireRecommendation}
      formatPrice={formatPrice}
    />
  );
};

function App() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Chargement de la traduction...</p>
      </div>
    </div>}>
      <NotificationProvider>  
        <TranslationGuardian>
          <AuthProvider>
            <AppProvider>
              <div className="App min-h-screen flex flex-col">
              <BrowserRouter>
                <AutoLanguageDetector />
                <CustomerTypeHandler />
                <Header />
                <main>
                  <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/particuliers" element={<Home />} />
                    <Route path="/professionnels" element={<BusinessHome />} />
                    <Route path="/produit/:productId" element={<ProductDetail />} />
                    <Route path="/panier" element={<Cart />} />
                    <Route path="/checkout" element={<Checkout />} />
                    <Route path="/contact" element={<Contact />} />
                    <Route path="/installation" element={<Installation />} />
                    <Route path="/consultation" element={<Consultation />} />
                    <Route path="/comment-ca-marche" element={<ProductExplanation />} />
                    <Route path="/promotions-manager" element={<PromotionsManager />} />
                    <Route path="/payment-success" element={<PaymentSuccess />} />
                    <Route path="/payment-cancelled" element={<PaymentCancelled />} />
                    {/* CRM Routes - Solution simplifiée */}
                    <Route path="/crm-login" element={<CRMLogin />} />
                    <Route path="/crm" element={<CRMDashboard />} />
                    <Route path="/crm/*" element={<CRMDashboard />} />
                    {/* WORKAROUND: Route publique désinscription */}
                    <Route path="/unsubscribe" element={<UnsubscribeHandler />} />
                    <Route path="/admin/upload" element={<AdminUpload />} />
                    <Route path="/blog" element={<BlogPage />} />
                    <Route path="/blog/:slug" element={<BlogArticle />} />
                    <Route path="/temoignages" element={<TestimonialsPage />} />
                    <Route path="/admin/login" element={<AdminLogin />} />
                    <Route path="/admin/dashboard" element={<AdminDashboard />} />
                    <Route path="/admin/ai-upload" element={<AIUploadAgent />} />
                    <Route path="/admin/upload-images" element={<AdminUploadImages />} />
                    <Route path="/admin/promotions" element={<PromotionsManager />} />
                    <Route path="/espace-client" element={<EspaceClient />} />
                    <Route path="/checkout-promo" element={<CheckoutWithPromo />} />
                  </Routes>
                </main>
                <Footer />
                {/* ChatBot pour prospects */}
                <ChatBotV2 />
                {/* Questionnaire produits */}
                <QuestionnaireWrapper />
              </BrowserRouter>
              </div>
            </AppProvider>
          </AuthProvider>
        </TranslationGuardian>
      </NotificationProvider>
    </Suspense>
  );
}

export default App;
export { useApp };