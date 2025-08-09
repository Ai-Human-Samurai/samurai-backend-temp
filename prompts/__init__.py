# All comments in English

from __future__ import annotations
import importlib
from functools import lru_cache
from typing import Any, Dict


def _import(module_path: str):
    """Safe import: return module or None if missing/failed."""
    try:
        return importlib.import_module(module_path)
    except Exception:
        return None


def _get(obj: Any, key: str, default):
    """Safe getter for dict-like payloads."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default


@lru_cache(maxsize=5)
def load_prompts(lang: str = "ru") -> Dict[str, Any]:
    """
    Unified loader for Samurai prompts.
    Keeps the original shape, adds offline known phrases and safe fallbacks.
    """

    # Styles
    styles_module = _import(f"prompts.styles.{lang}")
    styles = {
        "PHRASES_BY_STYLE": getattr(styles_module, "PHRASES_BY_STYLE", {}) if styles_module else {},
        "STYLE_ALIASES": getattr(styles_module, "STYLE_ALIASES", {}) if styles_module else {},
    }

    # SOS
    sos_module = _import(f"prompts.sos.{lang}")
    sos = getattr(sos_module, "PROMPT", {}) if sos_module else {}

    # Filters (semantic + flood)
    semantic_filter_module = _import(f"prompts.semantic_filter.{lang}")
    semantic_filter_payload = getattr(semantic_filter_module, "PROMPT", {}) if semantic_filter_module else {}
    sos_levels = getattr(semantic_filter_module, "sos_levels", {}) if semantic_filter_module else {}

    flood_module = _import(f"prompts.flood.{lang}")
    flood_prompt = getattr(flood_module, "PROMPT", {}) if flood_module else {}
    get_flood_phrase = getattr(flood_module, "get_flood_phrase", None) if flood_module else None

    # Intents, generation, system
    intents_module = _import(f"prompts.intents.{lang}")
    intents = getattr(intents_module, "PROMPT", {}) if intents_module else {}

    generation_module = _import(f"prompts.generation.{lang}")
    generation = getattr(generation_module, "PROMPT", {}) if generation_module else {}

    system_module = _import(f"prompts.system.{lang}")
    system = getattr(system_module, "PROMPT", {}) if system_module else {}

    # Reminders and presence
    reminders_module = _import(f"prompts.reminders.{lang}")
    known_phrases_reminders = {}
    if reminders_module:
        akp = getattr(reminders_module, "ALL_KNOWN_PHRASES", {})
        if isinstance(akp, dict):
            known_phrases_reminders = akp.get(lang, {}) or {}

    presence_module = _import(f"prompts.presence.{lang}")
    presence = getattr(presence_module, "PHRASES", {}) if presence_module else {}

    # Known phrases (identity, etc.)
    known_phrases_module = _import(f"prompts.known_phrases.{lang}")
    known_phrases_identity = getattr(known_phrases_module, "PHRASES", {}) if known_phrases_module else {}

    # Offline fallback (known_phrases_offline)
    offline_module = _import(f"prompts.known_phrases_offline.{lang}")
    offline_payload = getattr(offline_module, "PROMPT", {}) if offline_module else {}
    offline_known_phrases = _get(offline_payload, "known_phrases_offline", {})

    return {
        "styles": styles,
        "sos": sos,  # full PROMPT for backward compatibility
        "semantic_filter": {
            "PROMPT": _get(semantic_filter_payload, "SEMANTIC_FILTER_PROMPT", ""),
            "BAD_WORDS": _get(semantic_filter_payload, "BAD_WORDS", []),
            "sos_levels": sos_levels,
        },
        "filters": {
            "BAD_WORDS": _get(semantic_filter_payload, "BAD_WORDS", [])  # legacy mirror
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
            "offline": offline_known_phrases,
        },
    }