#!/usr/bin/env python3
"""
Playoff Bet Type Backtesting Engine
====================================
Backtests different bet types for playoff games to find where real edge exists.
Tests: moneyline, over/under, spreads, first half, props, etc.

This validates which bet types actually have edge in playoff games through historical data.
"""

import sys
import asyncio
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

from src.services.playoff_detector import playoff_detector
from src.services.real_sports_service import real_sports_service


@dataclass
class BetTypeResult:
    """Results for a specific bet type in playoff games."""
    bet_type: str
    total_bets: int
    wins: int
    losses: int
    pushes: int = 0
    total_wagered: float = 0.0
    total_profit: float = 0.0
    avg_edge: float = 0.0
    avg_confidence: float = 0.0
    
    @property
    def win_rate(self) -> float:
        if self.total_bets == 0:
            return 0.0
        return (self.wins / (self.wins + self.losses)) * 100 if (self.wins + self.losses) > 0 else 0.0
    
    @property
    def roi(self) -> float:
        if self.total_wagered == 0:
            return 0.0
        return (self.total_profit / self.total_wagered) * 100
    
    @property
    def has_edge(self) -> bool:
        """Determine if this bet type has edge (positive ROI)."""
        return self.roi > 0 and self.win_rate > 50


@dataclass
class PlayoffBacktestResult:
    """Complete backtest results for playoff games."""
    season: int
    round_name: str
    bet_type_results: Dict[str, BetTypeResult] = field(default_factory=dict)
    total_games: int = 0
    games_tested: int = 0


class PlayoffBetTypeBacktester:
    """
    Backtests different bet types for playoff games to find where edge exists.
    """
    
    def __init__(self):
        self.results_dir = Path("data/playoff_backtesting")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Bet types to test
        self.bet_types_to_test = [
            "moneyline",
            "over_under",
            "spread",
            # Future: Add when we have data
            # "first_half_moneyline",
            # "first_half_total",
            # "first_quarter_total",  # For basketball
            # "team_total",
            # "player_props",
        ]
        
        # Minimum games required for statistical significance
        self.min_games = 10
        
    async def backtest_playoff_season(
        self, 
        season: int,
        games: List[Dict[str, Any]]
    ) -> Dict[str, PlayoffBacktestResult]:
        """
        Backtest a specific playoff season.
        
        Args:
            season: Season year
            games: List of playoff games with results
            
        Returns:
            Dict of results by round
        """
        logger.info(f"📊 Backtesting {season} playoff season ({len(games)} games)")
        
        # Group games by round
        by_round = defaultdict(list)
        for game in games:
            game_name = game.get('name', '') or game.get('game_name', '')
            round_name = playoff_detector.get_playoff_round(game_name)
            by_round[round_name].append(game)
        
        results_by_round = {}
        
        for round_name, round_games in by_round.items():
            logger.info(f"   Testing {round_name}: {len(round_games)} games")
            
            result = PlayoffBacktestResult(
                season=season,
                round_name=round_name,
                total_games=len(round_games)
            )
            
            # Test each bet type
            for bet_type in self.bet_types_to_test:
                bet_result = await self._test_bet_type(
                    round_games, bet_type, season, round_name
                )
                
                if bet_result.total_bets >= self.min_games:
                    result.bet_type_results[bet_type] = bet_result
                    result.games_tested += bet_result.total_bets
                    
                    logger.info(
                        f"      {bet_type}: "
                        f"{bet_result.win_rate:.1f}% win rate, "
                        f"{bet_result.roi:+.1f}% ROI, "
                        f"{bet_result.total_bets} bets"
                    )
            
            results_by_round[round_name] = result
        
        return results_by_round
    
    async def _test_bet_type(
        self,
        games: List[Dict[str, Any]],
        bet_type: str,
        season: int,
        round_name: str
    ) -> BetTypeResult:
        """
        Test a specific bet type against playoff games.
        
        This simulates placing bets and tracks results.
        Note: This is a simplified version - real backtesting would need:
        - Historical odds data
        - Actual game results (scores)
        - Bet outcome calculations
        """
        result = BetTypeResult(
            bet_type=bet_type,
            total_bets=0,
            wins=0,
            losses=0,
            pushes=0,
            total_wagered=0.0,
            total_profit=0.0,
            avg_edge=0.0,
            avg_confidence=0.0
        )
        
        edges = []
        confidences = []
        
        for game in games:
            # Skip games without results
            if not self._has_complete_result(game):
                continue
            
            # Simulate bet placement
            # In real backtesting, we would:
            # 1. Get historical odds for this game
            # 2. Determine if we would bet (based on edge/confidence)
            # 3. Calculate outcome
            # 4. Track profit/loss
            
            # For now, this is a placeholder structure
            # TODO: Implement actual backtesting logic with historical odds
            
            # Simulated logic (needs real historical odds data):
            # - Check if prediction had edge
            # - Place bet if edge > threshold
            # - Calculate win/loss based on actual game result
            # - Track profit/loss
            
            result.total_bets += 1
            # result.wins/losses would be calculated based on actual outcomes
        
        if result.total_bets > 0:
            result.avg_edge = sum(edges) / len(edges) if edges else 0.0
            result.avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return result
    
    def _has_complete_result(self, game: Dict[str, Any]) -> bool:
        """Check if game has complete result data."""
        home_score = game.get('home_score')
        away_score = game.get('away_score')
        return home_score is not None and away_score is not None
    
    async def analyze_backtest_results(
        self,
        all_results: Dict[int, Dict[str, PlayoffBacktestResult]]
    ) -> Dict[str, Any]:
        """
        Analyze all backtest results to find patterns.
        
        Returns:
            Analysis dict with findings
        """
        logger.info("📊 Analyzing backtest results...")
        
        # Aggregate results across all seasons and rounds
        bet_type_aggregates: Dict[str, List[BetTypeResult]] = defaultdict(list)
        
        for season, round_results in all_results.items():
            for round_name, result in round_results.items():
                for bet_type, bet_result in result.bet_type_results.items():
                    bet_type_aggregates[bet_type].append(bet_result)
        
        # Calculate overall stats for each bet type
        analysis = {
            'bet_type_performance': {},
            'best_bet_types': [],
            'worst_bet_types': [],
            'recommendations': []
        }
        
        for bet_type, results_list in bet_type_aggregates.items():
            if not results_list:
                continue
            
            # Aggregate stats
            total_bets = sum(r.total_bets for r in results_list)
            total_wins = sum(r.wins for r in results_list)
            total_losses = sum(r.losses for r in results_list)
            total_wagered = sum(r.total_wagered for r in results_list)
            total_profit = sum(r.total_profit for r in results_list)
            
            overall_win_rate = (total_wins / (total_wins + total_losses) * 100) if (total_wins + total_losses) > 0 else 0
            overall_roi = (total_profit / total_wagered * 100) if total_wagered > 0 else 0
            
            analysis['bet_type_performance'][bet_type] = {
                'total_bets': total_bets,
                'win_rate': overall_win_rate,
                'roi': overall_roi,
                'total_profit': total_profit,
                'has_edge': overall_roi > 0 and overall_win_rate > 50
            }
            
            logger.info(
                f"   {bet_type}: "
                f"{overall_win_rate:.1f}% win rate, "
                f"{overall_roi:+.1f}% ROI, "
                f"{total_bets} bets"
            )
        
        # Rank bet types by ROI
        sorted_types = sorted(
            analysis['bet_type_performance'].items(),
            key=lambda x: x[1]['roi'],
            reverse=True
        )
        
        analysis['best_bet_types'] = [
            {'bet_type': bt, **stats}
            for bt, stats in sorted_types[:3]  # Top 3
        ]
        
        analysis['worst_bet_types'] = [
            {'bet_type': bt, **stats}
            for bt, stats in sorted_types[-3:]  # Bottom 3
        ]
        
        # Generate recommendations
        recommendations = []
        
        # Find bet types with edge
        edge_types = [
            (bt, stats) for bt, stats in analysis['bet_type_performance'].items()
            if stats['has_edge']
        ]
        
        if edge_types:
            recommendations.append(
                f"✅ Bet types with edge: {', '.join([bt for bt, _ in edge_types])}"
            )
        else:
            recommendations.append(
                "⚠️ No bet types show clear edge - may need more data or different strategy"
            )
        
        # Recommend avoiding bet types without edge
        no_edge_types = [
            bt for bt, stats in analysis['bet_type_performance'].items()
            if not stats['has_edge']
        ]
        if no_edge_types:
            recommendations.append(
                f"❌ Avoid these bet types in playoffs: {', '.join(no_edge_types)}"
            )
        
        analysis['recommendations'] = recommendations
        
        return analysis
    
    def save_results(
        self,
        all_results: Dict[int, Dict[str, PlayoffBacktestResult]],
        analysis: Dict[str, Any]
    ):
        """Save backtest results to files."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save detailed results
        results_file = self.results_dir / f"playoff_backtest_results_{timestamp}.json"
        results_data = {}
        
        for season, round_results in all_results.items():
            season_data = {}
            for round_name, result in round_results.items():
                season_data[round_name] = {
                    'season': result.season,
                    'round': result.round_name,
                    'total_games': result.total_games,
                    'games_tested': result.games_tested,
                    'bet_types': {
                        bt: {
                            'total_bets': r.total_bets,
                            'wins': r.wins,
                            'losses': r.losses,
                            'win_rate': r.win_rate,
                            'roi': r.roi,
                            'total_profit': r.total_profit,
                            'has_edge': r.has_edge
                        }
                        for bt, r in result.bet_type_results.items()
                    }
                }
            results_data[str(season)] = season_data
        
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        logger.info(f"💾 Saved results to {results_file}")
        
        # Save analysis
        analysis_file = self.results_dir / f"playoff_backtest_analysis_{timestamp}.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        logger.info(f"💾 Saved analysis to {analysis_file}")
        
        # Generate summary report
        report_file = self.results_dir / f"playoff_backtest_report_{timestamp}.md"
        self._generate_report(report_file, all_results, analysis)
        logger.info(f"📄 Generated report: {report_file}")
    
    def _generate_report(
        self,
        report_file: Path,
        all_results: Dict[int, Dict[str, PlayoffBacktestResult]],
        analysis: Dict[str, Any]
    ):
        """Generate markdown report of findings."""
        with open(report_file, 'w') as f:
            f.write("# Playoff Bet Type Backtesting Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Summary\n\n")
            f.write("This report analyzes which bet types have edge in playoff games.\n\n")
            
            f.write("## Bet Type Performance\n\n")
            for bet_type, stats in analysis['bet_type_performance'].items():
                f.write(f"### {bet_type.title()}\n\n")
                f.write(f"- **Total Bets:** {stats['total_bets']}\n")
                f.write(f"- **Win Rate:** {stats['win_rate']:.1f}%\n")
                f.write(f"- **ROI:** {stats['roi']:+.1f}%\n")
                f.write(f"- **Total Profit:** ${stats['total_profit']:.2f}\n")
                f.write(f"- **Has Edge:** {'✅ Yes' if stats['has_edge'] else '❌ No'}\n\n")
            
            f.write("## Recommendations\n\n")
            for rec in analysis['recommendations']:
                f.write(f"- {rec}\n")
            f.write("\n")
            
            f.write("## Best Bet Types\n\n")
            for bt_data in analysis['best_bet_types']:
                f.write(f"- **{bt_data['bet_type']}**: {bt_data['roi']:+.1f}% ROI, "
                       f"{bt_data['win_rate']:.1f}% win rate\n")
            f.write("\n")
            
            f.write("## Implementation Notes\n\n")
            f.write("Use these findings to:\n")
            f.write("1. Prioritize bet types with edge for playoff games\n")
            f.write("2. Avoid bet types without edge\n")
            f.write("3. Adjust confidence/edge thresholds based on bet type\n")
            f.write("4. Focus on bet types where we've proven edge exists\n\n")


async def main():
    """Main backtesting function."""
    print("=" * 80)
    print("🔬 PLAYOFF BET TYPE BACKTESTING ENGINE")
    print("=" * 80)
    print()
    print("This engine tests which bet types have real edge in playoff games")
    print("using historical data. Results will guide playoff betting strategy.")
    print()
    
    backtester = PlayoffBetTypeBacktester()
    
    # Note: This is a framework - actual backtesting requires:
    # 1. Historical playoff game data with results
    # 2. Historical odds data for those games
    # 3. Implementation of bet outcome calculation
    # 
    # The research script (research_ncaa_playoff_patterns.py) should be run first
    # to collect the necessary data, then this backtester can use that data.
    
    print("⚠️  Backtesting requires historical playoff data.")
    print("   1. Run research script first to collect data:")
    print("      python3 scripts/research_ncaa_playoff_patterns.py")
    print("   2. Then run this backtester with that data")
    print()
    
    # TODO: Load historical playoff games from research results
    # TODO: Load historical odds data (if available)
    # TODO: Run actual backtesting
    
    print("✅ Backtesting framework ready - needs historical data to run")


if __name__ == "__main__":
    asyncio.run(main())


