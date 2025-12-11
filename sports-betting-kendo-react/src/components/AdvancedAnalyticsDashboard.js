import React, { useState, useEffect } from 'react';
import { Card, CardBody } from '@progress/kendo-react-layout';
import { Chart, ChartSeries, ChartSeriesItem, ChartCategoryAxis, ChartCategoryAxisItem, ChartValueAxis, ChartValueAxisItem, ChartLegend, ChartTooltip } from '@progress/kendo-react-charts';
import { Grid, GridColumn } from '@progress/kendo-react-grid';
import { DropDownList } from '@progress/kendo-react-dropdowns';
import { Button } from '@progress/kendo-react-buttons';
import { Notification } from '@progress/kendo-react-notification';
import { CircularGauge } from '@progress/kendo-react-gauges';
import { ProgressBar } from '@progress/kendo-react-progressbars';
import { Badge } from '@progress/kendo-react-indicators';
import apiService from '../services/ApiService';
import realSportsApiService from '../services/RealSportsApiService';

const AdvancedAnalyticsDashboard = () => {
    const [analyticsData, setAnalyticsData] = useState(null);
    const [sportPerformance, setSportPerformance] = useState([]);
    const [riskAnalysis, setRiskAnalysis] = useState(null);
    const [insights, setInsights] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [notification, setNotification] = useState(null);
    const [selectedTimeframe, setSelectedTimeframe] = useState('30d');
    const [selectedSport, setSelectedSport] = useState('all');
    const [refreshInterval, setRefreshInterval] = useState(null);

    const timeframes = [
        { text: 'Last 7 Days', value: '7d' },
        { text: 'Last 30 Days', value: '30d' },
        { text: 'Last 90 Days', value: '90d' },
        { text: 'All Time', value: 'all' }
    ];

    const sports = [
        { text: 'All Sports', value: 'all' },
        { text: 'NFL Football', value: 'nfl' },
        { text: 'NCAAB Men\'s', value: 'ncaab' },
        { text: 'NCAAB Women\'s', value: 'ncaaw' },
        { text: 'WNBA Basketball', value: 'wnba' },
        { text: 'MLB Baseball', value: 'mlb' },
        { text: 'NHL Hockey', value: 'nhl' }
    ];

    useEffect(() => {
        fetchAnalyticsData();
        setupAutoRefresh();

        return () => {
            if (refreshInterval) {
                clearInterval(refreshInterval);
            }
        };
    }, [selectedTimeframe, selectedSport]);

    const setupAutoRefresh = () => {
        // Refresh data every 5 minutes
        const interval = setInterval(() => {
            fetchAnalyticsData();
        }, 5 * 60 * 1000);

        setRefreshInterval(interval);
    };

    const fetchAnalyticsData = async () => {
        try {
            setLoading(true);
            setError(null);

            // Fetch user performance metrics
            const metricsResponse = await apiService.getPortfolioPerformance();
            if (metricsResponse.success) {
                setAnalyticsData(metricsResponse.data);
            }

            // Fetch sport performance
            const sportResponse = await apiService.getSportPerformance(selectedSport);
            if (sportResponse.success) {
                setSportPerformance(sportResponse.data);
            }

            // Fetch risk analysis
            const riskResponse = await apiService.getRiskAnalysis();
            if (riskResponse.success) {
                setRiskAnalysis(riskResponse.data);
            }

            // Fetch AI insights
            const insightsResponse = await apiService.getAnalyticsInsights();
            if (insightsResponse.success) {
                setInsights(insightsResponse.data);
            }

            setNotification({
                type: 'success',
                message: 'Analytics data updated successfully'
            });

        } catch (err) {
            console.error('Error fetching analytics data:', err);
            setError('Failed to load analytics data');
            setNotification({
                type: 'error',
                message: 'Error loading analytics data'
            });
        } finally {
            setLoading(false);
        }
    };

    const closeNotification = () => {
        setNotification(null);
    };

    const getRiskLevelColor = (riskLevel) => {
        switch (riskLevel?.toLowerCase()) {
            case 'low': return '#28a745';
            case 'medium': return '#ffc107';
            case 'high': return '#fd7e14';
            case 'extreme': return '#dc3545';
            default: return '#6c757d';
        }
    };

    const getPerformanceColor = (roi) => {
        if (roi > 10) return '#28a745';
        if (roi > 0) return '#17a2b8';
        if (roi > -10) return '#ffc107';
        return '#dc3545';
    };

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    };

    const formatPercentage = (value) => {
        return `${value > 0 ? '+' : ''}${value.toFixed(1)}%`;
    };

    if (loading && !analyticsData) {
        return (
            <div className="analytics-dashboard">
                <div style={{ textAlign: 'center', padding: '50px' }}>
                    <div className="k-loading"></div>
                    <p>Loading advanced analytics...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="analytics-dashboard">
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
                            <h2 style={{ margin: '0 0 8px 0' }}>Advanced Analytics Dashboard</h2>
                            <p style={{ margin: 0, color: '#666', fontSize: '14px' }}>
                                Real-time performance tracking, risk analysis, and AI-powered insights
                            </p>
                        </div>

                        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                            <DropDownList
                                data={timeframes}
                                value={timeframes.find(t => t.value === selectedTimeframe)}
                                onChange={(e) => setSelectedTimeframe(e.target.value)}
                                textField="text"
                                valueField="value"
                                style={{ width: '150px' }}
                            />

                            <DropDownList
                                data={sports}
                                value={sports.find(s => s.value === selectedSport)}
                                onChange={(e) => setSelectedSport(e.target.value)}
                                textField="text"
                                valueField="value"
                                style={{ width: '150px' }}
                            />

                            <Button
                                themeColor="primary"
                                size="small"
                                onClick={fetchAnalyticsData}
                                icon="refresh"
                                disabled={loading}
                            >
                                {loading ? 'Refreshing...' : 'Refresh'}
                            </Button>
                        </div>
                    </div>
                </CardBody>
            </Card>

            {/* Key Performance Metrics */}
            {analyticsData && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px', marginBottom: '24px' }}>
                    <Card>
                        <CardBody>
                            <div style={{ textAlign: 'center' }}>
                                <h3 style={{ margin: '0 0 8px 0', fontSize: '16px', color: '#666' }}>Total Portfolio Value</h3>
                                <div style={{ fontSize: '28px', fontWeight: 'bold', color: getPerformanceColor(analyticsData.roi_percentage) }}>
                                    {formatCurrency(analyticsData.total_value)}
                                </div>
                                <div style={{ fontSize: '14px', color: getPerformanceColor(analyticsData.roi_percentage) }}>
                                    {formatPercentage(analyticsData.roi_percentage)} ROI
                                </div>
                            </div>
                        </CardBody>
                    </Card>

                    <Card>
                        <CardBody>
                            <div style={{ textAlign: 'center' }}>
                                <h3 style={{ margin: '0 0 8px 0', fontSize: '16px', color: '#666' }}>Win Rate</h3>
                                <div style={{ fontSize: '28px', fontWeight: 'bold', color: analyticsData.win_rate > 50 ? '#28a745' : '#dc3545' }}>
                                    {analyticsData.win_rate.toFixed(1)}%
                                </div>
                                <div style={{ fontSize: '14px', color: '#666' }}>
                                    {analyticsData.total_bets} total bets
                                </div>
                            </div>
                        </CardBody>
                    </Card>

                    <Card>
                        <CardBody>
                            <div style={{ textAlign: 'center' }}>
                                <h3 style={{ margin: '0 0 8px 0', fontSize: '16px', color: '#666' }}>Current Streak</h3>
                                <div style={{ fontSize: '28px', fontWeight: 'bold', color: analyticsData.current_streak > 0 ? '#28a745' : '#dc3545' }}>
                                    {analyticsData.current_streak > 0 ? '+' : ''}{analyticsData.current_streak}
                                </div>
                                <div style={{ fontSize: '14px', color: '#666' }}>
                                    {analyticsData.current_streak > 0 ? 'Winning' : 'Losing'} streak
                                </div>
                            </div>
                        </CardBody>
                    </Card>

                    <Card>
                        <CardBody>
                            <div style={{ textAlign: 'center' }}>
                                <h3 style={{ margin: '0 0 8px 0', fontSize: '16px', color: '#666' }}>Total Profit</h3>
                                <div style={{ fontSize: '28px', fontWeight: 'bold', color: getPerformanceColor(analyticsData.total_profit) }}>
                                    {formatCurrency(analyticsData.total_profit)}
                                </div>
                                <div style={{ fontSize: '14px', color: '#666' }}>
                                    All time profit/loss
                                </div>
                            </div>
                        </CardBody>
                    </Card>
                </div>
            )}

            {/* Charts Row */}
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px', marginBottom: '24px' }}>
                {/* Performance Chart */}
                <Card>
                    <CardBody>
                        <h3 style={{ margin: '0 0 16px 0' }}>Performance Over Time</h3>
                        <Chart style={{ height: '300px' }}>
                            <ChartTooltip />
                            <ChartLegend />
                            <ChartCategoryAxis>
                                <ChartCategoryAxisItem categories={['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7', 'Week 8']} />
                            </ChartCategoryAxis>
                            <ChartValueAxis>
                                <ChartValueAxisItem />
                            </ChartValueAxis>
                            <ChartSeries>
                                <ChartSeriesItem
                                    type="line"
                                    data={[1000, 1050, 980, 1120, 1080, 1250, 1180, 1350]}
                                    name="Portfolio Value"
                                    color="#007bff"
                                />
                                <ChartSeriesItem
                                    type="line"
                                    data={[0, 5, -2, 12, 8, 25, 18, 35]}
                                    name="ROI %"
                                    color="#28a745"
                                />
                            </ChartSeries>
                        </Chart>
                    </CardBody>
                </Card>

                {/* Risk Gauge */}
                <Card>
                    <CardBody>
                        <h3 style={{ margin: '0 0 16px 0' }}>Risk Level</h3>
                        <div style={{ textAlign: 'center' }}>
                            <CircularGauge
                                value={riskAnalysis?.risk_score || 0}
                                min={0}
                                max={100}
                                style={{ height: '200px' }}
                                color={getRiskLevelColor(riskAnalysis?.current_risk_level)}
                            />
                            <div style={{ marginTop: '16px' }}>
                                <Badge
                                    themeColor={riskAnalysis?.current_risk_level === 'low' ? 'success' :
                                        riskAnalysis?.current_risk_level === 'medium' ? 'warning' :
                                            riskAnalysis?.current_risk_level === 'high' ? 'error' : 'info'}
                                    style={{ fontSize: '16px', padding: '8px 16px' }}
                                >
                                    {riskAnalysis?.current_risk_level?.toUpperCase() || 'UNKNOWN'}
                                </Badge>
                            </div>
                            <div style={{ marginTop: '8px', fontSize: '14px', color: '#666' }}>
                                Risk Score: {riskAnalysis?.risk_score || 0}/100
                            </div>
                        </div>
                    </CardBody>
                </Card>
            </div>

            {/* Sport Performance Grid */}
            <Card style={{ marginBottom: '24px' }}>
                <CardBody>
                    <h3 style={{ margin: '0 0 16px 0' }}>Sport Performance Breakdown</h3>
                    <Grid
                        data={sportPerformance}
                        style={{ height: '300px' }}
                    >
                        <GridColumn field="sport" title="Sport" width="120px" />
                        <GridColumn field="total_bets" title="Total Bets" width="100px" />
                        <GridColumn
                            field="win_rate"
                            title="Win Rate"
                            width="120px"
                            cell={(props) => (
                                <td>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        <ProgressBar
                                            value={props.dataItem.win_rate * 100}
                                            style={{ flex: 1 }}
                                            color={props.dataItem.win_rate > 0.6 ? '#28a745' : props.dataItem.win_rate > 0.5 ? '#ffc107' : '#dc3545'}
                                        />
                                        <span style={{ fontSize: '12px', minWidth: '40px' }}>
                                            {(props.dataItem.win_rate * 100).toFixed(1)}%
                                        </span>
                                    </div>
                                </td>
                            )}
                        />
                        <GridColumn
                            field="roi"
                            title="ROI"
                            width="100px"
                            cell={(props) => (
                                <td style={{ color: getPerformanceColor(props.dataItem.roi) }}>
                                    {formatPercentage(props.dataItem.roi)}
                                </td>
                            )}
                        />
                        <GridColumn
                            field="total_profit"
                            title="Profit/Loss"
                            width="120px"
                            cell={(props) => (
                                <td style={{ color: getPerformanceColor(props.dataItem.total_profit) }}>
                                    {formatCurrency(props.dataItem.total_profit)}
                                </td>
                            )}
                        />
                        <GridColumn field="best_team" title="Best Team" width="150px" />
                        <GridColumn field="avg_confidence" title="Avg Confidence" width="120px" />
                    </Grid>
                </CardBody>
            </Card>

            {/* AI Insights */}
            <Card style={{ marginBottom: '24px' }}>
                <CardBody>
                    <h3 style={{ margin: '0 0 16px 0' }}>AI-Powered Insights</h3>
                    {insights.length > 0 ? (
                        <div style={{ display: 'grid', gap: '16px' }}>
                            {insights.map((insight, index) => (
                                <div key={index} style={{
                                    padding: '16px',
                                    border: '1px solid #e9ecef',
                                    borderRadius: '8px',
                                    backgroundColor: '#f8f9fa'
                                }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                                        <h4 style={{ margin: 0, color: '#007bff' }}>{insight.title}</h4>
                                        <Badge
                                            themeColor={insight.insight_type === 'trend' ? 'success' :
                                                insight.insight_type === 'risk' ? 'error' :
                                                    insight.insight_type === 'pattern' ? 'info' : 'warning'}
                                            style={{ fontSize: '12px' }}
                                        >
                                            {insight.insight_type.toUpperCase()}
                                        </Badge>
                                    </div>
                                    <p style={{ margin: '0 0 12px 0', color: '#666' }}>{insight.description}</p>
                                    <div style={{ display: 'flex', gap: '16px', marginBottom: '12px' }}>
                                        <span style={{ fontSize: '12px', color: '#666' }}>
                                            Confidence: {(insight.confidence * 100).toFixed(0)}%
                                        </span>
                                        <span style={{ fontSize: '12px', color: '#666' }}>
                                            Impact: {(insight.impact_score * 100).toFixed(0)}%
                                        </span>
                                    </div>
                                    {insight.recommendations && insight.recommendations.length > 0 && (
                                        <div>
                                            <strong style={{ fontSize: '14px', color: '#495057' }}>Recommendations:</strong>
                                            <ul style={{ margin: '8px 0 0 0', paddingLeft: '20px', fontSize: '14px' }}>
                                                {insight.recommendations.map((rec, recIndex) => (
                                                    <li key={recIndex} style={{ marginBottom: '4px' }}>{rec}</li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
                            <p>No insights available yet. Continue betting to generate personalized insights!</p>
                        </div>
                    )}
                </CardBody>
            </Card>

            {/* Risk Analysis Details */}
            {riskAnalysis && (
                <Card style={{ marginBottom: '24px' }}>
                    <CardBody>
                        <h3 style={{ margin: '0 0 16px 0' }}>Risk Analysis & Management</h3>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                            <div>
                                <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#666' }}>Bet Size Recommendation</h4>
                                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#007bff' }}>
                                    {formatCurrency(riskAnalysis.bet_size_recommendation)}
                                </div>
                            </div>

                            <div>
                                <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#666' }}>Max Daily Loss</h4>
                                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#dc3545' }}>
                                    {formatCurrency(riskAnalysis.max_daily_loss)}
                                </div>
                            </div>

                            <div>
                                <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#666' }}>Diversification Score</h4>
                                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#28a745' }}>
                                    {riskAnalysis.diversification_score.toFixed(0)}%
                                </div>
                            </div>

                            <div>
                                <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#666' }}>Bankroll Utilization</h4>
                                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#ffc107' }}>
                                    {riskAnalysis.bankroll_utilization.toFixed(1)}%
                                </div>
                            </div>
                        </div>

                        {riskAnalysis.risk_factors && riskAnalysis.risk_factors.length > 0 && (
                            <div style={{ marginTop: '16px' }}>
                                <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#666' }}>Risk Factors</h4>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                                    {riskAnalysis.risk_factors.map((factor, index) => (
                                        <Badge key={index} themeColor="error" style={{ fontSize: '12px' }}>
                                            {factor}
                                        </Badge>
                                    ))}
                                </div>
                            </div>
                        )}
                    </CardBody>
                </Card>
            )}

            {/* Footer */}
            <div style={{ fontSize: '14px', color: '#666', textAlign: 'center', padding: '16px' }}>
                <p>
                    🔄 Analytics data updates every 5 minutes. Last update: {new Date().toLocaleTimeString()}
                </p>
                <p>
                    📊 Advanced analytics powered by real-time data processing and AI insights
                </p>
            </div>
        </div>
    );
};

export default AdvancedAnalyticsDashboard; 