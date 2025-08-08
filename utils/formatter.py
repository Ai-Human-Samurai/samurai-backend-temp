import re

def clean_text(text: str) -> str:
    """
    Cleans and normalizes input text: trims, lowers case, removes extra spaces.

    Очищает и нормализует текст:
    - удаляет лишние пробелы
    - приводит к нижнему регистру
    - убирает пробелы по краям

    Example / Пример:
        clean_text("  Привет   МИР ") → "привет мир"
    """
    return re.sub(r'\s+', ' ', text).strip().lower()