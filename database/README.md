# 🗂️ database/

This directory contains all database-related logic and configuration for the Samurai backend.

---

## 📦 Files

- **`db.py`**  
  Initializes the SQLAlchemy engine and sessionmaker.  
  Used throughout the project for database access.

- **`models.py`**  
  Contains all ORM model definitions used in the application  
  (e.g. User, Reminder, VoiceCache, etc.).

- **`migrations.sql`**  
  Optional file to keep manual SQL migration scripts (for backup, upgrades, or initial setup).

- **`__init__.py`**  
  Makes the folder importable as a module.

---

## 🧩 How it fits in

- `models.py` is imported in `core/main.py` during app startup to ensure all tables are created.
- `db.py` provides `SessionLocal` and `engine` used in route and module layers.

---

## 🛠️ Example Usage

```python
from database.db import SessionLocal
from database.models import User

with SessionLocal() as db:
    user = db.query(User).filter_by(id=1).first()