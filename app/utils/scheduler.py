from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.slack_service import SlackService
from app.database import SessionLocal
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)


class TaskScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        # self.slack_service = SlackService()
    
    def start(self):
        # Weekly reminder every Friday at 10 AM
        self.scheduler.add_job(
            self.send_weekly_reminder,
            CronTrigger(day_of_week='fri', hour=10, minute=0),
            id='weekly_reminder'
        )
        
        # Monthly report on last day of month at 5 PM
        self.scheduler.add_job(
            self.send_monthly_summary,
            CronTrigger(day='last', hour=17, minute=0),
            id='monthly_summary'
        )
        
        self.scheduler.start()
        logger.info("Scheduler started")
    
    def stop(self):
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
    
    async def send_weekly_reminder(self):
        try:
            db = SessionLocal()
            
            # Get all channels where bot is present
            result = db.execute(text("SELECT DISTINCT channel_id FROM timesheet_entries"))
            channels = [row[0] for row in result]
            
            reminder_blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "⏰ *Weekly Timesheet Reminder*\n\nDon't forget to fill your timesheet for this week!\nUse `/timesheet` command to submit."
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Fill Timesheet"},
                            "action_id": "open_timesheet_modal",
                            "style": "primary"
                        }
                    ]
                }
            ]
            
            for channel in channels:
                self.slack_service.post_message(
                    channel,
                    reminder_blocks,
                    "Time to fill your timesheet!"
                )
            
            db.close()
            logger.info(f"Weekly reminder sent to {len(channels)} channels")
        
        except Exception as e:
            logger.error(f"Error sending weekly reminder: {str(e)}")
    
    async def send_monthly_summary(self):
        try:
            from app.services.timesheet_service import TimesheetService
            from app.utils.block_builder import BlockBuilder
            from app.config import get_settings
            
            settings = get_settings()
            db = SessionLocal()
            
            # Get monthly entries
            entries = TimesheetService.get_monthly_entries(db)
            blocks = BlockBuilder.build_report_blocks(
                entries,
                "📊 Monthly Timesheet Summary"
            )
            
            # Send to manager
            self.slack_service.send_dm(
                settings.slack_manager_user_id,
                blocks,
                "Monthly Timesheet Summary"
            )
            
            db.close()
            logger.info("Monthly summary sent to manager")
        
        except Exception as e:
            logger.error(f"Error sending monthly summary: {str(e)}")