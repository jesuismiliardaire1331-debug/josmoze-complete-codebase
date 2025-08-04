import React, { useState, useEffect, createContext, useContext } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, useNavigate, useSearchParams } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// ========== CONTEXT ==========
const AppContext = createContext();

const AppProvider = ({ children }) => {
  const [userLocation, setUserLocation] = useState(null);
  const [cart, setCart] = useState([]);
  const [loading, setLoading] = useState(true);

  // Detect user location on app start
  useEffect(() => {
    const detectLocation = async () => {
      try {
        const response = await axios.get(`${API}/detect-location`);
        setUserLocation(response.data);
      } catch (error) {
        console.error('Location detection failed:', error);
        // Fallback
        setUserLocation({
          country_code: 'FR',
          country_name: 'France',
          currency: 'EUR',
          language: 'fr',
          shipping_cost: 19
        });
      } finally {
        setLoading(false);
      }
    };

    detectLocation();
  }, []);

  const addToCart = (product, quantity = 1) => {
    setCart(prevCart => {
      const existingItem = prevCart.find(item => item.id === product.id);
      if (existingItem) {
        return prevCart.map(item =>
          item.id === product.id
            ? { ...item, quantity: item.quantity + quantity }
            : item
        );
      }
      return [...prevCart, { ...product, quantity }];
    });
  };

  const removeFromCart = (productId) => {
    setCart(prevCart => prevCart.filter(item => item.id !== productId));
  };

  const updateCartQuantity = (productId, quantity) => {
    if (quantity <= 0) {
      removeFromCart(productId);
      return;
    }
    setCart(prevCart =>
      prevCart.map(item =>
        item.id === productId ? { ...item, quantity } : item
      )
    );
  };

  const clearCart = () => {
    setCart([]);
  };

  const getCartTotal = () => {
    const subtotal = cart.reduce((total, item) => total + (item.price * item.quantity), 0);
    const shipping = userLocation ? userLocation.shipping_cost : 19;
    return { subtotal, shipping, total: subtotal + shipping };
  };

  const formatPrice = (price) => {
    if (!userLocation) return `€${price}`;
    
    const currency = userLocation.currency;
    
    // Simple currency conversion (in real app, use live rates)
    let convertedPrice = price;
    if (currency === 'GBP') convertedPrice = price * 0.86;
    if (currency === 'CHF') convertedPrice = price * 1.08;
    
    const currencySymbols = { EUR: '€', GBP: '£', CHF: 'CHF' };
    return `${currencySymbols[currency] || '€'}${convertedPrice.toFixed(2)}`;
  };

  return (
    <AppContext.Provider value={{
      userLocation,
      cart,
      addToCart,
      removeFromCart,
      updateCartQuantity,
      clearCart,
      getCartTotal,
      formatPrice,
      loading
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
    return { success: false, message: 'Payment status check timed out. Please check your email for confirmation.' };
  }

  try {
    const response = await fetch(`${API}/checkout/status/${sessionId}`);
    if (!response.ok) {
      throw new Error('Failed to check payment status');
    }

    const data = await response.json();
    
    if (data.payment_status === 'paid') {
      return { success: true, message: 'Payment successful! Thank you for your purchase.', data };
    } else if (data.status === 'expired') {
      return { success: false, message: 'Payment session expired. Please try again.' };
    }

    // If payment is still pending, continue polling
    await new Promise(resolve => setTimeout(resolve, pollInterval));
    return await pollPaymentStatus(sessionId, attempts + 1);
    
  } catch (error) {
    console.error('Error checking payment status:', error);
    return { success: false, message: 'Error checking payment status. Please try again.' };
  }
};

// ========== COMPONENTS ==========

const Header = () => {
  const { cart, userLocation } = useApp();
  const navigate = useNavigate();
  const cartItemsCount = cart.reduce((total, item) => total + item.quantity, 0);

  const getGreeting = () => {
    if (!userLocation) return "Bienvenue";
    
    const greetings = {
      fr: "Bienvenue",
      es: "Bienvenido",
      de: "Willkommen",
      it: "Benvenuto",
      en: "Welcome"
    };
    
    return greetings[userLocation.language] || "Bienvenue";
  };

  return (
    <header className="bg-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center cursor-pointer" onClick={() => navigate('/')}>
            <h1 className="text-2xl font-bold text-blue-600">
              Josmose.com
            </h1>
            <span className="ml-3 text-sm text-gray-600">
              {getGreeting()} 🇫🇷
            </span>
          </div>
          
          <div className="flex items-center space-x-6">
            {userLocation && (
              <div className="text-sm text-gray-600">
                📍 {userLocation.country_name} | 💱 {userLocation.currency}
              </div>
            )}
            
            <button 
              onClick={() => navigate('/panier')}
              className="relative p-2 text-gray-600 hover:text-blue-600 transition-colors"
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
  const { userLocation, formatPrice } = useApp();
  const navigate = useNavigate();

  const getHeroText = () => {
    if (!userLocation) return {
      title: "Eau Pure avec Système d'Osmose Inverse",
      subtitle: "Éliminez 99% des contaminants avec notre technologie avancée"
    };

    const texts = {
      fr: {
        title: "Eau Pure avec Système d'Osmose Inverse",
        subtitle: "Éliminez 99% des contaminants avec notre technologie avancée"
      },
      es: {
        title: "Agua Pura con Sistema de Ósmosis Inversa",
        subtitle: "Elimina el 99% de los contaminantes con nuestra tecnología avanzada"
      },
      de: {
        title: "Reines Wasser mit Umkehrosmose-System",
        subtitle: "Beseitigen Sie 99% der Schadstoffe mit unserer fortschrittlichen Technologie"
      },
      it: {
        title: "Acqua Pura con Sistema a Osmosi Inversa",
        subtitle: "Elimina il 99% dei contaminanti con la nostra tecnologia avanzata"
      },
      en: {
        title: "Pure Water with Reverse Osmosis System",
        subtitle: "Remove 99% of contaminants with our advanced technology"
      }
    };

    return texts[userLocation.language] || texts.fr;
  };

  const heroText = getHeroText();

  return (
    <div className="relative bg-gradient-to-r from-blue-600 to-blue-800 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <h1 className="text-5xl font-bold mb-6 leading-tight">
              {heroText.title}
            </h1>
            <p className="text-xl mb-8 text-blue-100">
              {heroText.subtitle}
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 mb-8">
              <div className="bg-white bg-opacity-20 rounded-lg p-4 text-center">
                <div className="text-3xl font-bold">{formatPrice(499)}</div>
                <div className="text-sm line-through opacity-75">{formatPrice(599)}</div>
                <div className="text-sm">Prix spécial Europe</div>
              </div>
              
              <div className="bg-white bg-opacity-20 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold">99%</div>
                <div className="text-sm">Contaminants éliminés</div>
              </div>
            </div>
            
            <button 
              onClick={() => {
                document.querySelector('#products-section')?.scrollIntoView({ behavior: 'smooth' });
              }}
              className="bg-white text-blue-600 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-blue-50 transition-colors shadow-lg"
            >
              Découvrir nos Produits 🏠
            </button>
          </div>
          
          <div className="relative">
            <img
              src="https://images.unsplash.com/photo-1610312973684-e47446aa260b"
              alt="Système d'osmose inverse"
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
  const { addToCart, formatPrice } = useApp();

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await axios.get(`${API}/products`);
        setProducts(response.data);
      } catch (error) {
        console.error('Failed to fetch products:', error);
      }
    };

    fetchProducts();
  }, []);

  const handleAddToCart = (product) => {
    addToCart(product);
    // Show feedback (could use toast notification)
    alert(`${product.name} ajouté au panier!`);
  };

  return (
    <div id="products-section" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">
        Nos Produits 💧
      </h2>
      
      <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
        {products.map(product => (
          <div key={product.id} className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
            <img
              src={product.image}
              alt={product.name}
              className="w-full h-48 object-cover"
            />
            
            <div className="p-6">
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
                </div>
                
                {product.in_stock ? (
                  <span className="text-green-600 text-sm">✅ En stock</span>
                ) : (
                  <span className="text-red-600 text-sm">❌ Rupture</span>
                )}
              </div>
              
              {product.features && product.features.length > 0 && (
                <ul className="text-xs text-gray-600 mb-4 space-y-1">
                  {product.features.slice(0, 3).map((feature, idx) => (
                    <li key={idx}>• {feature}</li>
                  ))}
                </ul>
              )}
              
              <button
                onClick={() => handleAddToCart(product)}
                disabled={!product.in_stock}
                className={`w-full py-3 px-4 rounded-lg font-semibold transition-colors ${
                  product.in_stock
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                {product.in_stock ? 'Ajouter au Panier 🛒' : 'Indisponible'}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const Features = () => {
  return (
    <div className="bg-gray-50 py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
          Pourquoi Choisir Nos Systèmes? 🌟
        </h2>
        
        <div className="grid md:grid-cols-3 gap-8">
          <div className="bg-white p-8 rounded-lg shadow-md text-center">
            <div className="text-4xl mb-4">🦠</div>
            <h3 className="text-xl font-semibold mb-4">Élimination Totale</h3>
            <p className="text-gray-600">
              Supprime 99% des virus, bactéries, chlore et particules organiques grâce à notre système 4 étapes.
            </p>
          </div>
          
          <div className="bg-white p-8 rounded-lg shadow-md text-center">
            <div className="text-4xl mb-4">⚡</div>
            <h3 className="text-xl font-semibold mb-4">Installation Simple</h3>
            <p className="text-gray-600">
              Aucun électricien nécessaire! Installation rapide sans électricité, utilise uniquement la pression du réseau.
            </p>
          </div>
          
          <div className="bg-white p-8 rounded-lg shadow-md text-center">
            <div className="text-4xl mb-4">💰</div>
            <h3 className="text-xl font-semibold mb-4">Économies Garanties</h3>
            <p className="text-gray-600">
              Économisez 500-700€ par an en supprimant l'achat de bouteilles d'eau. Rentabilité en moins d'un an.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

const CartSummary = () => {
  const { cart, getCartTotal, formatPrice, removeFromCart, updateCartQuantity, clearCart } = useApp();
  const navigate = useNavigate();
  
  if (cart.length === 0) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center">
        <div className="text-4xl mb-4">🛒</div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Votre panier est vide</h2>
        <p className="text-gray-600 mb-6">Découvrez nos systèmes d'osmose inverse</p>
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

  const handleCheckout = () => {
    navigate('/checkout');
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-16">
      <h2 className="text-3xl font-bold text-gray-900 mb-8">Votre Panier 🛒</h2>
      
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
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Récapitulatif</h3>
          
          <div className="space-y-2 mb-4">
            <div className="flex justify-between">
              <span>Sous-total:</span>
              <span>{formatPrice(subtotal)}</span>
            </div>
            <div className="flex justify-between">
              <span>Livraison:</span>
              <span>{formatPrice(shipping)}</span>
            </div>
            <hr />
            <div className="flex justify-between font-semibold text-lg">
              <span>Total:</span>
              <span>{formatPrice(total)}</span>
            </div>
          </div>
          
          <button 
            onClick={handleCheckout}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors mb-2"
          >
            Procéder au Paiement 💳
          </button>
          
          <button
            onClick={clearCart}
            className="w-full bg-gray-300 text-gray-700 py-2 rounded-lg font-medium hover:bg-gray-400 transition-colors text-sm"
          >
            Vider le panier
          </button>
        </div>
      </div>
    </div>
  );
};

const CheckoutForm = () => {
  const { cart, getCartTotal, formatPrice, clearCart } = useApp();
  const [customerInfo, setCustomerInfo] = useState({
    name: '',
    email: '',
    phone: ''
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

    if (!customerInfo.name || !customerInfo.email) {
      setError('Veuillez remplir tous les champs obligatoires');
      setLoading(false);
      return;
    }

    try {
      // Prepare cart items for backend
      const cartItems = cart.map(item => ({
        product_id: item.id,
        quantity: item.quantity,
        price: item.price
      }));

      // Create checkout session
      const response = await axios.post(`${API}/checkout/session`, {
        cart_items: cartItems,
        customer_info: customerInfo,
        origin_url: window.location.origin
      });

      if (response.data.url) {
        // Redirect to Stripe Checkout
        window.location.href = response.data.url;
      } else {
        throw new Error('No checkout URL received');
      }

    } catch (error) {
      console.error('Checkout error:', error);
      setError(error.response?.data?.detail || 'Erreur lors du paiement. Veuillez réessayer.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-16">
      <h2 className="text-3xl font-bold text-gray-900 mb-8">Finaliser la Commande 💳</h2>
      
      <div className="grid lg:grid-cols-2 gap-8">
        <div>
          <h3 className="text-xl font-semibold mb-4">Informations de Contact</h3>
          
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nom complet *
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
                Email *
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
            
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
            >
              {loading ? 'Redirection vers le paiement...' : 'Payer maintenant 💳'}
            </button>
          </form>
          
          <div className="mt-4 text-xs text-gray-500">
            <p>🔒 Paiement sécurisé avec Stripe</p>
            <p>💳 Cartes acceptées, Apple Pay, Google Pay</p>
            <p>🏦 Paiement en plusieurs fois disponible</p>
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
            <div className="flex justify-between font-semibold text-lg">
              <span>Total:</span>
              <span>{formatPrice(total)}</span>
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

const ContactForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    message: '',
    request_type: 'quote'
  });
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/contact`, formData);
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
        <p className="text-gray-600">Nous vous répondrons dans les plus brefs délais.</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-16">
      <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">
        Demande de Devis 📋
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
        
        <div className="mb-6">
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
            <option value="support">Support technique</option>
            <option value="general">Information générale</option>
          </select>
        </div>
        
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
            placeholder="Décrivez votre besoin en détail..."
          />
        </div>
        
        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
        >
          Envoyer ma Demande 📤
        </button>
      </form>
    </div>
  );
};

const Footer = () => {
  const { userLocation } = useApp();

  return (
    <footer className="bg-gray-900 text-white py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-xl font-bold mb-4">Josmose.com</h3>
            <p className="text-gray-300 text-sm">
              Spécialiste européen des systèmes d'osmose inverse. 
              Eau pure et saine pour toute votre famille.
            </p>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Produits</h4>
            <ul className="text-gray-300 text-sm space-y-2">
              <li>Systèmes d'osmose</li>
              <li>Filtres de rechange</li>
              <li>Extensions garantie</li>
              <li>Service après-vente</li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Support</h4>
            <ul className="text-gray-300 text-sm space-y-2">
              <li>Installation</li>
              <li>Maintenance</li>
              <li>Garantie</li>
              <li>Contact</li>
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
          </div>
        </div>
        
        <hr className="border-gray-700 my-8" />
        
        <div className="text-center text-gray-300 text-sm">
          <p>&copy; 2024 Josmose.com - Eau pure pour l'Europe 💧</p>
        </div>
      </div>
    </footer>
  );
};

// ========== MAIN APP ==========

const Home = () => {
  return (
    <div>
      <Hero />
      <Features />
      <ProductGrid />
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

function App() {
  return (
    <AppProvider>
      <div className="App min-h-screen bg-gray-50">
        <BrowserRouter>
          <Header />
          <main>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/panier" element={<Cart />} />
              <Route path="/checkout" element={<Checkout />} />
              <Route path="/contact" element={<Contact />} />
              <Route path="/payment-success" element={<PaymentSuccess />} />
              <Route path="/payment-cancelled" element={<PaymentCancelled />} />
            </Routes>
          </main>
          <Footer />
        </BrowserRouter>
      </div>
    </AppProvider>
  );
}

export default App;