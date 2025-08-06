import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import Backend from 'i18next-http-backend';

const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Configuration des langues disponibles
const supportedLanguages = ['FR', 'EN-GB', 'EN-US', 'ES', 'IT', 'DE', 'NL', 'PT-PT', 'PL'];

// Map DeepL language codes to i18next language codes
const languageCodeMap = {
  'EN-US': 'EN-US',
  'EN-GB': 'EN-GB', 
  'FR': 'FR',
  'ES': 'ES',
  'IT': 'IT',
  'DE': 'DE',
  'NL': 'NL',
  'PT-PT': 'PT-PT',
  'PL': 'PL'
};

// Ressources de traduction par défaut (fallback)
const resources = {
  'FR': {
    translation: {
      // Navigation
      'nav.home': 'Accueil',
      'nav.individuals': 'Particuliers', 
      'nav.professionals': 'Professionnels',
      'nav.installation': 'Installation',
      'nav.contact': 'Contact',
      'nav.cart': 'Panier',
      
      // Hero section
      'hero.title': 'Eau Pure & Saine avec l\'Osmose Inverse',
      'hero.subtitle': 'Filtration professionnelle pour votre santé et celle de votre famille',
      'hero.cta': 'Découvrir nos Solutions',
      
      // Produits
      'products.title': 'Nos Solutions d\'Osmose Inverse',
      'products.addToCart': 'Ajouter au Panier',
      'products.outOfStock': 'Rupture de Stock',
      'products.stockLimited': 'Stock Limité',
      
      // Panier
      'cart.title': 'Votre Panier',
      'cart.empty': 'Votre panier est vide',
      'cart.total': 'Total',
      'cart.checkout': 'Finaliser la Commande',
      'cart.quantity': 'Quantité',
      'cart.remove': 'Supprimer',
      
      // Contact
      'contact.title': 'Demande de Devis',
      'contact.name': 'Nom',
      'contact.email': 'Email',
      'contact.phone': 'Téléphone',
      'contact.company': 'Entreprise',
      'contact.message': 'Message',
      'contact.send': 'Envoyer',
      'contact.success': 'Message Envoyé!',
      
      // Footer
      'footer.about': 'À propos de Josmose',
      'footer.contact': 'Contact',
      'footer.legal': 'Mentions Légales',
      'footer.privacy': 'Confidentialité',
      
      // Localization
      'language.selector': 'Choisir la langue',
      'currency.symbol': '€',
      'shipping.cost': 'Frais de port'
    }
  },
  'EN-GB': {
    translation: {
      // Navigation  
      'nav.home': 'Home',
      'nav.individuals': 'Individuals',
      'nav.professionals': 'Professionals', 
      'nav.installation': 'Installation',
      'nav.contact': 'Contact',
      'nav.cart': 'Cart',
      
      // Hero section
      'hero.title': 'Pure & Healthy Water with Reverse Osmosis',
      'hero.subtitle': 'Professional filtration for you and your family\'s health',
      'hero.cta': 'Discover Our Solutions',
      
      // Products
      'products.title': 'Our Reverse Osmosis Solutions',
      'products.addToCart': 'Add to Cart',
      'products.outOfStock': 'Out of Stock',
      'products.stockLimited': 'Limited Stock',
      
      // Cart
      'cart.title': 'Your Cart',
      'cart.empty': 'Your cart is empty',
      'cart.total': 'Total',
      'cart.checkout': 'Checkout',
      'cart.quantity': 'Quantity',
      'cart.remove': 'Remove',
      
      // Contact
      'contact.title': 'Request Quote',
      'contact.name': 'Name',
      'contact.email': 'Email', 
      'contact.phone': 'Phone',
      'contact.company': 'Company',
      'contact.message': 'Message',
      'contact.send': 'Send',
      'contact.success': 'Message Sent!',
      
      // Footer
      'footer.about': 'About Josmose',
      'footer.contact': 'Contact',
      'footer.legal': 'Legal Notice',
      'footer.privacy': 'Privacy',
      
      // Localization
      'language.selector': 'Choose language',
      'currency.symbol': '£',
      'shipping.cost': 'Shipping cost'
    }
  },
  'ES': {
    translation: {
      // Navigation
      'nav.home': 'Inicio',
      'nav.individuals': 'Particulares',
      'nav.professionals': 'Profesionales',
      'nav.installation': 'Instalación',
      'nav.contact': 'Contacto',
      'nav.cart': 'Carrito',
      
      // Hero section
      'hero.title': 'Agua Pura y Sana con Ósmosis Inversa',
      'hero.subtitle': 'Filtración profesional para su salud y la de su familia',
      'hero.cta': 'Descubrir Nuestras Soluciones',
      
      // Products
      'products.title': 'Nuestras Soluciones de Ósmosis Inversa',
      'products.addToCart': 'Añadir al Carrito',
      'products.outOfStock': 'Sin Stock',
      'products.stockLimited': 'Stock Limitado',
      
      // Currency
      'currency.symbol': '€',
      'shipping.cost': 'Gastos de envío'
    }
  },
  'DE': {
    translation: {
      // Navigation
      'nav.home': 'Startseite',
      'nav.individuals': 'Privatkunden',
      'nav.professionals': 'Geschäftskunden', 
      'nav.installation': 'Installation',
      'nav.contact': 'Kontakt',
      'nav.cart': 'Warenkorb',
      
      // Hero section
      'hero.title': 'Reines & Gesundes Wasser mit Umkehrosmose',
      'hero.subtitle': 'Professionelle Filtration für Ihre Gesundheit und die Ihrer Familie',
      'hero.cta': 'Unsere Lösungen Entdecken',
      
      // Currency
      'currency.symbol': '€',
      'shipping.cost': 'Versandkosten'
    }
  }
};

// Configuration i18next
i18n
  .use(Backend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    lng: 'FR', // langue par défaut
    fallbackLng: 'FR',
    
    supportedLngs: supportedLanguages,
    
    // Configuration pour accepter les codes avec tirets
    load: 'languageOnly',
    cleanCode: false,
    
    debug: process.env.NODE_ENV === 'development',
    
    detection: {
      // Options de détection de langue
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
      excludeCacheFor: ['cimode'],
      lookupLocalStorage: 'i18nextLng'
    },
    
    backend: {
      // Configuration pour charger les traductions depuis notre API
      loadPath: `${backendUrl}/api/localization/translate-bulk`,
      addPath: `${backendUrl}/api/localization/translate`,
      allowMultiLoading: false,
      crossDomain: true,
      
      // Custom request function pour utiliser notre API
      request: (options, url, payload, callback) => {
        // Si on charge les traductions par défaut, utiliser les ressources locales
        if (url.includes('/localization/')) {
          const lng = options.lng || 'FR';
          const namespace = options.ns || 'translation';
          
          if (resources[lng] && resources[lng][namespace]) {
            callback(null, {
              status: 200,
              data: resources[lng][namespace]
            });
          } else {
            callback(null, {
              status: 404,
              data: {}
            });
          }
        } else {
          callback(new Error('Translation backend not available'), {
            status: 404,
            data: {}
          });
        }
      }
    },
    
    resources: resources,
    
    interpolation: {
      escapeValue: false, // React est déjà sécurisé
      format: function(value, format, lng) {
        if (format === 'currency') {
          // Formatage de devise selon la langue
          const currencyMap = {
            'FR': '€',
            'EN-GB': '£',
            'EN-US': '$',
            'ES': '€',
            'IT': '€', 
            'DE': '€',
            'NL': '€',
            'PT-PT': '€',
            'PL': 'zł'
          };
          
          const symbol = currencyMap[lng] || '€';
          return `${value}${symbol}`;
        }
        return value;
      }
    },
    
    react: {
      useSuspense: false,
      bindI18n: 'languageChanged loaded',
      bindI18nStore: 'added removed',
      transEmptyNodeValue: '',
      transSupportBasicHtmlNodes: true,
      transKeepBasicHtmlNodesFor: ['br', 'strong', 'i', 'p']
    }
  });

export default i18n;