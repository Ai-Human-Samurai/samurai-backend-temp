# 📁 routes/

This directory defines all **HTTP endpoints** of the Samurai backend.  
Each file is a FastAPI router, grouped by feature domain.

---

## 🧩 Purpose

- Encapsulates route logic (request parsing, validation, responses)
- Delegates core functionality to `modules/` logic layer
- Keeps API surface clean and modular

---

## 📌 Structure

Each file defines one `APIRouter()`:

- `reminders.py`  
  Handles creating, listing, deleting, snoozing reminders.

- `user.py`  
  Profile-related endpoints: style, voice, subscription.

- `voice.py`  
  Generates and serves TTS voice responses.

- `settings.py`  
  Exposes feature toggles and limits (for frontend).

- `ping.py`  
  Lightweight status check (used for monitoring / health check).

---

## 🔁 Import Pattern

Routes are mounted in `main.py`:

```python
app.include_router(reminders.router, prefix="/reminders", tags=["reminders"])
app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(voice.router, prefix="/voice", tags=["voice"])
app.include_router(settings.router, prefix="/settings", tags=["settings"])
app.include_router(ping.router, tags=["ping"])