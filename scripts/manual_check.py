# scripts/manual_check.py

from database.db import SessionLocal
from modules.executor.reminder_runner import get_active_reminders

def run():
    """
    CLI utility to manually list active reminders from the database.

    Утилита для ручной проверки активных напоминаний через терминал.
    """
    db = SessionLocal()
    try:
        reminders = get_active_reminders(db)
        print(f"Found {len(reminders)} active reminders:")
        for r in reminders:
            print(f"→ {r.text} @ {r.time} (User {r.user_id})")
    finally:
        db.close()

if __name__ == "__main__":
    run()