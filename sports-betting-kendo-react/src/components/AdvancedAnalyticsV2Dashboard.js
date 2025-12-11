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
import { PanelBar, PanelBarItem } from '@progress/kendo-react-layout';
import { TreeList, TreeListColumn } from '@progress/kendo-react-treelist';
import { Sparkline } from '@progress/kendo-react-charts';
import apiService from '../services/ApiService';

const AdvancedAnalyticsV2Dashboard = () => {
    const [insights, setInsights] = useState([]);
    const [trends, setTrends] = useState([]);
    const [riskAssessments, setRiskAssessments] = useState([]);
    const [performanceMetrics, setPerformanceMetrics] = useState([]);
    const [predictiveModels, setPredictiveModels] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [notification, setNotification] = useState(null);
    const [selectedSport, setSelectedSport] = useState('all');
    const [selectedCategory, setSelectedCategory] = useState('all');
    const [refreshInterval, setRefreshInterval] = useState(null);

    const sports = [
        { text: 'All Sports', value: 'all' },
        { text: 'NFL Football', value: 'nfl' },
        { text: 'NCAAB Men\'s', value: 'ncaab' },
        { text: 'NCAAB Women\'s', value: 'ncaaw' },
        { text: 'WNBA Basketball', value: 'wnba' },
        { text: 'MLB Baseball', value: 'mlb' },
        { text: 'NHL Hockey', value: 'nhl' }
    ];

    const categories = [
        { text: 'All Categories', value: 'all' },
        { text: 'Team Performance', value: 'team_performance' },
        { text: 'Player Performance', value: 'player_performance' },
        { text: 'Market Trends', value: 'market_trends' },
        { text: 'Risk Assessment', value: 'risk_assessment' },
        { text: 'Offensive Performance', value: 'offensive_performance' },
        { text: 'Injury Risk', value: 'injury_risk' }
    ];

    useEffect(() => {
        fetchAdvancedAnalytics();
        setupAutoRefresh();

        return () => {
            if (refreshInterval) {
                clearInterval(refreshInterval);
            }
        };
    }, [selectedSport, selectedCategory]);

    const setupAutoRefresh = () => {
        // Refresh data every 3 minutes
        const interval = setInterval(() => {
            fetchAdvancedAnalytics();
        }, 3 * 60 * 1000);

        setRefreshInterval(interval);
    };

    const fetchAdvancedAnalytics = async () => {
        try {
            setLoading(true);
            setError(null);

            // Fetch analytics insights
            const insightsResponse = await apiService.getAnalyticsInsights(selectedSport, selectedCategory);
            if (insightsResponse.success) {
                setInsights(insightsResponse.data);
            }

            // Fetch trend analysis
            const trendsResponse = await apiService.getTrendAnalysis(selectedSport);
            if (trendsResponse.success) {
                setTrends(trendsResponse.data);
            }

            // Fetch risk assessments
            const riskResponse = await apiService.getRiskAssessments(selectedSport);
            if (riskResponse.success) {
                setRiskAssessments(riskResponse.data);
            }

            // Fetch performance metrics
            const metricsResponse = await apiService.getPerformanceMetrics(selectedSport);
            if (metricsResponse.success) {
                setPerformanceMetrics(metricsResponse.data);
            }

            // Fetch predictive models
            const modelsResponse = await apiService.getPredictiveModels();
            if (modelsResponse.success) {
                setPredictiveModels(modelsResponse.data);
            }

            setNotification({
                type: 'success',
                message: 'Advanced analytics updated successfully'
            });

        } catch (err) {
            console.error('Error fetching advanced analytics:', err);
            setError('Failed to load advanced analytics');
            setNotification({
                type: 'error',
                message: 'Error loading advanced analytics'
            });
        } finally {
            setLoading(false);
        }
    };

    const closeNotification = () => {
        setNotification(null);
    };

    const getConfidenceColor = (confidence) => {
        if (confidence >= 0.8) return '#28a745';
        if (confidence >= 0.6) return '#ffc107';
        if (confidence >= 0.4) return '#fd7e14';
        return '#dc3545';
    };

    const getImpactColor = (impact) => {
        if (impact >= 0.8) return '#dc3545';
        if (impact >= 0.6) return '#fd7e14';
        if (impact >= 0.4) return '#ffc107';
        return '#28a745';
    };

    const getRiskColor = (riskLevel) => {
        const colors = {
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#dc3545'
        };
        return colors[riskLevel] || '#6c757d';
    };

    const formatPercentage = (value) => {
        return `${(value * 100).toFixed(1)}%`;
    };

    const generateInsight = async () => {
        try {
            const response = await apiService.generateAnalyticsInsight({
                sport: selectedSport,
                category: selectedCategory
            });

            if (response.success) {
                setNotification({
                    type: 'success',
                    message: 'New analytics insight generated successfully'
                });
                fetchAdvancedAnalytics(); // Refresh insights
            }
        } catch (err) {
            setNotification({
                type: 'error',
                message: 'Failed to generate analytics insight'
            });
        }
    };

    if (loading && insights.length === 0) {
        return (
            <div className="advanced-analytics-v2-dashboard">
                <div style={{ textAlign: 'center', padding: '50px' }}>
                    <div className="k-loading"></div>
                    <p>Loading Advanced Analytics...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="advanced-analytics-v2-dashboard">
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
                            <h2 style={{ margin: '0 0 8px 0' }}>📊 Advanced Analytics V2 Dashboard</h2>
                            <p style={{ margin: 0, color: '#666', fontSize: '14px' }}>
                                Sophisticated analytics with predictive modeling, trend analysis, and AI-powered insights
                            </p>
                        </div>

                        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                            <DropDownList
                                data={sports}
                                value={sports.find(s => s.value === selectedSport)}
                                onChange={(e) => setSelectedSport(e.target.value)}
                                textField="text"
                                valueField="value"
                                style={{ width: '150px' }}
                            />

                            <DropDownList
                                data={categories}
                                value={categories.find(c => c.value === selectedCategory)}
                                onChange={(e) => setSelectedCategory(e.target.value)}
                                textField="text"
                                valueField="value"
                                style={{ width: '150px' }}
                            />

                            <Button
                                themeColor="primary"
                                size="small"
                                onClick={fetchAdvancedAnalytics}
                                icon="refresh"
                                disabled={loading}
                            >
                                {loading ? 'Refreshing...' : 'Refresh'}
                            </Button>

                            <Button
                                themeColor="success"
                                size="small"
                                onClick={generateInsight}
                                icon="plus"
                            >
                                Generate Insight
                            </Button>
                        </div>
                    </div>
                </CardBody>
            </Card>

            {/* Performance Metrics Overview */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px', marginBottom: '24px' }}>
                {performanceMetrics.map((metric, index) => (
                    <Card key={index}>
                        <CardBody>
                            <div style={{ textAlign: 'center' }}>
                                <h3 style={{ margin: '0 0 8px 0', fontSize: '16px', color: '#666' }}>
                                    {metric.name}
                                </h3>
                                <div style={{ fontSize: '28px', fontWeight: 'bold', color: getConfidenceColor(metric.value) }}>
                                    {formatPercentage(metric.value)}
                                </div>
                                <div style={{ fontSize: '14px', color: '#666' }}>
                                    {metric.trend} trend
                                </div>
                                <div style={{ marginTop: '8px' }}>
                                    <ProgressBar
                                        value={metric.value * 100}
                                        color={getConfidenceColor(metric.value)}
                                        style={{ height: '8px' }}
                                    />
                                </div>
                                <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                                    {metric.percentile.toFixed(0)}% percentile
                                </div>
                            </div>
                        </CardBody>
                    </Card>
                ))}
            </div>

            {/* Analytics Insights */}
            <Card style={{ marginBottom: '24px' }}>
                <CardBody>
                    <h3 style={{ margin: '0 0 16px 0' }}>🧠 AI-Powered Analytics Insights</h3>
                    <PanelBar>
                        {insights.map((insight, index) => (
                            <PanelBarItem title={`${insight.title} (${insight.category.replace('_', ' ')})`} key={index}>
                                <div style={{ padding: '16px' }}>
                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                                        <div>
                                            <h4 style={{ margin: '0 0 8px 0' }}>Insight Details</h4>
                                            <p style={{ margin: '0 0 8px 0', fontSize: '14px', lineHeight: '1.5' }}>
                                                {insight.description}
                                            </p>
                                            <div style={{ fontSize: '14px', color: '#666' }}>
                                                Data Points: {insight.data_points}
                                            </div>
                                        </div>
                                        <div>
                                            <h4 style={{ margin: '0 0 8px 0' }}>Metrics</h4>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                                                <span>Confidence:</span>
                                                <CircularGauge
                                                    value={insight.confidence * 100}
                                                    min={0}
                                                    max={100}
                                                    style={{ height: '40px' }}
                                                    color={getConfidenceColor(insight.confidence)}
                                                />
                                                <span>{formatPercentage(insight.confidence)}</span>
                                            </div>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                                <span>Impact Score:</span>
                                                <CircularGauge
                                                    value={insight.impact_score * 100}
                                                    min={0}
                                                    max={100}
                                                    style={{ height: '40px' }}
                                                    color={getImpactColor(insight.impact_score)}
                                                />
                                                <span>{formatPercentage(insight.impact_score)}</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div style={{
                                        padding: '12px',
                                        backgroundColor: '#f8f9fa',
                                        borderRadius: '8px',
                                        borderLeft: '4px solid #007bff'
                                    }}>
                                        <h4 style={{ margin: '0 0 8px 0', color: '#007bff' }}>💡 Recommendation</h4>
                                        <p style={{ margin: 0, fontSize: '14px' }}>
                                            {insight.recommendation}
                                        </p>
                                    </div>
                                </div>
                            </PanelBarItem>
                        ))}
                    </PanelBar>
                </CardBody>
            </Card>

            {/* Trend Analysis */}
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px', marginBottom: '24px' }}>
                <Card>
                    <CardBody>
                        <h3 style={{ margin: '0 0 16px 0' }}>📈 Trend Analysis</h3>
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
                                    data={[0.65, 0.68, 0.72, 0.70, 0.75, 0.73, 0.77, 0.79]}
                                    name="Win Rate"
                                    color="#007bff"
                                />
                                <ChartSeriesItem
                                    type="line"
                                    data={[0.58, 0.61, 0.64, 0.62, 0.66, 0.65, 0.68, 0.70]}
                                    name="Scoring"
                                    color="#28a745"
                                />
                                <ChartSeriesItem
                                    type="line"
                                    data={[0.72, 0.70, 0.68, 0.71, 0.69, 0.73, 0.71, 0.74]}
                                    name="Defense"
                                    color="#fd7e14"
                                />
                            </ChartSeries>
                        </Chart>
                    </CardBody>
                </Card>

                <Card>
                    <CardBody>
                        <h3 style={{ margin: '0 0 16px 0' }}>🎯 Trend Summary</h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                            {trends.map((trend, index) => (
                                <div key={index} style={{
                                    padding: '12px',
                                    border: '1px solid #e9ecef',
                                    borderRadius: '8px',
                                    backgroundColor: '#f8f9fa'
                                }}>
                                    <div style={{ fontWeight: 'bold', fontSize: '14px' }}>
                                        {trend.metric.replace('_', ' ').toUpperCase()}
                                    </div>
                                    <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                                        Direction: {trend.trend_direction}
                                    </div>
                                    <div style={{ fontSize: '12px', color: '#666' }}>
                                        Confidence: {formatPercentage(trend.confidence)}
                                    </div>
                                    <div style={{ fontSize: '12px', color: '#666' }}>
                                        Data Points: {trend.data_points}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardBody>
                </Card>
            </div>

            {/* Risk Assessment */}
            <Card style={{ marginBottom: '24px' }}>
                <CardBody>
                    <h3 style={{ margin: '0 0 16px 0' }}>⚠️ Risk Assessment</h3>
                    <Grid
                        data={riskAssessments}
                        style={{ height: '400px' }}
                    >
                        <GridColumn field="bet_type" title="Bet Type" width="120px" />
                        <GridColumn
                            field="risk_level"
                            title="Risk Level"
                            width="100px"
                            cell={(props) => (
                                <td>
                                    <Badge
                                        themeColor={getRiskColor(props.dataItem.risk_level)}
                                        style={{ fontSize: '12px' }}
                                    >
                                        {props.dataItem.risk_level.toUpperCase()}
                                    </Badge>
                                </td>
                            )}
                        />
                        <GridColumn
                            field="risk_score"
                            title="Risk Score"
                            width="100px"
                            cell={(props) => (
                                <td>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        <CircularGauge
                                            value={props.dataItem.risk_score * 100}
                                            min={0}
                                            max={100}
                                            style={{ height: '30px' }}
                                            color={getRiskColor(props.dataItem.risk_level)}
                                        />
                                        <span>{formatPercentage(props.dataItem.risk_score)}</span>
                                    </div>
                                </td>
                            )}
                        />
                        <GridColumn
                            field="confidence"
                            title="Confidence"
                            width="100px"
                            cell={(props) => (
                                <td>
                                    {formatPercentage(props.dataItem.confidence)}
                                </td>
                            )}
                        />
                        <GridColumn
                            field="factors"
                            title="Risk Factors"
                            width="200px"
                            cell={(props) => (
                                <td>
                                    <div style={{ fontSize: '12px' }}>
                                        {props.dataItem.factors.slice(0, 2).join(', ')}
                                        {props.dataItem.factors.length > 2 && '...'}
                                    </div>
                                </td>
                            )}
                        />
                        <GridColumn
                            field="mitigation_strategies"
                            title="Mitigation"
                            width="200px"
                            cell={(props) => (
                                <td>
                                    <div style={{ fontSize: '12px' }}>
                                        {props.dataItem.mitigation_strategies.slice(0, 2).join(', ')}
                                        {props.dataItem.mitigation_strategies.length > 2 && '...'}
                                    </div>
                                </td>
                            )}
                        />
                    </Grid>
                </CardBody>
            </Card>

            {/* Predictive Models */}
            <Card style={{ marginBottom: '24px' }}>
                <CardBody>
                    <h3 style={{ margin: '0 0 16px 0' }}>🤖 Predictive Models Performance</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
                        {predictiveModels.map((model, index) => (
                            <div key={index} style={{
                                padding: '16px',
                                border: '1px solid #e9ecef',
                                borderRadius: '8px',
                                backgroundColor: '#f8f9fa'
                            }}>
                                <h4 style={{ margin: '0 0 12px 0', color: '#007bff' }}>
                                    {model.name}
                                </h4>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '12px' }}>
                                    <div>
                                        <div style={{ fontSize: '12px', color: '#666' }}>Accuracy</div>
                                        <div style={{ fontSize: '18px', fontWeight: 'bold' }}>
                                            {formatPercentage(model.accuracy)}
                                        </div>
                                    </div>
                                    <div>
                                        <div style={{ fontSize: '12px', color: '#666' }}>Precision</div>
                                        <div style={{ fontSize: '18px', fontWeight: 'bold' }}>
                                            {formatPercentage(model.precision)}
                                        </div>
                                    </div>
                                    <div>
                                        <div style={{ fontSize: '12px', color: '#666' }}>Recall</div>
                                        <div style={{ fontSize: '18px', fontWeight: 'bold' }}>
                                            {formatPercentage(model.recall)}
                                        </div>
                                    </div>
                                    <div>
                                        <div style={{ fontSize: '12px', color: '#666' }}>F1 Score</div>
                                        <div style={{ fontSize: '18px', fontWeight: 'bold' }}>
                                            {formatPercentage(model.f1_score)}
                                        </div>
                                    </div>
                                </div>
                                <div style={{ fontSize: '12px', color: '#666' }}>
                                    Training Data: {model.training_data_size.toLocaleString()} records
                                </div>
                                <div style={{ fontSize: '12px', color: '#666' }}>
                                    Type: {model.type}
                                </div>
                            </div>
                        ))}
                    </div>
                </CardBody>
            </Card>

            {/* Footer */}
            <div style={{ fontSize: '14px', color: '#666', textAlign: 'center', padding: '16px' }}>
                <p>
                    🔄 Advanced analytics update every 3 minutes. Last update: {new Date().toLocaleTimeString()}
                </p>
                <p>
                    🤖 Powered by AI/ML predictive modeling and sophisticated analytics algorithms
                </p>
            </div>
        </div>
    );
};

export default AdvancedAnalyticsV2Dashboard; 