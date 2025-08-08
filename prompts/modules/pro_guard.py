from datetime import datetime, timedelta
from database.models import User
from prompts import load_prompts

FREE_LIMIT = 5
TRIAL_DAYS = 3

def is_trial_active(user: User) -> bool:
    if not user.pro_until:
        return False
    return user.pro_until > datetime.utcnow()

def grant_trial(user: User):
    user.is_pro = True
    user.pro_until = datetime.utcnow() + timedelta(days=TRIAL_DAYS)

def is_pro_active(user: User) -> bool:
    return user.is_pro and (not user.pro_until or user.pro_until > datetime.utcnow())

def check_pro_access(user: User, usage_count: int, lang: str = "ru") -> str | None:
    prompts = load_prompts(lang)
    
    if is_pro_active(user):
        return None

    if usage_count < FREE_LIMIT:
        return None

    if user.pro_remind_disabled:
        return prompts["system"].PRO_REMIND_DISABLED_NOTICE

    return prompts["system"].PRO_LIMIT_NOTICE