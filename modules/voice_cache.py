import os
from hashlib import md5

# Пишем прямо в <REPO_ROOT>/voice_cache
VOICE_CACHE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "voice_cache")
)
os.makedirs(VOICE_CACHE_DIR, exist_ok=True)


def _hash_text(text: str) -> str:
    return md5(text.strip().lower().encode("utf-8")).hexdigest()


def get_voice_cache_path(text: str, lang: str, voice: str) -> str:
    filename = f"{lang}_{voice}_{_hash_text(text)}.mp3"
    return os.path.join(VOICE_CACHE_DIR, filename)


def is_voice_cached(text: str, lang: str, voice: str) -> bool:
    return os.path.exists(get_voice_cache_path(text, lang, voice))


def save_mp3_file(audio_bytes: bytes, text: str, lang: str, voice: str) -> str:
    path = get_voice_cache_path(text, lang, voice)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(audio_bytes)
    return path