from sqlalchemy.orm import Session
from modules.voice_module import generate_custom_voice
from modules.voice_cache import is_voice_cached, get_voice_cache_path
from modules.cached_responses import get_cached_phrase
from modules.behavior.style_map import resolve_style
import os


def play_or_generate_voice(
    user_id: int,
    text: str,
    style: str,
    lang: str,
    db: Session
) -> dict:
   
    
    style = resolve_style(style, lang)
    text = text.strip()

    if is_voice_cached(text, lang):
        path = get_voice_cache_path(text, lang)
        return {
            "status": "ok",
            "path": _url_from_path(path),
            "text": None
        }

    cached = get_cached_phrase(db, text, style, lang)
    if cached:
        if is_voice_cached(cached, lang):
            path = get_voice_cache_path(cached, lang)
            return {
                "status": "ok",
                "path": _url_from_path(path),
                "text": cached
            }

        path = generate_custom_voice(user_id, text=cached, style=style, lang=lang, db=db)
        if path:
            return {
                "status": "ok",
                "path": _url_from_path(path),
                "text": cached
            }

    path = generate_custom_voice(user_id, text=text, style=style, lang=lang, db=db)
    if path:
        return {
            "status": "ok",
            "path": _url_from_path(path),
            "text": text
        }

    return {
        "status": "text",
        "path": None,
        "text": text
    }


def _url_from_path(path: str) -> str:
    filename = os.path.basename(path)
    return f"/static/voice_cache/{filename}"