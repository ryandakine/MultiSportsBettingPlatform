import React, { useState, useEffect } from 'react';
import './Navigation.css';

const Navigation = () => {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToSection = (id) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <nav className={`navigation ${scrolled ? 'scrolled' : ''}`}>
      <div className="nav-container">
        <div className="nav-logo">
          <span className="logo-icon">🎯</span>
          <span className="logo-text">MultiSports AI</span>
        </div>
        <div className="nav-links">
          <a href="#story" onClick={(e) => { e.preventDefault(); scrollToSection('story'); }}>The System</a>
          <a href="#network" onClick={(e) => { e.preventDefault(); scrollToSection('network'); }}>The Network</a>
          <a href="#features" onClick={(e) => { e.preventDefault(); scrollToSection('features'); }}>What We Track</a>
          <a href="#proof" onClick={(e) => { e.preventDefault(); scrollToSection('proof'); }}>The Numbers</a>
          <a href="#pricing" onClick={(e) => { e.preventDefault(); scrollToSection('pricing'); }}>Why $10K</a>
          <a href="#faq" onClick={(e) => { e.preventDefault(); scrollToSection('faq'); }}>FAQ</a>
          <a href="#apply" className="btn btn-primary btn-small" onClick={(e) => { e.preventDefault(); scrollToSection('apply'); }}>
            Apply for Membership
          </a>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;


