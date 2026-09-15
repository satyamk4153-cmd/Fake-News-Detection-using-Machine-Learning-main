"""CLI inference prediction script for TruthLens."""

import argparse
import json
from pathlib import Path

from ml.models.ensemble import TruthLensEnsemble
from ml.explainability.claim_extractor import ClaimExtractor
from ml.explainability.highlighter import TextHighlighter


def predict(text: str, headline: str = "", model_dir: Path = Path("ml/artifacts")) -> dict:
    ensemble = TruthLensEnsemble()
    ensemble.load(model_dir)

    result = ensemble.assess(text, headline)
    
    # Claims extraction
    claim_extractor = ClaimExtractor()
    claims = [c.to_dict() for c in claim_extractor.extract_claims(f"{headline} {text}")]
    result["claims"] = claims

    # Highlighting
    highlighter = TextHighlighter()
    highlights = [h.to_dict() for h in highlighter.generate_highlights(f"{headline} {text}")]
    result["highlights"] = highlights

    return result


def main():
    parser = argparse.ArgumentParser(description="Predict news credibility with TruthLens.")
    parser.add_argument("--text", type=str, required=True, help="Article body or statement text")
    parser.add_argument("--headline", type=str, default="", help="Optional article headline")
    parser.add_argument("--model-dir", type=str, default="ml/artifacts", help="Path to model artifacts")
    args = parser.parse_args()

    res = predict(args.text, args.headline, Path(args.model_dir))
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
