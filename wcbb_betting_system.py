#!/usr/bin/env python3
"""
Women's College Basketball (WCBB) Betting System
================================================
Dedicated system for analyzing Women's NCAA Basketball games.
Leverages the existing CBB AI Council and Line Monitor infrastructure.
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Import shared components
from line_monitor import LineMonitor
from cbb_12model_ai_council import CBB12ModelAICouncil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/wcbb_betting_system.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("WCBB_System")

class WCBBBettingSystem:
    def __init__(self):
        self.monitor = LineMonitor()
        self.council = CBB12ModelAICouncil()
        self.sport_keys = ['basketball_ncaaw', 'basketball_wnba']
        
    def run_analysis(self) -> List[Dict]:
        """Fetch and analyze Women's Basketball games (NCAAW & WNBA)."""
        logger.info(f"🏀 Starting Women's Basketball Analysis for {datetime.now().strftime('%Y-%m-%d')}")
        
        all_picks = []
        
        for sport in self.sport_keys:
            sport_name = "NCAAW" if "ncaaw" in sport else "WNBA"
            logger.info(f"   Analyzing {sport_name}...")
            
            # 1. Fetch Odds
            odds_data = self.monitor.fetch_odds(sport=sport)
            games = odds_data.get('games', [])
            
            if not games:
                logger.info(f"   No {sport_name} games found today.")
                continue
                
            logger.info(f"   Found {len(games)} {sport_name} games.")
            
            # 2. Analyze Games
            for game in games:
                try:
                    # Adapt game data for AI Council if necessary
                    analysis = self.council.analyze_game(game)
                    
                    if analysis and analysis.confidence_score >= 0.60:
                        pick_data = {
                            "sport": sport_name,
                            "game_id": game.get('id'),
                            "home_team": game.get('home_team'),
                            "away_team": game.get('away_team'),
                            "pick": analysis.recommendation,
                            "confidence": analysis.confidence_score,
                            "logic": analysis.reasoning
                        }
                        all_picks.append(pick_data)
                        logger.info(f"✅ {sport_name} Pick: {analysis.recommendation} ({analysis.confidence_score:.2f})")
                        
                except Exception as e:
                    logger.error(f"Error analyzing {sport_name} game {game.get('home_team')} vs {game.get('away_team')}: {e}")
                    
        return all_picks

if __name__ == "__main__":
    system = WCBBBettingSystem()
    picks = system.run_analysis()
    print(json.dumps(picks, indent=2))
