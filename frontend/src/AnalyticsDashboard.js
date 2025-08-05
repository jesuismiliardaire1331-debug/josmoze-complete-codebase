import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const AnalyticsDashboard = ({ userRole, userToken }) => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dateRange, setDateRange] = useState(30);
  const [securityStats, setSecurityStats] = useState(null);

  useEffect(() => {
    if (userToken && (userRole === 'manager' || userRole === 'agent')) {
      fetchAnalyticsData();
    }
    if (userToken && (userRole === 'manager' || userRole === 'technique')) {
      fetchSecurityStats();
    }
  }, [userToken, userRole, dateRange]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        `${BACKEND_URL}/api/crm/analytics/dashboard?date_range=${dateRange}`,
        {
          headers: { Authorization: `Bearer ${userToken}` }
        }
      );
      
      if (response.data.success) {
        setAnalyticsData(response.data.data);
      } else {
        setError('Erreur lors du chargement des analytics');
      }
    } catch (err) {
      console.error('Analytics fetch error:', err);
      setError(`Erreur: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const fetchSecurityStats = async () => {
    try {
      const response = await axios.get(
        `${BACKEND_URL}/api/crm/security/stats`,
        {
          headers: { Authorization: `Bearer ${userToken}` }
        }
      );
      
      if (response.data.success) {
        setSecurityStats(response.data.security_stats);
      }
    } catch (err) {
      console.error('Security stats fetch error:', err);
    }
  };

  const exportCSV = async () => {
    if (userRole !== 'manager') {
      alert('Seuls les Managers peuvent exporter les données');
      return;
    }

    try {
      const response = await axios.get(
        `${BACKEND_URL}/api/crm/analytics/export/csv?date_range=${dateRange}`,
        {
          headers: { Authorization: `Bearer ${userToken}` },
          responseType: 'blob'
        }
      );
      
      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `josmose_analytics_${dateRange}days.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      alert(`Erreur export: ${err.response?.data?.detail || err.message}`);
    }
  };

  const clearCache = async () => {
    if (userRole !== 'manager') {
      alert('Seuls les Managers peuvent vider le cache');
      return;
    }

    if (!confirm('Êtes-vous sûr de vouloir vider le cache système ?')) {
      return;
    }

    try {
      await axios.post(
        `${BACKEND_URL}/api/crm/cache/clear`,
        { pattern: '*' },
        {
          headers: { Authorization: `Bearer ${userToken}` }
        }
      );
      
      alert('Cache vidé avec succès');
    } catch (err) {
      alert(`Erreur cache: ${err.response?.data?.detail || err.message}`);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <span className="ml-4 text-lg">Chargement des analytics...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center">
          <span className="text-2xl mr-3">❌</span>
          <div>
            <h3 className="text-lg font-semibold text-red-900">Erreur Analytics</h3>
            <p className="text-red-700">{error}</p>
            <button 
              onClick={fetchAnalyticsData}
              className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Réessayer
            </button>
          </div>
        </div>
      </div>
    );
  }

  const canViewAnalytics = userRole === 'manager' || userRole === 'agent';
  const canManage = userRole === 'manager';
  const canViewSecurity = userRole === 'manager' || userRole === 'technique';

  return (
    <div className="space-y-6">
      {/* Header Controls */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">📊 Analytics & Business Intelligence</h2>
            <p className="text-gray-600">Tableau de bord analytique avancé - Rôle: {userRole}</p>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-3">
            <select
              value={dateRange}
              onChange={(e) => setDateRange(Number(e.target.value))}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value={7}>7 derniers jours</option>
              <option value={30}>30 derniers jours</option>
              <option value={90}>90 derniers jours</option>
            </select>
            
            {canManage && (
              <>
                <button
                  onClick={exportCSV}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center"
                >
                  📥 Export CSV
                </button>
                
                <button
                  onClick={clearCache}
                  className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 flex items-center"
                >
                  🗑️ Vider Cache
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Sales Analytics */}
      {canViewAnalytics && analyticsData && (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-4 gap-6">
          <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100">Chiffre d'Affaires</p>
                <p className="text-2xl font-bold">
                  {analyticsData.sales_analytics?.summary?.total_revenue?.toFixed(2) || 0}€
                </p>
              </div>
              <div className="text-3xl">💰</div>
            </div>
            <div className="mt-2 text-sm text-blue-100">
              Croissance: {analyticsData.sales_analytics?.summary?.revenue_growth_percent?.toFixed(1) || 0}%
            </div>
          </div>

          <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-100">Commandes Totales</p>
                <p className="text-2xl font-bold">
                  {analyticsData.sales_analytics?.summary?.total_orders || 0}
                </p>
              </div>
              <div className="text-3xl">🛒</div>
            </div>
            <div className="mt-2 text-sm text-green-100">
              Panier moyen: {analyticsData.sales_analytics?.summary?.avg_order_value?.toFixed(2) || 0}€
            </div>
          </div>

          <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100">Leads Totaux</p>
                <p className="text-2xl font-bold">
                  {analyticsData.customer_analytics?.summary?.total_leads || 0}
                </p>
              </div>
              <div className="text-3xl">👥</div>
            </div>
            <div className="mt-2 text-sm text-purple-100">
              Rétention: {analyticsData.customer_analytics?.summary?.retention_rate?.toFixed(1) || 0}%
            </div>
          </div>

          <div className="bg-gradient-to-r from-orange-500 to-orange-600 rounded-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-100">Taux de Conversion</p>
                <p className="text-2xl font-bold">
                  {analyticsData.conversion_funnel?.conversion_rates?.overall?.toFixed(1) || 0}%
                </p>
              </div>
              <div className="text-3xl">📈</div>
            </div>
            <div className="mt-2 text-sm text-orange-100">
              Funnel global
            </div>
          </div>
        </div>
      )}

      {/* Customer Segmentation */}
      {canViewAnalytics && analyticsData?.customer_analytics && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">👥 Segmentation Clients</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold text-gray-800 mb-2">Par Type</h4>
              <div className="space-y-2">
                <div className="flex justify-between items-center p-3 bg-blue-50 rounded">
                  <span>B2B Leads</span>
                  <span className="font-bold text-blue-600">
                    {analyticsData.customer_analytics.summary.b2b_leads || 0}
                  </span>
                </div>
                <div className="flex justify-between items-center p-3 bg-green-50 rounded">
                  <span>B2C Leads</span>
                  <span className="font-bold text-green-600">
                    {analyticsData.customer_analytics.summary.b2c_leads || 0}
                  </span>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-semibold text-gray-800 mb-2">Valeur Client</h4>
              <div className="text-lg font-semibold text-gray-900">
                Valeur moyenne: {analyticsData.customer_analytics.summary.avg_customer_value?.toFixed(2) || 0}€
              </div>
              <div className="text-sm text-gray-600 mt-1">
                Clients récurrents: {analyticsData.customer_analytics.summary.repeat_customers || 0}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Security Statistics */}
      {canViewSecurity && securityStats && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">🛡️ Statistiques de Sécurité</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-4 bg-red-50 rounded-lg">
              <div className="text-2xl font-bold text-red-600">
                {securityStats.blocked_ips_count || 0}
              </div>
              <div className="text-sm text-red-800">IPs Bloquées</div>
            </div>
            
            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <div className="text-2xl font-bold text-yellow-600">
                {securityStats.security_events_24h || 0}
              </div>
              <div className="text-sm text-yellow-800">Événements 24h</div>
            </div>
            
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {securityStats.slow_requests_24h || 0}
              </div>
              <div className="text-sm text-blue-800">Requêtes Lentes 24h</div>
            </div>
          </div>
          
          <div className="mt-4 flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${securityStats.redis_available ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="text-sm text-gray-600">
              Redis: {securityStats.redis_available ? 'Connecté' : 'Déconnecté'}
            </span>
          </div>
        </div>
      )}

      {/* Recommendations */}
      {canViewAnalytics && analyticsData?.recommendations && analyticsData.recommendations.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">💡 Recommandations</h3>
          <div className="space-y-3">
            {analyticsData.recommendations.map((rec, index) => (
              <div key={index} className={`p-4 rounded-lg border-l-4 ${
                rec.priority === 'high' ? 'bg-red-50 border-red-500' :
                rec.priority === 'medium' ? 'bg-yellow-50 border-yellow-500' :
                'bg-blue-50 border-blue-500'
              }`}>
                <div className="flex items-start">
                  <span className="text-xl mr-3">
                    {rec.type === 'warning' ? '⚠️' : 
                     rec.type === 'improvement' ? '📈' : '💡'}
                  </span>
                  <div>
                    <h4 className="font-semibold text-gray-900">{rec.title}</h4>
                    <p className="text-gray-700 text-sm mt-1">{rec.description}</p>
                    <span className={`text-xs px-2 py-1 rounded mt-2 inline-block ${
                      rec.priority === 'high' ? 'bg-red-100 text-red-800' :
                      rec.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      Priorité {rec.priority}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Access Denied Message */}
      {!canViewAnalytics && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <span className="text-4xl mb-4 block">🔒</span>
          <h3 className="text-lg font-semibold text-yellow-900">Accès Limité</h3>
          <p className="text-yellow-700 mt-2">
            Votre rôle ({userRole}) ne permet pas d'accéder aux analytics avancés.
            {userRole === 'technique' && ' Vous avez accès aux statistiques de sécurité uniquement.'}
          </p>
        </div>
      )}
    </div>
  );
};

export default AnalyticsDashboard;