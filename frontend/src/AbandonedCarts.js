import React, { useState, useEffect } from 'react';
import axios from 'axios';

const AbandonedCarts = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  const loadDashboardData = async () => {
    try {
      setRefreshing(true);
      
      const token = localStorage.getItem('token');
      const config = {
        headers: { Authorization: `Bearer ${token}` }
      };

      const response = await axios.get(`${backendUrl}/api/crm/abandoned-carts/dashboard`, config);
      setDashboardData(response.data);
      
    } catch (error) {
      console.error('Erreur chargement dashboard paniers abandonnés:', error);
      alert('Erreur lors du chargement des données');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const processRecoveryEmails = async () => {
    try {
      const token = localStorage.getItem('token');
      const config = {
        headers: { Authorization: `Bearer ${token}` }
      };

      await axios.post(`${backendUrl}/api/crm/process-recovery-emails`, {}, config);
      alert('Emails de récupération traités avec succès !');
      await loadDashboardData(); // Recharger les données
      
    } catch (error) {
      console.error('Erreur traitement emails:', error);
      alert('Erreur lors du traitement des emails');
    }
  };

  const generateDeliveryNote = async (cart) => {
    try {
      const token = localStorage.getItem('token');
      const config = {
        headers: { Authorization: `Bearer ${token}` }
      };

      // Simuler une commande basée sur le panier pour générer le bon de livraison
      const deliveryData = {
        delivery_address: cart.customer_address || {
          street: "Adresse non fournie",
          postal_code: "00000",
          city: "Ville non fournie",
          country: "France"
        },
        delivery_method: "standard",
        delivery_date: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        tracking_number: `TRACK-${cart.cart_id}`,
        carrier: "Transporteur Standard",
        special_instructions: "Livraison pour panier récupéré"
      };

      const response = await axios.post(
        `${backendUrl}/api/orders/simulated-${cart.cart_id}/delivery-note`, 
        deliveryData, 
        config
      );
      
      if (response.data.pdf_base64) {
        // Créer le lien de téléchargement
        const blob = new Blob([Uint8Array.from(atob(response.data.pdf_base64), c => c.charCodeAt(0))], {
          type: 'application/pdf'
        });
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `bon-livraison-${response.data.delivery_id}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        alert('Bon de livraison généré et téléchargé !');
      }
      
    } catch (error) {
      console.error('Erreur génération bon de livraison:', error);
      alert('Erreur lors de la génération du bon de livraison');
    }
  };

  useEffect(() => {
    loadDashboardData();
    // Actualiser toutes les 30 secondes pour les nouvelles notifications
    const interval = setInterval(loadDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement des paniers abandonnés...</p>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Erreur lors du chargement des données</p>
        <button
          onClick={loadDashboardData}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Réessayer
        </button>
      </div>
    );
  }

  const { statistics, recent_carts } = dashboardData;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            🛒 Paniers Abandonnés
          </h2>
          <p className="text-gray-600">
            Gestion et récupération des paniers abandonnés avec notifications automatiques
          </p>
        </div>
        
        <div className="flex space-x-3">
          <button
            onClick={processRecoveryEmails}
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
          >
            📧 Traiter Emails
          </button>
          
          <button
            onClick={loadDashboardData}
            disabled={refreshing}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {refreshing ? '🔄 Actualisation...' : '🔄 Actualiser'}
          </button>
        </div>
      </div>

      {/* Statistiques principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-red-500">
          <div className="flex items-center">
            <div className="text-3xl text-red-600">🛒</div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-gray-700">Paniers Abandonnés</h3>
              <div className="flex items-center">
                <span className="text-3xl font-bold text-red-600">{statistics.total_abandoned}</span>
                {statistics.recent_abandoned_24h > 0 && (
                  <span className="ml-2 text-sm bg-red-100 text-red-800 px-2 py-1 rounded-full">
                    +{statistics.recent_abandoned_24h} (24h)
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
          <div className="flex items-center">
            <div className="text-3xl text-green-600">✅</div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-gray-700">Paniers Récupérés</h3>
              <div className="flex items-center">
                <span className="text-3xl font-bold text-green-600">{statistics.total_recovered}</span>
                <span className="ml-2 text-sm bg-green-100 text-green-800 px-2 py-1 rounded-full">
                  {statistics.recovery_rate}% taux
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-yellow-500">
          <div className="flex items-center">
            <div className="text-3xl text-yellow-600">💰</div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-gray-700">Valeur Perdue</h3>
              <div className="flex items-center">
                <span className="text-3xl font-bold text-yellow-600">
                  {statistics.total_abandoned_value.toFixed(0)}€
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
          <div className="flex items-center">
            <div className="text-3xl text-blue-600">📧</div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-gray-700">Emails Programmés</h3>
              <div className="flex items-center">
                <span className="text-3xl font-bold text-blue-600">{statistics.pending_recovery_emails}</span>
                <span className="ml-2 text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                  En attente
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Liste des paniers abandonnés récents */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            📋 Paniers Abandonnés Récents
            {recent_carts.length > 0 && (
              <span className="ml-2 bg-red-100 text-red-800 px-2 py-1 rounded-full text-sm">
                {recent_carts.length} actif{recent_carts.length > 1 ? 's' : ''}
              </span>
            )}
          </h3>
        </div>

        {recent_carts.length === 0 ? (
          <div className="p-8 text-center">
            <div className="text-6xl mb-4">🎉</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Aucun panier abandonné !</h3>
            <p className="text-gray-600">Toutes les commandes ont été finalisées avec succès.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Client
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Panier
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Valeur
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Abandonné le
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Emails
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {recent_carts.map((cart) => {
                  const abandonedDate = new Date(cart.abandoned_at);
                  const hoursSinceAbandoned = Math.floor((Date.now() - abandonedDate) / (1000 * 60 * 60));
                  const emailsSent = cart.recovery_emails_sent || [];
                  
                  return (
                    <tr key={cart.cart_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {cart.customer_name || 'Client anonyme'}
                          </div>
                          <div className="text-sm text-gray-500">{cart.customer_email}</div>
                          {cart.customer_phone && (
                            <div className="text-sm text-gray-500">{cart.customer_phone}</div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {cart.items.length} article{cart.items.length > 1 ? 's' : ''}
                        </div>
                        <div className="text-xs text-gray-500">
                          {cart.items.map(item => item.name || item.product_id).join(', ')}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {cart.total_value.toFixed(2)}€
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {abandonedDate.toLocaleDateString('fr-FR')}
                        </div>
                        <div className="text-xs text-gray-500">
                          Il y a {hoursSinceAbandoned}h
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center space-x-1">
                          {emailsSent.length === 0 ? (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                              📧 Aucun
                            </span>
                          ) : (
                            <>
                              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                📧 {emailsSent.length}
                              </span>
                              <div className="text-xs text-gray-500">
                                Dernier: {emailsSent[emailsSent.length - 1]?.type}
                              </div>
                            </>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                        <a
                          href={cart.recovery_link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-900 inline-block"
                          title="Lien de récupération"
                        >
                          🔗 Récupérer
                        </a>
                        
                        <button
                          onClick={() => generateDeliveryNote(cart)}
                          className="text-green-600 hover:text-green-900 ml-3"
                          title="Générer bon de livraison"
                        >
                          📄 Bon livraison
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Notifications en temps réel */}
      {statistics.recent_abandoned_24h > 0 && (
        <div className="fixed bottom-4 right-4 bg-red-600 text-white p-4 rounded-lg shadow-lg max-w-sm">
          <div className="flex items-center">
            <div className="text-2xl mr-3">🚨</div>
            <div>
              <div className="font-semibold">Nouveaux paniers abandonnés!</div>
              <div className="text-sm">
                {statistics.recent_abandoned_24h} panier{statistics.recent_abandoned_24h > 1 ? 's' : ''} abandonné{statistics.recent_abandoned_24h > 1 ? 's' : ''} dans les dernières 24h
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Informations système */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-semibold text-blue-900 mb-2">🤖 Système de Récupération Automatique</h4>
        <div className="text-sm text-blue-800 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <strong>Email Immédiat:</strong><br/>
            Après 30 minutes - Code RETOUR10 (10% remise)
          </div>
          <div>
            <strong>Email de Rappel:</strong><br/>
            Après 24 heures - Code RETOUR15 (15% remise)
          </div>
          <div>
            <strong>Email Final:</strong><br/>
            Après 72 heures - Code RETOUR20 (20% remise)
          </div>
        </div>
      </div>
    </div>
  );
};

export default AbandonedCarts;