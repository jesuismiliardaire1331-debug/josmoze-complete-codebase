import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Link, useNavigate } from "react-router-dom";
import axios from "axios";

// Import context
import { AppProvider, useApp } from './context/AppContext';
import { AuthProvider as UserAuthProvider } from './UserAuth';

// Import core components
import ChatBotV2 from "./ChatBot_V2";
import UserAuth from "./UserAuth";
import EspaceClient from "./EspaceClient";
import BlogPage from "./BlogPage";
import BlogArticle from "./BlogArticle";
import AdminLogin from "./AdminLogin";
import AdminDashboard from "./AdminDashboard";
import CRMLogin from "./CRMLogin";
import CRM from "./CRM";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

// Professional Header Component
const Header = () => {
  const navigate = useNavigate();
  const { cart } = useApp();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const totalItems = cart.reduce((total, item) => total + item.quantity, 0);

  return (
    <header className="bg-white shadow-lg sticky top-0 z-40">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center py-2 border-b border-gray-200">
          <div className="text-sm text-gray-600">Espace Professionnel</div>
          <div className="text-sm text-gray-600">🇫🇷 Français</div>
        </div>
        
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center cursor-pointer" onClick={() => navigate('/')}>
            <div className="text-2xl font-bold text-blue-600">🌊 JOSMOZE</div>
          </div>

          <nav className="hidden md:flex space-x-8">
            <button onClick={() => navigate('/')} className="text-gray-700 hover:text-blue-600 font-medium transition-colors">Accueil</button>
            <button onClick={() => navigate('/produits')} className="text-gray-700 hover:text-blue-600 font-medium transition-colors">Produits</button>
            <button onClick={() => navigate('/comment-ca-marche')} className="text-gray-700 hover:text-blue-600 font-medium transition-colors">Comment ça marche</button>
            <button onClick={() => navigate('/blog')} className="text-gray-700 hover:text-blue-600 font-medium transition-colors">Blog</button>
            <button onClick={() => navigate('/contact')} className="text-gray-700 hover:text-blue-600 font-medium transition-colors">Contact</button>
          </nav>

          <div className="flex items-center space-x-4">
            <button onClick={() => navigate('/panier')} className="relative p-2 text-gray-700 hover:text-blue-600 transition-colors">
              🛒
              {totalItems > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                  {totalItems}
                </span>
              )}
            </button>
            <button className="md:hidden p-2 text-gray-700 hover:text-blue-600" onClick={() => setIsMenuOpen(!isMenuOpen)}>☰</button>
          </div>
        </div>

        {isMenuOpen && (
          <div className="md:hidden border-t border-gray-200 py-4">
            <div className="flex flex-col space-y-3">
              <button onClick={() => {navigate('/'); setIsMenuOpen(false);}} className="text-left text-gray-700 hover:text-blue-600 font-medium py-2">Accueil</button>
              <button onClick={() => {navigate('/produits'); setIsMenuOpen(false);}} className="text-left text-gray-700 hover:text-blue-600 font-medium py-2">Produits</button>
              <button onClick={() => {navigate('/blog'); setIsMenuOpen(false);}} className="text-left text-gray-700 hover:text-blue-600 font-medium py-2">Blog</button>
              <button onClick={() => {navigate('/contact'); setIsMenuOpen(false);}} className="text-left text-gray-700 hover:text-blue-600 font-medium py-2">Contact</button>
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

// Professional Home Component
const Home = () => {
  const { openQuestionnaire } = useApp();
  const navigate = useNavigate();
  
  return (
    <div className="min-h-screen">
      <section className="bg-gradient-to-br from-blue-600 to-blue-800 text-white">
        <div className="container mx-auto px-4 py-20">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-5xl font-bold mb-6">L'eau la plus pure pour votre famille</h1>
              <p className="text-xl mb-8 opacity-90">Découvrez nos osmoseurs de dernière génération pour une eau parfaitement purifiée</p>
              <div className="flex flex-col sm:flex-row gap-4">
                <button onClick={() => navigate('/produits')} className="bg-yellow-500 hover:bg-yellow-600 text-black font-bold py-4 px-8 rounded-lg transition-colors">
                  Voir nos produits
                </button>
                <button onClick={() => navigate('/comment-ca-marche')} className="border-2 border-white hover:bg-white hover:text-blue-600 font-bold py-4 px-8 rounded-lg transition-colors">
                  Comment ça marche
                </button>
              </div>
            </div>
            <div className="text-center">
              <div className="text-8xl mb-4">🌊</div>
              <p className="text-lg opacity-75">Eau pure garantie à 99,9%</p>
            </div>
          </div>
        </div>
      </section>

      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl font-bold text-center mb-16 text-gray-800">Pourquoi choisir Josmoze ?</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center p-6">
              <div className="text-5xl mb-4">💧</div>
              <h3 className="text-xl font-bold mb-3 text-gray-800">Pureté maximale</h3>
              <p className="text-gray-600">Élimination de 99,9% des contaminants, métaux lourds et produits chimiques</p>
            </div>
            <div className="text-center p-6">
              <div className="text-5xl mb-4">⚡</div>
              <h3 className="text-xl font-bold mb-3 text-gray-800">Installation rapide</h3>
              <p className="text-gray-600">Installation professionnelle en moins de 2 heures par nos experts</p>
            </div>
            <div className="text-center p-6">
              <div className="text-5xl mb-4">💰</div>
              <h3 className="text-xl font-bold mb-3 text-gray-800">Économies garanties</h3>
              <p className="text-gray-600">Jusqu'à 80% d'économies par rapport à l'eau en bouteille</p>
            </div>
          </div>
        </div>
      </section>

      <section className="py-20 bg-blue-600 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold mb-6">Prêt à découvrir l'eau la plus pure ?</h2>
          <p className="text-xl mb-8 opacity-90">Obtenez votre devis personnalisé en 2 minutes</p>
          <button onClick={() => navigate('/contact')} className="bg-yellow-500 hover:bg-yellow-600 text-black font-bold py-4 px-8 rounded-lg text-lg transition-colors">
            Demander un devis
          </button>
        </div>
      </section>
    </div>
  );
};

// Simplified product page
const ProductsPage = () => {
  const { addToCart } = useApp();
  
  const products = [
    {
      id: 1,
      name: "Osmoseur Domestique Pro",
      price: 299,
      image: "https://images.unsplash.com/photo-1563453392212-326f5e854473?w=400",
      description: "Système d'osmose inverse 5 étapes pour usage domestique"
    },
    {
      id: 2,
      name: "Osmoseur Premium Plus",
      price: 499,
      image: "https://images.unsplash.com/photo-1582719471384-894fbb16e074?w=400",
      description: "Système avancé 7 étapes avec reminéralisation"
    }
  ];

  return (
    <div className="min-h-screen py-12">
      <div className="container mx-auto px-4">
        <h1 className="text-4xl font-bold text-center mb-12 text-gray-800">Nos Osmoseurs</h1>
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {products.map(product => (
            <div key={product.id} className="bg-white rounded-lg shadow-lg overflow-hidden">
              <img src={product.image} alt={product.name} className="w-full h-48 object-cover"/>
              <div className="p-6">
                <h3 className="text-xl font-bold mb-2">{product.name}</h3>
                <p className="text-gray-600 mb-4">{product.description}</p>
                <div className="flex justify-between items-center">
                  <span className="text-2xl font-bold text-blue-600">{product.price}€</span>
                  <button 
                    onClick={() => addToCart(product)}
                    className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-lg transition-colors"
                  >
                    Ajouter au panier
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Cart component
const Cart = () => {
  const { cart, removeFromCart, updateQuantity, getCartTotal, formatPrice } = useApp();
  const navigate = useNavigate();

  if (cart.length === 0) {
    return (
      <div className="min-h-screen py-12">
        <div className="container mx-auto px-4">
          <div className="max-w-2xl mx-auto text-center">
            <div className="text-6xl mb-6">🛒</div>
            <h1 className="text-3xl font-bold text-gray-800 mb-4">Votre panier est vide</h1>
            <p className="text-gray-600 mb-8">Découvrez nos osmoseurs et trouvez celui qui vous convient</p>
            <button onClick={() => navigate('/produits')} className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg transition-colors">
              Découvrir nos produits
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-12">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-800 mb-8">Votre panier</h1>
          <div className="grid lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg shadow-lg p-6">
                {cart.map((item) => (
                  <div key={item.id} className="flex items-center py-4 border-b border-gray-200 last:border-b-0">
                    <img src={item.image} alt={item.name} className="w-20 h-20 object-cover rounded-lg mr-4"/>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-800">{item.name}</h3>
                      <p className="text-blue-600 font-bold">{formatPrice(item.price)}</p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button onClick={() => updateQuantity(item.id, item.quantity - 1)} className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center hover:bg-gray-300">-</button>
                      <span className="w-8 text-center">{item.quantity}</span>
                      <button onClick={() => updateQuantity(item.id, item.quantity + 1)} className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center hover:bg-gray-300">+</button>
                      <button onClick={() => removeFromCart(item.id)} className="ml-4 text-red-500 hover:text-red-700">🗑️</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow-lg p-6 sticky top-4">
                <h2 className="text-xl font-bold text-gray-800 mb-4">Résumé de commande</h2>
                <div className="space-y-3 mb-6">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Sous-total</span>
                    <span className="font-semibold">{formatPrice(getCartTotal())}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Livraison</span>
                    <span className="font-semibold text-green-600">Gratuite</span>
                  </div>
                  <div className="border-t pt-3">
                    <div className="flex justify-between text-lg font-bold">
                      <span>Total</span>
                      <span className="text-blue-600">{formatPrice(getCartTotal())}</span>
                    </div>
                  </div>
                </div>
                <button onClick={() => navigate('/checkout')} className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition-colors">
                  Passer commande
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Checkout component with promo code
const Checkout = () => {
  const { cart, getCartTotal, formatPrice, clearCart } = useApp();
  const [promoCode, setPromoCode] = useState('');
  const [discount, setDiscount] = useState(0);
  const [promoApplied, setPromoApplied] = useState(false);
  const [orderData, setOrderData] = useState({
    email: '',
    firstName: '',
    lastName: '',
    phone: '',
    address: '',
    city: '',
    postalCode: ''
  });

  const applyPromoCode = () => {
    if (promoCode === 'TEST15') {
      setDiscount(0.15);
      setPromoApplied(true);
    }
  };

  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    alert('Commande simulée - Merci pour votre achat !');
    clearCart();
    navigate('/');
  };

  const finalTotal = getCartTotal() * (1 - discount);

  return (
    <div className="min-h-screen py-12">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-800 mb-8">Finaliser ma commande</h1>
          <form onSubmit={handleSubmit} className="grid lg:grid-cols-2 gap-8">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-bold mb-6">Informations de livraison</h2>
              <div className="grid md:grid-cols-2 gap-4 mb-4">
                <input type="text" placeholder="Prénom" value={orderData.firstName} onChange={(e) => setOrderData({...orderData, firstName: e.target.value})} required className="w-full px-3 py-2 border border-gray-300 rounded-lg"/>
                <input type="text" placeholder="Nom" value={orderData.lastName} onChange={(e) => setOrderData({...orderData, lastName: e.target.value})} required className="w-full px-3 py-2 border border-gray-300 rounded-lg"/>
              </div>
              <input type="email" placeholder="Email" value={orderData.email} onChange={(e) => setOrderData({...orderData, email: e.target.value})} required className="w-full px-3 py-2 border border-gray-300 rounded-lg mb-4"/>
              <input type="tel" placeholder="Téléphone" value={orderData.phone} onChange={(e) => setOrderData({...orderData, phone: e.target.value})} required className="w-full px-3 py-2 border border-gray-300 rounded-lg mb-4"/>
              <input type="text" placeholder="Adresse" value={orderData.address} onChange={(e) => setOrderData({...orderData, address: e.target.value})} required className="w-full px-3 py-2 border border-gray-300 rounded-lg mb-4"/>
              <div className="grid md:grid-cols-2 gap-4">
                <input type="text" placeholder="Ville" value={orderData.city} onChange={(e) => setOrderData({...orderData, city: e.target.value})} required className="w-full px-3 py-2 border border-gray-300 rounded-lg"/>
                <input type="text" placeholder="Code postal" value={orderData.postalCode} onChange={(e) => setOrderData({...orderData, postalCode: e.target.value})} required className="w-full px-3 py-2 border border-gray-300 rounded-lg"/>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-bold mb-6">Résumé de commande</h2>
              {cart.map((item) => (
                <div key={item.id} className="flex justify-between items-center py-2 border-b border-gray-100">
                  <div>
                    <span className="font-medium">{item.name}</span>
                    <span className="text-gray-500 ml-2">x{item.quantity}</span>
                  </div>
                  <span className="font-semibold">{formatPrice(item.price * item.quantity)}</span>
                </div>
              ))}
              
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <label className="block text-sm font-medium mb-2">Code promo</label>
                <div className="flex gap-2">
                  <input type="text" value={promoCode} onChange={(e) => setPromoCode(e.target.value)} placeholder="TEST15" className="flex-1 px-3 py-2 border border-gray-300 rounded-lg"/>
                  <button type="button" onClick={applyPromoCode} className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg">Appliquer</button>
                </div>
                {promoApplied && <p className="text-green-600 text-sm mt-2">Code TEST15 appliqué - 15% de réduction</p>}
              </div>
              
              <div className="border-t pt-4 mt-4">
                <div className="flex justify-between mb-2">
                  <span>Sous-total</span>
                  <span>{formatPrice(getCartTotal())}</span>
                </div>
                {discount > 0 && (
                  <div className="flex justify-between mb-2 text-green-600">
                    <span>Réduction ({Math.round(discount * 100)}%)</span>
                    <span>-{formatPrice(getCartTotal() * discount)}</span>
                  </div>
                )}
                <div className="flex justify-between text-lg font-bold">
                  <span>Total</span>
                  <span className="text-blue-600">{formatPrice(finalTotal)}</span>
                </div>
              </div>
              
              <button type="submit" className="w-full mt-6 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition-colors">
                Confirmer la commande
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

// Contact page
const Contact = () => {
  return (
    <div className="min-h-screen py-12">
      <div className="container mx-auto px-4">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-4xl font-bold text-center mb-8 text-gray-800">Contactez-nous</h1>
          <div className="bg-white rounded-lg shadow-lg p-8">
            <div className="space-y-6">
              <div className="flex items-center">
                <div className="text-2xl mr-4">📍</div>
                <div>
                  <p className="font-medium text-gray-800">Adresse</p>
                  <p className="text-gray-600">123 Avenue de l'Eau Pure<br/>75001 Paris, France</p>
                </div>
              </div>
              <div className="flex items-center">
                <div className="text-2xl mr-4">📞</div>
                <div>
                  <p className="font-medium text-gray-800">Téléphone</p>
                  <p className="text-gray-600">+33 1 23 45 67 89</p>
                </div>
              </div>
              <div className="flex items-center">
                <div className="text-2xl mr-4">📧</div>
                <div>
                  <p className="font-medium text-gray-800">Email</p>
                  <p className="text-gray-600">contact@josmoze.com</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

function App() {
  return (
    <AppProvider>
      <UserAuthProvider>
        <BrowserRouter>
          <div className="App min-h-screen flex flex-col">
            <Header />
            <main className="flex-1">
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/produits" element={<ProductsPage />} />
                <Route path="/panier" element={<Cart />} />
                <Route path="/checkout" element={<Checkout />} />
                <Route path="/contact" element={<Contact />} />
                <Route path="/login" element={<UserAuth />} />
                <Route path="/register" element={<UserAuth />} />
                <Route path="/espace-client" element={<EspaceClient />} />
                <Route path="/blog" element={<BlogPage />} />
                <Route path="/blog/:slug" element={<BlogArticle />} />
                <Route path="/admin/login" element={<AdminLogin />} />
                <Route path="/admin/dashboard" element={<AdminDashboard />} />
                <Route path="/crm-login" element={<CRMLogin />} />
                <Route path="/crm" element={<CRM />} />
              </Routes>
            </main>
            <footer className="bg-blue-900 text-white py-16">
              <div className="container mx-auto px-4 py-8">
                <div className="grid md:grid-cols-4 gap-8">
                  <div>
                    <h3 className="text-xl font-bold mb-4">🌊 JOSMOZE</h3>
                    <p className="text-blue-100">L'expert en osmose inverse pour une eau parfaitement pure</p>
                  </div>
                  <div>
                    <h4 className="font-semibold mb-3">Nos produits</h4>
                    <ul className="space-y-2 text-blue-100">
                      <li><Link to="/produits" className="hover:text-white">Osmoseurs</Link></li>
                      <li><Link to="/contact" className="hover:text-white">Installation</Link></li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-semibold mb-3">Support</h4>
                    <ul className="space-y-2 text-blue-100">
                      <li><Link to="/contact" className="hover:text-white">Contact</Link></li>
                      <li><Link to="/blog" className="hover:text-white">Blog</Link></li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-semibold mb-3">Contact</h4>
                    <div className="text-blue-100 space-y-2">
                      <p>📞 +33 1 23 45 67 89</p>
                      <p>📧 contact@josmoze.com</p>
                      <p>📍 Paris, France</p>
                    </div>
                  </div>
                </div>
                <div className="border-t border-blue-800 mt-8 pt-8 text-center text-blue-100">
                  <p>&copy; 2024 Josmoze. Tous droits réservés. - Osmoseurs professionnels</p>
                </div>
              </div>
            </footer>
            <ChatBotV2 />
          </div>
        </BrowserRouter>
      </UserAuthProvider>
    </AppProvider>
  );
}

export default App;