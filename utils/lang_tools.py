# utils/lang_tools.py

def detect_language(text: str) -> str:
    """
    Lightweight offline language detection for short text inputs.

    Лёгкая offline-функция для определения языка текста.
    Поддерживает только "ru" (кириллица) и "en" (латиница).

    Returns / Возвращает:
        - "ru" if text contains more Cyrillic characters
        - "en" otherwise (or if input is empty)

    Example / Пример:
        detect_language("Привет, как дела?") → "ru"
        detect_language("Hello world!") → "en"
    """
    if not text:
        return "en"  # default fallback

    cyrillic = sum(1 for c in text if "а" <= c.lower() <= "я")
    latin = sum(1 for c in text if "a" <= c.lower() <= "z")

    return "ru" if cyrillic > latin else "en"