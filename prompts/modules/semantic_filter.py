from prompts import load_prompts

def is_text_blocked(user_id: int, text: str, lang: str = "ru", db=None) -> bool:
    prompts = load_prompts(lang)
    bad_words = prompts["filters"].get("BAD_WORDS", [])
    lowered = text.lower()
    return any(bad_word in lowered for bad_word in bad_words)