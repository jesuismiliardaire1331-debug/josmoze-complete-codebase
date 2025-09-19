import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const AIAgentsManager = () => {
    const navigate = useNavigate();
    
    // 4 AGENTS IA AUTOMATISÉS comme spécifié
    const [agents, setAgents] = useState([
        {
            id: 'product-hunter',
            name: 'Agent Product Hunter',
            description: 'Recherche automatique de produits tendances',
            icon: '🔍',
            status: true // ON par défaut
        },
        {
            id: 'content-creator',
            name: 'Agent Content Creator', 
            description: 'Génération automatique de descriptions',
            icon: '✍️',
            status: false // OFF par défaut
        },
        {
            id: 'email-marketer',
            name: 'Agent Email Marketer',
            description: 'Campagnes email automatisées',
            icon: '📧',
            status: true // ON par défaut
        },
        {
            id: 'seo-master',
            name: 'Agent SEO Master',
            description: 'Optimisation SEO automatique',
            icon: '🎯',
            status: false // OFF par défaut
        }
    ]);

    // Toggle agent status ON/OFF
    const toggleAgent = (agentId) => {
        setAgents(prev => prev.map(agent => 
            agent.id === agentId 
                ? { ...agent, status: !agent.status }
                : agent
        ));
    };

    // Navigation vers Agent AI Upload
    const navigateToAIUpload = () => {
        navigate('/admin/ai-upload');
    };

    return (
        <div className="p-6 max-w-4xl mx-auto">
            {/* Header */}
            <div className="text-center mb-8">
                <h1 className="text-3xl font-bold text-gray-800 mb-2">
                    🤖 AGENTS IA - GESTION INTELLIGENTE
                </h1>
                <p className="text-gray-600">Gérez vos agents d'intelligence artificielle automatisés</p>
            </div>

            {/* Container principal avec bordure */}
            <div className="bg-white rounded-xl shadow-lg border-2 border-gray-200 p-8">
                
                {/* 4 Agents IA */}
                <div className="space-y-4 mb-8">
                    {agents.map((agent) => (
                        <div key={agent.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                            {/* Agent Info */}
                            <div className="flex items-center space-x-3">
                                <span className="text-2xl">{agent.icon}</span>
                                <div>
                                    <h3 className="text-lg font-semibold text-gray-800">{agent.name}</h3>
                                    <p className="text-sm text-gray-600">{agent.description}</p>
                                </div>
                            </div>
                            
                            {/* Toggle Switch ON/OFF */}
                            <div className="flex items-center space-x-3">
                                <span className={`text-sm font-medium ${agent.status ? 'text-green-600' : 'text-gray-500'}`}>
                                    {agent.status ? 'ON' : 'OFF'}
                                </span>
                                <button
                                    onClick={() => toggleAgent(agent.id)}
                                    className={`relative inline-flex h-8 w-14 items-center rounded-full transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                                        agent.status ? 'bg-green-500' : 'bg-gray-300'
                                    }`}
                                >
                                    <span
                                        className={`inline-block h-6 w-6 transform rounded-full bg-white transition duration-200 ${
                                            agent.status ? 'translate-x-7' : 'translate-x-1'
                                        }`}
                                    />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Séparateur */}
                <div className="border-t border-gray-200 my-6"></div>

                {/* Bouton Agent AI Upload */}
                <div className="text-center">
                    <button
                        onClick={navigateToAIUpload}
                        className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white text-lg font-semibold rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
                    >
                        🚀 Accéder à l'Agent AI Upload
                    </button>
                </div>

                {/* Statistiques rapides */}
                <div className="mt-8 grid grid-cols-2 gap-4">
                    <div className="text-center p-4 bg-green-50 rounded-lg">
                        <div className="text-2xl font-bold text-green-600">
                            {agents.filter(agent => agent.status).length}
                        </div>
                        <div className="text-sm text-green-700">Agents Actifs</div>
                    </div>
                    <div className="text-center p-4 bg-blue-50 rounded-lg">
                        <div className="text-2xl font-bold text-blue-600">4</div>
                        <div className="text-sm text-blue-700">Agents Disponibles</div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AIAgentsManager;