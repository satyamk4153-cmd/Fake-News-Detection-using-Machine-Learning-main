"""Text highlighting and token influence visualization for TruthLens."""

import re
from dataclasses import dataclass, asdict
from typing import List, Dict, Any


@dataclass
class HighlightedSpan:
    text: str
    start_char: int
    end_char: int
    influence_level: str  # 'high', 'medium', 'low'
    direction: str        # 'supports_misleading', 'supports_credible'
    weight: float
    explanation: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TextHighlighter:
    """Highlights key phrases contributing significantly to model classifications."""

    # High emotional/sensational keywords that drive misleading scores
    SENSATIONAL_INDICATORS = {
        "bombshell": (0.9, "Sensational framing"),
        "shocking": (0.85, "Emotional intensifier"),
        "whistleblowers": (0.6, "Unverified sourcing rhetoric"),
        "exposed": (0.75, "Dramatic accusation cue"),
        "miracle": (0.85, "Extraordinary medical claim"),
        "cabal": (0.95, "Conspiracy narrative marker"),
        "nanochips": (0.95, "Techno-conspiracy marker"),
        "insane": (0.7, "Hyperbolic language"),
        "jaw-dropping": (0.8, "Sensational framing"),
        "secret": (0.55, "Concealment rhetoric"),
        "corrupt": (0.65, "Ad hominem characterization"),
        "treason": (0.85, "Extreme political rhetoric"),
        "staged": (0.8, "Hoax narrative marker"),
        "hoax": (0.85, "Disinformation accusatory cue"),
    }

    # Journalistic attribution keywords that support credibility
    CREDIBLE_INDICATORS = {
        "according to": (0.85, "Explicit source attribution"),
        "stated that": (0.75, "Formal attribution"),
        "reported that": (0.7, "Standard journalistic attribution"),
        "published in": (0.85, "Peer-reviewed or public citation"),
        "officials said": (0.75, "Named institutional source"),
        "data showed": (0.8, "Empirical reference"),
        "researchers found": (0.8, "Scientific study attribution"),
        "clinical trial": (0.9, "Formal methodological citation"),
    }

    def generate_highlights(self, text: str) -> List[HighlightedSpan]:
        spans: List[HighlightedSpan] = []
        lower_text = text.lower()

        # 1. Search for sensational signals
        for phrase, (weight, reason) in self.SENSATIONAL_INDICATORS.items():
            pattern = re.compile(rf'\b{re.escape(phrase)}\b', re.IGNORECASE)
            for match in pattern.finditer(text):
                level = "high" if weight >= 0.8 else "medium"
                spans.append(HighlightedSpan(
                    text=match.group(0),
                    start_char=match.start(),
                    end_char=match.end(),
                    influence_level=level,
                    direction="supports_misleading",
                    weight=weight,
                    explanation=reason
                ))

        # 2. Search for credible signals
        for phrase, (weight, reason) in self.CREDIBLE_INDICATORS.items():
            pattern = re.compile(rf'\b{re.escape(phrase)}\b', re.IGNORECASE)
            for match in pattern.finditer(text):
                level = "high" if weight >= 0.8 else "medium"
                spans.append(HighlightedSpan(
                    text=match.group(0),
                    start_char=match.start(),
                    end_char=match.end(),
                    influence_level=level,
                    direction="supports_credible",
                    weight=weight,
                    explanation=reason
                ))

        # 3. Detect excessive capitalization anomalies (words in ALL CAPS with > 2 chars)
        for match in re.finditer(r'\b[A-Z]{3,}\b', text):
            word = match.group(0)
            if word not in {"USA", "WHO", "NASA", "FAA", "EPA", "NTSB", "UN", "EU", "JWST", "GDP"}:
                spans.append(HighlightedSpan(
                    text=word,
                    start_char=match.start(),
                    end_char=match.end(),
                    influence_level="medium",
                    direction="supports_misleading",
                    weight=0.7,
                    explanation="All-caps formatting anomaly"
                ))

        # Sort spans by position and resolve overlapping intervals
        spans.sort(key=lambda s: s.start_char)
        non_overlapping = []
        last_end = -1
        for s in spans:
            if s.start_char >= last_end:
                non_overlapping.append(s)
                last_end = s.end_char

        return non_overlapping
