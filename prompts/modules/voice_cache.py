import os
from hashlib import md5
from core.config import settings


def get_voice_cache_path(text: str, lang: str = "ru", voice: str = "neutral") -> str:
    """
    Генерирует путь к mp3-файлу на основе текста, языка и имени голоса.
    """
    text_hash = md5(text.strip().lower().encode("utf-8")).hexdigest()
    filename = f"{lang}_{voice}_{text_hash}.mp3"
    return os.path.join(settings.VOICE_CACHE_DIR, filename)


def is_voice_cached(text: str, lang: str = "ru", voice: str = "neutral") -> bool:
    """
    Проверяет, существует ли уже сгенерированный mp3-файл.
    """
    return os.path.exists(get_voice_cache_path(text, lang, voice))


def save_mp3_file(audio_bytes: bytes, text: str, lang: str = "ru", voice: str = "neutral") -> str:
    """
    Сохраняет байты аудио в mp3-файл по определённому пути.
    """
    path = get_voice_cache_path(text, lang, voice)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "wb") as f:
        f.write(audio_bytes)

    return path