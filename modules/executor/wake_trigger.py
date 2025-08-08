from sqlalchemy.orm import Session
from database.db import SessionLocal
from database.models import User

from modules.presence_trigger import trigger_presence
from modules.executor.voice_notify import play_voice

def handle_wake_event(user_id: int):
    
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"[wake] User not found: {user_id}")
            return

        trigger_presence(user, event="wake", db=db)

        play_voice(
            user_id=user.id,
            key="wake_success",
            lang=user.language,
            style=user.style,
            db=db
        )

        print(f"[wake] Triggered wake behavior for user {user.id}")

    except Exception as e:
        print(f"[wake] Error: {e}")
    finally:
        db.close()