import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from database.db import get_db
from modules.voice_engine import play_or_generate_voice

router = APIRouter()
logger = logging.getLogger("samurai.api.voice")


class VoiceRequest(BaseModel):
    user_id: int
    text: str | None = None
    intent: str | None = None
    lang: str | None = "ru"
    style: str | None = "дружественный"

    @field_validator("text", mode="before")
    @classmethod
    def strip_text(cls, v):
        return v.strip() if isinstance(v, str) else v


class VoiceResponse(BaseModel):
    status: str
    path: str | None = None
    text: str | None = None
    intent: str | None = None
    message: str | None = None


@router.post("", response_model=VoiceResponse)
def create_voice(req: VoiceRequest, db: Session = Depends(get_db)):
    if not (req.text and req.text.strip()) and not req.intent:
        raise HTTPException(status_code=422, detail="NO_TEXT_OR_INTENT")

    result = play_or_generate_voice(
        user_id=req.user_id,
        text=req.text,
        intent=req.intent,
        lang=req.lang or "ru",
        style=req.style or "дружественный",
        db=db,
    )

    status = result.get("status", "error")
    if status == "forbidden":
        return JSONResponse(content=result, status_code=403)
    if status == "error":
        return JSONResponse(content=result, status_code=400)

    # ok / text → 200
    return JSONResponse(content=result, status_code=200)