import React, { useState, useEffect } from 'react';
import './Alerts.css';
import { fetchAlerts, dismissAlert } from '../utils/api';

const Alerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [dismissStatus, setDismissStatus] = useState({});

  useEffect(() => {
    const fetchAlertData = async () => {
      try {
        const data = await fetchAlerts();
        setAlerts(data);
      } catch (error) {
        console.error('Error fetching alerts:', error);
      }
    };

    fetchAlertData();
    const interval = setInterval(fetchAlertData, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleDismiss = async (alertId) => {
    try {
      setDismissStatus(prev => ({ ...prev, [alertId]: 'Dismissing...' }));
      await dismissAlert(alertId);
      // Remove the dismissed alert from the state
      setAlerts(prev => prev.filter(alert => alert.id !== alertId));
      setDismissStatus(prev => ({ ...prev, [alertId]: 'Dismissed!' }));
      setTimeout(() => {
        setDismissStatus(prev => {
          const newStatus = { ...prev };
          delete newStatus[alertId];
          return newStatus;
        });
      }, 2000);
    } catch (error) {
      console.error('Error dismissing alert:', error);
      setDismissStatus(prev => ({ ...prev, [alertId]: 'Error dismissing' }));
      setTimeout(() => {
        setDismissStatus(prev => {
          const newStatus = { ...prev };
          delete newStatus[alertId];
          return newStatus;
        });
      }, 2000);
    }
  };

  return (
    <div className="alerts-container">
      <h2>System Alerts</h2>

      <div className="alerts-list">
        {alerts.map(alert => (
          <div key={alert.id} className="alert-card">
            <div className="alert-header">
              <h3>{alert.message}</h3>
            </div>
            <div className="alert-details">
              <div className="alert-location">
                <i className="location-icon">📍</i>
                {alert.location}
              </div>
              <div className="alert-time">
                <i className="time-icon">⏰</i>
                {alert.timestamp}
              </div>
            </div>
            <div className="alert-actions">
              <button 
                className="action-btn dismiss-btn"
                onClick={() => handleDismiss(alert.id)}
                disabled={dismissStatus[alert.id]}
              >
                {dismissStatus[alert.id] || 'Dismiss'}
              </button>
              <button className="action-btn">View Details</button>
            </div>
            {dismissStatus[alert.id] && (
              <div className="dismiss-status">{dismissStatus[alert.id]}</div>
            )}
          </div>
        ))}
        {alerts.length === 0 && (
          <div className="no-alerts">No active alerts</div>
        )}
      </div>
    </div>
  );
};

export default Alerts; 