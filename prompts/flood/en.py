from random import choice

# 🟡 Titles for debugging or UI (optional)
FLOOD_WARNING_TITLES = {
    "flood_warn_1": "First soft warning",
    "flood_warn_repeat": "Continued flood warning",
}

# 🔴 Main warning phrases
FLOOD_WARNINGS = {
    "flood_warn_1": [
        "I'm here. But don't forget why you came.",
        "Remember the reason. Don’t lose the path.",
        "I hear you. But I don’t speak without purpose.",
    ],
    "flood_warn_repeat": [
        "When there's meaning — I’ll respond.",
        "Silence is also an answer.",
        "I don’t oppose words. I oppose the void.",
    ],
}

# 🟢 Short messages allowed (simple greetings)
FLOOD_WHITELIST = {"hello", "hi", "good morning", "good evening", "hey"}

# 🔴 "Boring" messages considered flood
FLOOD_BORING = {
    "ok", "yeah", "no", "lol", "?", ".", "..", "...", "hmm", "ugh",
    "aha", "haha", "meh", "nah", "ah", "uh", "yep", "nope"
}

# ✅ Required for prompt loader
PROMPT = {
    "FLOOD_CHECK_PROMPT": (
        "Check if this phrase is similar to previous ones in meaning or structure.\n\n"
        "If it’s almost identical — answer TRUE.\n"
        "If it’s new in meaning — answer FALSE.\n\n"
        "Phrase: '{text}'\n\n"
        "Answer: TRUE or FALSE"
    ),
    "FLOOD_FEEDBACK": "I’ll speak when it matters.",
}


def get_flood_phrase(key: str) -> str | None:
    """
    Returns a random warning phrase for the given flood key.
    """
    return choice(FLOOD_WARNINGS.get(key, []))


def is_whitelist(text: str) -> bool:
    """
    Returns True if the text is an allowed short input (like greetings).
    """
    return text.lower() in FLOOD_WHITELIST


def is_boring(text: str) -> bool:
    """
    Returns True if the text is considered meaningless (triggers flood).
    """
    return text.lower() in FLOOD_BORING