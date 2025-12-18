import React from 'react';
import './Footer.css';

const Footer = () => {
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-content">
          <div className="footer-section">
            <h3>MultiSports AI</h3>
            <p>
              20 years of betting + cutting-edge AI. 17% hit rate on 6-leg parlays. 
              100 members. Closed network.
            </p>
          </div>

          <div className="footer-section">
            <h4>Platform</h4>
            <ul>
              <li><a href="#story">The System</a></li>
              <li><a href="#network">The Network</a></li>
              <li><a href="#features">What We Track</a></li>
              <li><a href="#proof">The Numbers</a></li>
              <li><a href="#how-it-works">How It Works</a></li>
            </ul>
          </div>

          <div className="footer-section">
            <h4>Membership</h4>
            <ul>
              <li><a href="#pricing">Why $10K</a></li>
              <li><a href="#apply">Apply for Membership</a></li>
              <li>NDA Required</li>
              <li>100 Members Max</li>
            </ul>
          </div>

          <div className="footer-section">
            <h4>Contact</h4>
            <p>Applications reviewed individually</p>
            <p>Not everyone is accepted</p>
          </div>
        </div>

        <div className="footer-bottom">
          <div className="footer-disclaimer">
            <p>
              <strong>Legal Disclaimer:</strong> Past performance does not guarantee future results. 
              Backtest results (17.1% 6-leg parlay hit rate, 54.5% straight bet win rate) are based on 
              10 years of historical data across 40,000+ bets and may not be indicative of future performance. 
              Individual results will vary. This platform is for educational and informational purposes only. 
              You are responsible for your own betting decisions and compliance with all applicable laws. 
              Betting involves substantial risk, and you may lose money. $10,000 membership is non-refundable. 
              Annual commitment required.
            </p>
          </div>

          <div className="footer-copyright">
            <p>© 2024 MultiSports AI Betting Platform. All rights reserved. Closed Network. NDA Protected.</p>
            <button className="back-to-top" onClick={scrollToTop}>
              Back to Top ↑
            </button>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;


