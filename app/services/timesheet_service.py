from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models.timesheet import TimesheetEntry
from datetime import datetime, timedelta
from typing import List, Dict, Any


class TimesheetService:
    @staticmethod
    def create_entry(
        db: Session,
        user_id: str,
        username: str,
        channel_id: str,
        client_name: str,
        hours: float,
        proof_url: str = None
    ) -> TimesheetEntry:
        entry = TimesheetEntry(
            user_id=user_id,
            username=username,
            channel_id=channel_id,
            client_name=client_name,
            hours=hours,
            proof_url=proof_url
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
    
    @staticmethod
    def get_weekly_entries(db: Session) -> List[Dict[str, Any]]:
        week_start = datetime.now() - timedelta(days=datetime.now().weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        entries = db.query(TimesheetEntry).filter(
            TimesheetEntry.submission_date >= week_start
        ).all()
        
        return [
            {
                'username': e.username,
                'client_name': e.client_name,
                'hours': e.hours,
                'proof_url': e.proof_url,
                'submission_date': e.submission_date.strftime('%Y-%m-%d %H:%M')
            }
            for e in entries
        ]
    
    @staticmethod
    def get_monthly_entries(db: Session) -> List[Dict[str, Any]]:
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        entries = db.query(TimesheetEntry).filter(
            TimesheetEntry.submission_date >= month_start
        ).all()
        
        return [
            {
                'username': e.username,
                'client_name': e.client_name,
                'hours': e.hours,
                'proof_url': e.proof_url,
                'submission_date': e.submission_date.strftime('%Y-%m-%d %H:%M')
            }
            for e in entries
        ]
    
    @staticmethod
    def get_user_entries(db: Session, user_id: str, days: int = 7) -> List[TimesheetEntry]:
        cutoff_date = datetime.now() - timedelta(days=days)
        return db.query(TimesheetEntry).filter(
            TimesheetEntry.user_id == user_id,
            TimesheetEntry.submission_date >= cutoff_date
        ).all()