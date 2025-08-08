PROMPT = {
    # 🗣️ Support phrases
    "SOS_PHRASES": [
        "You're not alone. I'm here.",
        "Just breathe. The rest will follow.",
        "I'm with you. Don't give up.",
        "Quiet now. This isn't the end — just a moment.",
        "Look toward life. Even if it hurts — we’ll make it through.",
        "Hold on. There's something in you that endures the storm.",
    ],

    # 🤖 GPT system prompt for generating SOS phrases
    "SYSTEM_SOS_PROMPT": (
        "Create short phrases that support someone in a hard moment. "
        "Don't give advice. Don't ramble. Avoid clichés. "
        "Max 1 sentence. No pity. Only quiet strength. "
        "You're not a therapist — you're simply present."
    ),

    # 🧠 Intent descriptions
    "SOS_INTENTS": {
        "sos_now": "The user is in crisis — immediate presence needed",
        "sos_breathe": "Reminder to breathe, to hold on",
        "sos_hold": "Support during emotional intensity",
    },

    # 🔁 Message shown when SOS is triggered too frequently
    "SOS_TOO_SOON": "I'm here.",
}