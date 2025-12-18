import React from 'react';
import './PlatformPreview.css';

const PlatformPreview = () => {
  return (
    <section id="preview" className="preview-section">
      <div className="container">
        <h2 className="section-title">Platform Preview</h2>
        <p className="section-subtitle">
          Here's what you'll get access to. The actual platform is hosted on a secure .onion domain 
          for maximum privacy and security.
        </p>

        <div className="preview-showcase">
          <div className="preview-card">
            <div className="preview-header">
              <div className="preview-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <div className="preview-title">Daily Picks Dashboard</div>
            </div>
            <div className="preview-content">
              <div className="preview-game">
                <div className="game-header">
                  <span className="sport-badge">⚾ MLB</span>
                  <span className="confidence-badge">92% Confidence</span>
                </div>
                <div className="game-matchup">
                  <span className="team">Yankees</span>
                  <span className="vs">@</span>
                  <span className="team">Red Sox</span>
                </div>
                <div className="game-pick">
                  <strong>AI Pick:</strong> Yankees ML
                  <div className="pick-reasoning">
                    Strong pitching matchup favors Yankees. Recent form and head-to-head 
                    statistics indicate 92% confidence in this pick.
                  </div>
                </div>
              </div>
              
              <div className="preview-game">
                <div className="game-header">
                  <span className="sport-badge">🏀 NBA</span>
                  <span className="confidence-badge">88% Confidence</span>
                </div>
                <div className="game-matchup">
                  <span className="team">Lakers</span>
                  <span className="vs">@</span>
                  <span className="team">Warriors</span>
                </div>
                <div className="game-pick">
                  <strong>AI Pick:</strong> Over 225.5
                  <div className="pick-reasoning">
                    Both teams averaging 115+ points recently. Fast-paced game expected. 
                    Historical matchups support over.
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="preview-card">
            <div className="preview-header">
              <div className="preview-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <div className="preview-title">6-Leg Parlay Builder</div>
            </div>
            <div className="preview-content">
              <div className="parlay-preview">
                <div className="parlay-legs">
                  <div className="parlay-leg">⚾ Yankees ML</div>
                  <div className="parlay-leg">🏀 Lakers Over 225.5</div>
                  <div className="parlay-leg">🏈 Chiefs -3.5</div>
                  <div className="parlay-leg">🏒 Lightning ML</div>
                  <div className="parlay-leg">⚾ Dodgers -1.5</div>
                  <div className="parlay-leg">🏀 Celtics Over 220</div>
                </div>
                <div className="parlay-stats">
                  <div className="parlay-stat">
                    <span>Combined Odds:</span>
                    <strong>+4840</strong>
                  </div>
                  <div className="parlay-stat">
                    <span>Expected Win Rate:</span>
                    <strong>17.33%</strong>
                  </div>
                  <div className="parlay-stat">
                    <span>Expected ROI:</span>
                    <strong>790%</strong>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="preview-card">
            <div className="preview-header">
              <div className="preview-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <div className="preview-title">Portfolio Analytics</div>
            </div>
            <div className="preview-content">
              <div className="analytics-preview">
                <div className="analytics-stat">
                  <div className="stat-label">Total ROI</div>
                  <div className="stat-value">+247.3%</div>
                </div>
                <div className="analytics-stat">
                  <div className="stat-label">Win Rate</div>
                  <div className="stat-value">18.2%</div>
                </div>
                <div className="analytics-stat">
                  <div className="stat-label">Total Profit</div>
                  <div className="stat-value">$24,730</div>
                </div>
                <div className="analytics-stat">
                  <div className="stat-label">Best Sport</div>
                  <div className="stat-value">Baseball (23.1%)</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="preview-note">
          <p>
            <strong>Full platform access</strong> includes all features: daily picks, best picks of day, 
            6-leg parlay builder, portfolio management, advanced analytics, and real-time updates. 
            Access provided via secure .onion domain after license activation.
          </p>
        </div>
      </div>
    </section>
  );
};

export default PlatformPreview;


