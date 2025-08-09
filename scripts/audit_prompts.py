#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit Samurai prompts:
- Load all prompt modules under prompts/*
- Enforce style rules (<=2 sentences, banned phrases)
- Validate variant lists (min length)
- Compute metrics (avg variants, offline coverage)
- Detect near-duplicates via cosine on bag-of-words
Exit code != 0 on violations.
"""
import importlib, pkgutil, re, sys, json
from pathlib import Path
from collections import Counter, defaultdict
from math import sqrt

ROOT = Path(__file__).resolve().parents[1]
PROMPTS_DIR = ROOT / "prompts"

# Contract
BANNED = {
    "Меня нельзя назвать. Можно использовать.",
    "Я — инструмент, не маска.",
    "Не для пользы. Для присутствия.",
    "Рядом — значит вовремя.",
    "Я не нужен. Но я рядом.",
    "Нужность проявляется в действии.",
    "Политика — шумный базар.",
    "Меч держу подальше от базара.",
}
MAX_SENTENCES = 2
MIN_VARIANTS = 5  # for variant lists

# Heuristics to identify variant containers
# known_phrases: {"key": {"text": [..]}}
# known_phrases_offline: PROMPT["known_phrases_offline"][key] -> list
# reminders: PHRASES[...] -> list
# sos: PROMPT["SOS_PHRASES"] -> list
# styles: PHRASES_BY_STYLE[style][category] -> list
VARIANT_ROOT_KEYS = {
    ("PHRASES", ),  # reminders/ presence etc.
    ("PROMPT", "SOS_PHRASES"),
    ("PROMPT", "known_phrases_offline"),
    ("PHRASES_BY_STYLE", ),
}
# For known_phrases/ru.py specifically, check ["text"] lists
KNOWN_PHRASES_TEXT_KEY = "text"

def sentences_ok(s: str) -> bool:
    # Simple sentence split by .!?; ignore ellipsis clusters
    parts = [p for p in re.split(r"[.!?]+", s.strip()) if p]
    return len(parts) <= MAX_SENTENCES

def walk_prompt_modules() -> list[str]:
    """Return module paths like 'prompts.known_phrases.ru'."""
    sys.path.insert(0, str(ROOT))
    mods = []
    for p in PROMPTS_DIR.rglob("*.py"):
        rel = p.relative_to(ROOT).as_posix().replace("/", ".")[:-3]
        if rel.endswith("__init__"):
            continue
        mods.append(rel)
    return sorted(mods)

def load_payload(modname: str):
    m = importlib.import_module(modname)
    return {
        "PROMPT": getattr(m, "PROMPT", None),
        "PHRASES": getattr(m, "PHRASES", None),
        "PHRASES_OFFLINE": getattr(m, "PHRASES_OFFLINE", None),
        "PHRASES_BY_STYLE": getattr(m, "PHRASES_BY_STYLE", None),
    }

def iter_strings(obj):
    """Yield all strings found in arbitrary nested containers."""
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from iter_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from iter_strings(v)

def tokenize(s: str) -> Counter:
    # Lowercase, remove punctuation, split by whitespace
    text = re.sub(r"[^\wёЁа-яА-Яa-zA-Z0-9]+", " ", s.lower())
    toks = [t for t in text.split() if t]
    return Counter(toks)

def cosine_sim(c1: Counter, c2: Counter) -> float:
    if not c1 or not c2:
        return 0.0
    inter = set(c1) & set(c2)
    dot = sum(c1[t]*c2[t] for t in inter)
    n1 = sqrt(sum(v*v for v in c1.values()))
    n2 = sqrt(sum(v*v for v in c2.values()))
    return 0.0 if n1 == 0 or n2 == 0 else dot/(n1*n2)

def is_variant_list_path(path_tuple) -> bool:
    # Check if a tuple path starts with a known variant root
    for root in VARIANT_ROOT_KEYS:
        if path_tuple[:len(root)] == root:
            return True
    return False

def iter_lists(obj, path=()):
    """Yield (path_tuple, list_obj)."""
    if isinstance(obj, list):
        yield (path, obj)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from iter_lists(v, path + (k,))

def collect_known_phrases_text_lists(data):
    """For known_phrases/ru.py: find all ['text'] arrays to enforce MIN_VARIANTS."""
    lists = []
    if not isinstance(data, dict):
        return lists
    for k, v in data.items():
        if isinstance(v, dict) and KNOWN_PHRASES_TEXT_KEY in v and isinstance(v[KNOWN_PHRASES_TEXT_KEY], list):
            lists.append((("PHRASES", k, "text"), v[KNOWN_PHRASES_TEXT_KEY]))
    return lists

def main():
    mods = walk_prompt_modules()
    report = {
        "files": len(mods),
        "stats": {"strings": 0, "banned": 0, "too_long": 0, "variant_short": 0, "duplicates": 0},
        "metrics": {
            "avg_variants_known_phrases": None,
            "offline_coverage_percent": None,
            "total_variant_lists": 0
        },
        "violations": []
    }

    # Buffers for metrics
    known_phrases_text_lengths = []
    online_keys = set()
    offline_keys = set()

    # Gather all strings for duplicate check (keep (module, value))
    all_strings = []

    for mod in mods:
        try:
            payload = load_payload(mod)
        except Exception as e:
            report["violations"].append({"module": mod, "type": "import_error", "value": str(e)})
            continue

        containers = [v for v in payload.values() if v is not None]
        if not containers:
            continue

        # Count strings + style checks
        for cont in containers:
            for s in iter_strings(cont):
                report["stats"]["strings"] += 1
                all_strings.append((mod, s))
                if s in BANNED:
                    report["stats"]["banned"] += 1
                    report["violations"].append({"module": mod, "type": "banned_phrase", "value": s})
                if isinstance(s, str) and not sentences_ok(s):
                    report["stats"]["too_long"] += 1
                    report["violations"].append({"module": mod, "type": "too_many_sentences", "value": s})

        # Variant lists length checks
        # 1) known_phrases: enforce len(text) >= MIN_VARIANTS
        if payload["PHRASES"] and isinstance(payload["PHRASES"], dict):
            # Heuristic: if PHRASES is a dict of dicts with 'text' -> list
            text_lists = collect_known_phrases_text_lists(payload["PHRASES"])
            for path, lst in text_lists:
                known_phrases_text_lengths.append(len(lst))
                if len(lst) < MIN_VARIANTS:
                    report["stats"]["variant_short"] += 1
                    report["violations"].append({"module": mod, "type": "too_few_variants", "path": ".".join(path), "len": len(lst)})

        # 2) other variant containers (offline, sos, styles, reminders)
        for name, cont in payload.items():
            if cont is None:
                continue
            for path, lst in iter_lists(cont):
                if not is_variant_list_path((name,) + path):
                    continue
                # Only lists of strings
                if not lst or not all(isinstance(x, str) for x in lst):
                    continue
                report["metrics"]["total_variant_lists"] += 1
                if len(lst) < MIN_VARIANTS:
                    report["stats"]["variant_short"] += 1
                    report["violations"].append({"module": mod, "type": "too_few_variants", "path": ".".join((name,)+path), "len": len(lst)})

        # Metrics: online/offline coverage
        # online keys (known_phrases/ru.py)
        if "prompts.known_phrases." in mod and payload["PHRASES"]:
            for k, v in payload["PHRASES"].items():
                if isinstance(v, dict) and "text" in v:
                    online_keys.add(k)
        # offline keys
        if "prompts.known_phrases_offline." in mod and payload["PROMPT"] and "known_phrases_offline" in payload["PROMPT"]:
            for k in payload["PROMPT"]["known_phrases_offline"].keys():
                offline_keys.add(k)

    # Duplicates (high-similarity pairs)
    # Compare only within strings longer than 10 chars to reduce noise
    vectors = []
    filtered = [(m, s) for (m, s) in all_strings if isinstance(s, str) and len(s) >= 10]
    for _, s in filtered:
        vectors.append(tokenize(s))
    n = len(filtered)
    seen_pairs = set()
    for i in range(n):
        for j in range(i+1, n):
            # quick prefilter: share at least 3 tokens
            if len((set(vectors[i]) & set(vectors[j]))) < 3:
                continue
            sim = cosine_sim(vectors[i], vectors[j])
            if sim >= 0.92:
                pair = (filtered[i][1], filtered[j][1])
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)
                report["stats"]["duplicates"] += 1
                report["violations"].append({
                    "module": f"{filtered[i][0]} ~ {filtered[j][0]}",
                    "type": "near_duplicate",
                    "similarity": round(sim, 3),
                    "a": filtered[i][1],
                    "b": filtered[j][1]
                })

    # Metrics
    if known_phrases_text_lengths:
        report["metrics"]["avg_variants_known_phrases"] = round(sum(known_phrases_text_lengths)/len(known_phrases_text_lengths), 2)
    if online_keys:
        coverage = 100.0 * (len(online_keys & offline_keys) / len(online_keys))
        report["metrics"]["offline_coverage_percent"] = round(coverage, 2)

    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["violations"]:
        sys.exit(1)

if __name__ == "__main__":
    main()