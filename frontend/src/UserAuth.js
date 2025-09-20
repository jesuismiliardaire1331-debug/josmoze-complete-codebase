import React, { useState, useContext, createContext } from 'react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Context pour l'authentification utilisateur
const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const token = localStorage.getItem('user_token');
    const userData = localStorage.getItem('user_data');
    if (token && userData) {
      try {
        return JSON.parse(userData);
      } catch (e) {
        localStorage.removeItem('user_token');
        localStorage.removeItem('user_data');
        return null;
      }
    }
    return null;
  });

  const login = async (email, password, rememberMe = false) => {
    try {
      const response = await axios.post(`${API_BASE}/api/auth/login`, {
        email,
        password,
        remember_me: rememberMe
      });

      if (response.data.success) {
        const { user: userData, token } = response.data;
        localStorage.setItem('user_token', token);
        localStorage.setItem('user_data', JSON.stringify(userData));
        setUser(userData);
        return { success: true };
      } else {
        return { success: false, error: response.data.error };
      }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Erreur de connexion' 
      };
    }
  };

  const register = async (userData) => {
    try {
      const response = await axios.post(`${API_BASE}/api/auth/register`, userData);

      if (response.data.success) {
        const { user: newUser, token } = response.data;
        localStorage.setItem('user_token', token);
        localStorage.setItem('user_data', JSON.stringify(newUser));
        setUser(newUser);
        return { success: true };
      } else {
        return { success: false, error: response.data.error };
      }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Erreur lors de l\'inscription' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('user_token');
    localStorage.removeItem('user_data');
    setUser(null);
  };

  const updateProfile = async (profileData) => {
    try {
      const token = localStorage.getItem('user_token');
      const response = await axios.put(`${API_BASE}/api/auth/profile`, profileData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        // Recharger les données utilisateur
        const profileResponse = await axios.get(`${API_BASE}/api/auth/profile`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        if (profileResponse.data.success) {
          const updatedUser = profileResponse.data.user;
          localStorage.setItem('user_data', JSON.stringify(updatedUser));
          setUser(updatedUser);
        }
        
        return { success: true };
      } else {
        return { success: false, error: response.data.error };
      }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Erreur de mise à jour' 
      };
    }
  };

  const getToken = () => localStorage.getItem('user_token');

  const value = {
    user,
    login,
    register,
    logout,
    updateProfile,
    getToken,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Composant de connexion/inscription
const UserAuth = ({ mode = 'login', onSuccess = () => {}, onToggleMode = () => {} }) => {
  const [currentMode, setCurrentMode] = useState(mode);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const { login, register } = useAuth();

  const [loginData, setLoginData] = useState({
    email: '',
    password: '',
    rememberMe: false
  });

  const [registerData, setRegisterData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
    phone: '',
    customer_type: 'B2C',
    company: '',
    accept_terms: false,
    newsletter: false
  });

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    const result = await login(loginData.email, loginData.password, loginData.rememberMe);
    
    if (result.success) {
      setMessage('✅ Connexion réussie !');
      onSuccess();
    } else {
      setMessage(`❌ ${result.error}`);
    }
    
    setLoading(false);
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    // Validation
    if (registerData.password !== registerData.confirmPassword) {
      setMessage('❌ Les mots de passe ne correspondent pas');
      setLoading(false);
      return;
    }

    if (!registerData.accept_terms) {
      setMessage('❌ Vous devez accepter les conditions d\'utilisation');
      setLoading(false);
      return;
    }

    const result = await register({
      email: registerData.email,
      password: registerData.password,
      first_name: registerData.first_name,
      last_name: registerData.last_name,
      phone: registerData.phone || null,
      customer_type: registerData.customer_type,
      company: registerData.company || null,
      accept_terms: registerData.accept_terms,
      newsletter: registerData.newsletter
    });
    
    if (result.success) {
      setMessage('✅ Inscription réussie !');
      onSuccess();
    } else {
      setMessage(`❌ ${result.error}`);
    }
    
    setLoading(false);
  };

  const toggleMode = () => {
    const newMode = currentMode === 'login' ? 'register' : 'login';
    setCurrentMode(newMode);
    setMessage('');
    onToggleMode(newMode);
  };

  return (
    <div className="max-w-md mx-auto bg-white rounded-lg shadow-lg p-6">
      {/* Header */}
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">
          {currentMode === 'login' ? '🔐 Connexion' : '📝 Inscription'}
        </h2>
        <p className="text-gray-600 mt-2">
          {currentMode === 'login' 
            ? 'Accédez à votre espace client Josmoze'
            : 'Créez votre compte pour profiter de tous nos avantages'
          }
        </p>
      </div>

      {/* Messages */}
      {message && (
        <div className={`p-3 rounded-lg mb-4 text-sm ${
          message.includes('✅') ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          {message}
        </div>
      )}

      {/* Formulaire de connexion */}
      {currentMode === 'login' && (
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email *
            </label>
            <input
              type="email"
              value={loginData.email}
              onChange={(e) => setLoginData({...loginData, email: e.target.value})}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="votre@email.com"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Mot de passe *
            </label>
            <input
              type="password"
              value={loginData.password}
              onChange={(e) => setLoginData({...loginData, password: e.target.value})}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="••••••••"
              required
            />
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="rememberMe"
              checked={loginData.rememberMe}
              onChange={(e) => setLoginData({...loginData, rememberMe: e.target.checked})}
              className="mr-2"
            />
            <label htmlFor="rememberMe" className="text-sm text-gray-600">
              Se souvenir de moi
            </label>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            {loading ? 'Connexion...' : 'Se connecter'}
          </button>
        </form>
      )}

      {/* Formulaire d'inscription */}
      {currentMode === 'register' && (
        <form onSubmit={handleRegister} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Prénom *
              </label>
              <input
                type="text"
                value={registerData.first_name}
                onChange={(e) => setRegisterData({...registerData, first_name: e.target.value})}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nom *
              </label>
              <input
                type="text"
                value={registerData.last_name}
                onChange={(e) => setRegisterData({...registerData, last_name: e.target.value})}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email *
            </label>
            <input
              type="email"
              value={registerData.email}
              onChange={(e) => setRegisterData({...registerData, email: e.target.value})}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="votre@email.com"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Téléphone
            </label>
            <input
              type="tel"
              value={registerData.phone}
              onChange={(e) => setRegisterData({...registerData, phone: e.target.value})}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="+33 1 23 45 67 89"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Type de client
            </label>
            <select
              value={registerData.customer_type}
              onChange={(e) => setRegisterData({...registerData, customer_type: e.target.value})}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="B2C">Particulier</option>
              <option value="B2B">Professionnel</option>
            </select>
          </div>

          {registerData.customer_type === 'B2B' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Entreprise
              </label>
              <input
                type="text"
                value={registerData.company}
                onChange={(e) => setRegisterData({...registerData, company: e.target.value})}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Nom de votre entreprise"
              />
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Mot de passe *
              </label>
              <input
                type="password"
                value={registerData.password}
                onChange={(e) => setRegisterData({...registerData, password: e.target.value})}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="••••••••"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Confirmer *
              </label>
              <input
                type="password"
                value={registerData.confirmPassword}
                onChange={(e) => setRegisterData({...registerData, confirmPassword: e.target.value})}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="••••••••"
                required
              />
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="acceptTerms"
                checked={registerData.accept_terms}
                onChange={(e) => setRegisterData({...registerData, accept_terms: e.target.checked})}
                className="mr-2"
                required
              />
              <label htmlFor="acceptTerms" className="text-sm text-gray-600">
                J'accepte les conditions d'utilisation *
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="newsletter"
                checked={registerData.newsletter}
                onChange={(e) => setRegisterData({...registerData, newsletter: e.target.checked})}
                className="mr-2"
              />
              <label htmlFor="newsletter" className="text-sm text-gray-600">
                Je souhaite recevoir la newsletter Josmoze
              </label>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-green-600 hover:bg-green-700 text-white p-3 rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            {loading ? 'Inscription...' : 'Créer mon compte'}
          </button>
        </form>
      )}

      {/* Toggle mode */}
      <div className="text-center mt-6">
        <button
          onClick={toggleMode}
          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          {currentMode === 'login' 
            ? "Pas encore de compte ? S'inscrire"
            : "Déjà un compte ? Se connecter"}
        </button>
      </div>
    </div>
  );
};

export default UserAuth;