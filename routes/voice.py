from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.db import get_db
from modules.voice_module import generate_and_save_voice
from modules.voice_engine import play_or_generate_voice
from modules.behavior.style_map import resolve_style
from modules.users import get_or_create_user
from prompts import load_prompts
import os

router = APIRouter()


class VoiceRequest(BaseModel):
    user_id: int
    text: str | None = None
    intent: str | None = None
    lang: str | None = None
    style: str | None = None


class VoiceResponse(BaseModel):
    status: str
    path: str | None = None
    text: str | None = None
    intent: str | None = None
    message: str | None = None


@router.post("", response_model=VoiceResponse)
def generate_voice(payload: VoiceRequest, db: Session = Depends(get_db)):
    user = get_or_create_user(payload.user_id, db)
    lang = payload.lang or user.language
    style = resolve_style(payload.style or user.style, lang)
    prompts = load_prompts(lang)

    # 🎯 Intent mode
    if payload.intent:
        path = generate_and_save_voice(
            user_id=payload.user_id,
            intent=payload.intent,
            style=style,
            lang=lang,
            db=db
        )
        if path:
            return VoiceResponse(
                status="ok",
                path=_url_from_path(path),
                intent=payload.intent
            )
        raise HTTPException(status_code=400, detail=prompts["system"]["GENERATION_FAILED"])

    # 🧾 Text mode
    if payload.text:
        text = payload.text.strip()
        if not text:
            raise HTTPException(status_code=400, detail=prompts["system"]["NO_TEXT_PROVIDED"])

        if is_text_blocked(text, lang):
            raise HTTPException(status_code=403, detail=prompts["system"]["TEXT_BLOCKED"])

        result = play_or_generate_voice(
            user_id=payload.user_id,
            text=text,
            style=style,
            lang=lang,
            db=db
        )
        return VoiceResponse(**result)

    # ❌ No text and no intent
    raise HTTPException(status_code=400, detail=prompts["system"]["NO_TEXT_OR_INTENT"])


# 🧱 Util
def _url_from_path(path: str) -> str:
    filename = os.path.basename(path)
    return f"/static/voice_cache/{filename}"


# 🚫 Text filtering
def is_text_blocked(text: str, lang: str = "ru") -> bool:
    prompts = load_prompts(lang)
    bad_words = prompts["filters"]["BAD_WORDS"]
    text_lower = text.lower()
    return any(word in text_lower for word in bad_words)