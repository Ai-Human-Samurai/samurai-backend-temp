from sqlalchemy.orm import Session
from database.models import MemoryThought
from modules.behavior_engine import get_phrase
from modules.voice_engine import play_or_generate_voice
from datetime import datetime


def save_thought(user_id: int, text: str, lang: str = "ru", db: Session = None) -> dict:
    
    if db is None:
        raise ValueError("Database session is required")

    # 🧠 Create thought record
    thought = MemoryThought(
        user_id=user_id,
        text=text,
        created_at=datetime.utcnow()
    )
    db.add(thought)
    db.commit()
    db.refresh(thought)

    # 🎤 Voice confirmation
    phrase = get_phrase(
        intent="memory_saved",
        style="дружественный",
        lang=lang,
        user_id=user_id
    )

    result = play_or_generate_voice(
        user_id=user_id,
        text=phrase["text"],
        lang=lang,
        style="дружественный",
        db=db
    )

    voice_path = result.get("path")
    if voice_path:
        thought.file_path = voice_path
        db.commit()

    return {
        "text": phrase["text"],
        "path": voice_path,
        "status": "memory_saved"
    }