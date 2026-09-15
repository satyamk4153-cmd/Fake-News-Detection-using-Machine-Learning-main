"""Language detection subsystem for TruthLens.

Enforces language validation to ensure English content is fed into English-calibrated models,
rejecting unsupported languages with explicit feedback.
"""

import re
from typing import Dict, Tuple

# Core English function words and stopword anchors
COMMON_ENGLISH_WORDS = {
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "i",
    "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
    "this", "but", "his", "by", "from", "they", "we", "say", "her",
    "she", "or", "an", "will", "my", "one", "all", "would", "there",
    "their", "what", "so", "up", "out", "if", "about", "who", "get",
    "which", "go", "me", "when", "make", "can", "like", "time", "no",
    "just", "him", "know", "take", "people", "into", "year", "your",
    "good", "some", "could", "them", "see", "other", "than", "then",
    "now", "look", "only", "come", "its", "over", "think", "also",
    "back", "after", "use", "two", "how", "our", "work", "first",
    "well", "way", "even", "new", "want", "because", "any", "these",
    "give", "day", "most", "us", "is", "was", "are", "been", "were"
}


def detect_language(text: str) -> Dict[str, any]:
    """Detect if the primary language of the text is English.
    
    Returns a dictionary with:
        language: 'en' or 'unsupported'
        confidence: float between 0.0 and 1.0
        supported: bool
        message: explanation string
    """
    if not text or len(text.strip()) < 10:
        return {
            "language": "unknown",
            "confidence": 0.0,
            "supported": False,
            "message": "Text is too short to reliably determine language."
        }
    
    # Extract lowercased alphabetic tokens
    tokens = re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())
    if not tokens:
        return {
            "language": "unknown",
            "confidence": 0.0,
            "supported": False,
            "message": "No alphabetic tokens found in the input."
        }
        
    total_tokens = len(tokens)
    english_hits = sum(1 for tok in tokens if tok in COMMON_ENGLISH_WORDS)
    ratio = english_hits / total_tokens

    # Check non-latin script characters (e.g. Cyrillic, CJK, Arabic, etc.)
    non_latin = len(re.findall(r"[^\x00-\x7F\u0080-\u024F]", text))
    total_chars = max(len(text), 1)
    non_latin_ratio = non_latin / total_chars

    if non_latin_ratio > 0.30:
        return {
            "language": "non-latin",
            "confidence": round(non_latin_ratio, 3),
            "supported": False,
            "message": "Non-Latin script detected. TruthLens currently only supports English text."
        }

    # For English text with >15 tokens, common stopword ratio is typically >= 0.15
    # For very short headlines, even 1 or 2 words might match
    if total_tokens >= 8:
        is_english = ratio >= 0.12
    else:
        is_english = english_hits >= 1 or ratio >= 0.10

    confidence = min(1.0, round(ratio / 0.35, 2)) if is_english else round(1.0 - ratio, 2)

    return {
        "language": "en" if is_english else "unsupported",
        "confidence": confidence,
        "supported": is_english,
        "message": "English language confirmed." if is_english else "Content appears to be in an unsupported language. TruthLens currently supports English."
    }


def is_english_supported(text: str) -> Tuple[bool, str]:
    """Convenience helper returning (is_supported, message)."""
    res = detect_language(text)
    return res["supported"], res["message"]
