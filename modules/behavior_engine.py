# modules/behavior_engine.py
# All comments in English

from __future__ import annotations
from typing import Optional, Dict, Any

from prompts import load_prompts
from helpers.prompt_utils import get_phrase as _gp
from utils.net import is_offline

# Legacy defaults (kept for callers that rely on them)
DEFAULT_STYLE = "friendly"
DEFAULT_LANGUAGE = "ru"

# Critical intents that must not be cached (legacy behavior)
_CRITICAL = {"sos_now", "sos_breathe", "sos_hold"}


def _intent_to_path(store: Dict[str, Any], intent: str) -> Optional[str]:
    """
    Best-effort mapping from legacy 'intent' names to unified prompt paths
    understood by helpers.prompt_utils.get_phrase().

    Returns a dotted path like:
      - known_phrases.reminders.reminder_confirm
      - presence.presence_morning
      - known_phrases.identity.who_are_you
      - sos
    or None if no direct path mapping is known (we will try raw traversal later).
    """

    # reminders.*
    if intent.startswith("reminder_"):
        # e.g. reminder_confirm, reminder_done, ...
        return f"known_phrases.reminders.{intent}"

    # presence.*
    if intent.startswith("presence_"):
        # e.g. presence_morning, presence_idle, are_you_there
        return f"presence.{intent}"

    # SOS buckets (list lives in store['sos']['SOS_PHRASES'])
    if intent in {"sos_now", "sos_breathe", "sos_hold", "sos"}:
        return "sos"

    # identity buckets discovered dynamically from loaded prompts
    identity = (store.get("known_phrases") or {}).get("identity") or {}
    if isinstance(identity, dict) and intent in identity:
        return f"known_phrases.identity.{intent}"

    # Fallback: no explicit mapping — let caller try raw traversal or default
    return None


def _infer_identity_from_text(store: Dict[str, Any], text: str) -> Optional[str]:
    """
    Lightweight identity intent detection via triggers located in prompts.intents.
    Returns an identity key (e.g., 'who_are_you') or None.
    """
    if not text:
        return None
    intents_payload = (store.get("intents") or {}).get("identity_triggers", {}) or {}
    lowered = text.lower()
    for ident_key, keywords in intents_payload.items():
        try:
            if any(k in lowered for k in keywords):
                return ident_key
        except Exception:
            # Defensive: skip malformed keywords
            continue
    return None


def get_phrase(
    style: str,
    intent: str,
    lang: str = DEFAULT_LANGUAGE,
    text: str = "",
    user_id: int | None = None,
) -> Dict[str, Any]:
    """
    Legacy-compatible get_phrase() that delegates phrase retrieval to
    helpers.prompt_utils.get_phrase() with:
      - anti-repeat
      - offline fallback
      - dynamic identity detection

    Returns a dict (legacy shape):
      {
        "text": str,           # chosen phrase or "..."
        "style": str,          # as given (no heavy style resolution here)
        "intent": str,         # may be tightened if identity inferred from text
        "critical": bool,      # True for SOS-like intents
        "cacheable": bool,     # False for critical intents
        "priority": int,       # 1 by default
      }
    """
    store = load_prompts(lang)
    offline_flag = is_offline()

    # 1) Map legacy intent → unified path and try direct fetch
    path = _intent_to_path(store, intent)
    phrase_text: Optional[str] = None
    if path:
        phrase_text = _gp(store, path, offline=offline_flag, default=None)

    # 2) If nothing found yet, try to infer identity by the raw text and fetch
    if not phrase_text and text:
        inferred = _infer_identity_from_text(store, text)
        if inferred:
            path2 = f"known_phrases.identity.{inferred}"
            phrase_text = _gp(store, path2, offline=offline_flag, default=None)
            if phrase_text:
                intent = inferred  # tighten the returned intent label

    # 3) Last resort: try raw traversal using the legacy intent as a dotted path,
    #    or return default "..."
    if not phrase_text:
        # This allows advanced callers to pass direct paths like "presence.are_you_there"
        phrase_text = _gp(store, intent, offline=offline_flag, default="...")

    is_critical = intent in _CRITICAL
    return {
        "text": phrase_text or "...",
        "style": style or DEFAULT_STYLE,
        "intent": intent,
        "critical": is_critical,
        "cacheable": not is_critical,
        "priority": 1,
    }