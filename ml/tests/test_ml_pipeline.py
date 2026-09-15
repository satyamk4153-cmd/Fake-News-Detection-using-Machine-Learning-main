"""ML Pipeline, Preprocessing, Feature Extraction, and Inference Tests."""

import pytest
import numpy as np
from pathlib import Path

from ml.preprocessing.text_cleaner import clean_text_traditional, clean_text_transformer, segment_sentences, strip_html
from ml.preprocessing.language_detector import detect_language
from ml.features.extractor import LinguisticFeatureExtractor
from ml.models.ensemble import TruthLensEnsemble
from ml.explainability.claim_extractor import ClaimExtractor
from ml.explainability.highlighter import TextHighlighter


def test_strip_html_and_unicode_cleanup():
    raw_html = "<p>Scientists at <b>NASA</b> announced a &quot;breakthrough&quot; today.</p><script>alert('xss')</script>"
    cleaned = strip_html(raw_html)
    assert "NASA" in cleaned
    assert "breakthrough" in cleaned
    assert "alert" not in cleaned
    assert "<p>" not in cleaned


def test_language_detection():
    en_text = "The Federal Reserve raised interest rates to combat rising consumer price index inflation."
    fr_text = "Bonjour tout le monde, bienvenue a la conference internationale de presse."
    
    assert detect_language(en_text)["supported"] is True
    assert detect_language(en_text)["language"] == "en"

    assert detect_language(fr_text)["supported"] is False
    assert detect_language(fr_text)["language"] != "en"


def test_feature_extractor_dimensions_and_validity():
    extractor = LinguisticFeatureExtractor()
    feature_names = extractor.get_feature_names()
    assert len(feature_names) == 20

    text = "SHOCKING BOMBSHELL! Are you aware of this unbelievable miracle? It was reported by officials."
    vec = extractor.extract_vector(text)
    assert isinstance(vec, np.ndarray)
    assert len(vec) == 20
    assert not np.isnan(vec).any()

    feat_dict = extractor.extract_dict(text)
    assert feat_dict["sensational_word_density"] > 0
    assert feat_dict["question_density"] > 0


def test_claims_extractor_types():
    extractor = ClaimExtractor()
    article = (
        "Nonfarm payroll employment rose by 216,000 in December, economists reported. "
        "Federal Reserve officials stated that inflation moderated significantly. "
        "I believe this is a wonderful accomplishment for the administration. "
        "Severe flooding was caused by torrential rainfall across coastal regions."
    )
    claims = extractor.extract_claims(article)
    assert len(claims) >= 3

    claim_types = {c.claim_type for c in claims}
    # Should identify numerical, attribution, or causal claims
    assert any(t in claim_types for t in ["numerical", "attribution", "causal", "factual"])
    # Opinions should not be mislabeled as numerical
    for c in claims:
        if "i believe" in c.text.lower():
            assert c.claim_type == "opinion"


def test_text_highlighter():
    highlighter = TextHighlighter()
    text = "BOMBSHELL report: According to officials, the miracle cure was completely staged."
    spans = highlighter.generate_highlights(text)
    assert len(spans) >= 2
    directions = {s.direction for s in spans}
    assert "supports_misleading" in directions
    assert "supports_credible" in directions


def test_loaded_ensemble_inference_bounds():
    model_dir = Path("ml/artifacts")
    assert (model_dir / "ensemble_meta.joblib").exists()

    ensemble = TruthLensEnsemble()
    ensemble.load(model_dir)

    test_text = "Federal Reserve officials reported that annual inflation moderated to 2.8 percent in the fourth quarter."
    res = ensemble.assess(test_text, headline="Federal Reserve Report")

    assert "assessment" in res
    assert res["assessment"] in ["LIKELY CREDIBLE", "UNCERTAIN", "LIKELY MISLEADING"]
    assert 0.0 <= res["calibrated_probability"] <= 1.0
    assert 0.0 <= res["confidence"] <= 100.0
    assert 0.0 <= res["ood_score"] <= 1.0
    assert res["model_agreement"] in ["High", "Medium", "Low"]
    assert len(res["model_scores"]) == 4
