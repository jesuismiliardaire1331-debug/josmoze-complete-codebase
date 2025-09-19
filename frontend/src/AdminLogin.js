import React, { useState } from 'react';
import axios from 'axios';

const AdminLogin = () => {
  const [credentials, setCredentials] = useState({
    username: 'admin@josmoze.com',
    password: 'JosmozAdmin2025!'
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || window.location.origin;

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const response = await axios.post(`${backendUrl}/api/auth/login`, credentials);
      
      if (response.data.access_token) {
        setResult({
          success: true,
          message: 'Connexion réussie !',
          token: response.data.access_token,
          user: response.data.user
        });
        
        // Sauvegarder le token
        localStorage.setItem('admin_token', response.data.access_token);
      }
    } catch (error) {
      setResult({
        success: false,
        message: error.response?.data?.detail || 'Erreur de connexion'
      });
    }

    setLoading(false);
  };

  const testAdminEndpoint = async () => {
    const token = localStorage.getItem('admin_token');
    if (!token) {
      alert('Veuillez vous connecter d\'abord');
      return;
    }

    try {
      const response = await axios.get(`${backendUrl}/api/admin/media/library`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      alert(`Test réussi ! ${response.data.media_count} médias trouvés`);
    } catch (error) {
      alert(`Échec test admin: ${error.response?.data?.detail || error.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            🔧 Test Admin Josmoze
          </h1>
          <p className="text-gray-600">
            Interface de test pour l'accès administrateur
          </p>
        </div>

        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email Admin
            </label>
            <input
              type="email"
              value={credentials.username}
              onChange={(e) => setCredentials({...credentials, username: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Mot de passe
            </label>
            <input
              type="password"
              value={credentials.password}
              onChange={(e) => setCredentials({...credentials, password: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className={`w-full py-3 px-4 rounded-md font-semibold transition-colors ${
              loading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {loading ? '🔄 Connexion...' : '🔑 Se connecter'}
          </button>
        </form>

        {result && (
          <div className={`mt-6 p-4 rounded-lg ${
            result.success 
              ? 'bg-green-100 border border-green-300 text-green-800'
              : 'bg-red-100 border border-red-300 text-red-800'
          }`}>
            <p className="font-medium">
              {result.success ? '✅ Succès!' : '❌ Erreur!'}
            </p>
            <p className="text-sm mt-1">{result.message}</p>
            {result.success && result.user && (
              <div className="mt-3 text-xs">
                <p><strong>Utilisateur:</strong> {result.user.full_name}</p>
                <p><strong>Rôle:</strong> {result.user.role}</p>
                <p><strong>Département:</strong> {result.user.department}</p>
              </div>
            )}
          </div>
        )}

        {result?.success && (
          <div className="mt-6 space-y-3">
            <button
              onClick={testAdminEndpoint}
              className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition-colors"
            >
              🧪 Test Endpoint Admin
            </button>
            
            <button
              onClick={() => window.location.href = '/admin/upload'}
              className="w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 transition-colors"
            >
              📤 Interface Upload
            </button>
          </div>
        )}

        <div className="mt-8 text-center text-sm text-gray-500">
          <p>Identifiants de test :</p>
          <p className="font-mono bg-gray-100 p-2 rounded mt-2">
            admin@josmoze.com<br/>
            JosmozAdmin2025!
          </p>
        </div>
      </div>
    </div>
  );
};

export default AdminLogin;