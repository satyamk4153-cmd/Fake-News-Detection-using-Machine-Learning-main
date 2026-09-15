"""Text cleaning and normalization pipelines for TruthLens."""

import re
import unicodedata
from typing import List


def normalize_unicode(text: str) -> str:
    """Normalize text using Unicode NFKC form to unify accented and compatibility characters."""
    if not text:
        return ""
    return unicodedata.normalize("NFKC", text)


def strip_html(text: str) -> str:
    """Safely strip HTML tags, script, and style blocks from raw text."""
    if not text:
        return ""
    # Remove script and style tags completely
    cleaned = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    # Strip remaining HTML tags
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    return cleaned


def normalize_whitespace(text: str) -> str:
    """Collapse excessive newlines, tabs, and duplicate spaces into clean single spaces."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def segment_sentences(text: str) -> List[str]:
    """Segment text into coherent sentences using punctuation boundary rules."""
    if not text:
        return []
    cleaned = normalize_unicode(text)
    # Match sentence boundaries while preserving acronyms (e.g., U.S., Dr., etc.)
    raw_sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'‘“])", cleaned)
    sentences = [s.strip() for s in raw_sentences if s.strip() and len(s.strip()) > 3]
    return sentences if sentences else [cleaned.strip()]


def clean_text_traditional(text: str) -> str:
    """Preprocessing pipeline tailored for Traditional ML (TF-IDF / N-grams).
    
    Performs Unicode normalization, HTML stripping, URL tokenization,
    lowercasing, and cleanup of excessive symbols while retaining alphanumeric words.
    """
    if not text:
        return ""
    t = normalize_unicode(text)
    t = strip_html(t)
    # Replace URLs with a semantic token
    t = re.sub(r"https?://\S+|www\.\S+", " [URL] ", t)
    # Lowercase for traditional bag-of-words
    t = t.lower()
    # Replace non-alphanumeric except spaces and basic punctuation
    t = re.sub(r"[^a-z0-9\s.,!?'\"-]", " ", t)
    t = normalize_whitespace(t)
    return t


def clean_text_transformer(text: str) -> str:
    """Preprocessing pipeline for Transformer models.
    
    Preserves casing, punctuation, quote structures, and paragraph flow
    while stripping HTML and normalizing unicode anomalies.
    """
    if not text:
        return ""
    t = normalize_unicode(text)
    t = strip_html(t)
    # Standardize curly quotes to straight quotes
    t = t.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    t = normalize_whitespace(t)
    return t
