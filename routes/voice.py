from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.db import get_db

from modules.voice_engine import play_or_generate_voice
from modules.behavior.style_map import resolve_style
from modules.users import get_or_create_user
from prompts import load_prompts
import os

router = APIRouter()


class VoiceRequest(BaseModel):
    user_id: int
    text: str | None = None     # free text to TTS
    intent: str | None = None   # intent key from prompts/behavior
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
    """
    Generate or play a voice response.
    - If `intent` is provided: choose phrase by intent key and TTS it (with caching).
    - Else if `text` is provided: TTS the provided text (with caching).
    Returns a JSON with status, path (mp3 url) or text fallback.
    """
    user = get_or_create_user(payload.user_id, db)
    lang = (payload.lang or user.language or "ru").strip()
    style = resolve_style((payload.style or user.style or "дружественный"), lang)
    prompts = load_prompts(lang)

    # ---- Intent Mode -------------------------------------------------------
    if payload.intent:
        # Route intent through the unified engine (engine picks phrase from prompts internally)
        try:
            result = play_or_generate_voice(
                user_id=payload.user_id,
                key=payload.intent,
                lang=lang,
                style=style,
                db=db,
            )
        except Exception as e:
            # Unexpected failure in engine
            raise HTTPException(
                status_code=500,
                detail=prompts.get("system", {}).get("GENERATION_FAILED", "Generation failed"),
            ) from e

        if not result or (not result.get("path") and not result.get("text")):
            # Engine returned nothing useful
            raise HTTPException(
                status_code=400,
                detail=prompts.get("system", {}).get("GENERATION_FAILED", "Generation failed"),
            )

        return VoiceResponse(
            status="ok",
            path=_url_from_path(result.get("path")) if result.get("path") else None,
            text=result.get("text"),
            intent=payload.intent,
            message=result.get("message", ""),
        )

    # ---- Text Mode ---------------------------------------------------------
    if payload.text is not None:
        text = payload.text.strip()
        if not text:
            raise HTTPException(
                status_code=400,
                detail=prompts.get("system", {}).get("NO_TEXT_PROVIDED", "No text provided"),
            )

        # Lightweight route-level filter (optional; engine has its own guards)
        if is_text_blocked(payload.user_id, text, lang):
            raise HTTPException(
                status_code=403,
                detail=prompts.get("system", {}).get("TEXT_BLOCKED", "Text blocked"),
            )

        try:
            result = play_or_generate_voice(
                user_id=payload.user_id,
                text=text,
                lang=lang,
                style=style,
                db=db,
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=prompts.get("system", {}).get("GENERATION_FAILED", "Generation failed"),
            ) from e

        if not result or (not result.get("path") and not result.get("text")):
            raise HTTPException(
                status_code=400,
                detail=prompts.get("system", {}).get("GENERATION_FAILED", "Generation failed"),
            )

        return VoiceResponse(
            status="ok",
            path=_url_from_path(result.get("path")) if result.get("path") else None,
            text=result.get("text"),
            intent=None,
            message=result.get("message", ""),
        )

    # ---- No text and no intent --------------------------------------------
    raise HTTPException(
        status_code=400,
        detail=prompts.get("system", {}).get("NO_TEXT_OR_INTENT", "No text or intent provided"),
    )


# ---------- Utils -----------------------------------------------------------

def _url_from_path(path: str | None) -> str | None:
    """
    Convert absolute/relative fs path to public URL.
    You mounted StaticFiles(directory=voice_cache_dir) at /static.
    So files inside voice_cache_dir are available at /static/<filename>.
    """
    if not path:
        return None
    filename = os.path.basename(path)
    return f"/static/{filename}"


def is_text_blocked(user_id: int, text: str, lang: str = "ru", db=None) -> bool:
    """
    Route-level lightweight filter (can be relaxed or removed).
    Engine has its own filters; this is just a pre-check.
    """
    p = load_prompts(lang)
    bad_words = p.get("filters", {}).get("BAD_WORDS", [])
    lower = text.lower()
    return any(w in lower for w in bad_words)