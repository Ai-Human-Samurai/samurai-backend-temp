from fastapi import Depends, Header
from sqlalchemy.orm import Session
from datetime import datetime

from database.models import User
from database.db import get_db

DEFAULT_LANGUAGE = "ru"
DEFAULT_STYLE = "friendly"

def get_or_create_user(
    x_user_id: int = Header(..., alias="X-User-Id"),  
    db: Session = Depends(get_db)
) -> str:

    user = db.query(User).filter(User.id == x_user_id).first()
    if user:
        return str(user.id)

    user = User(
        id=x_user_id,
        language=DEFAULT_LANGUAGE,
        style=DEFAULT_STYLE,
        is_pro=False,
        pro_until=None,
        pro_remind_disabled=False,
        created_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return str(user.id)


def update_user_presence_time(user_id: int, event: str, db: Session):
  
    field_name = f"last_presence_{event}"
    now = datetime.utcnow().isoformat()

    # SQL-level update (safe if field exists)
    db.execute(
        f"UPDATE users SET {field_name} = :now WHERE id = :user_id",
        {"now": now, "user_id": user_id}
    )
    db.commit() 
    
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from database.models import User
from database.db import get_db
from prompts import load_prompts

DEFAULT_LANGUAGE = "ru"
DEFAULT_STYLE = "дружественный"


def get_or_create_user(
    x_user_id: int = Header(..., alias="X-User-Id"),
    db: Session = Depends(get_db)
) -> str:
    
    user = db.query(User).filter(User.id == x_user_id).first()
    if user:
        return str(user.id)

    user = User(
        id=x_user_id,
        language=DEFAULT_LANGUAGE,
        style=DEFAULT_STYLE,
        is_pro=False,
        pro_until=None,
        pro_remind_disabled=False,
        created_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return str(user.id)



def update_user_presence_time(user_id: int, event: str, db: Session):
    
    field_name = f"last_presence_{event}"
    now = datetime.utcnow().isoformat()

    db.execute(
        f"UPDATE users SET {field_name} = :now WHERE id = :user_id",
        {"now": now, "user_id": user_id}
    )
    db.commit()


def get_user_or_404(user_id: int, db: Session, lang: str = "ru") -> User:
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        msg = load_prompts(lang)["system"].get("USER_NOT_FOUND", "User not found")
        raise HTTPException (status_code=404, detail=msg)
    return user