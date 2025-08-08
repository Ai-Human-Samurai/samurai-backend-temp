from core.config import settings
from database.models import Log
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

EMOTION_EVENT = "empathy_call"

def count_emotional_appeals(db: Session, user_id: int) -> int:
   
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)

    return db.query(Log).filter(
        Log.user_id == user_id,
        Log.event == EMOTION_EVENT,
        Log.timestamp >= one_hour_ago
    ).count()


def should_block_emotion(db: Session, user_id: int) -> bool:
    
    return count_emotional_appeals(db, user_id) >= settings.EMOTION_THRESHOLD


def log_emotional_appeal(db: Session, user_id: int, detail: str = "") -> None:
   
    log = Log(
        user_id=user_id,
        event=EMOTION_EVENT,
        detail=detail,
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()
