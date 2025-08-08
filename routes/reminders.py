# routes/reminders.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from database.db import get_db
from modules.users import get_user_or_404
from modules.reminders import (
    create_reminder,
    get_upcoming_reminders,
    mark_reminder_completed,
    delete_reminder
)

router = APIRouter()


@router.post("/create")
def api_create_reminder(
    user_id: int,
    text: str,
    time: datetime,
    db: Session = Depends(get_db)
):
    user = get_user_or_404(user_id, db)
    reminder = create_reminder(db, user.id, text, time)
    return {"status": "ok", "id": reminder.id}


@router.get("/list")
def api_get_reminders(
    user_id: int,
    db: Session = Depends(get_db)
):
    get_user_or_404(user_id, db)
    reminders = get_upcoming_reminders(db, user_id)
    return [
        {
            "id": r.id,
            "text": r.text,
            "time": r.time,
            "seen": r.is_seen,
            "played": r.is_played,
            "completed": r.is_completed
        }
        for r in reminders
    ]


@router.patch("/complete")
def api_complete_reminder(
    reminder_id: int,
    db: Session = Depends(get_db)
):
    mark_reminder_completed(db, reminder_id)
    return {"status": "completed"}


@router.delete("/delete")
def api_delete_reminder(
    reminder_id: int,
    db: Session = Depends(get_db)
):
    delete_reminder(db, reminder_id)
    return {"status": "deleted"}