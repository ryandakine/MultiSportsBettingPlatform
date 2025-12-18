"""
Social Media Formatter Service
===============================
Formats daily picks and parlays for posting on Twitter, Discord, and other platforms.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dateutil import parser

logger = logging.getLogger(__name__)


class SocialMediaFormatter:
    """Format bets and parlays for social media sharing."""
    
    def format_daily_post(
        self,
        daily_pick: Dict[str, Any],
        three_leg_parlay: Dict[str, Any],
        six_leg_parlay: Dict[str, Any],
        platform: str = "twitter"
    ) -> Dict[str, str]:
        """
        Format today's picks for social media posting.
        
        Args:
            daily_pick: Single bet (straight bet) dict
            three_leg_parlay: 3-leg parlay dict with legs
            six_leg_parlay: 6-leg parlay dict (results will be blacked out)
            platform: "twitter" or "discord"
        
        Returns:
            Dict with formatted text for each platform
        """
        posts = {}
        
        # Format single bet (straight bet)
        single_bet_text = self._format_single_bet(daily_pick, platform)
        
        # Format 3-leg parlay
        three_leg_text = self._format_parlay(three_leg_parlay, num_legs=3, platform=platform)
        
        # Format 6-leg parlay (blacked out - no teams shown)
        six_leg_text = self._format_parlay(
            six_leg_parlay, 
            num_legs=6, 
            platform=platform, 
            hide_teams=True
        )
        
        # Combine for Twitter (280 char limit, use threads if needed)
        if platform == "twitter":
            posts["twitter"] = self._format_twitter_post(
                single_bet_text, three_leg_text, six_leg_text
            )
        elif platform == "discord":
            posts["discord"] = self._format_discord_post(
                single_bet_text, three_leg_text, six_leg_text
            )
        else:
            posts["general"] = self._format_general_post(
                single_bet_text, three_leg_text, six_leg_text
            )
        
        return posts
    
    def _format_single_bet(self, bet: Dict[str, Any], platform: str) -> str:
        """Format a single straight bet."""
        team = bet.get("team", "TBD")
        sport = bet.get("sport", "").upper()
        odds = bet.get("odds", 0)
        bet_type = bet.get("bet_type", "moneyline")
        line = bet.get("line")
        
        # Format odds
        odds_str = f"+{odds:.0f}" if odds > 0 else f"{odds:.0f}"
        
        # Format bet type and line
        bet_desc = ""
        if bet_type == "moneyline":
            bet_desc = f"{team} ML"
        elif bet_type == "spread":
            line_str = f"+{line:.1f}" if line and line > 0 else f"{line:.1f}" if line else ""
            bet_desc = f"{team} {line_str}"
        elif bet_type == "over_under":
            bet_desc = f"O/U {line:.1f}" if line else "O/U"
        
        return f"📊 {sport} | {bet_desc} @ {odds_str}"
    
    def _format_parlay(
        self, 
        parlay: Dict[str, Any], 
        num_legs: int, 
        platform: str,
        hide_teams: bool = False
    ) -> str:
        """Format a parlay with legs."""
        legs = parlay.get("legs", [])
        combined_odds = parlay.get("combined_odds", 0)
        
        # Format odds
        odds_str = f"+{combined_odds:.0f}" if combined_odds > 0 else f"{combined_odds:.0f}"
        
        if hide_teams:
            # For 6-leg parlay - black out the teams
            return f"🎯 {num_legs}-Leg Parlay @ {odds_str}\n" + "\n".join([
                f"   Leg {i+1}: ████████" for i in range(num_legs)
            ])
        else:
            # Show actual teams for 3-leg parlay
            leg_texts = []
            for i, leg in enumerate(legs[:num_legs], 1):
                sport = leg.get("sport", "").upper()
                team = leg.get("team", "TBD")
                odds = leg.get("odds", 0)
                bet_type = leg.get("bet_type", "moneyline")
                
                odds_str_leg = f"+{odds:.0f}" if odds > 0 else f"{odds:.0f}"
                
                if bet_type == "moneyline":
                    leg_desc = f"{team} ML"
                elif bet_type == "spread":
                    line = leg.get("line")
                    line_str = f"+{line:.1f}" if line and line > 0 else f"{line:.1f}" if line else ""
                    leg_desc = f"{team} {line_str}"
                else:
                    leg_desc = team
                
                leg_texts.append(f"   Leg {i}: {sport} | {leg_desc} @ {odds_str_leg}")
            
            return f"🎯 {num_legs}-Leg Parlay @ {odds_str}\n" + "\n".join(leg_texts)
    
    def _format_twitter_post(
        self, 
        single_bet: str, 
        three_leg: str, 
        six_leg: str
    ) -> Dict[str, str]:
        """Format for Twitter (may need to split into threads)."""
        header = "🎯 Today's Picks\n\n"
        
        tweet1 = header + f"📊 Single Bet:\n{single_bet}\n\n{three_leg}"
        
        tweet2 = f"{six_leg}\n\n#SportsBetting #DailyPicks"
        
        # Check if we need to split
        if len(tweet1) <= 280:
            return {"tweet_1": tweet1, "tweet_2": tweet2}
        else:
            # Split further if needed
            return {
                "tweet_1": header + f"📊 Single Bet:\n{single_bet}",
                "tweet_2": three_leg,
                "tweet_3": tweet2
            }
    
    def _format_discord_post(
        self, 
        single_bet: str, 
        three_leg: str, 
        six_leg: str
    ) -> str:
        """Format for Discord (more room, can use code blocks)."""
        return f"""🎯 **Today's Picks**

**📊 Single Bet:**
```
{single_bet}
```

**🎯 3-Leg Parlay:**
```
{three_leg}
```

**🎯 6-Leg Parlay (Results Hidden):**
```
{six_leg}
```

#SportsBetting #DailyPicks"""
    
    def _format_general_post(
        self, 
        single_bet: str, 
        three_leg: str, 
        six_leg: str
    ) -> str:
        """General format for other platforms."""
        return f"""🎯 Today's Picks

📊 Single Bet:
{single_bet}

{three_leg}

{six_leg}

#SportsBetting #DailyPicks"""
    
    def format_parlay_result_post(
        self,
        parlay: Dict[str, Any],
        won: bool,
        platform: str = "twitter"
    ) -> str:
        """Format a parlay result for posting (after games finish)."""
        num_legs = len(parlay.get("legs", []))
        combined_odds = parlay.get("combined_odds", 0)
        amount = parlay.get("amount", 0)
        
        result_emoji = "✅" if won else "❌"
        result_text = "HIT" if won else "MISSED"
        
        if platform == "twitter":
            return f"""{result_emoji} {num_legs}-Leg Parlay {result_text}!

Odds: +{combined_odds:.0f}
Bet: ${amount:.2f}

#SportsBetting #Parlay"""
        else:
            return f"""{result_emoji} **{num_legs}-Leg Parlay {result_text}!**

**Odds:** +{combined_odds:.0f}
**Bet:** ${amount:.2f}

#SportsBetting #Parlay"""


# Global instance
social_media_formatter = SocialMediaFormatter()

