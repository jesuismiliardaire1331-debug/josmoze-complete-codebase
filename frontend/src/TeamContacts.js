import React, { useState, useEffect } from 'react';
import axios from 'axios';

const TeamContacts = () => {
  const [contacts, setContacts] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copiedEmail, setCopiedEmail] = useState('');

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    fetchTeamContacts();
  }, []);

  const fetchTeamContacts = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${backendUrl}/api/crm/team-contacts`);
      setContacts(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des contacts:', error);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (email) => {
    navigator.clipboard.writeText(email).then(() => {
      setCopiedEmail(email);
      setTimeout(() => setCopiedEmail(''), 2000);
    });
  };

  const sendEmail = (email, name) => {
    const subject = encodeURIComponent('Contact depuis le site Josmose.com');
    const body = encodeURIComponent(`Bonjour ${name},\n\nJe vous contacte concernant vos solutions d'osmose inverse.\n\nCordialement,`);
    window.open(`mailto:${email}?subject=${subject}&body=${body}`);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!contacts) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Impossible de charger les contacts</p>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          📧 Contacts d'Équipe @osmose.com
        </h2>
        <p className="text-gray-600">
          Adresses email professionnelles pour la communication avec clients et prospects
        </p>
      </div>

      {/* Informations générales */}
      <div className="bg-blue-50 rounded-lg p-4 mb-6">
        <h3 className="font-semibold text-blue-900 mb-2">🏢 Informations Générales</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div><span className="font-medium">Site web:</span> {contacts.contact_general.website}</div>
          <div><span className="font-medium">Domaine:</span> {contacts.contact_general.domain}</div>
          <div><span className="font-medium">Siège:</span> {contacts.contact_general.headquarters}</div>
          <div><span className="font-medium">Horaires:</span> {contacts.contact_general.business_hours}</div>
        </div>
      </div>

      {/* Managers */}
      <div className="mb-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          👑 Management - Équipe Dirigeante
          <span className="ml-2 bg-purple-100 text-purple-800 px-2 py-1 rounded-full text-sm">
            {contacts.managers.length}
          </span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {contacts.managers.map((manager, index) => (
            <div key={index} className="bg-white rounded-lg shadow-md p-4 border-l-4 border-purple-500">
              <div className="flex items-center mb-3">
                <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-600 rounded-full flex items-center justify-center text-white font-bold">
                  👑
                </div>
                <div className="ml-3">
                  <h4 className="font-semibold text-gray-900">{manager.name}</h4>
                  <p className="text-sm text-purple-600 font-medium">{manager.position}</p>
                </div>
              </div>
              
              <div className="space-y-2 mb-4">
                <div className="flex items-center text-sm">
                  <span className="w-2 h-2 bg-purple-500 rounded-full mr-2"></span>
                  <span className="text-gray-600">{manager.department}</span>
                </div>
                <div className="text-xs text-gray-500">
                  {manager.speciality}
                </div>
              </div>

              <div className="border-t pt-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-purple-900">Email professionnel:</span>
                </div>
                <div className="flex items-center space-x-2">
                  <code className="bg-purple-50 px-2 py-1 rounded text-sm flex-1">
                    {manager.email}
                  </code>
                  <button
                    onClick={() => copyToClipboard(manager.email)}
                    className="p-1 text-gray-500 hover:text-purple-600 transition-colors"
                    title="Copier l'email"
                  >
                    {copiedEmail === manager.email ? '✅' : '📋'}
                  </button>
                  <button
                    onClick={() => sendEmail(manager.email, manager.name)}
                    className="p-1 text-gray-500 hover:text-green-600 transition-colors"
                    title="Envoyer un email"
                  >
                    ✉️
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Agents */}
      {contacts.agents && (
        <div className="mb-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            👥 Agents Commerciaux
            <span className="ml-2 bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm">
              {contacts.agents.length}
            </span>
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {contacts.agents.map((agent, index) => (
              <div key={index} className="bg-white rounded-lg shadow-md p-4 border-l-4 border-blue-500">
                <div className="flex items-center mb-3">
                  <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-cyan-600 rounded-full flex items-center justify-center text-white font-bold">
                    👤
                  </div>
                  <div className="ml-3">
                    <h4 className="font-semibold text-gray-900">{agent.name}</h4>
                    <p className="text-sm text-blue-600 font-medium">{agent.position}</p>
                  </div>
                </div>
                
                <div className="space-y-2 mb-4">
                  <div className="flex items-center text-sm">
                    <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                    <span className="text-gray-600">{agent.department}</span>
                  </div>
                  <div className="text-xs text-gray-500">
                    {agent.speciality}
                  </div>
                </div>

                <div className="border-t pt-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-blue-900">Email professionnel:</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <code className="bg-blue-50 px-2 py-1 rounded text-sm flex-1">
                      {agent.email}
                    </code>
                    <button
                      onClick={() => copyToClipboard(agent.email)}
                      className="p-1 text-gray-500 hover:text-blue-600 transition-colors"
                      title="Copier l'email"
                    >
                      {copiedEmail === agent.email ? '✅' : '📋'}
                    </button>
                    <button
                      onClick={() => sendEmail(agent.email, agent.name)}
                      className="p-1 text-gray-500 hover:text-green-600 transition-colors"
                      title="Envoyer un email"
                    >
                      ✉️
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Services */}
      <div className="mb-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">🛠️ Services & Support</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {contacts.services.map((service, index) => (
            <div key={index} className="bg-white rounded-lg shadow-md p-4 border border-gray-200">
              <div className="flex items-center mb-3">
                <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-teal-600 rounded-full flex items-center justify-center text-white font-bold">
                  {service.name.charAt(0)}
                </div>
                <div className="ml-3">
                  <h4 className="font-semibold text-gray-900">{service.name}</h4>
                  <p className="text-sm text-gray-600">{service.position}</p>
                </div>
              </div>
              
              <div className="space-y-2 mb-4">
                <div className="flex items-center text-sm">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  <span className="text-gray-600">{service.department}</span>
                </div>
                <div className="text-xs text-gray-500">
                  {service.speciality}
                </div>
              </div>

              <div className="border-t pt-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Email professionnel:</span>
                </div>
                <div className="flex items-center space-x-2">
                  <code className="bg-gray-100 px-2 py-1 rounded text-sm flex-1">
                    {service.email}
                  </code>
                  <button
                    onClick={() => copyToClipboard(service.email)}
                    className="p-1 text-gray-500 hover:text-blue-600 transition-colors"
                    title="Copier l'email"
                  >
                    {copiedEmail === service.email ? '✅' : '📋'}
                  </button>
                  <button
                    onClick={() => sendEmail(service.email, service.name)}
                    className="p-1 text-gray-500 hover:text-green-600 transition-colors"
                    title="Envoyer un email"
                  >
                    ✉️
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Instructions d'utilisation */}
      <div className="bg-yellow-50 rounded-lg p-4">
        <h3 className="font-semibold text-yellow-900 mb-2">💡 Comment utiliser ces emails</h3>
        <div className="text-sm text-yellow-800 space-y-1">
          <p>• <strong>Clients existants:</strong> Utilisez les emails des managers pour un service personnalisé</p>
          <p>• <strong>Nouveaux prospects:</strong> Dirigez vers commercial@osmose.com pour les devis</p>
          <p>• <strong>Support technique:</strong> Utilisez support@osmose.com pour l'installation et maintenance</p>
          <p>• <strong>Direction générale:</strong> antonio@osmose.com pour les partenariats et décisions stratégiques</p>
        </div>
      </div>

      {/* Actions rapides */}
      <div className="mt-6 flex flex-wrap gap-2">
        <button
          onClick={() => copyToClipboard('commercial@osmose.com')}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm"
        >
          📧 Copier email commercial
        </button>
        <button
          onClick={() => copyToClipboard('support@osmose.com')}
          className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors text-sm"
        >
          🛠️ Copier email support
        </button>
        <button
          onClick={() => sendEmail('commercial@osmose.com', 'Service Commercial')}
          className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors text-sm"
        >
          ✉️ Nouveau devis
        </button>
      </div>
    </div>
  );
};

export default TeamContacts;