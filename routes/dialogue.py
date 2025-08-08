from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.db import get_db
from modules.users import get_or_create_user
from modules.behavior_engine import get_phrase
from modules.voice_engine import play_or_generate_voice
from modules.behavior.sos import trigger_sos_response, detect_level
from modules.flood_guard import guard, check_meaning
from modules.semantic_filter import is_text_blocked
from modules.behavior.presence_engine import should_trigger_presence
from modules.behavior.style_map import resolve_style
from modules.reminders import create_reminder
from modules.memory import save_thought
from modules.intents import detect_intent
from prompts import load_prompts
import openai

router = APIRouter()


class DialogueInput(BaseModel):
    user_id: int
    text: str
    lang: str = "ru"
    style: str = "дружественный"


@router.post("/dialogue")
def dialogue(input: DialogueInput, db: Session = Depends(get_db)):
    user = get_or_create_user(input.user_id, db)

    try:
        prompts = load_prompts(input.lang)
    except ModuleNotFoundError:
        return {"status": "error", "text": f"Unsupported language: {input.lang}", "path": None}

    # 🤫 Присутствие (если пустой ввод)
    if not input.text.strip():
        if should_trigger_presence(input.user_id, db):
            phrase = get_phrase(
                style=input.style,
                intent="presence_idle",
                lang=input.lang,
                user_id=input.user_id
            )
            if phrase:
                path = play_or_generate_voice(
                    user_id=input.user_id,
                    text=phrase["text"],
                    lang=input.lang,
                    style=input.style,
                    db=db
                )
                return {"status": "ok", "text": phrase["text"], "path": path}
        return {"status": "idle", "text": "", "path": None}

    # 🚫 Блокировка по смыслу / этике
    if is_text_blocked(input.text, input.lang):
        phrase = get_phrase(
            style=input.style,
            intent="blocked",
            lang=input.lang,
            user_id=input.user_id
        )
        return {
            "status": "blocked",
            "text": phrase["text"] if phrase else "Запрос заблокирован.",
            "path": None
        }

    # ⚠️ Флуд-фильтр
    is_meaningful = check_meaning(input.text, input.lang)
    flood_response = guard.update(
        user_id=input.user_id,
        is_meaningful=is_meaningful,
        lang=input.lang
    )
    if flood_response:
        return {"status": "flood", "text": flood_response, "path": None}

    # 🔍 Intent
    intent = detect_intent(input.text, input.lang)

    # 💥 SOS-проверка
    sos_level = detect_level(input.text, input.lang)
    if sos_level == "sos_now":
        result = trigger_sos_response(input.user_id, input.lang, input.style, db)
        return {"status": "sos", "text": result["text"], "path": result["path"]}

    # ⏰ Напоминание
    if intent == "reminder_create":
        create_reminder(input.user_id, input.text, input.lang, db=db)
        phrase = get_phrase(
            intent="reminder_confirm",
            style=input.style,
            lang=input.lang,
            user_id=input.user_id
        )
        if phrase:
            path = play_or_generate_voice(
                user_id=input.user_id,
                text=phrase["text"],
                lang=input.lang,
                style=input.style,
                db=db
            )
            return {"status": "reminder", "text": phrase["text"], "path": path}

    # 💭 Мысль
    if intent == "memory_save":
        save_thought(input.user_id, input.text, input.lang, db=db)
        phrase = get_phrase(
            intent="memory_saved",
            style=input.style,
            lang=input.lang,
            user_id=input.user_id
        )
        if phrase:
            path = play_or_generate_voice(
                user_id=input.user_id,
                text=phrase["text"],
                lang=input.lang,
                style=input.style,
                db=db
            )
            return {"status": "memory", "text": phrase["text"], "path": path}

    # 👤 Identity-фразы и философия
    identity_phrase = get_phrase(
        style="сухой",
        intent=intent,
        lang=input.lang,
        text=input.text,
        user_id=input.user_id
    )
    if identity_phrase:
        intent_value = identity_phrase.get("intent", "")
        if isinstance(intent_value, str) and intent_value.startswith(("who_", "what_")):
            path = play_or_generate_voice(
                user_id=input.user_id,
                text=identity_phrase["text"],
                lang=identity_phrase.get("lang", input.lang),
                style=identity_phrase.get("style", input.style),
                db=db
            )
            return {
                "status": "identity",
                "text": identity_phrase["text"],
                "path": path
            }

    # 🤖 GPT-ответ
    try:
        system_prompt = prompts["system"]["SYSTEM_PROMPT"]
    except KeyError:
        return {"status": "error", "text": "System prompt not found.", "path": None}

    completion = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": input.text}
        ],
        temperature=0.7,
        max_tokens=200
    )
    answer = completion.choices[0].message.content.strip()

    path = play_or_generate_voice(
        user_id=input.user_id,
        text=answer,
        lang=input.lang,
        style=input.style,
        db=db
    )
    return {"status": "gpt", "text": answer, "path": path}