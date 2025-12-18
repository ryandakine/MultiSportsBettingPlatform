import React from 'react';
import './Story.css';

const Story = () => {
  return (
    <section id="story" className="story-section">
      <div className="container">
        <div className="story-content">
          <h2 className="section-title">20 Years in the Making</h2>
          
          <div className="story-insight">
            <div className="insight-content">
              <p>
                I've been two things my entire adult life: <strong>a sports bettor and a developer</strong>.
              </p>
              <p>
                For 20 years, I've been grinding both - studying line movement, tracking referee tendencies, building systems, writing code. I've always believed there were edges in sports betting that could be found with the right data and the right analysis. But the processing power and AI capabilities weren't there yet.
              </p>
              <p>
                I've been obsessed with AI and machine learning since before it was cool. Watching it evolve. Waiting for it to catch up to what I knew was possible.
              </p>
              <p>
                When the recent AI advancements hit, I realized: <strong>I can finally build the system I've had in my head for two decades.</strong>
              </p>
              <p>
                So I took everything - 20 years of betting patterns, edge identification, correlation spotting, and domain expertise - and encoded it into AI models. I built proprietary algorithms that process thousands of data points per game and find correlations the books don't price correctly.
              </p>
              <p style={{fontSize: '20px', fontWeight: '600', marginTop: '24px'}}>
                The result: <strong>17% hit rate on 6-leg parlays.</strong>
              </p>
              <p>
                This isn't ChatGPT picking games. This is two decades of sports betting expertise fused with cutting-edge AI, trained specifically on finding parlay correlations.
              </p>
              <p>
                I finally have the tools to build what I always knew was possible. Now you can access it.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Story;


