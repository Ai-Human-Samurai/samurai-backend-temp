from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from modules.users import get_or_create_user, get_user_or_404
from modules.behavior.style_map import resolve_style
from database.models import User
from datetime import datetime
from core.config import AVAILABLE_VOICES, FREE_VOICE
from pydantic import BaseModel

router = APIRouter(prefix="", tags=["User"])

# ✅ Регистрация нового пользователя
@router.post("/register")
def register_user(
    lang: str = Query(default="ru"),
    style: str = Query(default="дружественный"),
    db: Session = Depends(get_db)
):
    resolved_style = resolve_style(style, lang)

    user = User(
        language=lang,
        style=resolved_style,
        created_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "id": user.id, 
        "style": user.style,
        "is_pro": user.is_pro,
        "pro_until": user.pro_until
    }

# ✅ Получить профиль пользователя
@router.get("/profile")
def get_user_profile(
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    user = get_user_or_404(user_id, db)
    return {
        "id": user.id,
        "language": user.language,
        "style": user.style,
        "voice": user.voice,
        "is_pro": user.is_pro,
        "pro_until": user.pro_until
    }

# ✅ Список доступных голосов
@router.get("/voices/list")
def list_voices():
    return [
        {"name": voice, "is_premium": voice != FREE_VOICE}
        for voice in AVAILABLE_VOICES
    ]

# ✅ Обновление настроек (голос)
class SettingsUpdate(BaseModel):
    voice: str

@router.patch("/user/settings")
def update_user_settings(
    payload: SettingsUpdate,
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    user = get_user_or_404(user_id, db)
    user.voice = payload.voice
    db.commit()
    return {"status": "ok", "voice": user.voice}