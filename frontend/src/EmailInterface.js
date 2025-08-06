import React, { useState, useEffect } from 'react';
import axios from 'axios';

const EmailInterface = () => {
  const [activeTab, setActiveTab] = useState('inbox');
  const [emails, setEmails] = useState([]);
  const [stats, setStats] = useState({ total: 0, unread: 0, sent: 0, received: 0 });
  const [loading, setLoading] = useState(false);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [composeData, setComposeData] = useState({
    to_email: '',
    subject: '',
    body: ''
  });
  const [simulateData, setSimulateData] = useState({
    from_email: '',
    subject: '',
    body: ''
  });

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    loadInboxData();
  }, []);

  const loadInboxData = async () => {
    try {
      setLoading(true);
      
      const token = localStorage.getItem('token');
      const config = {
        headers: { Authorization: `Bearer ${token}` }
      };

      // Charger les emails et statistiques
      const [emailsResponse, statsResponse] = await Promise.all([
        axios.get(`${backendUrl}/api/crm/emails/inbox`, config),
        axios.get(`${backendUrl}/api/crm/emails/stats`, config)
      ]);

      setEmails(emailsResponse.data.emails || []);
      setStats(statsResponse.data);
      
    } catch (error) {
      console.error('Erreur chargement données email:', error);
    } finally {
      setLoading(false);
    }
  };

  const sendEmail = async () => {
    try {
      setLoading(true);
      
      const token = localStorage.getItem('token');
      const config = {
        headers: { Authorization: `Bearer ${token}` }
      };

      await axios.post(`${backendUrl}/api/crm/emails/send`, composeData, config);
      
      // Réinitialiser le formulaire et recharger
      setComposeData({ to_email: '', subject: '', body: '' });
      setActiveTab('inbox');
      await loadInboxData();
      
      alert('Email envoyé avec succès!');
      
    } catch (error) {
      console.error('Erreur envoi email:', error);
      alert('Erreur lors de l\'envoi de l\'email');
    } finally {
      setLoading(false);
    }
  };

  const simulateIncomingEmail = async () => {
    try {
      setLoading(true);
      
      const token = localStorage.getItem('token');
      const config = {
        headers: { Authorization: `Bearer ${token}` }
      };

      await axios.post(`${backendUrl}/api/crm/emails/simulate-incoming`, simulateData, config);
      
      // Réinitialiser et recharger
      setSimulateData({ from_email: '', subject: '', body: '' });
      await loadInboxData();
      
      alert('Email entrant simulé! Un accusé de réception a été envoyé automatiquement.');
      
    } catch (error) {
      console.error('Erreur simulation email:', error);
      alert('Erreur lors de la simulation');
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (emailId) => {
    try {
      const token = localStorage.getItem('token');
      const config = {
        headers: { Authorization: `Bearer ${token}` }
      };

      await axios.post(`${backendUrl}/api/crm/emails/${emailId}/read`, {}, config);
      await loadInboxData();
      
    } catch (error) {
      console.error('Erreur marquage email:', error);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('fr-FR');
  };

  const getEmailTypeIcon = (email) => {
    if (email.type === 'sent') return '📤';
    if (email.type === 'auto_reply') return '🤖';
    return '📧';
  };

  return (
    <div className="p-6">
      {/* Header avec statistiques */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          📧 Interface Email Intégrée
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">{stats.total}</div>
            <div className="text-sm text-blue-800">Total</div>
          </div>
          <div className="bg-red-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-red-600">{stats.unread}</div>
            <div className="text-sm text-red-800">Non lus</div>
          </div>
          <div className="bg-green-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-green-600">{stats.sent}</div>
            <div className="text-sm text-green-800">Envoyés</div>
          </div>
          <div className="bg-purple-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-purple-600">{stats.received}</div>
            <div className="text-sm text-purple-800">Reçus</div>
          </div>
        </div>
      </div>

      {/* Navigation par onglets */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex space-x-8">
          {[
            { id: 'inbox', name: 'Boîte de réception', icon: '📥' },
            { id: 'compose', name: 'Nouveau message', icon: '✏️' },
            { id: 'simulate', name: 'Simuler email entrant', icon: '🎭' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.icon} {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Contenu des onglets */}
      {activeTab === 'inbox' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">📥 Boîte de réception</h3>
            <button
              onClick={loadInboxData}
              disabled={loading}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? '⏳' : '🔄'} Actualiser
            </button>
          </div>

          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            </div>
          ) : emails.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              Aucun email dans la boîte de réception
            </div>
          ) : (
            <div className="space-y-2">
              {emails.map((email) => (
                <div
                  key={email.id}
                  className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                    email.read ? 'bg-gray-50' : 'bg-white border-blue-200'
                  } hover:bg-gray-100`}
                  onClick={() => {
                    setSelectedEmail(selectedEmail?.id === email.id ? null : email);
                    if (!email.read) markAsRead(email.id);
                  }}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className="text-lg">{getEmailTypeIcon(email)}</span>
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <span className={`font-medium ${!email.read ? 'font-bold' : ''}`}>
                            {email.type === 'sent' ? `À: ${email.to_email}` : `De: ${email.from_email}`}
                          </span>
                          {!email.read && (
                            <span className="bg-red-500 text-white text-xs px-2 py-1 rounded-full">
                              Non lu
                            </span>
                          )}
                        </div>
                        <div className={`text-gray-900 ${!email.read ? 'font-semibold' : ''}`}>
                          {email.subject}
                        </div>
                        <div className="text-sm text-gray-500">
                          {formatDate(email.sent_at || email.received_at)}
                        </div>
                      </div>
                    </div>
                    <div className="text-gray-400">
                      {selectedEmail?.id === email.id ? '🔽' : '▶️'}
                    </div>
                  </div>

                  {/* Contenu développé */}
                  {selectedEmail?.id === email.id && (
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <div className="bg-gray-50 rounded-lg p-4">
                        <div className="whitespace-pre-wrap text-sm">
                          {email.body}
                        </div>
                        {email.reference && (
                          <div className="mt-2 text-xs text-gray-500">
                            Référence: {email.reference}
                          </div>
                        )}
                      </div>
                      <div className="mt-2 flex space-x-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setComposeData({
                              to_email: email.from_email,
                              subject: `Re: ${email.subject}`,
                              body: `\n\n---\n${email.body}`
                            });
                            setActiveTab('compose');
                          }}
                          className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
                        >
                          ↩️ Répondre
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'compose' && (
        <div className="max-w-2xl">
          <h3 className="text-lg font-semibold mb-4">✏️ Nouveau message</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Destinataire
              </label>
              <input
                type="email"
                value={composeData.to_email}
                onChange={(e) => setComposeData({...composeData, to_email: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="client@exemple.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Sujet
              </label>
              <input
                type="text"
                value={composeData.subject}
                onChange={(e) => setComposeData({...composeData, subject: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Sujet de votre message"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Message
              </label>
              <textarea
                value={composeData.body}
                onChange={(e) => setComposeData({...composeData, body: e.target.value})}
                rows="8"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Votre message..."
              />
            </div>

            <div className="flex space-x-3">
              <button
                onClick={sendEmail}
                disabled={loading || !composeData.to_email || !composeData.subject}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? '⏳ Envoi...' : '📤 Envoyer'}
              </button>
              <button
                onClick={() => setComposeData({ to_email: '', subject: '', body: '' })}
                className="bg-gray-300 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-400"
              >
                🗑️ Effacer
              </button>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'simulate' && (
        <div className="max-w-2xl">
          <h3 className="text-lg font-semibold mb-4">🎭 Simuler un email entrant</h3>
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
            <p className="text-sm text-yellow-800">
              <strong>Mode Démonstration :</strong> Cette fonction simule la réception d'un email 
              et déclenche automatiquement un accusé de réception personnalisé selon l'adresse 
              de destination.
            </p>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email de l'expéditeur (simulé)
              </label>
              <input
                type="email"
                value={simulateData.from_email}
                onChange={(e) => setSimulateData({...simulateData, from_email: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="client.prospect@exemple.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Sujet
              </label>
              <input
                type="text"
                value={simulateData.subject}
                onChange={(e) => setSimulateData({...simulateData, subject: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Demande d'information sur vos systèmes d'osmose inverse"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Message du prospect
              </label>
              <textarea
                value={simulateData.body}
                onChange={(e) => setSimulateData({...simulateData, body: e.target.value})}
                rows="6"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Bonjour, je suis intéressé par vos solutions d'osmose inverse pour ma maison. Pourriez-vous me faire parvenir un devis ? Cordialement,"
              />
            </div>

            <button
              onClick={simulateIncomingEmail}
              disabled={loading || !simulateData.from_email || !simulateData.subject}
              className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              {loading ? '⏳ Simulation...' : '🎭 Simuler réception + accusé automatique'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default EmailInterface;