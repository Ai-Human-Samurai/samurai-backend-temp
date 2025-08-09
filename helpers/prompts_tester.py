# All comments in English
"""
Prompts Tester
--------------
Walk through a curated set of keys and retrieve a sample phrase
using get_phrase() to ensure everything is accessible.
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path so that `import prompts` resolves to the package, not helpers/prompt_utils.py
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from prompts import load_prompts  # noqa: E402
from helpers.prompt_utils import get_phrase  # noqa: E402


if __name__ == "__main__":
    lang = "ru"
    store = load_prompts(lang=lang)

    keys = [
        "known_phrases.identity.who_are_you",
        "known_phrases.identity.what_can_you_do",
        "known_phrases.identity.why_are_you_here",
        "known_phrases.reminders.reminder_confirm",
        "known_phrases.reminders.reminder_done",
        "known_phrases.reminders.reminder_snooze",
        "presence.presence_morning",
        "sos",
        "known_phrases.offline.who_are_you",
        "known_phrases.offline.sos",
        "offline.are_you_there",
    ]

    print(f"Testing {len(keys)} keys (lang='{lang}'):\n")
    for k in keys:
        phrase = get_phrase(store, k)
        print(f"{k} → {phrase}")

    print("\nOffline preferred example:")
    print("known_phrases.identity.who_are_you (offline=True) →",
          get_phrase(store, "known_phrases.identity.who_are_you", offline=True))