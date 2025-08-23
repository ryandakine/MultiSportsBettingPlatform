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

const AdvancedAnalyticsV3Dashboard = () => {
    const [predictiveInsights, setPredictiveInsights] = useState([]);
    const [advancedMetrics, setAdvancedMetrics] = useState([]);
    const [marketIntelligence, setMarketIntelligence] = useState([]);
    const [behavioralAnalytics, setBehavioralAnalytics] = useState([]);
    const [mlModels, setMlModels] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [notification, setNotification] = useState(null);
    const [selectedSport, setSelectedSport] = useState('all');
    const [selectedCategory, setSelectedCategory] = useState('all');
    const [refreshInterval, setRefreshInterval] = useState(null);

    const sports = [
        { text: 'All Sports', value: 'all' },
        { text: 'NFL Football', value: 'nfl' },
        { text: 'NBA Basketball', value: 'nba' },
        { text: 'MLB Baseball', value: 'mlb' },
        { text: 'NHL Hockey', value: 'nhl' }
    ];

    const categories = [
        { text: 'All Categories', value: 'all' },
        { text: 'Predictive Insights', value: 'predictive' },
        { text: 'Market Intelligence', value: 'market' },
        { text: 'Behavioral Analytics', value: 'behavioral' },
        { text: 'Advanced Metrics', value: 'metrics' }
    ];

    useEffect(() => {
        fetchAdvancedAnalyticsV3();
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
            fetchAdvancedAnalyticsV3();
        }, 3 * 60 * 1000);
        
        setRefreshInterval(interval);
    };

    const fetchAdvancedAnalyticsV3 = async () => {
        try {
            setLoading(true);
            setError(null);

            // Fetch predictive insights
            const insightsResponse = await apiService.getPredictiveInsights(selectedSport, selectedCategory);
            if (insightsResponse.success) {
                setPredictiveInsights(insightsResponse.data);
            }

            // Fetch advanced metrics
            const metricsResponse = await apiService.getAdvancedMetrics(selectedSport);
            if (metricsResponse.success) {
                setAdvancedMetrics(metricsResponse.data);
            }

            // Fetch market intelligence
            const intelligenceResponse = await apiService.getMarketIntelligence(selectedSport);
            if (intelligenceResponse.success) {
                setMarketIntelligence(intelligenceResponse.data);
            }

            // Fetch behavioral analytics
            const behaviorResponse = await apiService.getBehavioralAnalytics(selectedSport);
            if (behaviorResponse.success) {
                setBehavioralAnalytics(behaviorResponse.data);
            }

            // Fetch ML models
            const modelsResponse = await apiService.getMLModels();
            if (modelsResponse.success) {
                setMlModels(modelsResponse.data);
            }

            setNotification({
                type: 'success',
                message: 'Advanced Analytics V3 updated successfully'
            });

        } catch (err) {
            console.error('Error fetching advanced analytics V3:', err);
            setError('Failed to load advanced analytics V3');
            setNotification({
                type: 'error',
                message: 'Error loading advanced analytics V3'
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

    const getTrendColor = (trend) => {
        const colors = {
            'increasing': '#28a745',
            'decreasing': '#dc3545',
            'stable': '#6c757d'
        };
        return colors[trend] || '#6c757d';
    };

    const formatPercentage = (value) => {
        return `${(value * 100).toFixed(1)}%`;
    };

    const formatCurrency = (value) => {
        return `$${value.toLocaleString()}`;
    };

    if (loading && predictiveInsights.length === 0) {
        return (
            <div className="advanced-analytics-v3-dashboard">
                <div style={{ textAlign: 'center', padding: '50px' }}>
                    <div className="k-loading"></div>
                    <p>Loading Advanced Analytics V3...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="advanced-analytics-v3-dashboard">
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
                            <h2 style={{ margin: '0 0 8px 0' }}>🔮 Advanced Analytics V3 Dashboard</h2>
                            <p style={{ margin: 0, color: '#666', fontSize: '14px' }}>
                                Sophisticated analytics with predictive modeling, market intelligence, behavioral analytics, and machine learning
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
                                onClick={fetchAdvancedAnalyticsV3}
                                icon="refresh"
                                disabled={loading}
                            >
                                {loading ? 'Refreshing...' : 'Refresh'}
                            </Button>
                        </div>
                    </div>
                </CardBody>
            </Card>

            {/* Advanced Metrics Overview */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px', marginBottom: '24px' }}>
                {advancedMetrics.map((metric, index) => (
                    <Card key={index}>
                        <CardBody>
                            <div style={{ textAlign: 'center' }}>
                                <h3 style={{ margin: '0 0 8px 0', fontSize: '16px', color: '#666' }}>
                                    {metric.name}
                                </h3>
                                <div style={{ fontSize: '28px', fontWeight: 'bold', color: getTrendColor(metric.trend) }}>
                                    {metric.unit === 'USD' ? formatCurrency(metric.value) : 
                                     metric.unit === 'percentage' ? formatPercentage(metric.value) : 
                                     `${metric.value.toFixed(2)} ${metric.unit}`}
                                </div>
                                <div style={{ fontSize: '14px', color: '#666' }}>
                                    {metric.trend} trend
                                </div>
                                <div style={{ marginTop: '8px' }}>
                                    <ProgressBar 
                                        value={metric.percentile} 
                                        color={getConfidenceColor(metric.percentile / 100)}
                                        style={{ height: '8px' }}
                                    />
                                </div>
                                <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                                    {metric.percentile.toFixed(0)}% percentile
                                </div>
                                <div style={{ fontSize: '12px', color: '#666' }}>
                                    Volatility: {formatPercentage(metric.volatility)}
                                </div>
                            </div>
                        </CardBody>
                    </Card>
                ))}
            </div>

            {/* Predictive Insights */}
            <Card style={{ marginBottom: '24px' }}>
                <CardBody>
                    <h3 style={{ margin: '0 0 16px 0' }}>🔮 Predictive Insights</h3>
                    <PanelBar>
                        {predictiveInsights.map((insight, index) => (
                            <PanelBarItem title={`${insight.title} (${insight.category.replace('_', ' ')})`} key={index}>
                                <div style={{ padding: '16px' }}>
                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                                        <div>
                                            <h4 style={{ margin: '0 0 8px 0' }}>Insight Details</h4>
                                            <p style={{ margin: '0 0 8px 0', fontSize: '14px', lineHeight: '1.5' }}>
                                                {insight.description}
                                            </p>
                                            <div style={{ fontSize: '14px', color: '#666' }}>
                                                Time Horizon: {insight.time_horizon}
                                            </div>
                                            <div style={{ fontSize: '14px', color: '#666' }}>
                                                Methodology: {insight.methodology}
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
                                    
                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                                        <div style={{ 
                                            padding: '12px', 
                                            backgroundColor: '#fff3cd', 
                                            borderRadius: '8px',
                                            borderLeft: '4px solid #ffc107'
                                        }}>
                                            <h4 style={{ margin: '0 0 8px 0', color: '#856404' }}>🚨 Risk Factors</h4>
                                            <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '14px' }}>
                                                {insight.risk_factors.slice(0, 3).map((risk, i) => (
                                                    <li key={i}>{risk}</li>
                                                ))}
                                            </ul>
                                        </div>
                                        
                                        <div style={{ 
                                            padding: '12px', 
                                            backgroundColor: '#d1ecf1', 
                                            borderRadius: '8px',
                                            borderLeft: '4px solid #17a2b8'
                                        }}>
                                            <h4 style={{ margin: '0 0 8px 0', color: '#0c5460' }}>💡 Opportunities</h4>
                                            <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '14px' }}>
                                                {insight.opportunities.slice(0, 3).map((opp, i) => (
                                                    <li key={i}>{opp}</li>
                                                ))}
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            </PanelBarItem>
                        ))}
                    </PanelBar>
                </CardBody>
            </Card>

            {/* Market Intelligence */}
            <Card style={{ marginBottom: '24px' }}>
                <CardBody>
                    <h3 style={{ margin: '0 0 16px 0' }}>🧠 Market Intelligence</h3>
                    <Grid
                        data={marketIntelligence}
                        style={{ height: '400px' }}
                    >
                        <GridColumn field="market_segment" title="Market Segment" width="120px" />
                        <GridColumn field="insight_type" title="Type" width="120px" />
                        <GridColumn 
                            field="title" 
                            title="Title" 
                            width="200px"
                            cell={(props) => (
                                <td>
                                    <div style={{ fontSize: '12px', fontWeight: 'bold' }}>
                                        {props.dataItem.title}
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
                            field="impact_level" 
                            title="Impact" 
                            width="100px"
                            cell={(props) => (
                                <td>
                                    <Badge 
                                        themeColor={props.dataItem.impact_level === 'high' ? 'error' : 
                                                   props.dataItem.impact_level === 'medium' ? 'warning' : 'success'}
                                        style={{ fontSize: '12px' }}
                                    >
                                        {props.dataItem.impact_level.toUpperCase()}
                                    </Badge>
                                </td>
                            )}
                        />
                        <GridColumn 
                            field="trend_direction" 
                            title="Trend" 
                            width="100px"
                            cell={(props) => (
                                <td>
                                    <div style={{ 
                                        color: getTrendColor(props.dataItem.trend_direction),
                                        fontWeight: 'bold'
                                    }}>
                                        {props.dataItem.trend_direction}
                                    </div>
                                </td>
                            )}
                        />
                        <GridColumn 
                            field="data_points" 
                            title="Data Points" 
                            width="100px"
                            cell={(props) => (
                                <td>
                                    {props.dataItem.data_points.toLocaleString()}
                                </td>
                            )}
                        />
                    </Grid>
                </CardBody>
            </Card>

            {/* Behavioral Analytics */}
            <Card style={{ marginBottom: '24px' }}>
                <CardBody>
                    <h3 style={{ margin: '0 0 16px 0' }}>👥 Behavioral Analytics</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
                        {behavioralAnalytics.map((behavior, index) => (
                            <div key={index} style={{ 
                                padding: '16px', 
                                border: '1px solid #e9ecef', 
                                borderRadius: '8px',
                                backgroundColor: '#f8f9fa'
                            }}>
                                <h4 style={{ margin: '0 0 12px 0', color: '#007bff' }}>
                                    {behavior.user_segment.replace('_', ' ').toUpperCase()} Users
                                </h4>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '12px' }}>
                                    <div>
                                        <div style={{ fontSize: '12px', color: '#666' }}>Frequency</div>
                                        <div style={{ fontSize: '18px', fontWeight: 'bold' }}>
                                            {formatPercentage(behavior.frequency)}
                                        </div>
                                    </div>
                                    <div>
                                        <div style={{ fontSize: '12px', color: '#666' }}>Conversion</div>
                                        <div style={{ fontSize: '18px', fontWeight: 'bold' }}>
                                            {formatPercentage(behavior.conversion_rate)}
                                        </div>
                                    </div>
                                    <div>
                                        <div style={{ fontSize: '12px', color: '#666' }}>Engagement</div>
                                        <div style={{ fontSize: '18px', fontWeight: 'bold' }}>
                                            {formatPercentage(behavior.engagement_score)}
                                        </div>
                                    </div>
                                    <div>
                                        <div style={{ fontSize: '12px', color: '#666' }}>Churn Risk</div>
                                        <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#dc3545' }}>
                                            {formatPercentage(behavior.churn_risk)}
                                        </div>
                                    </div>
                                </div>
                                <div style={{ fontSize: '12px', color: '#666', marginBottom: '8px' }}>
                                    Lifetime Value: {formatCurrency(behavior.lifetime_value)}
                                </div>
                                <div style={{ fontSize: '12px', color: '#666' }}>
                                    Pattern: {behavior.behavior_pattern.replace('_', ' ')}
                                </div>
                            </div>
                        ))}
                    </div>
                </CardBody>
            </Card>

            {/* Machine Learning Models */}
            <Card style={{ marginBottom: '24px' }}>
                <CardBody>
                    <h3 style={{ margin: '0 0 16px 0' }}>🤖 Machine Learning Models</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '16px' }}>
                        {mlModels.map((model, index) => (
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
                                <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>
                                    Algorithm: {model.algorithm}
                                </div>
                                <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>
                                    Training Data: {model.training_data_size.toLocaleString()} records
                                </div>
                                <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>
                                    Features: {model.features_count}
                                </div>
                                <div style={{ fontSize: '12px', color: '#666' }}>
                                    Performance: {model.performance_trend}
                                </div>
                            </div>
                        ))}
                    </div>
                </CardBody>
            </Card>

            {/* Analytics Performance Chart */}
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px', marginBottom: '24px' }}>
                <Card>
                    <CardBody>
                        <h3 style={{ margin: '0 0 16px 0' }}>📊 Advanced Analytics Performance</h3>
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
                                    data={[0.85, 0.87, 0.89, 0.88, 0.91, 0.90, 0.92, 0.94]} 
                                    name="Predictive Accuracy"
                                    color="#007bff"
                                />
                                <ChartSeriesItem 
                                    type="line" 
                                    data={[0.78, 0.80, 0.82, 0.81, 0.84, 0.83, 0.85, 0.87]} 
                                    name="Market Intelligence"
                                    color="#28a745"
                                />
                                <ChartSeriesItem 
                                    type="line" 
                                    data={[0.82, 0.84, 0.86, 0.85, 0.88, 0.87, 0.89, 0.91]} 
                                    name="Behavioral Analytics"
                                    color="#fd7e14"
                                />
                            </ChartSeries>
                        </Chart>
                    </CardBody>
                </Card>

                <Card>
                    <CardBody>
                        <h3 style={{ margin: '0 0 16px 0' }}>🔮 Analytics Categories</h3>
                        <Chart style={{ height: '300px' }}>
                            <ChartTooltip />
                            <ChartSeries>
                                <ChartSeriesItem 
                                    type="donut" 
                                    data={[
                                        { category: "Predictive Insights", value: 30 },
                                        { category: "Market Intelligence", value: 25 },
                                        { category: "Behavioral Analytics", value: 25 },
                                        { category: "Advanced Metrics", value: 20 }
                                    ]}
                                    field="value"
                                    categoryField="category"
                                />
                            </ChartSeries>
                        </Chart>
                    </CardBody>
                </Card>
            </div>

            {/* Footer */}
            <div style={{ fontSize: '14px', color: '#666', textAlign: 'center', padding: '16px' }}>
                <p>
                    🔄 Advanced Analytics V3 updates every 3 minutes. Last update: {new Date().toLocaleTimeString()}
                </p>
                <p>
                    🔮 Powered by predictive modeling, machine learning, and sophisticated analytics algorithms
                </p>
            </div>
        </div>
    );
};

export default AdvancedAnalyticsV3Dashboard; 