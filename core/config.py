from pathlib import Path

class Settings:
    BASE_DIR = Path(__file__).resolve().parent.parent

    DATABASE_URL = f"sqlite:///{(BASE_DIR / 'samurai.db').as_posix()}"

    VOICE_CACHE_DIR = BASE_DIR / "voice_cache"
    PHRASES_DIR = BASE_DIR / "phrases"
    DATA_DIR = BASE_DIR / "data"
    PUBLIC_DIR = BASE_DIR / "public"

    DEFAULT_LANGUAGE = "ru"
    SUPPORTED_LANGUAGES = ["ru", "en", "ja"]  

    MAX_REMINDERS = 30
    REMINDER_AUTO_POSTPONE_MINUTES = 30

    CHAT_SPAM_LIMIT = 4
    EMOTION_THRESHOLD = 5

    PRO_TRIAL_DAYS = 3
    MAX_VOICE_TASKS_FREE = 3
    MAX_VOICE_TASKS_PRO = 50

    DEFAULT_MP3 = {
        "ru": PUBLIC_DIR / "default_ru.mp3",
        "en": PUBLIC_DIR / "default_en.mp3",
        "ja": PUBLIC_DIR / "default_ja.mp3"  
    }

    CACHE_PHRASE_LIMIT = 500
    TTS_CACHE_LIMIT = 1000

    PIN_REQUIRED = False
    BIOMETRY_ALLOWED = False

    BLUETOOTH_AUTO_CONNECT = True
    SOS_CALL_ENABLED = True

AVAILABLE_VOICES = ["nova", "echo", "fable", "onyx"]
FREE_VOICE = "nova"

settings = Settings()
