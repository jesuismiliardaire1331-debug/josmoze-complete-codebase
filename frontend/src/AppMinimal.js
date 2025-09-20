import React from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import { AppProvider } from './context/AppContext';
import ChatBotV2 from "./ChatBot_V2";
import UserAuth from "./UserAuth";
import EspaceClient from "./EspaceClient";

// Test with authentication components for BUG 2
const AppMinimal = () => {
  return (
    <AppProvider>
      <BrowserRouter>
        <div style={{padding: '20px', minHeight: '100vh'}}>
          <h1>🎉 JOSMOZE OSMOSEURS</h1>
          <p>Testing with authentication system</p>
          
          {/* Navigation for testing */}
          <nav style={{margin: '20px 0', padding: '10px', backgroundColor: '#f0f0f0'}}>
            <Link to="/login" style={{marginRight: '20px', color: 'blue'}}>Se connecter</Link>
            <Link to="/register" style={{marginRight: '20px', color: 'blue'}}>S'inscrire</Link>
            <Link to="/espace-client" style={{marginRight: '20px', color: 'blue'}}>Espace Client</Link>
          </nav>
          
          <Routes>
            <Route path="/" element={<div><h2>Page d'accueil</h2><p>BUG 1 (Chatbot) résolu ✅</p><p>Test BUG 2 (Authentication) en cours...</p></div>} />
            <Route path="/login" element={<UserAuth />} />
            <Route path="/register" element={<UserAuth />} />
            <Route path="/espace-client" element={<EspaceClient />} />
          </Routes>
          
          {/* Thomas Chatbot - BUG 1 RESOLVED */}
          <ChatBotV2 />
        </div>
      </BrowserRouter>
    </AppProvider>
  );
};

export default AppMinimal;