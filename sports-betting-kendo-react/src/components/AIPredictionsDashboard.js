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
import apiService from '../services/ApiService';
import realSportsApiService from '../services/RealSportsApiService';

const AIPredictionsDashboard = () => {
    const [predictions, setPredictions] = useState([]);
    const [ensemblePredictions, setEnsemblePredictions] = useState([]);
    const [modelPerformance, setModelPerformance] = useState([]);
    const [liveGames, setLiveGames] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [notification, setNotification] = useState(null);
    const [selectedSport, setSelectedSport] = useState('all');
    const [selectedModel, setSelectedModel] = useState('all');
    const [refreshInterval, setRefreshInterval] = useState(null);

    const sports = [
        { text: 'All Sports', value: 'all' },
        { text: 'NFL Football', value: 'nfl' },
        { text: 'NBA Basketball', value: 'nba' },
        { text: 'MLB Baseball', value: 'mlb' },
        { text: 'NHL Hockey', value: 'nhl' }
    ];

    const models = [
        { text: 'All Models', value: 'all' },
        { text: 'Neural Network', value: 'neural_network' },
        { text: 'Random Forest', value: 'random_forest' },
        { text: 'Gradient Boosting', value: 'gradient_boosting' },
        { text: 'Ensemble', value: 'ensemble' }
    ];

    useEffect(() => {
        fetchAIPredictions();
        fetchLiveGames();
        setupAutoRefresh();
        
        return () => {
            if (refreshInterval) {
                clearInterval(refreshInterval);
            }
        };
    }, [selectedSport, selectedModel]);

    const setupAutoRefresh = () => {
        // Refresh data every 2 minutes
        const interval = setInterval(() => {
            fetchAIPredictions();
            fetchLiveGames();
        }, 2 * 60 * 1000);
        
        setRefreshInterval(interval);
    };

    const fetchAIPredictions = async () => {
        try {
            setLoading(true);
            setError(null);

            // Fetch AI predictions
            const predictionsResponse = await apiService.getAIPredictions(selectedSport);
            if (predictionsResponse.success) {
                setPredictions(predictionsResponse.data);
            }

            // Fetch ensemble predictions
            const ensembleResponse = await apiService.getEnsemblePredictions(selectedSport);
            if (ensembleResponse.success) {
                setEnsemblePredictions(ensembleResponse.data);
            }

            // Fetch model performance
            const performanceResponse = await apiService.getModelPerformance(selectedSport);
            if (performanceResponse.success) {
                setModelPerformance(performanceResponse.data);
            }

            setNotification({
                type: 'success',
                message: 'AI predictions updated successfully'
            });

        } catch (err) {
            console.error('Error fetching AI predictions:', err);
            setError('Failed to load AI predictions');
            setNotification({
                type: 'error',
                message: 'Error loading AI predictions'
            });
        } finally {
            setLoading(false);
        }
    };

    const fetchLiveGames = async () => {
        try {
            const gamesResponse = await realSportsApiService.getLiveGames(selectedSport);
            if (gamesResponse.success) {
                setLiveGames(gamesResponse.data);
            }
        } catch (err) {
            console.error('Error fetching live games:', err);
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

    const getModelColor = (modelName) => {
        const colors = {
            'neural_network': '#007bff',
            'random_forest': '#28a745',
            'gradient_boosting': '#fd7e14',
            'ensemble': '#6f42c1'
        };
        return colors[modelName] || '#6c757d';
    };

    const formatPercentage = (value) => {
        return `${(value * 100).toFixed(1)}%`;
    };

    const generatePrediction = async (game) => {
        try {
            const response = await apiService.generateAIPrediction({
                sport: selectedSport,
                home_team: game.home_team,
                away_team: game.away_team,
                game_data: game
            });

            if (response.success) {
                setNotification({
                    type: 'success',
                    message: `AI prediction generated for ${game.home_team} vs ${game.away_team}`
                });
                fetchAIPredictions(); // Refresh predictions
            }
        } catch (err) {
            setNotification({
                type: 'error',
                message: 'Failed to generate AI prediction'
            });
        }
    };

    if (loading && predictions.length === 0) {
        return (
            <div className="ai-predictions-dashboard">
                <div style={{ textAlign: 'center', padding: '50px' }}>
                    <div className="k-loading"></div>
                    <p>Loading AI predictions...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="ai-predictions-dashboard">
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
                            <h2 style={{ margin: '0 0 8px 0' }}>🤖 AI Predictions Dashboard</h2>
                            <p style={{ margin: 0, color: '#666', fontSize: '14px' }}>
                                Advanced machine learning predictions with ensemble methods and real-time insights
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
                                data={models}
                                value={models.find(m => m.value === selectedModel)}
                                onChange={(e) => setSelectedModel(e.target.value)}
                                textField="text"
                                valueField="value"
                                style={{ width: '150px' }}
                            />
                            
                            <Button 
                                themeColor="primary" 
                                size="small" 
                                onClick={fetchAIPredictions}
                                icon="refresh"
                                disabled={loading}
                            >
                                {loading ? 'Refreshing...' : 'Refresh'}
                            </Button>
                        </div>
                    </div>
                </CardBody>
            </Card>

            {/* Model Performance Overview */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px', marginBottom: '24px' }}>
                {modelPerformance.map((model, index) => (
                    <Card key={index}>
                        <CardBody>
                            <div style={{ textAlign: 'center' }}>
                                <h3 style={{ margin: '0 0 8px 0', fontSize: '16px', color: '#666' }}>
                                    {model.model_name.replace('_', ' ').toUpperCase()}
                                </h3>
                                <div style={{ fontSize: '28px', fontWeight: 'bold', color: getModelColor(model.model_name) }}>
                                    {formatPercentage(model.accuracy)}
                                </div>
                                <div style={{ fontSize: '14px', color: '#666' }}>
                                    Accuracy
                                </div>
                                <div style={{ marginTop: '8px' }}>
                                    <ProgressBar 
                                        value={model.accuracy * 100} 
                                        color={getModelColor(model.model_name)}
                                        style={{ height: '8px' }}
                                    />
                                </div>
                                <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                                    {model.total_predictions} predictions
                                </div>
                            </div>
                        </CardBody>
                    </Card>
                ))}
            </div>

            {/* Live Games with AI Predictions */}
            <Card style={{ marginBottom: '24px' }}>
                <CardBody>
                    <h3 style={{ margin: '0 0 16px 0' }}>🎯 Live Games & AI Predictions</h3>
                    <Grid
                        data={liveGames}
                        style={{ height: '400px' }}
                    >
                        <GridColumn field="sport" title="Sport" width="80px" />
                        <GridColumn field="home_team" title="Home Team" width="150px" />
                        <GridColumn field="away_team" title="Away Team" width="150px" />
                        <GridColumn field="status" title="Status" width="100px" />
                        <GridColumn 
                            field="ai_prediction" 
                            title="AI Prediction" 
                            width="120px"
                            cell={(props) => (
                                <td>
                                    {props.dataItem.ai_prediction ? (
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                            <span style={{ 
                                                color: getConfidenceColor(props.dataItem.ai_confidence || 0.5),
                                                fontWeight: 'bold'
                                            }}>
                                                {props.dataItem.ai_prediction}
                                            </span>
                                            <Badge 
                                                themeColor={props.dataItem.ai_confidence >= 0.7 ? 'success' : 
                                                           props.dataItem.ai_confidence >= 0.5 ? 'warning' : 'error'}
                                                style={{ fontSize: '10px' }}
                                            >
                                                {formatPercentage(props.dataItem.ai_confidence || 0.5)}
                                            </Badge>
                                        </div>
                                    ) : (
                                        <Button 
                                            size="small" 
                                            themeColor="primary"
                                            onClick={() => generatePrediction(props.dataItem)}
                                        >
                                            Generate
                                        </Button>
                                    )}
                                </td>
                            )}
                        />
                        <GridColumn 
                            field="ensemble_prediction" 
                            title="Ensemble" 
                            width="120px"
                            cell={(props) => (
                                <td>
                                    {props.dataItem.ensemble_prediction ? (
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                            <span style={{ 
                                                color: getConfidenceColor(props.dataItem.ensemble_confidence || 0.5),
                                                fontWeight: 'bold'
                                            }}>
                                                {props.dataItem.ensemble_prediction}
                                            </span>
                                            <Badge 
                                                themeColor={props.dataItem.ensemble_confidence >= 0.7 ? 'success' : 
                                                           props.dataItem.ensemble_confidence >= 0.5 ? 'warning' : 'error'}
                                                style={{ fontSize: '10px' }}
                                            >
                                                {formatPercentage(props.dataItem.ensemble_confidence || 0.5)}
                                            </Badge>
                                        </div>
                                    ) : (
                                        <span style={{ color: '#666', fontSize: '12px' }}>Pending</span>
                                    )}
                                </td>
                            )}
                        />
                        <GridColumn 
                            field="consensus_score" 
                            title="Consensus" 
                            width="100px"
                            cell={(props) => (
                                <td>
                                    {props.dataItem.consensus_score ? (
                                        <CircularGauge
                                            value={props.dataItem.consensus_score * 100}
                                            min={0}
                                            max={100}
                                            style={{ height: '40px' }}
                                            color={getConfidenceColor(props.dataItem.consensus_score)}
                                        />
                                    ) : (
                                        <span style={{ color: '#666', fontSize: '12px' }}>N/A</span>
                                    )}
                                </td>
                            )}
                        />
                    </Grid>
                </CardBody>
            </Card>

            {/* Ensemble Predictions */}
            <Card style={{ marginBottom: '24px' }}>
                <CardBody>
                    <h3 style={{ margin: '0 0 16px 0' }}>🎯 Ensemble Predictions</h3>
                    <PanelBar>
                        {ensemblePredictions.map((ensemble, index) => (
                            <PanelBarItem title={`${ensemble.home_team} vs ${ensemble.away_team} (${ensemble.sport})`} key={index}>
                                <div style={{ padding: '16px' }}>
                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                                        <div>
                                            <h4 style={{ margin: '0 0 8px 0' }}>Final Prediction</h4>
                                            <div style={{ fontSize: '24px', fontWeight: 'bold', color: getConfidenceColor(ensemble.ensemble_confidence) }}>
                                                {ensemble.final_prediction}
                                            </div>
                                            <div style={{ fontSize: '14px', color: '#666' }}>
                                                Confidence: {formatPercentage(ensemble.ensemble_confidence)}
                                            </div>
                                        </div>
                                        <div>
                                            <h4 style={{ margin: '0 0 8px 0' }}>Model Consensus</h4>
                                            <div style={{ fontSize: '24px', fontWeight: 'bold', color: getConfidenceColor(ensemble.consensus_score) }}>
                                                {formatPercentage(ensemble.consensus_score)}
                                            </div>
                                            <div style={{ fontSize: '14px', color: '#666' }}>
                                                Disagreement: {formatPercentage(ensemble.disagreement_level)}
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <h4 style={{ margin: '0 0 12px 0' }}>Individual Model Predictions</h4>
                                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
                                        {ensemble.model_predictions.map((prediction, predIndex) => (
                                            <div key={predIndex} style={{ 
                                                padding: '12px', 
                                                border: '1px solid #e9ecef', 
                                                borderRadius: '8px',
                                                backgroundColor: '#f8f9fa'
                                            }}>
                                                <div style={{ fontWeight: 'bold', color: getModelColor(prediction.model_name) }}>
                                                    {prediction.model_name.replace('_', ' ').toUpperCase()}
                                                </div>
                                                <div style={{ fontSize: '18px', fontWeight: 'bold', marginTop: '4px' }}>
                                                    {prediction.predicted_winner}
                                                </div>
                                                <div style={{ fontSize: '12px', color: '#666' }}>
                                                    Confidence: {formatPercentage(prediction.confidence)}
                                                </div>
                                                <div style={{ fontSize: '12px', color: '#666' }}>
                                                    Win Prob: {formatPercentage(prediction.win_probability)}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </PanelBarItem>
                        ))}
                    </PanelBar>
                </CardBody>
            </Card>

            {/* Prediction Accuracy Chart */}
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px', marginBottom: '24px' }}>
                <Card>
                    <CardBody>
                        <h3 style={{ margin: '0 0 16px 0' }}>📊 Model Performance Over Time</h3>
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
                                    data={[0.75, 0.78, 0.82, 0.79, 0.85, 0.83, 0.87, 0.89]} 
                                    name="Neural Network"
                                    color="#007bff"
                                />
                                <ChartSeriesItem 
                                    type="line" 
                                    data={[0.72, 0.75, 0.78, 0.76, 0.80, 0.82, 0.84, 0.86]} 
                                    name="Random Forest"
                                    color="#28a745"
                                />
                                <ChartSeriesItem 
                                    type="line" 
                                    data={[0.70, 0.73, 0.76, 0.74, 0.78, 0.80, 0.82, 0.84]} 
                                    name="Gradient Boosting"
                                    color="#fd7e14"
                                />
                                <ChartSeriesItem 
                                    type="line" 
                                    data={[0.78, 0.81, 0.85, 0.83, 0.87, 0.89, 0.91, 0.93]} 
                                    name="Ensemble"
                                    color="#6f42c1"
                                />
                            </ChartSeries>
                        </Chart>
                    </CardBody>
                </Card>

                <Card>
                    <CardBody>
                        <h3 style={{ margin: '0 0 16px 0' }}>🎯 Prediction Confidence Distribution</h3>
                        <Chart style={{ height: '300px' }}>
                            <ChartTooltip />
                            <ChartSeries>
                                <ChartSeriesItem 
                                    type="donut" 
                                    data={[
                                        { category: "High Confidence (>80%)", value: 45 },
                                        { category: "Medium Confidence (60-80%)", value: 35 },
                                        { category: "Low Confidence (<60%)", value: 20 }
                                    ]}
                                    field="value"
                                    categoryField="category"
                                />
                            </ChartSeries>
                        </Chart>
                    </CardBody>
                </Card>
            </div>

            {/* AI Insights */}
            <Card style={{ marginBottom: '24px' }}>
                <CardBody>
                    <h3 style={{ margin: '0 0 16px 0' }}>🧠 AI Insights & Recommendations</h3>
                    <div style={{ display: 'grid', gap: '16px' }}>
                        <div style={{ 
                            padding: '16px', 
                            border: '1px solid #e9ecef', 
                            borderRadius: '8px',
                            backgroundColor: '#f8f9fa'
                        }}>
                            <h4 style={{ margin: '0 0 8px 0', color: '#007bff' }}>🎯 High Confidence Predictions</h4>
                            <p style={{ margin: '0 0 8px 0', fontSize: '14px' }}>
                                Models show strong agreement on Kansas City Chiefs vs Buffalo Bills with 89% ensemble confidence.
                            </p>
                            <div style={{ fontSize: '12px', color: '#666' }}>
                                Recommendation: Consider higher bet sizes for high-confidence predictions
                            </div>
                        </div>
                        
                        <div style={{ 
                            padding: '16px', 
                            border: '1px solid #e9ecef', 
                            borderRadius: '8px',
                            backgroundColor: '#f8f9fa'
                        }}>
                            <h4 style={{ margin: '0 0 8px 0', color: '#fd7e14' }}>⚠️ Model Disagreement Alert</h4>
                            <p style={{ margin: '0 0 8px 0', fontSize: '14px' }}>
                                High disagreement (35%) detected in Lakers vs Warriors prediction.
                            </p>
                            <div style={{ fontSize: '12px', color: '#666' }}>
                                Recommendation: Reduce bet size or avoid this game due to uncertainty
                            </div>
                        </div>
                        
                        <div style={{ 
                            padding: '16px', 
                            border: '1px solid #e9ecef', 
                            borderRadius: '8px',
                            backgroundColor: '#f8f9fa'
                        }}>
                            <h4 style={{ margin: '0 0 8px 0', color: '#28a745' }}>📈 Performance Trend</h4>
                            <p style={{ margin: '0 0 8px 0', fontSize: '14px' }}>
                                Ensemble model accuracy improved 6% over the last 4 weeks.
                            </p>
                            <div style={{ fontSize: '12px', color: '#666' }}>
                                Recommendation: Models are learning and improving - trust recent predictions more
                            </div>
                        </div>
                    </div>
                </CardBody>
            </Card>

            {/* Footer */}
            <div style={{ fontSize: '14px', color: '#666', textAlign: 'center', padding: '16px' }}>
                <p>
                    🔄 AI predictions update every 2 minutes. Last update: {new Date().toLocaleTimeString()}
                </p>
                <p>
                    🤖 Powered by ensemble learning with Neural Networks, Random Forest, and Gradient Boosting
                </p>
            </div>
        </div>
    );
};

export default AIPredictionsDashboard; 