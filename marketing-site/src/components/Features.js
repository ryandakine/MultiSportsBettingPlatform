import React from 'react';
import './Features.css';

const Features = () => {
  const sports = [
    {
      icon: '🏈',
      title: 'NFL & College Football',
      description: 'Sept → Feb'
    },
    {
      icon: '🏒',
      title: 'NHL',
      description: 'Oct → June'
    },
    {
      icon: '⚾',
      title: 'MLB',
      description: 'March → Oct'
    },
    {
      icon: '🏀',
      title: 'Men\'s College Basketball',
      description: 'Nov → April'
    },
    {
      icon: '🏀',
      title: 'Women\'s College Basketball',
      description: 'Nov → April'
    },
    {
      icon: '🏀',
      title: 'WNBA',
      description: 'May → Sept'
    }
  ];

  const edgeFactors = [
    {
      icon: '🧠',
      title: '20 Years of Human Expertise',
      description: 'Encoded into the models'
    },
    {
      icon: '👨‍⚖️',
      title: '17 NFL Referee Crews',
      description: 'Tracked with historical tendency data'
    },
    {
      icon: '🌦️',
      title: 'Weather Impact Modeling',
      description: 'On scoring and totals'
    },
    {
      icon: '🏥',
      title: 'Injury Correlation Analysis',
      description: 'Across positions'
    },
    {
      icon: '🔍',
      title: 'Cross-Sport Pattern Recognition',
      description: 'The human eye can\'t see'
    },
    {
      icon: '⚙️',
      title: 'Proprietary Correlation Algorithms',
      description: 'For parlay construction'
    },
    {
      icon: '🤖',
      title: 'Machine Learning Models',
      description: 'That improve with every game'
    }
  ];

  return (
    <section id="features" className="features-section">
      <div className="container">
        <h2 className="section-title">What We Track</h2>
        <p className="section-subtitle">
          We're not guessing. We're running systems.
        </p>

        <div style={{marginBottom: '64px'}}>
          <h3 style={{textAlign: 'center', fontSize: '24px', marginBottom: '32px', color: 'white'}}>
            6 Sports. Year-Round Action.
          </h3>
          <div className="features-grid">
            {sports.map((sport, index) => (
              <div key={index} className="feature-card">
                <div className="feature-icon">{sport.icon}</div>
                <h3>{sport.title}</h3>
                <p>{sport.description}</p>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h3 style={{textAlign: 'center', fontSize: '24px', marginBottom: '32px', color: 'white'}}>
            What Powers the Edge:
          </h3>
          <div className="features-grid">
            {edgeFactors.map((factor, index) => (
              <div key={index} className="feature-card">
                <div className="feature-icon">{factor.icon}</div>
                <h3>{factor.title}</h3>
                <p>{factor.description}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="features-note" style={{marginTop: '48px'}}>
          <p>
            The AI processes thousands of data points per game that no human could analyze manually. 
            It finds the correlations between legs that books don't price correctly.
          </p>
          <p style={{marginTop: '16px', fontWeight: '600'}}>
            That's how you get 17% on 6-leg parlays when the industry hits 2-3%.
          </p>
          <p style={{marginTop: '16px', fontStyle: 'italic'}}>
            No NBA. Too scripted. College players actually try.
          </p>
        </div>

        <div style={{marginTop: '48px', padding: '32px', backgroundColor: 'rgba(26, 31, 58, 0.8)', borderRadius: '16px', border: '1px solid rgba(255, 255, 255, 0.1)'}}>
          <h3 style={{fontSize: '20px', marginBottom: '16px', color: 'white'}}>Coming Soon:</h3>
          <p style={{color: 'rgba(255, 255, 255, 0.9)', lineHeight: '1.8', marginBottom: '16px'}}>
            We're continuously expanding coverage to increase parlay correlation opportunities:
          </p>
          <ul style={{color: 'rgba(255, 255, 255, 0.9)', lineHeight: '1.8', paddingLeft: '24px'}}>
            <li>Soccer (MLS, Premier League)</li>
            <li>Golf majors</li>
            <li>Tennis Grand Slams</li>
            <li>Other college sports</li>
          </ul>
          <p style={{color: 'rgba(255, 255, 255, 0.9)', lineHeight: '1.8', marginTop: '16px'}}>
            More sports = more cross-sport correlations = more 6-leg opportunities the books can't price correctly.
          </p>
          <p style={{color: 'white', fontWeight: '600', marginTop: '16px'}}>
            Your membership doesn't just get you what we have now. It gets you everything we build.
          </p>
        </div>
      </div>
    </section>
  );
};

export default Features;

