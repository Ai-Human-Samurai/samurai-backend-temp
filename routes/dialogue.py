from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database.db import get_db
from modules.behavior_engine import get_phrase
from modules.behavior.style_map import resolve_style
from modules.voice_engine import play_or_generate_voice
from modules.users import get_or_create_user
from prompts import load_prompts
from modules.intents import detect_intent
from modules.behavior.sos import detect_level
import random

router = APIRouter()


class DialogueRequest(BaseModel):
    user_id: int | None = None
    text: str
    lang: str | None = None
    style: str | None = None
    offline: bool = False


class DialogueResponse(BaseModel):
    status: str
    text: str
    path: str | None = None


@router.post("/dialogue", response_model=DialogueResponse)
def dialogue(input: DialogueRequest, db: Session = Depends(get_db)):
    """
    Main behavioural entry point for Samurai dialogue.
    Processes user text through SOS detection, intent filtering,
    style resolution and voice playback.
    """

    # Ensure user exists
    user = get_or_create_user(db, input.user_id)
    lang = input.lang or user.language
    style = resolve_style(input.style or user.style)

    store = load_prompts(lang)
    offline = input.offline

    # 1. Detect SOS level first
    sos_level = detect_level(input.text, lang)
    if sos_level > 0:
        phrase_text = get_phrase(store, f"sos.SOS_LEVEL_{sos_level}", offline=offline)
        path = play_or_generate_voice(user.id, phrase_text, lang, style, db)
        return DialogueResponse(status="sos", text=phrase_text, path=path)

    # 2. Detect intent
    intent = detect_intent(input.text, lang=lang)

    # 3. Identity/meta answers (dynamic keys from known_phrases)
    identity_keys = set()
    identity_dict = store.get("known_phrases", {}).get("identity", {})
    if isinstance(identity_dict, dict):
        identity_keys = set(identity_dict.keys())

    if intent in identity_keys:
        phrase_text = get_phrase(store, f"known_phrases.identity.{intent}", offline=offline, default=None)
        if phrase_text:
            path = play_or_generate_voice(user.id, phrase_text, lang, style, db)
            return DialogueResponse(status="identity", text=phrase_text, path=path)

    # 4. Normal behaviour response
    phrase_text = get_phrase(store, f"intents.{intent}", offline=offline)
    path = play_or_generate_voice(user.id, phrase_text, lang, style, db)
    return DialogueResponse(status="ok", text=phrase_text, path=path)