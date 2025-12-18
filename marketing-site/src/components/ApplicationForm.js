import React, { useState } from 'react';
import './ApplicationForm.css';

const ApplicationForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    bettingExperience: '',
    annualBettingVolume: '',
    currentBankroll: '',
    howDidYouFindUs: '',
    whyDoYouWantIn: ''
  });

  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [applicationId, setApplicationId] = useState(null);

  // API URL - use environment variable or default to localhost for development
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    // Clear error when user starts typing
    if (error) setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Map frontend field names to backend API format
      // Combine fields into experience and interest for backend compatibility
      const experienceText = `Betting Experience: ${formData.bettingExperience}\nAnnual Betting Volume: ${formData.annualBettingVolume}\nCurrent Bankroll: ${formData.currentBankroll}`;
      const interestText = `How did you find us: ${formData.howDidYouFindUs}\nWhy do you want in: ${formData.whyDoYouWantIn}`;
      
      const payload = {
        name: formData.name.trim(),
        email: formData.email.trim(),
        phone: null,
        experience: experienceText.trim() || null,
        interest: interestText.trim() || null,
        monero_acknowledged: true // NDA/payment understanding implied by applying
      };

      const response = await fetch(`${API_URL}/api/v1/applications/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (!response.ok) {
        // Handle error response
        const errorMessage = data.message || data.error || 'Failed to submit application. Please try again.';
        throw new Error(errorMessage);
      }

      // Success
      setApplicationId(data.application_id);
      setSubmitted(true);
      
      // Reset form after 5 seconds
      setTimeout(() => {
        setSubmitted(false);
        setApplicationId(null);
        setFormData({
          name: '',
          email: '',
          bettingExperience: '',
          annualBettingVolume: '',
          currentBankroll: '',
          howDidYouFindUs: '',
          whyDoYouWantIn: ''
        });
      }, 10000); // Longer timeout to show success message

    } catch (err) {
      console.error('Application submission error:', err);
      setError(err.message || 'Failed to submit application. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <section id="apply" className="application-section">
        <div className="container">
          <div className="application-success">
            <div className="success-icon">✓</div>
            <h2>Application Submitted!</h2>
            {applicationId && (
              <p style={{ marginBottom: '1rem', fontWeight: '500', color: '#4a5568' }}>
                Application ID: <code style={{ background: '#edf2f7', padding: '0.25rem 0.5rem', borderRadius: '4px' }}>{applicationId}</code>
              </p>
            )}
            <p>
              Thank you for your interest. We review every application carefully. If approved, 
              you'll receive instructions for NDA signing and payment. Not everyone is accepted.
            </p>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section id="apply" className="application-section">
      <div className="container">
        <h2 className="section-title">Apply for Membership</h2>
        <p className="section-subtitle">
          [SPOTS REMAINING: XX/100]
        </p>
        <p style={{textAlign: 'center', marginBottom: '32px', color: 'rgba(255, 255, 255, 0.8)'}}>
          We review every application. Not everyone is accepted.
        </p>

        <div className="application-form-container">
          <form className="application-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="name">Full Name *</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                placeholder="John Doe"
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">Email Address *</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                placeholder="john@example.com"
              />
            </div>

            <div className="form-group">
              <label htmlFor="bettingExperience">Betting Experience (Years) *</label>
              <input
                type="text"
                id="bettingExperience"
                name="bettingExperience"
                value={formData.bettingExperience}
                onChange={handleChange}
                required
                placeholder="e.g., 5 years"
              />
            </div>

            <div className="form-group">
              <label htmlFor="annualBettingVolume">Estimated Annual Betting Volume *</label>
              <input
                type="text"
                id="annualBettingVolume"
                name="annualBettingVolume"
                value={formData.annualBettingVolume}
                onChange={handleChange}
                required
                placeholder="e.g., $50,000 per year"
              />
            </div>

            <div className="form-group">
              <label htmlFor="currentBankroll">Current Bankroll Dedicated to Betting *</label>
              <input
                type="text"
                id="currentBankroll"
                name="currentBankroll"
                value={formData.currentBankroll}
                onChange={handleChange}
                required
                placeholder="e.g., $25,000"
              />
            </div>

            <div className="form-group">
              <label htmlFor="howDidYouFindUs">How Did You Find Us? *</label>
              <input
                type="text"
                id="howDidYouFindUs"
                name="howDidYouFindUs"
                value={formData.howDidYouFindUs}
                onChange={handleChange}
                required
                placeholder="e.g., Twitter, referral, search engine, etc."
              />
            </div>

            <div className="form-group">
              <label htmlFor="whyDoYouWantIn">Why Do You Want In? *</label>
              <textarea
                id="whyDoYouWantIn"
                name="whyDoYouWantIn"
                value={formData.whyDoYouWantIn}
                onChange={handleChange}
                required
                rows="4"
                placeholder="Tell us why you want to join the network..."
              />
            </div>

            <div className="form-note">
              <p>
                <strong>The Process:</strong>
              </p>
              <ol>
                <li><strong>Apply</strong> - Tell us about your betting history and bankroll</li>
                <li><strong>Review</strong> - We verify you're serious (not everyone gets in)</li>
                <li><strong>NDA</strong> - Sign the agreement protecting the network</li>
                <li><strong>Payment</strong> - $10,000 for 12 months of access (cryptocurrency only)</li>
                <li><strong>Access</strong> - Secure credentials to the private system</li>
                <li><strong>Network</strong> - Introduction to the member community</li>
              </ol>
            </div>

            {error && (
              <div className="form-error" style={{ 
                padding: '1rem', 
                marginBottom: '1rem', 
                backgroundColor: '#fed7d7', 
                border: '1px solid #fc8181', 
                borderRadius: '4px', 
                color: '#c53030' 
              }}>
                <strong>Error:</strong> {error}
              </div>
            )}

            <button 
              type="submit" 
              className="btn btn-primary btn-large"
              disabled={loading}
            >
              {loading ? 'Submitting...' : 'Submit Application'}
            </button>
          </form>
        </div>
      </div>
    </section>
  );
};

export default ApplicationForm;

