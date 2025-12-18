#!/usr/bin/env python3
"""
Settle Bets Script
==================
Command-line script to settle pending bets.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from src.services.bet_settlement_service import bet_settlement_service


async def main():
    """Settle pending bets."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Settle pending bets")
    parser.add_argument("--days", type=int, default=7, help="Number of days to look back (default: 7)")
    
    args = parser.parse_args()
    
    print(f"🔍 Settling bets from the last {args.days} days...")
    
    try:
        result = await bet_settlement_service.settle_pending_bets(days_back=args.days)
        
        print("\n" + "=" * 80)
        print("✅ SETTLEMENT COMPLETE")
        print("=" * 80)
        print(f"Bets Checked:  {result['bets_checked']}")
        print(f"Bets Settled:  {result['bets_settled']}")
        print(f"  - Won:       {result['bets_won']}")
        print(f"  - Lost:      {result['bets_lost']}")
        print(f"  - Pushed:    {result['bets_pushed']}")
        print(f"Bets Skipped:  {result['bets_skipped']}")
        
        if result.get('errors'):
            print(f"\n⚠️  Errors: {len(result['errors'])}")
            for error in result['errors']:
                print(f"  - {error}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

