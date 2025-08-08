# modules/executor/wake_trigger.py

from sqlalchemy.orm import Session
from database.db import SessionLocal
from database.models import User

from modules.presence_trigger import trigger_presence
from modules.voice_engine import play_or_generate_voice
from modules.behavior.style_map import resolve_style
from modules.behavior_engine import get_phrase


def handle_wake_event(user_id: int) -> None:
    """
    Handles the wake-up event: triggers a voice phrase and presence flag.
    Used during wake-up rituals or reminders scheduled in the morning.
    """
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"[wake] User not found: {user_id}")
            return

        # Trigger presence (mark wake event in presence system)
        trigger_presence(user, event="wake", db=db)

        # Resolve user style and phrase for wake-up event
        resolved_style = resolve_style(user_id, style=user.style, lang=user.language, db=db)
        phrase = get_phrase(user_id, key="wake_success", lang=user.language, style=resolved_style)

        # Play or generate the phrase (returns mp3 or text fallback)
        result = play_or_generate_voice(
            user_id=user.id,
            key=None,
            text=phrase,
            lang=user.language,
            style=resolved_style,
            db=db
        )

        print(f"[wake] Wake-up phrase played: {result.get('path') or result.get('text')}")

    except Exception as e:
        print(f"[wake] Error: {e}")
    finally:
        db.close()
