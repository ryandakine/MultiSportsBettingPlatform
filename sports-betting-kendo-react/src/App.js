
import React, { useState, useEffect } from 'react';
import { Card, CardBody } from '@progress/kendo-react-layout';
import { Button } from '@progress/kendo-react-buttons';
import { DropDownList } from '@progress/kendo-react-dropdowns';
import { Notification } from '@progress/kendo-react-notification';
import ParlayMaker from './components/ParlayMaker';
import NotificationSystem from './components/NotificationSystem';
import UserManagement from './components/UserManagement';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import apiService from './services/ApiService';
import './App.css';

// Placeholder for chart-dependent components (Node 24 compatibility issue)
const ChartPlaceholder = ({ title }) => (
  <Card>
    <CardBody>
      <h3>{title}</h3>
      <div style={{
        height: '300px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#f8f9fa',
        borderRadius: '8px',
        color: '#666'
      }}>
        📊 Charts temporarily disabled due to Node 24 compatibility.
        <br />Use Node 20 LTS for full chart support.
      </div>
    </CardBody>
  </Card>
);

function App() {
  const [currentView, setCurrentView] = useState('parlay-maker'); // Default to Parlay Maker
  const [theme, setTheme] = useState('default');
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [notification, setNotification] = useState(null);

  const themes = [
    { text: 'Default Theme', value: 'default' },
    { text: 'Bootstrap Theme', value: 'bootstrap' },
    { text: 'Material Theme', value: 'material' },
    { text: 'Office 365 Theme', value: 'office365' }
  ];

  const views = [
    { text: 'AI Parlay Maker', value: 'parlay-maker', icon: '🎫' },
    { text: 'Sports Analytics', value: 'sports-analytics', icon: '🏀' },
    { text: 'Notifications', value: 'notifications', icon: '🔔' },
    { text: 'User Management', value: 'user-management', icon: '👥' },
    { text: 'Portfolio (Charts)', value: 'portfolio', icon: '📊' },
    { text: 'AI Predictions (Charts)', value: 'ai-predictions', icon: '🤖' },
    { text: 'Advanced Analytics (Charts)', value: 'analytics', icon: '📈' }
  ];

  useEffect(() => {
    checkAuthentication();
  }, []);

  const checkAuthentication = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (token) {
        const response = await apiService.getProfile();
        if (response.success) {
          setUser(response.user);
        } else {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
        }
      }
    } catch (error) {
      console.error('Authentication check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (credentials) => {
    try {
      const response = await apiService.login(credentials.username, credentials.password);
      if (response.success) {
        setUser(response.user);
        setNotification({ type: 'success', message: 'Login successful!' });
      } else {
        setNotification({ type: 'error', message: response.message || 'Login failed' });
      }
    } catch (error) {
      setNotification({ type: 'error', message: 'Login failed' });
    }
  };

  const handleLogout = async () => {
    try { await apiService.logout(); } catch (e) { console.error(e); }
    setUser(null);
    setNotification({ type: 'info', message: 'Logged out successfully' });
  };

  const closeNotification = () => setNotification(null);

  const renderView = () => {
    switch (currentView) {
      case 'parlay-maker':
        return <ParlayMaker />;
      case 'sports-analytics':
        return <AnalyticsDashboard />;
      case 'notifications':
        return <NotificationSystem />;
      case 'user-management':
        return <UserManagement />;
      case 'portfolio':
        return <ChartPlaceholder title="Portfolio Performance" />;
      case 'ai-predictions':
        return <ChartPlaceholder title="AI Predictions Dashboard" />;
      case 'analytics':
        return <ChartPlaceholder title="Advanced Analytics" />;
      default:
        return <ParlayMaker />;
    }
  };

  if (loading) {
    return (
      <div className="app">
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <div className="k-loading"></div>
          <p>Loading Sports Betting Platform...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`app theme-${theme}`}>
      {notification && (
        <Notification
          type={notification.type}
          closable={true}
          onClose={closeNotification}
          style={{ position: 'fixed', top: '20px', right: '20px', zIndex: 1000 }}
        >
          {notification.message}
        </Notification>
      )}

      {/* Header */}
      <Card style={{ marginBottom: '16px' }}>
        <CardBody>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
            <div>
              <h1 style={{ margin: '0 0 8px 0', fontSize: '28px', fontWeight: 'bold' }}>
                🏈 MultiSports Betting Platform
              </h1>
              <p style={{ margin: 0, color: '#666', fontSize: '14px' }}>
                Advanced sports betting with AI predictions and professional analytics
              </p>
            </div>

            <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
              <DropDownList
                data={themes}
                value={themes.find(t => t.value === theme)}
                onChange={(e) => setTheme(e.target.value)}
                textField="text"
                valueField="value"
                style={{ width: '150px' }}
              />

              {user ? (
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '14px', color: '#666' }}>
                    Welcome, {user.username}!
                  </span>
                  <Button themeColor="secondary" size="small" onClick={handleLogout}>
                    Logout
                  </Button>
                </div>
              ) : (
                <Button themeColor="primary" size="small" onClick={() => handleLogin({ username: 'demo', password: 'demo123' })}>
                  Demo Login
                </Button>
              )}
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Navigation */}
      <Card style={{ marginBottom: '16px' }}>
        <CardBody>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {views.map((view) => (
              <Button
                key={view.value}
                themeColor={currentView === view.value ? 'primary' : 'secondary'}
                size="small"
                onClick={() => setCurrentView(view.value)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  minWidth: 'auto',
                  padding: '8px 12px'
                }}
              >
                <span>{view.icon}</span>
                <span>{view.text}</span>
              </Button>
            ))}
          </div>
        </CardBody>
      </Card>

      {/* Main Content */}
      <div className="main-content">
        {renderView()}
      </div>

      {/* Footer */}
      <Card style={{ marginTop: '24px' }}>
        <CardBody>
          <div style={{ textAlign: 'center', fontSize: '14px', color: '#666' }}>
            <p style={{ margin: '0 0 8px 0' }}>
              🚀 MultiSports Betting Platform - Powered by Kendo React UI
            </p>
            <p style={{ margin: 0 }}>
              Real-time sports data • AI-powered predictions • Advanced analytics
            </p>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}

export default App;
