import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const PromotionsManager = () => {
  const [referralCode, setReferralCode] = useState('');
  const [testCode, setTestCode] = useState('');
  const [validation, setValidation] = useState(null);
  const [userId, setUserId] = useState('user123');
  const [stats, setStats] = useState(null);
  const [promotionRules, setPromotionRules] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  // Charger les règles de promotion au montage
  useEffect(() => {
    loadPromotionRules();
  }, []);

  const loadPromotionRules = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/promotions/rules`);
      if (response.data.success) {
        setPromotionRules(response.data.rules);
      }
    } catch (error) {
      console.error('Erreur chargement règles:', error);
    }
  };

  const generateReferralCode = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/api/promotions/referral/generate`, {
        user_id: userId
      });
      
      if (response.data.success) {
        setReferralCode(response.data.referral_code);
        setMessage(`✅ Code généré: ${response.data.referral_code}`);
      }
    } catch (error) {
      setMessage(`❌ Erreur: ${error.response?.data?.detail || error.message}`);
    }
    setLoading(false);
  };

  const validateCode = async () => {
    if (!testCode) return;
    
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/api/promotions/referral/validate`, {
        code: testCode
      });
      
      setValidation(response.data);
      if (response.data.valid) {
        setMessage(`✅ Code valide! Réduction: ${response.data.discount_percentage}%`);
      } else {
        setMessage('❌ Code invalide ou expiré');
      }
    } catch (error) {
      setMessage(`❌ Erreur: ${error.response?.data?.detail || error.message}`);
    }
    setLoading(false);
  };

  const loadStats = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/api/promotions/referral/stats/${userId}`);
      
      if (response.data.success) {
        setStats(response.data.stats);
        setMessage('✅ Statistiques chargées');
      }
    } catch (error) {
      setMessage(`❌ Erreur: ${error.response?.data?.detail || error.message}`);
    }
    setLoading(false);
  };

  const testLaunchOffer = async () => {
    setLoading(true);
    try {
      // Test avec un panier éligible
      const testCart = [
        {
          product_id: 'osmoseur-premium',
          quantity: 1,
          price: 549
        }
      ];

      const response = await axios.post(`${API_BASE}/api/promotions/launch-offer/check`, {
        items: testCart
      });
      
      if (response.data.success && response.data.eligibility.eligible) {
        setMessage('🎁 Panier éligible à l\'offre de lancement!');
        
        // Test d'application de l'offre
        const applyResponse = await axios.post(`${API_BASE}/api/promotions/launch-offer/apply`, {
          cart_items: testCart,
          selected_gift_id: 'fontaine-eau-animaux',
          customer_email: 'test@josmoze.com'
        });
        
        if (applyResponse.data.success) {
          setMessage('🎉 Offre de lancement appliquée avec succès!');
        }
      } else {
        setMessage('ℹ️ Panier non éligible à l\'offre de lancement');
      }
    } catch (error) {
      setMessage(`❌ Erreur: ${error.response?.data?.detail || error.message}`);
    }
    setLoading(false);
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h1 className="text-3xl font-bold text-gray-800 mb-8 text-center">
        🎁 Gestionnaire de Promotions Josmoze
      </h1>

      {/* Messages */}
      {message && (
        <div className={`p-4 rounded-lg mb-6 ${
          message.includes('✅') || message.includes('🎉') ? 'bg-green-100 text-green-800' :
          message.includes('❌') ? 'bg-red-100 text-red-800' :
          'bg-blue-100 text-blue-800'
        }`}>
          {message}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        
        {/* Section Codes de Parrainage */}
        <div className="bg-gray-50 p-6 rounded-lg">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">
            👥 Système de Parrainage
          </h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-2">
                User ID:
              </label>
              <input
                type="text"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="user123"
              />
            </div>

            <button
              onClick={generateReferralCode}
              disabled={loading}
              className="w-full bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 text-white px-4 py-2 rounded-md transition-colors"
            >
              {loading ? 'Génération...' : 'Générer Code de Parrainage'}
            </button>

            {referralCode && (
              <div className="p-3 bg-green-50 border border-green-200 rounded-md">
                <p className="text-sm text-gray-600">Code généré:</p>
                <p className="font-mono text-lg font-bold text-green-700">{referralCode}</p>
              </div>
            )}
          </div>
        </div>

        {/* Section Validation */}
        <div className="bg-gray-50 p-6 rounded-lg">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">
            ✅ Validation de Code
          </h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-2">
                Code à tester:
              </label>
              <input
                type="text"
                value={testCode}
                onChange={(e) => setTestCode(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="JOSM1234"
              />
            </div>

            <button
              onClick={validateCode}
              disabled={loading || !testCode}
              className="w-full bg-green-500 hover:bg-green-600 disabled:bg-gray-300 text-white px-4 py-2 rounded-md transition-colors"
            >
              {loading ? 'Validation...' : 'Valider Code'}
            </button>

            {validation && (
              <div className={`p-3 rounded-md border ${
                validation.valid 
                  ? 'bg-green-50 border-green-200 text-green-700'
                  : 'bg-red-50 border-red-200 text-red-700'
              }`}>
                {validation.valid ? (
                  <div>
                    <p>✅ Code valide</p>
                    <p>Réduction: {validation.discount_percentage}%</p>
                    <p className="text-sm">{validation.description}</p>
                  </div>
                ) : (
                  <p>❌ {validation.message}</p>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Section Statistiques */}
        <div className="bg-gray-50 p-6 rounded-lg">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">
            📊 Statistiques de Parrainage
          </h2>
          
          <button
            onClick={loadStats}
            disabled={loading}
            className="w-full bg-purple-500 hover:bg-purple-600 disabled:bg-gray-300 text-white px-4 py-2 rounded-md transition-colors mb-4"
          >
            {loading ? 'Chargement...' : 'Charger Statistiques'}
          </button>

          {stats && (
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Code personnel:</span>
                <span className="font-mono font-bold">{stats.referral_code || 'Aucun'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Total parrainages:</span>
                <span className="font-bold">{stats.total_referrals || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Bonus gagnés:</span>
                <span className="font-bold text-green-600">{stats.total_bonus_earned || 0}€</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Bons disponibles:</span>
                <span className="font-bold text-blue-600">{stats.available_vouchers_amount || 0}€</span>
              </div>
            </div>
          )}
        </div>

        {/* Section Offre de Lancement */}
        <div className="bg-gray-50 p-6 rounded-lg">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">
            🚀 Offre de Lancement
          </h2>
          
          <button
            onClick={testLaunchOffer}
            disabled={loading}
            className="w-full bg-orange-500 hover:bg-orange-600 disabled:bg-gray-300 text-white px-4 py-2 rounded-md transition-colors mb-4"
          >
            {loading ? 'Test...' : 'Tester Offre de Lancement'}
          </button>

          {promotionRules && (
            <div className="text-sm space-y-2">
              <h3 className="font-semibold text-gray-700">Règles actuelles:</h3>
              {promotionRules.launch_offer && (
                <div className="bg-white p-3 rounded border">
                  <p className="text-gray-600 text-xs">
                    {promotionRules.launch_offer.description}
                  </p>
                  <p className="mt-2 text-xs">
                    <strong>Produits éligibles:</strong> {promotionRules.launch_offer.eligible_products?.join(', ')}
                  </p>
                  <p className="text-xs">
                    <strong>Cadeaux:</strong> {promotionRules.launch_offer.gift_options?.join(', ')}
                  </p>
                </div>
              )}
              {promotionRules.referral_system && (
                <div className="bg-white p-3 rounded border">
                  <p className="text-gray-600 text-xs">
                    {promotionRules.referral_system.description}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Section Test Global */}
      <div className="mt-8 p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
        <h2 className="text-xl font-semibold text-gray-700 mb-4">
          🧪 Tests des Nouvelles Fonctionnalités
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="font-semibold text-green-600 mb-2">✅ Nouveaux Produits</h3>
            <ul className="text-xs space-y-1">
              <li>• Osmoseur Essentiel - 449€</li>
              <li>• Osmoseur Premium - 549€</li>
              <li>• Osmoseur Prestige - 899€</li>
              <li>• Purificateur H2 - 79€</li>
              <li>• Fontaine Animaux - 49€</li>
            </ul>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="font-semibold text-blue-600 mb-2">🎁 Promotions</h3>
            <ul className="text-xs space-y-1">
              <li>• Offre lancement active</li>
              <li>• Système parrainage 10%/50€</li>
              <li>• Codes uniques générés</li>
              <li>• Validation temps réel</li>
            </ul>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="font-semibold text-purple-600 mb-2">🔧 API Ready</h3>
            <ul className="text-xs space-y-1">
              <li>• 7 endpoints promotions</li>
              <li>• Base données optimisée</li>
              <li>• Thomas ChatBot V2</li>
              <li>• Email Sequencer V2</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PromotionsManager;