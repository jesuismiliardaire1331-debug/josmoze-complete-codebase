import React from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import { AppProvider } from './context/AppContext';
import { AuthProvider } from './UserAuth';
import ChatBotV2 from "./ChatBot_V2";
import UserAuth from "./UserAuth";
import EspaceClient from "./EspaceClient";
import BlogPage from "./BlogPage";
import BlogArticle from "./BlogArticle";

// Test with blog components for BUG 3
const AppMinimal = () => {
  return (
    <AppProvider>
      <AuthProvider>
        <BrowserRouter>
          <div style={{padding: '20px', minHeight: '100vh'}}>
            <h1>🎉 JOSMOZE OSMOSEURS</h1>
            <p>Testing all resolved bugs + Blog content (BUG 3)</p>
            
            {/* Navigation for testing */}
            <nav style={{margin: '20px 0', padding: '10px', backgroundColor: '#f0f0f0', borderRadius: '5px'}}>
              <Link to="/" style={{marginRight: '15px', color: 'blue', textDecoration: 'none'}}>🏠 Accueil</Link>
              <Link to="/login" style={{marginRight: '15px', color: 'blue', textDecoration: 'none'}}>🔐 Connexion</Link>
              <Link to="/register" style={{marginRight: '15px', color: 'blue', textDecoration: 'none'}}>📝 Inscription</Link>
              <Link to="/espace-client" style={{marginRight: '15px', color: 'blue', textDecoration: 'none'}}>👤 Espace Client</Link>
              <Link to="/blog" style={{marginRight: '15px', color: 'blue', textDecoration: 'none'}}>📖 Blog</Link>
            </nav>
            
            <Routes>
              <Route path="/" element={
                <div style={{padding: '20px', backgroundColor: '#f9f9f9', borderRadius: '10px'}}>
                  <h2>🎉 Status des Bugs</h2>
                  <p style={{color: 'green', fontWeight: 'bold'}}>✅ BUG 1 (Thomas Chatbot): RÉSOLU</p>
                  <p style={{color: 'green', fontWeight: 'bold'}}>✅ BUG 2 (Authentication): RÉSOLU</p>
                  <p style={{color: 'orange', fontWeight: 'bold'}}>🔄 BUG 3 (Blog Content): EN TEST</p>
                  <p>📊 <strong>9/10 articles blog importés avec succès!</strong></p>
                  <p>Testez le lien "Blog" ci-dessus pour vérifier l'affichage des articles</p>
                </div>
              } />
              <Route path="/login" element={<UserAuth />} />
              <Route path="/register" element={<UserAuth />} />
              <Route path="/espace-client" element={<EspaceClient />} />
              <Route path="/blog" element={<BlogPage />} />
              <Route path="/blog/:slug" element={<BlogArticle />} />
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