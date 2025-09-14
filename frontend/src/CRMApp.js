import React, { Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import CRMLogin from './CRMLogin';
import CRMDashboard from './CRM';
import { NotificationProvider } from './NotificationSystem';

/**
 * Application CRM dédiée pour basename /crm
 * Séparée du site principal Josmoze
 */
const CRMApp = () => {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement du CRM...</p>
        </div>
      </div>
    }>
      <NotificationProvider>
        <div className="min-h-screen bg-gray-100">
          <BrowserRouter basename="/crm">
            <Routes>
              {/* Routes CRM */}
              <Route path="/login" element={<CRMLogin />} />
              <Route path="/dashboard" element={<CRMDashboard />} />
              <Route path="/" element={<Navigate to="/login" replace />} />
              
              {/* Redirection par défaut vers login */}
              <Route path="*" element={<Navigate to="/login" replace />} />
            </Routes>
          </BrowserRouter>
        </div>
      </NotificationProvider>
    </Suspense>
  );
};

export default CRMApp;