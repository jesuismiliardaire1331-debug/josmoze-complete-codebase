import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const AIAgentsManager = () => {
    const navigate = useNavigate();
    const [agentsStatus, setAgentsStatus] = useState({
        'product-hunter': { 
            name: 'Agent Product Hunter', 
            description: 'Recherche et analyse des tendances produits automatiquement',
            status: false,
            icon: '🔍'
        },
        'content-creator': { 
            name: 'Agent Content Creator', 
            description: 'Génération automatique de contenu marketing et articles',
            status: false,
            icon: '✍️'
        },
        'email-marketer': { 
            name: 'Agent Email Marketer', 
            description: 'Campagnes email automatisées et personnalisées',
            status: true,
            icon: '📧'
        },
        'seo-master': { 
            name: 'Agent SEO Master', 
            description: 'Optimisation SEO et référencement automatique',
            status: false,
            icon: '🎯'
        }
    });
    const [loading, setLoading] = useState(false);

    const backendUrl = process.env.REACT_APP_BACKEND_URL || 'https://josmoze.com';

    // Toggle agent status
    const toggleAgentStatus = (agentId) => {
        setLoading(true);
        
        // Simulate API call
        setTimeout(() => {
            setAgentsStatus(prev => ({
                ...prev,
                [agentId]: {
                    ...prev[agentId],
                    status: !prev[agentId].status
                }
            }));
            setLoading(false);
        }, 500);
    };

    // Navigate to AI Upload Agent
    const navigateToAIUpload = () => {
        navigate('/ai-upload-agent');
    };

    return (
        <div className="p-6 max-w-7xl mx-auto">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-800 mb-2 flex items-center">
                    🤖 AGENTS IA - GESTION INTELLIGENTE
                </h1>
                <p className="text-gray-600">Gérez vos agents d'intelligence artificielle et automatisez vos processus</p>
            </div>

            {/* Agents Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                {Object.entries(agentsStatus).map(([agentId, agent]) => (
                    <div key={agentId} className="bg-white rounded-xl shadow-lg border border-gray-200 p-6 hover:shadow-xl transition-all duration-200">
                        {/* Header avec icon et toggle */}
                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center space-x-3">
                                <span className="text-3xl">{agent.icon}</span>
                                <div>
                                    <h3 className="text-lg font-bold text-gray-800">{agent.name}</h3>
                                    <p className="text-sm text-gray-600">{agent.description}</p>
                                </div>
                            </div>
                            
                            {/* Toggle Switch */}
                            <div className="flex items-center space-x-2">
                                <span className={`text-sm font-medium ${agent.status ? 'text-green-600' : 'text-gray-500'}`}>
                                    {agent.status ? 'ON' : 'OFF'}
                                </span>
                                <button
                                    onClick={() => toggleAgentStatus(agentId)}
                                    disabled={loading}
                                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                                        agent.status ? 'bg-green-500' : 'bg-gray-300'
                                    }`}
                                >
                                    <span
                                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition duration-200 ${
                                            agent.status ? 'translate-x-6' : 'translate-x-1'
                                        }`}
                                    />
                                </button>
                            </div>
                        </div>

                        {/* Status and Configure */}
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-2">
                                <div className={`w-2 h-2 rounded-full ${agent.status ? 'bg-green-500' : 'bg-gray-400'}`}></div>
                                <span className="text-sm font-medium text-gray-700">
                                    {agent.status ? 'Actif' : 'Inactif'}
                                </span>
                            </div>
                            
                            <button 
                                className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium rounded-lg transition-colors duration-200"
                                onClick={() => alert(`Configuration de ${agent.name} (fonctionnalité à venir)`)}
                            >
                                Configurer
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            {/* AI Upload Agent Button */}
            <div className="bg-gradient-to-r from-indigo-600 to-purple-700 rounded-xl shadow-lg p-6 text-white">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-xl font-bold mb-2 flex items-center">
                            🚀 Agent AI Upload - Importation Intelligente
                        </h2>
                        <p className="text-indigo-100">
                            Scannez et importez automatiquement des produits depuis des sites e-commerce
                        </p>
                    </div>
                    <button
                        onClick={navigateToAIUpload}
                        className="bg-white text-indigo-600 hover:bg-indigo-50 px-6 py-3 rounded-lg font-semibold text-lg transition-colors duration-200 shadow-md hover:shadow-lg transform hover:scale-105"
                    >
                        🔗 Accéder à l'Agent AI Upload
                    </button>
                </div>
            </div>

            {/* Quick Stats */}
            <div className="mt-8">
                <h2 className="text-xl font-bold text-gray-800 mb-4">📊 Statistiques Rapides</h2>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
                        <div className="flex items-center">
                            <div className="flex-shrink-0">
                                <div className="text-2xl">🤖</div>
                            </div>
                            <div className="ml-3">
                                <p className="text-sm font-medium text-gray-500">Agents Actifs</p>
                                <p className="text-lg font-semibold text-gray-900">
                                    {Object.values(agentsStatus).filter(agent => agent.status).length}
                                </p>
                            </div>
                        </div>
                    </div>
                    
                    <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
                        <div className="flex items-center">
                            <div className="flex-shrink-0">
                                <div className="text-2xl">⚡</div>
                            </div>
                            <div className="ml-3">
                                <p className="text-sm font-medium text-gray-500">Automatisations</p>
                                <p className="text-lg font-semibold text-gray-900">4</p>
                            </div>
                        </div>
                    </div>
                    
                    <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
                        <div className="flex items-center">
                            <div className="flex-shrink-0">
                                <div className="text-2xl">📈</div>
                            </div>
                            <div className="ml-3">
                                <p className="text-sm font-medium text-gray-500">Performance</p>
                                <p className="text-lg font-semibold text-green-600">95%</p>
                            </div>
                        </div>
                    </div>
                    
                    <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
                        <div className="flex items-center">
                            <div className="flex-shrink-0">
                                <div className="text-2xl">🎯</div>
                            </div>
                            <div className="ml-3">
                                <p className="text-sm font-medium text-gray-500">Efficacité</p>
                                <p className="text-lg font-semibold text-blue-600">Optimal</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AIAgentsManager;