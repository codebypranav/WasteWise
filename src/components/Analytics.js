import React, { useState, useEffect } from 'react';
import './Analytics.css';
import { fetchCurrentStats } from '../utils/api';

const Analytics = () => {
  const [stats, setStats] = useState({
    current: {
      recyclable: 0,
      organic: 0,
      nonRecyclable: 0
    }
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

  const efficiencyScore = Math.round((stats.current.recyclable + stats.current.organic) / 2);

  return (
    <div className="analytics">
      <h2>Waste Analytics</h2>
      
      <div className="analytics-grid">
        <div className="analytics-card">
          <h3>Efficiency Score</h3>
          <div className="efficiency-score">
            <div className="score-circle" style={{ '--score': `${efficiencyScore}%` }}>
              {efficiencyScore}%
            </div>
            <p>Overall waste management efficiency</p>
          </div>
        </div>

        <div className="analytics-card">
          <h3>Current Breakdown</h3>
          <div className="waste-breakdown">
            <div className="breakdown-bar">
              <div 
                className="bar-segment recyclable" 
                style={{ width: `${stats.current.recyclable}%` }}
              >
                {stats.current.recyclable}%
              </div>
              <div 
                className="bar-segment organic" 
                style={{ width: `${stats.current.organic}%` }}
              >
                {stats.current.organic}%
              </div>
              <div 
                className="bar-segment non-recyclable" 
                style={{ width: `${stats.current.nonRecyclable}%` }}
              >
                {stats.current.nonRecyclable}%
              </div>
            </div>
            <div className="breakdown-legend">
              <div className="legend-item">
                <span className="legend-color recyclable"></span>
                <span>Recyclable</span>
              </div>
              <div className="legend-item">
                <span className="legend-color organic"></span>
                <span>Organic</span>
              </div>
              <div className="legend-item">
                <span className="legend-color non-recyclable"></span>
                <span>Non-recyclable</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics; 