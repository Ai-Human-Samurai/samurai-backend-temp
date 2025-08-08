from datetime import datetime, timedelta
import random

from modules.voice_engine import play_or_generate_voice
from modules.behavior.presence_engine import get_presence_phrase
from modules.users import update_user_presence_time
from prompts import load_prompts

# Default fallback values
DEFAULT_LANG = "ru"
DEFAULT_STYLE = "дружественный"

# Delay between presence phrases for each event type
PRESENCE_DELAYS = {
    "reminder": timedelta(days=1),
    "thought": timedelta(days=2),
    "wake": timedelta(days=3),  # fallback default if random logic skipped
}

def should_say_presence(user: dict, event: str) -> bool:
    
    key = f"last_presence_{event}"
    last_time = user.get(key)

    if event == "wake":
        min_delay = timedelta(days=2)
        if not last_time:
            return random.random() < 0.5  

        try:
            last_dt = datetime.fromisoformat(last_time)
        except Exception:
            return random.random() < 0.5  

        if datetime.utcnow() - last_dt < min_delay:
            return False

        return random.random() < 0.4 

    delay = PRESENCE_DELAYS.get(event, timedelta(days=1))
    if not last_time:
        return True

    try:
        last_dt = datetime.fromisoformat(last_time)
    except Exception:
        return True

    return datetime.utcnow() - last_dt > delay


def trigger_presence(user: dict, event: str, db=None) -> str | None:
    
    if not should_say_presence(user, event):
        return None

    lang = user.get("language", DEFAULT_LANG)
    style = user.get("style", DEFAULT_STYLE)

    # Normalize style through prompt aliasing
    style_aliases = load_prompts(lang).styles.STYLE_ALIASES
    style = style_aliases.get(style.strip().lower(), DEFAULT_STYLE if lang == "ru" else "friendly")

    phrase = get_presence_phrase(event=event, lang=lang, style=style)
    if not phrase:
        return None

    play_or_generate_voice(
        user_id=user["id"],
        text=phrase,
        lang=lang,
        style=style,
        db=db
    )

    update_user_presence_time(user["id"], event, db)

    return phrase