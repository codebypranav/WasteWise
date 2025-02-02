import React, { useState, useEffect, useRef } from 'react';
import './Dashboard.css';
import { fetchCurrentStats, resetBin, fetchHistoricalStats, fetchAlerts } from '../utils/api';
import toast, { Toaster } from 'react-hot-toast';

const Dashboard = () => {
  const [stats, setStats] = useState({
    fillLevel: 0,
    current: {
      recyclable: 0,
      organic: 0,
      nonRecyclable: 0
    },
    temperature: 0
  });
  const [historicalStats, setHistoricalStats] = useState({
    history: [],
    averages: {
      recyclable: 0,
      organic: 0,
      nonRecyclable: 0,
      efficiency: 0,
      maxTemperature: 0,
      fillDuration: 0
    }
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
    // Fetch every 30 seconds
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const loadHistoricalStats = async () => {
      try {
        const data = await fetchHistoricalStats();
        setHistoricalStats(data);
      } catch (error) {
        console.error('Error fetching historical stats:', error);
      }
    };
    loadHistoricalStats();
  }, []);

  useEffect(() => {
    const fetchAlertData = async () => {
      try {
        const data = await fetchAlerts();
        // Check for new alerts by comparing with previous alerts
        if (previousAlerts.current.length > 0) {
          const newAlerts = data.filter(
            alert => !previousAlerts.current.find(
              prevAlert => prevAlert.id === alert.id
            )
          );
          
          // Show toast for each new alert
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
    if (window.confirm('Are you sure you want to reset the bin? This will archive current stats.')) {
      try {
        await resetBin();
        // Refresh both current and historical stats
        const [currentData, historicalData] = await Promise.all([
          fetchCurrentStats(),
          fetchHistoricalStats()
        ]);
        setStats(currentData);
        setHistoricalStats(historicalData);
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
        <h2>Waste Management Dashboard</h2>
        <div className="dashboard-actions">
          <button className="reset-btn" onClick={handleReset}>Reset Bin</button>
        </div>
      </div>
      <div className="dashboard-grid">
        <div className="dashboard-card">
          <h3>Current Fill Level</h3>
          <div className="fill-level">{stats.fillLevel}%</div>
        </div>
        <div className="dashboard-card">
          <h3>Current Temperature</h3>
          <div className="temperature">
            <span className={`temp-value ${stats.temperature > 100 ? 'high-temp' : ''}`}>
              {stats.temperature}°F
            </span>
          </div>
        </div>
        <div className="dashboard-card">
          <h3>Waste Classification</h3>
          <div className="waste-types">
            <div>Recyclable: {stats.current.recyclable}%</div>
            <div>Organic: {stats.current.organic}%</div>
            <div>Non-recyclable: {stats.current.nonRecyclable}%</div>
          </div>
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

      <h2>Historical Statistics</h2>
      <div className="dashboard-grid">
        <div className="dashboard-card">
          <h3>Average Composition</h3>
          <div className="waste-types">
            <div>Recyclable: {historicalStats.averages.recyclable}%</div>
            <div>Organic: {historicalStats.averages.organic}%</div>
            <div>Non-recyclable: {historicalStats.averages.nonRecyclable}%</div>
          </div>
        </div>

        <div className="dashboard-card">
          <h3>Performance Metrics</h3>
          <div className="metrics">
            <div>Average Efficiency: {historicalStats.averages.efficiency}%</div>
            <div>Average Max Temperature: {historicalStats.averages.maxTemperature}°F</div>
            <div>Average Fill Duration: {historicalStats.averages.fillDuration.toFixed(1)} hours</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 