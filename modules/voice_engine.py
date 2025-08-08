import random
from modules.voice_module import (
    generate_and_save_voice,
    save_mp3_file,
    style_to_voice,
    is_text_blocked,
)
from modules.voice_cache import (
    get_voice_cache_path,
    is_voice_cached,
)
from prompts import load_prompts


def play_or_generate_voice(
    user_id: int,
    key: str = None,
    lang: str = "ru",
    style: str = "дружественный",
    text: str = None,
    db=None,
) -> dict:
    """
    Возвращает голосовую фразу по ключу или произвольному тексту.
    Проверяет кэш, генерирует при необходимости.
    
    Возвращает:
        {
            "text": "сама фраза",
            "path": "путь к mp3 или None"
        }
    """
    prompts = load_prompts(lang)
    phrase = None

    # 🧠 1. Выбор фразы
    if key:
        phrase_list = prompts.get(key, [])
        phrase = random.choice(phrase_list) if isinstance(phrase_list, list) else phrase_list
    elif text:
        phrase = text.strip()
    else:
        return {"text": None, "path": None}

    # 🚫 2. Фильтрация (токсичность, флад и пр.)
    if is_text_blocked(user_id=user_id, text=phrase, lang=lang, db=db):
        return {"text": None, "path": None}

    # 🔊 3. Кэш
    voice = style_to_voice(style, lang)
    cache_path = get_voice_cache_path(text=phrase, lang=lang, voice=voice)

    if is_voice_cached(text=phrase, lang=lang, voice=voice):
        return {"text": phrase, "path": cache_path}

    # 🎤 4. Генерация
    try:
        generate_and_save_voice(
            text=phrase,
            user_id=user_id,
            voice=voice,
            lang=lang,
        )
        return {"text": phrase, "path": cache_path}
    except Exception:
        return {"text": phrase, "path": None}