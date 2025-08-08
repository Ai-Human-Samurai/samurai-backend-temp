import os
from hashlib import md5
from core.config import settings


def get_voice_cache_path(text: str, lang: str = "ru") -> str:
    
    text_hash = md5(text.strip().lower().encode("utf-8")).hexdigest()
    filename = f"{lang}_{text_hash}.mp3"
    return os.path.join(settings.VOICE_CACHE_DIR, filename)


def is_voice_cached(text: str, lang: str = "ru") -> bool:
    
    return os.path.exists(get_voice_cache_path(text, lang))


def save_mp3_file(audio_bytes: bytes, text: str, lang: str = "ru") -> str:
    
    path = get_voice_cache_path(text, lang)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "wb") as f:
        f.write(audio_bytes)

    return path
