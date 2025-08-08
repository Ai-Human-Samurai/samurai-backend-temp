from prompts import load_prompts


def detect_intent(text: str, lang: str = "ru") -> str | None:

    lowered = text.lower()
    prompts = load_prompts(lang)
    triggers = prompts["intents"].get("INTENTS", {})

    for intent, value in triggers.items():
        if isinstance(value, dict):
            continue  # Пропускаем identity_triggers
        if isinstance(value, str):
            value = [value]
        if any(trigger in lowered for trigger in value):
            return intent

    return None