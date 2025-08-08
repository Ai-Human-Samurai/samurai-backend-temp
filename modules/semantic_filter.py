from prompts import load_prompts

def is_text_blocked(text: str, lang: str = "ru") -> bool:
    prompts = load_prompts(lang)
    bad_words = prompts["filters"].get("BAD_WORDS", [])
    lowered = text.lower()
    return any(bad_word in lowered for bad_word in bad_words)