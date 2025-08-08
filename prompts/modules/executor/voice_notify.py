# modules/executor/voice_notify.py

from modules.voice_engine import play_or_generate_voice
from modules.behavior_engine import get_phrase
from modules.behavior.style_map import resolve_style


def play_voice(user_id: int, key: str, lang: str = "ru", style: str = "дружественный", db=None) -> str | None:
    """
    Main interface to trigger behavioral voice playback.

    This function should be used after specific user actions:
        - After reminder creation
        - After memory recording
        - During wake-up ritual
        - For SOS responses
        - For system-level prompts

    Returns the path to the generated mp3 or None.
    """
    # Resolve actual speaking style based on user profile or default
    resolved_style = resolve_style(user_id, style=style, lang=lang, db=db)

    # Get the exact phrase to be played based on intent key
    phrase = get_phrase(user_id, key=key, lang=lang, style=resolved_style)

    # Generate or retrieve from cache the mp3 version of this phrase
    result = play_or_generate_voice(
        user_id=user_id,
        key=None,  # Key is not needed anymore — we already have the final text
        text=phrase,
        lang=lang,
        style=resolved_style,
        db=db,
    )

    return result["path"]