from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from database.db import get_db
from modules.users import get_user_or_404
from database.models import CalendarEvent
from prompts import load_prompts

router = APIRouter(prefix="/calendar", tags=["calendar"])


# 📦 Модель для создания события
class CalendarEventCreate(BaseModel):
    title: str
    description: str = ""
    event_time: datetime


# ✅ Модель для возврата события
class CalendarEventOut(BaseModel):
    id: int
    title: str
    description: str
    event_time: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# 📥 Добавить событие
@router.post("/add", response_model=CalendarEventOut)
def add_event(
    event: CalendarEventCreate,
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    user = get_user_or_404(user_id, db)
    new_event = CalendarEvent(
        user_id=user.id,
        title=event.title,
        description=event.description,
        event_time=event.event_time,
        created_at=datetime.utcnow()
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event


# 📃 Получить список событий
@router.get("/list", response_model=List[CalendarEventOut])
def list_events(
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    _ = get_user_or_404(user_id, db)
    return db.query(CalendarEvent).filter_by(user_id=user_id).order_by(CalendarEvent.event_time).all()


# ❌ Удалить событие
@router.delete("/delete")
def delete_event(
    event_id: int = Query(...),
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    user = get_user_or_404(user_id, db)
    lang = user.language
    prompts = load_prompts(lang)

    event = db.query(CalendarEvent).filter_by(id=event_id, user_id=user.id).first()
    if not event:
        raise HTTPException(status_code=404, detail=prompts["system"].get("EVENT_NOT_FOUND", "Event not found"))

    db.delete(event)
    db.commit()
    return {"success": True, "deleted_id": event_id}