import importlib
from functools import lru_cache


@lru_cache(maxsize=5)
def load_prompts(lang: str = "ru") -> dict:
    # 🎨 Стили
    styles_module = importlib.import_module(f"prompts.styles.{lang}")
    styles = {
        "PHRASES_BY_STYLE": getattr(styles_module, "PHRASES_BY_STYLE", {}),
        "STYLE_ALIASES": getattr(styles_module, "STYLE_ALIASES", {}),
    }

    # 🆘 SOS
    sos = importlib.import_module(f"prompts.sos.{lang}").PROMPT

    # 🧱 Фильтры (semantic + flood)
    semantic_filter_module = importlib.import_module(f"prompts.semantic_filter.{lang}")
    semantic_filter = getattr(semantic_filter_module, "PROMPT", {})
    sos_levels = getattr(semantic_filter_module, "sos_levels", {})

    flood_module = importlib.import_module(f"prompts.flood.{lang}")
    flood_prompt = getattr(flood_module, "PROMPT", {})
    get_flood_phrase = getattr(flood_module, "get_flood_phrase", None)

    # 📚 Интенты, генерация, система
    intents = importlib.import_module(f"prompts.intents.{lang}").PROMPT
    generation = importlib.import_module(f"prompts.generation.{lang}").PROMPT
    system = importlib.import_module(f"prompts.system.{lang}").PROMPT

    # ⏰ Напоминания и presence
    reminders_module = importlib.import_module(f"prompts.reminders.{lang}")
    known_phrases_reminders = getattr(reminders_module, "ALL_KNOWN_PHRASES", {}).get(lang, {})

    presence_module = importlib.import_module(f"prompts.presence.{lang}")
    presence = getattr(presence_module, "PHRASES", {})

    # 🧠 Общие фразы (кто ты, зачем и т.д.)
    known_phrases_module = importlib.import_module(f"prompts.known_phrases.{lang}")
    known_phrases_identity = getattr(known_phrases_module, "PHRASES", {})

    return {
        "styles": styles,
        "sos": sos,
        "semantic_filter": {
            "PROMPT": semantic_filter.get("SEMANTIC_FILTER_PROMPT", ""),
            "BAD_WORDS": semantic_filter.get("BAD_WORDS", []),
            "sos_levels": sos_levels,
        },
        "filters": {
            "BAD_WORDS": semantic_filter.get("BAD_WORDS", [])  # для совместимости
        },
        "flood": {
            "PROMPT": flood_prompt,
            "get_flood_phrase": get_flood_phrase,
        },
        "intents": intents,
        "generation": generation,
        "system": system,
        "presence": {
            "PHRASES": presence,
        },
        "known_phrases": {
            "identity": known_phrases_identity,
            "reminders": known_phrases_reminders,
        },
    }