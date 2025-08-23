
import React, { useState, useEffect } from 'react';
import { Notification } from '@progress/kendo-react-notification';
import { Button } from '@progress/kendo-react-buttons';

const NotificationSystem = () => {
    const [notifications, setNotifications] = useState([]);

    const addNotification = (type, message) => {
        const notification = {
            id: Date.now(),
            type: type,
            message: message,
            time: new Date().toLocaleTimeString()
        };
        
        setNotifications(prev => [...prev, notification]);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            setNotifications(prev => prev.filter(n => n.id !== notification.id));
        }, 5000);
    };

    // Simulate real-time notifications
    useEffect(() => {
        const interval = setInterval(() => {
            const notificationTypes = [
                { type: 'success', message: 'Bet placed successfully!' },
                { type: 'info', message: 'New betting opportunity available' },
                { type: 'warning', message: 'High volatility detected in portfolio' },
                { type: 'error', message: 'Payment processing failed' }
            ];
            
            const randomNotification = notificationTypes[Math.floor(Math.random() * notificationTypes.length)];
            if (Math.random() > 0.7) { // 30% chance every 10 seconds
                addNotification(randomNotification.type, randomNotification.message);
            }
        }, 10000);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="notification-container">
            <div className="notification-controls">
                <Button 
                    themeColor="success" 
                    onClick={() => addNotification('success', 'Manual success notification')}
                >
                    Test Success
                </Button>
                <Button 
                    themeColor="info" 
                    onClick={() => addNotification('info', 'Manual info notification')}
                >
                    Test Info
                </Button>
                <Button 
                    themeColor="warning" 
                    onClick={() => addNotification('warning', 'Manual warning notification')}
                >
                    Test Warning
                </Button>
                <Button 
                    themeColor="error" 
                    onClick={() => addNotification('error', 'Manual error notification')}
                >
                    Test Error
                </Button>
            </div>
            
            <div className="notifications-list">
                {notifications.map(notification => (
                    <Notification
                        key={notification.id}
                        type={notification.type}
                        closable={true}
                        onClose={() => setNotifications(prev => prev.filter(n => n.id !== notification.id))}
                    >
                        <div className="notification-content">
                            <div className="notification-message">{notification.message}</div>
                            <div className="notification-time">{notification.time}</div>
                        </div>
                    </Notification>
                ))}
            </div>
        </div>
    );
};

export default NotificationSystem;
