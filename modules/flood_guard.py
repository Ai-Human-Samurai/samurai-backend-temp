from datetime import datetime, timedelta
from collections import defaultdict
from prompts import load_prompts
from typing import Optional

FLOOD_LIMIT = 2
FLOOD_TIMEOUT_MINUTES = 5


class FloodGuard:
    

    def __init__(self):
        self.user_states = defaultdict(lambda: {
            "count": 0,
            "last_time": datetime.utcnow(),
            "flooding": False
        })

    def update(self, user_id: int, is_meaningful: bool, lang: str = "ru") -> Optional[str]:
       
        state = self.user_states[user_id]
        now = datetime.utcnow()

        # Сброс счётчика по таймеру
        if now - state["last_time"] > timedelta(minutes=FLOOD_TIMEOUT_MINUTES):
            state["count"] = 0
            state["flooding"] = False

        if is_meaningful:
            state["last_time"] = now
            state["count"] = 0
            state["flooding"] = False
            return None

        state["count"] += 1
        state["last_time"] = now

        if state["count"] <= FLOOD_LIMIT:
            return None

        prompts = load_prompts(lang).get("flood")

        if not state["flooding"]:
            state["flooding"] = True
            return prompts.get_flood_phrase("flood_warn_1")

        return prompts.get_flood_phrase("flood_warn_repeat")


guard = FloodGuard()


def check_meaning(text: str, lang: str = "ru") -> bool:

    text = text.strip().lower()
    prompts = load_prompts(lang)["flood"]

    whitelist = prompts.get("WHITELIST", [])
    boring = prompts.get("BORING", [])

    for phrase in whitelist:
        if phrase in text:
            return True

    if len(text) < 5:
        return False

    for phrase in boring:
        if phrase in text:
            return False

    return True