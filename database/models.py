from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.db import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    language = Column(String, default="ru")
    style = Column(String, default="дружественный")
    is_pro = Column(Boolean, default=False)
    pro_until = Column(DateTime, nullable=True)
    pro_remind_disabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    last_presence_reminder_created = Column(DateTime, nullable=True)
    last_presence_thought_saved = Column(DateTime, nullable=True)
    last_presence_wakeup_triggered = Column(DateTime, nullable=True)
    last_presence_snoozed = Column(DateTime, nullable=True)
    last_presence_calendar_synced = Column(DateTime, nullable=True)

    memory_thoughts = relationship("MemoryThought", back_populates="user", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    calendar_events = relationship("CalendarEvent", back_populates="user", cascade="all, delete-orphan")


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    text = Column(String)
    time = Column(DateTime)

    is_seen = Column(Boolean, default=False)
    is_played = Column(Boolean, default=False)
    is_completed = Column(Boolean, default=False)

    voice_enabled = Column(Boolean, default=True)
    mp3_path = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="reminders")


class CachedPhrase(Base):
    __tablename__ = "cached_phrases"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    response_text = Column(String)
    style = Column(String)
    lang = Column(String)
    usage_count = Column(Integer, default=1)
    priority = Column(Integer, default=1)
    mp3_fallback = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    event = Column(String)
    detail = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    ends_at = Column(DateTime)
    trial_used = Column(Boolean, default=False)

    user = relationship("User", back_populates="subscriptions")


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    event_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="calendar_events")


class MemoryThought(Base):
    __tablename__ = "memory_thoughts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    text = Column(Text, nullable=True)
    audio_path = Column(String, nullable=True) 
    is_favorite = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="memory_thoughts")