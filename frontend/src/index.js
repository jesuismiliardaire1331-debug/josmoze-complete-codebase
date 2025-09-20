import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";

// Minimal App component to test step by step
const MinimalApp = () => {
  console.log("🧪 MinimalApp rendering");
  return (
    <div style={{padding: '20px'}}>
      <h1>🧪 MINIMAL APP TEST</h1>
      <p>Testing basic app structure...</p>
    </div>
  );
};

console.log("🧪 Mounting MinimalApp");
const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<MinimalApp />);
