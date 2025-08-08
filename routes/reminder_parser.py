from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.db import get_db
from modules.users import get_user_or_404
from core.credentials import openai_client
from prompts import load_prompts
from datetime import datetime
import json
import logging

router = APIRouter(prefix="/reminders", tags=["reminders"])
logger = logging.getLogger("reminders")


class ReminderParseRequest(BaseModel):
    user_id: int
    text: str


class ReminderParseResponse(BaseModel):
    text: str
    time: str


@router.post("/parse", response_model=ReminderParseResponse)
def parse_reminder(payload: ReminderParseRequest, db: Session = Depends(get_db)):
    user = get_user_or_404(payload.user_id, db)
    lang = user.language
    prompts = load_prompts(lang)

    if len(payload.text) > 500:
        raise HTTPException(status_code=400, detail=prompts["system"].get("REMINDER_PARSE_TOO_LONG", "Text too long"))

    system = prompts["system"].get("REMINDER_PARSE_SYSTEM")
    example = prompts["system"].get("REMINDER_PARSE_EXAMPLE")

    full_prompt = [
        {"role": "system", "content": system},
        {"role": "user", "content": payload.text},
        {"role": "assistant", "content": example}
    ]

    try:
        # 🧠 GPT-4o → fallback: 3.5-turbo
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=full_prompt,
                temperature=0.3
            )
        except Exception:
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=full_prompt,
                temperature=0.3
            )

        content = response.choices[0].message.content.strip()

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            raise ValueError(prompts["system"].get("REMINDER_PARSE_INVALID_JSON", "Invalid format"))

        if not parsed.get("text") or not parsed.get("time"):
            raise ValueError(prompts["system"].get("REMINDER_PARSE_INCOMPLETE", "Missing fields"))

        datetime.fromisoformat(parsed["time"])

        logger.info(f"[PARSE] user_id={payload.user_id} text='{payload.text}' → parsed={parsed}")

        return parsed

    except Exception as e:
        raise HTTPException(status_code=400, detail=prompts["system"].get("REMINDER_PARSE_FAILURE", "Failed to parse"))