import os
import re
import sys
import sqlite3


def _resource_path(relative_path: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)


_DB_PATH = _resource_path("offline_dictionary.db")

_FORM_OF_PATTERNS = [
    re.compile(r"^simple past tense and past participle of ([a-zA-Z\-]+)\.?$", re.I),
    re.compile(r"^simple past tense of ([a-zA-Z\-]+)\.?$", re.I),
    re.compile(r"^past participle of ([a-zA-Z\-]+)\.?$", re.I),
    re.compile(r"^present participle of ([a-zA-Z\-]+)\.?$", re.I),
    re.compile(r"^plural of ([a-zA-Z\-]+)\.?$", re.I),
    re.compile(r"^alternative form of ([a-zA-Z\-]+)\.?$", re.I),
    re.compile(r"^alternative spelling of ([a-zA-Z\-]+)\.?$", re.I),
    re.compile(r"^archaic form of ([a-zA-Z\-]+)\.?$", re.I),
    re.compile(r"^dated form of ([a-zA-Z\-]+)\.?$", re.I),
    re.compile(r"^synonym of ([a-zA-Z\-]+)\.?$", re.I),
    re.compile(r"^third-person singular simple present indicative form of ([a-zA-Z\-]+)\.?$", re.I),
    re.compile(r"^comparative form of ([a-zA-Z\-]+):.*$", re.I),
    re.compile(r"^superlative form of ([a-zA-Z\-]+):.*$", re.I),
]


def _resolve_form_reference(definition_text: str):
    text = definition_text.strip()
    for pattern in _FORM_OF_PATTERNS:
        match = pattern.match(text)
        if match:
            return match.group(1)
    return None


def _lookup_row(clean_word: str):
    try:
        conn = sqlite3.connect(_DB_PATH)
        row = conn.execute(
            "SELECT part_of_speech, definition, example FROM words WHERE word = ?",
            (clean_word,),
        ).fetchone()
        conn.close()
        return row
    except sqlite3.Error:
        return None


def get_definition(word: str, _depth: int = 0):
    clean = word.strip().strip(".,;:!?\"'()[]{}").upper()
    if not clean:
        return None

    if clean in _cache:
        return _cache[clean]

    result = None
    row = _lookup_row(clean)

    if row is not None:
        part_of_speech, definition, example = row

        base_word = _resolve_form_reference(definition) if _depth == 0 else None
        if base_word and base_word.upper() != clean:
            resolved = get_definition(base_word, _depth=1)
            if resolved:
                result = {
                    "word": word,
                    "phonetic": "",
                    "part_of_speech": resolved["part_of_speech"],
                    "definition": resolved["definition"],
                    "example": resolved["example"],
                }

        if result is None:
            result = {
                "word": word,
                "phonetic": "",
                "part_of_speech": part_of_speech or "",
                "definition": definition,
                "example": example or "",
            }

    _cache[clean] = result
    return result