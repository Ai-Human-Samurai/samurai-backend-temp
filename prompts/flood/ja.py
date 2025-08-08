from random import choice

# 🟡 UIデバッグ用タイトル（任意）
FLOOD_WARNING_TITLES = {
    "flood_warn_1": "最初の注意",
    "flood_warn_repeat": "繰り返しの注意",
}

# 🔴 警告フレーズ
FLOOD_WARNINGS = {
    "flood_warn_1": [
        "私はここにいる。でも、なぜここに来たのかを忘れないで。",
        "目的を思い出せ。道を見失うな。",
        "私は聞いている。でも、意味のない言葉は話さない。",
    ],
    "flood_warn_repeat": [
        "意味があれば応える。",
        "沈黙もまた答えだ。",
        "言葉に反対しているのではない。空虚に反対している。",
    ],
}

# 🟢 許容される短い入力（挨拶など）
FLOOD_WHITELIST = {"こんにちは", "やあ", "おはよう", "こんばんは", "はい"}

# 🔴 フラッドと見なされる「退屈な」言葉
FLOOD_BORING = {
    "うん", "ああ", "そう", "?", ".", "..", "...", "ふーん", "はは", "へぇ", "まじ", "は?", "うーん", "ふふ", "笑"
}

# ✅ GPTやフィードバック用の定数
PROMPT = {
    "FLOOD_CHECK_PROMPT": (
        "このフレーズが以前のものと意味や構造が似ているかどうかを判断してください。\n\n"
        "ほとんど同じであれば → TRUE\n"
        "意味が新しければ → FALSE\n\n"
        "フレーズ: '{text}'\n\n"
        "答えは TRUE または FALSE"
    ),
    "FLOOD_FEEDBACK": "似たような言葉が続いています。少し時間を置きましょう。",
}


def get_flood_phrase(key: str) -> str | None:
    """
    指定されたキーに対応する警告フレーズをランダムで返す
    """
    return choice(FLOOD_WARNINGS.get(key, []))


def is_whitelist(text: str) -> bool:
    """
    許容される短い入力かどうかを判定する（挨拶など）
    """
    return text.lower() in FLOOD_WHITELIST


def is_boring(text: str) -> bool:
    """
    内容が薄く、フラッドと見なされるかどうかを判定する
    """
    return text.lower() in FLOOD_BORING