import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import CRMApp from './CRMApp';

/**
 * Point d'entrée pour l'application CRM dédiée
 * Utilisé quand le CRM est servi sous /crm avec basename
 */

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <CRMApp />
  </React.StrictMode>
);

// Hot Module Replacement pour le développement
if (module.hot) {
  module.hot.accept();
}