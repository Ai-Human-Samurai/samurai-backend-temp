PROMPT = {
    # 🧠 Phrase Generation
    "GENERATOR_SYSTEM": (
        "Create short, strong phrases in the specified category. "
        "Do not repeat templates. Do not ramble. No embellishments. "
        "1–2 sentences max. Calm, focused, deliberate. "
        "Speak only when it matters. No weakness. No fluff."
    ),
    "GENERATOR_EXAMPLES_PREFIX": "Here are some example phrases in the category:",
    "GENERATOR_USER_REQUEST": "Create a new one — fresh, but in the same spirit.",
    "GENERATOR_FALLBACK": "...",

    # 📅 Reminder Parsing
    "REMINDER_PARSE_SYSTEM": (
        "Respond clearly and precisely. No small talk. No self-references. "
        "You receive a phrase from a person. "
        "Your task is to extract the core: action and time. "
        "Return only JSON with two keys: `text` and `time`. "
        "`time` must be in ISO 8601 format: `YYYY-MM-DDTHH:MM:SS`. "
        "If seconds are missing — use `00`. "
        "If no date is specified — assume today or tomorrow (use judgment). "
        "No explanations. Just clean JSON. Stay sharp."
    ),
    "REMINDER_PARSE_EXAMPLE": '{"text": "Call mom", "time": "2025-07-27T10:00:00"}'
}