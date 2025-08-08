import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from database.db import SessionLocal
from modules.reminders import get_active_reminders, mark_reminder_seen
from modules.executor.voice_notify import play_voice
from modules.executor.push_notify import send_push

OFFLINE_MODE = False 


def fetch_reminders(db: Session | None = None) -> list:
    """
    Wrapper for loading reminders. Swappable in offline mode.

    Online → uses SQLAlchemy
    Offline → will later use local SQLite or JSON
    """
    if OFFLINE_MODE:
        # TODO: load from local SQLite or JSON
        # Example:
        # return load_from_json("local_reminders.json")
        return []

    return get_active_reminders(db)


def check_and_trigger_reminders(db: Session | None = None):
    
    now = datetime.now()
    reminders = fetch_reminders(db)

    for reminder in reminders:
        if not reminder.seen and reminder.time <= now:
            try:
                if getattr(reminder, "voice_enabled", False):
                    play_voice(reminder)
                else:
                    send_push(reminder)

                if not OFFLINE_MODE:
                    mark_reminder_seen(db, reminder.id)

                print(f"[reminder] Triggered: {reminder.id} - {reminder.text}")
            except Exception as e:
                print(f"[reminder] Failed: {reminder.id} — {e}")


async def reminder_loop(interval_seconds: int = 60):
    print("[reminder_loop] Started")
    while True:
        try:
            db = None
            if not OFFLINE_MODE:
                db = SessionLocal()

            check_and_trigger_reminders(db)

        except Exception as e:
            print(f"[reminder_loop error] {e}")
        finally:
            if db:
                db.close()

        await asyncio.sleep(interval_seconds)
