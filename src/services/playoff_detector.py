"""
Playoff Game Detector Service
==============================
Detects if games are playoff/championship games and applies playoff-specific logic.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, date
import re

logger = logging.getLogger(__name__)


class PlayoffDetector:
    """
    Detects playoff games and provides playoff-specific information.
    """
    
    # Playoff keywords in game names
    PLAYOFF_KEYWORDS = [
        'playoff', 'championship', 'semifinal', 'quarterfinal',
        'bowl', 'rose bowl', 'sugar bowl', 'orange bowl', 'fiesta bowl',
        'cotton bowl', 'peach bowl', 'cfp', 'college football playoff',
        'national championship', 'conference championship',
        'first round', 'second round', 'sweet sixteen', 'elite eight',
        'final four', 'march madness'
    ]
    
    # NCAA Playoff date ranges (approximate)
    NCAAF_PLAYOFF_START_MONTH = 12
    NCAAF_PLAYOFF_START_DAY = 15
    NCAAF_PLAYOFF_END_MONTH = 1
    NCAAF_PLAYOFF_END_DAY = 15
    
    def __init__(self):
        # Cache for playoff status checks
        self._playoff_cache: Dict[str, bool] = {}
    
    def is_playoff_game(
        self, 
        game_data: Dict[str, Any], 
        sport: str
    ) -> bool:
        """
        Determine if a game is a playoff/championship game.
        
        Args:
            game_data: Game information dict with name, date, etc.
            sport: Sport code (ncaaf, ncaab, etc.)
            
        Returns:
            True if this is a playoff game
        """
        game_name = game_data.get('name', '') or game_data.get('game_name', '') or ''
        game_date = game_data.get('date') or game_data.get('game_date')
        
        # Check cache
        cache_key = f"{sport}_{game_name}_{game_date}"
        if cache_key in self._playoff_cache:
            return self._playoff_cache[cache_key]
        
        is_playoff = False
        
        # Method 1: Check game name for playoff keywords
        if game_name:
            name_lower = game_name.lower()
            is_playoff = any(
                keyword.lower() in name_lower 
                for keyword in self.PLAYOFF_KEYWORDS
            )
        
        # Method 2: Check date range for playoff seasons
        if not is_playoff and game_date:
            is_playoff = self._is_playoff_date(game_date, sport)
        
        # Cache result
        self._playoff_cache[cache_key] = is_playoff
        
        if is_playoff:
            logger.debug(f"🏆 Playoff game detected: {game_name} ({sport})")
        
        return is_playoff
    
    def _is_playoff_date(self, game_date: date | datetime | str, sport: str) -> bool:
        """Check if date falls in playoff season."""
        # Convert to date if needed
        if isinstance(game_date, str):
            try:
                from dateutil import parser
                game_date = parser.parse(game_date).date()
            except:
                return False
        elif isinstance(game_date, datetime):
            game_date = game_date.date()
        
        # Sport-specific playoff date ranges
        if sport.lower() in ['ncaaf', 'football']:
            month = game_date.month
            day = game_date.day
            year = game_date.year
            
            # Playoff season: Dec 15 - Jan 15
            if month == 12 and day >= 15:
                return True
            elif month == 1 and day <= 15:
                return True
        
        elif sport.lower() in ['ncaab', 'ncaaw', 'basketball']:
            # March Madness: March - April
            month = game_date.month
            if month in [3, 4]:
                return True
        
        return False
    
    def get_playoff_round(self, game_name: str) -> Optional[str]:
        """
        Determine the playoff round from game name.
        
        Returns:
            Round name (e.g., "Championship", "Semifinal", "Quarterfinal", "Bowl")
        """
        name_lower = game_name.lower()
        
        if 'championship' in name_lower or 'national championship' in name_lower:
            return "Championship"
        elif 'semifinal' in name_lower:
            return "Semifinal"
        elif 'quarterfinal' in name_lower:
            return "Quarterfinal"
        elif 'first round' in name_lower:
            return "First Round"
        elif 'second round' in name_lower:
            return "Second Round"
        elif any(bowl in name_lower for bowl in ['rose', 'sugar', 'orange', 'fiesta', 'cotton', 'peach']):
            return "Bowl"  # New Year's Six or CFP bowl
        elif 'bowl' in name_lower:
            return "Bowl"
        elif 'sweet sixteen' in name_lower or 'round of 16' in name_lower:
            return "Sweet Sixteen"
        elif 'elite eight' in name_lower or 'quarterfinal' in name_lower:
            return "Elite Eight"
        elif 'final four' in name_lower:
            return "Final Four"
        
        return "Playoff"  # Generic playoff game
    
    def get_playoff_adjustments(
        self, 
        game_data: Dict[str, Any], 
        sport: str
    ) -> Dict[str, Any]:
        """
        Get playoff-specific adjustments for betting strategy.
        
        Returns:
            Dict with adjustments like confidence_multiplier, edge_adjustment, etc.
        """
        is_playoff = self.is_playoff_game(game_data, sport)
        
        if not is_playoff:
            return {
                'is_playoff': False,
                'confidence_multiplier': 1.0,
                'edge_adjustment': 0.0,
                'reasoning': 'Regular season game'
            }
        
        game_name = game_data.get('name', '') or game_data.get('game_name', '')
        round_name = self.get_playoff_round(game_name)
        
        # Playoff-specific adjustments
        # Research shows playoff games may have different patterns
        # Adjustments should be refined based on research findings
        
        adjustments = {
            'is_playoff': True,
            'round': round_name,
            'confidence_multiplier': 1.0,  # Start neutral, adjust based on research
            'edge_adjustment': 0.0,  # Start neutral
            'reasoning': f'Playoff game ({round_name}) - may require different strategy'
        }
        
        # Round-specific adjustments (to be refined with research)
        if round_name == "Championship":
            adjustments['confidence_multiplier'] = 0.95  # Slightly more conservative
            adjustments['edge_adjustment'] = -0.01  # Slightly reduce edge requirement
            adjustments['reasoning'] = 'Championship game - historically more predictable patterns'
        elif round_name == "Semifinal":
            adjustments['confidence_multiplier'] = 0.98
            adjustments['edge_adjustment'] = 0.0
            adjustments['reasoning'] = 'Semifinal game - high stakes, may follow patterns'
        
        return adjustments


# Global instance
playoff_detector = PlayoffDetector()


