import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useSafeCleanup } from './hooks/useSafeCleanup';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const EmailSequencer = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [sequences, setSequences] = useState([]);
  const [metrics, setMetrics] = useState({});
  const [templates, setTemplates] = useState({});
  const [loading, setLoading] = useState(false);
  const [showStartModal, setShowStartModal] = useState(false);
  const [sequenceConfig, setSequenceConfig] = useState({
    test_mode: true,
    test_emails: ['test@example.com']
  });
  const [recentEvents, setRecentEvents] = useState([]);
  const [selectedSequence, setSelectedSequence] = useState(null);
  const [sequenceDetails, setSequenceDetails] = useState(null);
  const { safeSetTimeout } = useSafeCleanup();

  useEffect(() => {
    loadDashboardData();
    loadTemplates();
    
    // Actualiser les données toutes les 30 secondes
    const interval = setInterval(() => {
      loadDashboardData();
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${BACKEND_URL}/api/email-sequencer/metrics?limit=50`);
      
      if (response.data.status === 'success') {
        const data = response.data.data;
        setMetrics(data.metrics || {});
        setSequences(data.active_sequences || []);
        setRecentEvents(data.recent_events || []);
      }
    } catch (error) {
      console.error('Erreur chargement dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadTemplates = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/email-sequencer/templates`);
      if (response.data.status === 'success') {
        setTemplates(response.data.templates);
      }
    } catch (error) {
      console.error('Erreur chargement templates:', error);
    }
  };

  const loadSequenceDetails = async (sequenceId) => {
    try {
      setLoading(true);
      const response = await axios.get(`${BACKEND_URL}/api/email-sequencer/sequence/${sequenceId}`);
      
      if (response.data.status === 'success') {
        setSequenceDetails(response.data.data);
        setSelectedSequence(sequenceId);
      }
    } catch (error) {
      console.error('Erreur chargement détails séquence:', error);
    } finally {
      setLoading(false);
    }
  };

  const startSequence = async () => {
    try {
      setLoading(true);
      const response = await axios.post(`${BACKEND_URL}/api/email-sequencer/start`, sequenceConfig);
      
      if (response.data.status === 'success') {
        setShowStartModal(false);
        alert(`✅ Séquence démarrée avec succès !\n\nID: ${response.data.data.sequence_id}\nProspects traités: ${response.data.data.total_prospects}\nEmails envoyés: ${response.data.data.email1_sent}\nIgnorés (suppression): ${response.data.data.skipped_count}`);
        loadDashboardData();
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Erreur lors du démarrage';
      alert(`❌ ${errorMsg}`);
    } finally {
      setLoading(false);
    }
  };

  const stopSequence = async (sequenceId) => {
    if (!window.confirm(`Êtes-vous sûr de vouloir arrêter la séquence ${sequenceId} ?\n\nTous les emails non envoyés seront annulés.`)) {
      return;
    }

    try {
      setLoading(true);
      const response = await axios.post(`${BACKEND_URL}/api/email-sequencer/stop/${sequenceId}`);
      
      if (response.data.status === 'success') {
        alert(`✅ Séquence arrêtée\n\n${response.data.data.cancelled_emails} emails annulés`);
        loadDashboardData();
        if (selectedSequence === sequenceId) {
          setSelectedSequence(null);
          setSequenceDetails(null);
        }
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Erreur lors de l\'arrêt';
      alert(`❌ ${errorMsg}`);
    } finally {
      setLoading(false);
    }
  };

  const processScheduledEmails = async () => {
    try {
      setLoading(true);
      const response = await axios.post(`${BACKEND_URL}/api/email-sequencer/process-scheduled`);
      
      if (response.data.status === 'success') {
        const data = response.data.data;
        alert(`✅ Traitement des emails programmés terminé\n\nTraités: ${data.processed}\nEnvoyés: ${data.sent}\nErreurs: ${data.errors}`);
        loadDashboardData();
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Erreur lors du traitement';
      alert(`❌ ${errorMsg}`);
    } finally {
      setLoading(false);
    }
  };

  const calculateSequenceStats = (sequenceMetrics) => {
    let totalSent = 0;
    let totalOpened = 0;
    let totalClicked = 0;
    let totalBounced = 0;
    let totalSkipped = 0;

    Object.values(sequenceMetrics).forEach(stepMetrics => {
      totalSent += stepMetrics.sent || 0;
      totalOpened += stepMetrics.opened || 0;
      totalClicked += stepMetrics.clicked || 0;
      totalBounced += (stepMetrics.hard_bounce || 0) + (stepMetrics.soft_bounce || 0);
      totalSkipped += stepMetrics.skipped_suppressed || 0;
    });

    return { totalSent, totalOpened, totalClicked, totalBounced, totalSkipped };
  };

  const getEventIcon = (eventType) => {
    const icons = {
      sent: '📧',
      delivered: '✅',
      opened: '👁️',
      clicked: '🔗',
      hard_bounce: '🚫',
      soft_bounce: '⚠️',
      skipped_suppressed: '🛡️',
      skipped_generic: '🏷️',
      error: '❌'
    };
    return icons[eventType] || '📄';
  };

  const getEventLabel = (eventType) => {
    const labels = {
      sent: 'Envoyé',
      delivered: 'Délivré',
      opened: 'Ouvert',
      clicked: 'Cliqué',
      hard_bounce: 'Bounce Hard',
      soft_bounce: 'Bounce Soft',
      skipped_suppressed: 'Ignoré (Suppression)',
      skipped_generic: 'Ignoré (Générique)',
      error: 'Erreur'
    };
    return labels[eventType] || eventType;
  };

  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleString('fr-FR');
    } catch {
      return dateString;
    }
  };

  const addTestEmail = () => {
    setSequenceConfig(prev => ({
      ...prev,
      test_emails: [...prev.test_emails, '']
    }));
  };

  const updateTestEmail = (index, value) => {
    setSequenceConfig(prev => ({
      ...prev,
      test_emails: prev.test_emails.map((email, i) => i === index ? value : email)
    }));
  };

  const removeTestEmail = (index) => {
    setSequenceConfig(prev => ({
      ...prev,
      test_emails: prev.test_emails.filter((_, i) => i !== index)
    }));
  };

  return (
    <div className="p-6">
      {/* En-tête */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              📧 Email Sequencer Osmoseur
            </h1>
            <p className="text-gray-600">
              Séquences automatiques de marketing par email avec conformité GDPR
            </p>
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={() => setShowStartModal(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              🚀 Lancer Séquence
            </button>
            <button
              onClick={processScheduledEmails}
              disabled={loading}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
            >
              ⚡ Traiter Programmés
            </button>
            <button
              onClick={loadDashboardData}
              disabled={loading}
              className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors disabled:opacity-50"
            >
              🔄 Actualiser
            </button>
          </div>
        </div>

        {/* Statistiques globales */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                  <span className="text-blue-600 font-bold">📧</span>
                </div>
              </div>
              <div className="ml-4">
                <h3 className="text-sm font-medium text-gray-500">Séquences Actives</h3>
                <p className="text-2xl font-bold text-gray-900">
                  {sequences.length}
                </p>
              </div>
            </div>
          </div>

          {Object.keys(metrics).length > 0 && (() => {
            const globalStats = Object.values(metrics).reduce((acc, seq) => {
              const stats = calculateSequenceStats(seq);
              acc.totalSent += stats.totalSent;
              acc.totalOpened += stats.totalOpened;
              acc.totalClicked += stats.totalClicked;
              acc.totalBounced += stats.totalBounced;
              acc.totalSkipped += stats.totalSkipped;
              return acc;
            }, { totalSent: 0, totalOpened: 0, totalClicked: 0, totalBounced: 0, totalSkipped: 0 });

            return (
              <>
                <div className="bg-white rounded-lg shadow-md p-6">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                        <span className="text-green-600 font-bold">✅</span>
                      </div>
                    </div>
                    <div className="ml-4">
                      <h3 className="text-sm font-medium text-gray-500">Envoyés</h3>
                      <p className="text-2xl font-bold text-gray-900">
                        {globalStats.totalSent}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-white rounded-lg shadow-md p-6">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                        <span className="text-purple-600 font-bold">👁️</span>
                      </div>
                    </div>
                    <div className="ml-4">
                      <h3 className="text-sm font-medium text-gray-500">Ouverts</h3>
                      <p className="text-2xl font-bold text-gray-900">
                        {globalStats.totalOpened}
                      </p>
                      <p className="text-xs text-gray-500">
                        {globalStats.totalSent > 0 ? Math.round((globalStats.totalOpened / globalStats.totalSent) * 100) : 0}%
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-white rounded-lg shadow-md p-6">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center">
                        <span className="text-indigo-600 font-bold">🔗</span>
                      </div>
                    </div>
                    <div className="ml-4">
                      <h3 className="text-sm font-medium text-gray-500">Cliqués</h3>
                      <p className="text-2xl font-bold text-gray-900">
                        {globalStats.totalClicked}
                      </p>
                      <p className="text-xs text-gray-500">
                        {globalStats.totalSent > 0 ? Math.round((globalStats.totalClicked / globalStats.totalSent) * 100) : 0}%
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-white rounded-lg shadow-md p-6">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
                        <span className="text-red-600 font-bold">🛡️</span>
                      </div>
                    </div>
                    <div className="ml-4">
                      <h3 className="text-sm font-medium text-gray-500">Ignorés GDPR</h3>
                      <p className="text-2xl font-bold text-gray-900">
                        {globalStats.totalSkipped}
                      </p>
                    </div>
                  </div>
                </div>
              </>
            );
          })()}
        </div>
      </div>

      {/* Onglets */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'dashboard'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              📊 Dashboard
            </button>
            <button
              onClick={() => setActiveTab('sequences')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'sequences'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              📧 Séquences Actives
            </button>
            <button
              onClick={() => setActiveTab('templates')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'templates'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              📝 Templates
            </button>
            <button
              onClick={() => setActiveTab('events')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'events'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              📋 Événements
            </button>
          </nav>
        </div>
      </div>

      {/* Contenu des onglets */}
      {activeTab === 'dashboard' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Séquences récentes */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">🔥 Séquences Actives</h3>
            
            {sequences.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-4xl mb-4">📧</div>
                <p className="text-gray-600">Aucune séquence active</p>
                <button
                  onClick={() => setShowStartModal(true)}
                  className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Lancer votre première séquence
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {sequences.slice(0, 5).map((sequenceId) => {
                  const sequenceMetrics = metrics[sequenceId] || {};
                  const stats = calculateSequenceStats(sequenceMetrics);
                  
                  return (
                    <div key={`sequence-${sequenceId}`} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer transition-colors">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h4 className="font-medium text-gray-900">Séquence {sequenceId.slice(0, 8)}</h4>
                          <p className="text-sm text-gray-600">{stats.totalSent} envoyés • {stats.totalSkipped} ignorés</p>
                        </div>
                        <div className="flex space-x-2">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              loadSequenceDetails(sequenceId);
                            }}
                            className="text-xs bg-blue-100 hover:bg-blue-200 text-blue-700 px-2 py-1 rounded"
                          >
                            📋 Détails
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              stopSequence(sequenceId);
                            }}
                            className="text-xs bg-red-100 hover:bg-red-200 text-red-700 px-2 py-1 rounded"
                          >
                            🛑 Arrêter
                          </button>
                        </div>
                      </div>
                      
                      <div className="flex space-x-4 text-xs">
                        <span className="text-green-600">👁️ {stats.totalOpened}</span>
                        <span className="text-blue-600">🔗 {stats.totalClicked}</span>
                        <span className="text-red-600">🚫 {stats.totalBounced}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Templates d'emails */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">📝 Séquence Osmoseur (3 emails)</h3>
            
            <div className="space-y-4">
              {Object.entries(templates).map(([step, template]) => (
                <div key={`template-${step}`} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h4 className="font-medium text-gray-900">
                        {step === 'email1' && '📧 Email 1 - Découverte'}
                        {step === 'email2' && '📧 Email 2 - Relance'}
                        {step === 'email3' && '📧 Email 3 - Offre finale'}
                      </h4>
                      <p className="text-sm text-gray-600">{template.subject}</p>
                    </div>
                    <span className={`text-xs px-2 py-1 rounded ${
                      template.delay_days === 0 ? 'bg-green-100 text-green-700' :
                      template.delay_days <= 2 ? 'bg-yellow-100 text-yellow-700' :
                      'bg-red-100 text-red-700'
                    }`}>
                      J+{template.delay_days}
                    </span>
                  </div>
                  
                  <div className="text-xs text-gray-500">
                    UTM: {template.utm_content}
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-4 p-4 bg-blue-50 rounded-lg">
              <h5 className="font-medium text-blue-900 mb-2">🛡️ Protection GDPR</h5>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• Lien de désinscription automatique</li>
                <li>• Respect de la liste de suppression</li>
                <li>• Filtrage des emails génériques</li>
                <li>• Journal d'audit complet</li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'sequences' && (
        <div>
          {sequences.length === 0 ? (
            <div className="bg-white rounded-lg shadow-md p-8 text-center">
              <div className="text-4xl mb-4">📧</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Aucune séquence active</h3>
              <p className="text-gray-600 mb-6">Lancez votre première campagne d'email marketing</p>
              <button
                onClick={() => setShowStartModal(true)}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
              >
                🚀 Lancer une séquence
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              {sequences.map((sequenceId) => {
                const sequenceMetrics = metrics[sequenceId] || {};
                const stats = calculateSequenceStats(sequenceMetrics);
                
                return (
                  <div key={`detailed-sequence-${sequenceId}`} className="bg-white rounded-lg shadow-md p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-lg font-medium text-gray-900">
                          Séquence {sequenceId.slice(0, 8)}...
                        </h3>
                        <p className="text-sm text-gray-600">ID: {sequenceId}</p>
                      </div>
                      
                      <div className="flex space-x-2">
                        <button
                          onClick={() => loadSequenceDetails(sequenceId)}
                          className="bg-blue-100 hover:bg-blue-200 text-blue-700 px-3 py-2 rounded-lg text-sm"
                        >
                          📋 Voir détails
                        </button>
                        <button
                          onClick={() => stopSequence(sequenceId)}
                          className="bg-red-100 hover:bg-red-200 text-red-700 px-3 py-2 rounded-lg text-sm"
                        >
                          🛑 Arrêter
                        </button>
                      </div>
                    </div>
                    
                    {/* Métriques par étape */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {Object.entries(sequenceMetrics).map(([step, stepMetrics]) => (
                        <div key={`step-${step}`} className="border border-gray-200 rounded-lg p-4">
                          <h4 className="font-medium text-gray-900 mb-2">
                            {step === 'email1' && '📧 Email 1'}
                            {step === 'email2' && '📧 Email 2'}
                            {step === 'email3' && '📧 Email 3'}
                          </h4>
                          
                          <div className="space-y-2 text-sm">
                            <div className="flex justify-between">
                              <span>Envoyés:</span>
                              <span className="font-medium">{stepMetrics.sent || 0}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Ouverts:</span>
                              <span className="font-medium text-green-600">{stepMetrics.opened || 0}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Cliqués:</span>
                              <span className="font-medium text-blue-600">{stepMetrics.clicked || 0}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Ignorés:</span>
                              <span className="font-medium text-orange-600">{stepMetrics.skipped_suppressed || 0}</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {activeTab === 'templates' && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-6">📝 Templates de la Séquence Osmoseur</h3>
          
          <div className="space-y-6">
            {Object.entries(templates).map(([step, template]) => (
              <div key={`template-detail-${step}`} className="border border-gray-200 rounded-lg p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h4 className="text-xl font-medium text-gray-900">
                      {step === 'email1' && '📧 Email 1 - Découverte (J+0)'}
                      {step === 'email2' && '📧 Email 2 - Relance (J+2)'}
                      {step === 'email3' && '📧 Email 3 - Offre finale (J+5/J+7)'}
                    </h4>
                    <p className="text-lg text-gray-700">{template.subject}</p>
                  </div>
                  
                  <div className="flex space-x-2">
                    <span className={`px-3 py-1 rounded-full text-sm ${
                      template.delay_days === 0 ? 'bg-green-100 text-green-700' :
                      template.delay_days <= 2 ? 'bg-yellow-100 text-yellow-700' :
                      'bg-red-100 text-red-700'
                    }`}>
                      Délai: {template.delay_days} jour{template.delay_days > 1 ? 's' : ''}
                    </span>
                    <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm">
                      UTM: {template.utm_content}
                    </span>
                  </div>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-4">
                  <h5 className="font-medium text-gray-900 mb-2">Contenu clé:</h5>
                  <ul className="text-sm text-gray-700 space-y-1">
                    {step === 'email1' && (
                      <>
                        <li>• Introduction au problème de l'eau du robinet</li>
                        <li>• Présentation des bénéfices de l'osmoseur</li>
                        <li>• Offre de lancement : 549€ TTC (au lieu de 649€)</li>
                        <li>• Paiement 3× sans frais + Filtres année 1 offerts</li>
                      </>
                    )}
                    {step === 'email2' && (
                      <>
                        <li>• Focus sur l'expérience utilisateur</li>
                        <li>• Élimination des contaminants spécifiques</li>
                        <li>• Témoignage client</li>
                        <li>• Rappel de l'offre promotionnelle</li>
                      </>
                    )}
                    {step === 'email3' && (
                      <>
                        <li>• Urgence - Derniers jours de l'offre</li>
                        <li>• Récapitulatif complet des avantages</li>
                        <li>• Retour au prix normal après expiration</li>
                        <li>• Social proof (2000+ familles)</li>
                      </>
                    )}
                  </ul>
                </div>
                
                <div className="mt-4 text-sm text-gray-600">
                  <strong>CTA Link:</strong> www.josmoze.com/acheter?utm_source=email&utm_campaign=osmozeur_seq1&utm_content={template.utm_content}
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-6 p-4 bg-green-50 rounded-lg">
            <h5 className="font-medium text-green-900 mb-2">🛡️ Conformité GDPR intégrée</h5>
            <ul className="text-sm text-green-700 space-y-1">
              <li>• Lien de désinscription unique généré automatiquement</li>
              <li>• Vérification de la suppression_list avant chaque envoi</li>
              <li>• Gestion automatique des bounces (hard bounce → suppression_list)</li>
              <li>• Journalisation de tous les événements dans le Journal GDPR</li>
              <li>• Filtrage automatique des emails génériques</li>
            </ul>
          </div>
        </div>
      )}

      {activeTab === 'events' && (
        <div className="bg-white rounded-lg shadow-md">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">📋 Événements Récents</h3>
            <p className="text-sm text-gray-600 mt-1">
              Journal des envois et interactions des 50 derniers événements
            </p>
          </div>

          {loading ? (
            <div className="p-8 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Chargement des événements...</p>
            </div>
          ) : recentEvents.length === 0 ? (
            <div className="p-8 text-center">
              <div className="text-4xl mb-4">📋</div>
              <p className="text-gray-600">Aucun événement récent</p>
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
                      Événement
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Email
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Étape
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Séquence
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Détails
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {recentEvents.map((event, index) => (
                    <tr key={`event-${event.sequence_id}-${event.prospect_email}-${index}`} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {formatDate(event.created_at)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          event.event_type === 'sent' ? 'bg-blue-100 text-blue-800' :
                          event.event_type === 'opened' ? 'bg-green-100 text-green-800' :
                          event.event_type === 'clicked' ? 'bg-purple-100 text-purple-800' :
                          event.event_type.includes('bounce') ? 'bg-red-100 text-red-800' :
                          event.event_type.includes('skipped') ? 'bg-yellow-100 text-yellow-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {getEventIcon(event.event_type)} {getEventLabel(event.event_type)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {event.prospect_email}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {event.step}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {event.sequence_id.slice(0, 8)}...
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                        {event.details}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Modal Démarrage de Séquence */}
      {showStartModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-2/3 max-w-2xl shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                🚀 Lancer une Séquence Email Osmoseur
              </h3>
              
              <div className="space-y-6">
                {/* Mode de test */}
                <div>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={sequenceConfig.test_mode}
                      onChange={(e) => setSequenceConfig(prev => ({ ...prev, test_mode: e.target.checked }))}
                      className="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="text-sm text-gray-700">
                      <strong>Mode Test</strong> - Envoi simulé (recommandé pour la première fois)
                    </span>
                  </label>
                </div>

                {/* Configuration des emails de test */}
                {sequenceConfig.test_mode && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Emails de test
                    </label>
                    
                    <div className="space-y-2">
                      {sequenceConfig.test_emails.map((email, index) => (
                        <div key={`test-email-${index}`} className="flex space-x-2">
                          <input
                            type="email"
                            value={email}
                            onChange={(e) => updateTestEmail(index, e.target.value)}
                            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            placeholder="email@example.com"
                          />
                          {sequenceConfig.test_emails.length > 1 && (
                            <button
                              onClick={() => removeTestEmail(index)}
                              className="px-3 py-2 bg-red-100 text-red-700 rounded-md hover:bg-red-200 transition-colors"
                            >
                              🗑️
                            </button>
                          )}
                        </div>
                      ))}
                    </div>
                    
                    <button
                      onClick={addTestEmail}
                      className="mt-2 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1 rounded-md"
                    >
                      ➕ Ajouter un email de test
                    </button>
                  </div>
                )}

                {/* Informations sur la séquence */}
                <div className="bg-blue-50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-blue-900 mb-2">🎯 Séquence "Osmoseur" - 3 emails</h4>
                  <ul className="text-sm text-blue-700 space-y-1">
                    <li>• <strong>Email 1</strong> : Envoi immédiat (J+0) - "Votre eau mérite mieux"</li>
                    <li>• <strong>Email 2</strong> : Dans 2 jours (J+2) - "Et si vous goûtiez la différence ?"</li>
                    <li>• <strong>Email 3</strong> : Dans 5-7 jours (J+5/J+7) - "Derniers jours offre spéciale"</li>
                  </ul>
                </div>

                {/* Cible */}
                <div className="bg-green-50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-green-900 mb-2">🎯 Cible</h4>
                  <p className="text-sm text-green-700">
                    {sequenceConfig.test_mode 
                      ? `Emails de test : ${sequenceConfig.test_emails.filter(e => e.trim()).length} adresse(s)`
                      : 'Tous les prospects avec status="new" non présents dans la liste de suppression'
                    }
                  </p>
                </div>

                {/* Protection GDPR */}
                <div className="bg-yellow-50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-yellow-900 mb-2">🛡️ Protection GDPR</h4>
                  <ul className="text-sm text-yellow-700 space-y-1">
                    <li>• Vérification automatique de la liste de suppression</li>
                    <li>• Lien de désinscription dans chaque email</li>
                    <li>• Journalisation complète des actions</li>
                    <li>• Exclusion des emails génériques (info@, contact@, etc.)</li>
                  </ul>
                </div>
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => {
                    setShowStartModal(false);
                    setSequenceConfig({
                      test_mode: true,
                      test_emails: ['test@example.com']
                    });
                  }}
                  className="px-4 py-2 text-gray-600 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
                >
                  Annuler
                </button>
                <button
                  onClick={startSequence}
                  disabled={loading || (sequenceConfig.test_mode && sequenceConfig.test_emails.filter(e => e.trim()).length === 0)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
                >
                  {loading ? 'Lancement...' : '🚀 Lancer la Séquence'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal Détails de Séquence */}
      {selectedSequence && sequenceDetails && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-10 mx-auto p-5 border w-5/6 max-w-6xl shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-medium text-gray-900">
                    📧 Détails Séquence {selectedSequence.slice(0, 8)}
                  </h3>
                  <p className="text-sm text-gray-600">ID: {selectedSequence}</p>
                </div>
                <button
                  onClick={() => {
                    setSelectedSequence(null);
                    setSequenceDetails(null);
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              
              {/* Métriques de la séquence */}
              <div className="mb-6">
                <h4 className="font-medium text-gray-900 mb-3">📊 Métriques par étape</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {Object.entries(sequenceDetails.metrics).map(([step, stepMetrics]) => (
                    <div key={`detail-step-${step}`} className="bg-gray-50 rounded-lg p-4">
                      <h5 className="font-medium text-gray-900 mb-2">
                        {step === 'email1' && 'Email 1 - Découverte'}
                        {step === 'email2' && 'Email 2 - Relance'}
                        {step === 'email3' && 'Email 3 - Offre finale'}
                      </h5>
                      <div className="space-y-1 text-sm">
                        <div className="flex justify-between">
                          <span>Envoyés:</span>
                          <span className="font-medium">{stepMetrics.sent || 0}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Ouverts:</span>
                          <span className="font-medium text-green-600">{stepMetrics.opened || 0}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Cliqués:</span>
                          <span className="font-medium text-blue-600">{stepMetrics.clicked || 0}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Ignorés:</span>
                          <span className="font-medium text-orange-600">{stepMetrics.skipped_suppressed || 0}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Détails par prospect */}
              <div className="mb-6">
                <h4 className="font-medium text-gray-900 mb-3">👥 Prospects ({Object.keys(sequenceDetails.prospects).length})</h4>
                <div className="bg-gray-50 rounded-lg max-h-64 overflow-y-auto">
                  <table className="min-w-full">
                    <thead className="bg-gray-100 sticky top-0">
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Nom</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Email 1</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Email 2</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Email 3</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {Object.entries(sequenceDetails.prospects).map(([email, prospect]) => (
                        <tr key={`prospect-${email}`} className="hover:bg-white">
                          <td className="px-4 py-2 text-sm font-medium text-gray-900">{email}</td>
                          <td className="px-4 py-2 text-sm text-gray-600">{prospect.first_name || '-'}</td>
                          <td className="px-4 py-2 text-sm">
                            <span className={`px-2 py-1 rounded-full text-xs ${
                              prospect.steps.email1?.status === 'sent' ? 'bg-green-100 text-green-700' :
                              prospect.steps.email1?.status === 'scheduled' ? 'bg-yellow-100 text-yellow-700' :
                              'bg-gray-100 text-gray-700'
                            }`}>
                              {prospect.steps.email1?.status || 'N/A'}
                            </span>
                          </td>
                          <td className="px-4 py-2 text-sm">
                            <span className={`px-2 py-1 rounded-full text-xs ${
                              prospect.steps.email2?.status === 'sent' ? 'bg-green-100 text-green-700' :
                              prospect.steps.email2?.status === 'scheduled' ? 'bg-yellow-100 text-yellow-700' :
                              'bg-gray-100 text-gray-700'
                            }`}>
                              {prospect.steps.email2?.status || 'N/A'}
                            </span>
                          </td>
                          <td className="px-4 py-2 text-sm">
                            <span className={`px-2 py-1 rounded-full text-xs ${
                              prospect.steps.email3?.status === 'sent' ? 'bg-green-100 text-green-700' :
                              prospect.steps.email3?.status === 'scheduled' ? 'bg-yellow-100 text-yellow-700' :
                              'bg-gray-100 text-gray-700'
                            }`}>
                              {prospect.steps.email3?.status || 'N/A'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => stopSequence(selectedSequence)}
                  className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
                >
                  🛑 Arrêter cette séquence
                </button>
                <button
                  onClick={() => {
                    setSelectedSequence(null);
                    setSequenceDetails(null);
                  }}
                  className="px-4 py-2 text-gray-600 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
                >
                  Fermer
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EmailSequencer;