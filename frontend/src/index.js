import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import { AppProvider } from './context/AppContext';
import App from "./App";

// Test with actual App component
const TestWithApp = () => {
  console.log("🧪 TestWithApp rendering");
  try {
    return (
      <AppProvider>
        <App />
      </AppProvider>
    );
  } catch (error) {
    console.error("🧪 Error rendering App:", error);
    return (
      <div style={{padding: '20px', color: 'red'}}>
        <h1>❌ APP ERROR</h1>
        <p>Error: {error.message}</p>
      </div>
    );
  }
};

console.log("🧪 Mounting TestWithApp");
const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<TestWithApp />);
