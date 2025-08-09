# utils/lang_tools.py

def detect_language(text: str) -> str:
   
    if not text:
        return "en"  # default fallback

    cyrillic = sum(1 for c in text if "а" <= c.lower() <= "я")
    latin = sum(1 for c in text if "a" <= c.lower() <= "z")

    return "ru" if cyrillic > latin else "en"