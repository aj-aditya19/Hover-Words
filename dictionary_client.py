import requests

API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/{}"

# Simple in-memory cache so we don't re-hit the API for words we've
# already looked up in this session.
_cache = {}


def get_definition(word: str):
    """
    Looks up a word's definition. Returns a dict:
    {'word', 'phonetic', 'part_of_speech', 'definition', 'example'}
    or None if no definition was found / the request failed.
    """
    clean = word.lower().strip(".,;:!?\"'()[]{}")
    if not clean:
        return None

    if clean in _cache:
        return _cache[clean]

    try:
        resp = requests.get(API_URL.format(clean), timeout=3)
        if resp.status_code != 200:
            _cache[clean] = None
            return None

        data = resp.json()
        entry = data[0]
        meaning = entry["meanings"][0]
        definition_block = meaning["definitions"][0]

        result = {
            "word": entry.get("word", clean),
            "phonetic": entry.get("phonetic", ""),
            "part_of_speech": meaning.get("partOfSpeech", ""),
            "definition": definition_block.get("definition", ""),
            "example": definition_block.get("example", ""),
        }
        _cache[clean] = result
        return result

    except (requests.RequestException, KeyError, IndexError, ValueError):
        _cache[clean] = None
        return None
