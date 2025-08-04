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
      console.error('Failed to fetch leads:', error);
    }
  };

  const fetchOrders = async () => {
    try {
      const response = await axios.get(`${API}/orders`);
      setOrders(response.data);
    } catch (error) {
      console.error('Failed to fetch orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCampaigns = async () => {
    try {
      const response = await axios.get(`${API}/crm/marketing/campaigns`);
      setCampaigns(response.data);
    } catch (error) {
      console.error('Failed to fetch campaigns:', error);
    }
  };

  const fetchAutomationLogs = async () => {
    try {
      const response = await axios.get(`${API}/crm/automation/logs`);
      setAutomationLogs(response.data);
    } catch (error) {
      console.error('Failed to fetch automation logs:', error);
    }
  };

  const updateLeadStatus = async (leadId, newStatus) => {
    try {
      await axios.put(`${API}/crm/leads/${leadId}`, { status: newStatus });
      fetchLeads();
      fetchAdvancedDashboard();
    } catch (error) {
      console.error('Failed to update lead:', error);
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
    const statusStyles = {
      new: 'bg-blue-100 text-blue-800',
      contacted: 'bg-yellow-100 text-yellow-800',
      qualified: 'bg-purple-100 text-purple-800',
      converted: 'bg-green-100 text-green-800',
      lost: 'bg-red-100 text-red-800'
    };

    const statusLabels = {
      new: 'Nouveau',
      contacted: 'Contacté',
      qualified: 'Qualifié',
      converted: 'Converti',
      lost: 'Perdu'
    };

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusStyles[status] || 'bg-gray-100 text-gray-800'}`}>
        {statusLabels[status] || status}
      </span>
    );
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600 font-bold';
    if (score >= 60) return 'text-yellow-600 font-semibold';
    if (score >= 40) return 'text-orange-600';
    return 'text-red-600';
  };

  const getRoleColor = (role) => {
    const colors = {
      admin: 'text-red-600',
      manager: 'text-purple-600',
      agent: 'text-blue-600',
      support: 'text-orange-600'
    };
    return colors[role] || 'text-gray-600';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl mb-4">⏳</div>
          <p className="text-gray-600">Chargement du CRM...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header with User Info */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <span className="text-2xl">💧</span>
                <h1 className="text-2xl font-bold text-gray-900">Josmose CRM</h1>
              </div>
              {dashboardData?.automation?.automation_health && (
                <div className="flex items-center space-x-2">
                  <div className={`w-3 h-3 rounded-full ${
                    dashboardData.automation.automation_health === 'healthy' ? 'bg-green-400' : 'bg-yellow-400'
                  }`}></div>
                  <span className="text-sm text-gray-600">
                    Automation {dashboardData.automation.automation_health}
                  </span>
                </div>
              )}
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <div className="text-sm font-medium text-gray-900">
                  {user?.full_name}
                </div>
                <div className={`text-xs ${getRoleColor(user?.role)} font-medium`}>
                  {user?.role?.toUpperCase()}
                </div>
              </div>
              <button
                onClick={logout}
                className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              >
                Déconnexion
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'dashboard', name: 'Analytics 📊', icon: '📊' },
              { id: 'leads', name: 'Leads 👥', icon: '👥' },
              { id: 'orders', name: 'Commandes 🛒', icon: '🛒' },
              { id: 'automation', name: 'Automation 🤖', icon: '🤖' },
              { id: 'campaigns', name: 'Campagnes 📧', icon: '📧' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && dashboardData && (
          <div className="mt-6">
            {/* Enhanced KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="text-2xl">👥</div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Total Leads
                        </dt>
                        <dd className="text-lg font-medium text-gray-900">
                          {dashboardData.total_leads}
                        </dd>
                      </dl>
                    </div>
                  </div>
                  <div className="mt-2">
                    <div className="flex items-center text-sm">
                      <span className="text-green-600 font-medium">+15%</span>
                      <span className="text-gray-500 ml-2">vs mois dernier</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="text-2xl">🎯</div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Conversion
                        </dt>
                        <dd className="text-lg font-medium text-gray-900">
                          {dashboardData.conversion_rate}%
                        </dd>
                      </dl>
                    </div>
                  </div>
                  <div className="mt-2">
                    <div className="flex items-center text-sm">
                      <span className="text-blue-600 font-medium">Excellent</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="text-2xl">💰</div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          CA Mensuel
                        </dt>
                        <dd className="text-lg font-medium text-gray-900">
                          €{dashboardData.advanced_metrics?.monthly_revenue?.toFixed(2) || '0.00'}
                        </dd>
                      </dl>
                    </div>
                  </div>
                  <div className="mt-2">
                    <div className="flex items-center text-sm">
                      <span className="text-green-600 font-medium">+{dashboardData.advanced_metrics?.growth_rate || 0}%</span>
                      <span className="text-gray-500 ml-2">croissance</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="text-2xl">🤖</div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Messages Auto
                        </dt>
                        <dd className="text-lg font-medium text-gray-900">
                          {(dashboardData.automation?.email_sent || 0) + 
                           (dashboardData.automation?.sms_sent || 0) + 
                           (dashboardData.automation?.whatsapp_sent || 0)}
                        </dd>
                      </dl>
                    </div>
                  </div>
                  <div className="mt-2">
                    <div className="flex items-center text-sm">
                      <span className="text-purple-600 font-medium">
                        {dashboardData.automation?.pending_automations || 0} en attente
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Charts and Analytics */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              {/* Conversion Funnel */}
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Funnel de Conversion</h3>
                {dashboardData.advanced_metrics?.conversion_funnel && (
                  <div className="space-y-4">
                    {Object.entries(dashboardData.advanced_metrics.conversion_funnel).map(([status, count], index) => (
                      <div key={status} className="flex items-center">
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-sm font-medium capitalize">{status}</span>
                            <span className="text-sm text-gray-600">{count}</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full ${
                                index === 0 ? 'bg-blue-500' :
                                index === 1 ? 'bg-yellow-500' :
                                index === 2 ? 'bg-purple-500' : 'bg-green-500'
                              }`}
                              style={{ 
                                width: `${Math.max(10, (count / Math.max(...Object.values(dashboardData.advanced_metrics.conversion_funnel))) * 100)}%`
                              }}
                            ></div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Lead Sources */}
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Sources de Leads</h3>
                {dashboardData.advanced_metrics?.lead_sources && (
                  <div className="space-y-3">
                    {dashboardData.advanced_metrics.lead_sources.map((source, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <span className="text-sm text-gray-600 capitalize">{source._id || 'Non défini'}</span>
                        <span className="text-sm font-medium">{source.count}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Recent Activity */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Leads Récents</h3>
                <div className="space-y-3">
                  {dashboardData.recent_leads.slice(0, 5).map((lead) => (
                    <div key={lead.id} className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-900">{lead.name}</p>
                        <p className="text-xs text-gray-500">{lead.email}</p>
                      </div>
                      <div className="text-right">
                        {getStatusBadge(lead.status)}
                        <p className="text-xs text-gray-500 mt-1">
                          Score: <span className={getScoreColor(lead.score)}>{lead.score}</span>
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Automation Status</h3>
                {dashboardData.automation && (
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Emails envoyés</span>
                      <span className="text-sm font-medium">{dashboardData.automation.email_sent || 0}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">SMS envoyés</span>
                      <span className="text-sm font-medium">{dashboardData.automation.sms_sent || 0}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">WhatsApp envoyés</span>
                      <span className="text-sm font-medium">{dashboardData.automation.whatsapp_sent || 0}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Actions programmées</span>
                      <span className="text-sm font-medium text-orange-600">{dashboardData.automation.pending_automations || 0}</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Leads Tab */}
        {activeTab === 'leads' && (
          <div className="mt-6">
            {/* Filters - same as before */}
            <div className="bg-white shadow rounded-lg p-4 mb-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Statut
                  </label>
                  <select
                    value={filters.status}
                    onChange={(e) => setFilters({...filters, status: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Tous les statuts</option>
                    <option value="new">Nouveau</option>
                    <option value="contacted">Contacté</option>
                    <option value="qualified">Qualifié</option>
                    <option value="converted">Converti</option>
                    <option value="lost">Perdu</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Type de Client
                  </label>
                  <select
                    value={filters.customer_type}
                    onChange={(e) => setFilters({...filters, customer_type: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Tous</option>
                    <option value="B2C">Particuliers</option>
                    <option value="B2B">Professionnels</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Actions
                  </label>
                  <button
                    onClick={fetchLeads}
                    className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
                  >
                    Filtrer
                  </button>
                </div>
              </div>
            </div>

            {/* Leads Table - same as before but with enhanced UI */}
            <div className="bg-white shadow rounded-lg overflow-hidden">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-medium text-gray-900">
                    Leads ({leads.length})
                  </h3>
                  <div className="flex space-x-2">
                    <button className="bg-green-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-green-700">
                      Exporter CSV
                    </button>
                    <button className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700">
                      Campagne Email
                    </button>
                  </div>
                </div>
                
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Contact
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Type
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Statut
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Score IA
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Date
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {leads.map((lead) => (
                        <tr key={lead.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div>
                              <div className="text-sm font-medium text-gray-900">
                                {lead.name}
                              </div>
                              <div className="text-sm text-gray-500">{lead.email}</div>
                              {lead.phone && (
                                <div className="text-sm text-gray-500">{lead.phone}</div>
                              )}
                              {lead.company && (
                                <div className="text-xs text-blue-600">{lead.company}</div>
                              )}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                lead.customer_type === 'B2B' ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'
                              }`}>
                                {lead.customer_type === 'B2B' ? '🏢 Pro' : '🏠 Part'}
                              </span>
                              <div className="ml-2 text-xs text-gray-500">
                                {lead.lead_type}
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {getStatusBadge(lead.status)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <span className={`text-lg font-bold ${getScoreColor(lead.score)}`}>
                                {lead.score}
                              </span>
                              <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                                <div 
                                  className={`h-2 rounded-full ${
                                    lead.score >= 80 ? 'bg-green-500' : 
                                    lead.score >= 60 ? 'bg-yellow-500' : 
                                    lead.score >= 40 ? 'bg-orange-500' : 'bg-red-500'
                                  }`}
                                  style={{ width: `${lead.score}%` }}
                                ></div>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {formatDate(lead.created_at)}
                            {lead.follow_up_date && (
                              <div className="text-xs text-orange-600">
                                Relance: {formatDate(lead.follow_up_date)}
                              </div>
                            )}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-y-2">
                            <select
                              value={lead.status}
                              onChange={(e) => updateLeadStatus(lead.id, e.target.value)}
                              className="text-xs border border-gray-300 rounded px-2 py-1"
                            >
                              <option value="new">Nouveau</option>
                              <option value="contacted">Contacté</option>
                              <option value="qualified">Qualifié</option>
                              <option value="converted">Converti</option>
                              <option value="lost">Perdu</option>
                            </select>
                            {lead.consultation_requested && (
                              <div className="text-xs text-green-600">
                                ☎️ Consultation demandée
                              </div>
                            )}
                            <div className="flex space-x-1 mt-2">
                              <button className="text-blue-600 hover:text-blue-800 text-xs">📧</button>
                              <button className="text-green-600 hover:text-green-800 text-xs">📱</button>
                              <button className="text-purple-600 hover:text-purple-800 text-xs">📞</button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Automation Tab */}
        {activeTab === 'automation' && (
          <div className="mt-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
              {/* Email Automation */}
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                  📧 Email Automation
                </h3>
                {automationLogs?.email_logs && (
                  <div className="space-y-3">
                    {automationLogs.email_logs.slice(0, 5).map((log, index) => (
                      <div key={index} className="border-l-4 border-blue-400 pl-3">
                        <div className="text-sm font-medium">{log.subject}</div>
                        <div className="text-xs text-gray-500">
                          À: {log.recipient} | {formatDate(log.sent_at)}
                        </div>
                      </div>
                    ))}
                    <div className="text-center">
                      <span className="text-sm text-gray-500">
                        {automationLogs.email_logs.length} emails envoyés
                      </span>
                    </div>
                  </div>
                )}
              </div>

              {/* SMS Automation */}
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                  📱 SMS Automation
                </h3>
                {automationLogs?.sms_logs && (
                  <div className="space-y-3">
                    {automationLogs.sms_logs.slice(0, 5).map((log, index) => (
                      <div key={index} className="border-l-4 border-green-400 pl-3">
                        <div className="text-sm">{log.message.substring(0, 50)}...</div>
                        <div className="text-xs text-gray-500">
                          À: {log.to_number} | {formatDate(log.sent_at)}
                        </div>
                      </div>
                    ))}
                    <div className="text-center">
                      <span className="text-sm text-gray-500">
                        {automationLogs.sms_logs.length} SMS envoyés
                      </span>
                    </div>
                  </div>
                )}
              </div>

              {/* WhatsApp Automation */}
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                  💬 WhatsApp Automation
                </h3>
                {automationLogs?.whatsapp_logs && (
                  <div className="space-y-3">
                    {automationLogs.whatsapp_logs.slice(0, 5).map((log, index) => (
                      <div key={index} className="border-l-4 border-purple-400 pl-3">
                        <div className="text-sm">{log.message.substring(0, 50)}...</div>
                        <div className="text-xs text-gray-500">
                          À: {log.to_number} | {formatDate(log.sent_at)}
                        </div>
                      </div>
                    ))}
                    <div className="text-center">
                      <span className="text-sm text-gray-500">
                        {automationLogs.whatsapp_logs.length} messages envoyés
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Automation Rules */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Règles d'Automation Active</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h4 className="font-medium text-gray-900">Séquences B2C (Particuliers)</h4>
                  <div className="bg-gray-50 p-4 rounded-lg space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Email de bienvenue</span>
                      <span className="text-green-600 text-xs">Immédiat</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">WhatsApp promo</span>
                      <span className="text-blue-600 text-xs">+1 jour</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Relance panier abandonné</span>
                      <span className="text-orange-600 text-xs">+2 heures</span>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <h4 className="font-medium text-gray-900">Séquences B2B (Professionnels)</h4>
                  <div className="bg-gray-50 p-4 rounded-lg space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Email de bienvenue</span>
                      <span className="text-green-600 text-xs">Immédiat</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">SMS rappel consultation</span>
                      <span className="text-purple-600 text-xs">+1 heure</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Email devis personnalisé</span>
                      <span className="text-blue-600 text-xs">+4 heures</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Orders Tab - Enhanced version */}
        {activeTab === 'orders' && (
          <div className="mt-6">
            <div className="bg-white shadow rounded-lg overflow-hidden">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-medium text-gray-900">
                    Commandes ({orders.length})
                  </h3>
                  <div className="flex space-x-2">
                    <button className="bg-green-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-green-700">
                      Exporter
                    </button>
                  </div>
                </div>
                
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Client
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Articles
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Total
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Statut
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Date
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {orders.map((order) => (
                        <tr key={order.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div>
                              <div className="text-sm font-medium text-gray-900">
                                {order.customer_name}
                              </div>
                              <div className="text-sm text-gray-500">{order.customer_email}</div>
                              {order.customer_type === 'B2B' && (
                                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                                  🏢 Professionnel
                                </span>
                              )}
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <div className="text-sm text-gray-900">
                              {order.items.length} article(s)
                            </div>
                            <div className="text-xs text-gray-500">
                              {order.items.map((item, idx) => (
                                <div key={idx}>
                                  {item.quantity}x {item.product_id}
                                </div>
                              ))}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900">
                              €{order.total}
                            </div>
                            <div className="text-xs text-gray-500">
                              {order.currency}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              order.status === 'paid' ? 'bg-green-100 text-green-800' : 
                              order.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : 
                              'bg-red-100 text-red-800'
                            }`}>
                              {order.status}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {formatDate(order.created_at)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <div className="flex space-x-2">
                              <button className="text-blue-600 hover:text-blue-800">📧</button>
                              <button className="text-green-600 hover:text-green-800">📋</button>
                              <button className="text-purple-600 hover:text-purple-800">🚚</button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Campaigns Tab */}
        {activeTab === 'campaigns' && (
          <div className="mt-6">
            <div className="text-center py-12">
              <div className="text-4xl mb-4">📧</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Campagnes Marketing</h3>
              <p className="text-gray-600 mb-4">
                Créez et gérez vos campagnes email, SMS et WhatsApp automatisées
              </p>
              <button className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors">
                Créer une Campagne 🚀
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CRMDashboard;
      lost: 'Perdu'
    };

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusStyles[status] || 'bg-gray-100 text-gray-800'}`}>
        {statusLabels[status] || status}
      </span>
    );
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600 font-bold';
    if (score >= 60) return 'text-yellow-600 font-semibold';
    if (score >= 40) return 'text-orange-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl mb-4">⏳</div>
          <p className="text-gray-600">Chargement du CRM...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">CRM Josmose 📊</h1>
              <p className="text-gray-600">Gestion des leads et analytics</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-600">
                Dernière mise à jour: {new Date().toLocaleTimeString('fr-FR')}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'dashboard', name: 'Dashboard 📈', icon: '📈' },
              { id: 'leads', name: 'Leads 👥', icon: '👥' },
              { id: 'orders', name: 'Commandes 🛒', icon: '🛒' },
              { id: 'analytics', name: 'Analytics 📊', icon: '📊' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && dashboardData && (
          <div className="mt-6">
            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="text-2xl">👥</div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Total Leads
                        </dt>
                        <dd className="text-lg font-medium text-gray-900">
                          {dashboardData.total_leads}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="text-2xl">🎯</div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Taux de Conversion
                        </dt>
                        <dd className="text-lg font-medium text-gray-900">
                          {dashboardData.conversion_rate}%
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="text-2xl">🛒</div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Commandes Semaine
                        </dt>
                        <dd className="text-lg font-medium text-gray-900">
                          {dashboardData.weekly_orders}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="text-2xl">💰</div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          CA Semaine
                        </dt>
                        <dd className="text-lg font-medium text-gray-900">
                          €{dashboardData.weekly_revenue.toFixed(2)}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              {/* Leads by Status */}
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Leads par Statut</h3>
                <div className="space-y-3">
                  {Object.entries(dashboardData.leads_by_status).map(([status, count]) => (
                    <div key={status} className="flex items-center justify-between">
                      <div className="flex items-center">
                        {getStatusBadge(status)}
                      </div>
                      <span className="text-lg font-medium text-gray-900">{count}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Leads by Type */}
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Leads par Type</h3>
                <div className="space-y-3">
                  {Object.entries(dashboardData.leads_by_type).map(([type, count]) => (
                    <div key={type} className="flex items-center justify-between">
                      <span className="text-sm text-gray-600 capitalize">{type}</span>
                      <span className="text-lg font-medium text-gray-900">{count}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Leads Récents</h3>
                <div className="space-y-3">
                  {dashboardData.recent_leads.slice(0, 5).map((lead) => (
                    <div key={lead.id} className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-900">{lead.name}</p>
                        <p className="text-xs text-gray-500">{lead.email}</p>
                      </div>
                      <div className="text-right">
                        {getStatusBadge(lead.status)}
                        <p className="text-xs text-gray-500 mt-1">
                          Score: <span className={getScoreColor(lead.score)}>{lead.score}</span>
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Commandes Récentes</h3>
                <div className="space-y-3">
                  {dashboardData.recent_orders.slice(0, 5).map((order) => (
                    <div key={order.id} className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-900">{order.customer_name}</p>
                        <p className="text-xs text-gray-500">{formatDate(order.created_at)}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium text-gray-900">€{order.total}</p>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          order.status === 'paid' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {order.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Leads Tab */}
        {activeTab === 'leads' && (
          <div className="mt-6">
            {/* Filters */}
            <div className="bg-white shadow rounded-lg p-4 mb-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Statut
                  </label>
                  <select
                    value={filters.status}
                    onChange={(e) => setFilters({...filters, status: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Tous les statuts</option>
                    <option value="new">Nouveau</option>
                    <option value="contacted">Contacté</option>
                    <option value="qualified">Qualifié</option>
                    <option value="converted">Converti</option>
                    <option value="lost">Perdu</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Type de Client
                  </label>
                  <select
                    value={filters.customer_type}
                    onChange={(e) => setFilters({...filters, customer_type: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Tous</option>
                    <option value="B2C">Particuliers</option>
                    <option value="B2B">Professionnels</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Actions
                  </label>
                  <button
                    onClick={fetchLeads}
                    className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
                  >
                    Filtrer
                  </button>
                </div>
              </div>
            </div>

            {/* Leads Table */}
            <div className="bg-white shadow rounded-lg overflow-hidden">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  Leads ({leads.length})
                </h3>
                
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Contact
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Type
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Statut
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Score
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Date
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {leads.map((lead) => (
                        <tr key={lead.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div>
                              <div className="text-sm font-medium text-gray-900">
                                {lead.name}
                              </div>
                              <div className="text-sm text-gray-500">{lead.email}</div>
                              {lead.phone && (
                                <div className="text-sm text-gray-500">{lead.phone}</div>
                              )}
                              {lead.company && (
                                <div className="text-xs text-blue-600">{lead.company}</div>
                              )}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                lead.customer_type === 'B2B' ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'
                              }`}>
                                {lead.customer_type === 'B2B' ? '🏢 Pro' : '🏠 Part'}
                              </span>
                              <div className="ml-2 text-xs text-gray-500">
                                {lead.lead_type}
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {getStatusBadge(lead.status)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`text-lg font-bold ${getScoreColor(lead.score)}`}>
                              {lead.score}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {formatDate(lead.created_at)}
                            {lead.follow_up_date && (
                              <div className="text-xs text-orange-600">
                                Relance: {formatDate(lead.follow_up_date)}
                              </div>
                            )}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <select
                              value={lead.status}
                              onChange={(e) => updateLeadStatus(lead.id, e.target.value)}
                              className="text-xs border border-gray-300 rounded px-2 py-1"
                            >
                              <option value="new">Nouveau</option>
                              <option value="contacted">Contacté</option>
                              <option value="qualified">Qualifié</option>
                              <option value="converted">Converti</option>
                              <option value="lost">Perdu</option>
                            </select>
                            {lead.consultation_requested && (
                              <div className="text-xs text-green-600 mt-1">
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
          </div>
        )}

        {/* Orders Tab */}
        {activeTab === 'orders' && (
          <div className="mt-6">
            <div className="bg-white shadow rounded-lg overflow-hidden">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  Commandes ({orders.length})
                </h3>
                
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Client
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Articles
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Total
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Statut
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Date
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {orders.map((order) => (
                        <tr key={order.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div>
                              <div className="text-sm font-medium text-gray-900">
                                {order.customer_name}
                              </div>
                              <div className="text-sm text-gray-500">{order.customer_email}</div>
                              {order.customer_type === 'B2B' && (
                                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                                  🏢 Professionnel
                                </span>
                              )}
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <div className="text-sm text-gray-900">
                              {order.items.length} article(s)
                            </div>
                            <div className="text-xs text-gray-500">
                              {order.items.map((item, idx) => (
                                <div key={idx}>
                                  {item.quantity}x {item.product_id}
                                </div>
                              ))}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900">
                              €{order.total}
                            </div>
                            <div className="text-xs text-gray-500">
                              {order.currency}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              order.status === 'paid' ? 'bg-green-100 text-green-800' : 
                              order.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : 
                              'bg-red-100 text-red-800'
                            }`}>
                              {order.status}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {formatDate(order.created_at)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="mt-6">
            <div className="text-center py-12">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Analytics Avancées</h3>
              <p className="text-gray-600">
                Fonctionnalité en développement - Graphiques détaillés et rapports personnalisés à venir
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CRMDashboard;