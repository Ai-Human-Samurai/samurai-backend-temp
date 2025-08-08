import re

def extract_keywords(text: str, stopwords: list[str] = None) -> list[str]:
    """
    Extracts keywords from the input text, removing stopwords and duplicates.

    Разбивает текст на ключевые слова, убирает стоп-слова и дубликаты.

    Example / Пример:
        extract_keywords("Привет, как дела?", ["как"]) → ["привет", "дела"]
    """
    stopwords = stopwords or []
    words = re.findall(r"\w+", text.lower())
    return list(set(w for w in words if w not in stopwords))