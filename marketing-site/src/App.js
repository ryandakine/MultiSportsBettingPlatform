import React from 'react';
import './App.css';
import Hero from './components/Hero';
import Story from './components/Story';
import Network from './components/Network';
import Features from './components/Features';
import Proof from './components/Proof';
import HowItWorks from './components/HowItWorks';
import Pricing from './components/Pricing';
import ApplicationForm from './components/ApplicationForm';
import FAQ from './components/FAQ';
import Footer from './components/Footer';
import Navigation from './components/Navigation';

function App() {
  return (
    <div className="App">
      <Navigation />
      <Hero />
      <Story />
      <Network />
      <Features />
      <Proof />
      <HowItWorks />
      <Pricing />
      <ApplicationForm />
      <FAQ />
      <Footer />
    </div>
  );
}

export default App;


