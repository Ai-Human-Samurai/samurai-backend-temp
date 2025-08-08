from sqlalchemy.orm import Session
from database.models import CachedPhrase
from datetime import datetime
from core.config import settings
from typing import Optional


def get_cached_phrase(db: Session, text: str, style: str, lang: str) -> Optional[str]:
   
    clean_text = text.strip()
    phrase = db.query(CachedPhrase).filter_by(
        text=clean_text,
        style=style,
        lang=lang
    ).first()

    if phrase:
        phrase.usage_count += 1
        phrase.updated_at = datetime.utcnow()
        db.commit()
        return phrase.response_text

    return None


def save_cached_phrase(
    db: Session,
    text: str,
    response_text: str,
    style: str,
    lang: str,
    mp3_fallback: Optional[str] = None,
    priority: int = 1
) -> None:
   
    enforce_cache_limit(db)

    clean_text = text.strip()

    existing = db.query(CachedPhrase).filter_by(
        text=clean_text,
        style=style,
        lang=lang
    ).first()
    if existing:
        return

    phrase = CachedPhrase(
        text=clean_text,
        response_text=response_text,
        style=style,
        lang=lang,
        usage_count=1,
        priority=priority,
        mp3_fallback=mp3_fallback,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(phrase)
    db.commit()


def enforce_cache_limit(db: Session) -> None:
    """
    Deletes oldest/least-used phrases if cache exceeds limit.
    """
    total_count = db.query(CachedPhrase).count()
    limit = settings.CACHE_PHRASE_LIMIT

    if total_count > limit:
        overflow = total_count - limit
        to_delete = (
            db.query(CachedPhrase)
            .order_by(CachedPhrase.usage_count.asc(), CachedPhrase.updated_at.asc())
            .limit(overflow)
            .all()
        )
        for phrase in to_delete:
            db.delete(phrase)
        db.commit()


def get_all_cached_phrases(db: Session, lang: Optional[str] = None) -> list[CachedPhrase]:
    """
    Returns all cached phrases (optionally filtered by language).
    Useful for admin/export/debug tools.
    """
    query = db.query(CachedPhrase)
    if lang:
        query = query.filter(CachedPhrase.lang == lang)
    return query.all()