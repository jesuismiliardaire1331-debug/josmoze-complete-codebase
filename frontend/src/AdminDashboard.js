import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const AdminDashboard = () => {
  const [user, setUser] = useState(null);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const backendUrl = process.env.REACT_APP_BACKEND_URL || window.location.origin;

  useEffect(() => {
    checkAuth();
    loadStats();
  }, []);

  const checkAuth = () => {
    const token = localStorage.getItem('admin_token');
    const userData = localStorage.getItem('admin_user');
    
    if (!token || !userData) {
      navigate('/admin/login');
      return;
    }

    try {
      setUser(JSON.parse(userData));
    } catch {
      navigate('/admin/login');
    }
  };

  const loadStats = async () => {
    try {
      // Simuler chargement des statistiques
      setStats({
        total_products: 12,
        pending_testimonials: 3,
        blog_articles: 3,
        imported_products: 5,
        active_agents: 2
      });
    } catch (error) {
      console.error('Erreur chargement stats:', error);
    }
    setLoading(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_user');
    navigate('/admin/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header Admin */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-gray-900">
                🔧 Dashboard Admin Josmoze
              </h1>
              <span className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full">
                Connecté
              </span>
            </div>
            
            <div className="flex items-center space-x-4">
              <span className="text-gray-600">
                👋 {user?.full_name || 'Admin'}
              </span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                Déconnexion
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats Overview */}
        <div className="grid md:grid-cols-5 gap-6 mb-8">
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Produits</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_products}</p>
              </div>
              <div className="text-3xl">📦</div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avis en attente</p>
                <p className="text-2xl font-bold text-gray-900">{stats.pending_testimonials}</p>
              </div>
              <div className="text-3xl">⭐</div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Articles Blog</p>
                <p className="text-2xl font-bold text-gray-900">{stats.blog_articles}</p>
              </div>
              <div className="text-3xl">📚</div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Importés AI</p>
                <p className="text-2xl font-bold text-gray-900">{stats.imported_products}</p>
              </div>
              <div className="text-3xl">🤖</div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Agents Actifs</p>
                <p className="text-2xl font-bold text-gray-900">{stats.active_agents}</p>
              </div>
              <div className="text-3xl">⚡</div>
            </div>
          </div>
        </div>

        {/* Actions Principales */}
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Gestion Produits */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              📦 Gestion Produits
            </h3>
            
            <div className="space-y-3">
              <button
                onClick={() => navigate('/admin/upload')}
                className="w-full text-left p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">📤</span>
                  <div>
                    <p className="font-medium text-blue-900">Upload Images Manuel</p>
                    <p className="text-sm text-blue-600">Ajouter images produits depuis PDF</p>
                  </div>
                </div>
              </button>

              <button
                onClick={() => navigate('/admin/ai-upload')}
                className="w-full text-left p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">🤖</span>
                  <div>
                    <p className="font-medium text-purple-900">Agent AI Upload</p>
                    <p className="text-sm text-purple-600">Import auto depuis AliExpress/Temu</p>
                  </div>
                </div>
              </button>

              <button
                className="w-full text-left p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">✏️</span>
                  <div>
                    <p className="font-medium text-green-900">Modifier Produits</p>
                    <p className="text-sm text-green-600">Prix, descriptions, stocks</p>
                  </div>
                </div>
              </button>
            </div>
          </div>

          {/* Gestion Contenu */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              📝 Gestion Contenu
            </h3>
            
            <div className="space-y-3">
              <button
                onClick={() => navigate('/blog')}
                className="w-full text-left p-4 bg-orange-50 rounded-lg hover:bg-orange-100 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">📚</span>
                  <div>
                    <p className="font-medium text-orange-900">Gestion Blog</p>
                    <p className="text-sm text-orange-600">Créer/modifier articles</p>
                  </div>
                </div>
              </button>

              <button
                onClick={() => navigate('/temoignages')}
                className="w-full text-left p-4 bg-yellow-50 rounded-lg hover:bg-yellow-100 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">⭐</span>
                  <div>
                    <p className="font-medium text-yellow-900">Modération Avis</p>
                    <p className="text-sm text-yellow-600">{stats.pending_testimonials} en attente</p>
                  </div>
                </div>
              </button>

              <button
                className="w-full text-left p-4 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">📊</span>
                  <div>
                    <p className="font-medium text-indigo-900">Analytics</p>
                    <p className="text-sm text-indigo-600">Statistiques du site</p>
                  </div>
                </div>
              </button>
            </div>
          </div>

          {/* Agents IA */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              🤖 Agents IA
            </h3>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <span className="text-xl">🕵️</span>
                  <div>
                    <p className="font-medium text-gray-900">Product Hunter</p>
                    <p className="text-xs text-gray-600">Recherche de produits</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="w-3 h-3 bg-green-500 rounded-full"></span>
                  <span className="text-sm text-gray-600">ON</span>
                </div>
              </div>

              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <span className="text-xl">✍️</span>
                  <div>
                    <p className="font-medium text-gray-900">Content Creator</p>
                    <p className="text-xs text-gray-600">Génération contenu</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="w-3 h-3 bg-green-500 rounded-full"></span>
                  <span className="text-sm text-gray-600">ON</span>
                </div>
              </div>

              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <span className="text-xl">📧</span>
                  <div>
                    <p className="font-medium text-gray-900">Email Marketer</p>
                    <p className="text-xs text-gray-600">Campagnes email</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="w-3 h-3 bg-red-500 rounded-full"></span>
                  <span className="text-sm text-gray-600">OFF</span>
                </div>
              </div>

              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <span className="text-xl">🔍</span>
                  <div>
                    <p className="font-medium text-gray-900">SEO Master</p>
                    <p className="text-xs text-gray-600">Optimisation SEO</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="w-3 h-3 bg-green-500 rounded-full"></span>
                  <span className="text-sm text-gray-600">ON</span>
                </div>
              </div>

              <button
                onClick={() => navigate('/admin/ai-upload')}
                className="w-full p-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-colors"
              >
                🚀 Accès Agent AI Upload
              </button>
            </div>
          </div>
        </div>

        {/* Actions Rapides */}
        <div className="mt-8 bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            ⚡ Actions Rapides
          </h3>
          
          <div className="grid md:grid-cols-4 gap-4">
            <button
              onClick={() => window.open('/', '_blank')}
              className="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors text-center"
            >
              <div className="text-2xl mb-2">🌐</div>
              <p className="font-medium text-gray-900">Voir Site</p>
            </button>

            <button
              onClick={() => navigate('/crm')}
              className="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors text-center"
            >
              <div className="text-2xl mb-2">🏢</div>
              <p className="font-medium text-gray-900">CRM</p>
            </button>

            <button
              className="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors text-center"
            >
              <div className="text-2xl mb-2">📈</div>
              <p className="font-medium text-gray-900">Ventes</p>
            </button>

            <button
              className="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors text-center"
            >
              <div className="text-2xl mb-2">⚙️</div>
              <p className="font-medium text-gray-900">Paramètres</p>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;