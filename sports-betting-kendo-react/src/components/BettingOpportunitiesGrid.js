
import React, { useState, useEffect } from 'react';
import { Grid, GridColumn } from '@progress/kendo-react-grid';
import { Button } from '@progress/kendo-react-buttons';
import { Dialog, DialogActionsBar } from '@progress/kendo-react-dialogs';
import { Form, Field, FormElement } from '@progress/kendo-react-form';
import { NumericTextBox } from '@progress/kendo-react-inputs';
import { DropDownList } from '@progress/kendo-react-dropdowns';
import { Notification } from '@progress/kendo-react-notification';
import apiService from '../services/ApiService';

const BettingOpportunitiesGrid = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [notification, setNotification] = useState(null);
    const [showBetDialog, setShowBetDialog] = useState(false);
    const [selectedOpportunity, setSelectedOpportunity] = useState(null);
    const [placingBet, setPlacingBet] = useState(false);

    useEffect(() => {
        fetchBettingOpportunities();
        
        // Set up auto-refresh every 30 seconds
        const interval = setInterval(fetchBettingOpportunities, 30000);
        return () => clearInterval(interval);
    }, []);

    const fetchBettingOpportunities = async () => {
        try {
            setLoading(true);
            setError(null);

            const response = await apiService.getBettingOpportunities();
            
            if (response.success) {
                setData(response.data);
            } else {
                setError(response.message || 'Failed to load betting opportunities');
                setNotification({
                    type: 'error',
                    message: response.message || 'Failed to load betting opportunities'
                });
            }
        } catch (err) {
            console.error('Error fetching betting opportunities:', err);
            setError('Network error occurred');
            setNotification({
                type: 'error',
                message: 'Network error occurred'
            });
        } finally {
            setLoading(false);
        }
    };

    const handlePlaceBet = (dataItem) => {
        setSelectedOpportunity(dataItem);
        setShowBetDialog(true);
    };

    const handleBetSubmit = async (dataItem) => {
        try {
            setPlacingBet(true);
            
            const response = await apiService.placeBet(
                selectedOpportunity.id,
                dataItem.amount,
                dataItem.selection
            );

            if (response.success) {
                setNotification({
                    type: 'success',
                    message: `Bet placed successfully! Bet ID: ${response.data.bet_id}`
                });
                setShowBetDialog(false);
                // Refresh opportunities
                fetchBettingOpportunities();
            } else {
                setNotification({
                    type: 'error',
                    message: response.message || 'Failed to place bet'
                });
            }
        } catch (err) {
            console.error('Error placing bet:', err);
            setNotification({
                type: 'error',
                message: 'Network error occurred while placing bet'
            });
        } finally {
            setPlacingBet(false);
        }
    };

    const handleCloseBetDialog = () => {
        setShowBetDialog(false);
        setSelectedOpportunity(null);
    };

    const closeNotification = () => {
        setNotification(null);
    };

    // Custom cell renderers
    const MatchCell = (props) => (
        <td>
            <div style={{ fontWeight: 'bold' }}>
                {props.dataItem.homeTeam} vs {props.dataItem.awayTeam}
            </div>
            <div style={{ fontSize: '12px', color: '#666' }}>
                {new Date(props.dataItem.gameTime).toLocaleString()}
            </div>
        </td>
    );

    const OddsCell = (props) => (
        <td>
            <div style={{ display: 'flex', gap: '8px' }}>
                <span style={{ padding: '2px 6px', backgroundColor: '#e3f2fd', borderRadius: '4px' }}>
                    H: {props.dataItem.homeOdds}
                </span>
                <span style={{ padding: '2px 6px', backgroundColor: '#f3e5f5', borderRadius: '4px' }}>
                    A: {props.dataItem.awayOdds}
                </span>
            </div>
        </td>
    );

    const PredictionCell = (props) => (
        <td>
            <span 
                style={{ 
                    padding: '4px 8px', 
                    borderRadius: '4px', 
                    backgroundColor: '#3f51b5', 
                    color: 'white',
                    fontSize: '12px',
                    fontWeight: '500'
                }}
            >
                {props.dataItem.prediction}
            </span>
        </td>
    );

    const ConfidenceCell = (props) => (
        <td>
            <div style={{ position: 'relative', width: '100%', height: '20px', backgroundColor: '#f5f5f5', borderRadius: '10px', overflow: 'hidden' }}>
                <div 
                    style={{ 
                        width: `${props.dataItem.confidence}%`, 
                        height: '100%', 
                        background: `linear-gradient(90deg, #dc3545 0%, #ffc107 50%, #28a745 100%)`,
                        transition: 'width 0.3s ease'
                    }}
                ></div>
                <span 
                    style={{ 
                        position: 'absolute', 
                        top: '50%', 
                        left: '50%', 
                        transform: 'translate(-50%, -50%)', 
                        fontSize: '11px', 
                        fontWeight: 'bold',
                        color: '#333',
                        textShadow: '1px 1px 1px rgba(255,255,255,0.8)'
                    }}
                >
                    {props.dataItem.confidence.toFixed(1)}%
                </span>
            </div>
        </td>
    );

    const ROICell = (props) => (
        <td>
            <span 
                style={{ 
                    color: props.dataItem.expectedROI > 0 ? '#28a745' : '#dc3545', 
                    fontWeight: 'bold' 
                }}
            >
                {props.dataItem.expectedROI.toFixed(1)}%
            </span>
        </td>
    );

    const RiskCell = (props) => {
        const riskColors = {
            'Low': '#28a745',
            'Medium': '#ffc107',
            'High': '#dc3545'
        };
        
        return (
            <td>
                <span 
                    style={{ 
                        padding: '2px 8px', 
                        borderRadius: '12px', 
                        fontSize: '11px', 
                        fontWeight: '500',
                        backgroundColor: riskColors[props.dataItem.riskLevel],
                        color: 'white',
                        textTransform: 'uppercase'
                    }}
                >
                    {props.dataItem.riskLevel}
                </span>
            </td>
        );
    };

    const StatusCell = (props) => {
        const statusColors = {
            'Live': '#28a745',
            'Upcoming': '#007bff'
        };
        
        return (
            <td>
                <span 
                    style={{ 
                        padding: '2px 8px', 
                        borderRadius: '12px', 
                        fontSize: '11px', 
                        fontWeight: '500',
                        backgroundColor: statusColors[props.dataItem.status],
                        color: 'white',
                        textTransform: 'uppercase',
                        animation: props.dataItem.status === 'Live' ? 'pulse 2s infinite' : 'none'
                    }}
                >
                    {props.dataItem.status}
                </span>
            </td>
        );
    };

    const ActionCell = (props) => (
        <td>
            <Button 
                themeColor="primary" 
                size="small"
                onClick={() => handlePlaceBet(props.dataItem)}
                disabled={props.dataItem.status !== 'Live' && props.dataItem.status !== 'Upcoming'}
            >
                Place Bet
            </Button>
        </td>
    );

    if (loading && data.length === 0) {
        return (
            <div className="grid-container">
                <div style={{ textAlign: 'center', padding: '50px' }}>
                    <div className="k-loading"></div>
                    <p>Loading betting opportunities...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="grid-container">
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
                <h3>Live Betting Opportunities</h3>
                <div>
                    <Button 
                        themeColor="primary" 
                        size="small" 
                        onClick={fetchBettingOpportunities}
                        icon="refresh"
                        disabled={loading}
                    >
                        {loading ? 'Refreshing...' : 'Refresh'}
                    </Button>
                </div>
            </div>

            <Grid
                data={data}
                pageable={true}
                sortable={true}
                filterable={true}
                groupable={true}
                resizable={true}
                reorderable={true}
                height="500px"
                loading={loading}
            >
                <GridColumn field="sport" title="Sport" width="100px" />
                <GridColumn title="Match" width="200px" cell={MatchCell} />
                <GridColumn title="Odds" width="120px" cell={OddsCell} />
                <GridColumn title="Prediction" width="100px" cell={PredictionCell} />
                <GridColumn title="Confidence" width="120px" cell={ConfidenceCell} />
                <GridColumn title="Expected ROI" width="110px" cell={ROICell} />
                <GridColumn title="Risk" width="80px" cell={RiskCell} />
                <GridColumn title="Status" width="80px" cell={StatusCell} />
                <GridColumn title="Actions" width="120px" cell={ActionCell} />
            </Grid>

            {showBetDialog && selectedOpportunity && (
                <Dialog 
                    title={`Place Bet - ${selectedOpportunity.homeTeam} vs ${selectedOpportunity.awayTeam}`}
                    onClose={handleCloseBetDialog}
                    width={500}
                >
                    <Form
                        initialValues={{
                            amount: 100,
                            selection: selectedOpportunity.prediction.toLowerCase() === selectedOpportunity.homeTeam.toLowerCase() ? 'home' : 'away'
                        }}
                        onSubmit={handleBetSubmit}
                        render={(formRenderProps) => (
                            <FormElement style={{ maxWidth: 450 }}>
                                <div style={{ marginBottom: '16px', padding: '12px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
                                    <p><strong>Match:</strong> {selectedOpportunity.homeTeam} vs {selectedOpportunity.awayTeam}</p>
                                    <p><strong>Sport:</strong> {selectedOpportunity.sport}</p>
                                    <p><strong>Recommended:</strong> {selectedOpportunity.prediction}</p>
                                    <p><strong>Confidence:</strong> {selectedOpportunity.confidence.toFixed(1)}%</p>
                                    <p><strong>Expected ROI:</strong> <span style={{ color: selectedOpportunity.expectedROI > 0 ? '#28a745' : '#dc3545' }}>
                                        {selectedOpportunity.expectedROI.toFixed(1)}%
                                    </span></p>
                                </div>

                                <Field
                                    name="selection"
                                    component={DropDownList}
                                    label="Your Selection"
                                    data={[
                                        { text: `${selectedOpportunity.homeTeam} (${selectedOpportunity.homeOdds})`, value: 'home' },
                                        { text: `${selectedOpportunity.awayTeam} (${selectedOpportunity.awayOdds})`, value: 'away' }
                                    ]}
                                    textField="text"
                                    valueField="value"
                                    required={true}
                                />

                                <Field
                                    name="amount"
                                    component={NumericTextBox}
                                    label="Bet Amount ($)"
                                    min={10}
                                    max={1000}
                                    step={10}
                                    format="c2"
                                    required={true}
                                />

                                <div style={{ marginTop: '16px', fontSize: '14px', color: '#666' }}>
                                    <p>⚠️ Please bet responsibly. Only bet what you can afford to lose.</p>
                                </div>

                                <DialogActionsBar>
                                    <Button 
                                        type="submit" 
                                        themeColor="primary"
                                        disabled={placingBet || !formRenderProps.allowSubmit}
                                        loading={placingBet}
                                    >
                                        {placingBet ? 'Placing Bet...' : 'Place Bet'}
                                    </Button>
                                    <Button 
                                        onClick={handleCloseBetDialog}
                                        disabled={placingBet}
                                    >
                                        Cancel
                                    </Button>
                                </DialogActionsBar>
                            </FormElement>
                        )}
                    />
                </Dialog>
            )}

            <div style={{ marginTop: '16px', fontSize: '14px', color: '#666' }}>
                <p>
                    🔄 Data refreshes automatically every 30 seconds. 
                    Last update: {new Date().toLocaleTimeString()}
                </p>
                <p>
                    🎯 Click "Place Bet" to open the betting dialog. All bets are processed through our secure payment system.
                </p>
            </div>
        </div>
    );
};

export default BettingOpportunitiesGrid;
