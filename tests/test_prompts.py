# -*- coding: utf-8 -*-
"""
Prompt integrity tests
----------------------
- Import all prompt modules under prompts/*
- Ensure PROMPT/PHRASES/PHRASES_BY_STYLE/ALL_KNOWN_PHRASES structures exist
- Enforce style (<= 2 sentences) for user-facing short phrases
- Enforce no banned phrases
- Validate min variants for known containers
"""

import importlib
import re
import sys
from pathlib import Path
from typing import Any, Iterator, Tuple, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

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

EXEMPT_PATH_KEYS = {
    "SYSTEM_PROMPT",
    "FLOOD_CHECK_PROMPT",
    "REMINDER_PARSE_SYSTEM",
    "REMINDER_PARSE_EXAMPLE",
    "SEMANTIC_FILTER_PROMPT",
    "GENERATOR_SYSTEM",
    "SYSTEM_SOS_PROMPT",
}

MAX_SENTENCES = 2
MIN_VARIANTS = 5

def sentences_ok(s: str) -> bool:
    """
    - OK if <= 2 sentences
    - OK if triad (==3 sentences) and total words <= 16
    """
    sent = [p.strip() for p in re.split(r"[.!?]+", s.strip()) if p.strip()]
    if len(sent) <= 2:
        return True
    if len(sent) == 3:
        total_words = sum(len(x.split()) for x in sent)
        return total_words <= 16
    return False

def iter_strings_with_path(obj: Any, path: Tuple[str, ...] = ()) -> Iterator[Tuple[Tuple[str, ...], str]]:
    """Yield (path, string) for all strings in nested dict/list structures."""
    if isinstance(obj, str):
        yield path, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from iter_strings_with_path(v, path + (str(k),))
    elif isinstance(obj, list):
        for idx, v in enumerate(obj):
            yield from iter_strings_with_path(v, path + (str(idx),))

def test_prompts_integrity_and_style():
    modules: List[str] = []
    for p in (ROOT / "prompts").rglob("*.py"):
        rel = p.relative_to(ROOT).as_posix().replace("/", ".")[:-3]
        if rel.endswith("__init__"):
            continue
        modules.append(rel)

    assert modules, "No prompt modules found under prompts/"

    total_strings = 0

    for name in modules:
        m = importlib.import_module(name)
        data = (
            getattr(m, "PROMPT", None)
            or getattr(m, "PHRASES", None)
            or getattr(m, "PHRASES_BY_STYLE", None)
            or getattr(m, "ALL_KNOWN_PHRASES", None)   # ← added
        )
        assert data is not None, f"{name}: missing PROMPT/PHRASES/PHRASES_BY_STYLE/ALL_KNOWN_PHRASES"

        for path, s in iter_strings_with_path(data):
            total_strings += 1
            assert s not in BANNED, f"{name}:{'.'.join(path)} banned phrase: {s!r}"
            if any(seg in EXEMPT_PATH_KEYS for seg in path):
                continue
            assert sentences_ok(s), f"{name}:{'.'.join(path)} too many sentences: {s!r}"

    assert total_strings > 100, "Suspiciously low number of strings; check prompt loading"

def test_min_variants_where_applicable():
    """Enforce MIN_VARIANTS for common variant containers."""

    # known_phrases (online)
    try:
        kp = importlib.import_module("prompts.known_phrases.ru")
        PHRASES = getattr(kp, "PHRASES", {})
        if isinstance(PHRASES, dict):
            for k, v in PHRASES.items():
                if isinstance(v, dict) and "text" in v and isinstance(v["text"], list):
                    assert len(v["text"]) >= MIN_VARIANTS, f"known_phrases:{k} < {MIN_VARIANTS}"
    except ModuleNotFoundError:
        pass

    # known_phrases_offline
    try:
        kpo = importlib.import_module("prompts.known_phrases_offline.ru")
        payload = getattr(kpo, "PROMPT", {})
        if isinstance(payload, dict):
            off = payload.get("known_phrases_offline", {})
            if isinstance(off, dict):
                for k, lst in off.items():
                    if isinstance(lst, list):
                        assert len(lst) >= MIN_VARIANTS, f"known_phrases_offline:{k} < {MIN_VARIANTS}"
    except ModuleNotFoundError:
        pass

    # sos
    try:
        sos = importlib.import_module("prompts.sos.ru")
        prompt = getattr(sos, "PROMPT", {})
        lst = prompt.get("SOS_PHRASES", [])
        if isinstance(lst, list) and lst:
            assert len(lst) >= MIN_VARIANTS, "sos.SOS_PHRASES has too few variants"
    except ModuleNotFoundError:
        pass

    # styles
    try:
        styles = importlib.import_module("prompts.styles.ru")
        by_style = getattr(styles, "PHRASES_BY_STYLE", {})
        if isinstance(by_style, dict):
            for style, buckets in by_style.items():
                if not isinstance(buckets, dict):
                    continue
                for bk, lst in buckets.items():
                    if isinstance(lst, list) and lst:
                        assert len(lst) >= MIN_VARIANTS, f"styles.{style}.{bk} < {MIN_VARIANTS}"
    except ModuleNotFoundError:
        pass

    # reminders (support both PHRASES and ALL_KNOWN_PHRASES)
    try:
        rem = importlib.import_module("prompts.reminders.ru")
        PH = getattr(rem, "PHRASES", None)
        if isinstance(PH, dict) and PH:
            for k, lst in PH.items():
                if isinstance(lst, list) and lst:
                    assert len(lst) >= MIN_VARIANTS, f"reminders.{k} < {MIN_VARIANTS}"

        AKP = getattr(rem, "ALL_KNOWN_PHRASES", None)
        if isinstance(AKP, dict) and "ru" in AKP:
            for k, v in AKP["ru"].items():
                if isinstance(v, dict) and "text" in v and isinstance(v["text"], list):
                    assert len(v["text"]) >= MIN_VARIANTS, f"reminders.AKP:{k} < {MIN_VARIANTS}"
    except ModuleNotFoundError:
        pass