import React, { useState, useEffect } from 'react';
import { useAuth } from './UserAuth';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const EspaceClient = () => {
  const { user, logout, updateProfile, getToken } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [orders, setOrders] = useState([]);
  const [referralStats, setReferralStats] = useState({ referral_code: null, stats: {} });

  // Profile data
  const [profileData, setProfileData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    phone: user?.phone || '',
    company: user?.company || '',
    address: user?.address || {
      street: '',
      city: '',
      postal_code: '',
      country: 'France'
    }
  });

  useEffect(() => {
    if (activeTab === 'orders') {
      loadOrders();
    } else if (activeTab === 'referral') {
      loadReferralStats();
    }
  }, [activeTab]);

  const loadOrders = async () => {
    try {
      setLoading(true);
      const token = getToken();
      const response = await axios.get(`${API_BASE}/api/orders/history`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        setOrders(response.data.orders);
      }
    } catch (error) {
      console.error('Error loading orders:', error);
      setMessage('❌ Erreur lors du chargement des commandes');
    } finally {
      setLoading(false);
    }
  };

  const loadReferralStats = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/api/referrals/stats/${user.email}`);
      if (response.data) {
        setReferralStats(response.data);

        // Générer code parrainage si pas encore créé
        if (!response.data.referral_code) {
          const generateResponse = await axios.post(`${API_BASE}/api/referrals/generate`, {
            user_email: user.email
          });
          
          if (generateResponse.data.success) {
            setReferralStats({
              referral_code: generateResponse.data.referral_code,
              stats: {}
            });
          }
        }
      }
    } catch (error) {
      console.error('Error loading referral stats:', error);
      setMessage('❌ Erreur lors du chargement du parrainage');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    const result = await updateProfile(profileData);
    
    if (result.success) {
      setMessage('✅ Profil mis à jour avec succès !');
    } else {
      setMessage(`❌ ${result.error}`);
    }
    
    setLoading(false);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'confirmed': return 'bg-blue-100 text-blue-800';
      case 'shipped': return 'bg-purple-100 text-purple-800';
      case 'delivered': return 'bg-green-100 text-green-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'pending': return 'En attente';
      case 'confirmed': return 'Confirmée';
      case 'shipped': return 'Expédiée';
      case 'delivered': return 'Livrée';
      case 'cancelled': return 'Annulée';
      default: return status;
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR'
    }).format(price);
  };

  const copyReferralCode = () => {
    if (referralStats.referral_code) {
      navigator.clipboard.writeText(referralStats.referral_code);
      setMessage('✅ Code de parrainage copié !');
      setTimeout(() => setMessage(''), 3000);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">
                👋 Bonjour {user?.first_name} !
              </h1>
              <p className="text-gray-600">Bienvenue dans votre espace client Josmoze</p>
            </div>
            <button
              onClick={logout}
              className="bg-red-100 text-red-700 px-4 py-2 rounded-lg hover:bg-red-200 transition-colors"
            >
              Déconnexion
            </button>
          </div>
        </div>

        {/* Messages */}
        {message && (
          <div className={`p-4 rounded-lg mb-6 ${
            message.includes('✅') ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            {message}
            <button 
              onClick={() => setMessage('')}
              className="float-right text-lg font-bold ml-4"
            >
              ×
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Navigation */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm p-4">
              <nav className="space-y-2">
                <button
                  onClick={() => setActiveTab('profile')}
                  className={`w-full text-left p-3 rounded-lg transition-colors ${
                    activeTab === 'profile'
                      ? 'bg-blue-100 text-blue-700 font-medium'
                      : 'hover:bg-gray-100'
                  }`}
                >
                  👤 Mon Profil
                </button>
                <button
                  onClick={() => setActiveTab('orders')}
                  className={`w-full text-left p-3 rounded-lg transition-colors ${
                    activeTab === 'orders'
                      ? 'bg-blue-100 text-blue-700 font-medium'
                      : 'hover:bg-gray-100'
                  }`}
                >
                  📦 Mes Commandes
                </button>
                <button
                  onClick={() => setActiveTab('referral')}
                  className={`w-full text-left p-3 rounded-lg transition-colors ${
                    activeTab === 'referral'
                      ? 'bg-blue-100 text-blue-700 font-medium'
                      : 'hover:bg-gray-100'
                  }`}
                >
                  👥 Parrainage
                </button>
              </nav>
            </div>
          </div>

          {/* Contenu principal */}
          <div className="lg:col-span-3">
            {/* Profil */}
            {activeTab === 'profile' && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h2 className="text-xl font-semibold mb-6">👤 Mon Profil</h2>
                
                <form onSubmit={handleUpdateProfile}>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Prénom *
                      </label>
                      <input
                        type="text"
                        value={profileData.first_name}
                        onChange={(e) => setProfileData({...profileData, first_name: e.target.value})}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Nom *
                      </label>
                      <input
                        type="text"
                        value={profileData.last_name}
                        onChange={(e) => setProfileData({...profileData, last_name: e.target.value})}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Email
                      </label>
                      <input
                        type="email"
                        value={user?.email || ''}
                        className="w-full p-3 border border-gray-300 rounded-lg bg-gray-100"
                        disabled
                      />
                      <p className="text-xs text-gray-500 mt-1">L'email ne peut pas être modifié</p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Téléphone
                      </label>
                      <input
                        type="tel"
                        value={profileData.phone}
                        onChange={(e) => setProfileData({...profileData, phone: e.target.value})}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        placeholder="+33 1 23 45 67 89"
                      />
                    </div>

                    {user?.customer_type === 'B2B' && (
                      <div className="md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Entreprise
                        </label>
                        <input
                          type="text"
                          value={profileData.company}
                          onChange={(e) => setProfileData({...profileData, company: e.target.value})}
                          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    )}

                    <div className="md:col-span-2">
                      <h3 className="text-lg font-medium text-gray-800 mb-4">📍 Adresse</h3>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="md:col-span-2">
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Adresse
                          </label>
                          <input
                            type="text"
                            value={profileData.address.street}
                            onChange={(e) => setProfileData({
                              ...profileData, 
                              address: {...profileData.address, street: e.target.value}
                            })}
                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            placeholder="123 rue de la Paix"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Ville
                          </label>
                          <input
                            type="text"
                            value={profileData.address.city}
                            onChange={(e) => setProfileData({
                              ...profileData, 
                              address: {...profileData.address, city: e.target.value}
                            })}
                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            placeholder="Paris"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Code postal
                          </label>
                          <input
                            type="text"
                            value={profileData.address.postal_code}
                            onChange={(e) => setProfileData({
                              ...profileData, 
                              address: {...profileData.address, postal_code: e.target.value}
                            })}
                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            placeholder="75001"
                          />
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="mt-6">
                    <button
                      type="submit"
                      disabled={loading}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors disabled:opacity-50"
                    >
                      {loading ? 'Mise à jour...' : 'Mettre à jour'}
                    </button>
                  </div>
                </form>
              </div>
            )}

            {/* Commandes */}
            {activeTab === 'orders' && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h2 className="text-xl font-semibold mb-6">📦 Mes Commandes</h2>
                
                {loading ? (
                  <div className="text-center py-8">
                    <div className="text-gray-500">Chargement des commandes...</div>
                  </div>
                ) : orders.length === 0 ? (
                  <div className="text-center py-8">
                    <div className="text-gray-500 mb-4">Aucune commande trouvée</div>
                    <button
                      onClick={() => window.location.href = '/'}
                      className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                    >
                      Découvrir nos produits
                    </button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {orders.map((order) => (
                      <div key={order.id} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex justify-between items-start mb-3">
                          <div>
                            <h3 className="font-medium text-gray-800">
                              Commande #{order.order_number}
                            </h3>
                            <p className="text-sm text-gray-500">
                              {new Date(order.created_at).toLocaleDateString('fr-FR')}
                            </p>
                          </div>
                          <div className="text-right">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(order.status)}`}>
                              {getStatusLabel(order.status)}
                            </span>
                            <div className="text-lg font-semibold text-gray-800 mt-1">
                              {formatPrice(order.total)}
                            </div>
                          </div>
                        </div>
                        
                        <div className="space-y-2">
                          {order.items.map((item, index) => (
                            <div key={index} className="flex justify-between text-sm">
                              <span>{item.name} × {item.quantity}</span>
                              <span>{formatPrice(item.price * item.quantity)}</span>
                            </div>
                          ))}
                        </div>
                        
                        {(order.discount_amount > 0 || order.promotion_code) && (
                          <div className="mt-2 pt-2 border-t border-gray-100">
                            {order.promotion_code && (
                              <div className="text-sm text-green-600">
                                Code promo: {order.promotion_code}
                              </div>
                            )}
                            {order.discount_amount > 0 && (
                              <div className="text-sm text-green-600">
                                Réduction: -{formatPrice(order.discount_amount)}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Parrainage */}
            {activeTab === 'referral' && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h2 className="text-xl font-semibold mb-6">👥 Programme de Parrainage</h2>
                
                <div className="bg-gradient-to-r from-green-50 to-blue-50 p-6 rounded-lg mb-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">
                    🎁 Comment ça marche ?
                  </h3>
                  <div className="text-sm text-gray-700 space-y-1">
                    <p>• Partagez votre code de parrainage avec vos proches</p>
                    <p>• Ils bénéficient de <strong>15% de réduction</strong> sur leur première commande</p>
                    <p>• Vous recevez un <strong>bon de 20€</strong> après validation de leur commande</p>
                  </div>
                </div>

                {referralStats.referral_code ? (
                  <>
                    <div className="bg-gray-50 p-6 rounded-lg mb-6">
                      <h3 className="text-lg font-semibold text-gray-800 mb-4">
                        🔗 Votre code de parrainage
                      </h3>
                      <div className="flex items-center space-x-3">
                        <div className="bg-white p-3 rounded-lg border-2 border-dashed border-blue-300 font-mono text-lg font-bold text-blue-600 flex-1">
                          {referralStats.referral_code}
                        </div>
                        <button
                          onClick={copyReferralCode}
                          className="bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 font-medium"
                        >
                          Copier
                        </button>
                      </div>
                      <p className="text-sm text-gray-600 mt-2">
                        Partagez ce code avec vos amis et famille
                      </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <div className="text-2xl font-bold text-blue-600">
                          {referralStats.stats.total_referrals || 0}
                        </div>
                        <div className="text-sm text-blue-700">Parrainages réussis</div>
                      </div>
                      
                      <div className="bg-orange-50 p-4 rounded-lg">
                        <div className="text-2xl font-bold text-orange-600">
                          {referralStats.stats.pending_referrals || 0}
                        </div>
                        <div className="text-sm text-orange-700">En attente</div>
                      </div>
                      
                      <div className="bg-green-50 p-4 rounded-lg">
                        <div className="text-2xl font-bold text-green-600">
                          {formatPrice(referralStats.stats.total_earnings || 0)}
                        </div>
                        <div className="text-sm text-green-700">Gains totaux</div>
                      </div>
                      
                      <div className="bg-purple-50 p-4 rounded-lg">
                        <div className="text-2xl font-bold text-purple-600">
                          {formatPrice(referralStats.stats.pending_earnings || 0)}
                        </div>
                        <div className="text-sm text-purple-700">Gains en attente</div>
                      </div>
                    </div>

                    {referralStats.stats.active_codes && referralStats.stats.active_codes.length > 0 && (
                      <div className="mt-6">
                        <h3 className="text-lg font-semibold text-gray-800 mb-4">
                          🎫 Vos bons de réduction
                        </h3>
                        <div className="space-y-2">
                          {referralStats.stats.active_codes.map((code, index) => (
                            <div key={index} className="bg-green-50 p-3 rounded-lg border border-green-200">
                              <span className="font-mono font-medium text-green-800">
                                {code}
                              </span>
                              <span className="text-sm text-green-600 ml-2">
                                - Bon de 20€ disponible
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="text-center py-8">
                    <div className="text-gray-500">Génération de votre code de parrainage...</div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default EspaceClient;