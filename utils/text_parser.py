import re

def extract_keywords(text: str, stopwords: list[str] = None) -> list[str]:
    
    stopwords = stopwords or []
    words = re.findall(r"\w+", text.lower())
    return list(set(w for w in words if w not in stopwords))