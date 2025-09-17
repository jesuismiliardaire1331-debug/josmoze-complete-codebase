import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { useSafeCleanup } from './hooks/useSafeCleanup';

// Configuration
const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Base de connaissances enrichie V2 (version frontend)
const KNOWLEDGE_BASE_V2 = {
  dangers_eau: {
    nitrates: {
      chiffres: "15% des communes dépassent les seuils, 142 cas de syndrome du bébé bleu depuis 2020",
      zones: "Bretagne (68% communes), Champagne-Ardenne (52%), Beauce (45%)",
      risques: "Empêchent le sang de transporter l'oxygène chez les bébés, +18% risque cancer colorectal"
    },
    pesticides: {
      chiffres: "5,7 pesticides différents par verre, 68% des points de contrôle contaminés",
      top_danger: "Glyphosate 65%, Atrazine 78%, Métolachlore 52%",
      zones: "Champagne-Ardenne 82%, Centre-Val Loire 79%"
    },
    chlore: {
      probleme: "Crée sous-produits cancérigènes (trihalométhanes)",
      impact: "Détruit la flore intestinale (-23% en 6 mois)"
    }
  },
  solutions: {
    carafe: "Inefficace sur nitrates/pesticides, juste améliore le goût",
    robinet: "70% pesticides mais 0% nitrates/virus/métaux",
    osmose: "99,9% élimination TOUT, seule solution complète"
  },
  josmoze: {
    efficacite: "98,5% nitrates, 99,2% pesticides, 99,8% chlore",
    prix: "890€ (au lieu de 1290€) = 37€/mois sur 24 mois",
    economies: "4800€ économisés sur 5 ans vs eau bouteille",
    garanties: "30 jours satisfait/remboursé, garantie 5 ans totale"
  },
  animaux: {
    fontaine: "49€ - Eau pure pour animaux avec filtration avancée",
    sac: "29€ - Transport premium avec purificateur d'air intégré", 
    distributeur: "39€ - Intelligent avec mini-fontaine intégrée",
    offre: "1 produit animal OFFERT avec chaque osmoseur"
  }
};

const ChatBot = () => {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [hasShownWelcome, setHasShownWelcome] = useState(false);
  const messagesEndRef = useRef(null);
  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
  const { safeSetTimeout, isMounted } = useSafeCleanup();

  // Messages d'accueil selon la langue
  const welcomeMessages = {
    fr: {
      initial: "👋 Salut ! Thomas, expert eau pure Josmoze. Préoccupé par votre eau du robinet ? Je peux vous éclairer sur les nitrates, pesticides, chlore... Comment puis-je vous aider ?",
      suggestions: [
        "💧 En savoir plus sur l'osmose inverse",
        "💰 Voir les prix et offres",
        "🔧 Comment ça fonctionne ?",
        "📞 Parler à un humain"
      ]
    },
    en: {
      initial: "👋 Hello! I'm Thomas, your water purification advisor. How can I help you?",
      suggestions: [
        "💧 Learn about reverse osmosis",
        "💰 See prices and offers", 
        "🔧 How does it work?",
        "📞 Talk to a human"
      ]
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && !hasShownWelcome) {
      // Détecter la langue automatiquement
      const currentLang = window.i18n?.language || 'fr';
      const isFrench = currentLang.startsWith('fr') || 
                      window.location.pathname.includes('/fr') ||
                      localStorage.getItem('i18nextLng')?.startsWith('fr') ||
                      true; // Par défaut français pour JOSMOSE.COM
      
      const currentLangCode = isFrench ? 'fr' : 'en';
      const welcome = welcomeMessages[currentLangCode];
      
      setMessages([
        {
          type: 'bot',
          content: welcome.initial,
          timestamp: new Date().toISOString(),
          suggestions: welcome.suggestions
        }
      ]);
      setHasShownWelcome(true);
    }
  }, [isOpen, hasShownWelcome]);

  // Afficher automatiquement après 10 secondes sur le site
  useEffect(() => {
    const timerId = safeSetTimeout(() => {
      if (!hasShownWelcome && !isOpen && isMounted()) {
        // Pulse animation pour attirer l'attention
        const chatButton = document.querySelector('.chatbot-button');
        if (chatButton) {
          chatButton.classList.add('animate-pulse');
          safeSetTimeout(() => {
            if (isMounted() && chatButton) {
              chatButton.classList.remove('animate-pulse');
            }
          }, 3000);
        }
      }
    }, 10000);

    return () => {
      // Cleanup is handled by useSafeCleanup
    };
  }, [hasShownWelcome, isOpen, safeSetTimeout, isMounted]);

  const sendMessage = async (message) => {
    if (!message.trim()) return;

    const userMessage = {
      type: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Détecter la langue pour Thomas
      const currentLang = window.i18n?.language || 'fr';
      const isFrench = currentLang.startsWith('fr') || 
                      localStorage.getItem('i18nextLng')?.startsWith('fr') ||
                      true; // Par défaut français
      
      console.log('🤖 Thomas sending message:', message, 'Language detected:', isFrench ? 'FR' : 'EN');

      // Appel à l'agent Thomas pour réponse intelligente
      const response = await axios.post(`${backendUrl}/api/ai-agents/chat`, {
        message: message,
        agent: 'thomas',
        context: 'website_chat',
        language: isFrench ? 'french' : 'english'
      }, {
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 10000 // 10 secondes timeout
      });

      console.log('🤖 Thomas response:', response.data);

      const botMessage = {
        type: 'bot',
        content: response.data.response || "Je vous écoute ! Comment puis-je vous aider avec nos systèmes de purification d'eau ?",
        timestamp: new Date().toISOString(),
        suggestions: response.data.suggestions || []
      };

      setMessages(prev => [...prev, botMessage]);

    } catch (error) {
      console.error('❌ Erreur chatbot:', error);
      
      // Réponse de fallback intelligente en français
      const fallbackMessage = {
        type: 'bot',
        content: "Je suis temporairement indisponible, mais notre équipe peut vous aider ! 📞 Appelez-nous ou envoyez un email à commercial@josmoze.com",
        timestamp: new Date().toISOString(),
        suggestions: ['💰 Voir les prix', '📞 Contacter l\'équipe', '💧 En savoir plus']
      };

      setMessages(prev => [...prev, fallbackMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    // Logique selon la suggestion
    if (suggestion.includes('prix') || suggestion.includes('prices')) {
      window.scrollTo({
        top: document.querySelector('#products-section')?.offsetTop || 0,
        behavior: 'smooth'
      });
      setIsOpen(false);
    } else if (suggestion.includes('humain') || suggestion.includes('human')) {
      window.location.href = '#contact';
      setIsOpen(false);
    } else {
      sendMessage(suggestion);
    }
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  if (!isOpen) {
    return (
      <div className="fixed bottom-6 right-6 z-50">
        <button
          onClick={toggleChat}
          className="chatbot-button bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white rounded-full p-4 shadow-lg transition-all duration-300 transform hover:scale-110"
          title={t('chatbot.open', 'Discuter avec Thomas')}
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          <div className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center animate-bounce">
            !
          </div>
        </button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Chat Window */}
      <div className="bg-white rounded-lg shadow-2xl border border-gray-200 w-96 h-96 flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-4 rounded-t-lg flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
            <div>
              <div className="font-semibold">💬 Thomas - Conseiller</div>
              <div className="text-xs opacity-90">Spécialiste purification</div>
            </div>
          </div>
          <button
            onClick={toggleChat}
            className="text-white hover:text-gray-200 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message, index) => (
            <div key={index} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.type === 'user' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-gray-100 text-gray-800'
              }`}>
                <div className="text-sm">{message.content}</div>
                
                {/* Suggestions */}
                {message.suggestions && message.suggestions.length > 0 && (
                  <div className="mt-2 space-y-1">
                    {message.suggestions.map((suggestion, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSuggestionClick(suggestion)}
                        className="block w-full text-left text-xs bg-white bg-opacity-20 hover:bg-opacity-30 rounded px-2 py-1 transition-colors"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-lg px-4 py-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-gray-200">
          <div className="flex space-x-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage(inputMessage)}
              placeholder={t('chatbot.placeholder', 'Tapez votre message...')}
              className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
            <button
              onClick={() => sendMessage(inputMessage)}
              disabled={isLoading || !inputMessage.trim()}
              className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 text-white px-4 py-2 rounded-lg transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
          
          <div className="text-xs text-gray-500 mt-2 text-center">
            🤖 Propulsé par IA • Réponses en temps réel
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatBot;