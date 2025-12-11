import React from 'react';
import { Card, CardBody } from '@progress/kendo-react-layout';

const StatsCard = ({ game, weatherData }) => {
    if (!game) return null;

    const weather = weatherData ? weatherData[game.id] : null;

    return (
        <Card style={{ marginBottom: '16px' }}>
            <CardBody>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                    <div>
                        <h4>Game Details</h4>
                        <p><strong>Matchup:</strong> {game.awayTeam} @ {game.homeTeam}</p>
                        <p><strong>Sport:</strong> {game.sport}</p>
                        <p><strong>Status:</strong> {game.status}</p>
                        <p><strong>Venue:</strong> {game.venue}</p>
                    </div>
                    <div>
                        <h4>AI Analysis</h4>
                        <p><strong>Prediction:</strong> {game.prediction}</p>
                        <p><strong>Confidence:</strong> {game.confidence}%</p>
                        <p><strong>Expected ROI:</strong>
                            <span style={{ color: game.expectedROI > 0 ? '#28a745' : '#dc3545' }}>
                                {game.expectedROI > 0 ? '+' : ''}{game.expectedROI}%
                            </span>
                        </p>
                        <p><strong>Risk Level:</strong> {game.riskLevel}</p>
                    </div>
                </div>

                {weather && (
                    <div style={{ marginTop: '12px', padding: '8px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
                        <strong>Weather:</strong> {weather.temperature}°F, {weather.conditions},
                        Wind {weather.windSpeed} mph {weather.windDirection}
                    </div>
                )}
            </CardBody>
        </Card>
    );
};

export default StatsCard;
