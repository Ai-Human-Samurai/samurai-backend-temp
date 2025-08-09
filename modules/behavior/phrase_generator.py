import random
from openai import OpenAIError
from core.credentials import openai_client
from prompts import load_prompts
from modules.behavior.known_phrases import ALL_KNOWN_PHRASES


def generate_dynamic_phrase(category: str, lang: str = "ru") -> str:
    """
    Generates a fresh Samurai-style phrase for a given category and language.
    """
    prompts = load_prompts(lang)
    examples = ALL_KNOWN_PHRASES.get(category, [])
    system_prompt = prompts["generation"].get("GENERATOR_SYSTEM", "")
    fallback_phrase = prompts["generation"].get("GENERATOR_FALLBACK", "...")

    if not examples:
        return fallback_phrase

    examples_text = "\n".join(f"- {item['text']}" for item in examples)
    prefix = prompts["generation"].get("GENERATOR_EXAMPLES_PREFIX", "")
    user_req = prompts["generation"].get("GENERATOR_USER_REQUEST", "")

    user_prompt = f"{prefix}\n{examples_text}\n\n{user_req}".strip()

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            temperature=0.7,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        )
        return response.choices[0].message.content.strip() if response.choices else fallback_phrase
    except OpenAIError:
        return random.choice(examples)["text"]
    
# ── Adapter for voice_engine ──
try:
    from modules.behavior_engine import get_phrase as _get_phrase_impl
except Exception:
    _get_phrase_impl = None

def get_phrase(style: str, intent: str, lang: str, user_id: int, db=None) -> dict | None:
    """
    Thin adapter. Keeps legacy import path used by voice_engine.
    Delegates to modules.behavior_engine.get_phrase(...).
    Returns dict like {"text": "..."} or None.
    """
    if _get_phrase_impl is None:
        return None
    return _get_phrase_impl(style=style, intent=intent, lang=lang, user_id=user_id, db=db)