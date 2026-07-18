COMMON_WORDS = {
    "the", "and", "for", "are", "but", "not", "you", "all", "any", "can",
    "had", "her", "was", "one", "our", "out", "day", "get", "has", "him",
    "his", "how", "man", "new", "now", "old", "see", "two", "way", "who",
    "boy", "did", "its", "let", "put", "say", "she", "too", "use", "that",
    "with", "have", "this", "will", "your", "from", "they", "know", "want",
    "been", "good", "much", "some", "time", "very", "when", "come", "here",
    "just", "like", "long", "make", "many", "over", "such", "take", "than",
    "them", "well", "were", "what", "about", "after", "again", "could",
    "every", "first", "found", "great", "house", "large", "learn", "never",
    "other", "place", "right", "small", "sound", "spell", "still", "study",
    "their", "there", "these", "thing", "think", "three", "water", "where",
    "which", "world", "would", "write", "because", "between", "through",
    "should", "people", "little", "before", "always", "around", "asked",
    "began", "being", "below", "black", "book", "both", "came", "does",
    "each", "eyes", "gave", "give", "going", "hand", "head", "help", "high",
    "into", "keep", "kind", "knew", "land", "left", "light", "line", "live",
    "look", "made", "mean", "might", "more", "most", "mother", "must",
    "name", "need", "next", "number", "only", "open", "own", "page",
    "paper", "part", "picture", "play", "point", "read", "real", "room",
    "said", "same", "school", "seem", "sentence", "since", "side", "story",
    "tell", "thought", "today", "together", "took", "under", "until", "used",
    "walk", "want", "watch", "went", "while", "why", "words", "work",
    "year", "years", "young",
}


def is_common(word: str) -> bool:
    return word.lower() in COMMON_WORDS
