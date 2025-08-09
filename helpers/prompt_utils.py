# All comments in English

from __future__ import annotations
import random
from typing import Any, Dict, List, Optional, Tuple

# In-memory cache to avoid immediate repetition per key
_LAST_PICK: Dict[str, str] = {}


def _anti_repeat_pick(items: List[str], cache_key: str) -> Optional[str]:
    """Pick a random item with 'no immediate repeat' guarantee."""
    if not items:
        return None
    prev = _LAST_PICK.get(cache_key)
    pool = [x for x in items if x != prev] or items
    choice = random.choice(pool)
    _LAST_PICK[cache_key] = choice
    return choice


def _ensure_list_of_str(value: Any) -> Optional[List[str]]:
    """Normalize a value to a list[str] when possible."""
    if isinstance(value, list) and all(isinstance(x, str) for x in value):
        return value
    return None


def _resolve_presence_bucket(store: Dict[str, Any], key: str) -> Optional[List[str]]:
    """Resolve presence buckets from store['presence'] with or without 'PHRASES' hop."""
    presence = store.get("presence") or {}
    if isinstance(presence, dict):
        if "PHRASES" in presence and isinstance(presence["PHRASES"], dict):
            bucket = presence["PHRASES"].get(key)
            return _ensure_list_of_str(bucket)
        bucket = presence.get(key)
        return _ensure_list_of_str(bucket)
    return None


def _resolve_known_identity(store: Dict[str, Any], key: str) -> Tuple[List[str], List[str]]:
    """
    Return (online_texts, offline_texts) for known_phrases.identity.KEY.
    Online texts live in PHRASES[key]['text']; offline in known_phrases.offline[key].
    """
    known = store.get("known_phrases") or {}

    online_texts: List[str] = []
    identity = known.get("identity") or {}
    if isinstance(identity, dict):
        entry = identity.get(key) or {}
        if isinstance(entry, dict):
            t = entry.get("text")
            if isinstance(t, list) and all(isinstance(x, str) for x in t):
                online_texts = t

    offline_texts: List[str] = []
    off = known.get("offline") or {}
    if isinstance(off, dict):
        t2 = off.get(key)
        if isinstance(t2, list) and all(isinstance(x, str) for x in t2):
            offline_texts = t2

    return online_texts, offline_texts


def _resolve_known_reminders(store: Dict[str, Any], key: str) -> List[str]:
    """Return online texts for known_phrases.reminders.KEY['text']."""
    known = store.get("known_phrases") or {}
    rem = known.get("reminders") or {}
    entry = rem.get(key) or {}
    if isinstance(entry, dict):
        t = entry.get("text")
        if isinstance(t, list) and all(isinstance(x, str) for x in t):
            return t
    return []


def _resolve_offline_bucket(store: Dict[str, Any], key: str) -> List[str]:
    """Return offline known bucket by key."""
    known = store.get("known_phrases") or {}
    off = known.get("offline") or {}
    bucket = off.get(key) if isinstance(off, dict) else []
    return bucket if isinstance(bucket, list) and all(isinstance(x, str) for x in bucket) else []


def get_phrase(
    store: Dict[str, Any],
    path: str,
    *,
    offline: bool = False,
    default: Optional[str] = "..."
) -> Optional[str]:
    """
    Unified phrase getter with anti-repeat and offline fallback.

    Supported paths:
      - "known_phrases.identity.<key>"
      - "known_phrases.reminders.<key>"
      - "known_phrases.offline.<key>"
      - "presence.<key>" or "presence.PHRASES.<key>"
      - "sos" or "sos.SOS_PHRASES"
    """
    try:
        parts = path.split(".")
        if not parts:
            return default

        head = parts[0]

        # SOS
        if head == "sos":
            sos_list = None
            if len(parts) == 1 or (len(parts) == 2 and parts[1] == "SOS_PHRASES"):
                sos_list = (store.get("sos") or {}).get("SOS_PHRASES")
            if isinstance(sos_list, list) and all(isinstance(x, str) for x in sos_list):
                pick = _anti_repeat_pick(sos_list, "sos")
                if pick:
                    return pick
            off = _resolve_offline_bucket(store, "sos")
            pick = _anti_repeat_pick(off, "sos:offline")
            return pick or default

        # Presence
        if head == "presence":
            key = parts[1] if len(parts) > 1 and parts[1] != "PHRASES" else (parts[2] if len(parts) > 2 else "presence_general")
            bucket = _resolve_presence_bucket(store, key)
            if bucket:
                pick = _anti_repeat_pick(bucket, f"presence:{key}")
                if pick:
                    return pick
            off = _resolve_offline_bucket(store, "are_you_there")
            pick = _anti_repeat_pick(off, "presence:offline")
            return pick or default

        # Known phrases
        if head == "known_phrases":
            group = parts[1] if len(parts) > 1 else None
            key = parts[2] if len(parts) > 2 else None
            if not group or not key:
                return default

            if group == "identity":
                online_texts, offline_texts = _resolve_known_identity(store, key)
                if offline and offline_texts:
                    return _anti_repeat_pick(offline_texts, f"known:offline:{key}") or default
                if online_texts:
                    return _anti_repeat_pick(online_texts, f"known:identity:{key}") or default
                if offline_texts:
                    return _anti_repeat_pick(offline_texts, f"known:offline:{key}") or default
                return default

            if group == "reminders":
                texts = _resolve_known_reminders(store, key)
                if texts:
                    return _anti_repeat_pick(texts, f"known:reminders:{key}") or default
                off = _resolve_offline_bucket(store, key)
                if off:
                    return _anti_repeat_pick(off, f"known:offline:{key}") or default
                return default

            if group == "offline":
                off = _resolve_offline_bucket(store, key)
                return _anti_repeat_pick(off, f"known:offline:{key}") or default

        # Direct offline shorthand: "offline.<key>"
        if head == "offline" and len(parts) == 2:
            off = _resolve_offline_bucket(store, parts[1])
            return _anti_repeat_pick(off, f"known:offline:{parts[1]}") or default

        # Raw dict traversal (last-resort)
        node: Any = store
        for seg in parts:
            if isinstance(node, dict) and seg in node:
                node = node[seg]
            elif isinstance(node, dict) and seg == "PHRASES" and "PHRASES" in node:
                node = node["PHRASES"]
            else:
                node = None
                break

        bucket = _ensure_list_of_str(node)
        if bucket:
            return _anti_repeat_pick(bucket, f"raw:{path}") or default

        if isinstance(node, dict) and "text" in node:
            bucket = _ensure_list_of_str(node.get("text"))
            if bucket:
                return _anti_repeat_pick(bucket, f"raw:{path}:text") or default

        return default
    except Exception:
        return default
