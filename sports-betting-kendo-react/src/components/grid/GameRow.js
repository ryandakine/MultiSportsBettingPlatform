import React from 'react';
import { Button } from '@progress/kendo-react-buttons';
import { Badge } from '@progress/kendo-react-indicators';

const GameRow = ({ game, onBetClick, onStatsClick }) => {
    const getScoreColor = (score, opponentScore) => {
        if (!score || !opponentScore) return 'inherit';
        return parseInt(score) > parseInt(opponentScore) ? '#28a745' : '#dc3545';
    };

    const getStatusBadge = (status) => {
        switch (status) {
            case 'LIVE': return <Badge themeColor="error">LIVE</Badge>;
            case 'FINISHED': return <Badge themeColor="secondary">FINAL</Badge>;
            case 'SCHEDULED': return <Badge themeColor="info">UPCOMING</Badge>;
            default: return <Badge themeColor="light">{status}</Badge>;
        }
    };

    return (
        <div className="game-row" style={{
            display: 'grid',
            gridTemplateColumns: '80px 2fr 1fr 1fr 120px',
            gap: '15px',
            padding: '15px',
            borderBottom: '1px solid #eee',
            alignItems: 'center',
            backgroundColor: '#fff',
            transition: 'background-color 0.2s'
        }}>
            {/* Time/Status */}
            <div style={{ textAlign: 'center' }}>
                <div style={{ fontWeight: 'bold', fontSize: '12px', marginBottom: '4px' }}>
                    {new Date(game.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
                {getStatusBadge(game.status)}
            </div>

            {/* Teams */}
            <div className="teams-info">
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span style={{ fontWeight: 'bold' }}>{game.home_team}</span>
                    <span style={{ color: getScoreColor(game.home_score, game.away_score), fontWeight: 'bold' }}>
                        {game.home_score}
                    </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>{game.away_team}</span>
                    <span style={{ color: getScoreColor(game.away_score, game.home_score), fontWeight: 'bold' }}>
                        {game.away_score}
                    </span>
                </div>
            </div>

            {/* Moneyline */}
            <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>Moneyline</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    <Button size="small" fillMode="flat" themeColor="primary" onClick={() => onBetClick(game, 'moneyline', game.home_team)}>
                        {game.odds?.home_ml || '-'}
                    </Button>
                    <Button size="small" fillMode="flat" themeColor="primary" onClick={() => onBetClick(game, 'moneyline', game.away_team)}>
                        {game.odds?.away_ml || '-'}
                    </Button>
                </div>
            </div>

            {/* Spread */}
            <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>Spread</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    <Button size="small" fillMode="flat" onClick={() => onBetClick(game, 'spread', game.home_team)}>
                        {game.odds?.home_spread || '-'}
                    </Button>
                    <Button size="small" fillMode="flat" onClick={() => onBetClick(game, 'spread', game.away_team)}>
                        {game.odds?.away_spread || '-'}
                    </Button>
                </div>
            </div>

            {/* Actions */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <Button icon="chart-line-markers" themeColor="base" onClick={() => onStatsClick(game)}>
                    Stats
                </Button>
            </div>
        </div>
    );
};

export default GameRow;
