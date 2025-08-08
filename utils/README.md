🛠️ utils/ — Utility Functions for Samurai Core
This folder contains low-level utility functions that support the Samurai system. They are small, isolated helpers that are used across different modules (voice, behavior, reminders, etc).

📂 Files and Purpose
File	Description
formatter.py	Contains basic text cleaning tools (e.g., remove newlines, trim whitespace, lowercase).
lang_tools.py	Lightweight language detection (currently detects Russian vs. English using character heuristics). Used for voice and behavior modules.
text_parser.py	Experimental keyword extractor (basic version). Not actively used, but may support NLP features in the future.

⚙️ Language Detection Logic (in lang_tools.py)
python
Копировать
Редактировать
def detect_language(text: str) -> str:
    cyrillic = sum(1 for c in text if "а" <= c.lower() <= "я")
    latin = sum(1 for c in text if "a" <= c.lower() <= "z")
    return "ru" if cyrillic > latin else "en"
Fast, offline

Ideal for low-resource environments or mobile offline apps

Can be upgraded to langdetect or fasttext if more languages are added (es, fr, tr, etc.)

✅ Notes
All utils are stateless and reusable.

Avoid tight coupling with other modules — these are meant to be stable building blocks.

When adding new utilities, prefer pure functions that don’t rely on app context.

