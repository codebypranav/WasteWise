import React, { useState, useEffect, useRef } from 'react';
import './Dashboard.css';
import { fetchCurrentStats, resetBin, fetchAlerts } from '../utils/api';
import toast, { Toaster } from 'react-hot-toast';

const Dashboard = () => {
  const [stats, setStats] = useState({
    fill_level: 0
  });
  const [alerts, setAlerts] = useState([]);
  const previousAlerts = useRef([]);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await fetchCurrentStats();
        setStats(data);
      } catch (error) {
        console.error('Error fetching stats:', error);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const fetchAlertData = async () => {
      try {
        const data = await fetchAlerts();
        if (previousAlerts.current.length > 0) {
          const newAlerts = data.filter(
            alert => !previousAlerts.current.find(
              prevAlert => prevAlert.id === alert.id
            )
          );
          
          newAlerts.forEach(alert => {
            toast(
              <div className="alert-toast">
                <div className="alert-toast-title">{alert.message}</div>
                <div className="alert-toast-location">{alert.location}</div>
              </div>,
              {
                duration: 5000,
                style: {
                  background: '#34495e',
                  color: '#fff',
                  padding: '16px',
                },
                icon: '⚠️',
              }
            );
          });
        }
        
        setAlerts(data);
        previousAlerts.current = data;
      } catch (error) {
        console.error('Error fetching alerts:', error);
      }
    };

    fetchAlertData();
    const interval = setInterval(fetchAlertData, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleReset = async () => {
    if (window.confirm('Are you sure you want to reset the bin?')) {
      try {
        await resetBin();
        const currentData = await fetchCurrentStats();
        setStats(currentData);
        toast.success('Bin reset successfully!', {
          duration: 3000,
          icon: '🔄'
        });
      } catch (error) {
        console.error('Error resetting bin:', error);
        toast.error('Failed to reset bin', {
          duration: 3000,
        });
      }
    }
  };

  return (
    <div className="dashboard">
      <Toaster 
        position="top-right"
        toastOptions={{
          className: '',
          style: {
            border: '1px solid var(--forest-green)',
            padding: '16px',
            color: '#713200',
          },
        }}
      />
      <div className="dashboard-header">
        <h2>Smart Bin Dashboard</h2>
        <div className="dashboard-actions">
          <button className="reset-btn" onClick={handleReset}>Reset Bin</button>
        </div>
      </div>
      <div className="dashboard-grid">
        <div className="dashboard-card">
          <h3>Current Fill Level</h3>
          <div className="fill-level">{stats.fill_level}%</div>
        </div>
        <div className="dashboard-card">
          <h3>Recent Alerts</h3>
          <div className="alerts-list">
            {alerts.length > 0 ? (
              alerts.slice(0, 2).map(alert => (
                <div key={alert.id} className="alert-item">
                  {alert.message} - {alert.timestamp}
                </div>
              ))
            ) : (
              <div className="alert-item">No recent alerts</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;