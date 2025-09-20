import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AppProvider } from './context/AppContext';
import ChatBotV2 from "./ChatBot_V2";

// Test with just the chatbot to resolve BUG 1
const AppMinimal = () => {
  return (
    <AppProvider>
      <BrowserRouter>
        <div style={{padding: '20px', minHeight: '100vh'}}>
          <h1>🎉 JOSMOZE OSMOSEURS</h1>
          <p>Minimal app with Thomas chatbot</p>
          
          {/* Thomas Chatbot - THE FIX FOR BUG 1 */}
          <ChatBotV2 />
        </div>
      </BrowserRouter>
    </AppProvider>
  );
};

export default AppMinimal;