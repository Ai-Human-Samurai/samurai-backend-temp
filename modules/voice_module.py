import os
import logging
import tempfile
from typing import Optional, Tuple
from openai import OpenAI

from modules.voice_cache import save_mp3_file
from modules.behavior.style_map import resolve_style, style_to_voice
from modules.semantic_filter import is_text_blocked  # (user_id, text, lang, db=None)

logger = logging.getLogger("samurai.voice")
_client: Optional[OpenAI] = None


def _client_singleton() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI()  # читает OPENAI_API_KEY из .env
    return _client


def _synthesize_once(text: str, voice: str) -> Optional[bytes]:
    """
    Надёжная генерация через streaming → файл → bytes.
    """
    client = _client_singleton()
    try:
        with client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice=voice,
            input=text,
        ) as response:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tmp_path = tmp.name
            response.stream_to_file(tmp_path)
            with open(tmp_path, "rb") as f:
                data = f.read()
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            return data
    except Exception as e:
        logger.error("TTS synth failed (voice=%s): %s", voice, e)
        return None


def _synthesize_with_fallback(text: str, voice: str) -> Tuple[Optional[bytes], str]:
    """
    Сначала выбранный голос, при ошибке — fallback на 'alloy'.
    """
    audio = _synthesize_once(text, voice)
    if audio:
        return audio, voice
    if voice != "alloy":
        logger.info("TTS fallback → 'alloy'")
        audio = _synthesize_once(text, "alloy")
        if audio:
            return audio, "alloy"
    return None, voice


def generate_and_save_voice(
    text: str,
    user_id: int,
    lang: str = "ru",
    style: str = "дружественный",
) -> Optional[str]:
    style = resolve_style(style, lang)
    voice = style_to_voice(style, lang)

    audio_bytes, used_voice = _synthesize_with_fallback(text, voice)
    if not audio_bytes:
        logger.error("TTS generation failed")
        return None

    path = save_mp3_file(audio_bytes, text=text, lang=lang, voice=used_voice)
    logger.info("TTS saved: voice=%s path=%s", used_voice, path)
    return path


def generate_custom_voice(
    user_id: int,
    text: str,
    style: str = "дружественный",
    db=None,
    lang: str = "ru",
) -> Optional[str]:
    if is_text_blocked(user_id, text, lang=lang, db=db):
        logger.info("Text blocked by filters, user_id=%s", user_id)
        return None
    return generate_and_save_voice(text=text, user_id=user_id, lang=lang, style=style)