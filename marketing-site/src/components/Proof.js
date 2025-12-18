import React from 'react';
import './Proof.css';

const Proof = () => {
  const stats = [
    { number: '17.1%', label: '6-Leg Parlay Hit Rate', description: 'Industry standard is 2-3%' },
    { number: '48x', label: 'Average Parlay Return', description: 'Multiplier per winning parlay' },
    { number: '54.5%', label: 'Straight Bet Win Rate', description: 'Win rate on individual picks' },
    { number: '10', label: 'Years Backtested', description: '10 years of historical data' },
    { number: '40,000+', label: 'Total Bets Analyzed', description: 'Bets analyzed in backtest' },
    { number: '1,700+', label: 'Parlays Tracked', description: 'Parlays generated and tracked' }
  ];

  const legComparison = [
    { legs: 2, winRate: '56.83%', roi: '107.1%', payout: '3.6x', zone: 'Safe Zone' },
    { legs: 3, winRate: '42.27%', roi: '194.1%', payout: '6.9x', zone: 'Safe Zone' },
    { legs: 4, winRate: '31.15%', roi: '313.7%', payout: '13.3x', zone: 'Balanced' },
    { legs: 5, winRate: '22.86%', roi: '479.5%', payout: '25.4x', zone: 'High ROI' },
    { legs: 6, winRate: '17.33%', roi: '738.5%', payout: '48.4x', zone: 'High ROI', highlight: true }
  ];

  return (
    <section id="proof" className="proof-section">
      <div className="container">
        <h2 className="section-title">The Numbers</h2>
        <p className="section-subtitle">
          Exposed Results
        </p>

        <div className="proof-stats">
          {stats.map((stat, index) => (
            <div key={index} className="proof-stat">
              <div className="stat-number">{stat.number}</div>
              <div className="stat-label">{stat.label}</div>
              <div className="stat-description">{stat.description}</div>
            </div>
          ))}
        </div>

        <div className="proof-conclusion" style={{marginTop: '60px', marginBottom: '60px'}}>
          <h3>What 17% Means</h3>
          <p>
            Most 6-leg parlays hit around 1.5-3% of the time. <strong>Ours hit 17%.</strong>
          </p>
          <p>
            That's not luck. That's finding correlations the books don't price correctly.
          </p>
          <p>
            One 6-leg parlay per week at 17% with 48x return = math you can do yourself.
          </p>
        </div>

        <div className="proof-breakdown">
          <h3>Performance by Leg Count</h3>
          <p className="breakdown-subtitle">
            The platform tested different parlay sizes. Here's how each performed:
          </p>
          
          <div className="leg-comparison">
            {legComparison.map((leg, index) => (
              <div 
                key={index} 
                className={`leg-card ${leg.highlight ? 'highlight' : ''}`}
              >
                {leg.highlight && <div className="highlight-badge">⭐ Best ROI</div>}
                <div className="leg-number">{leg.legs}-Leg Parlay</div>
                <div className="leg-zone">{leg.zone}</div>
                <div className="leg-stats">
                  <div className="leg-stat">
                    <span className="stat-name">Win Rate:</span>
                    <span className="stat-value">{leg.winRate}</span>
                  </div>
                  <div className="leg-stat">
                    <span className="stat-name">ROI:</span>
                    <span className="stat-value">{leg.roi}</span>
                  </div>
                  <div className="leg-stat">
                    <span className="stat-name">Payout:</span>
                    <span className="stat-value">{leg.payout}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </section>
  );
};

export default Proof;

