import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import Backend from 'i18next-http-backend';

const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Configuration des langues disponibles - utiliser des codes compatibles i18next
const supportedLanguages = ['FR', 'EN', 'ES', 'IT', 'DE', 'NL', 'PT', 'PL'];

// Map DeepL language codes to i18next language codes
const deepLToI18nMap = {
  'FR': 'FR',
  'EN-US': 'EN', 
  'EN-GB': 'EN',
  'ES': 'ES',
  'IT': 'IT',
  'DE': 'DE',
  'NL': 'NL',
  'PT-PT': 'PT',
  'PL': 'PL'
};

// Map inverse pour l'affichage
const i18nToDeepLMap = {
  'FR': 'FR',
  'EN': 'EN-GB', // Par défaut britannique pour l'Europe
  'ES': 'ES',
  'IT': 'IT', 
  'DE': 'DE',
  'NL': 'NL',
  'PT': 'PT-PT',
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
      
      // Hero section - B2C
      'hero.title.b2c': 'Eau Pure avec Système d\'Osmose Inverse',
      'hero.subtitle.b2c': 'Éliminez 99% des contaminants avec notre technologie avancée',
      'hero.title.b2b': 'Solutions Professionnelles d\'Osmose Inverse',
      'hero.subtitle.b2b': 'Équipez votre entreprise avec nos systèmes industriels',
      'hero.special_price': 'Prix spécial Europe',
      'hero.original_price': 'Prix normal',
      'hero.cta': 'Commander Maintenant',
      'hero.guarantee': '✓ Garantie 2 ans ✓ Installation incluse ✓ SAV France',
      
      // Contaminants section
      'contaminants.title': 'Contaminants éliminés',
      'contaminants.chlore': 'Chlore',
      'contaminants.plomb': 'Plomb',
      'contaminants.pesticides': 'Pesticides',
      'contaminants.nitrates': 'Nitrates',
      'contaminants.virus': 'Virus & Bactéries',
      'contaminants.metaux': 'Métaux lourds',
      
      // Products section
      'products.title.b2c': 'Nos Produits 💧',
      'products.title.b2b': 'Solutions Professionnelles 💼',
      'products.subtitle.b2c': 'Systèmes d\'osmose inverse pour votre foyer',
      'products.subtitle.b2b': 'Systèmes industriels pour restaurants, bureaux et commerces',
      'products.addToCart.b2c': 'Ajouter au Panier 🛒',
      'products.addToCart.b2b': 'Demander un Devis 📋',
      'products.outOfStock': 'Indisponible',
      'products.inStock': '✅ En stock',
      'products.outOfStockStatus': '❌ Rupture',
      'products.stockLimited': '⚠️ Stock limité !',
      'products.professionalPrice': 'Prix Professionnel HT',
      'products.professionalBadge': 'Solution Pro',
      
      // Customer type selector
      'customer.individuals': '👨‍👩‍👧‍👦 Particuliers',
      'customer.professionals': '🏢 Professionnels',
      
      // Cart
      'cart.title': 'Votre Panier 🛒',
      'cart.empty': 'Votre panier est vide',
      'cart.emptySubtitle': 'Découvrez nos systèmes d\'osmose inverse',
      'cart.viewProducts': 'Voir nos produits',
      'cart.summary': 'Récapitulatif',
      'cart.subtotal': 'Sous-total:',
      'cart.shipping': 'Livraison:',
      'cart.total': 'Total:',
      'cart.checkout': 'Procéder au Paiement 💳',
      'cart.continueShop': 'Continuer mes achats',
      
      // Contact & Consultation
      'consultation.title': 'Consultation Gratuite avec un Expert 📞',
      'consultation.subtitle': 'Obtenez un diagnostic complet et une solution adaptée à vos besoins professionnels',
      'consultation.success.title': 'Consultation Programmée!',
      'consultation.success.subtitle': 'Un expert vous contactera dans les prochaines heures pour programmer votre consultation gratuite.',
      'consultation.whatYouGet': 'Ce que vous obtiendrez :',
      'consultation.experts': '🏆 Nos Experts',
      'consultation.expertsDesc': 'Ingénieurs spécialisés avec +10 ans d\'expérience dans le traitement de l\'eau industriel. Certifications ISO et formations techniques continues.',
      
      // Form fields
      'form.name': 'Nom complet',
      'form.email': 'Email',
      'form.phone': 'Téléphone',
      'form.company': 'Entreprise',
      'form.message': 'Message',
      'form.send': 'Envoyer',
      'form.required': 'obligatoire',
      'form.success': 'Message Envoyé!',
      
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
  'EN': {
    translation: {
      // Navigation  
      'nav.home': 'Home',
      'nav.individuals': 'Individuals',
      'nav.professionals': 'Professionals', 
      'nav.installation': 'Installation',
      'nav.contact': 'Contact',
      'nav.cart': 'Cart',
      
      // Hero section
      'hero.title.b2c': 'Pure Water with Reverse Osmosis System',
      'hero.subtitle.b2c': 'Remove 99% of contaminants with our advanced technology',
      'hero.title.b2b': 'Professional Reverse Osmosis Solutions',
      'hero.subtitle.b2b': 'Equip your business with our industrial systems',
      'hero.special_price': 'Special European price',
      'hero.original_price': 'Normal price',
      'hero.cta': 'Order Now',
      'hero.guarantee': '✓ 2-year warranty ✓ Installation included ✓ UK support',
      
      // Contaminants section
      'contaminants.title': 'Contaminants removed',
      'contaminants.chlore': 'Chlorine',
      'contaminants.plomb': 'Lead',
      'contaminants.pesticides': 'Pesticides',
      'contaminants.nitrates': 'Nitrates',
      'contaminants.virus': 'Viruses & Bacteria',
      'contaminants.metaux': 'Heavy metals',
      
      // Products
      'products.title.b2c': 'Our Products 💧',
      'products.title.b2b': 'Professional Solutions 💼',
      'products.subtitle.b2c': 'Reverse osmosis systems for your home',
      'products.subtitle.b2b': 'Industrial systems for restaurants, offices and businesses',
      'products.addToCart.b2c': 'Add to Cart 🛒',
      'products.addToCart.b2b': 'Request Quote 📋',
      'products.outOfStock': 'Unavailable',
      'products.inStock': '✅ In stock',
      'products.outOfStockStatus': '❌ Out of stock',
      'products.stockLimited': '⚠️ Limited stock!',
      'products.professionalPrice': 'Professional Price excl. VAT',
      'products.professionalBadge': 'Pro Solution',
      
      // Customer type
      'customer.individuals': '👨‍👩‍👧‍👦 Individuals',
      'customer.professionals': '🏢 Professionals',
      
      // Cart
      'cart.title': 'Your Cart 🛒',
      'cart.empty': 'Your cart is empty',
      'cart.emptySubtitle': 'Discover our reverse osmosis systems',
      'cart.viewProducts': 'View our products',
      'cart.summary': 'Summary',
      'cart.subtotal': 'Subtotal:',
      'cart.shipping': 'Shipping:',
      'cart.total': 'Total:',
      'cart.checkout': 'Proceed to Payment 💳',
      'cart.continueShop': 'Continue shopping',
      
      // Contact & Consultation
      'consultation.title': 'Free Expert Consultation 📞',
      'consultation.subtitle': 'Get a complete diagnosis and solution adapted to your professional needs',
      'consultation.success.title': 'Consultation Scheduled!',
      'consultation.success.subtitle': 'An expert will contact you within the next few hours to schedule your free consultation.',
      'consultation.whatYouGet': 'What you will get:',
      'consultation.experts': '🏆 Our Experts',
      'consultation.expertsDesc': 'Specialized engineers with 10+ years experience in industrial water treatment. ISO certifications and continuous technical training.',
      
      // Form fields
      'form.name': 'Full name',
      'form.email': 'Email',
      'form.phone': 'Phone',
      'form.company': 'Company',
      'form.message': 'Message',
      'form.send': 'Send',
      'form.required': 'required',
      'form.success': 'Message Sent!',
      
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
      'hero.title.b2c': 'Agua Pura con Sistema de Ósmosis Inversa',
      'hero.subtitle.b2c': 'Elimina el 99% de los contaminantes con nuestra tecnología avanzada',
      'hero.title.b2b': 'Soluciones Profesionales de Ósmosis Inversa',
      'hero.subtitle.b2b': 'Equipe su empresa con nuestros sistemas industriales',
      'hero.special_price': 'Precio especial Europa',
      'hero.original_price': 'Precio normal',
      'hero.cta': 'Pedir Ahora',
      'hero.guarantee': '✓ Garantía 2 años ✓ Instalación incluida ✓ Soporte España',
      
      // Contaminants
      'contaminants.title': 'Contaminantes eliminados',
      'contaminants.chlore': 'Cloro',
      'contaminants.plomb': 'Plomo',
      'contaminants.pesticides': 'Pesticidas',
      'contaminants.nitrates': 'Nitratos',
      'contaminants.virus': 'Virus y Bacterias',
      'contaminants.metaux': 'Metales pesados',
      
      // Products
      'products.title.b2c': 'Nuestros Productos 💧',
      'products.title.b2b': 'Soluciones Profesionales 💼',
      'products.subtitle.b2c': 'Sistemas de ósmosis inversa para su hogar',
      'products.subtitle.b2b': 'Sistemas industriales para restaurantes, oficinas y comercios',
      'products.addToCart.b2c': 'Añadir al Carrito 🛒',
      'products.addToCart.b2b': 'Solicitar Presupuesto 📋',
      'products.outOfStock': 'No disponible',
      'products.inStock': '✅ En stock',
      'products.outOfStockStatus': '❌ Sin stock',
      'products.stockLimited': '⚠️ ¡Stock limitado!',
      'products.professionalPrice': 'Precio Profesional sin IVA',
      'products.professionalBadge': 'Solución Pro',
      
      'customer.individuals': '👨‍👩‍👧‍👦 Particulares',
      'customer.professionals': '🏢 Profesionales',
      
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
      'hero.title.b2c': 'Reines Wasser mit Umkehrosmose-System',
      'hero.subtitle.b2c': 'Beseitigen Sie 99% der Schadstoffe mit unserer fortschrittlichen Technologie',
      'hero.title.b2b': 'Professionelle Umkehrosmose-Lösungen',
      'hero.subtitle.b2b': 'Statten Sie Ihr Unternehmen mit unseren Industriesystemen aus',
      'hero.special_price': 'Europa Sonderpreis',
      'hero.original_price': 'Normalpreis',
      'hero.cta': 'Jetzt bestellen',
      'hero.guarantee': '✓ 2 Jahre Garantie ✓ Installation inklusive ✓ Deutschland Support',
      
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

// Fonctions utilitaires pour la conversion des codes de langue
export const convertDeepLToI18n = (deepLCode) => {
  return deepLToI18nMap[deepLCode] || 'FR';
};

export const convertI18nToDeepL = (i18nCode) => {
  return i18nToDeepLMap[i18nCode] || 'FR';
};

export const getAvailableLanguagesForDisplay = () => {
  return {
    'FR': { name: 'Français', native_name: 'Français', flag: '🇫🇷', deepl_code: 'FR' },
    'EN': { name: 'English', native_name: 'English', flag: '🇬🇧', deepl_code: 'EN-GB' },
    'ES': { name: 'Español', native_name: 'Español', flag: '🇪🇸', deepl_code: 'ES' },
    'IT': { name: 'Italiano', native_name: 'Italiano', flag: '🇮🇹', deepl_code: 'IT' },
    'DE': { name: 'Deutsch', native_name: 'Deutsch', flag: '🇩🇪', deepl_code: 'DE' },
    'NL': { name: 'Nederlands', native_name: 'Nederlands', flag: '🇳🇱', deepl_code: 'NL' },
    'PT': { name: 'Português', native_name: 'Português', flag: '🇵🇹', deepl_code: 'PT-PT' },
    'PL': { name: 'Polski', native_name: 'Polski', flag: '🇵🇱', deepl_code: 'PL' }
  };
};

export default i18n;