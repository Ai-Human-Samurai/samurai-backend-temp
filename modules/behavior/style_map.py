from functools import lru_cache
from prompts import load_prompts

@lru_cache()
def get_style_map(lang: str = "ru") -> dict:
    prompts = load_prompts(lang)
    return prompts["styles"].get("PHRASES_BY_STYLE", {})

def resolve_style(input_style: str, lang: str = "ru") -> str:
    known_langs = ["ru", "en", "ja"]
    if input_style in known_langs:
        return "дружественный" if input_style == "ru" else "friendly"

    cleaned = input_style.strip().lower()
    try:
        prompts = load_prompts(lang)
        aliases = prompts["styles"].get("STYLE_ALIASES", {})
        return aliases.get(cleaned, "дружественный" if lang == "ru" else "friendly")
    except Exception:
        return "дружественный" if lang == "ru" else "friendly"

def style_to_voice(style: str, lang: str = "ru") -> str:
    """
    Преобразует стиль общения в имя TTS-голоса.
    """
    style_map = {
        "ru": {
            "дружественный": "ru_friendly_male",
            "официальный": "ru_official_male",
            "сухой": "ru_dry_male",
        },
        "en": {
            "friendly": "en_friendly_male",
            "official": "en_official_male",
            "dry": "en_dry_male",
        },
        "ja": {
            "friendly": "ja_friendly_male",
            "official": "ja_official_male",
            "dry": "ja_dry_male",
        }
    }
    style = resolve_style(style, lang)
    return style_map.get(lang, {}).get(style, "ru_friendly_male")