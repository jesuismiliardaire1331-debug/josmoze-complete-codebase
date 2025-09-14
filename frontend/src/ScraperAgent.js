import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ScraperAgent = () => {
  const [scraperStatus, setScraperStatus] = useState({});
  const [domains, setDomains] = useState([]);
  const [sessionStats, setSessionStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [scheduledRunning, setScheduledRunning] = useState(false);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    loadScraperStatus();
    loadDomains();
  }, []);

  const loadScraperStatus = async () => {
    try {
      const response = await axios.get(`${backendUrl}/api/scraper/status`);
      setScraperStatus(response.data);
      setScheduledRunning(response.data.scraper_status.is_running);
    } catch (error) {
      console.error('Erreur chargement statut scraper:', error);
    }
  };

  const loadDomains = async () => {
    try {
      const response = await axios.get(`${backendUrl}/api/scraper/domains`);
      setDomains(response.data.allowed_domains || []);
    } catch (error) {
      console.error('Erreur chargement domaines:', error);
    }
  };

  const runManualSession = async (maxProspects = 50) => {
    if (!window.confirm(`⚠️ Lancer une session de scraping manuelle ?\n\nMax prospects: ${maxProspects}\n\nCela respecte la conformité GDPR : données publiques uniquement.`)) {
      return;
    }

    try {
      setLoading(true);
      const response = await axios.post(`${backendUrl}/api/scraper/run-session?max_prospects=${maxProspects}`);
      setSessionStats(response.data);
      await loadScraperStatus();
      alert(`✅ Session terminée !\n\nPages scrapées: ${response.data.stats.pages_scraped}\nProspects trouvés: ${response.data.stats.prospects_found}\nProspects sauvegardés: ${response.data.stats.prospects_saved}`);
    } catch (error) {
      console.error('Erreur session scraping:', error);
      alert('❌ Erreur lors du scraping');
    } finally {
      setLoading(false);
    }
  };

  const startScheduledScraping = async () => {
    if (!window.confirm('Démarrer le scraping automatique programmé ?\n\nFréquence: Toutes les 24h\nMax prospects: 25 par session')) {
      return;
    }

    try {
      const response = await axios.post(`${backendUrl}/api/scraper/start-scheduled?interval_hours=24`);
      alert(`✅ ${response.data.message}\n\nProchaine session: ${new Date(response.data.next_session).toLocaleString('fr-FR')}`);
      setScheduledRunning(true);
      await loadScraperStatus();
    } catch (error) {
      console.error('Erreur démarrage scraping programmé:', error);
      alert('❌ Erreur lors du démarrage');
    }
  };

  const stopScheduledScraping = async () => {
    if (!window.confirm('Arrêter le scraping automatique ?')) {
      return;
    }

    try {
      const response = await axios.post(`${backendUrl}/api/scraper/stop-scheduled`);
      alert(`✅ ${response.data.message}`);
      setScheduledRunning(false);
      await loadScraperStatus();
    } catch (error) {
      console.error('Erreur arrêt scraping:', error);
      alert('❌ Erreur lors de l\'arrêt');
    }
  };

  const testDomain = async (domain) => {
    try {
      setLoading(true);
      const response = await axios.post(`${backendUrl}/api/scraper/test-domain`, { domain });
      const result = response.data;
      
      alert(`🧪 Test de domaine: ${domain}\n\nRésultat: ${result.test_result}\nStatut robots.txt: ${result.robots_txt_status}\nTemps de réponse: ${result.response_time}\nProspects estimés: ${result.estimated_prospects}\nGDPR: ${result.gdpr_compliant ? '✅' : '❌'}`);
    } catch (error) {
      console.error('Erreur test domaine:', error);
      alert('❌ Erreur lors du test');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">🕷️ Scraper Osmoseurs France</h1>
          <p className="text-gray-600 mt-2">Agent IA de collecte prospects - Conforme GDPR</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => runManualSession(25)}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-medium"
          >
            {loading ? '⏳ En cours...' : '🚀 Session Manuelle'}
          </button>
          {scheduledRunning ? (
            <button
              onClick={stopScheduledScraping}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-medium"
            >
              ⏹️ Arrêter Auto
            </button>
          ) : (
            <button
              onClick={startScheduledScraping}
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium"
            >
              📅 Démarrer Auto
            </button>
          )}
        </div>
      </div>

      {/* Statut Agent */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-md border">
          <div className="flex items-center">
            <div className={`p-3 rounded-full ${scheduledRunning ? 'bg-green-100' : 'bg-gray-100'}`}>
              <span className={`text-xl ${scheduledRunning ? 'text-green-600' : 'text-gray-600'}`}>
                {scheduledRunning ? '🟢' : '⭕'}
              </span>
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Statut Agent</p>
              <p className="text-lg font-bold text-gray-900">
                {scheduledRunning ? 'Actif' : 'Arrêté'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md border">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-full">
              <span className="text-blue-600 text-xl">📊</span>
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Prospects 24h</p>
              <p className="text-2xl font-bold text-gray-900">
                {scraperStatus.statistics?.scraped_prospects_24h || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md border">
          <div className="flex items-center">
            <div className="p-3 bg-purple-100 rounded-full">
              <span className="text-purple-600 text-xl">🎯</span>
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Total Scrapés</p>
              <p className="text-2xl font-bold text-gray-900">
                {scraperStatus.statistics?.scraped_prospects_total || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md border">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-full">
              <span className="text-green-600 text-xl">✅</span>
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Taux Succès</p>
              <p className="text-2xl font-bold text-gray-900">
                {scraperStatus.statistics?.success_rate || 'N/A'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Mots-clés ciblés */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6 border">
        <h3 className="text-lg font-semibold mb-4">🎯 Mots-clés Ciblés</h3>
        <div className="flex flex-wrap gap-2">
          {scraperStatus.keywords_targeted?.map((keyword, index) => (
            <span 
              key={index}
              className="bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full"
            >
              {keyword}
            </span>
          ))}
        </div>
        <p className="text-sm text-gray-600 mt-3">
          L'agent recherche uniquement ces termes dans les forums français pour garantir la pertinence
        </p>
      </div>

      {/* Sources configurées */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6 border">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">🌐 Sources Autorisées ({domains.length})</h3>
          <button
            onClick={loadDomains}
            className="text-blue-600 hover:text-blue-800 text-sm"
          >
            🔄 Actualiser
          </button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {domains.map((domain, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4">
              <div className="flex justify-between items-start mb-2">
                <h4 className="font-medium text-gray-900">{domain.domain}</h4>
                <button
                  onClick={() => testDomain(domain.domain)}
                  disabled={loading}
                  className="text-xs bg-gray-100 hover:bg-gray-200 px-2 py-1 rounded disabled:opacity-50"
                >
                  🧪 Test
                </button>
              </div>
              <p className="text-sm text-gray-600 mb-2">{domain.type}</p>
              <div className="flex justify-between text-xs">
                <span className={`px-2 py-1 rounded ${domain.gdpr_compliant ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}`}>
                  {domain.gdpr_compliant ? '✅ GDPR' : '❌ Non conforme'}
                </span>
                <span className="text-gray-500">
                  {domain.avg_prospects_per_session} prospects/session
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Statistiques dernière session */}
      {sessionStats && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold text-green-800 mb-4">📊 Dernière Session Manuelle</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-green-600">Pages Scrapées</p>
              <p className="text-2xl font-bold text-green-800">{sessionStats.stats.pages_scraped}</p>
            </div>
            <div>
              <p className="text-sm text-green-600">Prospects Trouvés</p>
              <p className="text-2xl font-bold text-green-800">{sessionStats.stats.prospects_found}</p>
            </div>
            <div>
              <p className="text-sm text-green-600">Prospects Sauvés</p>
              <p className="text-2xl font-bold text-green-800">{sessionStats.stats.prospects_saved}</p>
            </div>
            <div>
              <p className="text-sm text-green-600">Durée</p>
              <p className="text-2xl font-bold text-green-800">{sessionStats.stats.duration_minutes?.toFixed(1)}min</p>
            </div>
          </div>
        </div>
      )}

      {/* Configuration Avancée */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6 border">
        <h3 className="text-lg font-semibold mb-4">⚙️ Sessions Manuelles</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => runManualSession(10)}
            disabled={loading}
            className="bg-yellow-500 hover:bg-yellow-600 disabled:bg-gray-400 text-white p-4 rounded-lg font-medium"
          >
            🐣 Session Légère
            <div className="text-sm opacity-90">Max 10 prospects</div>
          </button>
          <button
            onClick={() => runManualSession(25)}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white p-4 rounded-lg font-medium"
          >
            🎯 Session Standard
            <div className="text-sm opacity-90">Max 25 prospects</div>
          </button>
          <button
            onClick={() => runManualSession(50)}
            disabled={loading}
            className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white p-4 rounded-lg font-medium"
          >
            🚀 Session Intensive
            <div className="text-sm opacity-90">Max 50 prospects</div>
          </button>
        </div>
      </div>

      {/* Conformité GDPR */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-green-800 mb-4">⚖️ Conformité CNIL/GDPR</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-green-700">
          <div>
            ✅ <strong>Sources :</strong> Forums publics français uniquement<br/>
            ✅ <strong>Robots.txt :</strong> Vérification automatique<br/>
            ✅ <strong>Rate limiting :</strong> 2 secondes entre requêtes<br/>
            ✅ <strong>Contexte :</strong> Mots-clés eau/osmoseur uniquement
          </div>
          <div>
            ✅ <strong>Consentement :</strong> Intérêt légitime (données publiques)<br/>
            ✅ <strong>Opt-out :</strong> Token unique par prospect<br/>
            ✅ <strong>Rétention :</strong> 3 ans maximum<br/>
            ✅ <strong>Audit :</strong> Logs complets de toutes actions
          </div>
        </div>
        
        <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-yellow-800">
            <strong>⚠️ Utilisation Responsable :</strong> Cet agent collecte uniquement des données publiques 
            en contexte d'osmoseurs/filtration eau. Respecte robots.txt et inclut mécanismes d'opt-out conformes GDPR.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ScraperAgent;