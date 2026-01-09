#!/usr/bin/env python3
"""
Fix Bet Type Case
=================
Fix uppercase bet_type values to lowercase to match enum.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.db.database import AsyncSessionLocal
from sqlalchemy import text


async def fix_case():
    """Fix bet_type case to match enum."""
    print("Fixing bet_type values to lowercase...")
    
    mapping = {
        'OVER_UNDER': 'over_under',
        'MONEYLINE': 'moneyline',
        'SPREAD': 'spread',
        'PARLAY': 'parlay',
        'PROP': 'prop',
        'TOTAL': 'over_under'  # TOTAL is alias for over_under
    }
    
    async with AsyncSessionLocal() as db:
        for old, new in mapping.items():
            result = await db.execute(
                text(f"UPDATE bets SET bet_type = :new WHERE bet_type = :old"),
                {"old": old, "new": new}
            )
            if result.rowcount > 0:
                print(f"  Fixed {result.rowcount} bets: {old} -> {new}")
        
        await db.commit()
        print("✅ All bet_type values fixed!")


if __name__ == "__main__":
    asyncio.run(fix_case())



