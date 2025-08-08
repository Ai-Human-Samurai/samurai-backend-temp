import random
from modules.behavior.known_phrases import ALL_KNOWN_PHRASES
from modules.behavior.style_map import get_style_map, resolve_style
from modules.behavior_cache import is_recent_repeat, store_phrase
from prompts import load_prompts

DEFAULT_STYLE = "friendly"
DEFAULT_LANGUAGE = "ru"

CRITICAL_INTENTS = {"sos_now", "sos_breathe", "sos_hold"}

FALLBACK_PHRASE = "..."


def detect_identity_intent(text: str, lang: str) -> str | None:
    
    lowered = text.lower()
    triggers = load_prompts(lang)["intents"].get("identity_triggers", {})
    for intent_key, keywords in triggers.items():
        if any(k in lowered for k in keywords):
            return intent_key
    return None


def store_if_needed(user_id: int | None, intent: str, value: str):
    if user_id:
        store_phrase(user_id, intent, value)


def get_phrase(
    style: str,
    intent: str,
    lang: str = DEFAULT_LANGUAGE,
    text: str = "",
    user_id: int | None = None
) -> dict:
    is_critical = intent in CRITICAL_INTENTS
    prompts = load_prompts(lang)

    # 🧠 Проверка identity-интента
    identity_intent = detect_identity_intent(text, lang)
    if identity_intent:
        phrases = prompts["known_phrases"]["identity"].get(identity_intent)
        if phrases:
            value = random.choice(phrases)
            store_if_needed(user_id, identity_intent, value)
            return {
                "text": value,
                "style": resolve_style("dry", lang),
                "intent": identity_intent,
                "critical": False,
                "cacheable": True,
                "priority": 1,
            }

    if is_critical and "SOS_PHRASES" in prompts:
        value = random.choice(prompts["SOS_PHRASES"])
        store_if_needed(user_id, intent, value)
        return {
            "text": value,
            "style": resolve_style("friendly", lang),
            "intent": intent,
            "critical": True,
            "cacheable": False,
            "priority": 2,
        }

    resolved_style = resolve_style(DEFAULT_STYLE if is_critical else style, lang)
    style_prompts = get_style_map(lang).get(resolved_style) or {}

    phrase_set = style_prompts.get(intent)

    if not phrase_set:
        known = ALL_KNOWN_PHRASES.get(lang, {}).get(intent)
        if known:
            value = random.choice(known["text"])
            if user_id and is_recent_repeat(user_id, intent, value):
                return {
                    "text": FALLBACK_PHRASE,
                    "style": resolved_style,
                    "intent": intent,
                    "critical": is_critical,
                    "cacheable": False,
                    "priority": 0,
                }
            store_if_needed(user_id, intent, value)
            return {
                "text": value,
                "style": resolved_style,
                "intent": intent,
                "critical": is_critical,
                "cacheable": True,
                "priority": known.get("priority", 1),
            }

        return {
            "text": FALLBACK_PHRASE,
            "style": resolved_style,
            "intent": intent,
            "critical": is_critical,
            "cacheable": False,
            "priority": 0,
        }

    value = random.choice(phrase_set) if isinstance(phrase_set, list) else phrase_set
    if user_id and is_recent_repeat(user_id, intent, value):
        return {
            "text": FALLBACK_PHRASE,
            "style": resolved_style,
            "intent": intent,
            "critical": is_critical,
            "cacheable": False,
            "priority": 0,
        }

    store_if_needed(user_id, intent, value)
    return {
        "text": value,
        "style": resolved_style,
        "intent": intent,
        "critical": is_critical,
        "cacheable": not is_critical,
        "priority": 1,
    }