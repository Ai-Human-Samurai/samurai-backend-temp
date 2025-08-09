# main.py
# All comments in English

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from dotenv import load_dotenv

# Database imports
from database.db import Base, engine
from database import models  # ensure models are imported so metadata is complete

# Routers
from routes.user import router as user
from routes.reminders import router as reminders
from routes.reminder_parser import router as reminder_parser
from routes.voice import router as voice
from routes.settings import router as settings
from routes.system import router as system
from routes.ping import router as ping
from routes.calendar import router as calendar
from routes import memory
from routes import sos
from routes import dialogue

# --- Environment -------------------------------------------------------------

# Load .env from project root (auto-walk upwards)
load_dotenv()

APP_TITLE = os.getenv("APP_TITLE", "Samurai API")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

# CORS: allow specific origins via env (comma-separated), or "*" for dev
ALLOW_ORIGINS = [
    o.strip()
    for o in os.getenv("ALLOW_ORIGINS", "*").split(",")
    if o.strip()
]

# Voice cache dir
BASE_DIR = Path(__file__).resolve().parent
VOICE_CACHE_DIR = BASE_DIR / "voice_cache"
VOICE_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# --- Application -------------------------------------------------------------

app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if ALLOW_ORIGINS == ["*"] else ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static (cached voices)
app.mount("/static", StaticFiles(directory=str(VOICE_CACHE_DIR)), name="static")

# --- Lifespan hooks ----------------------------------------------------------
# Create tables on startup (safe for dev; for prod prefer Alembic migrations)
@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


# --- Routes ------------------------------------------------------------------

# Health & root
@app.get("/", tags=["system"])
def root():
    return {"status": "Samurai API is alive", "version": APP_VERSION}

@app.get("/health", tags=["system"])
def health():
    return {"ok": True}

@app.get("/ready", tags=["system"])
def ready():
    # Extend with checks: DB ping, external services, etc.
    return {"ready": True}

# Register feature routers
app.include_router(user, prefix="/user", tags=["user"])
app.include_router(reminders, prefix="/reminders", tags=["reminders"])
app.include_router(reminder_parser, prefix="/reminders", tags=["reminders"])
app.include_router(voice, prefix="/voice", tags=["voice"])
app.include_router(sos.router, prefix="/sos", tags=["sos"])
app.include_router(settings, prefix="/settings", tags=["settings"])
app.include_router(system, tags=["system"])
app.include_router(ping, tags=["ping"])
app.include_router(calendar, prefix="/calendar", tags=["calendar"])
app.include_router(memory.router)
app.include_router(dialogue.router, prefix="/dialogue", tags=["dialogue"])