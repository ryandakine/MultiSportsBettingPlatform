#!/usr/bin/env python3
"""
Fix Bet Status Case Mismatch
=============================
Convert all bet status values in the database to lowercase to match the enum.
"""

import asyncio
import sys
sys.path.insert(0, '.')

from src.db.database import AsyncSessionLocal, engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def fix_bet_status_case():
    """Convert all bet status values to lowercase."""
    logger.info("🔧 Starting bet status case fix...")
    
    async with AsyncSessionLocal() as db:
        try:
            # Check current status distribution
            result = await db.execute(text("SELECT status, COUNT(*) FROM bets GROUP BY status"))
            logger.info("📊 Current status distribution:")
            for row in result.fetchall():
                logger.info(f"   {row[0]}: {row[1]}")
            
            # Update all status values to lowercase
            updates = {
                'PENDING': 'pending',
                'WON': 'won',
                'LOST': 'lost',
                'PUSHED': 'pushed',
                'CANCELLED': 'cancelled'
            }
            
            total_updated = 0
            for old_status, new_status in updates.items():
                result = await db.execute(
                    text("UPDATE bets SET status = :new WHERE status = :old"),
                    {"new": new_status, "old": old_status}
                )
                count = result.rowcount
                if count > 0:
                    logger.info(f"✅ Updated {count} bets from '{old_status}' to '{new_status}'")
                    total_updated += count
            
            await db.commit()
            logger.info(f"✅ Successfully updated {total_updated} bets")
            
            # Verify the fix
            result = await db.execute(text("SELECT status, COUNT(*) FROM bets GROUP BY status"))
            logger.info("📊 Updated status distribution:")
            for row in result.fetchall():
                logger.info(f"   {row[0]}: {row[1]}")
            
            # Check for any remaining uppercase
            result = await db.execute(
                text("SELECT COUNT(*) FROM bets WHERE status IN ('PENDING', 'WON', 'LOST', 'PUSHED', 'CANCELLED')")
            )
            remaining = result.scalar()
            if remaining > 0:
                logger.warning(f"⚠️  Warning: {remaining} bets still have uppercase status values")
            else:
                logger.info("✅ All status values are now lowercase")
                
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Error fixing bet status case: {e}", exc_info=True)
            raise


if __name__ == "__main__":
    asyncio.run(fix_bet_status_case())


