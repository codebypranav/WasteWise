import React, { useState, useEffect } from 'react';
import './Settings.css';
import { fetchSettings, saveSettings } from '../utils/api';

const Settings = () => {
  const [settings, setSettings] = useState({
    notifications: {
      email: false,
      push: false,
      sms: false
    },
    thresholds: {
      capacity: 80
    }
  });
  const [saveStatus, setSaveStatus] = useState('');

  useEffect(() => {
    const loadSettings = async () => {
      try {
        const data = await fetchSettings();
        setSettings(data);
      } catch (error) {
        console.error('Error loading settings:', error);
      }
    };

    loadSettings();
  }, []);

  const handleNotificationChange = (type) => {
    setSettings(prev => ({
      ...prev,
      notifications: {
        ...prev.notifications,
        [type]: !prev.notifications[type]
      }
    }));
  };

  const handleThresholdChange = (value) => {
    setSettings(prev => ({
      ...prev,
      thresholds: {
        ...prev.thresholds,
        capacity: value
      }
    }));
  };

  const handleSave = async () => {
    try {
      setSaveStatus('Saving...');
      await saveSettings(settings);
      setSaveStatus('Settings saved successfully!');
      setTimeout(() => setSaveStatus(''), 3000);
    } catch (error) {
      console.error('Error saving settings:', error);
      setSaveStatus('Error saving settings');
      setTimeout(() => setSaveStatus(''), 3000);
    }
  };

  return (
    <div className="settings-container">
      <h2>System Settings</h2>
      <div className="settings-grid">
        <div className="settings-card">
          <h3>Notifications</h3>
          <div className="settings-options">
            <label className="toggle-switch">
              <input
                type="checkbox"
                checked={settings.notifications.email}
                onChange={() => handleNotificationChange('email')}
              />
              <span className="toggle-slider"></span>
              <span className="toggle-label">Email Notifications</span>
            </label>

            <label className="toggle-switch">
              <input
                type="checkbox"
                checked={settings.notifications.push}
                onChange={() => handleNotificationChange('push')}
              />
              <span className="toggle-slider"></span>
              <span className="toggle-label">Push Notifications</span>
            </label>

            <label className="toggle-switch">
              <input
                type="checkbox"
                checked={settings.notifications.sms}
                onChange={() => handleNotificationChange('sms')}
              />
              <span className="toggle-slider"></span>
              <span className="toggle-label">SMS Notifications</span>
            </label>
          </div>
        </div>

        <div className="settings-card">
          <h3>Alert Thresholds</h3>
          <div className="settings-options">
            <div className="threshold-setting">
              <label>Fill Level Alert Threshold (%)</label>
              <input
                type="range"
                min="50"
                max="95"
                value={settings.thresholds.capacity}
                onChange={(e) => handleThresholdChange(e.target.value)}
              />
              <span>{settings.thresholds.capacity}%</span>
            </div>
          </div>
        </div>
      </div>

      <div className="settings-actions">
        <button className="save-btn" onClick={handleSave}>Save Changes</button>
        {saveStatus && <div className="save-status">{saveStatus}</div>}
      </div>
    </div>
  );
};

export default Settings;