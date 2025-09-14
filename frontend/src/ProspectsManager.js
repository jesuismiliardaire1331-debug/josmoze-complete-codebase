import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ProspectsManager = () => {
  const [prospects, setProspects] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [showBulkImport, setShowBulkImport] = useState(false);
  const [filters, setFilters] = useState({
    status: '',
    consent_status: '',
    country: 'FR'
  });

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    loadProspects();
    loadStats();
  }, [filters]);

  const loadProspects = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (filters.status) params.append('status', filters.status);
      if (filters.consent_status) params.append('consent_status', filters.consent_status);
      if (filters.country) params.append('country', filters.country);

      const response = await axios.get(`${backendUrl}/api/prospects?${params}`);
      setProspects(response.data);
    } catch (error) {
      console.error('Erreur chargement prospects:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await axios.get(`${backendUrl}/api/prospects/stats/overview`);
      setStats(response.data);
    } catch (error) {
      console.error('Erreur chargement stats:', error);
    }
  };

  const deleteProspect = async (prospectId) => {
    if (!window.confirm('⚠️ ATTENTION: Cette action est irréversible (droit à l\'oubli GDPR). Confirmer la suppression ?')) {
      return;
    }

    try {
      await axios.delete(`${backendUrl}/api/prospects/${prospectId}`);
      await loadProspects();
      await loadStats();
      alert('✅ Prospect supprimé avec succès');
    } catch (error) {
      console.error('Erreur suppression:', error);
      alert('❌ Erreur lors de la suppression');
    }
  };

  const updateProspectStatus = async (prospectId, newStatus) => {
    try {
      await axios.put(`${backendUrl}/api/prospects/${prospectId}`, {
        status: newStatus
      });
      await loadProspects();
      await loadStats();
    } catch (error) {
      console.error('Erreur mise à jour statut:', error);
    }
  };

  const cleanupExpired = async () => {
    if (!window.confirm('Nettoyer les prospects expirés (conformité GDPR) ?')) {
      return;
    }

    try {
      const response = await axios.post(`${backendUrl}/api/prospects/cleanup/expired`);
      alert(`✅ ${response.data.deleted_count} prospects expirés supprimés`);
      await loadProspects();
      await loadStats();
    } catch (error) {
      console.error('Erreur nettoyage:', error);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      new: 'bg-blue-100 text-blue-800',
      contacted: 'bg-yellow-100 text-yellow-800',
      engaged: 'bg-purple-100 text-purple-800',
      qualified: 'bg-green-100 text-green-800',
      converted: 'bg-emerald-100 text-emerald-800',
      unsubscribed: 'bg-red-100 text-red-800',
      bounced: 'bg-gray-100 text-gray-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getConsentColor = (consent) => {
    const colors = {
      b2b_optout_allowed: 'bg-blue-100 text-blue-600',
      b2c_optin_required: 'bg-yellow-100 text-yellow-600',
      b2c_optin_confirmed: 'bg-green-100 text-green-600',
      legitimate_interest: 'bg-purple-100 text-purple-600',
      withdrawn: 'bg-red-100 text-red-600',
      expired: 'bg-gray-100 text-gray-600'
    };
    return colors[consent] || 'bg-gray-100 text-gray-600';
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">📋 Gestion Prospects</h1>
          <p className="text-gray-600 mt-2">Base de données conforme CNIL/GDPR</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowBulkImport(true)}
            className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg font-medium"
          >
            📥 Import en lot
          </button>
          <button
            onClick={() => setShowAddForm(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium"
          >
            ➕ Ajouter Prospect
          </button>
        </div>
      </div>

      {/* Statistiques */}
      {stats.prospects_stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-md border">
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 rounded-full">
                <span className="text-blue-600 text-xl">👥</span>
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">Total Prospects</p>
                <p className="text-2xl font-bold text-gray-900">{stats.prospects_stats.total_prospects}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border">
            <div className="flex items-center">
              <div className="p-3 bg-green-100 rounded-full">
                <span className="text-green-600 text-xl">✅</span>
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">Nouveaux</p>
                <p className="text-2xl font-bold text-gray-900">{stats.prospects_stats.status_breakdown?.new || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border">
            <div className="flex items-center">
              <div className="p-3 bg-yellow-100 rounded-full">
                <span className="text-yellow-600 text-xl">📞</span>
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">Contactés</p>
                <p className="text-2xl font-bold text-gray-900">{stats.prospects_stats.status_breakdown?.contacted || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border">
            <div className="flex items-center">
              <div className="p-3 bg-red-100 rounded-full">
                <span className="text-red-600 text-xl">⚠️</span>
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">Expirés GDPR</p>
                <p className="text-2xl font-bold text-gray-900">{stats.prospects_stats.gdpr_expired_count || 0}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filtres */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6 border">
        <h3 className="text-lg font-semibold mb-4">🔍 Filtres</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Statut</label>
            <select
              value={filters.status}
              onChange={(e) => setFilters({...filters, status: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Tous les statuts</option>
              <option value="new">Nouveau</option>
              <option value="contacted">Contacté</option>
              <option value="engaged">Engagé</option>
              <option value="qualified">Qualifié</option>
              <option value="converted">Converti</option>
              <option value="unsubscribed">Désinscrit</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Consentement</label>
            <select
              value={filters.consent_status}
              onChange={(e) => setFilters({...filters, consent_status: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Tous les consentements</option>
              <option value="b2b_optout_allowed">B2B Opt-out</option>
              <option value="b2c_optin_confirmed">B2C Opt-in</option>
              <option value="legitimate_interest">Intérêt légitime</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Pays</label>
            <select
              value={filters.country}
              onChange={(e) => setFilters({...filters, country: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="FR">France</option>
              <option value="BE">Belgique</option>
              <option value="CH">Suisse</option>
              <option value="CA">Canada</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={cleanupExpired}
              className="w-full bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-medium"
            >
              🧹 Nettoyage GDPR
            </button>
          </div>
        </div>
      </div>

      {/* Tableau des prospects */}
      <div className="bg-white rounded-lg shadow-md border overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold">📋 Liste des Prospects ({prospects.length})</h3>
        </div>

        {loading ? (
          <div className="p-8 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-2 text-gray-600">Chargement...</p>
          </div>
        ) : prospects.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            Aucun prospect trouvé avec ces filtres
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nom</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Intention</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Consentement</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Créé</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {prospects.map((prospect) => (
                  <tr key={prospect.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{prospect.email}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {prospect.first_name} {prospect.last_name}
                      </div>
                      {prospect.company && (
                        <div className="text-xs text-gray-500">{prospect.company}</div>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900 max-w-xs truncate">
                        {prospect.keyword_intent || '-'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <select
                        value={prospect.status}
                        onChange={(e) => updateProspectStatus(prospect.id, e.target.value)}
                        className={`text-xs px-2 py-1 rounded-full border-0 ${getStatusColor(prospect.status)}`}
                      >
                        <option value="new">Nouveau</option>
                        <option value="contacted">Contacté</option>
                        <option value="engaged">Engagé</option>
                        <option value="qualified">Qualifié</option>
                        <option value="converted">Converti</option>
                        <option value="unsubscribed">Désinscrit</option>
                      </select>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`text-xs px-2 py-1 rounded-full ${getConsentColor(prospect.consent_status)}`}>
                        {prospect.consent_status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(prospect.created_at).toLocaleDateString('fr-FR')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => deleteProspect(prospect.id)}
                        className="text-red-600 hover:text-red-900 ml-3"
                        title="Supprimer (droit à l'oubli GDPR)"
                      >
                        🗑️
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Conformité GDPR */}
      <div className="mt-8 bg-green-50 border border-green-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-green-800 mb-4">⚖️ Conformité CNIL/GDPR</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-green-700">
          <div>
            ✅ <strong>Rétention des données :</strong> 3 ans maximum<br/>
            ✅ <strong>Droit à l'oubli :</strong> Bouton de suppression disponible<br/>
            ✅ <strong>Consentement :</strong> Tracking du type de consentement
          </div>
          <div>
            ✅ <strong>Désinscription :</strong> Token unique par prospect<br/>
            ✅ <strong>Nettoyage automatique :</strong> Prospects expirés supprimés<br/>
            ✅ <strong>Audit trail :</strong> Toutes les actions sont loggées
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProspectsManager;