
import React, { useState, useEffect } from 'react';
import { Chart, ChartTitle, ChartLegend, ChartTooltip, ChartSeries, ChartSeriesItem, ChartCategoryAxis, ChartCategoryAxisItem, ChartValueAxis, ChartValueAxisItem } from '@progress/kendo-react-charts';
import { Button } from '@progress/kendo-react-buttons';
import { Notification } from '@progress/kendo-react-notification';
import apiService from '../services/ApiService';

const PortfolioPerformanceChart = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [notification, setNotification] = useState(null);

    useEffect(() => {
        fetchPortfolioData();
    }, []);

    const fetchPortfolioData = async () => {
        try {
            setLoading(true);
            setError(null);

            const response = await apiService.getPortfolioPerformance();
            
            if (response.success) {
                setData(response.data);
                setNotification({
                    type: 'success',
                    message: 'Portfolio data updated successfully'
                });
            } else {
                setError(response.message || 'Failed to load portfolio data');
                setNotification({
                    type: 'error',
                    message: response.message || 'Failed to load portfolio data'
                });
            }
        } catch (err) {
            console.error('Error fetching portfolio data:', err);
            setError('Network error occurred');
            setNotification({
                type: 'error',
                message: 'Network error occurred'
            });
        } finally {
            setLoading(false);
        }
    };

    const handleRefresh = () => {
        fetchPortfolioData();
    };

    const closeNotification = () => {
        setNotification(null);
    };

    if (loading) {
        return (
            <div className="chart-container">
                <div style={{ textAlign: 'center', padding: '50px' }}>
                    <div className="k-loading"></div>
                    <p>Loading portfolio data...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="chart-container">
                <div style={{ textAlign: 'center', padding: '50px' }}>
                    <h3>Error Loading Data</h3>
                    <p>{error}</p>
                    <Button themeColor="primary" onClick={handleRefresh}>
                        Try Again
                    </Button>
                </div>
            </div>
        );
    }

    return (
        <div className="chart-container">
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
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <h3>Portfolio Performance Over Time</h3>
                <Button 
                    themeColor="primary" 
                    size="small" 
                    onClick={handleRefresh}
                    icon="refresh"
                >
                    Refresh
                </Button>
            </div>

            <Chart>
                <ChartTitle text="Portfolio Performance Over Time" />
                <ChartLegend position="bottom" orientation="horizontal" />
                <ChartTooltip 
                    visible={true} 
                    format="{0}"
                    template={(context) => {
                        const dataItem = context.dataItem;
                        return `
                            <div style="padding: 8px;">
                                <strong>Date:</strong> ${new Date(dataItem.date).toLocaleDateString()}<br/>
                                <strong>Value:</strong> $${dataItem.value?.toLocaleString()}<br/>
                                <strong>Profit:</strong> <span style="color: ${dataItem.profit >= 0 ? '#28a745' : '#dc3545'}">
                                    $${dataItem.profit?.toLocaleString()}
                                </span><br/>
                                <strong>ROI:</strong> <span style="color: ${dataItem.roi >= 0 ? '#28a745' : '#dc3545'}">
                                    ${dataItem.roi?.toFixed(2)}%
                                </span>
                            </div>
                        `;
                    }}
                />
                <ChartCategoryAxis>
                    <ChartCategoryAxisItem 
                        field="date" 
                        type="date"
                        baseUnit="days"
                        labels={{
                            format: "MMM dd",
                            rotation: -45
                        }}
                    />
                </ChartCategoryAxis>
                <ChartValueAxis>
                    <ChartValueAxisItem 
                        title={{ text: "Portfolio Value ($)" }}
                        labels={{ 
                            format: "${0:n0}",
                            step: 2
                        }}
                    />
                </ChartValueAxis>
                <ChartSeries>
                    <ChartSeriesItem 
                        type="line" 
                        field="value" 
                        name="Portfolio Value" 
                        color="#3f51b5"
                        markers={{
                            visible: true,
                            size: 6
                        }}
                        line={{
                            style: "smooth"
                        }}
                    />
                    <ChartSeriesItem 
                        type="column" 
                        field="profit" 
                        name="Daily Profit/Loss" 
                        color="#ff4081"
                        axis="profit"
                        gap={2}
                        spacing={0.1}
                    />
                </ChartSeries>
            </Chart>

            <div style={{ marginTop: '16px', fontSize: '14px', color: '#666' }}>
                <p>
                    📊 Data refreshed automatically every 5 minutes. 
                    Last update: {new Date().toLocaleTimeString()}
                </p>
                <p>
                    💡 Click and drag to zoom, double-click to reset zoom.
                </p>
            </div>
        </div>
    );
};

export default PortfolioPerformanceChart;
