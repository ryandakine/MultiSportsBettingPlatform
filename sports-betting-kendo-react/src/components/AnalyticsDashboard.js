
import React from 'react';
import { TileLayout } from '@progress/kendo-react-layout';
import { Card, CardHeader, CardBody } from '@progress/kendo-react-layout';

// Simple placeholder components for missing charts
const WinRateDonut = () => (
    <div style={{ height: '150px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{
            width: '100px', height: '100px', borderRadius: '50%',
            background: 'conic-gradient(#28a745 0% 65%, #dc3545 65% 100%)',
            display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}>
            <div style={{ width: '60px', height: '60px', borderRadius: '50%', backgroundColor: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>
                65%
            </div>
        </div>
    </div>
);

const SportPerformanceBar = () => (
    <div style={{ padding: '10px' }}>
        {['NBA', 'NFL', 'MLB', 'NHL'].map(sport => (
            <div key={sport} style={{ marginBottom: '10px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span>{sport}</span>
                    <span>{Math.floor(Math.random() * 30 + 50)}%</span>
                </div>
                <div style={{ height: '20px', backgroundColor: '#eee', borderRadius: '4px' }}>
                    <div style={{
                        height: '100%',
                        width: `${Math.floor(Math.random() * 30 + 50)}%`,
                        backgroundColor: '#28a745',
                        borderRadius: '4px'
                    }}></div>
                </div>
            </div>
        ))}
    </div>
);

const AnalyticsDashboard = () => {
    const tiles = [
        { id: 'winRate', col: 1, row: 1, colSpan: 2, rowSpan: 2 },
        { id: 'sportPerformance', col: 3, row: 1, colSpan: 4, rowSpan: 2 },
        { id: 'recentActivity', col: 1, row: 3, colSpan: 6, rowSpan: 2 }
    ];

    return (
        <div className="analytics-dashboard">
            <h2>Sports Analytics Dashboard</h2>
            <TileLayout
                columns={6}
                rowHeight={200}
                gap={{ col: 16, row: 16 }}
                tiles={tiles}
            >
                <div className="tile-content">
                    <Card>
                        <CardHeader>
                            <h3>Win Rate Distribution</h3>
                        </CardHeader>
                        <CardBody>
                            <WinRateDonut />
                        </CardBody>
                    </Card>
                </div>
                <div className="tile-content">
                    <Card>
                        <CardHeader>
                            <h3>Performance by Sport</h3>
                        </CardHeader>
                        <CardBody>
                            <SportPerformanceBar />
                        </CardBody>
                    </Card>
                </div>
                <div className="tile-content">
                    <Card>
                        <CardHeader>
                            <h3>Recent Activity</h3>
                        </CardHeader>
                        <CardBody>
                            <p>Recent betting activity and system events will be displayed here.</p>
                        </CardBody>
                    </Card>
                </div>
            </TileLayout>
        </div>
    );
};

export default AnalyticsDashboard;
