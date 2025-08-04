import React, { useState, createContext, useContext } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const token = localStorage.getItem('crm_token');
    const userData = localStorage.getItem('crm_user');
    return token && userData ? JSON.parse(userData) : null;
  });

  const login = async (username, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, {
        username,
        password
      });

      const { access_token, user: userData } = response.data;
      
      localStorage.setItem('crm_token', access_token);
      localStorage.setItem('crm_user', JSON.stringify(userData));
      
      // Set default auth header
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      setUser(userData);
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('crm_token');
    localStorage.removeItem('crm_user');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
  };

  // Set auth header on app load
  React.useEffect(() => {
    const token = localStorage.getItem('crm_token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
  }, []);

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

const CRMLogin = ({ onLogin }) => {
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await login(credentials.username, credentials.password);
    
    if (result.success) {
      onLogin();
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  const handleDemoLogin = async (userEmail) => {
    setLoading(true);
    const passwordMap = {
      'antonio@josmose.com': 'Antonio@2024!Secure',
      'aziza@josmose.com': 'Aziza@2024!Director',
      'naima@josmose.com': 'Naima@2024!Commerce',
      'support@josmose.com': 'Support@2024!Help'
    };
    
    const result = await login(userEmail, passwordMap[userEmail]);
    if (result.success) {
      onLogin();
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        {/* Logo and Header */}
        <div className="text-center mb-8">
          <div className="mx-auto w-20 h-20 bg-white rounded-full flex items-center justify-center mb-4">
            <span className="text-3xl">💧</span>
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">
            Josmose CRM
          </h1>
          <p className="text-blue-200">
            Système de Gestion Commerciale
          </p>
        </div>

        {/* Login Form */}
        <div className="bg-white rounded-lg shadow-2xl p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            Connexion Équipe
          </h2>

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email Professionnel
              </label>
              <input
                type="email"
                required
                value={credentials.username}
                onChange={(e) => setCredentials({...credentials, username: e.target.value})}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                placeholder="votre.email@josmose.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Mot de passe
              </label>
              <input
                type="password"
                required
                value={credentials.password}
                onChange={(e) => setCredentials({...credentials, password: e.target.value})}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                placeholder="Votre mot de passe"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Connexion...' : 'Se Connecter 🔐'}
            </button>
          </form>

          {/* Demo Users */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <p className="text-sm text-gray-600 mb-4 text-center">
              Connexion rapide équipe :
            </p>
            
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => handleDemoLogin('naima')}
                disabled={loading}
                className="bg-purple-100 text-purple-800 py-2 px-3 rounded-lg text-sm font-medium hover:bg-purple-200 transition-colors disabled:opacity-50"
              >
                👩‍💼 Naima<br />
                <span className="text-xs">Manager</span>
              </button>
              
              <button
                onClick={() => handleDemoLogin('aziza')}
                disabled={loading}
                className="bg-green-100 text-green-800 py-2 px-3 rounded-lg text-sm font-medium hover:bg-green-200 transition-colors disabled:opacity-50"
              >
                👩‍💻 Aziza<br />
                <span className="text-xs">Agent</span>
              </button>
              
              <button
                onClick={() => handleDemoLogin('antonio')}
                disabled={loading}
                className="bg-blue-100 text-blue-800 py-2 px-3 rounded-lg text-sm font-medium hover:bg-blue-200 transition-colors disabled:opacity-50"
              >
                👨‍💻 Antonio<br />
                <span className="text-xs">Agent</span>
              </button>
              
              <button
                onClick={() => handleDemoLogin('support')}
                disabled={loading}
                className="bg-orange-100 text-orange-800 py-2 px-3 rounded-lg text-sm font-medium hover:bg-orange-200 transition-colors disabled:opacity-50"
              >
                🛠️ Support<br />
                <span className="text-xs">Technique</span>
              </button>
            </div>
          </div>

          {/* Info */}
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h4 className="text-sm font-medium text-gray-900 mb-2">
              🔒 Accès Sécurisé
            </h4>
            <ul className="text-xs text-gray-600 space-y-1">
              <li>• Session chiffrée 8 heures</li>
              <li>• Permissions par rôle</li>
              <li>• Logs d'activité complets</li>
              <li>• Protection données RGPD</li>
            </ul>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8 text-blue-200">
          <p className="text-sm">
            Josmose.com © 2024 | Système CRM & Marketing Automation
          </p>
        </div>
      </div>
    </div>
  );
};

export default CRMLogin;