import React from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import { AppProvider } from './context/AppContext';
import { AuthProvider } from './UserAuth';
import ChatBotV2 from "./ChatBot_V2";
import UserAuth from "./UserAuth";
import EspaceClient from "./EspaceClient";

// Test with authentication components for BUG 2
const AppMinimal = () => {
  return (
    <AppProvider>
      <AuthProvider>
        <BrowserRouter>
          <div style={{padding: '20px', minHeight: '100vh'}}>
            <h1>🎉 JOSMOZE OSMOSEURS</h1>
            <p>Testing authentication system - BUG 2</p>
            
            {/* Navigation for testing */}
            <nav style={{margin: '20px 0', padding: '10px', backgroundColor: '#f0f0f0', borderRadius: '5px'}}>
              <Link to="/" style={{marginRight: '20px', color: 'blue', textDecoration: 'none'}}>🏠 Accueil</Link>
              <Link to="/login" style={{marginRight: '20px', color: 'blue', textDecoration: 'none'}}>🔐 Se connecter</Link>
              <Link to="/register" style={{marginRight: '20px', color: 'blue', textDecoration: 'none'}}>📝 S'inscrire</Link>
              <Link to="/espace-client" style={{marginRight: '20px', color: 'blue', textDecoration: 'none'}}>👤 Espace Client</Link>
            </nav>
            
            <Routes>
              <Route path="/" element={
                <div style={{padding: '20px', backgroundColor: '#f9f9f9', borderRadius: '10px'}}>
                  <h2>🎉 Status des Bugs</h2>
                  <p style={{color: 'green', fontWeight: 'bold'}}>✅ BUG 1 (Thomas Chatbot): RÉSOLU</p>
                  <p style={{color: 'orange', fontWeight: 'bold'}}>🔄 BUG 2 (Authentication): EN TEST</p>
                  <p>Testez les liens ci-dessus pour vérifier l'authentification</p>
                </div>
              } />
              <Route path="/login" element={<UserAuth />} />
              <Route path="/register" element={<UserAuth />} />
              <Route path="/espace-client" element={<EspaceClient />} />
            </Routes>
            
            {/* Thomas Chatbot - BUG 1 RESOLVED */}
            <ChatBotV2 />
          </div>
        </BrowserRouter>
      </AuthProvider>
    </AppProvider>
  );
};

export default AppMinimal;