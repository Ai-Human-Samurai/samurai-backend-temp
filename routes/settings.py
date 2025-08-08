from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from core.config import settings
from database.db import get_db
from modules.users import get_or_create_user

router = APIRouter()

@router.get("/limits", tags=["settings"])
def get_limits(
    user_id: int = Query(default=None),
    lang: str = Query(default=None),
    db: Session = Depends(get_db)
):
    if not lang and user_id:
        user = get_or_create_user(user_id, db)
        lang = user.language

    lang = lang or "ru"

    return {
        "MAX_REMINDERS": settings.MAX_REMINDERS,
        "CACHE_PHRASE_LIMIT": settings.CACHE_PHRASE_LIMIT,
        "TTS_CACHE_LIMIT": settings.TTS_CACHE_LIMIT,
        "CHAT_SPAM_LIMIT": settings.CHAT_SPAM_LIMIT,
        "EMOTION_THRESHOLD": settings.EMOTION_THRESHOLD,
        "PRO_TRIAL_DAYS": settings.PRO_TRIAL_DAYS,
        "MAX_VOICE_TASKS_FREE": settings.MAX_VOICE_TASKS_FREE,
        "MAX_VOICE_TASKS_PRO": settings.MAX_VOICE_TASKS_PRO,
        "SOS_CALL_ENABLED": settings.SOS_CALL_ENABLED
    }