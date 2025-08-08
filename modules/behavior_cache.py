import time
from collections import defaultdict

_recent_phrases = defaultdict(dict)

REPEAT_TIMEOUT_SEC = 180  
def is_recent_repeat(user_id: int, intent: str) -> bool:
  
    now = time.time()
    last_time = _recent_phrases[user_id].get(intent, 0)
    return (now - last_time) < REPEAT_TIMEOUT_SEC

def store_phrase(user_id: int, intent: str) -> None:
   
    _recent_phrases[user_id][intent] = time.time()