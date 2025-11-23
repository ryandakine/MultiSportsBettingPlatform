#!/usr/bin/env python3
"""
Unified Brain Optimizer
=======================
Runs parameter sweeps to find the optimal configuration for the Supreme Court system.
Tests:
- Parlay Sizes (2, 3, 4, 5 legs)
- Confidence Thresholds (0.6 - 0.95)
- Portfolio Allocation (Flat vs Kelly)
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import json
from itertools import product

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("Optimizer")

class UnifiedBrainOptimizer:
    def __init__(self):
        self.historical_data = self.load_data()
        self.results = []

    def load_data(self):
        """Load historical data."""
        file_path = Path("data/historical/all_games_10yr.csv")
        if file_path.exists():
            return pd.read_csv(file_path)
        return pd.DataFrame()

    def simulate_predictions(self, games, base_accuracy=0.65):
        """Simulate AI predictions with a given base accuracy."""
        predictions = []
        for _, game in games.iterrows():
            home_score = game.get('home_score', 0)
            away_score = game.get('away_score', 0)
            point_diff = abs(home_score - away_score)
            
            # Determine actual winner
            if game.get('winner') == 'home':
                actual_winner = game.get('home_team')
            elif game.get('winner') == 'away':
                actual_winner = game.get('away_team')
            else:
                actual_winner = game.get('home_team') if home_score > away_score else game.get('away_team')

            # Simulate confidence
            confidence = min(0.99, 0.55 + (point_diff / 40.0))
            
            # Simulate prediction accuracy
            # Higher confidence = higher chance of being correct
            adjusted_accuracy = base_accuracy + (confidence - 0.55) * 0.5
            is_correct = np.random.random() < adjusted_accuracy
            
            pick = actual_winner if is_correct else (
                game.get('away_team') if actual_winner == game.get('home_team') else game.get('home_team')
            )
            
            predictions.append({
                'pick': pick,
                'actual_winner': actual_winner,
                'confidence': confidence,
                'is_correct': is_correct
            })
        return predictions

    def run_optimization(self, num_trials=1000):
        """Run parameter sweep."""
        if self.historical_data.empty:
            logger.error("No data found.")
            return

        configs = {
            'parlay_size': [2, 3, 4, 5],
            'min_confidence': [0.60, 0.70, 0.80, 0.90]
        }
        
        logger.info(f"🚀 Starting Optimization Sweep ({num_trials} trials per config)...")
        logger.info("-" * 60)
        logger.info(f"{'Legs':<5} | {'Conf':<5} | {'Win Rate':<9} | {'ROI':<8} | {'Profit':<10} | {'Rating':<8}")
        logger.info("-" * 60)

        best_roi = -float('inf')
        best_config = None

        # Grid search
        for legs, min_conf in product(configs['parlay_size'], configs['min_confidence']):
            total_profit = 0
            wins = 0
            total_bets = 0
            
            # Odds mapping (approximate standard odds)
            # 2-leg: +260 (3.6x)
            # 3-leg: +600 (7.0x)
            # 4-leg: +1200 (13.0x)
            # 5-leg: +2400 (25.0x)
            payout_multipliers = {2: 3.6, 3: 7.0, 4: 13.0, 5: 25.0}
            multiplier = payout_multipliers.get(legs, 0)

            for _ in range(num_trials):
                # Sample a "day" of games
                batch = self.historical_data.sample(n=30)
                preds = self.simulate_predictions(batch)
                
                # Filter by confidence
                eligible_preds = [p for p in preds if p['confidence'] >= min_conf]
                
                # Sort by confidence
                eligible_preds.sort(key=lambda x: x['confidence'], reverse=True)
                
                # Take top N
                if len(eligible_preds) >= legs:
                    parlay = eligible_preds[:legs]
                    
                    # Check result
                    if all(leg['is_correct'] for leg in parlay):
                        profit = 100 * (multiplier - 1)
                        wins += 1
                    else:
                        profit = -100
                    
                    total_profit += profit
                    total_bets += 1

            # Calculate metrics
            win_rate = (wins / total_bets * 100) if total_bets > 0 else 0
            roi = (total_profit / (total_bets * 100) * 100) if total_bets > 0 else 0
            
            # Rating score (balance of ROI and Volume)
            # We penalize very low volume configs
            volume_factor = min(1.0, total_bets / (num_trials * 0.5))
            rating = roi * volume_factor

            logger.info(f"{legs:<5} | {min_conf:<5} | {win_rate:>6.1f}% | {roi:>6.1f}% | ${total_profit:>8,.0f} | {rating:>6.1f}")

            if rating > best_roi:
                best_roi = rating
                best_config = {'legs': legs, 'min_conf': min_conf, 'roi': roi, 'win_rate': win_rate}

        logger.info("-" * 60)
        logger.info("🏆 OPTIMAL CONFIGURATION FOUND:")
        logger.info(f"   Parlay Legs: {best_config['legs']}")
        logger.info(f"   Min Confidence: {best_config['min_conf']}")
        logger.info(f"   Expected ROI: {best_config['roi']:.1f}%")
        logger.info(f"   Win Rate: {best_config['win_rate']:.1f}%")

        # Save results
        with open("data/optimization_results.json", "w") as f:
            json.dump(best_config, f, indent=2)

if __name__ == "__main__":
    optimizer = UnifiedBrainOptimizer()
    optimizer.run_optimization()
