"""
Example usage of load_prompts() and get_phrase()
to retrieve phrases with anti-repetition and offline fallback.
"""

from prompts import load_prompts
from helpers.prompt_utils import get_phrase

store = load_prompts(lang="ru")

# Identity (online and offline fallback)
print(get_phrase(store, "known_phrases.identity.who_are_you"))
print(get_phrase(store, "known_phrases.identity.who_are_you", offline=True))

# Reminders
print(get_phrase(store, "known_phrases.reminders.reminder_confirm"))

# Presence
print(get_phrase(store, "presence.PHRASES.presence_morning"))

# SOS
print(get_phrase(store, "sos"))