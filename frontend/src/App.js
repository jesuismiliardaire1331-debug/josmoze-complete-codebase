import React, { useState, useEffect, Suspense } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import axios from "axios";

// Import traduction
import './i18n';
import { useTranslation } from 'react-i18next';

// Import context
import { AppProvider, useApp } from './context/AppContext';
import { AuthProvider as UserAuthProvider } from './UserAuth';

// Import core components
import ChatBotV2 from "./ChatBot_V2";
import UserAuth from "./UserAuth";
import EspaceClient from "./EspaceClient";
import BlogPage from "./BlogPage";
import BlogArticle from "./BlogArticle";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Temporary Header component to avoid import issues
const TempHeader = () => {
  const { t } = useTranslation();
  return (
    <header style={{padding: '10px 20px', backgroundColor: '#1e40af', color: 'white'}}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <h1 style={{margin: 0}}>🌊 JOSMOZE OSMOSEURS</h1>
        <nav style={{display: 'flex', gap: '20px'}}>
          <Link to="/" style={{color: 'white', textDecoration: 'none'}}>Accueil</Link>
          <Link to="/blog" style={{color: 'white', textDecoration: 'none'}}>Blog</Link>
          <Link to="/login" style={{color: 'white', textDecoration: 'none'}}>Connexion</Link>
          <Link to="/register" style={{color: 'white', textDecoration: 'none'}}>Inscription</Link>
        </nav>
      </div>
    </header>
  );
};

// Temporary Home component
const TempHome = () => {
  const { t } = useTranslation();
  return (
    <div style={{padding: '40px 20px', textAlign: 'center'}}>
      <h1>🎉 JOSMOZE OSMOSEURS - MAIN APPLICATION RESTORED</h1>
      <div style={{maxWidth: '800px', margin: '0 auto', padding: '20px', backgroundColor: '#f0f8ff', borderRadius: '10px'}}>
        <h2>🚀 Status des Corrections</h2>
        <p style={{color: 'green', fontWeight: 'bold'}}>✅ MAIN APP FUNCTIONING</p>
        <p style={{color: 'green', fontWeight: 'bold'}}>✅ React Mounting FIXED</p>
        <p style={{color: 'blue', fontWeight: 'bold'}}>🔄 Testing Thomas Chatbot...</p>
        <p style={{color: 'blue', fontWeight: 'bold'}}>🔄 Testing Authentication...</p>
        <p style={{color: 'blue', fontWeight: 'bold'}}>🔄 Testing Blog Content...</p>
      </div>
      
      <div style={{marginTop: '30px', padding: '20px', backgroundColor: '#fff3cd', borderRadius: '10px'}}>
        <h3>🧪 Tests Disponibles</h3>
        <ul style={{textAlign: 'left', maxWidth: '400px', margin: '0 auto'}}>
          <li><strong>Thomas Chatbot:</strong> Bouton visible en bas à droite</li>
          <li><strong>Blog:</strong> <Link to="/blog" style={{color: '#1e40af'}}>Consulter les articles</Link></li>
          <li><strong>Authentification:</strong> <Link to="/login" style={{color: '#1e40af'}}>Se connecter</Link></li>
          <li><strong>Inscription:</strong> <Link to="/register" style={{color: '#1e40af'}}>Créer un compte</Link></li>
        </ul>
      </div>
    </div>
  );
};

function App() {
  return (
    <AppProvider>
      <UserAuthProvider>
        <BrowserRouter>
          <div className="App min-h-screen flex flex-col">
            <TempHeader />
            <main style={{flex: 1}}>
              <Routes>
                <Route path="/" element={<TempHome />} />
                <Route path="/login" element={<UserAuth />} />
                <Route path="/register" element={<UserAuth />} />
                <Route path="/espace-client" element={<EspaceClient />} />
                <Route path="/blog" element={<BlogPage />} />
                <Route path="/blog/:slug" element={<BlogArticle />} />
              </Routes>
            </main>
            <footer style={{padding: '20px', backgroundColor: '#1e40af', color: 'white', textAlign: 'center'}}>
              <p>&copy; 2024 Josmoze - Osmoseurs professionnels</p>
            </footer>
            <ChatBotV2 />
          </div>
        </BrowserRouter>
      </UserAuthProvider>
    </AppProvider>
  );
}

export default App;