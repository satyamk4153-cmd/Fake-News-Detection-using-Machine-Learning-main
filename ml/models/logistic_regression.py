"""Model 1: Calibrated Logistic Regression with TF-IDF Features."""

from typing import Dict, List, Tuple, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib
from pathlib import Path


class TruthLensLogisticRegression:
    """Logistic Regression text classifier with TF-IDF word and character n-grams."""

    def __init__(self, model_version: str = "lr-v1.0"):
        self.version = model_version
        self.model_name = "TF-IDF Logistic Regression"
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=10000,
            sublinear_tf=True,
            strip_accents="unicode"
        )
        self.classifier = LogisticRegression(
            C=1.0,
            max_iter=1000,
            solver="lbfgs",
            random_state=42
        )
        self.is_fitted = False

    def fit(self, texts: List[str], labels: List[int]) -> "TruthLensLogisticRegression":
        X = self.vectorizer.fit_transform(texts)
        self.classifier.fit(X, labels)
        self.is_fitted = True
        return self

    def predict_proba(self, texts: List[str]) -> np.ndarray:
        """Predict probabilities [P(misleading), P(credible)]."""
        if not self.is_fitted:
            raise RuntimeError("Model has not been fitted.")
        X = self.vectorizer.transform(texts)
        return self.classifier.predict_proba(X)

    def predict(self, texts: List[str]) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("Model has not been fitted.")
        X = self.vectorizer.transform(texts)
        return self.classifier.predict(X)

    def get_top_features(self, n: int = 10) -> Dict[str, List[Tuple[str, float]]]:
        """Return top indicative features for both classes."""
        if not self.is_fitted:
            raise RuntimeError("Model has not been fitted.")
        feature_names = np.array(self.vectorizer.get_feature_names_out())
        coefs = self.classifier.coef_[0]
        
        # Positive coefs indicate Credible, Negative indicate Misleading
        top_credible_idx = np.argsort(coefs)[-n:][::-1]
        top_misleading_idx = np.argsort(coefs)[:n]

        return {
            "credible_signals": [(feature_names[i], round(float(coefs[i]), 4)) for i in top_credible_idx],
            "misleading_signals": [(feature_names[i], round(float(abs(coefs[i])), 4)) for i in top_misleading_idx]
        }

    def explain_instance(self, text: str, top_k: int = 5) -> Dict[str, Any]:
        """Explain feature contributions for a specific instance."""
        if not self.is_fitted:
            raise RuntimeError("Model has not been fitted.")
        x_vec = self.vectorizer.transform([text])
        feature_names = self.vectorizer.get_feature_names_out()
        coefs = self.classifier.coef_[0]
        
        # Element-wise contribution
        non_zero_indices = x_vec.nonzero()[1]
        contributions = []
        for idx in non_zero_indices:
            weight = float(x_vec[0, idx] * coefs[idx])
            contributions.append((feature_names[idx], weight))

        # Sort by magnitude
        contributions.sort(key=lambda x: abs(x[1]), reverse=True)
        supporting_credible = [(feat, round(w, 4)) for feat, w in contributions if w > 0][:top_k]
        supporting_misleading = [(feat, round(abs(w), 4)) for feat, w in contributions if w < 0][:top_k]

        prob = self.predict_proba([text])[0]
        return {
            "model": self.model_name,
            "version": self.version,
            "probability_credible": round(float(prob[1]), 4),
            "probability_misleading": round(float(prob[0]), 4),
            "top_supporting_credible": supporting_credible,
            "top_supporting_misleading": supporting_misleading
        }

    def save(self, filepath: Path) -> None:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"vectorizer": self.vectorizer, "classifier": self.classifier, "version": self.version}, filepath)

    def load(self, filepath: Path) -> "TruthLensLogisticRegression":
        data = joblib.load(filepath)
        self.vectorizer = data["vectorizer"]
        self.classifier = data["classifier"]
        self.version = data.get("version", self.version)
        self.is_fitted = True
        return self
