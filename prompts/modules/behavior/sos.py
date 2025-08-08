from modules.voice_engine import play_or_generate_voice
from modules.behavior.style_map import resolve_style
from modules.behavior_engine import get_phrase
from modules.emotion_detector import should_block_emotion, log_emotional_appeal
from prompts import load_prompts


def trigger_sos_response(user_id: int, lang: str = "ru", style: str = "сухой", db=None) -> dict:
    
    if should_block_emotion(db, user_id):
        return {"text": None, "path": None, "blocked": True}

    log_emotional_appeal(db, user_id, detail="sos_now")

    resolved_style = resolve_style(style, lang)

    phrase_data = get_phrase(
        style=resolved_style,
        intent="sos_now",
        lang=lang,
        user_id=user_id
    )

    result = play_or_generate_voice(
        user_id=user_id,
        text=phrase_data["text"],
        style=resolved_style,
        lang=lang,
        db=db
    )

    return {
        "text": phrase_data["text"],
        "path": result.get("path"),
        "blocked": False
    }


def detect_level(text: str, lang: str = "ru") -> int:
    
    lowered = text.lower()
    levels = load_prompts(lang).get("semantic_filter", {}).get("sos_levels", {})

    if any(phrase in lowered for phrase in levels.get("level_3", [])):
        return 3
    elif any(phrase in lowered for phrase in levels.get("level_2", [])):
        return 2
    return 1