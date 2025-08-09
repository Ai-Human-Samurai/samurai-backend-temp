# routes/sos.py
# All comments in English

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.db import get_db
from modules.users import get_or_create_user
from modules.behavior.sos import trigger_sos_response
from prompts import load_prompts

router = APIRouter()


@router.post("/sos/trigger")
def sos_trigger(
    user_id: int,
    db: Session = Depends(get_db),
):
    # Ensure user exists and fetch language
    user = get_or_create_user(user_id, db)
    lang = getattr(user, "language", None) or "ru"

    store = load_prompts(lang)
    prompt = store.get("sos", {})  # to read SOS_TOO_SOON if needed

    # Note: trigger_sos_response signature must match your implementation
    result = trigger_sos_response(user_id=user_id, lang=lang, style=None, db=db)

    if result.get("blocked"):
        return {
            "ok": False,
            "reason": "blocked",
            "message": prompt.get("SOS_TOO_SOON", "Я рядом."),
        }

    return {
        "ok": True,
        "text": result["text"],
        "mp3": result["path"],
    }