# core/

This folder contains fundamental configuration and credentials used across the entire Samurai backend.

---

## Files

### `config.py`
Holds runtime settings and project-wide constants:
- Limits (e.g., reminder cap)
- Feature toggles
- Default values (language, style, etc.)

### `credentials.py`
Sensitive keys and tokens (e.g., OpenAI API key).  
**Note:** Not included in version control. Load securely.

### `logger.py`
Custom logging utility used for monitoring behavior, voice generation, and error tracking.  
Consistent formatting across all modules.

### `__init__.py`
Makes the `core` directory a Python module.

---

## Philosophy

The `core/` layer reflects the Samurai principle of clarity:
- Centralized settings
- Clean separation of config and logic
- Secure by design

> 🧠 Think of `core/` as the “inner scroll” — configuration wisdom behind the blade.