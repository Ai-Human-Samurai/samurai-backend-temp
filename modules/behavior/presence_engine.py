import random
import datetime
from typing import Optional

from sqlalchemy.orm import Session
from database.models import User
from prompts import load_prompts

MIN_INTERVALS = {
    "reminder_created": 60 * 60 * 12,     # 12 hours
    "thought_saved":    60 * 60 * 24,     # 1 day
    "wakeup_triggered": 60 * 60 * 48,     # 2 days
    "snoozed":          60 * 60 * 8,      # 8 hours
    "calendar_synced":  60 * 60 * 24,     # 1 day
}


def should_trigger_presence(user_id: int, db: Session, event_type: str) -> bool:
   
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    return should_say_presence(user, event_type)


def should_say_presence(user: User, event_type: str) -> bool:
   
    now = datetime.datetime.utcnow()
    last_attr = f"last_presence_{event_type}"

    if not hasattr(user, last_attr):
        return True

    last_time = getattr(user, last_attr)
    if not last_time:
        return True

    delta = (now - last_time).total_seconds()
    return delta >= MIN_INTERVALS.get(event_type, 86400)  # Default: 24h


def update_presence_timestamp(user: User, event_type: str):
 
    now = datetime.datetime.utcnow()
    attr = f"last_presence_{event_type}"
    if hasattr(user, attr):
        setattr(user, attr, now)


def get_presence_phrase(event_type: str, lang: str = "ru") -> Optional[str]:
    
    phrases = load_prompts(lang).get("presence", {}).get("PHRASES", {})
    options = phrases.get(event_type)
    if not options:
        return None
    return random.choice(options)