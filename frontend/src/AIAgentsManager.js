import React, { useState, useEffect } from 'react';

const AIAgentsManager = () => {
    const [agentsData, setAgentsData] = useState(null);
    const [selectedAgent, setSelectedAgent] = useState(null);
    const [clientProfiles, setClientProfiles] = useState([]);
    const [analytics, setAnalytics] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('dashboard');

    const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

    // Load dashboard data
    useEffect(() => {
        loadAgentsDashboard();
        loadClientProfiles();
        loadAnalytics();
    }, []);

    const loadAgentsDashboard = async () => {
        try {
            const token = localStorage.getItem('crm_token');
            const response = await fetch(`${backendUrl}/api/crm/ai-agents/dashboard`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                const data = await response.json();
                setAgentsData(data);
            }
        } catch (error) {
            console.error('Erreur lors du chargement du dashboard agents:', error);
        }
    };

    const loadClientProfiles = async () => {
        try {
            const token = localStorage.getItem('crm_token');
            const response = await fetch(`${backendUrl}/api/crm/ai-agents/client-profiles`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                const data = await response.json();
                setClientProfiles(data.profiles || []);
            }
        } catch (error) {
            console.error('Erreur lors du chargement des profils:', error);
        }
    };

    const loadAnalytics = async () => {
        try {
            const token = localStorage.getItem('crm_token');
            const response = await fetch(`${backendUrl}/api/crm/ai-agents/performance-analytics`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                const data = await response.json();
                setAnalytics(data.analytics);
            }
            setLoading(false);
        } catch (error) {
            console.error('Erreur lors du chargement des analytics:', error);
            setLoading(false);
        }
    };

    const toggleAgentStatus = async (agentName, newStatus) => {
        try {
            const token = localStorage.getItem('crm_token');
            const response = await fetch(`${backendUrl}/api/crm/ai-agents/${agentName}/status`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ status: newStatus })
            });

            if (response.ok) {
                await loadAgentsDashboard(); // Reload data
                alert(`Agent ${agentName} mis à jour: ${newStatus}`);
            }
        } catch (error) {
            console.error('Erreur lors du changement de statut:', error);
            alert('Erreur lors du changement de statut');
        }
    };

    const triggerAbandonedCartRecovery = async () => {
        try {
            const token = localStorage.getItem('crm_token');
            const response = await fetch(`${backendUrl}/api/crm/ai-agents/abandoned-cart-recovery`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ hours_threshold: 2 })
            });

            if (response.ok) {
                const result = await response.json();
                alert(`Récupération lancée: ${result.abandoned_cart_recovery.recovery_attempts} paniers traités`);
            }
        } catch (error) {
            console.error('Erreur lors de la récupération:', error);
            alert('Erreur lors de la récupération des paniers');
        }
    };

    const bulkContact = async (agentName, filters) => {
        try {
            const token = localStorage.getItem('crm_token');
            const response = await fetch(`${backendUrl}/api/crm/ai-agents/bulk-contact`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    agent: agentName,
                    filters: filters,
                    message_type: agentName === 'aristote' ? 'call' : 'sms',
                    max_contacts: 20
                })
            });

            if (response.ok) {
                const result = await response.json();
                alert(`Contact en masse: ${result.bulk_contact_results.successfully_contacted} clients contactés`);
            }
        } catch (error) {
            console.error('Erreur lors du contact en masse:', error);
            alert('Erreur lors du contact en masse');
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                <span className="ml-4 text-gray-600">Chargement des agents IA...</span>
            </div>
        );
    }

    const getAgentEmoji = (agentName) => {
        const emojis = {
            socrate: '🧠', aristote: '📞', ciceron: '💬',
            demosthene: '🛒', platon: '📊'
        };
        return emojis[agentName] || '🤖';
    };

    const getAgentStatusColor = (status) => {
        const colors = {
            active: 'bg-green-500',
            inactive: 'bg-red-500',
            paused: 'bg-yellow-500',
            scheduled: 'bg-blue-500'
        };
        return colors[status] || 'bg-gray-500';
    };

    const renderDashboardTab = () => (
        <div className="space-y-6">
            {/* Header avec KPIs globaux */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-lg">
                <h2 className="text-2xl font-bold mb-4">🤖 Système d'Agents IA - Stratégies Schopenhauer</h2>
                {analytics && (
                    <div className="grid grid-cols-4 gap-4">
                        <div className="text-center">
                            <div className="text-3xl font-bold">{analytics.global_kpis?.total_interactions || 0}</div>
                            <div className="text-blue-200">Interactions Totales</div>
                        </div>
                        <div className="text-center">
                            <div className="text-3xl font-bold">{analytics.global_kpis?.satisfaction_score || 0}%</div>
                            <div className="text-blue-200">Satisfaction Client</div>
                        </div>
                        <div className="text-center">
                            <div className="text-3xl font-bold">{analytics.global_kpis?.average_response_time_seconds || 0}s</div>
                            <div className="text-blue-200">Temps de Réponse</div>
                        </div>
                        <div className="text-center">
                            <div className="text-3xl font-bold">
                                {analytics.global_kpis?.performance_status === 'exceeding_targets' ? '🎯' : '⚠️'}
                            </div>
                            <div className="text-blue-200">Performance</div>
                        </div>
                    </div>
                )}
            </div>

            {/* Agents Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {agentsData?.dashboard?.agents_status && Object.entries(agentsData.dashboard.agents_status).map(([agentKey, agent]) => (
                    <div key={agentKey} className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-blue-500">
                        <div className="flex justify-between items-start mb-4">
                            <div>
                                <h3 className="text-lg font-bold text-gray-800 flex items-center">
                                    {getAgentEmoji(agentKey)} {agent.name}
                                </h3>
                                <p className="text-sm text-gray-600 mt-1">{agent.specialty}</p>
                            </div>
                            <div className="flex items-center space-x-2">
                                <div className={`w-3 h-3 rounded-full ${getAgentStatusColor(agent.status)}`}></div>
                                <span className="text-sm font-medium text-gray-700 capitalize">{agent.status}</span>
                            </div>
                        </div>

                        {/* Performance Metrics */}
                        <div className="space-y-2 mb-4">
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-600">Conversations aujourd'hui:</span>
                                <span className="font-semibold">{agent.conversations_today || 0}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-600">Taux de conversion:</span>
                                <span className="font-semibold">{(agent.performance?.conversion_rate * 100 || 0).toFixed(1)}%</span>
                            </div>
                        </div>

                        {/* Working Hours */}
                        <div className="text-xs text-gray-500 mb-4">
                            {agent.working_hours?.always_active ? 
                                "🌍 Actif 24/7" : 
                                `🕘 ${agent.working_hours?.start_time}-${agent.working_hours?.end_time}`
                            }
                        </div>

                        {/* Controls */}
                        <div className="flex space-x-2">
                            <button
                                onClick={() => toggleAgentStatus(agentKey, agent.status === 'active' ? 'inactive' : 'active')}
                                className={`flex-1 py-2 px-3 rounded text-sm font-medium ${
                                    agent.status === 'active' 
                                        ? 'bg-red-500 hover:bg-red-600 text-white' 
                                        : 'bg-green-500 hover:bg-green-600 text-white'
                                }`}
                            >
                                {agent.status === 'active' ? 'DÉSACTIVER' : 'ACTIVER'}
                            </button>
                            <button
                                onClick={() => setSelectedAgent({...agent, key: agentKey})}
                                className="flex-1 py-2 px-3 bg-blue-500 hover:bg-blue-600 text-white rounded text-sm font-medium"
                            >
                                CONFIGURER
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            {/* Actions Rapides */}
            <div className="bg-white rounded-lg shadow-lg p-6">
                <h3 className="text-lg font-bold text-gray-800 mb-4">🚀 Actions Rapides</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <button
                        onClick={triggerAbandonedCartRecovery}
                        className="p-4 bg-orange-500 hover:bg-orange-600 text-white rounded-lg text-left"
                    >
                        <div className="text-lg font-semibold">🛒 Récupération Paniers</div>
                        <div className="text-sm opacity-90">Lancer Démosthène sur paniers abandonnés</div>
                    </button>
                    <button
                        onClick={() => bulkContact('ciceron', {high_conversion: true})}
                        className="p-4 bg-green-500 hover:bg-green-600 text-white rounded-lg text-left"
                    >
                        <div className="text-lg font-semibold">💬 SMS Prospects Chauds</div>
                        <div className="text-sm opacity-90">Contact masse clients à forte conversion</div>
                    </button>
                    <button
                        onClick={() => bulkContact('aristote', {personality: 'SKEPTIQUE'})}
                        className="p-4 bg-purple-500 hover:bg-purple-600 text-white rounded-lg text-left"
                    >
                        <div className="text-lg font-semibold">📞 Appels Sceptiques</div>
                        <div className="text-sm opacity-90">Aristote spécialisé objections</div>
                    </button>
                </div>
            </div>
        </div>
    );

    const renderAnalyticsTab = () => (
        <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-800">📊 Analytics Avancées - Stratégies Schopenhauer</h2>
            
            {/* Performance par Agent */}
            {analytics?.agent_performance && (
                <div className="bg-white rounded-lg shadow-lg p-6">
                    <h3 className="text-lg font-bold text-gray-800 mb-4">Performance par Agent</h3>
                    <div className="space-y-4">
                        {analytics.agent_performance.map((agent, idx) => (
                            <div key={idx} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                                <div className="flex items-center">
                                    <span className="text-2xl mr-3">{getAgentEmoji(agent._id)}</span>
                                    <div>
                                        <div className="font-semibold capitalize">{agent._id}</div>
                                        <div className="text-sm text-gray-600">
                                            {agent.total_interactions} interactions
                                        </div>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="font-semibold text-blue-600">
                                        {agent.avg_strategies_used?.toFixed(1) || 0} stratégies/conv
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Insights Personnalités */}
            {analytics?.personality_insights && (
                <div className="bg-white rounded-lg shadow-lg p-6">
                    <h3 className="text-lg font-bold text-gray-800 mb-4">🧠 Insights Personnalités Clients</h3>
                    <div className="grid grid-cols-2 gap-4">
                        {analytics.personality_insights.map((insight, idx) => (
                            <div key={idx} className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded">
                                <div className="font-semibold text-gray-800 capitalize">{insight._id?.toLowerCase()}</div>
                                <div className="text-sm text-gray-600 mt-1">{insight.count} clients</div>
                                <div className="mt-2">
                                    <div className="text-lg font-bold text-blue-600">
                                        {(insight.avg_conversion_probability * 100 || 0).toFixed(1)}%
                                    </div>
                                    <div className="text-xs text-gray-500">Taux conversion moyen</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Recommandations */}
            {analytics?.recommendations && (
                <div className="bg-white rounded-lg shadow-lg p-6">
                    <h3 className="text-lg font-bold text-gray-800 mb-4">💡 Recommandations IA</h3>
                    <div className="space-y-2">
                        {analytics.recommendations.map((rec, idx) => (
                            <div key={idx} className="p-3 bg-yellow-50 border-l-4 border-yellow-400 rounded">
                                <p className="text-gray-700">{rec}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );

    const renderClientsTab = () => (
        <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-800">👥 Profils Clients - Analyse Comportementale</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {clientProfiles.slice(0, 12).map((client, idx) => (
                    <div key={idx} className="bg-white rounded-lg shadow-lg p-4 border-l-4 border-green-500">
                        <div className="flex justify-between items-start mb-3">
                            <div>
                                <h3 className="font-bold text-gray-800">{client.name || 'Client Anonyme'}</h3>
                                <p className="text-sm text-gray-600">{client.email}</p>
                            </div>
                            <div className="text-right">
                                <div className="text-sm font-semibold text-blue-600 capitalize">
                                    {client.personality?.toLowerCase() || 'Non défini'}
                                </div>
                                {client.cart_abandoned && (
                                    <div className="text-xs text-red-600 mt-1">🛒 Panier abandonné</div>
                                )}
                            </div>
                        </div>

                        <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-600">Conversion:</span>
                                <div className="flex items-center">
                                    <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                                        <div 
                                            className="bg-green-500 h-2 rounded-full" 
                                            style={{width: `${(client.conversion_probability || 0) * 100}%`}}
                                        ></div>
                                    </div>
                                    <span className="font-semibold">{((client.conversion_probability || 0) * 100).toFixed(0)}%</span>
                                </div>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-600">Interactions:</span>
                                <span className="font-semibold">{client.interaction_history?.length || 0}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-600">Dernière activité:</span>
                                <span className="font-semibold text-xs">
                                    {client.last_interaction ? new Date(client.last_interaction).toLocaleDateString() : 'N/A'}
                                </span>
                            </div>
                        </div>

                        {client.objections_raised && client.objections_raised.length > 0 && (
                            <div className="mt-3 p-2 bg-red-50 rounded text-xs">
                                <div className="font-semibold text-red-800">Objections:</div>
                                <div className="text-red-600">{client.objections_raised.slice(0, 2).join(', ')}</div>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );

    return (
        <div className="p-6 max-w-7xl mx-auto">
            {/* Navigation Tabs */}
            <div className="flex space-x-1 mb-6">
                {[
                    { id: 'dashboard', name: '🤖 Dashboard Agents', icon: '🎯' },
                    { id: 'analytics', name: '📊 Analytics Avancées', icon: '📈' },
                    { id: 'clients', name: '👥 Profils Clients', icon: '👤' }
                ].map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`px-4 py-2 rounded-t-lg font-medium ${
                            activeTab === tab.id
                                ? 'bg-blue-600 text-white'
                                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                        }`}
                    >
                        {tab.icon} {tab.name}
                    </button>
                ))}
            </div>

            {/* Tab Content */}
            {activeTab === 'dashboard' && renderDashboardTab()}
            {activeTab === 'analytics' && renderAnalyticsTab()}
            {activeTab === 'clients' && renderClientsTab()}

            {/* Agent Configuration Modal */}
            {selectedAgent && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 w-96 max-w-90vw">
                        <h3 className="text-lg font-bold mb-4">
                            {getAgentEmoji(selectedAgent.key)} Configuration {selectedAgent.name}
                        </h3>
                        
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Spécialité:
                                </label>
                                <p className="text-sm text-gray-600">{selectedAgent.specialty}</p>
                            </div>
                            
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Horaires de travail:
                                </label>
                                <p className="text-sm text-gray-600">
                                    {selectedAgent.working_hours?.always_active 
                                        ? "Actif 24h/24, 7j/7" 
                                        : `${selectedAgent.working_hours?.start_time || '09:00'} - ${selectedAgent.working_hours?.end_time || '18:00'}`
                                    }
                                </p>
                            </div>
                            
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Performance:
                                </label>
                                <div className="text-sm space-y-1">
                                    <div>Conversion: {(selectedAgent.performance?.conversion_rate * 100 || 0).toFixed(1)}%</div>
                                    <div>Satisfaction: {(selectedAgent.performance?.satisfaction_score * 100 || 0).toFixed(1)}%</div>
                                </div>
                            </div>
                        </div>

                        <div className="flex justify-end space-x-3 mt-6">
                            <button
                                onClick={() => setSelectedAgent(null)}
                                className="px-4 py-2 text-gray-600 border rounded hover:bg-gray-50"
                            >
                                Fermer
                            </button>
                            <button
                                onClick={() => {
                                    toggleAgentStatus(selectedAgent.key, selectedAgent.status === 'active' ? 'inactive' : 'active');
                                    setSelectedAgent(null);
                                }}
                                className={`px-4 py-2 rounded text-white ${
                                    selectedAgent.status === 'active'
                                        ? 'bg-red-500 hover:bg-red-600'
                                        : 'bg-green-500 hover:bg-green-600'
                                }`}
                            >
                                {selectedAgent.status === 'active' ? 'Désactiver' : 'Activer'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AIAgentsManager;