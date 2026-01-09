import React from 'react';
import './PrivacySecurity.css';

const PrivacySecurity = () => {
  return (
    <section id="privacy" className="privacy-section">
      <div className="container">
        <h2 className="section-title">Privacy-First Platform</h2>
        <p className="section-subtitle">
          We take privacy seriously because betting is privacy-sensitive. That's why we use 
          enterprise-grade security throughout the platform.
        </p>

        <div className="privacy-grid">
          <div className="privacy-card">
            <div className="privacy-icon">🔒</div>
            <h3>.onion Domain Hosting</h3>
            <ul>
              <li>Platform hosted on secure .onion domain</li>
              <li>Maximum privacy and security</li>
              <li>Protected from DDoS attacks</li>
              <li>Server location and IP hidden</li>
              <li>Exclusive access for license holders</li>
            </ul>
            <p className="privacy-note">
              .onion address shared only after license activation. Access requires Tor browser 
              (free download, setup guide included).
            </p>
          </div>

          <div className="privacy-card">
            <div className="privacy-icon">💰</div>
            <h3>Monero Payments</h3>
            <ul>
              <li>True financial privacy</li>
              <li>No public transaction ledger</li>
              <li>Protects both buyer and seller</li>
              <li>No credit card fraud risk</li>
              <li>Professional-grade privacy protection</li>
            </ul>
            <p className="privacy-note">
              We accept only Monero (XMR) for payments. This aligns with our privacy-first 
              approach and protects professional bettors who value discretion.
            </p>
          </div>

          <div className="privacy-card">
            <div className="privacy-icon">🛡️</div>
            <h3>Complete Protection</h3>
            <ul>
              <li>NDA required (non-disclosure agreement)</li>
              <li>License holder identity protected</li>
              <li>Betting activity completely private</li>
              <li>No data sharing with third parties</li>
              <li>Enterprise-grade encryption</li>
            </ul>
            <p className="privacy-note">
              Your betting activity is completely private. We protect your identity, your 
              payments, and your data.
            </p>
          </div>
        </div>

        <div className="privacy-philosophy">
          <h3>Our Privacy Philosophy</h3>
          <p>
            Betting is privacy-sensitive. Whether you're a professional bettor, serious hobbyist, 
            or someone who values discretion, your betting activity should be private. That's why 
            we've built privacy protection into every layer of the platform:
          </p>
          <div className="philosophy-points">
            <div className="philosophy-point">
              <span className="point-icon">✓</span>
              <span>Privacy-first hosting (.onion domain)</span>
            </div>
            <div className="philosophy-point">
              <span className="point-icon">✓</span>
              <span>Privacy-first payments (Monero only)</span>
            </div>
            <div className="philosophy-point">
              <span className="point-icon">✓</span>
              <span>Privacy-first access (exclusive license holders)</span>
            </div>
            <div className="philosophy-point">
              <span className="point-icon">✓</span>
              <span>Privacy-first data (no sharing, no tracking)</span>
            </div>
          </div>
          <p className="philosophy-conclusion">
            This isn't about being "sketchy" - it's about professional-grade privacy protection 
            for serious bettors who value discretion. If privacy matters to you, you'll appreciate 
            this approach.
          </p>
        </div>
      </div>
    </section>
  );
};

export default PrivacySecurity;




