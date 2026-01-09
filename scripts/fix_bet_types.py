#!/usr/bin/env python3
"""
Fix Bet Types
=============
Fix bet_type='total' to be 'over_under' in database
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.db.database import AsyncSessionLocal
from sqlalchemy import text


async def fix_bet_types():
    """Fix bet_type='total' to 'over_under'."""
    print("Fixing bet_type='total' to 'over_under'...")
    
    async with AsyncSessionLocal() as db:
        # Update all bets with bet_type='total' to 'over_under'
        result = await db.execute(
            text("UPDATE bets SET bet_type = 'over_under' WHERE bet_type = 'total'")
        )
        await db.commit()
        
        print(f"✅ Fixed {result.rowcount} bets")


if __name__ == "__main__":
    asyncio.run(fix_bet_types())



