from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.slack_service import SlackService
from app.services.timesheet_service import TimesheetService
from app.utils.block_builder import BlockBuilder
from app.config import get_settings
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class CommandHandler:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.slack_service = SlackService()
        self.block_builder = BlockBuilder()
    
    async def handle_timesheet_command(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Show initial form
        blocks = self.block_builder.build_initial_form()
        
        return {
            "response_type": "ephemeral",
            "blocks": blocks,
            "text": "Fill your timesheet"
        }
    
    async def handle_weekly_report(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        user_id = payload.get('user_id')
        
        # Check if user is manager
        if user_id != settings.slack_manager_user_id:
            return {
                "response_type": "ephemeral",
                "text": "⚠️ You don't have permission to view reports."
            }
        
        # Get weekly entries
        entries = TimesheetService.get_weekly_entries(self.db)
        blocks = self.block_builder.build_report_blocks(
            entries,
            "📊 Weekly Timesheet Report"
        )
        
        return {
            "response_type": "ephemeral",
            "blocks": blocks,
            "text": "Weekly Report"
        }
    
    async def handle_monthly_report(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        user_id = payload.get('user_id')
        
        # Check if user is manager
        if user_id != settings.slack_manager_user_id:
            return {
                "response_type": "ephemeral",
                "text": "⚠️ You don't have permission to view reports."
            }
        
        # Get monthly entries
        entries = TimesheetService.get_monthly_entries(self.db)
        blocks = self.block_builder.build_report_blocks(
            entries,
            "📊 Monthly Timesheet Report"
        )
        
        return {
            "response_type": "ephemeral",
            "blocks": blocks,
            "text": "Monthly Report"
        }

