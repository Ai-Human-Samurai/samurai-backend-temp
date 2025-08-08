from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from modules.users import get_or_create_user
from modules.behavior.sos import trigger_sos_response
from prompts import load_prompts

router = APIRouter()


@router.post("/sos/trigger")
def sos_trigger(
    user_id: int = Depends(get_or_create_user),
    db: Session = Depends(get_db)
):
    """
    Triggers a voice-based SOS response (1–2 короткие фразы поддержки).
    Может быть заблокировано при частом повторе.
    """
    # Получаем пользователя и язык
    from modules.users import get_user_by_id
    user = get_user_by_id(user_id, db)
    lang = user.language if user and user.language else "ru"
    PROMPT = load_prompts(lang).get("sos", {})

    result = trigger_sos_response(user_id=user_id, db=db)

    if result.get("blocked"):
        return {
            "ok": False,
            "reason": "blocked",
            "message": PROMPT.get("SOS_TOO_SOON", "I'm here.")
        }

    return {
        "ok": True,
        "text": result["text"],
        "mp3": result["path"]
    }