#!/usr/bin/env python3
"""
Unified Brain Backtester (5-Sport Edition)
==========================================
Simulates the "Supreme Court" logic across 5 sports:
1. CBB (Real Historical Data)
2. NFL (Simulated)
3. NCAAF (Simulated)
4. NHL (Simulated)
5. WCBB/WNBA (Simulated)
"""

import pandas as pd
import numpy as np
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("Backtester")

class SportsSimulator:
    """Generates synthetic game data and AI predictions for non-CBB sports."""
    
    def __init__(self):
        # Base accuracy for AI models in each sport
        self.sport_profiles = {
            'NFL': {'accuracy': 0.58, 'volatility': 0.15, 'games_per_day': (1, 3)},
            'NCAAF': {'accuracy': 0.62, 'volatility': 0.20, 'games_per_day': (2, 5)},
            'NHL': {'accuracy': 0.56, 'volatility': 0.25, 'games_per_day': (3, 8)},
            'NCAAW': {'accuracy': 0.65, 'volatility': 0.18, 'games_per_day': (2, 6)},
            'WNBA': {'accuracy': 0.60, 'volatility': 0.15, 'games_per_day': (1, 3)}
        }

    def generate_slate(self, sport: str) -> List[Dict]:
        """Generate a daily slate of games and AI picks for a sport."""
        profile = self.sport_profiles.get(sport)
        if not profile:
            return []
            
        num_games = random.randint(*profile['games_per_day'])
        picks = []
        
        for i in range(num_games):
            # Simulate Game Outcome
            is_favorite_winner = random.random() < 0.65 
            
            # Simulate AI Prediction
            is_correct = random.random() < profile['accuracy']
            
            # Generate Confidence
            base_conf = 0.60
            if is_correct:
                confidence = min(0.99, base_conf + random.random() * 0.35)
            else:
                confidence = min(0.95, base_conf + random.random() * 0.30) 
                
            picks.append({
                'sport': sport,
                'game_id': f"{sport}_{random.randint(1000,9999)}",
                'pick': f"{sport} Team {i+1}",
                'confidence': round(confidence, 2),
                'is_correct': is_correct,
                'reasoning': "Simulated AI Analysis"
            })
            
        return picks

class UnifiedBrainBacktester:
    def __init__(self):
        self.cbb_data = self.load_historical_cbb_data()
        self.simulator = SportsSimulator()
        self.results = []
        self.bankroll = 10000
        self.initial_bankroll = 10000
        self.bet_size = 100
        
    def load_historical_cbb_data(self):
        """Load historical CBB games."""
        path = Path("data/historical/all_games_10yr.csv")
        if path.exists():
            df = pd.read_csv(path)
            logger.info(f"✅ Loaded {len(df)} historical CBB games")
            return df
        else:
            logger.warning("⚠️ CBB historical data not found. Using simulation only.")
            return pd.DataFrame()

    def get_real_cbb_picks(self, n=5) -> List[Dict]:
        """Sample real CBB games and simulate AI predictions on them."""
        if self.cbb_data.empty:
            return []

        sample_size = min(n, len(self.cbb_data))
        if sample_size == 0:
            return []
            
        sample = self.cbb_data.sample(n=sample_size)
        picks = []
        
        for _, row in sample.iterrows():
            winner = row['home_team'] if row['home_score'] > row['away_score'] else row['away_team']
            margin = abs(row['home_score'] - row['away_score'])
            
            base_acc = 0.60 + (min(margin, 20) / 100)
            is_correct = random.random() < base_acc
            
            pick_team = winner if is_correct else (row['away_team'] if winner == row['home_team'] else row['home_team'])
            confidence = 0.60 + (min(margin, 25) / 80) + (random.random() * 0.1)
            
            picks.append({
                'sport': 'NCAAB',
                'game_id': str(row['game_id']),
                'pick': pick_team,
                'confidence': round(min(0.99, confidence), 2),
                'is_correct': is_correct,
                'reasoning': f"Historical Margin: {margin}"
            })
        return picks

    def run_simulation(self, days=365):
        """Run the backtest over N days."""
        logger.info(f"🚀 Starting 5-Sport Backtest ({days} Days)...")
        logger.info(f"💰 Initial Bankroll: ${self.bankroll}")
        
        for day in range(days):
            daily_pool = []
            
            # Real CBB Data
            daily_pool.extend(self.get_real_cbb_picks(n=random.randint(5, 15)))
            
            # Simulated Sports
            for sport in ['NFL', 'NCAAF', 'NHL', 'NCAAW', 'WNBA']:
                if random.random() < 0.7: 
                    daily_pool.extend(self.simulator.generate_slate(sport))
            
            if len(daily_pool) < 5:
                continue 
                
            # Supreme Court Logic
            daily_pool.sort(key=lambda x: x['confidence'], reverse=True)
            parlay_legs = daily_pool[:5]
            
            parlay_won = all(leg['is_correct'] for leg in parlay_legs)
            payout_multiplier = (1.909 ** 5) 
            
            if parlay_won:
                profit = (self.bet_size * payout_multiplier) - self.bet_size
                self.bankroll += profit
                result = "WIN"
            else:
                loss = self.bet_size
                self.bankroll -= loss
                result = "LOSS"
                
            self.results.append({
                'day': day + 1,
                'parlay_legs': [f"{leg['sport']}:{leg['pick']}" for leg in parlay_legs],
                'parlay_won': parlay_won,
                'result': result,
                'bankroll_after': self.bankroll
            })
        
        logger.info(f"✅ Simulation complete.")
        self.display_results()

    def display_results(self):
        """Display backtest results."""
        total_parlays = len(self.results)
        wins = sum(1 for r in self.results if r['result'] == 'WIN')
        losses = total_parlays - wins
        
        win_rate = (wins / total_parlays * 100) if total_parlays > 0 else 0
        roi = ((self.bankroll - self.initial_bankroll) / self.initial_bankroll) * 100
        
        print("\n" + "="*60)
        print("🏆 UNIFIED BRAIN BACKTEST RESULTS (5-SPORT SIMULATION)")
        print("="*60)
        print(f"Total Days:      {len(self.results)}")
        print(f"Total Parlays:   {total_parlays}")
        print(f"Wins:            {wins}")
        print(f"Losses:          {losses}")
        print(f"Win Rate:        {win_rate:.2f}%")
        print(f"Final Bankroll:  ${self.bankroll:,.2f}")
        print(f"Total ROI:       {roi:.2f}%")
        print("="*60)
        
        sport_counts = {}
        for res in self.results:
            for leg_str in res['parlay_legs']:
                sport = leg_str.split(':')[0]
                sport_counts[sport] = sport_counts.get(sport, 0) + 1
                
        print("\n🏆 Sport Representation in Parlays:")
        for sport, count in sorted(sport_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {sport}: {count} legs")
        
        output_file = Path("data/unified_brain_backtest.json")
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump({
                'summary': {
                    'total_parlays': total_parlays,
                    'wins': wins,
                    'win_rate': win_rate,
                    'final_bankroll': self.bankroll,
                    'roi': roi
                },
                'sport_distribution': sport_counts,
                'history': self.results
            }, f, indent=2)
        
        logger.info(f"\n✅ Results saved to {output_file}")

if __name__ == "__main__":
    backtester = UnifiedBrainBacktester()
    backtester.run_simulation()
