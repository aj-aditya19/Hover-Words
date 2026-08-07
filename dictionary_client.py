import os
import re
import sys
import sqlite3


def _resource_path(relative_path: str) -> str:
    """
    Resolves a path to a bundled resource, whether running from source
    or as a PyInstaller-frozen exe (where bundled files are extracted
    under sys._MEIPASS at runtime).
    """
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)


_DB_PATH = _resource_path("offline_dictionary.db")

# Simple in-memory cache so repeat lookups of the same word (or hovering
# back and forth) don't hit the database again.
_cache = {}

# Some dictionary entries (inflected word forms) just point to a base
# word instead of giving an actual meaning, e.g. "simple past tense of
# awake" for "awoke", or "plural of cat" for "cats". When we hit one of
# these, we resolve it to the base word's real definition instead, so
# the tooltip always shows an actual meaning.
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
    """If `definition_text` is just a grammatical pointer to another
    word (e.g. 'simple past tense of awake'), returns that base word.
    Otherwise returns None."""
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
    """
    Looks up a word in the bundled offline dictionary (no internet
    required - sourced from Wiktionary via the open-dictionary
    project, ~260k English words). Returns a dict: {'word', 'phonetic',
    'part_of_speech', 'definition', 'example'} or None if not found.

    If the stored entry is just a grammatical reference to another
    word (e.g. an inflected form), this follows it once to return the
    base word's real meaning instead.
    """
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