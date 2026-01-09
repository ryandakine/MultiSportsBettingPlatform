#!/usr/bin/env python3
"""
NCAA Playoff Pattern Research Script
====================================
Research and analyze NCAA playoff game patterns to find correlations.
Focuses on:
- Who wins playoff games and why
- How they win (dominance patterns, close games, etc.)
- Historical trends and "scripted" patterns
- Team characteristics that correlate with playoff success
"""

import sys
import asyncio
import httpx
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict
from dataclasses import dataclass, field
import json

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(message)s')


@dataclass
class PlayoffGame:
    """Represents a playoff game with all relevant data."""
    date: str
    season: int
    round: str  # "First Round", "Second Round", "Quarterfinal", "Semifinal", "Championship"
    home_team: str
    away_team: str
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    winner: Optional[str] = None
    margin: Optional[int] = None
    home_rank: Optional[int] = None
    away_rank: Optional[int] = None
    conference: Optional[str] = None
    venue: Optional[str] = None
    over_under: Optional[float] = None
    spread: Optional[float] = None


@dataclass
class PlayoffPattern:
    """Represents a discovered pattern in playoff games."""
    pattern_type: str  # "favorite_wins", "rank_correlation", "conference_dominance", etc.
    description: str
    confidence: float  # 0-1
    sample_size: int
    correlation: float  # -1 to 1
    examples: List[str] = field(default_factory=list)


class NCAAPlayoffResearcher:
    """
    Research NCAA playoff patterns using historical data.
    """
    
    def __init__(self):
        self.games: List[PlayoffGame] = []
        self.patterns: List[PlayoffPattern] = []
        self.results_dir = Path("data/playoff_research")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # ESPN endpoint for college football
        self.espn_base = "https://site.api.espn.com/apis/site/v2/sports/football/college-football"
        
    async def fetch_playoff_games(self, seasons: List[int] = None) -> List[PlayoffGame]:
        """
        Fetch historical playoff games from ESPN or other sources.
        
        NCAA Playoff seasons: 2014-2024 (and beyond)
        """
        if seasons is None:
            # Get last 10 seasons of playoff data
            current_year = datetime.now().year
            seasons = list(range(2014, current_year + 1))
        
        logger.info(f"🔍 Fetching NCAA playoff games for seasons: {seasons}")
        playoff_games = []
        
        # Note: ESPN API may not have a dedicated playoff endpoint
        # We'll need to:
        # 1. Identify playoff dates (usually late December through early January)
        # 2. Fetch games for those dates
        # 3. Filter for playoff games (FCS, FBS bowls, CFP)
        
        for season in seasons:
            # Playoff timeframe: Late December through early January
            playoff_start = datetime(season, 12, 15)
            playoff_end = datetime(season + 1, 1, 15)
            
            logger.info(f"   Fetching {season} playoffs ({playoff_start.date()} to {playoff_end.date()})")
            
            # Fetch games in this timeframe
            season_games = await self._fetch_games_for_date_range(playoff_start, playoff_end, season)
            playoff_games.extend(season_games)
        
        logger.info(f"✅ Fetched {len(playoff_games)} potential playoff games")
        return playoff_games
    
    async def _fetch_games_for_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        season: int
    ) -> List[PlayoffGame]:
        """Fetch games for a date range and identify playoff games."""
        games = []
        current_date = start_date
        
        async with httpx.AsyncClient() as client:
            while current_date <= end_date:
                try:
                    # ESPN date format: YYYYMMDD
                    date_str = current_date.strftime('%Y%m%d')
                    url = f"{self.espn_base}/scoreboard"
                    params = {'dates': date_str}
                    
                    response = await client.get(url, params=params, timeout=10.0)
                    if response.status_code == 200:
                        data = response.json()
                        day_games = self._parse_espn_scoreboard(data, current_date, season)
                        games.extend(day_games)
                    
                    # Rate limiting
                    await asyncio.sleep(0.5)
                    current_date += timedelta(days=1)
                    
                except Exception as e:
                    logger.debug(f"Error fetching {current_date.date()}: {e}")
                    current_date += timedelta(days=1)
        
        return games
    
    def _parse_espn_scoreboard(
        self, 
        data: Dict, 
        game_date: datetime, 
        season: int
    ) -> List[PlayoffGame]:
        """Parse ESPN scoreboard response and extract playoff games."""
        games = []
        events = data.get('events', [])
        
        for event in events:
            # Identify if this is a playoff/bowl game
            # Check competition name, season type, etc.
            competition = event.get('competitions', [{}])[0]
            name = event.get('name', '')
            
            # Keywords that indicate playoff/bowl games
            playoff_keywords = [
                'playoff', 'bowl', 'championship', 'semifinal', 'quarterfinal',
                'rose bowl', 'sugar bowl', 'orange bowl', 'fiesta bowl',
                'cotton bowl', 'peach bowl', 'cfp', 'college football playoff'
            ]
            
            is_playoff = any(keyword.lower() in name.lower() for keyword in playoff_keywords)
            
            if not is_playoff:
                continue
            
            # Determine round
            round_name = self._determine_round(name, season)
            
            competitors = competition.get('competitors', [])
            if len(competitors) < 2:
                continue
            
            home_team_data = next((c for c in competitors if c.get('homeAway') == 'home'), None)
            away_team_data = next((c for c in competitors if c.get('homeAway') == 'away'), None)
            
            if not home_team_data or not away_team_data:
                continue
            
            home_team = home_team_data.get('team', {}).get('displayName', '')
            away_team = away_team_data.get('team', {}).get('displayName', '')
            home_score = home_team_data.get('score')
            away_score = away_team_data.get('score')
            
            winner = None
            margin = None
            if home_score is not None and away_score is not None:
                if home_score > away_score:
                    winner = home_team
                    margin = home_score - away_score
                elif away_score > home_score:
                    winner = away_team
                    margin = away_score - home_score
            
            game = PlayoffGame(
                date=game_date.isoformat(),
                season=season,
                round=round_name,
                home_team=home_team,
                away_team=away_team,
                home_score=home_score,
                away_score=away_score,
                winner=winner,
                margin=margin
            )
            
            games.append(game)
        
        return games
    
    def _determine_round(self, game_name: str, season: int) -> str:
        """Determine the playoff round from game name."""
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
            # New Year's Six bowls are usually semifinals or quarterfinals
            if season >= 2014:  # CFP era
                return "Semifinal"  # Or Quarterfinal depending on year
            else:
                return "Bowl"
        else:
            return "Bowl/Playoff"
    
    def analyze_patterns(self, games: List[PlayoffGame]) -> List[PlayoffPattern]:
        """Analyze games to find patterns and correlations."""
        logger.info(f"📊 Analyzing {len(games)} playoff games for patterns...")
        patterns = []
        
        # Filter to games with results
        completed_games = [g for g in games if g.winner is not None]
        logger.info(f"   {len(completed_games)} games with results")
        
        if len(completed_games) < 20:
            logger.warning("⚠️  Not enough data for meaningful analysis")
            return patterns
        
        # Pattern 1: Home team advantage in playoff games
        home_wins = sum(1 for g in completed_games if g.winner == g.home_team)
        home_win_rate = home_wins / len(completed_games) if completed_games else 0
        
        patterns.append(PlayoffPattern(
            pattern_type="home_advantage",
            description=f"Home teams win {home_win_rate:.1%} of playoff games",
            confidence=min(0.9, len(completed_games) / 100),
            sample_size=len(completed_games),
            correlation=home_win_rate - 0.5,  # Above/below 50%
            examples=[f"{g.home_team} beat {g.away_team}" for g in completed_games[:3] if g.winner == g.home_team]
        ))
        
        # Pattern 2: Blowouts vs close games
        margins = [g.margin for g in completed_games if g.margin is not None]
        if margins:
            avg_margin = sum(margins) / len(margins)
            blowouts = sum(1 for m in margins if m > 14)  # More than 2 TDs
            close_games = sum(1 for m in margins if m <= 7)  # One score or less
            
            patterns.append(PlayoffPattern(
                pattern_type="game_margin",
                description=f"Average margin: {avg_margin:.1f} points. {blowouts}/{len(margins)} blowouts (>14), {close_games}/{len(margins)} close games (≤7)",
                confidence=0.8,
                sample_size=len(margins),
                correlation=0.0,  # Descriptive, not predictive
                examples=[]
            ))
        
        # Pattern 3: Round-by-round analysis
        by_round = defaultdict(list)
        for g in completed_games:
            by_round[g.round].append(g)
        
        for round_name, round_games in by_round.items():
            if len(round_games) >= 10:
                home_win_rate_round = sum(1 for g in round_games if g.winner == g.home_team) / len(round_games)
                avg_margin_round = sum(g.margin for g in round_games if g.margin) / len([g for g in round_games if g.margin])
                
                patterns.append(PlayoffPattern(
                    pattern_type=f"{round_name.lower().replace(' ', '_')}_characteristics",
                    description=f"{round_name}: Home win rate {home_win_rate_round:.1%}, Avg margin {avg_margin_round:.1f}",
                    confidence=0.7,
                    sample_size=len(round_games),
                    correlation=0.0,
                    examples=[]
                ))
        
        # Pattern 4: Conference analysis (if we have conference data)
        # TODO: Add when we have conference information
        
        # Pattern 5: Favorite vs underdog (if we have ranking/spread data)
        # TODO: Add when we have odds/ranking data
        
        logger.info(f"✅ Discovered {len(patterns)} patterns")
        return patterns
    
    def save_results(self, games: List[PlayoffGame], patterns: List[PlayoffPattern]):
        """Save research results to files."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save games data (used for backtesting)
        games_file = self.results_dir / f"playoff_games_{timestamp}.json"
        games_data = [
            {
                'date': g.date,
                'season': g.season,
                'round': g.round,
                'home_team': g.home_team,
                'away_team': g.away_team,
                'home_score': g.home_score,
                'away_score': g.away_score,
                'winner': g.winner,
                'margin': g.margin,
                'name': f"{g.home_team} vs {g.away_team}",  # For playoff detection
                'game_id': f"playoff_{g.season}_{i}"  # Generate ID
            }
            for i, g in enumerate(games)
        ]
        
        with open(games_file, 'w') as f:
            json.dump(games_data, f, indent=2)
        
        logger.info(f"💾 Saved {len(games)} games to {games_file}")
        logger.info(f"   📊 This data can be used for backtesting bet types")
        
        # Save patterns
        patterns_file = self.results_dir / f"playoff_patterns_{timestamp}.json"
        patterns_data = [
            {
                'pattern_type': p.pattern_type,
                'description': p.description,
                'confidence': p.confidence,
                'sample_size': p.sample_size,
                'correlation': p.correlation,
                'examples': p.examples
            }
            for p in patterns
        ]
        
        with open(patterns_file, 'w') as f:
            json.dump(patterns_data, f, indent=2)
        
        logger.info(f"💾 Saved {len(patterns)} patterns to {patterns_file}")
        
        # Save summary report
        report_file = self.results_dir / f"playoff_research_report_{timestamp}.md"
        self._generate_report(report_file, games, patterns)
        logger.info(f"📄 Generated report: {report_file}")
    
    def _generate_report(self, report_file: Path, games: List[PlayoffGame], patterns: List[PlayoffPattern]):
        """Generate a markdown report of findings."""
        with open(report_file, 'w') as f:
            f.write("# NCAA Playoff Pattern Research Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Total Games Analyzed:** {len(games)}\n")
            f.write(f"**Completed Games:** {len([g for g in games if g.winner])}\n\n")
            
            f.write("## Discovered Patterns\n\n")
            for pattern in patterns:
                f.write(f"### {pattern.pattern_type.replace('_', ' ').title()}\n\n")
                f.write(f"- **Description:** {pattern.description}\n")
                f.write(f"- **Confidence:** {pattern.confidence:.1%}\n")
                f.write(f"- **Sample Size:** {pattern.sample_size}\n")
                f.write(f"- **Correlation:** {pattern.correlation:+.2f}\n")
                if pattern.examples:
                    f.write(f"- **Examples:** {', '.join(pattern.examples)}\n")
                f.write("\n")
            
            f.write("## Recommendations\n\n")
            f.write("Based on the patterns discovered, consider:\n")
            f.write("1. Adjusting betting strategy for playoff games\n")
            f.write("2. Using different confidence thresholds for playoff rounds\n")
            f.write("3. Considering home advantage and margin patterns\n")
            f.write("4. Applying round-specific strategies\n\n")


async def main():
    """Main research function."""
    print("=" * 80)
    print("🏈 NCAA PLAYOFF PATTERN RESEARCH")
    print("=" * 80)
    print()
    
    researcher = NCAAPlayoffResearcher()
    
    # Fetch playoff games
    games = await researcher.fetch_playoff_games()
    
    if not games:
        print("❌ No playoff games found. This could mean:")
        print("   1. API is unavailable")
        print("   2. Date range needs adjustment")
        print("   3. Need to use alternative data source")
        return
    
    # Analyze patterns
    patterns = researcher.analyze_patterns(games)
    
    # Save results
    researcher.save_results(games, patterns)
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 RESEARCH SUMMARY")
    print("=" * 80)
    print(f"Games analyzed: {len(games)}")
    print(f"Patterns discovered: {len(patterns)}")
    print()
    print("Key Findings:")
    for pattern in patterns[:5]:  # Show top 5
        print(f"  • {pattern.description}")
    
    print(f"\n💾 Full results saved to: {researcher.results_dir}")


if __name__ == "__main__":
    asyncio.run(main())

