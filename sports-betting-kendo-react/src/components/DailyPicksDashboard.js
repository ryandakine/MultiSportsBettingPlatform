
import React, { useState, useEffect } from 'react';
import { Card, CardBody, CardTitle } from '@progress/kendo-react-layout';
import { Button } from '@progress/kendo-react-buttons';
import { DropDownList } from '@progress/kendo-react-dropdowns';
import realSportsApiService from '../services/RealSportsApiService';

// Inline Badge Component (Workaround for Kendo version conflicts)
const Badge = ({ themeColor, children, style }) => (
    <span style={{
        padding: '4px 8px',
        borderRadius: '4px',
        fontSize: '12px',
        fontWeight: 'bold',
        backgroundColor: themeColor === 'success' ? '#28a745' :
            themeColor === 'warning' ? '#ffc107' :
                themeColor === 'error' ? '#dc3545' : '#17a2b8',
        color: themeColor === 'warning' ? '#000' : '#fff',
        ...style
    }}>
        {children}
    </span>
);

const DailyPicksDashboard = () => {
    const [selectedSport, setSelectedSport] = useState('nfl');
    const [games, setGames] = useState([]);
    const [loading, setLoading] = useState(false);

    const sports = [
        { text: 'NFL Football', value: 'nfl', icon: '🏈' },
        { text: 'NCAAB Men\'s', value: 'ncaab', icon: '🏀' },
        { text: 'NCAAB Women\'s', value: 'ncaaw', icon: '🏀' },
        { text: 'WNBA Basketball', value: 'wnba', icon: '🏀' },
        { text: 'MLB Baseball', value: 'mlb', icon: '⚾' },
        { text: 'NHL Hockey', value: 'nhl', icon: '🏒' }
    ];

    useEffect(() => {
        fetchDailyGames();
    }, [selectedSport]);

    const fetchDailyGames = async () => {
        setLoading(true);
        try {
            const response = await realSportsApiService.getLiveGames(selectedSport);
            if (response.success) {
                // Sort games: Live first, then by time
                const sortedGames = response.data.sort((a, b) => {
                    if (a.status === 'Live' && b.status !== 'Live') return -1;
                    if (a.status !== 'Live' && b.status === 'Live') return 1;
                    return new Date(a.gameTime) - new Date(b.gameTime);
                });
                setGames(sortedGames);
            }
        } catch (error) {
            console.error("Error fetching games:", error);
        } finally {
            setLoading(false);
        }
    };

    const getConfidenceColor = (confidence) => {
        if (confidence >= 80) return 'success';
        if (confidence >= 60) return 'warning';
        return 'error';
    };

    const generateReasoning = (game) => {
        // Generate dynamic "Why?" reasoning based on game data
        const sentiment = game.confidence > 75 ? "Strongly favors" : "Slight edge to";
        const team = game.prediction;
        const opponent = team === game.homeTeam ? game.awayTeam : game.homeTeam;

        return `${sentiment} ${team} to cover against ${opponent}. ` +
            `Models indicate ${game.confidence}% probability based on recent matchups and ` +
            `${game.weather ? 'current weather conditions' : 'team efficiency metrics'}.`;
    };

    return (
        <div className="daily-picks-dashboard">
            <Card style={{ marginBottom: '20px' }}>
                <CardBody>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
                        <div>
                            <h2 style={{ margin: '0 0 8px 0' }}>📅 Daily AI Picks</h2>
                            <p style={{ margin: 0, color: '#666' }}>Full daily schedule with AI predictions and analysis</p>
                        </div>
                        <div style={{ display: 'flex', gap: '12px' }}>
                            {sports.map(sport => (
                                <Button
                                    key={sport.value}
                                    themeColor={selectedSport === sport.value ? 'primary' : 'base'}
                                    onClick={() => setSelectedSport(sport.value)}
                                >
                                    {sport.icon} {sport.text}
                                </Button>
                            ))}
                        </div>
                    </div>
                </CardBody>
            </Card>

            {loading ? (
                <div style={{ textAlign: 'center', padding: '40px' }}>
                    <div className="k-loading-mask" style={{ position: 'relative', height: '40px', width: '40px', margin: '0 auto' }}></div>
                    <p>Analyzing today's matchups...</p>
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '20px' }}>
                    {games.map(game => (
                        <Card key={game.id} style={{ borderLeft: `4px solid ${game.confidence >= 80 ? '#28a745' : '#ffc107'}` }}>
                            <CardBody>
                                {/* Header: Matchup & Time */}
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px', fontSize: '12px', color: '#666' }}>
                                    <span>{new Date(game.gameTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                    <span>{game.venue}</span>
                                </div>

                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                                    <div style={{ width: '45%' }}>
                                        <div style={{ fontWeight: 'bold', fontSize: '16px' }}>{game.awayTeam}</div>
                                        <div style={{ fontSize: '12px', color: '#999' }}>Away</div>
                                    </div>
                                    <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#666' }}>@</div>
                                    <div style={{ width: '45%', textAlign: 'right' }}>
                                        <div style={{ fontWeight: 'bold', fontSize: '16px' }}>{game.homeTeam}</div>
                                        <div style={{ fontSize: '12px', color: '#999' }}>Home</div>
                                    </div>
                                </div>

                                {/* AI Pick Section */}
                                <div style={{ backgroundColor: '#f8f9fa', padding: '16px', borderRadius: '8px', marginBottom: '16px' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                                        <span style={{ fontWeight: 'bold', color: '#007bff' }}>🤖 AI Pick</span>
                                        <Badge themeColor={getConfidenceColor(game.confidence)}>
                                            {game.confidence}% Confidence
                                        </Badge>
                                    </div>
                                    <div style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '4px' }}>
                                        {game.prediction}
                                    </div>
                                    <div style={{ fontSize: '12px', color: '#666' }}>
                                        Target Odds: {game.prediction === game.homeTeam ? game.homeOdds : game.awayOdds}
                                    </div>
                                </div>

                                {/* Analysis "Why?" Section */}
                                <div style={{ fontSize: '14px', lineHeight: '1.4' }}>
                                    <strong style={{ display: 'block', marginBottom: '4px', color: '#555' }}>💡 Why?</strong>
                                    <p style={{ margin: 0, color: '#666' }}>
                                        {generateReasoning(game)}
                                    </p>
                                </div>
                            </CardBody>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
};

export default DailyPicksDashboard;
