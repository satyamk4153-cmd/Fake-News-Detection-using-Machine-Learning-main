"""Model 2: Calibrated Linear Support Vector Machine (SVM)."""

from typing import Dict, List, Tuple, Any
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
import joblib


class TruthLensLinearSVM:
    """Linear Support Vector Classifier with Platt probability calibration."""

    def __init__(self, model_version: str = "svm-v1.0"):
        self.version = model_version
        self.model_name = "Calibrated Linear SVM"
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=10000,
            sublinear_tf=True,
            strip_accents="unicode"
        )
        base_svc = LinearSVC(
            C=1.0,
            loss="squared_hinge",
            dual="auto",
            random_state=42,
            max_iter=2000
        )
        self.calibrated_classifier = CalibratedClassifierCV(
            estimator=base_svc,
            method="sigmoid",
            cv=3
        )
        self.is_fitted = False

    def fit(self, texts: List[str], labels: List[int]) -> "TruthLensLinearSVM":
        X = self.vectorizer.fit_transform(texts)
        self.calibrated_classifier.fit(X, labels)
        self.is_fitted = True
        return self

    def predict_proba(self, texts: List[str]) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("Model has not been fitted.")
        X = self.vectorizer.transform(texts)
        return self.calibrated_classifier.predict_proba(X)

    def predict(self, texts: List[str]) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("Model has not been fitted.")
        X = self.vectorizer.transform(texts)
        return self.calibrated_classifier.predict(X)

    def save(self, filepath: Path) -> None:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "vectorizer": self.vectorizer,
            "classifier": self.calibrated_classifier,
            "version": self.version
        }, filepath)

    def load(self, filepath: Path) -> "TruthLensLinearSVM":
        data = joblib.load(filepath)
        self.vectorizer = data["vectorizer"]
        self.calibrated_classifier = data["classifier"]
        self.version = data.get("version", self.version)
        self.is_fitted = True
        return self
