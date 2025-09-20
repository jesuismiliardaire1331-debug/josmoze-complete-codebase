import React from "react";
import { AppProvider } from './context/AppContext';

// Minimal App to test what's breaking
const AppMinimal = () => {
  return (
    <AppProvider>
      <div style={{padding: '20px'}}>
        <h1>🎉 APP IS WORKING!</h1>
        <p>If you see this, the basic app structure is functional</p>
      </div>
    </AppProvider>
  );
};

export default AppMinimal;