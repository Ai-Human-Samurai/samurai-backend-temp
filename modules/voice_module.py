import os
from openai import OpenAI, OpenAIError

from core.credentials import OPENAI_API_KEY
from modules.voice_cache import save_mp3_file, get_voice_cache_path  # get_voice_cache_path нужен для пути
from modules.flood_guard import check_meaning
from modules.emotion_detector import should_block_emotion
from modules.behavior.style_map import resolve_style
from prompts import load_prompts

client = OpenAI(api_key=OPENAI_API_KEY)


def is_text_blocked(user_id: int, text: str, lang: str = "ru", db=None) -> bool:
    if not text:
        return True
    text = text.strip().lower()
    bad_words = load_prompts(lang).get("filters", {}).get("BAD_WORDS", [])
    return any(w in text for w in bad_words)


def style_to_voice(style: str = "дружественный", lang: str = "ru") -> str:
    style = style.lower().strip()
    if lang == "ru":
        return {
            "сухой": "nova",
            "официальный": "aidar",
            "дружественный": "baya",
        }.get(style, "baya")
    elif lang == "en":
        return {
            "dry": "echo",
            "formal": "onyx",
            "friendly": "alloy",
        }.get(style, "alloy")
    return "alloy"


def generate_and_save_voice(
    text: str,
    user_id: int,
    lang: str = "ru",
    style: str = "дружественный",
) -> str | None:
    """
    Generate TTS and save MP3 to cache. Returns absolute file path or None.
    Uses streaming write to avoid API response handling quirks.
    """
    # ⛳ временно можно выключить фильтры, если нужно исключить их влияние
    if is_text_blocked(user_id, text, lang):
        print("⛔ Blocked by toxic filter")
        return None

    if not check_meaning(text, lang=lang):
        print("⛔ Blocked by semantic filter")
        return None

    if should_block_emotion(text, user_id=user_id, lang=lang):
        print("⛔ Blocked by emotion filter")
        return None

    style = resolve_style(style, lang)
    voice = style_to_voice(style, lang)

    # путь к файлу кэша (учитываем голос)
    try:
        cache_path = get_voice_cache_path(text=text, lang=lang, voice=voice)
    except TypeError:
        # если у тебя старая сигнатура get_voice_cache_path без voice — срочно обнови voice_cache.py
        # на версию с (text, lang, voice)
        print("⚠️ get_voice_cache_path() без voice — обнови modules/voice_cache.py")
        return None

    os.makedirs(os.path.dirname(cache_path), exist_ok=True)

    print(f"🎙️ TTS try: model='tts-1', voice='{voice}', lang='{lang}', text='{text}'")
    try:
        # надёжный способ: streaming → сразу в файл
        with client.audio.speech.with_streaming_response.create(
            model="tts-1",          # или "gpt-4o-mini-tts" если включена
            voice=voice,
            input=text,
        ) as resp:
            resp.stream_to_file(cache_path)

        exists = os.path.exists(cache_path)
        print(f"✅ TTS done, file_exists={exists}, path={cache_path}")
        return cache_path if exists else None

    except OpenAIError as e:
        print("❌ OpenAI TTS error:", repr(e))
        return None
    except Exception as e:
        print("❌ TTS unexpected error:", repr(e))
        return None