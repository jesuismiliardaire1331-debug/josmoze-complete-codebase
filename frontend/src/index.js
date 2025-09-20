// Test React mounting directly - TEMPORARY
import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";

console.log("🧪 Index.js loaded");
console.log("🧪 React:", React);
console.log("🧪 ReactDOM:", ReactDOM);

const TestApp = () => {
  console.log("🧪 TestApp rendering");
  return (
    <div style={{padding: '20px', backgroundColor: '#f0f0f0', minHeight: '100vh'}}>
      <h1 style={{color: 'red'}}>🧪 REACT MOUNTING TEST</h1>
      <p>If you can see this, React is working!</p>
      <button onClick={() => alert('React is working!')}>Test Click</button>
    </div>
  );
};

console.log("🧪 About to get root element");
const rootElement = document.getElementById("root");
console.log("🧪 Root element:", rootElement);

if (rootElement) {
  try {
    console.log("🧪 Creating root...");
    const root = ReactDOM.createRoot(rootElement);
    console.log("🧪 Root created:", root);
    
    console.log("🧪 Rendering TestApp...");
    root.render(<TestApp />);
    console.log("🧪 TestApp rendered successfully");
  } catch (error) {
    console.error("🧪 Error during mounting:", error);
  }
} else {
  console.error("🧪 Root element not found!");
}
