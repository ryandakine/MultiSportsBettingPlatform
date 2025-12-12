"""
Paper Trading Demo Script
=========================
Simulate bets with fake money to test the system.
"""

import asyncio
import random
from datetime import datetime, timedelta

from src.services.bet_tracker import bet_tracker
from src.db.models.bet import BetType


async def simulate_bet(user_id: str, sport: str, team: str, odds: float, amount: float):
    """Place a simulated paper trading bet."""
    
    bet_data = {
        "sportsbook": "paper_trading",
        "sport": sport,
        "game_id": f"game_{random.randint(1000, 9999)}",
        "bet_type": random.choice([BetType.MONEYLINE, BetType.SPREAD, BetType.OVER_UNDER]),
        "team": team,
        "line": random.choice([-7.5, -3.5, 220.5, 45.5]) if random.random() > 0.5 else None,
        "amount": amount,
        "odds": odds,
        "predicted_probability": random.uniform(0.50, 0.75),
        "predicted_edge": random.uniform(0.03, 0.12),
        "model_confidence": random.uniform(0.60, 0.85)
    }
    
    bet_id = await bet_tracker.place_bet(user_id, bet_data, is_autonomous=True)
    print(f"✅ Placed bet: {bet_id} | {team} @ {odds} | ${amount}")
    
    return bet_id


async def simulate_bet_settlement(bet_id: str, win: bool):
    """Simulate bet settlement (win or loss)."""
    from src.db.models.bet import BetStatus
    
    if win:
        await bet_tracker.update_bet_status(bet_id, BetStatus.WON)
        print(f"🎉 Bet {bet_id} WON!")
    else:
        await bet_tracker.update_bet_status(bet_id, BetStatus.LOST)
        print(f"❌ Bet {bet_id} LOST")


async def run_demo(user_id: str = "demo_user"):
    """Run paper trading demo with simulated bets."""
    
    print("🎯 Starting Paper Trading Demo")
    print("=" * 50)
    
    # Simulate 10 bets
    bet_ids = []
    
    games = [
        ("basketball", "Lakers", -150, 50),
        ("football", "Chiefs", -200, 75),
        ("basketball", "Celtics", +120, 40),
        ("football", "49ers", -110, 60),
        ("basketball", "Bucks", -180, 55),
        ("football", "Bills", +150, 45),
        ("basketball", "Nuggets", -130, 50),
        ("football", "Cowboys", -105, 65),
        ("basketball", "Warriors", +110, 35),
        ("football", "Eagles", -140, 70)
    ]
    
    for sport, team, odds, amount in games:
        bet_id = await simulate_bet(user_id, sport, team, odds, amount)
        bet_ids.append(bet_id)
        await asyncio.sleep(0.5)
    
    print("\n" + "=" * 50)
    print("⏳ Simulating game outcomes...")
    print("=" * 50 + "\n")
    
    await asyncio.sleep(2)
    
    # Simulate outcomes (60% win rate - profitable!)
    for bet_id in bet_ids:
        win = random.random() < 0.60  # 60% win rate
        await simulate_bet_settlement(bet_id, win)
        await asyncio.sleep(0.5)
    
    print("\n" + "=" * 50)
    print("📊 Calculating ROI...")
    print("=" * 50 + "\n")
    
    # Get ROI
    roi_data = await bet_tracker.calculate_roi(user_id)
    bankroll = await bet_tracker.get_bankroll(user_id)
    
    print(f"💰 PAPER TRADING RESULTS")
    print(f"   Total Bets: {roi_data['total_bets']}")
    print(f"   Wins: {roi_data['wins']} | Losses: {roi_data['losses']}")
    print(f"   Win Rate: {roi_data['win_rate']:.1f}%")
    print(f"   Total Wagered: ${roi_data['total_wagered']:.2f}")
    print(f"   Net Profit: ${roi_data['net_profit']:.2f}")
    print(f"   ROI: {roi_data['roi_percentage']:.2f}%")
    print(f"\n💵 BANKROLL STATUS")
    print(f"   Current Balance: ${bankroll['current_balance']:.2f}")
    print(f"   Available: ${bankroll['available_balance']:.2f}")
    
    print("\n✅ Demo complete! Check dashboard to see results.")


if __name__ == "__main__":
    asyncio.run(run_demo())
