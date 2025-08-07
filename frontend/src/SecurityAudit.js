import React, { useState, useEffect } from 'react';
import axios from 'axios';

const SecurityAudit = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [securityThreats, setSecurityThreats] = useState([]);
  const [auditHistory, setAuditHistory] = useState([]);
  const [blockedIps, setBlockedIps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeSection, setActiveSection] = useState('dashboard');

  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  const loadAllSecurityData = async () => {
    try {
      setLoading(true);
      
      const token = localStorage.getItem('token');
      const config = {
        headers: { Authorization: `Bearer ${token}` }
      };

      // Charger toutes les données en parallèle
      const [dashboardRes, threatsRes, auditsRes, blockedIpsRes] = await Promise.all([
        axios.get(`${backendUrl}/api/crm/security/dashboard`, config),
        axios.get(`${backendUrl}/api/crm/security/threats`, config),
        axios.get(`${backendUrl}/api/crm/security/audits`, config),
        axios.get(`${backendUrl}/api/crm/security/blocked-ips`, config)
      ]);

      setDashboardData(dashboardRes.data);
      setSecurityThreats(threatsRes.data.threats || []);
      setAuditHistory(auditsRes.data.audits || []);
      setBlockedIps(blockedIpsRes.data.blocked_ips || []);
      
    } catch (error) {
      console.error('Erreur chargement données sécurité:', error);
    } finally {
      setLoading(false);
    }
  };

  const triggerManualAudit = async () => {
    try {
      const token = localStorage.getItem('token');
      const config = {
        headers: { Authorization: `Bearer ${token}` }
      };

      const response = await axios.post(`${backendUrl}/api/crm/security/manual-audit`, {}, config);
      
      if (response.data.success) {
        alert(`Audit manuel réussi!\nScore: ${response.data.overall_score}/100\nBugs corrigés: ${response.data.bugs_fixed}`);
        await loadAllSecurityData(); // Recharger les données
      }
      
    } catch (error) {
      console.error('Erreur audit manuel:', error);
      alert('Erreur lors de l\'audit manuel');
    }
  };

  const unblockIp = async (ip) => {
    try {
      const token = localStorage.getItem('token');
      const config = {
        headers: { Authorization: `Bearer ${token}` }
      };

      const response = await axios.post(`${backendUrl}/api/crm/security/unblock-ip`, { ip }, config);
      
      if (response.data.success) {
        alert(`IP ${ip} débloquée avec succès!`);
        await loadAllSecurityData(); // Recharger les données
      }
      
    } catch (error) {
      console.error('Erreur déblocage IP:', error);
      alert('Erreur lors du déblocage de l\'IP');
    }
  };

  const getSeverityColor = (severity) => {
    switch(severity) {
      case 'CRITICAL': return 'text-red-800 bg-red-100 border-red-500';
      case 'HIGH': return 'text-orange-800 bg-orange-100 border-orange-500';
      case 'MEDIUM': return 'text-yellow-800 bg-yellow-100 border-yellow-500';
      case 'LOW': return 'text-green-800 bg-green-100 border-green-500';
      default: return 'text-gray-800 bg-gray-100 border-gray-500';
    }
  };

  const getThreatLevelIcon = (level) => {
    switch(level) {
      case 'CRITICAL': return '🚨';
      case 'HIGH': return '⚠️';
      case 'MEDIUM': return '🟡';
      case 'LOW': return '🟢';
      default: return '❓';
    }
  };

  const getSystemHealthColor = (health) => {
    switch(health) {
      case 'GOOD': return 'text-green-800 bg-green-100';
      case 'WARNING': return 'text-yellow-800 bg-yellow-100';
      case 'AT_RISK': return 'text-orange-800 bg-orange-100';
      case 'CRITICAL': return 'text-red-800 bg-red-100';
      default: return 'text-gray-800 bg-gray-100';
    }
  };

  useEffect(() => {
    loadAllSecurityData();
    
    // Auto-refresh toutes les 30 secondes
    const interval = setInterval(loadAllSecurityData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement du système de sécurité...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center">
            🛡️ Agent Audit & Cybersécurité 24/7
            {dashboardData?.agent_status === 'ACTIVE' && (
              <span className="ml-3 px-3 py-1 text-sm bg-green-100 text-green-800 rounded-full animate-pulse">
                🟢 ACTIF 24/7
              </span>
            )}
          </h2>
          <p className="text-gray-600">
            Surveillance continue, détection de menaces et audit automatique du système
          </p>
        </div>
        
        <div className="flex space-x-3">
          <button
            onClick={triggerManualAudit}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center"
          >
            🔍 Audit Manuel
          </button>
          <button
            onClick={loadAllSecurityData}
            className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700"
          >
            🔄 Actualiser
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-lg">
        {[
          { id: 'dashboard', name: 'Dashboard', icon: '📊' },
          { id: 'threats', name: 'Menaces', icon: '🚨' },
          { id: 'audits', name: 'Audits', icon: '🔍' },
          { id: 'blocked', name: 'IPs Bloquées', icon: '🚫' }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveSection(tab.id)}
            className={`flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeSection === tab.id
                ? 'bg-white text-red-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <span className="mr-2">{tab.icon}</span>
            {tab.name}
          </button>
        ))}
      </div>

      {/* Dashboard Section */}
      {activeSection === 'dashboard' && dashboardData && (
        <div>
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-red-500">
              <div className="flex items-center">
                <div className="text-3xl text-red-600">🚨</div>
                <div className="ml-4">
                  <h3 className="text-lg font-semibold text-gray-700">Menaces Actives</h3>
                  <div className="text-3xl font-bold text-red-600">{dashboardData.active_threats}</div>
                  <div className="text-sm text-gray-500">Dernières 24h</div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-orange-500">
              <div className="flex items-center">
                <div className="text-3xl text-orange-600">🛡️</div>
                <div className="ml-4">
                  <h3 className="text-lg font-semibold text-gray-700">Attaques Bloquées</h3>
                  <div className="text-3xl font-bold text-orange-600">{dashboardData.stats?.attacks_prevented || 0}</div>
                  <div className="text-sm text-gray-500">Total depuis démarrage</div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
              <div className="flex items-center">
                <div className="text-3xl text-blue-600">🔧</div>
                <div className="ml-4">
                  <h3 className="text-lg font-semibold text-gray-700">Bugs Corrigés</h3>
                  <div className="text-3xl font-bold text-blue-600">{dashboardData.stats?.bugs_fixed || 0}</div>
                  <div className="text-sm text-gray-500">Corrections automatiques</div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-purple-500">
              <div className="flex items-center">
                <div className="text-3xl text-purple-600">⏱️</div>
                <div className="ml-4">
                  <h3 className="text-lg font-semibold text-gray-700">Uptime Agent</h3>
                  <div className="text-3xl font-bold text-purple-600">{Math.floor(dashboardData.uptime_minutes / 60)}h</div>
                  <div className="text-sm text-gray-500">{dashboardData.uptime_minutes % 60}min actif</div>
                </div>
              </div>
            </div>
          </div>

          {/* System Health */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                📈 État du Système
                <span className={`ml-3 px-2 py-1 rounded-full text-sm ${getSystemHealthColor(dashboardData.system_health)}`}>
                  {dashboardData.system_health}
                </span>
              </h3>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-gray-700">Niveau de Menace</span>
                  <span className="flex items-center">
                    {getThreatLevelIcon(dashboardData.threat_level)}
                    <span className={`ml-2 px-2 py-1 rounded text-sm ${getSeverityColor(dashboardData.threat_level)}`}>
                      {dashboardData.threat_level}
                    </span>
                  </span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-gray-700">IPs Bloquées</span>
                  <span className="font-semibold text-red-600">{dashboardData.blocked_ips_count}</span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-gray-700">Agent Status</span>
                  <span className={`px-2 py-1 rounded text-sm ${
                    dashboardData.agent_status === 'ACTIVE' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {dashboardData.agent_status}
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">📋 Dernier Audit</h3>
              
              {dashboardData.last_audit ? (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-700">Date</span>
                    <span className="font-semibold">
                      {new Date(dashboardData.last_audit.date).toLocaleDateString('fr-FR')}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-gray-700">Score Global</span>
                    <span className={`font-bold text-lg ${
                      dashboardData.last_audit.score >= 90 ? 'text-green-600' :
                      dashboardData.last_audit.score >= 70 ? 'text-yellow-600' : 'text-red-600'
                    }`}>
                      {dashboardData.last_audit.score}/100
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-gray-700">Problèmes Détectés</span>
                    <span className="font-semibold text-orange-600">{dashboardData.last_audit.issues}</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-gray-700">Bugs Corrigés</span>
                    <span className="font-semibold text-blue-600">{dashboardData.last_audit.bugs_fixed}</span>
                  </div>
                </div>
              ) : (
                <div className="text-center py-6 text-gray-500">
                  Aucun audit effectué récemment
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Threats Section */}
      {activeSection === 'threats' && (
        <div className="bg-white rounded-lg shadow-md">
          <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              🚨 Menaces de Sécurité (24h)
              {securityThreats.length > 0 && (
                <span className="ml-2 bg-red-100 text-red-800 px-2 py-1 rounded-full text-sm">
                  {securityThreats.length} détectée{securityThreats.length > 1 ? 's' : ''}
                </span>
              )}
            </h3>
          </div>

          {securityThreats.length === 0 ? (
            <div className="p-8 text-center">
              <div className="text-6xl mb-4">🛡️</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Système sécurisé!</h3>
              <p className="text-gray-600">Aucune menace détectée dans les dernières 24 heures.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sévérité</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">IP Source</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Détectée le</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {securityThreats.map((threat, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm font-medium text-gray-900">
                          {threat.threat_type || 'Unknown'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full border ${getSeverityColor(threat.severity)}`}>
                          {threat.severity}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {threat.source_ip || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(threat.detected_at).toLocaleString('fr-FR')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                          threat.status === 'MITIGATED' ? 'bg-green-100 text-green-800' :
                          threat.status === 'BLOCKED' ? 'bg-red-100 text-red-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {threat.auto_fixed ? '🤖 Auto-corrigé' : threat.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                        {threat.description || 'Aucune description'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Audits Section */}
      {activeSection === 'audits' && (
        <div className="bg-white rounded-lg shadow-md">
          <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">🔍 Historique des Audits</h3>
          </div>

          {auditHistory.length === 0 ? (
            <div className="p-8 text-center">
              <div className="text-6xl mb-4">📋</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Aucun audit disponible</h3>
              <p className="text-gray-600">Les audits automatiques démarrent à minuit.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID Audit</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Score</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Bugs Détectés</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Bugs Corrigés</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Problèmes Sécurité</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {auditHistory.map((audit, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {audit.audit_id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(audit.audit_date).toLocaleString('fr-FR')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-sm font-bold rounded ${
                          audit.overall_score >= 90 ? 'bg-green-100 text-green-800' :
                          audit.overall_score >= 70 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {audit.overall_score}/100
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {audit.bugs_detected?.length || 0}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 font-semibold">
                        {audit.bugs_fixed?.length || 0}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600 font-semibold">
                        {audit.security_issues?.length || 0}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Blocked IPs Section */}
      {activeSection === 'blocked' && (
        <div className="bg-white rounded-lg shadow-md">
          <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              🚫 Adresses IP Bloquées
              {blockedIps.length > 0 && (
                <span className="ml-2 bg-red-100 text-red-800 px-2 py-1 rounded-full text-sm">
                  {blockedIps.length} active{blockedIps.length > 1 ? 's' : ''}
                </span>
              )}
            </h3>
          </div>

          {blockedIps.length === 0 ? (
            <div className="p-8 text-center">
              <div className="text-6xl mb-4">🟢</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Aucune IP bloquée!</h3>
              <p className="text-gray-600">Système ouvert, aucune restriction active.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Adresse IP</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Raison</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Bloquée le</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Expire le</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {blockedIps.map((ipRecord, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <code className="bg-gray-100 px-2 py-1 rounded text-sm font-mono">
                          {ipRecord.ip}
                        </code>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                          ipRecord.reason === 'brute_force' ? 'bg-red-100 text-red-800' :
                          ipRecord.reason === 'malicious_payload' ? 'bg-orange-100 text-orange-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {ipRecord.reason}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(ipRecord.blocked_at).toLocaleString('fr-FR')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(ipRecord.expires_at).toLocaleString('fr-FR')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button
                          onClick={() => unblockIp(ipRecord.ip)}
                          className="text-green-600 hover:text-green-900 bg-green-100 px-3 py-1 rounded"
                        >
                          🔓 Débloquer
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Alert Info */}
      <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
        <h4 className="font-semibold text-red-900 mb-2">🤖 Agent de Sécurité 24/7 - Fonctionnalités</h4>
        <div className="text-sm text-red-800 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <strong>🔍 Surveillance Continue:</strong><br/>
            • Détection temps réel des menaces<br/>
            • Analyse des logs système<br/>
            • Monitoring des ressources
          </div>
          <div>
            <strong>🛡️ Protection Automatique:</strong><br/>
            • Blocage automatique des IPs malveillantes<br/>
            • Correction automatique des bugs<br/>
            • Mitigation des attaques DDoS
          </div>
          <div>
            <strong>📅 Audit Quotidien:</strong><br/>
            • Chaque jour à minuit (heure française)<br/>
            • Rapport de sécurité complet<br/>
            • Score de santé système
          </div>
          <div>
            <strong>🚨 Alertes Critiques:</strong><br/>
            • Notification immédiate<br/>
            • Actions de mitigation automatiques<br/>
            • Historique complet des incidents
          </div>
        </div>
      </div>
    </div>
  );
};

export default SecurityAudit;