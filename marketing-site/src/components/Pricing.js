import React from 'react';
import './Pricing.css';

const Pricing = () => {
  const scrollToApply = () => {
    const element = document.getElementById('apply');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <section id="pricing" className="pricing-section">
      <div className="container">
        <h2 className="section-title">Why $10,000</h2>
        <p className="section-subtitle">
          This isn't for everyone. That's the point.
        </p>

        <div className="pricing-card">
          <div className="pricing-header">
            <div className="pricing-badge">Exclusive License</div>
            <div className="pricing-amount">
              <span className="amount">$10,000</span>
              <span className="period">Per Year</span>
            </div>
          </div>

          <div className="pricing-features">
            <h3>What's Included:</h3>
            <ul>
              <li>✓ Complete platform access (annual subscription)</li>
              <li>✓ Daily picks for all games</li>
              <li>✓ Best pick of day per sport</li>
              <li>✓ 6-leg parlay system</li>
              <li>✓ Portfolio management</li>
              <li>✓ Advanced analytics</li>
              <li>✓ Real-time updates</li>
              <li>✓ Secure .onion domain access</li>
              <li>✓ Email support</li>
              <li>✓ Full backtest data</li>
              <li>✓ <strong>New features and improvements added each year</strong></li>
            </ul>
            <div style={{marginTop: '1.5rem', padding: '1.5rem', backgroundColor: 'rgba(26, 31, 58, 0.8)', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.1)'}}>
              <p style={{margin: 0, fontWeight: '500', lineHeight: '1.6', color: 'rgba(255, 255, 255, 0.9)'}}>
                <strong>$10,000 filters for:</strong>
              </p>
              <ul style={{marginTop: '12px', paddingLeft: '24px', color: 'rgba(255, 255, 255, 0.9)', lineHeight: '1.8'}}>
                <li>Bettors with real bankrolls</li>
                <li>People who won't share and kill the edge</li>
                <li>Members who add value to the community</li>
                <li>Commitment that keeps the network tight</li>
              </ul>
            </div>
          </div>

          <div className="pricing-note">
            <strong>Payment:</strong> Cryptocurrency only. No PayPal. No credit cards. No payment plans. 
            If you're betting serious money on sports, you already know how to move crypto.
          </div>

          <div className="pricing-cta">
            <button className="btn btn-primary btn-large" onClick={scrollToApply}>
              Apply for Membership
            </button>
          </div>

          <div className="pricing-value" style={{marginTop: '32px'}}>
            <h3 style={{fontSize: '24px', marginBottom: '24px', color: 'white'}}>What $10,000 Gets You</h3>
            <p style={{color: 'rgba(255, 255, 255, 0.9)', lineHeight: '1.8', marginBottom: '16px'}}>
              At 17% hit rate on 6-leg parlays with 48x average return:
            </p>
            <ul style={{color: 'rgba(255, 255, 255, 0.9)', lineHeight: '1.8', marginBottom: '24px', paddingLeft: '24px'}}>
              <li>1 parlay/week = 52 parlays/year</li>
              <li>17% of 52 = ~9 winners</li>
              <li>9 × 48x = 432x return on those hits alone</li>
            </ul>
            <p style={{color: 'rgba(255, 255, 255, 0.9)', lineHeight: '1.8', marginBottom: '8px'}}>
              If you're betting $100 per parlay, that's $43,200 in parlay returns.
            </p>
            <p style={{color: 'rgba(255, 255, 255, 0.9)', lineHeight: '1.8', marginBottom: '16px'}}>
              If you're betting $500 per parlay, that's $216,000.
            </p>
            <p style={{color: 'white', fontWeight: '600', fontSize: '18px', marginTop: '24px'}}>
              The $10,000 membership pays for itself on the FIRST 6-leg hit if you're betting with real money.
            </p>
            <p style={{color: 'rgba(255, 255, 255, 0.9)', lineHeight: '1.8', marginTop: '16px'}}>
              This doesn't count the straight bets running at 54.5%.
            </p>
          </div>

          <div className="pricing-limit" style={{marginTop: '48px'}}>
            <div className="limit-badge">🔒 Only 100 Spots</div>
            <p>
              Not 101. Not "we'll make room." When it's full, it's full. The only way in after that is if someone leaves.
            </p>
            <p style={{marginTop: '16px', fontWeight: '500'}}>
              Why?
            </p>
            <ul style={{marginTop: '8px', paddingLeft: '24px'}}>
              <li>More members = more money on the same lines = edges disappear</li>
              <li>More members = harder to maintain community quality</li>
              <li>More members = someone eventually leaks</li>
            </ul>
            <p style={{marginTop: '16px', fontWeight: '600'}}>
              100 is the number that lets us win without killing the edge.
            </p>
          </div>
        </div>

      </div>
    </section>
  );
};

export default Pricing;

