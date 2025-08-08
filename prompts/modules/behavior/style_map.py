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