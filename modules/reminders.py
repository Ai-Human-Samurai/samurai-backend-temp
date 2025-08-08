from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from database.models import Reminder
from core.config import settings


def create_reminder(db: Session, user_id: int, text: str, time: datetime) -> Reminder:
    
    reminder = Reminder(
        user_id=user_id,
        text=text,
        time=time,
        created_at=datetime.utcnow()
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


def get_upcoming_reminders(db: Session, user_id: int) -> list[Reminder]:
    
    now = datetime.utcnow()
    return db.query(Reminder).filter(
        Reminder.user_id == user_id,
        Reminder.time >= now,
        Reminder.is_completed == False
    ).all()


def get_active_reminders(db: Session) -> list[Reminder]:
    
    now = datetime.utcnow()
    return db.query(Reminder).filter(
        Reminder.time <= now,
        Reminder.is_completed == False,
        Reminder.is_played == False
    ).all()


def mark_reminder_seen(db: Session, reminder_id: int) -> None:
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if reminder:
        reminder.is_seen = True
        db.commit()


def mark_reminder_played(db: Session, reminder_id: int) -> None:
    
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if reminder:
        reminder.is_played = True
        db.commit()


def mark_reminder_completed(db: Session, reminder_id: int) -> None:
    
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if reminder:
        reminder.is_completed = True
        db.commit()


def auto_postpone_reminder(db: Session, reminder_id: int) -> None:
    
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if reminder and not reminder.is_completed:
        reminder.time += timedelta(minutes=settings.REMINDER_AUTO_POSTPONE_MINUTES)
        db.commit()


def delete_reminder(db: Session, reminder_id: int) -> None:
    
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if reminder:
        db.delete(reminder)
        db.commit()
