"""Linguistic and structural feature extractor for news credibility analysis."""

import re
import math
from typing import Dict, List, Any
import numpy as np
import pandas as pd

# Lexicons for indicators
EMOTIONAL_WORDS = {
    "shocking", "outrageous", "unbelievable", "horrifying", "devastating",
    "furious", "terrifying", "miracle", "insane", "explosive", "scandalous",
    "disaster", "catastrophe", "nightmare", "fury", "panic", "chaos",
    "traitor", "corrupt", "wicked", "evil", "disgrace", "shameful", "hero"
}

SENSATIONAL_WORDS = {
    "bombshell", "exposed", "jaw-dropping", "must-see", "breaking", "unreal",
    "secret", "conspiracy", "hidden", "coverup", "banned", "censored",
    "unmasked", "they-dont-want-you-to-know", "leaked", "shock", "proof",
    "urgent", "alert", "hoax", "truth", "revealed", "destroyed", "slammed"
}

MODAL_VERBS = {
    "might", "could", "would", "may", "allegedly", "supposedly", "reportedly",
    "purportedly", "apparently", "seemingly", "claimed", "claims"
}

FIRST_PERSON = {"i", "me", "my", "mine", "myself", "we", "us", "our", "ours", "ourselves"}
SECOND_PERSON = {"you", "your", "yours", "yourself", "yourselves"}

ATTRIBUTION_PATTERNS = [
    re.compile(r'\baccording to\b', re.I),
    re.compile(r'\bstated that\b', re.I),
    re.compile(r'\breported that\b', re.I),
    re.compile(r'\bciting\b', re.I),
    re.compile(r'\bofficials said\b', re.I),
    re.compile(r'\bspokesperson said\b', re.I),
    re.compile(r'\bresearchers found\b', re.I),
    re.compile(r'\bstudy published\b', re.I),
]

CITATION_PATTERNS = [
    re.compile(r'\bhttps?://\S+'),
    re.compile(r'\[\d+\]'),
    re.compile(r'\(\w+ et al\.,? \d{4}\)', re.I),
    re.compile(r'\bdoi:\S+', re.I),
]


class LinguisticFeatureExtractor:
    """Extracts linguistic, emotional, and structural signals from text."""

    FEATURE_NAMES = [
        "word_count",
        "sentence_count",
        "avg_sentence_length",
        "lexical_diversity",
        "uppercase_ratio",
        "exclamation_density",
        "question_density",
        "punctuation_density",
        "emotional_word_density",
        "sensational_word_density",
        "modal_verb_density",
        "first_person_density",
        "second_person_density",
        "quote_count",
        "number_density",
        "attribution_count",
        "citation_count",
        "paragraph_count",
        "capitalized_word_anomalies",
        "char_count"
    ]

    @classmethod
    def get_feature_names(cls) -> List[str]:
        return cls.FEATURE_NAMES.copy()

    def extract_dict(self, text: str, headline: str = "") -> Dict[str, float]:
        """Extract structured linguistic feature dictionary."""
        combined_text = f"{headline} {text}".strip() if headline else text.strip()
        char_count = len(combined_text)
        if char_count == 0:
            return {name: 0.0 for name in self.FEATURE_NAMES}

        # Tokenization
        words = re.findall(r"\b[a-zA-Z0-9'-]+\b", combined_text)
        word_count = len(words)
        lower_words = [w.lower() for w in words]

        # Sentence segmentation
        raw_sentences = [s.strip() for s in re.split(r'[.!?]+', combined_text) if s.strip()]
        sentence_count = max(len(raw_sentences), 1)

        # Paragraphs
        paragraphs = [p.strip() for p in combined_text.split("\n\n") if p.strip()]
        paragraph_count = max(len(paragraphs), 1)

        # Calculations
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0.0
        unique_words = set(lower_words)
        lexical_diversity = len(unique_words) / word_count if word_count > 0 else 0.0

        # Capitalization
        uppercase_chars = sum(1 for c in combined_text if c.isupper())
        uppercase_ratio = uppercase_chars / char_count if char_count > 0 else 0.0
        
        # Capitalization anomalies (e.g., words in ALL CAPS with > 2 chars)
        all_caps_words = sum(1 for w in words if len(w) > 2 and w.isupper())
        capitalized_word_anomalies = all_caps_words / word_count if word_count > 0 else 0.0

        # Punctuation counts
        exclamations = combined_text.count("!")
        questions = combined_text.count("?")
        total_punct = sum(1 for c in combined_text if c in "!?,;:-'\"()[]")

        exclamation_density = (exclamations / word_count * 100) if word_count > 0 else 0.0
        question_density = (questions / word_count * 100) if word_count > 0 else 0.0
        punctuation_density = (total_punct / char_count * 100) if char_count > 0 else 0.0

        # Indicators
        emotional_count = sum(1 for w in lower_words if w in EMOTIONAL_WORDS)
        emotional_density = (emotional_count / word_count * 100) if word_count > 0 else 0.0

        sensational_count = sum(1 for w in lower_words if w in SENSATIONAL_WORDS)
        sensational_density = (sensational_count / word_count * 100) if word_count > 0 else 0.0

        modal_count = sum(1 for w in lower_words if w in MODAL_VERBS)
        modal_density = (modal_count / word_count * 100) if word_count > 0 else 0.0

        first_p_count = sum(1 for w in lower_words if w in FIRST_PERSON)
        first_p_density = (first_p_count / word_count * 100) if word_count > 0 else 0.0

        second_p_count = sum(1 for w in lower_words if w in SECOND_PERSON)
        second_p_density = (second_p_count / word_count * 100) if word_count > 0 else 0.0

        quote_count = combined_text.count('"') + combined_text.count('“') + combined_text.count('”')
        number_count = sum(1 for w in words if any(c.isdigit() for c in w))
        number_density = (number_count / word_count * 100) if word_count > 0 else 0.0

        attribution_count = sum(len(p.findall(combined_text)) for p in ATTRIBUTION_PATTERNS)
        citation_count = sum(len(p.findall(combined_text)) for p in CITATION_PATTERNS)

        return {
            "word_count": float(word_count),
            "sentence_count": float(sentence_count),
            "avg_sentence_length": round(float(avg_sentence_length), 2),
            "lexical_diversity": round(float(lexical_diversity), 4),
            "uppercase_ratio": round(float(uppercase_ratio), 4),
            "exclamation_density": round(float(exclamation_density), 4),
            "question_density": round(float(question_density), 4),
            "punctuation_density": round(float(punctuation_density), 4),
            "emotional_word_density": round(float(emotional_density), 4),
            "sensational_word_density": round(float(sensational_density), 4),
            "modal_verb_density": round(float(modal_density), 4),
            "first_person_density": round(float(first_p_density), 4),
            "second_person_density": round(float(second_p_density), 4),
            "quote_count": float(quote_count),
            "number_density": round(float(number_density), 4),
            "attribution_count": float(attribution_count),
            "citation_count": float(citation_count),
            "paragraph_count": float(paragraph_count),
            "capitalized_word_anomalies": round(float(capitalized_word_anomalies), 4),
            "char_count": float(char_count)
        }

    def extract_vector(self, text: str, headline: str = "") -> np.ndarray:
        """Extract features as a 1D numpy array."""
        feat_dict = self.extract_dict(text, headline)
        return np.array([feat_dict[name] for name in self.FEATURE_NAMES], dtype=np.float32)

    def extract_dataframe(self, texts: List[str], headlines: List[str] = None) -> pd.DataFrame:
        """Extract features for a list of texts into a pandas DataFrame."""
        if headlines is None:
            headlines = [""] * len(texts)
        rows = [self.extract_dict(t, h) for t, h in zip(texts, headlines)]
        return pd.DataFrame(rows, columns=self.FEATURE_NAMES)


def extract_all_features(text: str, headline: str = "") -> Dict[str, float]:
    """Convenience helper to extract features as dict."""
    extractor = LinguisticFeatureExtractor()
    return extractor.extract_dict(text, headline)
