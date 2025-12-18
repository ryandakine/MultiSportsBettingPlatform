import React from 'react';
import './Hero.css';

const Hero = () => {
  const scrollToApply = () => {
    const element = document.getElementById('apply');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <section className="hero">
      <div className="hero-container">
        <div className="hero-content">
          <div className="hero-badge">
            <span className="badge-icon">🔒</span>
            <span>100 Exclusive Licenses • $10,000 Per Year</span>
          </div>
          
          <h1 className="hero-title">
            17% Hit Rate on 6-Leg Parlays.
            <br />
            <span className="text-gradient">48x Average Return.</span>
            <br />
            100 Members. Closed Network.
          </h1>
          
          <p className="hero-subtitle">
            A private betting intelligence network built on 10 years of data, 40,000+ backtested bets, 
            and a community of 100 serious bettors who can't talk to anyone but each other.
          </p>

          <div className="hero-features">
            <div className="hero-feature">
              <span className="feature-icon">🔒</span>
              <span>Closed Network</span>
            </div>
            <div className="hero-feature">
              <span className="feature-icon">📊</span>
              <span>40,000+ Bets Analyzed</span>
            </div>
            <div className="hero-feature">
              <span className="feature-icon">⏱️</span>
              <span>10 Years Backtested</span>
            </div>
          </div>

          <div className="hero-stats">
            <div className="hero-stat">
              <div className="stat-number">17.1%</div>
              <div className="stat-label">6-Leg Parlay Hit Rate</div>
            </div>
            <div className="hero-stat">
              <div className="stat-number">48x</div>
              <div className="stat-label">Average Return</div>
            </div>
            <div className="hero-stat">
              <div className="stat-number">54.5%</div>
              <div className="stat-label">Straight Bet Win Rate</div>
            </div>
            <div className="hero-stat">
              <div className="stat-number">100</div>
              <div className="stat-label">Members Max</div>
            </div>
          </div>

          <div className="hero-cta">
            <button className="btn btn-primary btn-large" onClick={scrollToApply}>
              Apply for Membership
            </button>
            <a href="#proof" className="btn btn-secondary btn-large">
              See the Proof
            </a>
          </div>

          <p className="hero-note">
            Most 6-leg parlays hit around 1.5-3% of the time. Ours hit 17%.
            <br />
            <strong>That's not luck. That's finding correlations the books don't price correctly.</strong>
          </p>
        </div>
      </div>
    </section>
  );
};

export default Hero;

