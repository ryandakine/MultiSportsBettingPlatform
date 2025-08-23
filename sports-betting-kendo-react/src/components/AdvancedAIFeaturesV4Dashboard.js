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

const AdvancedAIFeaturesV4Dashboard = () => {
    const [transformerPredictions, setTransformerPredictions] = useState([]);
    const [ensemblePredictions, setEnsemblePredictions] = useState([]);
    const [aiPatterns, setAiPatterns] = useState([]);
    const [aiRecommendations, setAiRecommendations] = useState([]);
    const [transformerModels, setTransformerModels] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [notification, setNotification] = useState(null);
    const [selectedModel, setSelectedModel] = useState('all');
    const [selectedFeature, setSelectedFeature] = useState('all');
    const [refreshInterval, setRefreshInterval] = useState(null);

    const models = [
        { text: 'All Models', value: 'all' },
        { text: 'Betting Pattern Transformer', value: 'betting_pattern_transformer' },
        { text: 'Odds Prediction Transformer', value: 'odds_prediction_transformer' },
        { text: 'User Behavior Transformer', value: 'user_behavior_transformer' }
    ];

    const features = [
        { text: 'All Features', value: 'all' },
        { text: 'Transformer Models', value: 'transformer' },
        { text: 'Ensemble Learning', value: 'ensemble' },
        { text: 'Pattern Recognition', value: 'patterns' },
        { text: 'AI Recommendations', value: 'recommendations' }
    ];

    useEffect(() => {
        fetchAdvancedAIFeaturesV4();
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
            fetchAdvancedAIFeaturesV4();
        }, 3 * 60 * 1000);
        
        setRefreshInterval(interval);
    };

    const fetchAdvancedAIFeaturesV4 = async () => {
        try {
            setLoading(true);
            setError(null);

            // Fetch transformer predictions
            const transformerResponse = await apiService.getTransformerPredictions(selectedModel);
            if (transformerResponse.success) {
                setTransformerPredictions(transformerResponse.data);
            }

            // Fetch ensemble predictions
            const ensembleResponse = await apiService.getEnsemblePredictions();
            if (ensembleResponse.success) {
                setEnsemblePredictions(ensembleResponse.data);
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

            // Fetch transformer models
            const modelsResponse = await apiService.getTransformerModels();
            if (modelsResponse.success) {
                setTransformerModels(modelsResponse.data);
            }

            setNotification({
                type: 'success',
                message: 'Advanced AI Features V4 updated successfully'
            });

        } catch (err) {
            console.error('Error fetching advanced AI features V4:', err);
            setError('Failed to load advanced AI features V4');
            setNotification({
                type: 'error',
                message: 'Error loading advanced AI features V4'
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

    const getPriorityColor = (priority) => {
        const colors = {
            'critical': '#dc3545',
            'high': '#fd7e14',
            'medium': '#ffc107',
            'low': '#28a745'
        };
        return colors[priority] || '#6c757d';
    };

    const formatPercentage = (value) => {
        return `${(value * 100).toFixed(1)}%`;
    };

    if (loading && transformerPredictions.length === 0) {
        return (
            <div className="advanced-ai-features-v4-dashboard">
                <div style={{ textAlign: 'center', padding: '50px' }}>
                    <div className="k-loading"></div>
                    <p>Loading Advanced AI Features V4...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="advanced-ai-features-v4-dashboard">
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
                            <h2 style={{ margin: '0 0 8px 0' }}>🧠 Advanced AI Features V4 Dashboard</h2>
                            <p style={{ margin: 0, color: '#666', fontSize: '14px' }}>
                                Cutting-edge AI with transformer models, ensemble learning, attention mechanisms, and sophisticated AI capabilities
                            </p>
                        </div>
                        
                        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                            <DropDownList
                                data={models}
                                value={models.find(m => m.value === selectedModel)}
                                onChange={(e) => setSelectedModel(e.target.value)}
                                textField="text"
                                valueField="value"
                                style={{ width: '200px' }}
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
                                onClick={fetchAdvancedAIFeaturesV4}
                                icon="refresh"
                                disabled={loading}
                            >
                                {loading ? 'Refreshing...' : 'Refresh'}
                            </Button>
                        </div>
                    </div>
                </CardBody>
            </Card>

            {/* Transformer Models Overview */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px', marginBottom: '24px' }}>
                {transformerModels.map((model, index) => (
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
                                <div style={{ fontSize: '12px', color: '#666' }}>
                                    {model.layers} layers, {model.attention_heads} heads
                                </div>
                            </div>
                        </CardBody>
                    </Card>
                ))}
            </div>

            {/* Transformer Predictions */}
            <Card style={{ marginBottom: '24px' }}>
                <CardBody>
                    <h3 style={{ margin: '0 0 16px 0' }}>🤖 Transformer Model Predictions</h3>
                    <PanelBar>
                        {transformerPredictions.map((prediction, index) => (
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
                                            {prediction.attention_weights && (
                                                <div style={{ fontSize: '14px' }}>
                                                    Attention Heads: {Object.keys(prediction.attention_weights).length}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                    
                                    {prediction.attention_weights && (
                                        <div style={{ 
                                            padding: '12px', 
                                            backgroundColor: '#f8f9fa', 
                                            borderRadius: '8px',
                                            border: '1px solid #e9ecef'
                                        }}>
                                            <h4 style={{ margin: '0 0 8px 0', color: '#007bff' }}>🧠 Attention Weights</h4>
                                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '8px' }}>
                                                {Object.entries(prediction.attention_weights).slice(0, 6).map(([key, value]) => (
                                                    <div key={key} style={{ fontSize: '12px' }}>
                                                        <strong>{key}:</strong> {value.toFixed(3)}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </PanelBarItem>
                        ))}
                    </PanelBar>
                </CardBody>
            </Card>

            {/* Ensemble Predictions */}
            <Card style={{ marginBottom: '24px' }}>
                <CardBody>
                    <h3 style={{ margin: '0 0 16px 0' }}>🎯 Ensemble Learning Predictions</h3>
                    <Grid
                        data={ensemblePredictions}
                        style={{ height: '400px' }}
                    >
                        <GridColumn field="ensemble_id" title="Ensemble ID" width="200px" />
                        <GridColumn 
                            field="model_ensemble" 
                            title="Models" 
                            width="200px"
                            cell={(props) => (
                                <td>
                                    <div style={{ fontSize: '12px' }}>
                                        {props.dataItem.model_ensemble.slice(0, 2).join(', ')}
                                        {props.dataItem.model_ensemble.length > 2 && '...'}
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
                            field="processing_time" 
                            title="Processing Time" 
                            width="120px"
                            cell={(props) => (
                                <td>
                                    {props.dataItem.processing_time.toFixed(3)}s
                                </td>
                            )}
                        />
                        <GridColumn 
                            field="model_weights" 
                            title="Model Weights" 
                            width="200px"
                            cell={(props) => (
                                <td>
                                    <div style={{ fontSize: '12px' }}>
                                        {Object.entries(props.dataItem.model_weights).slice(0, 2).map(([model, weight]) => (
                                            <div key={model}>{model}: {weight.toFixed(2)}</div>
                                        ))}
                                    </div>
                                </td>
                            )}
                        />
                    </Grid>
                </CardBody>
            </Card>

            {/* AI Patterns */}
            <Card style={{ marginBottom: '24px' }}>
                <CardBody>
                    <h3 style={{ margin: '0 0 16px 0' }}>🔍 Advanced AI Pattern Recognition</h3>
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
                                    Complexity: {formatPercentage(pattern.complexity_score)}
                                </div>
                                <div style={{ fontSize: '12px', color: '#666' }}>
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
                    <h3 style={{ margin: '0 0 16px 0' }}>💡 Advanced AI Recommendations</h3>
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
                            field="priority" 
                            title="Priority" 
                            width="100px"
                            cell={(props) => (
                                <td>
                                    <Badge 
                                        themeColor={getPriorityColor(props.dataItem.priority)}
                                        style={{ fontSize: '12px' }}
                                    >
                                        {props.dataItem.priority.toUpperCase()}
                                    </Badge>
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
                        <h3 style={{ margin: '0 0 16px 0' }}>📊 Advanced AI Performance</h3>
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
                                    data={[0.88, 0.90, 0.92, 0.91, 0.94, 0.93, 0.95, 0.96]} 
                                    name="Transformer Accuracy"
                                    color="#007bff"
                                />
                                <ChartSeriesItem 
                                    type="line" 
                                    data={[0.85, 0.87, 0.89, 0.88, 0.91, 0.90, 0.92, 0.93]} 
                                    name="Ensemble Accuracy"
                                    color="#28a745"
                                />
                                <ChartSeriesItem 
                                    type="line" 
                                    data={[0.82, 0.84, 0.86, 0.85, 0.88, 0.87, 0.89, 0.90]} 
                                    name="Pattern Recognition"
                                    color="#fd7e14"
                                />
                            </ChartSeries>
                        </Chart>
                    </CardBody>
                </Card>

                <Card>
                    <CardBody>
                        <h3 style={{ margin: '0 0 16px 0' }}>🧠 AI Model Distribution</h3>
                        <Chart style={{ height: '300px' }}>
                            <ChartTooltip />
                            <ChartSeries>
                                <ChartSeriesItem 
                                    type="donut" 
                                    data={[
                                        { category: "Transformer Models", value: 40 },
                                        { category: "Ensemble Learning", value: 30 },
                                        { category: "Pattern Recognition", value: 20 },
                                        { category: "AI Recommendations", value: 10 }
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
                    🔄 Advanced AI Features V4 updates every 3 minutes. Last update: {new Date().toLocaleTimeString()}
                </p>
                <p>
                    🧠 Powered by transformer models, ensemble learning, attention mechanisms, and cutting-edge AI algorithms
                </p>
            </div>
        </div>
    );
};

export default AdvancedAIFeaturesV4Dashboard; 