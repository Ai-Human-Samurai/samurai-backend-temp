import os
import logging
from typing import Optional
from sqlalchemy.orm import Session

from modules.voice_module import generate_custom_voice, generate_and_save_voice
from modules.voice_cache import is_voice_cached, get_voice_cache_path
from modules.behavior.style_map import resolve_style, style_to_voice
from modules.behavior_engine import get_phrase
from modules.semantic_filter import is_text_blocked

logger = logging.getLogger("samurai.voice.engine")


def _url_from_path(path: str) -> str:
    # /static смонтирован на саму папку voice_cache → публикуем только имя файла
    filename = os.path.basename(path)
    return f"/static/{filename}"


def play_or_generate_voice(
    user_id: int,
    text: Optional[str] = None,
    intent: Optional[str] = None,
    lang: str = "ru",
    style: str = "дружественный",
    db: Optional[Session] = None,
) -> dict:
    """
    Единая точка TTS:
      1) фраза (если intent),
      2) фильтры,
      3) кэш (учитывает voice),
      4) генерация,
      5) {status, path?, text?, intent?, message?}
    """
    style = resolve_style(style, lang)
    phrase_text = (text or "").strip()

    # 1) Если нет явного текста — берём фразу по intent
    if not phrase_text and intent:
        try:
            data = get_phrase(style=style, intent=intent, lang=lang, user_id=user_id, db=db) or {}
            phrase_text = (data.get("text") or "").strip()
        except Exception as e:
            logger.error("get_phrase failed: %s", e)

    if not phrase_text:
        return {"status": "error", "message": "NO_TEXT_OR_INTENT", "path": None, "text": None, "intent": intent}

    # 2) Фильтры
    try:
        if is_text_blocked(user_id, phrase_text, lang=lang, db=db):
            return {"status": "forbidden", "message": "TEXT_BLOCKED", "path": None, "text": None, "intent": intent}
    except Exception as e:
        logger.error("is_text_blocked error: %s (fallback allow)", e)

    # 3) Кэш (учитывает voice)
    voice = style_to_voice(style, lang)
    try:
        if is_voice_cached(phrase_text, lang, voice):
            path = get_voice_cache_path(phrase_text, lang, voice)
            logger.info("Cache hit: %s", path)
            return {"status": "ok", "path": _url_from_path(path), "text": phrase_text, "intent": intent}
    except Exception as e:
        logger.error("Cache check error: %s", e)

    # 4) Генерация
    try:
        path = generate_and_save_voice(text=phrase_text, user_id=user_id, lang=lang, style=style)
        if path:
            return {"status": "ok", "path": _url_from_path(path), "text": phrase_text, "intent": intent}
        # Фолбэк — текст
        return {"status": "text", "path": None, "text": phrase_text, "intent": intent}
    except Exception as e:
        logger.error("TTS generation exception: %s", e)
        return {"status": "error", "message": "GENERATION_FAILED", "path": None, "text": phrase_text, "intent": intent}