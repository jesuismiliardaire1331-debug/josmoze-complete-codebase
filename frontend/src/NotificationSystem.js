import React, { useState, useEffect, useContext, createContext } from 'react';

// Notification Context
const NotificationContext = createContext();

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider');
  }
  return context;
};

// Notification Provider
export const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([]);

  const addNotification = (notification) => {
    const id = Date.now() + Math.random();
    const newNotification = {
      id,
      type: notification.type || 'info', // info, success, warning, error
      title: notification.title,
      message: notification.message,
      duration: notification.duration || 5000,
      timestamp: new Date()
    };

    setNotifications(prev => [...prev, newNotification]);

    // Auto-remove after duration
    if (newNotification.duration > 0) {
      setTimeout(() => {
        removeNotification(id);
      }, newNotification.duration);
    }
  };

  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(notif => notif.id !== id));
  };

  const clearAll = () => {
    setNotifications([]);
  };

  // Success helper
  const success = (title, message, duration = 4000) => {
    addNotification({ type: 'success', title, message, duration });
  };

  // Error helper
  const error = (title, message, duration = 6000) => {
    addNotification({ type: 'error', title, message, duration });
  };

  // Warning helper
  const warning = (title, message, duration = 5000) => {
    addNotification({ type: 'warning', title, message, duration });
  };

  // Info helper
  const info = (title, message, duration = 4000) => {
    addNotification({ type: 'info', title, message, duration });
  };

  const value = {
    notifications,
    addNotification,
    removeNotification,
    clearAll,
    success,
    error,
    warning,
    info
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
      <NotificationContainer notifications={notifications} onRemove={removeNotification} />
    </NotificationContext.Provider>
  );
};

// Notification Container Component
const NotificationContainer = ({ notifications, onRemove }) => {
  if (!notifications.length) return null;

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm">
      {notifications.map((notification) => (
        <NotificationItem
          key={notification.id}
          notification={notification}
          onRemove={onRemove}
        />
      ))}
    </div>
  );
};

// Individual Notification Component
const NotificationItem = ({ notification, onRemove }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isLeaving, setIsLeaving] = useState(false);

  useEffect(() => {
    // Trigger entrance animation
    setTimeout(() => setIsVisible(true), 50);
  }, []);

  const handleRemove = () => {
    setIsLeaving(true);
    setTimeout(() => onRemove(notification.id), 300);
  };

  const getIcon = () => {
    switch (notification.type) {
      case 'success':
        return '✅';
      case 'error':
        return '❌';
      case 'warning':
        return '⚠️';
      case 'info':
      default:
        return 'ℹ️';
    }
  };

  const getBackgroundColor = () => {
    switch (notification.type) {
      case 'success':
        return 'bg-green-50 border-green-200';
      case 'error':
        return 'bg-red-50 border-red-200';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200';
      case 'info':
      default:
        return 'bg-blue-50 border-blue-200';
    }
  };

  const getTextColor = () => {
    switch (notification.type) {
      case 'success':
        return 'text-green-900';
      case 'error':
        return 'text-red-900';
      case 'warning':
        return 'text-yellow-900';
      case 'info':
      default:
        return 'text-blue-900';
    }
  };

  const getBorderColor = () => {
    switch (notification.type) {
      case 'success':
        return 'border-l-green-500';
      case 'error':
        return 'border-l-red-500';
      case 'warning':
        return 'border-l-yellow-500';
      case 'info':
      default:
        return 'border-l-blue-500';
    }
  };

  return (
    <div
      className={`
        ${getBackgroundColor()} ${getBorderColor()} border-l-4 border rounded-lg shadow-lg p-4 
        transform transition-all duration-300 ease-in-out
        ${isVisible && !isLeaving ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'}
        ${isLeaving ? 'scale-95' : ''}
      `}
    >
      <div className="flex items-start">
        <div className="text-xl mr-3 flex-shrink-0">
          {getIcon()}
        </div>
        <div className="flex-1 min-w-0">
          <div className={`font-semibold text-sm ${getTextColor()}`}>
            {notification.title}
          </div>
          {notification.message && (
            <div className={`text-xs mt-1 ${getTextColor()} opacity-80`}>
              {notification.message}
            </div>
          )}
          <div className="text-xs mt-1 opacity-60">
            {notification.timestamp.toLocaleTimeString()}
          </div>
        </div>
        <button
          onClick={handleRemove}
          className={`ml-2 text-lg ${getTextColor()} opacity-60 hover:opacity-100 transition-opacity`}
        >
          ×
        </button>
      </div>
    </div>
  );
};

// Real-time notification service for CRM events
export class CRMNotificationService {
  constructor(notificationSystem) {
    this.notify = notificationSystem;
    this.setupEventListeners();
  }

  setupEventListeners() {
    // Listen for CRM events
    window.addEventListener('crm-lead-created', (event) => {
      this.notify.success(
        '🎉 Nouveau Lead',
        `${event.detail.name} s'est inscrit !`,
        5000
      );
    });

    window.addEventListener('crm-order-created', (event) => {
      this.notify.success(
        '💰 Nouvelle Commande',
        `Commande de ${event.detail.amount}€ reçue`,
        6000
      );
    });

    window.addEventListener('crm-stock-low', (event) => {
      this.notify.warning(
        '📦 Stock Faible',
        `${event.detail.product} : ${event.detail.quantity} restants`,
        8000
      );
    });

    window.addEventListener('crm-campaign-result', (event) => {
      this.notify.info(
        '📊 Résultat Campagne',
        `${event.detail.campaignName} : ${event.detail.result}`,
        5000
      );
    });

    window.addEventListener('crm-system-alert', (event) => {
      this.notify.error(
        '🚨 Alerte Système',
        event.detail.message,
        10000
      );
    });
  }

  // Manual notification methods
  leadCreated(leadData) {
    this.notify.success(
      '🎉 Nouveau Lead',
      `${leadData.name} (${leadData.email}) s'est inscrit`,
      5000
    );
  }

  orderReceived(orderData) {
    this.notify.success(
      '💰 Nouvelle Commande',
      `Commande #${orderData.id} - ${orderData.amount}€`,
      6000
    );
  }

  stockAlert(productName, quantity) {
    this.notify.warning(
      '📦 Stock Critique',
      `${productName} : seulement ${quantity} unités restantes`,
      8000
    );
  }

  campaignUpdate(campaignName, metrics) {
    this.notify.info(
      '📊 Mise à jour Campagne',
      `${campaignName} : ${metrics.clicks} clics, ${metrics.conversions} conversions`,
      5000
    );
  }

  systemError(message) {
    this.notify.error(
      '🚨 Erreur Système',
      message,
      10000
    );
  }

  systemSuccess(message) {
    this.notify.success(
      '✅ Opération Réussie',
      message,
      4000
    );
  }
}

// Custom hook for CRM notifications
export const useCRMNotifications = () => {
  const notifications = useNotifications();
  const [service, setService] = useState(null);

  useEffect(() => {
    const crmService = new CRMNotificationService(notifications);
    setService(crmService);
    
    return () => {
      // Cleanup event listeners if needed
    };
  }, [notifications]);

  return service;
};