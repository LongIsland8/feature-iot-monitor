// frontend/src/App.jsx

import React, { useState, useEffect } from 'react';

function App() {
  const [events, setEvents] = useState([]);
  const [filters, setFilters] = useState({ severity: '', sensor_id: '' });
  const [loading, setLoading] = useState(false);

  // Автоматическая загрузка каждые 3 секунды
  useEffect(() => {
    const fetchEvents = () => {
      setLoading(true);
      const params = new URLSearchParams();
      if (filters.severity) params.append('severity', filters.severity);
      if (filters.sensor_id) params.append('sensor_id', filters.sensor_id);

      fetch(`http://localhost:8000/api/events/?${params}`)
        .then(r => r.json())
        .then(data => {
          setEvents(data);
          setLoading(false);
        })
        .catch(err => {
          console.error("Ошибка загрузки:", err);
          setLoading(false);
        });
    };

    fetchEvents();
    const interval = setInterval(fetchEvents, 3000);
    return () => clearInterval(interval);
  }, [filters]);

  // Симуляция события
  const handleSimulate = () => {
    const temp = Math.random() > 0.5 ? 55 : 25; // critical или normal
    const data = {
      sensor_id: 'sim-' + Date.now(),
      location: 'Simulated Room',
      temperature: temp,
      humidity: 60,
      timestamp: new Date().toISOString(),
    };

    fetch('http://localhost:8000/webhooks/sensor', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }).then(() => alert('Событие отправлено!'));
  };

  // Статистика
  const total = events.length;
  const criticalToday = events.filter(e =>
    e.severity === 'critical' &&
    new Date(e.created_at).toDateString() === new Date().toDateString()
  ).length;

  const latest = events[0] || null;

  return (
    <div style={{ padding: 20, fontFamily: 'Arial, sans-serif', maxWidth: '1200px', margin: '0 auto' }}>
      <h1>📊 IoT Monitor Dashboard</h1>

      {/* Статистика */}
      <div style={{ display: 'flex', gap: 20, marginBottom: 30 }}>
        <div style={cardStyle}>Всего событий: <b>{total}</b></div>
        <div style={{ ...cardStyle, background: '#ffebee' }}>
          Critical сегодня: <b>{criticalToday}</b>
        </div>
        <div style={cardStyle}>
          Последнее: <b>{latest?.sensor_id || '-'}</b>
        </div>
      </div>

      {/* Управление */}
      <div style={{ marginBottom: 20 }}>
        <button onClick={handleSimulate} style={buttonStyle}>
          🔁 Симулировать датчик
        </button>
      </div>

      {/* Фильтры */}
      <div style={{ marginBottom: 20, display: 'flex', gap: 10, alignItems: 'center' }}>
        <input
          placeholder="Фильтр по sensor_id"
          value={filters.sensor_id}
          onChange={(e) => setFilters(f => ({ ...f, sensor_id: e.target.value }))}
          style={{ padding: '8px', borderRadius: 4, border: '1px solid #ccc' }}
        />
        <select
          value={filters.severity}
          onChange={(e) => setFilters(f => ({ ...f, severity: e.target.value }))}
          style={{ padding: '8px', borderRadius: 4, border: '1px solid #ccc' }}
        >
          <option value="">Все уровни</option>
          <option value="normal">Normal</option>
          <option value="warning">Warning</option>
          <option value="critical">Critical</option>
        </select>
      </div>

      {/* Таблица */}
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#f0f0f0', textAlign: 'left' }}>
              <th style={thStyle}>Время</th>
              <th style={thStyle}>Sensor ID</th>
              <th style={thStyle}>Location</th>
              <th style={thStyle}>Temp (°C)</th>
              <th style={thStyle}>Hum (%)</th>
              <th style={thStyle}>Severity</th>
              <th style={thStyle}>Notified</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan="7" style={{ textAlign: 'center', padding: '20px' }}>
                  Загрузка...
                </td>
              </tr>
            ) : events.length === 0 ? (
              <tr>
                <td colSpan="7" style={{ textAlign: 'center', padding: '20px', color: '#888' }}>
                  Нет данных
                </td>
              </tr>
            ) : (
              events.map(e => (
                <tr key={e.id} style={{
                  background: e.severity === 'critical' ? '#ffebee' :
                    e.severity === 'warning' ? '#fff3e0' : '#f9f9f9'
                }}>
                  <td style={tdStyle}>{new Date(e.created_at).toLocaleString()}</td>
                  <td style={tdStyle}>{e.sensor_id}</td>
                  <td style={tdStyle}>{e.location}</td>
                  <td style={tdStyle}>{e.temperature}</td>
                  <td style={tdStyle}>{e.humidity}</td>
                  <td style={tdStyle}>
                    <b style={{
                      color: e.severity === 'critical' ? '#c62828' :
                        e.severity === 'warning' ? '#fb8c00' : '#2e7d32'
                    }}>
                      {e.severity.toUpperCase()}
                    </b>
                  </td>
                  <td style={tdStyle}>{e.notification_sent ? '✅' : '❌'}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// Стили
const cardStyle = {
  border: '1px solid #ddd',
  padding: '15px',
  borderRadius: '8px',
  flex: 1,
  background: '#f9f9f9',
  textAlign: 'center'
};

const buttonStyle = {
  padding: '12px 24px',
  background: '#1976d2',
  color: 'white',
  border: 'none',
  borderRadius: '4px',
  cursor: 'pointer',
  fontWeight: 'bold'
};

const thStyle = {
  padding: '12px',
  borderBottom: '2px solid #ddd',
  textAlign: 'left',
  background: '#f5f5f5'
};

const tdStyle = {
  padding: '10px 12px',
  borderBottom: '1px solid #eee'
};

export default App;