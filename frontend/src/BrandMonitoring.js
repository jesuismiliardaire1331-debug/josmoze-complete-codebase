import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BrandMonitoring = () => {
  const [monitoringStatus, setMonitoringStatus] = useState(null);
  const [violations, setViolations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [scanResults, setScanResults] = useState(null);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    loadMonitoringData();
    
    // Rafraîchir toutes les 30 secondes
    const interval = setInterval(loadMonitoringData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadMonitoringData = async () => {
    try {
      const token = localStorage.getItem('token');
      const config = {
        headers: { Authorization: `Bearer ${token}` }
      };

      // Charger le statut et les violations récentes
      const [statusResponse, violationsResponse] = await Promise.all([
        axios.get(`${backendUrl}/api/crm/brand-monitoring/status`, config),
        axios.get(`${backendUrl}/api/crm/brand-monitoring/violations`, config)
      ]);

      setMonitoringStatus(statusResponse.data);
      setViolations(violationsResponse.data.recent_violations || []);
      
    } catch (error) {
      console.error('Erreur chargement surveillance:', error);
    }
  };

  const startMonitoring = async () => {
    try {
      setLoading(true);
      
      const token = localStorage.getItem('token');
      const config = {
        headers: { Authorization: `Bearer ${token}` }
      };

      const response = await axios.post(`${backendUrl}/api/crm/brand-monitoring/start`, {}, config);
      
      alert('Agent de surveillance démarré avec succès !');
      loadMonitoringData(); // Recharger les données
      
    } catch (error) {
      console.error('Erreur démarrage surveillance:', error);
      alert('Erreur lors du démarrage de l\'agent');
    } finally {
      setLoading(false);
    }
  };

  const forceScan = async () => {
    try {
      setLoading(true);
      
      const token = localStorage.getItem('token');
      const config = {
        headers: { Authorization: `Bearer ${token}` }
      };

      const response = await axios.post(`${backendUrl}/api/crm/brand-monitoring/force-scan`, {}, config);
      
      setScanResults(response.data);
      await loadMonitoringData(); // Recharger les données
      
    } catch (error) {
      console.error('Erreur scan forcé:', error);
      alert('Erreur lors du scan forcé');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('fr-FR');
  };

  const getStatusIcon = (status) => {
    switch(status) {
      case 'RUNNING': return '🟢';
      case 'STOPPED': return '🔴';
      case 'CLEAN': return '✅';
      case 'VIOLATIONS_DETECTED': return '⚠️';
      default: return '❓';
    }
  };

  const getViolationSeverity = (violationCount) => {
    if (violationCount === 0) return { color: 'text-green-600', bg: 'bg-green-50' };
    if (violationCount <= 5) return { color: 'text-yellow-600', bg: 'bg-yellow-50' };
    return { color: 'text-red-600', bg: 'bg-red-50' };
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          🛡️ Surveillance Marque JOSMOZE.COM - MODE RENFORCÉ ⚡
        </h2>
        <p className="text-gray-600">
          Agent de surveillance HAUTE INTENSITÉ 24/7 qui vérifie <strong>toutes les 30 secondes</strong> 
          que toute mention "emergent" est supprimée et que le site reste www.josmoze.com
        </p>
        <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 text-sm">
            🚨 <strong>MODE SURVEILLANCE RENFORCÉE ACTIVÉ</strong> - Alerte immédiate dès détection
          </p>
        </div>
      </div>

      {/* Statut général */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow-md p-4 text-center">
          <div className="text-3xl mb-2">
            {monitoringStatus ? getStatusIcon(monitoringStatus.status) : '⏳'}
          </div>
          <div className="font-semibold text-gray-900">
            {monitoringStatus?.status || 'CHARGEMENT'}
          </div>
          <div className="text-sm text-gray-600">Statut Agent</div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-4 text-center">
          <div className="text-2xl font-bold text-blue-600">
            {monitoringStatus?.total_scans || 0}
          </div>
          <div className="text-sm text-gray-600">Total Scans</div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-4 text-center">
          <div className="text-2xl font-bold text-green-600">
            {monitoringStatus?.clean_scans || 0}
          </div>
          <div className="text-sm text-gray-600">Scans Propres</div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-4 text-center">
          <div className="text-2xl font-bold text-red-600">
            {monitoringStatus?.violation_scans || 0}
          </div>
          <div className="text-sm text-gray-600">Violations Détectées</div>
        </div>
      </div>

      {/* Dernier scan */}
      {monitoringStatus?.last_scan && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 Dernier Scan Effectué</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <div className="text-sm text-gray-600">Heure du scan</div>
              <div className="font-medium">{formatDate(monitoringStatus.last_scan.scan_time)}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Durée</div>
              <div className="font-medium">{monitoringStatus.last_scan.duration_seconds?.toFixed(2)}s</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Résultat</div>
              <div className={`font-medium ${getViolationSeverity(monitoringStatus.last_scan.violations_found).color}`}>
                {getStatusIcon(monitoringStatus.last_scan.status)} {monitoringStatus.last_scan.status}
              </div>
            </div>
          </div>

          {monitoringStatus.last_scan.violations_found > 0 && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <h4 className="font-semibold text-red-800 mb-2">
                ⚠️ {monitoringStatus.last_scan.violations_found} Violations Détectées !
              </h4>
              <div className="space-y-2">
                {monitoringStatus.last_scan.violations?.slice(0, 3).map((violation, index) => (
                  <div key={index} className="text-sm">
                    <span className="font-medium text-red-700">"{violation.term}"</span> 
                    {' '}trouvé dans{' '}
                    <code className="bg-red-100 px-1 rounded">{violation.file || violation.url}</code>
                  </div>
                ))}
                {monitoringStatus.last_scan.violations_found > 3 && (
                  <div className="text-sm text-red-600">
                    ... et {monitoringStatus.last_scan.violations_found - 3} autres violations
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🎛️ Actions de Surveillance</h3>
        
        <div className="flex flex-wrap space-x-4 space-y-2 md:space-y-0">
          <button
            onClick={startMonitoring}
            disabled={loading || monitoringStatus?.status === 'RUNNING'}
            className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            {monitoringStatus?.status === 'RUNNING' ? '✅ Agent Actif' : '🚀 Démarrer Agent'}
          </button>
          
          <button
            onClick={forceScan}
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? '⏳ Scan en cours...' : '🔍 Scanner Maintenant'}
          </button>
          
          <button
            onClick={loadMonitoringData}
            className="bg-gray-600 text-white px-6 py-2 rounded-lg hover:bg-gray-700"
          >
            🔄 Actualiser
          </button>
        </div>
      </div>

      {/* Résultats du scan forcé */}
      {scanResults && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            🔍 Résultats du Scan Forcé
          </h3>
          
          <div className={`p-4 rounded-lg ${getViolationSeverity(scanResults.violations_found).bg}`}>
            <div className={`font-semibold ${getViolationSeverity(scanResults.violations_found).color}`}>
              {getStatusIcon(scanResults.status)} {scanResults.status}
            </div>
            <div className="text-sm mt-1">
              {scanResults.violations_found} violations trouvées en {scanResults.duration_seconds?.toFixed(2)} secondes
            </div>
            
            {scanResults.violations && scanResults.violations.length > 0 && (
              <div className="mt-3 space-y-2">
                {scanResults.violations.map((violation, index) => (
                  <div key={index} className="bg-white p-2 rounded border">
                    <div className="font-medium text-red-800">"{violation.term}"</div>
                    <div className="text-sm text-gray-600">
                      Fichier: <code>{violation.file || violation.url}</code>
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      Contexte: {violation.context?.substring(0, 100)}...
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Historique des violations */}
      {violations.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            📋 Historique des Violations
          </h3>
          
          <div className="space-y-3">
            {violations.map((violation, index) => (
              <div key={index} className="border border-red-200 rounded-lg p-4 bg-red-50">
                <div className="flex justify-between items-start">
                  <div>
                    <div className="font-semibold text-red-800">
                      {violation.violations_found} violations détectées
                    </div>
                    <div className="text-sm text-gray-600">
                      {formatDate(violation.scan_time)}
                    </div>
                  </div>
                  <div className="text-red-600 font-bold">
                    ⚠️
                  </div>
                </div>
                
                <div className="mt-2 text-sm space-y-1">
                  {violation.violations?.slice(0, 2).map((v, i) => (
                    <div key={i}>
                      • <span className="font-medium">"{v.term}"</span> dans{' '}
                      <code className="bg-red-100 px-1 rounded text-xs">
                        {v.file || v.url}
                      </code>
                    </div>
                  ))}
                  {violation.violations_found > 2 && (
                    <div className="text-gray-600">
                      ... et {violation.violations_found - 2} autres
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Configuration de surveillance */}
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 mt-6">
        <h3 className="font-semibold text-red-900 mb-2">🚨 Configuration Agent - MODE RENFORCÉ</h3>
        <div className="text-sm text-red-800 grid grid-cols-1 md:grid-cols-2 gap-2">
          <div>• Vérification : <strong>Toutes les 30 SECONDES ⚡</strong></div>
          <div>• Surveillance : <strong>emergent, made with emergent, powered by emergent</strong></div>
          <div>• Scan renforcé : <strong>.js, .py, .html, .css, .json, métadonnées</strong></div>
          <div>• Domaine surveillé : <strong>www.josmoze.com UNIQUEMENT</strong></div>
          <div>• Mode alerte : <strong>IMMÉDIATE (dès 1ère détection)</strong></div>
          <div>• URLs surveillées : <strong>5 points de contrôle web</strong></div>
        </div>
      </div>
    </div>
  );
};

export default BrandMonitoring;