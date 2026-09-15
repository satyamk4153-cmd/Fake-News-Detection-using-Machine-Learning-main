"""Claim Extraction Subsystem for TruthLens.

Segments articles into sentences, detects candidate claims,
classifies claim types (factual, numerical, attribution, causal, opinion, prediction),
and ranks them for fact-checking review without mislabeling opinions as factual claims.
"""

import re
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
from ml.preprocessing.text_cleaner import segment_sentences


@dataclass
class ExtractedClaim:
    claim_id: str
    text: str
    sentence_index: int
    claim_type: str
    confidence: float
    verification_priority: str  # High, Medium, Low
    keywords: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ClaimExtractor:
    """Extracts verifiable claims from structured article text."""

    OPINION_TRIGGERS = [
        re.compile(r'\b(i believe|i think|in my view|in our opinion|feel that|seems like|beautiful|disgusting|wonderful|terrible|wicked|evil|morally)\b', re.I)
    ]
    
    NUMERICAL_PATTERNS = [
        re.compile(r'\b\d+(\.\d+)?%?\b'),
        re.compile(r'\$\d+(\.\d+)?\b'),
        re.compile(r'\b(million|billion|trillion|hundred|thousand|percent)\b', re.I)
    ]

    ATTRIBUTION_PATTERNS = [
        re.compile(r'\b(said|stated|reported|announced|claimed|testified|noted|argued|declared)\b', re.I),
        re.compile(r'\baccording to\b', re.I)
    ]

    CAUSAL_PATTERNS = [
        re.compile(r'\b(caused by|resulted in|led to|due to|because of|provoked|triggered by)\b', re.I)
    ]

    PREDICTION_PATTERNS = [
        re.compile(r'\b(will be|projected to|expected to|anticipated to|predicts that|forecasts)\b', re.I)
    ]

    def extract_claims(self, text: str, max_claims: int = 5) -> List[ExtractedClaim]:
        sentences = segment_sentences(text)
        claims: List[ExtractedClaim] = []

        for idx, sentence in enumerate(sentences):
            s_clean = sentence.strip()
            if len(s_clean) < 25:
                continue

            # Determine claim type
            is_opinion = any(p.search(s_clean) for p in self.OPINION_TRIGGERS)
            is_numerical = any(p.search(s_clean) for p in self.NUMERICAL_PATTERNS)
            is_attribution = any(p.search(s_clean) for p in self.ATTRIBUTION_PATTERNS)
            is_causal = any(p.search(s_clean) for p in self.CAUSAL_PATTERNS)
            is_prediction = any(p.search(s_clean) for p in self.PREDICTION_PATTERNS)

            if is_opinion:
                claim_type = "opinion"
                confidence = 0.70
                priority = "Low"
            elif is_numerical:
                claim_type = "numerical"
                confidence = 0.88
                priority = "High"
            elif is_attribution:
                claim_type = "attribution"
                confidence = 0.84
                priority = "High"
            elif is_causal:
                claim_type = "causal"
                confidence = 0.80
                priority = "High"
            elif is_prediction:
                claim_type = "prediction"
                confidence = 0.75
                priority = "Medium"
            else:
                claim_type = "factual"
                confidence = 0.78
                priority = "Medium"

            # Extract distinct keywords
            words = [w.lower() for w in re.findall(r'\b[a-zA-Z]{4,}\b', s_clean)]
            unique_kws = list(dict.fromkeys(words))[:4]

            claim = ExtractedClaim(
                claim_id=f"claim-{idx+1}",
                text=s_clean,
                sentence_index=idx,
                claim_type=claim_type,
                confidence=confidence,
                verification_priority=priority,
                keywords=unique_kws
            )
            claims.append(claim)

        # Sort priority: numerical/factual first, opinion last
        type_weights = {"numerical": 3, "causal": 3, "attribution": 2, "factual": 2, "prediction": 1, "opinion": 0}
        claims.sort(key=lambda c: (type_weights.get(c.claim_type, 0), c.confidence), reverse=True)

        return claims[:max_claims]
