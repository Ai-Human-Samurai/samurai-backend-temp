from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database.db import Base, engine
from database import models

import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

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

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Samurai API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

voice_cache_dir = os.path.join(os.path.dirname(__file__), "..", "voice_cache")
app.mount("/static", StaticFiles(directory=voice_cache_dir), name="static")

@app.get("/")
def root():
    return {"status": "Samurai API is alive"}