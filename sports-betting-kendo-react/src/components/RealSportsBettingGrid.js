import React, { useState, useEffect } from 'react';
import { Grid, GridColumn } from '@progress/kendo-react-grid';
import { Button } from '@progress/kendo-react-buttons';
import { DropDownList } from '@progress/kendo-react-dropdowns';
import { Dialog, DialogActionsBar } from '@progress/kendo-react-dialogs';
import { Form, Field, FormElement } from '@progress/kendo-react-form';
import { NumericTextBox } from '@progress/kendo-react-inputs';
import { Notification } from '@progress/kendo-react-notification';
import { Card, CardBody } from '@progress/kendo-react-layout';
import realSportsApiService from '../services/RealSportsApiService';
import apiService from '../services/ApiService';

const RealSportsBettingGrid = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [notification, setNotification] = useState(null);
    const [selectedSport, setSelectedSport] = useState('nfl');
    const [showBetDialog, setShowBetDialog] = useState(false);
    const [selectedGame, setSelectedGame] = useState(null);
    const [placingBet, setPlacingBet] = useState(false);
    const [weatherData, setWeatherData] = useState({});
    const [teamStats, setTeamStats] = useState({});
    const [liveUpdatesEnabled, setLiveUpdatesEnabled] = useState(true);

    const sports = [
        { text: 'NFL Football', value: 'nfl' },
        { text: 'NBA Basketball', value: 'nba' },
        { text: 'MLB Baseball', value: 'mlb' },
        { text: 'NHL Hockey', value: 'nhl' }
    ];

    useEffect(() => {
        fetchSportsData();
        
        let unsubscribe;
        if (liveUpdatesEnabled) {
            // Subscribe to live updates
            unsubscribe = realSportsApiService.subscribeToLiveUpdates((update) => {
                if (update.data[selectedSport]) {
                    setData(update.data[selectedSport]);
                    setNotification({
                        type: 'info',
                        message: `Live data updated for ${selectedSport.toUpperCase()}`
                    });
                }
            }, [selectedSport]);
        }

        return () => {
            if (unsubscribe) unsubscribe();
        };
    }, [selectedSport, liveUpdatesEnabled]);

    const fetchSportsData = async () => {
        try {
            setLoading(true);
            setError(null);

            // Fetch live games
            const gamesResponse = await realSportsApiService.getLiveGames(selectedSport);
            
            if (gamesResponse.success) {
                const games = gamesResponse.data;
                setData(games);

                // Fetch additional data for each game
                await fetchAdditionalGameData(games);
                
                setNotification({
                    type: 'success',
                    message: `Loaded ${games.length} live ${selectedSport.toUpperCase()} games`
                });
            } else {
                setError(gamesResponse.error || 'Failed to load games');
            }
        } catch (err) {
            console.error('Error fetching sports data:', err);
            setError('Network error occurred');
        } finally {
            setLoading(false);
        }
    };

    const fetchAdditionalGameData = async (games) => {
        const weatherPromises = [];
        const statsPromises = [];

        games.forEach(game => {
            // Fetch weather for outdoor sports
            if (['nfl', 'mlb'].includes(selectedSport)) {
                const city = game.venue.split(' ')[0]; // Simple city extraction
                weatherPromises.push(
                    realSportsApiService.getWeatherData(city)
                        .then(response => ({ gameId: game.id, weather: response.data }))
                );
            }

            // Fetch team stats
            statsPromises.push(
                realSportsApiService.getTeamStats(game.homeTeam, selectedSport)
                    .then(response => ({ team: game.homeTeam, stats: response.data })),
                realSportsApiService.getTeamStats(game.awayTeam, selectedSport)
                    .then(response => ({ team: game.awayTeam, stats: response.data }))
            );
        });

        // Process weather data
        try {
            const weatherResults = await Promise.all(weatherPromises);
            const weatherMap = {};
            weatherResults.forEach(result => {
                if (result.weather) {
                    weatherMap[result.gameId] = result.weather;
                }
            });
            setWeatherData(weatherMap);
        } catch (error) {
            console.warn('Error fetching weather data:', error);
        }

        // Process team stats
        try {
            const statsResults = await Promise.all(statsPromises);
            const statsMap = {};
            statsResults.forEach(result => {
                if (result.stats) {
                    statsMap[result.team] = result.stats;
                }
            });
            setTeamStats(statsMap);
        } catch (error) {
            console.warn('Error fetching team stats:', error);
        }
    };

    const handleSportChange = (event) => {
        setSelectedSport(event.target.value);
    };

    const handlePlaceBet = (game) => {
        setSelectedGame(game);
        setShowBetDialog(true);
    };

    const handleBetSubmit = async (formData) => {
        try {
            setPlacingBet(true);
            
            // Use the real API service for bet placement
            const response = await apiService.placeBet(
                selectedGame.id,
                formData.amount,
                formData.selection
            );

            if (response.success) {
                setNotification({
                    type: 'success',
                    message: `Bet placed successfully! ${formData.selection} for $${formData.amount}`
                });
                setShowBetDialog(false);
                
                // Refresh data
                fetchSportsData();
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
                message: 'Network error while placing bet'
            });
        } finally {
            setPlacingBet(false);
        }
    };

    const handleRefresh = () => {
        fetchSportsData();
    };

    const closeNotification = () => {
        setNotification(null);
    };

    // Custom cell renderers
    const MatchupCell = (props) => {
        const game = props.dataItem;
        const homeStats = teamStats[game.homeTeam];
        const awayStats = teamStats[game.awayTeam];
        
        return (
            <td>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    <div style={{ fontWeight: 'bold', fontSize: '14px' }}>
                        {game.awayTeam} @ {game.homeTeam}
                    </div>
                    {game.status === 'Live' && (
                        <div style={{ fontSize: '16px', color: '#28a745', fontWeight: 'bold' }}>
                            {game.awayScore} - {game.homeScore}
                        </div>
                    )}
                    <div style={{ fontSize: '12px', color: '#666' }}>
                        {new Date(game.gameTime).toLocaleString()}
                    </div>
                    {homeStats && awayStats && (
                        <div style={{ fontSize: '11px', color: '#888' }}>
                            Records: {awayStats.record} vs {homeStats.record}
                        </div>
                    )}
                </div>
            </td>
        );
    };

    const StatusCell = (props) => {
        const game = props.dataItem;
        
        return (
            <td>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
                    <span 
                        style={{ 
                            padding: '4px 8px', 
                            borderRadius: '12px', 
                            fontSize: '11px', 
                            fontWeight: '500',
                            backgroundColor: game.status === 'Live' ? '#28a745' : '#007bff',
                            color: 'white',
                            textTransform: 'uppercase',
                            animation: game.status === 'Live' ? 'pulse 2s infinite' : 'none'
                        }}
                    >
                        {game.status}
                    </span>
                    {game.status === 'Live' && (
                        <div style={{ fontSize: '11px', textAlign: 'center' }}>
                            <div>{game.period}</div>
                            <div>{game.timeRemaining}</div>
                        </div>
                    )}
                </div>
            </td>
        );
    };

    const OddsCell = (props) => {
        const game = props.dataItem;
        
        return (
            <td>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    <div style={{ display: 'flex', gap: '8px' }}>
                        <span style={{ 
                            padding: '2px 6px', 
                            backgroundColor: '#e3f2fd', 
                            borderRadius: '4px',
                            fontSize: '12px'
                        }}>
                            H: {game.homeOdds}
                        </span>
                        <span style={{ 
                            padding: '2px 6px', 
                            backgroundColor: '#f3e5f5', 
                            borderRadius: '4px',
                            fontSize: '12px'
                        }}>
                            A: {game.awayOdds}
                        </span>
                    </div>
                    <div style={{ fontSize: '11px', color: '#666' }}>
                        Spread: {game.homeOdds > game.awayOdds ? '+' : ''}{((game.homeOdds - game.awayOdds) * 3).toFixed(1)}
                    </div>
                </div>
            </td>
        );
    };

    const PredictionCell = (props) => {
        const game = props.dataItem;
        
        return (
            <td>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    <span 
                        style={{ 
                            padding: '4px 8px', 
                            borderRadius: '4px', 
                            backgroundColor: '#3f51b5', 
                            color: 'white',
                            fontSize: '12px',
                            fontWeight: '500',
                            textAlign: 'center'
                        }}
                    >
                        {game.prediction}
                    </span>
                    <div style={{ fontSize: '11px', textAlign: 'center' }}>
                        {game.confidence}% confidence
                    </div>
                </div>
            </td>
        );
    };

    const WeatherCell = (props) => {
        const game = props.dataItem;
        const weather = weatherData[game.id];
        
        if (!weather || !['nfl', 'mlb'].includes(selectedSport)) {
            return <td>Indoor</td>;
        }
        
        return (
            <td>
                <div style={{ fontSize: '11px', textAlign: 'center' }}>
                    <div>{weather.temperature}°F</div>
                    <div>{weather.conditions}</div>
                    <div>{weather.windSpeed} mph {weather.windDirection}</div>
                </div>
            </td>
        );
    };

    const ROICell = (props) => {
        const game = props.dataItem;
        
        return (
            <td>
                <span 
                    style={{ 
                        color: game.expectedROI > 0 ? '#28a745' : '#dc3545', 
                        fontWeight: 'bold',
                        fontSize: '14px'
                    }}
                >
                    {game.expectedROI > 0 ? '+' : ''}{game.expectedROI}%
                </span>
            </td>
        );
    };

    const ActionCell = (props) => {
        const game = props.dataItem;
        
        return (
            <td>
                <Button 
                    themeColor="primary" 
                    size="small"
                    onClick={() => handlePlaceBet(game)}
                    disabled={game.status === 'Final'}
                >
                    {game.status === 'Live' ? 'Live Bet' : 'Place Bet'}
                </Button>
            </td>
        );
    };

    if (loading && data.length === 0) {
        return (
            <div className="grid-container">
                <div style={{ textAlign: 'center', padding: '50px' }}>
                    <div className="k-loading"></div>
                    <p>Loading real sports data...</p>
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

            {/* Header with controls */}
            <Card style={{ marginBottom: '16px' }}>
                <CardBody>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
                        <div>
                            <h3 style={{ margin: '0 0 8px 0' }}>Real Sports Betting Opportunities</h3>
                            <p style={{ margin: 0, color: '#666', fontSize: '14px' }}>
                                Live data from ESPN, real team statistics, and current betting odds
                            </p>
                        </div>
                        
                        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                            <DropDownList
                                data={sports}
                                value={sports.find(s => s.value === selectedSport)}
                                onChange={handleSportChange}
                                textField="text"
                                valueField="value"
                                style={{ width: '150px' }}
                            />
                            
                            <Button 
                                onClick={() => setLiveUpdatesEnabled(!liveUpdatesEnabled)}
                                themeColor={liveUpdatesEnabled ? 'success' : 'secondary'}
                                size="small"
                                icon={liveUpdatesEnabled ? 'play' : 'pause'}
                            >
                                {liveUpdatesEnabled ? 'Live' : 'Paused'}
                            </Button>
                            
                            <Button 
                                themeColor="primary" 
                                size="small" 
                                onClick={handleRefresh}
                                icon="refresh"
                                disabled={loading}
                            >
                                {loading ? 'Refreshing...' : 'Refresh'}
                            </Button>
                        </div>
                    </div>
                </CardBody>
            </Card>

            {/* Games Grid */}
            <Grid
                data={data}
                pageable={true}
                sortable={true}
                filterable={true}
                resizable={true}
                height="600px"
                loading={loading}
            >
                <GridColumn title="Matchup" width="250px" cell={MatchupCell} />
                <GridColumn title="Status" width="100px" cell={StatusCell} />
                <GridColumn title="Odds" width="120px" cell={OddsCell} />
                <GridColumn title="AI Prediction" width="120px" cell={PredictionCell} />
                <GridColumn title="Weather" width="100px" cell={WeatherCell} />
                <GridColumn title="Expected ROI" width="110px" cell={ROICell} />
                <GridColumn field="riskLevel" title="Risk" width="80px" />
                <GridColumn title="Actions" width="120px" cell={ActionCell} />
            </Grid>

            {/* Bet Placement Dialog */}
            {showBetDialog && selectedGame && (
                <Dialog 
                    title={`Place Bet - ${selectedGame.awayTeam} @ ${selectedGame.homeTeam}`}
                    onClose={() => setShowBetDialog(false)}
                    width={600}
                >
                    <Form
                        initialValues={{
                            amount: 100,
                            selection: selectedGame.prediction === selectedGame.homeTeam ? 'home' : 'away'
                        }}
                        onSubmit={handleBetSubmit}
                        render={(formRenderProps) => (
                            <FormElement style={{ maxWidth: 550 }}>
                                {/* Game Info Card */}
                                <Card style={{ marginBottom: '16px' }}>
                                    <CardBody>
                                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                                            <div>
                                                <h4>Game Details</h4>
                                                <p><strong>Matchup:</strong> {selectedGame.awayTeam} @ {selectedGame.homeTeam}</p>
                                                <p><strong>Sport:</strong> {selectedGame.sport}</p>
                                                <p><strong>Status:</strong> {selectedGame.status}</p>
                                                <p><strong>Venue:</strong> {selectedGame.venue}</p>
                                            </div>
                                            <div>
                                                <h4>AI Analysis</h4>
                                                <p><strong>Prediction:</strong> {selectedGame.prediction}</p>
                                                <p><strong>Confidence:</strong> {selectedGame.confidence}%</p>
                                                <p><strong>Expected ROI:</strong> 
                                                    <span style={{ color: selectedGame.expectedROI > 0 ? '#28a745' : '#dc3545' }}>
                                                        {selectedGame.expectedROI > 0 ? '+' : ''}{selectedGame.expectedROI}%
                                                    </span>
                                                </p>
                                                <p><strong>Risk Level:</strong> {selectedGame.riskLevel}</p>
                                            </div>
                                        </div>
                                        
                                        {weatherData[selectedGame.id] && (
                                            <div style={{ marginTop: '12px', padding: '8px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
                                                <strong>Weather:</strong> {weatherData[selectedGame.id].temperature}°F, {weatherData[selectedGame.id].conditions}, 
                                                Wind {weatherData[selectedGame.id].windSpeed} mph {weatherData[selectedGame.id].windDirection}
                                            </div>
                                        )}
                                    </CardBody>
                                </Card>

                                {/* Bet Form */}
                                <Field
                                    name="selection"
                                    component={DropDownList}
                                    label="Your Selection"
                                    data={[
                                        { text: `${selectedGame.homeTeam} (${selectedGame.homeOdds})`, value: 'home' },
                                        { text: `${selectedGame.awayTeam} (${selectedGame.awayOdds})`, value: 'away' }
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

                                <div style={{ marginTop: '16px', padding: '12px', backgroundColor: '#fff3cd', borderRadius: '4px', fontSize: '14px' }}>
                                    <p style={{ margin: '0 0 8px 0' }}><strong>⚠️ Betting Responsibly:</strong></p>
                                    <ul style={{ margin: 0, paddingLeft: '20px' }}>
                                        <li>Only bet what you can afford to lose</li>
                                        <li>Set limits and stick to them</li>
                                        <li>Never chase losses</li>
                                        <li>Consider this entertainment, not investment</li>
                                    </ul>
                                </div>

                                <DialogActionsBar>
                                    <Button 
                                        type="submit" 
                                        themeColor="primary"
                                        disabled={placingBet || !formRenderProps.allowSubmit}
                                        loading={placingBet}
                                    >
                                        {placingBet ? 'Placing Bet...' : 'Confirm Bet'}
                                    </Button>
                                    <Button 
                                        onClick={() => setShowBetDialog(false)}
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

            {/* Footer Info */}
            <div style={{ marginTop: '16px', fontSize: '14px', color: '#666' }}>
                <p>
                    🔄 Live data updates every 30 seconds from ESPN and other sports APIs. 
                    Last update: {new Date().toLocaleTimeString()}
                </p>
                <p>
                    📊 Showing {data.length} live {selectedSport.toUpperCase()} games with real team data, weather conditions, and current betting odds.
                </p>
                <p>
                    🎯 AI predictions based on team statistics, recent performance, and multiple data sources.
                </p>
            </div>
        </div>
    );
};

export default RealSportsBettingGrid; 