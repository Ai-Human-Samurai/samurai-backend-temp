from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import os
import shutil

from database.db import get_db
from database.models import MemoryThought, User
from modules.users import get_user_or_404
from modules.presence_trigger import trigger_presence
from prompts import load_prompts
from core.config import settings

router = APIRouter(prefix="/memory", tags=["memory"])

UPLOAD_DIR = settings.DATA_DIR / "thoughts"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 📥 Input model for saving memory
class MemoryThoughtCreate(BaseModel):
    text: Optional[str] = None
    audio_path: Optional[str] = None

# 📤 Output model
class MemoryThoughtOut(BaseModel):
    id: int
    text: Optional[str]
    audio_path: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# 📥 Add memory (text or audio)
@router.post("/add", response_model=MemoryThoughtOut)
def add_memory(
    thought: MemoryThoughtCreate,
    user_id: int = Form(...),
    db: Session = Depends(get_db)
):
    user = get_user_or_404(user_id, db)
    lang = user.language
    prompts = load_prompts(lang)

    if not thought.text and not thought.audio_path:
        raise HTTPException(status_code=400, detail=prompts["system"].THOUGHT_MISSING_INPUT)

    new_thought = MemoryThought(
        user_id=user_id,
        text=thought.text,
        audio_path=thought.audio_path,
        created_at=datetime.utcnow()
    )
    db.add(new_thought)
    db.commit()
    db.refresh(new_thought)

    trigger_presence(user, event="thought_saved", db=db)

    return new_thought

@router.get("/list", response_model=List[MemoryThoughtOut])
def list_memories(
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    _ = get_user_or_404(user_id, db)
    return db.query(MemoryThought)\
        .filter_by(user_id=user_id)\
        .order_by(MemoryThought.created_at.desc())\
        .all()

@router.delete("/delete/{thought_id}")
def delete_memory(
    thought_id: int,
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    user = get_user_or_404(user_id, db)
    lang = user.language
    prompts = load_prompts(lang)

    thought = db.query(MemoryThought).filter_by(id=thought_id, user_id=user_id).first()
    if not thought:
        raise HTTPException(status_code=404, detail=prompts["system"].THOUGHT_NOT_FOUND)

    db.delete(thought)
    db.commit()
    return {"success": True, "deleted_id": thought_id}


@router.post("/upload", response_model=MemoryThoughtOut)
def upload_memory(
    file: UploadFile = File(...),
    text: Optional[str] = Form(""),
    user_id: int = Form(...),
    db: Session = Depends(get_db)
):
    user = get_user_or_404(user_id, db)

    filename = f"{user_id}_{datetime.utcnow().isoformat().replace(':', '-')}.m4a"
    file_path = UPLOAD_DIR / filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    thought = MemoryThought(
        user_id=user_id,
        text=text,
        audio_path=str(file_path),
        created_at=datetime.utcnow()
    )
    db.add(thought)
    db.commit()
    db.refresh(thought)
    return thought

@router.get("/audio/{thought_id}")
def get_memory_audio(
    thought_id: int,
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    user = get_user_or_404(user_id, db)
    lang = user.language
    prompts = load_prompts(lang)

    thought = db.query(MemoryThought).filter_by(id=thought_id, user_id=user_id).first()
    if not thought:
        raise HTTPException(status_code=404, detail=prompts["system"].THOUGHT_NOT_FOUND)

    if not thought.audio_path:
        raise HTTPException(status_code=400, detail=prompts["system"].THOUGHT_NO_AUDIO)

    if not os.path.exists(thought.audio_path):
        raise HTTPException(status_code=404, detail=prompts["system"].FILE_NOT_FOUND)

    return FileResponse(thought.audio_path, media_type="audio/mpeg")