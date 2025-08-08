from modules.voice_engine import play_or_generate_voice
from modules.behavior_engine import get_phrase
from modules.behavior.style_map import resolve_style


def play_voice(user_id: int, key: str, lang: str = "ru", style: str = "дружественный", db=None) -> str | None:
    
    normalized_style = resolve_style(style, lang)
    phrase_data = get_phrase(style=normalized_style, intent=key, lang=lang, user_id=user_id)
    text = phrase_data.get("text")

    result = play_or_generate_voice(
        user_id=user_id,
        text=text,
        style=normalized_style,
        lang=lang,
        db=db
    )

    return result.get("path")