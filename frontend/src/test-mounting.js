// Test React mounting directly
import React from "react";
import ReactDOM from "react-dom/client";

console.log("🧪 Test mounting script loaded");
console.log("🧪 React:", React);
console.log("🧪 ReactDOM:", ReactDOM);

const TestComponent = () => {
  console.log("🧪 TestComponent rendering");
  return React.createElement('div', {}, 'TEST COMPONENT WORKING!');
};

// Try to mount immediately
const rootElement = document.getElementById("root");
console.log("🧪 Root element:", rootElement);

if (rootElement) {
  try {
    const root = ReactDOM.createRoot(rootElement);
    console.log("🧪 Root created:", root);
    
    root.render(React.createElement(TestComponent));
    console.log("🧪 Test component rendered");
  } catch (error) {
    console.error("🧪 Error creating/rendering:", error);
  }
} else {
  console.error("🧪 Root element not found!");
}