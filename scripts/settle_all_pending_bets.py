#!/usr/bin/env python3
"""
Settle All Pending Bets
=======================
Settle all pending bets in the database, regardless of date.
"""

import asyncio
import sys
sys.path.insert(0, '.')

from src.services.bet_settlement_service import bet_settlement_service
from src.db.database import AsyncSessionLocal
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def settle_all_pending():
    """Settle all pending bets."""
    logger.info("🎯 Starting settlement of all pending bets...")
    
    # First, check how many pending bets we have
    async with AsyncSessionLocal() as db:
        result = await db.execute(text("SELECT COUNT(*) FROM bets WHERE status = 'pending'"))
        pending_count = result.scalar()
        logger.info(f"📊 Found {pending_count} pending bets")
        
        if pending_count == 0:
            logger.info("✅ No pending bets to settle")
            return
    
    # Settle with a large lookback window (90 days should cover everything)
    logger.info("🚀 Starting settlement process (looking back 90 days)...")
    result = await bet_settlement_service.settle_pending_bets(days_back=90)
    
    logger.info("=" * 60)
    logger.info("📊 SETTLEMENT SUMMARY")
    logger.info("=" * 60)
    logger.info(f"✅ Bets checked: {result['bets_checked']}")
    logger.info(f"✅ Bets settled: {result['bets_settled']}")
    logger.info(f"✅ Bets won: {result['bets_won']}")
    logger.info(f"❌ Bets lost: {result['bets_lost']}")
    logger.info(f"🔄 Bets pushed: {result['bets_pushed']}")
    logger.info(f"⏭️  Bets skipped: {result['bets_skipped']}")
    
    if result['errors']:
        logger.warning(f"⚠️  Errors encountered: {len(result['errors'])}")
        for error in result['errors'][:10]:  # Show first 10 errors
            logger.warning(f"   - {error}")
    
    # Check final status
    async with AsyncSessionLocal() as db:
        result = await db.execute(text("SELECT status, COUNT(*) FROM bets GROUP BY status"))
        logger.info("\n📊 Final bet status distribution:")
        for row in result.fetchall():
            logger.info(f"   {row[0]}: {row[1]}")


if __name__ == "__main__":
    asyncio.run(settle_all_pending())
