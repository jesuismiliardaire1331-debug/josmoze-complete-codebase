import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import { AppProvider } from './context/AppContext';

// Test with AppProvider
const TestWithContext = () => {
  console.log("🧪 TestWithContext rendering");
  return (
    <AppProvider>
      <div style={{padding: '20px'}}>
        <h1>🧪 CONTEXT TEST</h1>
        <p>Testing with AppProvider...</p>
      </div>
    </AppProvider>
  );
};

console.log("🧪 Mounting TestWithContext");
const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<TestWithContext />);
