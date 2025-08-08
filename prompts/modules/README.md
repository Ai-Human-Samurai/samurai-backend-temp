# modules/

This folder contains the core logic of the Samurai backend.  
All functionality — from behavioral response to voice caching — is implemented here.

---

## Structure

### `behavior/`
Handles intent recognition and phrase mapping.

- `behavior_engine.py`: selects phrases based on style, intent, and context.
- `known_phrases/`: predefined static responses for common queries.
  - `ru.py` / `en.py`: language-specific phrase dictionaries.
  - `__init__.py`: exports `ALL_KNOWN_PHRASES` for unified access.

---

### Voice & Audio

- `voice_module.py`: generates and returns voice responses via OpenAI TTS.
- `voice_cache.py`: manages MP3 storage and retrieval to minimize API calls.

---

### Caching

- `cached_responses.py`: caches structured responses per intent/style/language to optimize processing and response time.

---

### Behavior & Filters

- `emotion_detector.py`: detects heightened emotional states.
- `flood_guard.py`: limits excessive user input (anti-flood logic).
- `config_loader.py`: loads limits and settings from `data/`.

---

### Core Logic

- `main.py`: central logic and entry point for behavior handling (used by FastAPI or external triggers).
- `reminders.py`: reminder-related logic and data access.
- `user.py`: manages user profiles and preferences.
- `storage.py`: utilities for file saving, e.g., voice files.

---

## Principles

- **Modular:** Each file has one clear purpose.
- **Scalable:** Easy to extend with more behaviors or languages.
- **Aligned with Samurai Philosophy:** Every module respects the balance between function, ethics, and minimalism.

> 🥷 Clarity over complexity. This is not just code — it's the soul of Samurai.