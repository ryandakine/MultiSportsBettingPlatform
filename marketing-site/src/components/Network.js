import React from 'react';
import './Network.css';

const Network = () => {
  return (
    <section id="network" className="network-section">
      <div className="container">
        <h2 className="section-title">The Network</h2>
        <p className="section-subtitle">
          This Isn't a Discord Full of Randos.
        </p>
        <p style={{textAlign: 'center', fontSize: '24px', fontWeight: '600', color: 'white', marginBottom: '48px'}}>
          It's 100 people. That's it. Ever.
        </p>

        <div className="network-content">
          <div className="network-card">
            <h3>What the NDA Creates</h3>
            <p>
              When you sign, you agree not to discuss picks, methods, or membership with anyone outside the network.
            </p>
            <ul>
              <li>The only people you can talk to about this are the other 99 members</li>
              <li>Everyone in the room is serious (they paid $10K to be there)</li>
              <li>No lurkers, no tire-kickers, no one sharing your edge on Twitter</li>
              <li>A closed network of bettors who all have skin in the game</li>
            </ul>
          </div>

          <div className="network-card">
            <h3>What This Becomes</h3>
            <ul>
              <li>100 people sharing insights within the rules</li>
              <li>100 people discussing line movement, book limits, bet placement strategy</li>
              <li>100 people who GET IT because they paid to be there</li>
              <li>Relationships with other serious bettors you can't find anywhere else</li>
            </ul>
          </div>
        </div>

        <div className="network-note">
          <p>
            <strong>Want your friend in?</strong> They apply like everyone else. If there's a spot, they can join. Then you have someone to talk to.
          </p>
          <p>
            The NDA doesn't limit you. It guarantees the quality of who you're surrounded by.
          </p>
        </div>
      </div>
    </section>
  );
};

export default Network;

