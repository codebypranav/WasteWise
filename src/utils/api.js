const API_BASE_URL = 'http://localhost:5000/api';

export const fetchCurrentStats = async () => {
  const response = await fetch(`${API_BASE_URL}/current-stats`);
  if (!response.ok) throw new Error('Failed to fetch current stats');
  return response.json();
};

export const fetchAlerts = async () => {
  const response = await fetch(`${API_BASE_URL}/alerts`);
  if (!response.ok) throw new Error('Failed to fetch alerts');
  return response.json();
};

export const fetchSettings = async () => {
  const response = await fetch(`${API_BASE_URL}/settings`);
  if (!response.ok) throw new Error('Failed to fetch settings');
  return response.json();
};

export const saveSettings = async (settings) => {
  const response = await fetch(`${API_BASE_URL}/settings`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(settings)
  });
  if (!response.ok) throw new Error('Failed to save settings');
  return response.json();
};

export const resetBin = async () => {
  const response = await fetch(`${API_BASE_URL}/reset-bin`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Failed to reset bin');
  return response.json();
};

export const fetchHistoricalStats = async () => {
  const response = await fetch(`${API_BASE_URL}/historical-stats`);
  if (!response.ok) throw new Error('Failed to fetch historical stats');
  return response.json();
};

export const dismissAlert = async (alertId) => {
  const response = await fetch(`${API_BASE_URL}/alerts/${alertId}/dismiss`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Failed to dismiss alert');
  return response.json();
}; 