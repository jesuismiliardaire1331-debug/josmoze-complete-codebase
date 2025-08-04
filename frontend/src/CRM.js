import React, { useState, useEffect } from "react";
import axios from "axios";
import { useAuth } from "./CRMLogin";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CRMDashboard = () => {
  const { user, logout } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [leads, setLeads] = useState([]);
  const [orders, setOrders] = useState([]);
  const [stockData, setStockData] = useState(null);
  const [invoices, setInvoices] = useState([]);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [filters, setFilters] = useState({
    status: '',
    customer_type: '',
    lead_type: ''
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
    fetchLeads();
    fetchOrders();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get(`${API}/crm/dashboard`);
      setDashboardData(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement du dashboard:', error);
      if (error.response?.status === 401) {
        logout();
      }
    }
  };

  const fetchLeads = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.status) params.append('status', filters.status);
      if (filters.customer_type) params.append('customer_type', filters.customer_type);

      const response = await axios.get(`${API}/crm/leads?${params}`);
      setLeads(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des leads:', error);
    }
  };

  const fetchOrders = async () => {
    try {
      const response = await axios.get(`${API}/orders`);
      setOrders(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des commandes:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateLeadStatus = async (leadId, newStatus) => {
    try {
      await axios.put(`${API}/crm/leads/${leadId}`, { status: newStatus });
      fetchLeads();
      fetchDashboardData();
      alert('✅ Statut mis à jour avec succès !');
    } catch (error) {
      console.error('Erreur lors de la mise à jour:', error);
      alert('❌ Erreur lors de la mise à jour');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      new: { style: 'bg-gradient-to-r from-blue-400 to-blue-600 text-white', label: '🆕 Nouveau', icon: '🆕' },
      contacted: { style: 'bg-gradient-to-r from-yellow-400 to-orange-500 text-white', label: '📞 Contacté', icon: '📞' },
      qualified: { style: 'bg-gradient-to-r from-purple-400 to-purple-600 text-white', label: '⭐ Qualifié', icon: '⭐' },
      converted: { style: 'bg-gradient-to-r from-green-400 to-green-600 text-white', label: '✅ Converti', icon: '✅' },
      lost: { style: 'bg-gradient-to-r from-red-400 to-red-600 text-white', label: '❌ Perdu', icon: '❌' }
    };

    const config = statusConfig[status] || { style: 'bg-gray-100 text-gray-800', label: status, icon: '❓' };

    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold shadow-sm ${config.style}`}>
        {config.label}
      </span>
    );
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600 font-bold bg-green-100 px-2 py-1 rounded-full';
    if (score >= 60) return 'text-yellow-600 font-semibold bg-yellow-100 px-2 py-1 rounded-full';
    if (score >= 40) return 'text-orange-600 font-medium bg-orange-100 px-2 py-1 rounded-full';
    return 'text-red-600 font-medium bg-red-100 px-2 py-1 rounded-full';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center bg-white p-8 rounded-xl shadow-lg">
          <div className="text-6xl mb-4 animate-bounce">🚀</div>
          <h2 className="text-xl font-bold text-gray-700 mb-2">Chargement du CRM Josmose</h2>
          <p className="text-gray-500">Préparation de vos données...</p>
          <div className="mt-4 w-8 h-8 border-4 border-blue-200 border-top-blue-500 rounded-full animate-spin mx-auto"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header Coloré et Ludique */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-700 shadow-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-4xl font-bold text-white flex items-center">
                🌊 CRM Josmose 📊
              </h1>
              <p className="text-blue-100 mt-2 text-lg">Tableau de bord - Gestion intelligente des leads</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="bg-white/20 rounded-lg px-4 py-2 text-white">
                <div className="text-sm opacity-90">Connecté:</div>
                <div className="font-semibold">{user?.name || 'Utilisateur'}</div>
              </div>
              <button
                onClick={logout}
                className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg font-semibold transition-colors shadow-md"
              >
                🚪 Déconnexion
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Onglets Colorés et Ludiques */}
        <div className="mb-8">
          <div className="flex flex-wrap gap-2 bg-white p-2 rounded-xl shadow-lg">
            {[
              { id: 'dashboard', name: 'Dashboard', icon: '📊', color: 'from-blue-500 to-blue-600' },
              { id: 'leads', name: 'Leads', icon: '👥', color: 'from-green-500 to-emerald-600' },
              { id: 'orders', name: 'Commandes', icon: '🛒', color: 'from-purple-500 to-violet-600' },
              { id: 'analytics', name: 'Analytics', icon: '📈', color: 'from-orange-500 to-red-500' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-semibold text-sm transition-all duration-200 ${
                  activeTab === tab.id
                    ? `bg-gradient-to-r ${tab.color} text-white shadow-lg transform scale-105`
                    : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
                }`}
              >
                <span className="text-lg">{tab.icon}</span>
                <span>{tab.name}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Contenu selon l'onglet actif */}
        {activeTab === 'dashboard' && dashboardData && (
          <div className="space-y-8">
            {/* Cartes KPI Colorées */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white p-6 rounded-xl shadow-lg hover:transform hover:scale-105 transition-all">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-blue-100 text-sm font-medium">Total Leads</p>
                    <p className="text-3xl font-bold">{dashboardData.total_leads}</p>
                  </div>
                  <div className="text-4xl opacity-80">👥</div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-green-500 to-emerald-600 text-white p-6 rounded-xl shadow-lg hover:transform hover:scale-105 transition-all">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-green-100 text-sm font-medium">Taux Conversion</p>
                    <p className="text-3xl font-bold">{dashboardData.conversion_rate}%</p>
                  </div>
                  <div className="text-4xl opacity-80">🎯</div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-purple-500 to-violet-600 text-white p-6 rounded-xl shadow-lg hover:transform hover:scale-105 transition-all">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-purple-100 text-sm font-medium">Commandes Semaine</p>
                    <p className="text-3xl font-bold">{dashboardData.weekly_orders}</p>
                  </div>
                  <div className="text-4xl opacity-80">🛒</div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-orange-500 to-red-500 text-white p-6 rounded-xl shadow-lg hover:transform hover:scale-105 transition-all">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-orange-100 text-sm font-medium">CA Semaine</p>
                    <p className="text-3xl font-bold">€{dashboardData.weekly_revenue?.toFixed(2)}</p>
                  </div>
                  <div className="text-4xl opacity-80">💰</div>
                </div>
              </div>
            </div>

            {/* Graphiques */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-100">
                <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center">
                  <span className="mr-3">📊</span>
                  Leads par Statut
                </h3>
                <div className="space-y-4">
                  {Object.entries(dashboardData.leads_by_status).map(([status, count]) => (
                    <div key={status} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center">
                        {getStatusBadge(status)}
                      </div>
                      <span className="text-2xl font-bold text-gray-700 bg-white px-3 py-1 rounded-full shadow">{count}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-100">
                <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center">
                  <span className="mr-3">🎯</span>
                  Leads par Type
                </h3>
                <div className="space-y-4">
                  {Object.entries(dashboardData.leads_by_type).map(([type, count]) => (
                    <div key={type} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <span className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-semibold ${
                        type === 'B2B' ? 'bg-gradient-to-r from-purple-400 to-purple-600 text-white' : 
                        'bg-gradient-to-r from-blue-400 to-blue-600 text-white'
                      }`}>
                        {type === 'B2B' ? '🏢 Professionnels' : '🏠 Particuliers'}
                      </span>
                      <span className="text-2xl font-bold text-gray-700 bg-white px-3 py-1 rounded-full shadow">{count}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Activité Récente */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-100">
                <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center">
                  <span className="mr-3">🌟</span>
                  Leads Récents
                </h3>
                <div className="space-y-4">
                  {dashboardData.recent_leads?.slice(0, 5).map((lead) => (
                    <div key={lead.id} className="bg-gray-50 p-4 rounded-lg hover:bg-gray-100 transition-colors">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-semibold text-gray-800">{lead.name}</p>
                          <p className="text-sm text-gray-600">{lead.email}</p>
                        </div>
                        <div className="text-right space-y-2">
                          {getStatusBadge(lead.status)}
                          <div className="flex items-center space-x-2">
                            <span className="text-xs text-gray-500">Score:</span>
                            <span className={`text-sm font-bold ${getScoreColor(lead.score)}`}>
                              {lead.score}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-100">
                <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center">
                  <span className="mr-3">🛍️</span>
                  Commandes Récentes
                </h3>
                <div className="space-y-4">
                  {dashboardData.recent_orders?.slice(0, 5).map((order) => (
                    <div key={order.id} className="bg-gray-50 p-4 rounded-lg hover:bg-gray-100 transition-colors">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-semibold text-gray-800">{order.customer_name}</p>
                          <p className="text-sm text-gray-600">{formatDate(order.created_at)}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-lg font-bold text-gray-800">€{order.total}</p>
                          <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${
                            order.status === 'paid' ? 'bg-gradient-to-r from-green-400 to-green-600 text-white' : 
                            'bg-gradient-to-r from-yellow-400 to-orange-500 text-white'
                          }`}>
                            {order.status === 'paid' ? '✅ Payé' : '⏳ En attente'}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Onglet Leads */}
        {activeTab === 'leads' && (
          <div className="space-y-6">
            {/* Filtres */}
            <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-100">
              <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
                <span className="mr-2">🔍</span>
                Filtres
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Statut</label>
                  <select
                    value={filters.status}
                    onChange={(e) => setFilters({...filters, status: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                  >
                    <option value="">Tous les statuts</option>
                    <option value="new">🆕 Nouveau</option>
                    <option value="contacted">📞 Contacté</option>
                    <option value="qualified">⭐ Qualifié</option>
                    <option value="converted">✅ Converti</option>
                    <option value="lost">❌ Perdu</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Type Client</label>
                  <select
                    value={filters.customer_type}
                    onChange={(e) => setFilters({...filters, customer_type: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                  >
                    <option value="">Tous</option>
                    <option value="B2C">🏠 Particuliers</option>
                    <option value="B2B">🏢 Professionnels</option>
                  </select>
                </div>

                <div className="md:col-span-2 flex items-end">
                  <button
                    onClick={fetchLeads}
                    className="w-full bg-gradient-to-r from-blue-500 to-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:from-blue-600 hover:to-blue-700 transition-all shadow-md transform hover:scale-105"
                  >
                    🔍 Rechercher
                  </button>
                </div>
              </div>
            </div>

            {/* Tableau des Leads */}
            <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
              <div className="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4 border-b">
                <h3 className="text-xl font-bold text-gray-800 flex items-center">
                  <span className="mr-3">👥</span>
                  Mes Leads ({leads.length})
                </h3>
              </div>
              
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Contact</th>
                      <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Type</th>
                      <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Statut</th>
                      <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Score</th>
                      <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Date</th>
                      <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {leads.map((lead, index) => (
                      <tr key={lead.id} className={`hover:bg-blue-50 transition-colors ${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
                        <td className="px-6 py-4">
                          <div>
                            <div className="font-semibold text-gray-900">{lead.name}</div>
                            <div className="text-sm text-gray-600">{lead.email}</div>
                            {lead.phone && <div className="text-sm text-gray-500">{lead.phone}</div>}
                            {lead.company && <div className="text-xs text-blue-600 font-medium">{lead.company}</div>}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${
                            lead.customer_type === 'B2B' ? 'bg-gradient-to-r from-purple-400 to-purple-600 text-white' : 
                            'bg-gradient-to-r from-blue-400 to-blue-600 text-white'
                          }`}>
                            {lead.customer_type === 'B2B' ? '🏢 Pro' : '🏠 Part'}
                          </span>
                          <div className="text-xs text-gray-500 mt-1">{lead.lead_type}</div>
                        </td>
                        <td className="px-6 py-4">
                          {getStatusBadge(lead.status)}
                        </td>
                        <td className="px-6 py-4">
                          <span className={`text-lg font-bold ${getScoreColor(lead.score)}`}>
                            {lead.score}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {formatDate(lead.created_at)}
                          {lead.follow_up_date && (
                            <div className="text-xs text-orange-600 mt-1">
                              📅 Relance: {formatDate(lead.follow_up_date)}
                            </div>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          <select
                            value={lead.status}
                            onChange={(e) => updateLeadStatus(lead.id, e.target.value)}
                            className="text-sm border border-gray-300 rounded-lg px-3 py-1 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          >
                            <option value="new">🆕 Nouveau</option>
                            <option value="contacted">📞 Contacté</option>
                            <option value="qualified">⭐ Qualifié</option>
                            <option value="converted">✅ Converti</option>
                            <option value="lost">❌ Perdu</option>
                          </select>
                          {lead.consultation_requested && (
                            <div className="text-xs text-green-600 mt-2 font-medium">
                              ☎️ Consultation demandée
                            </div>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Onglet Commandes */}
        {activeTab === 'orders' && (
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
              <div className="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4 border-b">
                <h3 className="text-xl font-bold text-gray-800 flex items-center">
                  <span className="mr-3">🛒</span>
                  Mes Commandes ({orders.length})
                </h3>
              </div>
              
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Client</th>
                      <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Articles</th>
                      <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Total</th>
                      <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Statut</th>
                      <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Date</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {orders.map((order, index) => (
                      <tr key={order.id} className={`hover:bg-blue-50 transition-colors ${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
                        <td className="px-6 py-4">
                          <div>
                            <div className="font-semibold text-gray-900">{order.customer_name}</div>
                            <div className="text-sm text-gray-600">{order.customer_email}</div>
                            {order.customer_type === 'B2B' && (
                              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold bg-gradient-to-r from-purple-400 to-purple-600 text-white mt-1">
                                🏢 Professionnel
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm font-medium text-gray-900">{order.items?.length || 0} article(s)</div>
                          <div className="text-xs text-gray-500">
                            {order.items?.map((item, idx) => (
                              <div key={idx}>
                                {item.quantity}x {item.product_id}
                              </div>
                            ))}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-lg font-bold text-gray-900">€{order.total}</div>
                          <div className="text-xs text-gray-500">{order.currency}</div>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold ${
                            order.status === 'paid' ? 'bg-gradient-to-r from-green-400 to-green-600 text-white' : 
                            order.status === 'pending' ? 'bg-gradient-to-r from-yellow-400 to-orange-500 text-white' : 
                            'bg-gradient-to-r from-red-400 to-red-600 text-white'
                          }`}>
                            {order.status === 'paid' ? '✅ Payé' : 
                             order.status === 'pending' ? '⏳ En attente' : '❌ Échoué'}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {formatDate(order.created_at)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Onglet Analytics */}
        {activeTab === 'analytics' && (
          <div className="text-center py-16">
            <div className="bg-white p-12 rounded-2xl shadow-xl max-w-2xl mx-auto">
              <div className="text-8xl mb-6">📈</div>
              <h3 className="text-2xl font-bold text-gray-800 mb-4">Analytics Avancées</h3>
              <p className="text-gray-600 text-lg mb-8">
                Fonctionnalité en développement - Graphiques détaillés et rapports personnalisés arrivent bientôt !
              </p>
              <div className="grid grid-cols-2 gap-4 text-left">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="text-2xl mb-2">📊</div>
                  <h4 className="font-semibold text-gray-800">Graphiques Interactifs</h4>
                  <p className="text-sm text-gray-600">Visualisation avancée des données</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="text-2xl mb-2">📋</div>
                  <h4 className="font-semibold text-gray-800">Rapports Exportables</h4>
                  <p className="text-sm text-gray-600">PDF et Excel disponibles</p>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <div className="text-2xl mb-2">🎯</div>
                  <h4 className="font-semibold text-gray-800">Prédictions IA</h4>
                  <p className="text-sm text-gray-600">Analyse prédictive des ventes</p>
                </div>
                <div className="bg-orange-50 p-4 rounded-lg">
                  <div className="text-2xl mb-2">⚡</div>
                  <h4 className="font-semibold text-gray-800">Temps Réel</h4>
                  <p className="text-sm text-gray-600">Données en direct</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CRMDashboard;