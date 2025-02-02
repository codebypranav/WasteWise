import React, { useState, useEffect } from 'react';
import './Analytics.css';
import { fetchCurrentStats } from '../utils/api';

const Analytics = () => {
  const [stats, setStats] = useState({
    fill_level: 0
  });

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

  return (
    <div className="analytics">
      <h2>Bin Analytics</h2>
      <div className="analytics-grid">
        <div className="analytics-card">
          <h3>Fill Level History</h3>
          <div className="efficiency-score">
            <div className="score-circle" style={{ '--score': `${stats.fill_level}%` }}>
              {stats.fill_level}%
            </div>
            <p>Current fill level</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;