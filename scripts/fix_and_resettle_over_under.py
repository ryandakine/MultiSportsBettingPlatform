#!/usr/bin/env python3
"""
Fix and Re-settle Over/Under Bets
==================================
Learn from bad data: Fix mislabeled bets and re-settle them correctly.
"""

import asyncio
import sys
sys.path.insert(0, '.')

from src.db.database import AsyncSessionLocal
from sqlalchemy import text
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def fix_and_resettle():
    """Fix data issues and re-settle over/under bets correctly."""
    async with AsyncSessionLocal() as db:
        # Get all over/under bets
        result = await db.execute(text("""
            SELECT id, status, sport, team, line, home_team, away_team, game_date
            FROM bets
            WHERE bet_type IN ('over_under', 'total')
            ORDER BY placed_at
        """))
        
        bets = [dict(row._mapping) for row in result.fetchall()]
        logger.info(f"🔍 Analyzing {len(bets)} over/under bets")
        
        fixed = 0
        needs_resettlement = []
        
        for bet in bets:
            issues = []
            fixes = {}
            
            # Issue 1: Negative line means this is a SPREAD bet, not over/under
            if bet['line'] is not None and bet['line'] < 0:
                issues.append(f"Negative line ({bet['line']}) - this is a SPREAD bet")
                # Fix: Change bet_type to spread
                fixes['bet_type'] = 'spread'
                needs_resettlement.append((bet['id'], 'spread'))
            
            # Issue 2: Missing line
            elif bet['line'] is None:
                issues.append("Missing line")
                # Can't fix without knowing the actual total line
                # Mark for review
                needs_resettlement.append((bet['id'], 'needs_line'))
            
            # Issue 3: Team field has team name instead of Over/Under
            elif bet['team'] and bet['team'].lower() not in ['over', 'under', 'o', 'u']:
                issues.append(f"Team field has '{bet['team']}' instead of Over/Under")
                # Can't auto-fix - we don't know if it should be over or under
                needs_resettlement.append((bet['id'], 'needs_direction'))
            
            if issues:
                logger.info(f"📋 Bet {bet['id'][:8]}... issues: {', '.join(issues)}")
                
                # Apply fixes
                if fixes:
                    if 'bet_type' in fixes:
                        await db.execute(text("""
                            UPDATE bets SET bet_type = :bet_type
                            WHERE id = :id
                        """), {"bet_type": fixes['bet_type'], "id": bet['id']})
                        logger.info(f"   ✅ Fixed: Changed to {fixes['bet_type']}")
                        fixed += 1
        
        await db.commit()
        logger.info(f"\n✅ Fixed {fixed} bets (changed mislabeled spread bets)")
        logger.info(f"📊 {len(needs_resettlement)} bets need manual review/resettlement")
        
        # Summary of what we learned
        logger.info("\n📚 LESSONS LEARNED:")
        logger.info("   1. Over/under bets MUST have positive line values (totals)")
        logger.info("   2. Over/under team field MUST be 'Over' or 'Under'")
        logger.info("   3. Never place over/under bets without a total line")
        logger.info("   4. Validation needed in betting engine to prevent bad data")

if __name__ == "__main__":
    asyncio.run(fix_and_resettle())


