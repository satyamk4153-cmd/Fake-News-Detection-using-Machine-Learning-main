"""Model 3: Gradient Boosting Classifier on Linguistic & Structural Features."""

from typing import Dict, List, Tuple, Any
from pathlib import Path
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import joblib

from ml.features.extractor import LinguisticFeatureExtractor


class TruthLensGradientBoosting:
    """Gradient Boosting classifier trained on 20 engineered linguistic and structural signals."""

    def __init__(self, model_version: str = "gb-v1.0"):
        self.version = model_version
        self.model_name = "HistGradientBoosting Linguistic Classifier"
        self.extractor = LinguisticFeatureExtractor()
        self.scaler = StandardScaler()
        self.classifier = HistGradientBoostingClassifier(
            max_iter=150,
            learning_rate=0.08,
            max_depth=5,
            min_samples_leaf=2,
            random_state=42
        )
        self.feature_names = self.extractor.get_feature_names()
        self.is_fitted = False

    def _extract_matrix(self, texts: List[str], headlines: List[str] = None) -> np.ndarray:
        if headlines is None:
            headlines = [""] * len(texts)
        vectors = [self.extractor.extract_vector(t, h) for t, h in zip(texts, headlines)]
        return np.vstack(vectors)

    def fit(self, texts: List[str], labels: List[int], headlines: List[str] = None) -> "TruthLensGradientBoosting":
        X_raw = self._extract_matrix(texts, headlines)
        X_scaled = self.scaler.fit_transform(X_raw)
        self.classifier.fit(X_scaled, labels)
        self.is_fitted = True
        return self

    def predict_proba(self, texts: List[str], headlines: List[str] = None) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("Model has not been fitted.")
        X_raw = self._extract_matrix(texts, headlines)
        X_scaled = self.scaler.transform(X_raw)
        return self.classifier.predict_proba(X_scaled)

    def predict(self, texts: List[str], headlines: List[str] = None) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("Model has not been fitted.")
        X_raw = self._extract_matrix(texts, headlines)
        X_scaled = self.scaler.transform(X_raw)
        return self.classifier.predict(X_scaled)

    def explain_features(self, text: str, headline: str = "") -> Dict[str, Any]:
        """Return raw features and their deviations for a sample."""
        feat_dict = self.extractor.extract_dict(text, headline)
        vec = self.extractor.extract_vector(text, headline)
        scaled = (vec - self.scaler.mean_) / (self.scaler.scale_ + 1e-8)
        
        # High deviations (Z-score magnitude)
        deviations = [
            (self.feature_names[i], round(float(feat_dict[self.feature_names[i]]), 3), round(float(scaled[i]), 2))
            for i in range(len(self.feature_names))
        ]
        deviations.sort(key=lambda x: abs(x[2]), reverse=True)

        return {
            "model": self.model_name,
            "version": self.version,
            "top_signal_deviations": deviations[:6]
        }

    def save(self, filepath: Path) -> None:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "scaler": self.scaler,
            "classifier": self.classifier,
            "version": self.version
        }, filepath)

    def load(self, filepath: Path) -> "TruthLensGradientBoosting":
        data = joblib.load(filepath)
        self.scaler = data["scaler"]
        self.classifier = data["classifier"]
        self.version = data.get("version", self.version)
        self.is_fitted = True
        return self
