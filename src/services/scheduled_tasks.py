"""
Scheduled Tasks Service
=======================
Background tasks that run on a schedule.
"""

import asyncio
import logging
import subprocess
import sys
import os
from datetime import datetime, time, timedelta
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ScheduledTasksService:
    """
    Service to manage scheduled background tasks.
    
    Currently manages:
    - Automatic bet settlement
    """
    
    def __init__(self):
        self.settlement_task: Optional[asyncio.Task] = None
        self.prediction_generation_task: Optional[asyncio.Task] = None
        self.running = False
    
    async def start(self):
        """Start all scheduled tasks."""
        if self.running:
            logger.warning("⚠️ Scheduled tasks already running")
            return
        
        self.running = True
        logger.info("🚀 Starting scheduled tasks service")
        
        # Start bet settlement task (runs hourly)
        self.settlement_task = asyncio.create_task(self._settlement_loop())
        logger.info("✅ Bet settlement task started (runs every hour)")
        
        # Start daily prediction generation task (runs once per day)
        self.prediction_generation_task = asyncio.create_task(self._daily_prediction_generation_loop())
        logger.info("✅ Daily prediction generation task started (runs once per day)")
    
    async def stop(self):
        """Stop all scheduled tasks."""
        self.running = False
        
        if self.settlement_task:
            self.settlement_task.cancel()
            try:
                await self.settlement_task
            except asyncio.CancelledError:
                pass
        
        if self.prediction_generation_task:
            self.prediction_generation_task.cancel()
            try:
                await self.prediction_generation_task
            except asyncio.CancelledError:
                pass
        
        logger.info("🛑 Scheduled tasks stopped")
    
    async def _settlement_loop(self):
        """Background loop to settle bets periodically."""
        from src.services.bet_settlement_service import bet_settlement_service
        
        # Run settlement every hour
        SETTLEMENT_INTERVAL = 3600  # 1 hour in seconds
        
        logger.info("🔄 Bet settlement loop started (runs every hour)")
        
        while self.running:
            try:
                # Run settlement for bets from last 7 days
                logger.info("⏰ Running scheduled bet settlement...")
                result = await bet_settlement_service.settle_pending_bets(days_back=7)
                
                logger.info(
                    f"✅ Settlement complete: {result['bets_settled']} settled "
                    f"({result['bets_won']} won, {result['bets_lost']} lost, "
                    f"{result['bets_pushed']} pushed)"
                )
                
                # Wait for next interval
                await asyncio.sleep(SETTLEMENT_INTERVAL)
                
            except asyncio.CancelledError:
                logger.info("🛑 Settlement loop cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Error in settlement loop: {e}")
                # Wait a bit before retrying on error
                await asyncio.sleep(300)  # 5 minutes
    
    async def _daily_prediction_generation_loop(self):
        """Background loop to generate predictions daily."""
        # Run prediction generation daily at 8 AM UTC (adjust as needed)
        # This ensures predictions exist for today's games before betting starts
        
        logger.info("🔄 Daily prediction generation loop started")
        
        # Run immediately on first start if it's past 8 AM UTC
        first_run = True
        
        while self.running:
            try:
                now = datetime.utcnow()
                
                if first_run:
                    # On first start, check if we should run immediately
                    today_8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
                    if now >= today_8am:
                        # It's past 8 AM today, run immediately
                        logger.info("⏰ It's past 8 AM UTC - running prediction generation immediately...")
                        await self._generate_predictions()
                        first_run = False
                        
                        # Then schedule for tomorrow at 8 AM
                        tomorrow_8am = today_8am + timedelta(days=1)
                        seconds_until_target = (tomorrow_8am - now).total_seconds()
                        logger.info(
                            f"⏰ Next prediction generation scheduled for: {tomorrow_8am.strftime('%Y-%m-%d %H:%M:%S')} UTC "
                            f"({seconds_until_target/3600:.1f} hours from now)"
                        )
                        await asyncio.sleep(seconds_until_target)
                        continue
                    else:
                        # It's before 8 AM, wait until 8 AM
                        seconds_until_target = (today_8am - now).total_seconds()
                        logger.info(
                            f"⏰ Next prediction generation scheduled for: {today_8am.strftime('%Y-%m-%d %H:%M:%S')} UTC "
                            f"({seconds_until_target/3600:.1f} hours from now)"
                        )
                        await asyncio.sleep(seconds_until_target)
                        first_run = False
                        continue
                
                # Regular daily execution at 8 AM UTC
                # Calculate next 8 AM UTC
                target_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
                if now >= target_time:
                    # Already past 8 AM today, schedule for tomorrow
                    target_time = target_time + timedelta(days=1)
                
                seconds_until_target = (target_time - now).total_seconds()
                
                logger.info(
                    f"⏰ Next prediction generation scheduled for: {target_time.strftime('%Y-%m-%d %H:%M:%S')} UTC "
                    f"({seconds_until_target/3600:.1f} hours from now)"
                )
                
                # Wait until target time
                await asyncio.sleep(seconds_until_target)
                
                # Run prediction generation
                logger.info("🎯 Running daily prediction generation...")
                await self._generate_predictions()
                
            except asyncio.CancelledError:
                logger.info("🛑 Prediction generation loop cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Error in prediction generation loop: {e}")
                import traceback
                traceback.print_exc()
                # Wait 1 hour before retrying on error
                await asyncio.sleep(3600)
    
    async def _generate_predictions(self):
        """Run the prediction generation script."""
        try:
            # Get the project root directory
            project_root = Path(__file__).parent.parent.parent
            script_path = project_root / "scripts" / "generate_predictions_with_betting_metadata.py"
            
            if not script_path.exists():
                logger.error(f"❌ Prediction generation script not found: {script_path}")
                return
            
            # Set PYTHONPATH to include project root
            env = os.environ.copy()
            env["PYTHONPATH"] = str(project_root)
            
            # Run the script
            logger.info(f"📝 Executing: {script_path}")
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                str(script_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                cwd=str(project_root)
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info("✅ Prediction generation completed successfully")
                if stdout:
                    logger.debug(f"Output: {stdout.decode()[:500]}")  # First 500 chars
            else:
                logger.error(f"❌ Prediction generation failed with code {process.returncode}")
                if stderr:
                    logger.error(f"Error: {stderr.decode()[:1000]}")  # First 1000 chars
                    
        except Exception as e:
            logger.error(f"❌ Error running prediction generation: {e}")
            import traceback
            traceback.print_exc()


# Global instance
scheduled_tasks_service = ScheduledTasksService()

