# Marketing Site for MultiSports Betting Platform

This is the public-facing marketing website (.com) that advertises the platform and collects applications.

## Structure

- **Landing Page**: Complete marketing site with all sections
- **Platform Preview**: Shows what the .onion platform looks like
- **Application Form**: Collects license applications
- **Payment**: Monero payment integration (to be added)

## Sections

1. **Hero** - Main headline with key stats
2. **Story** - 20 years of experience, how platform was built
3. **Features** - Complete platform feature breakdown
4. **Proof** - Backtest data (88,687 games, 18.4% win rate, 790% ROI)
5. **Platform Preview** - Demo/preview of actual platform
6. **Privacy & Security** - .onion hosting + Monero payments explanation
7. **Pricing** - $10K one-time, 100 licenses only
8. **Application Form** - Collect applications
9. **FAQ** - Common questions
10. **Footer** - Legal disclaimers, links

## Setup

```bash
cd marketing-site
npm install
npm start
```

## Build for Production

```bash
npm run build
```

## Deployment

The built site should be deployed to a .com domain for public marketing. The actual platform remains on .onion domain for license holders only.

## Notes

- This is the PUBLIC marketing site
- Actual platform access is via .onion domain (separate)
- Payment integration (Monero) to be added later
- Application form needs backend API integration




