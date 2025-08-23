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
import { TextArea } from '@progress/kendo-react-inputs';
import apiService from '../services/ApiService';

const AdvancedAIFeaturesV3Dashboard = () => {
    const [sentimentAnalysis, setSentimentAnalysis] = useState([]);
    const [neuralPredictions, setNeuralPredictions] = useState([]);
    const [aiPatterns, setAiPatterns] = useState([]);
    const [aiRecommendations, setAiRecommendations] = useState([]);
    const [deepModels, setDeepModels] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [notification, setNotification] = useState(null);
    const [selectedModel, setSelectedModel] = useState('all');
    const [selectedFeature, setSelectedFeature] = useState('all');
    const [refreshInterval, setRefreshInterval] = useState(null);
    const [inputText, setInputText] = useState('');
    const [testInput, setTestInput] = useState({});

    const models = [
        { text: 'All Models', value: 'all' },
        { text: 'Betting Pattern Predictor', value: 'betting_pattern_predictor' },
        { text: 'Odds Movement Predictor', value: 'odds_movement_predictor' },
        { text: 'Injury Impact Predictor', value: 'injury_impact_predictor' }
    ];

    const features = [
        { text: 'All Features', value: 'all' },
        { text: 'Sentiment Analysis', value: 'sentiment' },
        { text: 'Neural Networks', value: 'neural' },
        { text: 'Pattern Recognition', value: 'patterns' },
        { text: 'AI Recommendations', value: 'recommendations' }
    ];

    useEffect(() => {
        fetchAdvancedAIFeatures();
        setupAutoRefresh();
        
        return () => {
            if (refreshInterval) {
                clearInterval(refreshInterval);
            }
        };
    }, [selectedModel, selectedFeature]);

    const setupAutoRefresh = () => {
        // Refresh data every 3 minutes
        const interval = setInterval(() => {
            fetchAdvancedAIFeatures();
        }, 3 * 60 * 1000);
        
        setRefreshInterval(interval);
    };

    const fetchAdvancedAIFeatures = async () => {
        try {
            setLoading(true);
            setError(null);

            // Fetch sentiment analysis
            const sentimentResponse = await apiService.getSentimentAnalysis();
            if (sentimentResponse.success) {
                setSentimentAnalysis(sentimentResponse.data);
            }

            // Fetch neural network predictions
            const predictionsResponse = await apiService.getNeuralPredictions(selectedModel);
            if (predictionsResponse.success) {
                setNeuralPredictions(predictionsResponse.data);
            }

            // Fetch AI patterns
            const patternsResponse = await apiService.getAIPatterns();
            if (patternsResponse.success) {
                setAiPatterns(patternsResponse.data);
            }

            // Fetch AI recommendations
            const recommendationsResponse = await apiService.getAIRecommendations();
            if (recommendationsResponse.success) {
                setAiRecommendations(recommendationsResponse.data);
            }

            // Fetch deep learning models
            const modelsResponse = await apiService.getDeepLearningModels();
            if (modelsResponse.success) {
                setDeepModels(modelsResponse.data);
            }

            setNotification({
                type: 'success',
                message: 'Advanced AI features updated successfully'
            });

        } catch (err) {
            console.error('Error fetching advanced AI features:', err);
            setError('Failed to load advanced AI features');
            setNotification({
                type: 'error',
                message: 'Error loading advanced AI features'
            });
        } finally {
            setLoading(false);
        }
    };

    const closeNotification = () => {
        setNotification(null);
    };

    const getSentimentColor = (sentiment) => {
        const colors = {
            'positive': '#28a745',
            'negative': '#dc3545',
            'neutral': '#6c757d'
        };
        return colors[sentiment] || '#6c757d';
    };

    const getEmotionIcon = (emotion) => {
        const icons = {
            'optimistic': '😊',
            'pessimistic': '😔',
            'neutral': '😐'
        };
        return icons[emotion] || '😐';
    };

    const getConfidenceColor = (confidence) => {
        if (confidence >= 0.8) return '#28a745';
        if (confidence >= 0.6) return '#ffc107';
        if (confidence >= 0.4) return '#fd7e14';
        return '#dc3545';
    };

    const formatPercentage = (value) => {
        return `${(value * 100).toFixed(1)}%`;
    };

    const analyzeSentiment = async () => {
        try {
            if (!inputText.trim()) {
                setNotification({
                    type: 'warning',
                    message: 'Please enter text to analyze'
                });
                return;
            }

            const response = await apiService.analyzeSentiment(inputText);
            if (response.success) {
                setNotification({
                    type: 'success',
                    message: 'Sentiment analysis completed successfully'
                });
                fetchAdvancedAIFeatures(); // Refresh data
                setInputText(''); // Clear input
            }
        } catch (err) {
            setNotification({
                type: 'error',
                message: 'Failed to analyze sentiment'
            });
        }
    };

    const makeNeuralPrediction = async () => {
        try {
            const response = await apiService.makeNeuralPrediction(selectedModel, testInput);
            if (response.success) {
                setNotification({
                    type: 'success',
                    message: 'Neural network prediction completed successfully'
                });
                fetchAdvancedAIFeatures(); // Refresh data
            }
        } catch (err) {
            setNotification({
                type: 'error',
                message: 'Failed to make neural prediction'
            });
        }
    };

    if (loading && sentimentAnalysis.length === 0) {
        return (
            <div className="advanced-ai-features-v3-dashboard">
                <div style={{ textAlign: 'center', padding: '50px' }}>
                    <div className="k-loading"></div>
                    <p>Loading Advanced AI Features...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="advanced-ai-features-v3-dashboard">
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
                            <h2 style={{ margin: '0 0 8px 0' }}>🧠 Advanced AI Features V3 Dashboard</h2>
                            <p style={{ margin: 0, color: '#666', fontSize: '14px' }}>
                                Cutting-edge AI with deep learning, sentiment analysis, pattern recognition, and neural networks
                            </p>
                        </div>
                        
                        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                            <DropDownList
                                data={models}
                                value={models.find(m => m.value === selectedModel)}
                                onChange={(e) => setSelectedModel(e.target.value)}
                                textField="text"
                                valueField="value"
                                style={{ width: '180px' }}
                            />
                            
                            <DropDownList
                                data={features}
                                value={features.find(f => f.value === selectedFeature)}
                                onChange={(e) => setSelectedFeature(e.target.value)}
                                textField="text"
                                valueField="value"
                                style={{ width: '150px' }}
                            />
                            
                            <Button 
                                themeColor="primary" 
                                size="small" 
                                onClick={fetchAdvancedAIFeatures}
                                icon="refresh"
                                disabled={loading}
                            >
                                {loading ? 'Refreshing...' : 'Refresh'}
                            </Button>
                        </div>
                    </div>
                </CardBody>
            </Card>

            {/* Deep Learning Models Overview */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px', marginBottom: '24px' }}>
                {deepModels.map((model, index) => (
                    <Card key={index}>
                        <CardBody>
                            <div style={{ textAlign: 'center' }}>
                                <h3 style={{ margin: '0 0 8px 0', fontSize: '16px', color: '#666' }}>
                                    {model.name}
                                </h3>
                                <div style={{ fontSize: '28px', fontWeight: 'bold', color: getConfidenceColor(model.accuracy) }}>
                                    {formatPercentage(model.accuracy)}
                                </div>
                                <div style={{ fontSize: '14px', color: '#666' }}>
                                    Accuracy
                                </div>
                                <div style={{ marginTop: '8px' }}>
                                    <ProgressBar 
                                        value={model.accuracy * 100} 
                                        color={getConfidenceColor(model.accuracy)}
                                        style={{ height: '8px' }}
                                    />
                                </div>
                                <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                                    {model.parameters.toLocaleString()} parameters
                                </div>
                                <div style={{ fontSize: '12px', color: '#666' }}>
                                    {model.architecture}
                                </div>
                            </div>
                        </CardBody>
                    </Card>
                ))}
            </div>

            {/* Sentiment Analysis */}
            <Card style={{ marginBottom: '24px' }}>
                <CardBody>
                    <h3 style={{ margin: '0 0 16px 0' }}>🧠 Sentiment Analysis</h3>
                    
                    {/* Input Section */}
                    <div style={{ marginBottom: '16px' }}>
                        <TextArea
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                            placeholder="Enter text to analyze sentiment..."
                            style={{ width: '100%', minHeight: '80px', marginBottom: '8px' }}
                        />
                        <Button 
                            themeColor="primary" 
                            size="small" 
                            onClick={analyzeSentiment}
                            icon="search"
                        >
                            Analyze Sentiment
                        </Button>
                    </div>
                    
                    <Grid
                        data={sentimentAnalysis}
                        style={{ height: '400px' }}
                    >
                        <GridColumn field="text" title="Text" width="300px" />
                        <GridColumn 
                            field="sentiment_label" 
                            title="Sentiment" 
                            width="100px"
                            cell={(props) => (
                                <td>
                                    <Badge 
                                        themeColor={getSentimentColor(props.dataItem.sentiment_label)}
                                        style={{ fontSize: '12px' }}
                                    >
                                        {props.dataItem.sentiment_label.toUpperCase()}
                                    </Badge>
                                </td>
                            )}
                        />
                        <GridColumn 
                            field="sentiment_score" 
                            title="Score" 
                            width="100px"
                            cell={(props) => (
                                <td>
                                    <div style={{ 
                                        color: getSentimentColor(props.dataItem.sentiment_label),
                                        fontWeight: 'bold'
                                    }}>
                                        {props.dataItem.sentiment_score.toFixed(2)}
                                    </div>
                                </td>
                            )}
                        />
                        <GridColumn 
                            field="emotion" 
                            title="Emotion" 
                            width="100px"
                            cell={(props) => (
                                <td>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                                        <span>{getEmotionIcon(props.dataItem.emotion)}</span>
                                        <span>{props.dataItem.emotion}</span>
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
                            field="entities" 
                            title="Entities" 
                            width="150px"
                            cell={(props) => (
                                <td>
                                    <div style={{ fontSize: '12px' }}>
                                        {props.dataItem.entities.slice(0, 3).join(', ')}
                                        {props.dataItem.entities.length > 3 && '...'}
                                    </div>
                                </td>
                            )}
                        />
                    </Grid>
                </CardBody>
            </Card>

            {/* Neural Network Predictions */}
            <Card style={{ marginBottom: '24px' }}>
                <CardBody>
                    <h3 style={{ margin: '0 0 16px 0' }}>🤖 Neural Network Predictions</h3>
                    <PanelBar>
                        {neuralPredictions.map((prediction, index) => (
                            <PanelBarItem title={`${prediction.model_name} - ${prediction.created_at}`} key={index}>
                                <div style={{ padding: '16px' }}>
                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                                        <div>
                                            <h4 style={{ margin: '0 0 8px 0' }}>Model Output</h4>
                                            <div style={{ fontSize: '14px', lineHeight: '1.5' }}>
                                                {Object.entries(prediction.output).map(([key, value]) => (
                                                    <div key={key} style={{ marginBottom: '4px' }}>
                                                        <strong>{key}:</strong> {typeof value === 'number' ? value.toFixed(3) : value}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                        <div>
                                            <h4 style={{ margin: '0 0 8px 0' }}>Performance Metrics</h4>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                                                <span>Confidence:</span>
                                                <CircularGauge
                                                    value={prediction.confidence * 100}
                                                    min={0}
                                                    max={100}
                                                    style={{ height: '40px' }}
                                                    color={getConfidenceColor(prediction.confidence)}
                                                />
                                                <span>{formatPercentage(prediction.confidence)}</span>
                                            </div>
                                            <div style={{ fontSize: '14px' }}>
                                                Processing Time: {prediction.processing_time.toFixed(3)}s
                                            </div>
                                            <div style={{ fontSize: '14px' }}>
                                                Model Version: {prediction.model_version}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </PanelBarItem>
                        ))}
                    </PanelBar>
                </CardBody>
            </Card>

            {/* AI Patterns */}
            <Card style={{ marginBottom: '24px' }}>
                <CardBody>
                    <h3 style={{ margin: '0 0 16px 0' }}>🔍 AI Pattern Recognition</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px' }}>
                        {aiPatterns.map((pattern, index) => (
                            <div key={index} style={{ 
                                padding: '16px', 
                                border: '1px solid #e9ecef', 
                                borderRadius: '8px',
                                backgroundColor: '#f8f9fa'
                            }}>
                                <div style={{ fontWeight: 'bold', color: '#007bff', marginBottom: '8px' }}>
                                    {pattern.pattern_type.replace('_', ' ').toUpperCase()}
                                </div>
                                <div style={{ fontSize: '14px', marginBottom: '8px' }}>
                                    {pattern.description}
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#666' }}>
                                    <span>Confidence: {formatPercentage(pattern.confidence)}</span>
                                    <span>Significance: {formatPercentage(pattern.significance)}</span>
                                </div>
                                <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                                    Data Points: {pattern.data_points}
                                </div>
                            </div>
                        ))}
                    </div>
                </CardBody>
            </Card>

            {/* AI Recommendations */}
            <Card style={{ marginBottom: '24px' }}>
                <CardBody>
                    <h3 style={{ margin: '0 0 16px 0' }}>💡 AI Recommendations</h3>
                    <Grid
                        data={aiRecommendations}
                        style={{ height: '400px' }}
                    >
                        <GridColumn field="type" title="Type" width="150px" />
                        <GridColumn field="title" title="Title" width="200px" />
                        <GridColumn 
                            field="description" 
                            title="Description" 
                            width="300px"
                            cell={(props) => (
                                <td>
                                    <div style={{ fontSize: '12px' }}>
                                        {props.dataItem.description.length > 100 
                                            ? props.dataItem.description.substring(0, 100) + '...'
                                            : props.dataItem.description
                                        }
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
                            field="impact_score" 
                            title="Impact" 
                            width="100px"
                            cell={(props) => (
                                <td>
                                    <div style={{ 
                                        color: getConfidenceColor(props.dataItem.impact_score),
                                        fontWeight: 'bold'
                                    }}>
                                        {formatPercentage(props.dataItem.impact_score)}
                                    </div>
                                </td>
                            )}
                        />
                        <GridColumn 
                            field="action_items" 
                            title="Actions" 
                            width="200px"
                            cell={(props) => (
                                <td>
                                    <div style={{ fontSize: '12px' }}>
                                        {props.dataItem.action_items.slice(0, 2).join(', ')}
                                        {props.dataItem.action_items.length > 2 && '...'}
                                    </div>
                                </td>
                            )}
                        />
                    </Grid>
                </CardBody>
            </Card>

            {/* AI Performance Chart */}
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px', marginBottom: '24px' }}>
                <Card>
                    <CardBody>
                        <h3 style={{ margin: '0 0 16px 0' }}>📊 AI Model Performance</h3>
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
                                    data={[0.82, 0.84, 0.86, 0.85, 0.88, 0.87, 0.89, 0.91]} 
                                    name="Betting Pattern Predictor"
                                    color="#007bff"
                                />
                                <ChartSeriesItem 
                                    type="line" 
                                    data={[0.78, 0.79, 0.81, 0.80, 0.83, 0.82, 0.84, 0.86]} 
                                    name="Odds Movement Predictor"
                                    color="#28a745"
                                />
                                <ChartSeriesItem 
                                    type="line" 
                                    data={[0.82, 0.83, 0.85, 0.84, 0.87, 0.86, 0.88, 0.90]} 
                                    name="Injury Impact Predictor"
                                    color="#fd7e14"
                                />
                            </ChartSeries>
                        </Chart>
                    </CardBody>
                </Card>

                <Card>
                    <CardBody>
                        <h3 style={{ margin: '0 0 16px 0' }}>🧠 AI Feature Usage</h3>
                        <Chart style={{ height: '300px' }}>
                            <ChartTooltip />
                            <ChartSeries>
                                <ChartSeriesItem 
                                    type="donut" 
                                    data={[
                                        { category: "Sentiment Analysis", value: 35 },
                                        { category: "Neural Networks", value: 30 },
                                        { category: "Pattern Recognition", value: 20 },
                                        { category: "AI Recommendations", value: 15 }
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
                    🔄 Advanced AI features update every 3 minutes. Last update: {new Date().toLocaleTimeString()}
                </p>
                <p>
                    🧠 Powered by deep learning, neural networks, and cutting-edge AI algorithms
                </p>
            </div>
        </div>
    );
};

export default AdvancedAIFeaturesV3Dashboard; 