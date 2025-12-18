import React from 'react';
import './HowItWorks.css';

const HowItWorks = () => {
  return (
    <section id="how-it-works" className="how-it-works-section">
      <div className="container">
        <h2 className="section-title">How It Works</h2>
        
        <div className="how-it-works-grid">
          <div className="tier-card">
            <div className="tier-badge">Free (Public)</div>
            <h3>Follow us on Twitter/X</h3>
            <p>We post daily:</p>
            <ul>
              <li>1 straight bet per active sport</li>
              <li>1 three-leg parlay</li>
              <li>6-leg parlay RESULT ONLY (██████ 🔒)</li>
            </ul>
            <p style={{marginTop: '24px', fontWeight: '500'}}>
              Watch us hit. Track our record. See what you're missing.
            </p>
          </div>

          <div className="tier-card featured">
            <div className="tier-badge featured-badge">Members ($10,000/year)</div>
            <h3>The Picks:</h3>
            <ul>
              <li>Full 6-leg parlay picks before lock</li>
              <li>All straight bets across 5 sports</li>
              <li>The WHY behind each pick (referee, weather, injury, correlation insights)</li>
            </ul>
            
            <h3 style={{marginTop: '32px', marginBottom: '16px'}}>The Access:</h3>
            <ul>
              <li>Secure, private delivery system</li>
              <li>Not on the clearnet - protected infrastructure</li>
              <li>Direct communication channel</li>
            </ul>

            <h3 style={{marginTop: '32px', marginBottom: '16px'}}>The Network:</h3>
            <ul>
              <li>100 members max, permanently</li>
              <li>Private community of verified serious bettors</li>
              <li>NDA-protected discussions</li>
              <li>The only place you can talk about this</li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;

