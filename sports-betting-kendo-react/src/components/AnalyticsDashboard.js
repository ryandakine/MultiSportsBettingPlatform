
import React from 'react';
import { TileLayout } from '@progress/kendo-react-layout';
import { Card, CardHeader, CardBody } from '@progress/kendo-react-layout';
import winratedonut from './winratedonut'
import sportperformancebar from './sportperformancebar'

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
                            <winratedonut />
                        </CardBody>
                    </Card>
                </div>
                <div className="tile-content">
                    <Card>
                        <CardHeader>
                            <h3>Performance by Sport</h3>
                        </CardHeader>
                        <CardBody>
                            <sportperformancebar />
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
