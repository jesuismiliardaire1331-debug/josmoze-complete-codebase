import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const PromotionsManager = () => {
  const [promotions, setPromotions] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [newPromotion, setNewPromotion] = useState({
    code: '',
    name: '',
    description: '',
    type: 'percentage',
    value: '',
    min_order_amount: '0',
    max_discount_amount: '',
    usage_limit: '',
    usage_limit_per_customer: '1',
    expires_at: '',
    target_customer_type: 'both'
  });

  useEffect(() => {
    fetchPromotions();
  }, []);

  const fetchPromotions = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/api/admin/promotions`);
      if (response.data.success) {
        setPromotions(response.data.promotions);
      }
    } catch (error) {
      console.error('Error fetching promotions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePromotion = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      
      // Préparer les données
      const promotionData = {
        ...newPromotion,
        value: parseFloat(newPromotion.value),
        min_order_amount: parseFloat(newPromotion.min_order_amount) || 0,
        max_discount_amount: newPromotion.max_discount_amount ? parseFloat(newPromotion.max_discount_amount) : null,
        usage_limit: newPromotion.usage_limit ? parseInt(newPromotion.usage_limit) : null,
        usage_limit_per_customer: parseInt(newPromotion.usage_limit_per_customer),
        expires_at: newPromotion.expires_at ? new Date(newPromotion.expires_at).toISOString() : null
      };

      const response = await axios.post(`${API_BASE}/api/admin/promotions/create`, promotionData);
      
      if (response.data.success) {
        await fetchPromotions();
        setShowCreateForm(false);
        setNewPromotion({
          code: '',
          name: '',
          description: '',
          type: 'percentage',
          value: '',
          min_order_amount: '0',
          max_discount_amount: '',
          usage_limit: '',
          usage_limit_per_customer: '1',
          expires_at: '',
          target_customer_type: 'both'
        });
        alert('Promotion créée avec succès !');
      }
    } catch (error) {
      console.error('Error creating promotion:', error);
      alert('Erreur lors de la création de la promotion');
    } finally {
      setLoading(false);
    }
  };

  const togglePromotionStatus = async (promotionId) => {
    try {
      const response = await axios.post(`${API_BASE}/api/admin/promotions/${promotionId}/toggle`);
      if (response.data.success) {
        await fetchPromotions();
      }
    } catch (error) {
      console.error('Error toggling promotion:', error);
      alert('Erreur lors de la modification');
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Pas de limite';
    return new Date(dateString).toLocaleDateString('fr-FR');
  };

  const getTypeLabel = (type) => {
    switch (type) {
      case 'percentage': return 'Pourcentage';
      case 'fixed_amount': return 'Montant fixe';
      case 'free_shipping': return 'Livraison gratuite';
      default: return type;
    }
  };

  const getValueDisplay = (promotion) => {
    switch (promotion.type) {
      case 'percentage': return `${promotion.value}%`;
      case 'fixed_amount': return `${promotion.value}€`;
      case 'free_shipping': return 'Livraison offerte';
      default: return promotion.value;
    }
  };

  return (
    <div className="promotions-manager p-6 bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">🎁 Gestion des Promotions</h2>
          <p className="text-gray-600">Créer et gérer les codes promotionnels</p>
        </div>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
        >
          {showCreateForm ? '✕ Annuler' : '+ Nouvelle Promotion'}
        </button>
      </div>

      {/* Formulaire de création */}
      {showCreateForm && (
        <div className="bg-gray-50 p-6 rounded-lg mb-6">
          <h3 className="text-lg font-semibold mb-4">Créer une nouvelle promotion</h3>
          <form onSubmit={handleCreatePromotion} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Code promotionnel *</label>
              <input
                type="text"
                value={newPromotion.code}
                onChange={(e) => setNewPromotion({...newPromotion, code: e.target.value.toUpperCase()})}
                className="w-full p-2 border border-gray-300 rounded-md"
                placeholder="Ex: BIENVENUE10"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nom de la promotion *</label>
              <input
                type="text"
                value={newPromotion.name}
                onChange={(e) => setNewPromotion({...newPromotion, name: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-md"
                placeholder="Ex: Réduction de bienvenue"
                required
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                value={newPromotion.description}
                onChange={(e) => setNewPromotion({...newPromotion, description: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-md"
                rows="2"
                placeholder="Description visible par les clients"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Type de réduction</label>
              <select
                value={newPromotion.type}
                onChange={(e) => setNewPromotion({...newPromotion, type: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-md"
              >
                <option value="percentage">Pourcentage</option>
                <option value="fixed_amount">Montant fixe</option>
                <option value="free_shipping">Livraison gratuite</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Valeur {newPromotion.type === 'percentage' ? '(%)' : newPromotion.type === 'fixed_amount' ? '(€)' : ''}
              </label>
              <input
                type="number"
                step="0.01"
                value={newPromotion.value}
                onChange={(e) => setNewPromotion({...newPromotion, value: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-md"
                placeholder={newPromotion.type === 'percentage' ? '10' : '20'}
                required={newPromotion.type !== 'free_shipping'}
                disabled={newPromotion.type === 'free_shipping'}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Commande minimum (€)</label>
              <input
                type="number"
                step="0.01"
                value={newPromotion.min_order_amount}
                onChange={(e) => setNewPromotion({...newPromotion, min_order_amount: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-md"
                placeholder="0"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Réduction maximum (€)</label>
              <input
                type="number"
                step="0.01"
                value={newPromotion.max_discount_amount}
                onChange={(e) => setNewPromotion({...newPromotion, max_discount_amount: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-md"
                placeholder="Pas de limite"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Limite d'utilisation totale</label>
              <input
                type="number"
                value={newPromotion.usage_limit}
                onChange={(e) => setNewPromotion({...newPromotion, usage_limit: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-md"
                placeholder="Illimité"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Limite par client</label>
              <input
                type="number"
                value={newPromotion.usage_limit_per_customer}
                onChange={(e) => setNewPromotion({...newPromotion, usage_limit_per_customer: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-md"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Date d'expiration</label>
              <input
                type="datetime-local"
                value={newPromotion.expires_at}
                onChange={(e) => setNewPromotion({...newPromotion, expires_at: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-md"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Type de client</label>
              <select
                value={newPromotion.target_customer_type}
                onChange={(e) => setNewPromotion({...newPromotion, target_customer_type: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-md"
              >
                <option value="both">Tous les clients</option>
                <option value="B2C">Particuliers (B2C)</option>
                <option value="B2B">Professionnels (B2B)</option>
              </select>
            </div>

            <div className="md:col-span-2">
              <button
                type="submit"
                disabled={loading}
                className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg font-medium transition-colors disabled:opacity-50"
              >
                {loading ? 'Création...' : 'Créer la promotion'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Liste des promotions */}
      <div className="overflow-x-auto">
        <table className="w-full table-auto">
          <thead>
            <tr className="bg-gray-50">
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Code</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Nom</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Type</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Valeur</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Utilisations</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Expiration</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Statut</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan="8" className="px-4 py-8 text-center text-gray-500">
                  Chargement des promotions...
                </td>
              </tr>
            ) : promotions.length === 0 ? (
              <tr>
                <td colSpan="8" className="px-4 py-8 text-center text-gray-500">
                  Aucune promotion trouvée
                </td>
              </tr>
            ) : (
              promotions.map((promotion) => (
                <tr key={promotion.id} className="border-b hover:bg-gray-50">
                  <td className="px-4 py-3 font-mono font-medium">{promotion.code}</td>
                  <td className="px-4 py-3">{promotion.name}</td>
                  <td className="px-4 py-3">{getTypeLabel(promotion.type)}</td>
                  <td className="px-4 py-3 font-medium">{getValueDisplay(promotion)}</td>
                  <td className="px-4 py-3">
                    {promotion.used_count}{promotion.usage_limit ? `/${promotion.usage_limit}` : ''}
                  </td>
                  <td className="px-4 py-3">{formatDate(promotion.expires_at)}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      promotion.active 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {promotion.active ? 'Actif' : 'Inactif'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => togglePromotionStatus(promotion.id)}
                      className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                        promotion.active
                          ? 'bg-red-100 text-red-700 hover:bg-red-200'
                          : 'bg-green-100 text-green-700 hover:bg-green-200'
                      }`}
                    >
                      {promotion.active ? 'Désactiver' : 'Activer'}
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Statistiques */}
      {promotions.length > 0 && (
        <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{promotions.length}</div>
            <div className="text-sm text-blue-700">Promotions totales</div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {promotions.filter(p => p.active).length}
            </div>
            <div className="text-sm text-green-700">Actives</div>
          </div>
          <div className="bg-orange-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-orange-600">
              {promotions.reduce((sum, p) => sum + p.used_count, 0)}
            </div>
            <div className="text-sm text-orange-700">Utilisations totales</div>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">
              {promotions.filter(p => p.expires_at && new Date(p.expires_at) < new Date()).length}
            </div>
            <div className="text-sm text-purple-700">Expirées</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PromotionsManager;