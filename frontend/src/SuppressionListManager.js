import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useSafeCleanup } from './hooks/useSafeCleanup';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const SuppressionListManager = () => {
  const [suppressionList, setSuppressionList] = useState([]);
  const [gdprJournal, setGdprJournal] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('list');
  const [filters, setFilters] = useState({
    search_email: '',
    reason: '',
    source: '',
    date_from: '',
    date_to: ''
  });
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalCount: 0,
    pageSize: 50
  });
  const [showAddModal, setShowAddModal] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const [newEmail, setNewEmail] = useState({
    email: '',
    reason: 'manual',
    source: 'crm_manual',
    notes: ''
  });
  const [csvContent, setCsvContent] = useState('');
  const [importResults, setImportResults] = useState(null);
  const fileInputRef = useRef(null);
  const { safeSetTimeout, isMounted } = useSafeCleanup();

  // Charger les données au montage
  useEffect(() => {
    loadSuppressionList();
    loadStats();
  }, [filters, pagination.currentPage]);

  const loadSuppressionList = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        skip: ((pagination.currentPage - 1) * pagination.pageSize).toString(),
        limit: pagination.pageSize.toString(),
        ...(filters.search_email && { search_email: filters.search_email }),
        ...(filters.reason && { reason: filters.reason }),
        ...(filters.source && { source: filters.source }),
        ...(filters.date_from && { date_from: filters.date_from }),
        ...(filters.date_to && { date_to: filters.date_to })
      });

      const response = await axios.get(`${BACKEND_URL}/api/suppression-list?${params}`);
      
      if (response.data.status === 'success') {
        setSuppressionList(response.data.data);
        setPagination(prev => ({
          ...prev,
          totalCount: response.data.pagination.total_count
        }));
      }
    } catch (error) {
      console.error('Erreur chargement liste suppression:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/suppression-list/stats`);
      if (response.data.status === 'success') {
        setStats(response.data.stats);
      }
    } catch (error) {
      console.error('Erreur chargement statistiques:', error);
    }
  };

  const loadGdprJournal = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${BACKEND_URL}/api/gdpr-journal?limit=100`);
      
      if (response.data.status === 'success') {
        setGdprJournal(response.data.data);
      }
    } catch (error) {
      console.error('Erreur chargement journal GDPR:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddEmail = async () => {
    try {
      setLoading(true);
      const response = await axios.post(`${BACKEND_URL}/api/suppression-list/add`, newEmail);
      
      if (response.data.status === 'success') {
        setShowAddModal(false);
        setNewEmail({ email: '', reason: 'manual', source: 'crm_manual', notes: '' });
        loadSuppressionList();
        loadStats();
        alert('✅ Email ajouté à la liste d\'exclusion');
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Erreur lors de l\'ajout';
      alert(`❌ ${errorMsg}`);
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveEmail = async (email) => {
    if (!window.confirm(`Êtes-vous sûr de vouloir retirer ${email} de la liste d'exclusion ?`)) {
      return;
    }

    try {
      setLoading(true);
      const response = await axios.delete(`${BACKEND_URL}/api/suppression-list/remove/${encodeURIComponent(email)}`);
      
      if (response.data.status === 'success') {
        loadSuppressionList();
        loadStats();
        alert('✅ Email retiré de la liste d\'exclusion');
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Erreur lors de la suppression';
      alert(`❌ ${errorMsg}`);
    } finally {
      setLoading(false);
    }
  };

  const handleImportCSV = async () => {
    try {
      setLoading(true);
      const response = await axios.post(`${BACKEND_URL}/api/suppression-list/import-csv`, {
        csv_content: csvContent
      });
      
      if (response.data.status === 'success') {
        setImportResults(response.data);
        setCsvContent('');
        loadSuppressionList();
        loadStats();
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Erreur lors de l\'import';
      alert(`❌ ${errorMsg}`);
    } finally {
      setLoading(false);
    }
  };

  const handleExportCSV = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${BACKEND_URL}/api/suppression-list/export-csv`, {
        responseType: 'blob'
      });
      
      // Créer un lien de téléchargement
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `suppression_list_${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      alert('❌ Erreur lors de l\'export CSV');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file && file.type === 'text/csv') {
      const reader = new FileReader();
      reader.onload = (e) => {
        setCsvContent(e.target.result);
      };
      reader.readAsText(file);
    } else {
      alert('⚠️ Veuillez sélectionner un fichier CSV valide');
    }
  };

  const applyFilters = () => {
    setPagination(prev => ({ ...prev, currentPage: 1 }));
    loadSuppressionList();
  };

  const clearFilters = () => {
    setFilters({
      search_email: '',
      reason: '',
      source: '',
      date_from: '',
      date_to: ''
    });
    setPagination(prev => ({ ...prev, currentPage: 1 }));
  };

  const getReasonBadge = (reason) => {
    const badgeStyles = {
      unsubscribe: 'bg-blue-100 text-blue-800',
      hard_bounce: 'bg-red-100 text-red-800',
      complaint: 'bg-orange-100 text-orange-800',
      manual: 'bg-gray-100 text-gray-800',
      import_csv: 'bg-purple-100 text-purple-800'
    };
    
    const style = badgeStyles[reason] || 'bg-gray-100 text-gray-800';
    
    const labels = {
      unsubscribe: '📧 Désinscription',
      hard_bounce: '🚫 Bounce Hard',
      complaint: '⚠️ Plainte',
      manual: '✋ Manuel',
      import_csv: '📁 Import CSV'
    };
    
    const label = labels[reason] || reason;
    
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${style}`}>
        {label}
      </span>
    );
  };

  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleString('fr-FR');
    } catch {
      return dateString;
    }
  };

  return (
    <div className="p-6">
      {/* En-tête avec statistiques */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              🛡️ Liste d'exclusion (GDPR)
            </h1>
            <p className="text-gray-600">
              Gestion des désinscriptions et conformité CNIL
            </p>
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={() => setShowAddModal(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              ➕ Ajouter Email
            </button>
            <button
              onClick={() => setShowImportModal(true)}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
            >
              📁 Import CSV
            </button>
            <button
              onClick={handleExportCSV}
              disabled={loading}
              className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
            >
              📤 Export CSV
            </button>
          </div>
        </div>

        {/* Cartes statistiques */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
                  <span className="text-red-600 font-bold">🚫</span>
                </div>
              </div>
              <div className="ml-4">
                <h3 className="text-sm font-medium text-gray-500">Total Exclus</h3>
                <p className="text-2xl font-bold text-gray-900">
                  {stats.total_suppressed || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center">
                  <span className="text-orange-600 font-bold">📅</span>
                </div>
              </div>
              <div className="ml-4">
                <h3 className="text-sm font-medium text-gray-500">30 Derniers Jours</h3>
                <p className="text-2xl font-bold text-gray-900">
                  {stats.recent_suppressed_30d || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                  <span className="text-blue-600 font-bold">📧</span>
                </div>
              </div>
              <div className="ml-4">
                <h3 className="text-sm font-medium text-gray-500">Désinscriptions</h3>
                <p className="text-2xl font-bold text-gray-900">
                  {stats.by_reason?.find(r => r._id === 'unsubscribe')?.count || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                  <span className="text-green-600 font-bold">🔒</span>
                </div>
              </div>
              <div className="ml-4">
                <h3 className="text-sm font-medium text-gray-500">Conformité</h3>
                <p className="text-sm font-bold text-green-600">GDPR ✓</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Onglets */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => {
                setActiveTab('list');
                if (activeTab !== 'list') loadSuppressionList();
              }}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'list'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              📋 Liste d'exclusion
            </button>
            <button
              onClick={() => {
                setActiveTab('journal');
                if (activeTab !== 'journal') loadGdprJournal();
              }}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'journal'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              📖 Journal GDPR
            </button>
          </nav>
        </div>
      </div>

      {/* Contenu des onglets */}
      {activeTab === 'list' && (
        <div>
          {/* Filtres */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">🔍 Filtres de recherche</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={filters.search_email}
                  onChange={(e) => setFilters(prev => ({ ...prev, search_email: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Rechercher un email..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Motif
                </label>
                <select
                  value={filters.reason}
                  onChange={(e) => setFilters(prev => ({ ...prev, reason: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Tous les motifs</option>
                  <option value="unsubscribe">Désinscription</option>
                  <option value="hard_bounce">Bounce Hard</option>
                  <option value="complaint">Plainte</option>
                  <option value="manual">Manuel</option>
                  <option value="import_csv">Import CSV</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Source
                </label>
                <select
                  value={filters.source}
                  onChange={(e) => setFilters(prev => ({ ...prev, source: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Toutes les sources</option>
                  <option value="footer_link">Lien désinscription</option>
                  <option value="crm_manual">CRM Manuel</option>
                  <option value="csv_import">Import CSV</option>
                  <option value="bounce_handler">Bounce Handler</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Date début
                </label>
                <input
                  type="date"
                  value={filters.date_from}
                  onChange={(e) => setFilters(prev => ({ ...prev, date_from: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Date fin
                </label>
                <input
                  type="date"
                  value={filters.date_to}
                  onChange={(e) => setFilters(prev => ({ ...prev, date_to: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            <div className="flex justify-end space-x-3">
              <button
                onClick={clearFilters}
                className="px-4 py-2 text-gray-600 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
              >
                🗑️ Effacer
              </button>
              <button
                onClick={applyFilters}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                🔍 Rechercher
              </button>
            </div>
          </div>

          {/* Table des exclusions */}
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">
                📋 Emails exclus ({pagination.totalCount})
              </h3>
            </div>

            {loading ? (
              <div className="p-8 text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Chargement...</p>
              </div>
            ) : suppressionList.length === 0 ? (
              <div className="p-8 text-center">
                <div className="text-4xl mb-4">📭</div>
                <p className="text-gray-600">Aucun email dans la liste d'exclusion</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Email
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Motif
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Source
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Date
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Notes
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {suppressionList.map((item) => (
                      <tr key={`suppression-${item.email}`} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="font-medium text-gray-900">{item.email}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {getReasonBadge(item.reason)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                          {item.source}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                          {formatDate(item.unsubscribed_at)}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600 max-w-xs truncate">
                          {item.notes}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <button
                            onClick={() => handleRemoveEmail(item.email)}
                            className="text-red-600 hover:text-red-800 transition-colors"
                            title="Retirer de la liste"
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

            {/* Pagination */}
            {pagination.totalCount > pagination.pageSize && (
              <div className="px-6 py-3 bg-gray-50 flex items-center justify-between">
                <div className="text-sm text-gray-700">
                  Page {pagination.currentPage} sur {Math.ceil(pagination.totalCount / pagination.pageSize)}
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setPagination(prev => ({ ...prev, currentPage: Math.max(1, prev.currentPage - 1) }))}
                    disabled={pagination.currentPage <= 1}
                    className="px-3 py-1 bg-gray-200 text-gray-700 rounded disabled:opacity-50"
                  >
                    ← Précédent
                  </button>
                  <button
                    onClick={() => setPagination(prev => ({ ...prev, currentPage: prev.currentPage + 1 }))}
                    disabled={pagination.currentPage >= Math.ceil(pagination.totalCount / pagination.pageSize)}
                    className="px-3 py-1 bg-gray-200 text-gray-700 rounded disabled:opacity-50"
                  >
                    Suivant →
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Journal GDPR */}
      {activeTab === 'journal' && (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              📖 Journal GDPR - Historique des actions
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              Traçabilité complète des actions de suppression (lecture seule)
            </p>
          </div>

          {loading ? (
            <div className="p-8 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Chargement du journal...</p>
            </div>
          ) : gdprJournal.length === 0 ? (
            <div className="p-8 text-center">
              <div className="text-4xl mb-4">📋</div>
              <p className="text-gray-600">Aucune entrée dans le journal GDPR</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date/Heure
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Action
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Email
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Détails
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Agent
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {gdprJournal.map((entry) => (
                    <tr key={`journal-${entry.id}`} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {formatDate(entry.timestamp)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          entry.action_type === 'add_suppression' ? 'bg-red-100 text-red-800' :
                          entry.action_type === 'remove_suppression' ? 'bg-green-100 text-green-800' :
                          entry.action_type === 'csv_import' ? 'bg-purple-100 text-purple-800' :
                          entry.action_type === 'csv_export' ? 'bg-blue-100 text-blue-800' :
                          entry.action_type === 'skip_send' ? 'bg-orange-100 text-orange-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {entry.action_type === 'add_suppression' && '🚫 Ajout'}
                          {entry.action_type === 'remove_suppression' && '✅ Suppression'}
                          {entry.action_type === 'csv_import' && '📁 Import'}
                          {entry.action_type === 'csv_export' && '📤 Export'}
                          {entry.action_type === 'skip_send' && '⏭️ Envoi bloqué'}
                          {!['add_suppression', 'remove_suppression', 'csv_import', 'csv_export', 'skip_send'].includes(entry.action_type) && entry.action_type}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {entry.email || '-'}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600 max-w-xs truncate">
                        {entry.details}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {entry.agent_email}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Modal Ajout Email */}
      {showAddModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                ➕ Ajouter un email à la liste d'exclusion
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email *
                  </label>
                  <input
                    type="email"
                    required
                    value={newEmail.email}
                    onChange={(e) => setNewEmail(prev => ({ ...prev, email: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="example@domain.com"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Motif
                  </label>
                  <select
                    value={newEmail.reason}
                    onChange={(e) => setNewEmail(prev => ({ ...prev, reason: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="manual">Manuel</option>
                    <option value="unsubscribe">Désinscription</option>
                    <option value="hard_bounce">Bounce Hard</option>
                    <option value="complaint">Plainte</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Source
                  </label>
                  <select
                    value={newEmail.source}
                    onChange={(e) => setNewEmail(prev => ({ ...prev, source: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="crm_manual">CRM Manuel</option>
                    <option value="footer_link">Lien désinscription</option>
                    <option value="bounce_handler">Bounce Handler</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Notes (optionnel)
                  </label>
                  <textarea
                    rows="3"
                    value={newEmail.notes}
                    onChange={(e) => setNewEmail(prev => ({ ...prev, notes: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Raison ou contexte..."
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 text-gray-600 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
                >
                  Annuler
                </button>
                <button
                  onClick={handleAddEmail}
                  disabled={loading || !newEmail.email}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
                >
                  {loading ? 'Ajout...' : 'Ajouter'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal Import CSV */}
      {showImportModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-10 mx-auto p-5 border w-2/3 max-w-2xl shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                📁 Import CSV - Liste d'exclusion
              </h3>
              
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Format CSV attendu :</h4>
                <div className="bg-gray-100 p-3 rounded-md text-sm font-mono">
                  email,reason,source,notes<br/>
                  test@example.com,unsubscribe,footer_link,Désinscrit via email<br/>
                  spam@domain.com,complaint,manual,Plainte client
                </div>
                <p className="text-xs text-gray-600 mt-2">
                  * Seule la colonne "email" est obligatoire. Les autres colonnes sont optionnelles.
                </p>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Fichier CSV
                  </label>
                  <input
                    type="file"
                    accept=".csv"
                    ref={fileInputRef}
                    onChange={handleFileUpload}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Contenu CSV
                  </label>
                  <textarea
                    rows="10"
                    value={csvContent}
                    onChange={(e) => setCsvContent(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
                    placeholder="Collez votre contenu CSV ici ou utilisez le bouton de fichier ci-dessus..."
                  />
                </div>

                {importResults && (
                  <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                    <h4 className="text-sm font-medium text-blue-800 mb-2">Résultats de l'import :</h4>
                    <p className="text-sm text-blue-700">✅ {importResults.imported_count} emails ajoutés</p>
                    {importResults.errors.length > 0 && (
                      <div className="mt-2">
                        <p className="text-sm text-red-600">❌ {importResults.errors.length} erreurs :</p>
                        <div className="mt-1 max-h-32 overflow-y-auto">
                          {importResults.errors.slice(0, 5).map((error, idx) => (
                            <p key={`import-error-${idx}`} className="text-xs text-red-600">• {error}</p>
                          ))}
                          {importResults.errors.length > 5 && (
                            <p className="text-xs text-red-600">... et {importResults.errors.length - 5} autres erreurs</p>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => {
                    setShowImportModal(false);
                    setCsvContent('');
                    setImportResults(null);
                  }}
                  className="px-4 py-2 text-gray-600 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
                >
                  Fermer
                </button>
                <button
                  onClick={handleImportCSV}
                  disabled={loading || !csvContent.trim()}
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:opacity-50"
                >
                  {loading ? 'Import...' : 'Importer CSV'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SuppressionListManager;