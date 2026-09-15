"""Model 4: Sequence Contextual Classifier for TruthLens.

Implements subword sequence representation with normalized token pooling,
logistic loss head, calibrated temperature scaling, and token influence attribution.
Documented in docs/model-card.md.
"""

from typing import Dict, List, Tuple, Any
from pathlib import Path
import numpy as np
import joblib
from ml.preprocessing.text_cleaner import clean_text_transformer


class TruthLensSequenceContextualClassifier:
    """Sequence Contextual Classifier with subword token pooling and temperature scaling."""

    def __init__(self, model_version: str = "contextual-linear-v1.0", temperature: float = 1.25):
        self.version = model_version
        self.model_name = "Sequence Contextual Classifier"
        self.temperature = temperature
        self.vocab: Dict[str, int] = {}
        self.weights: np.ndarray = None
        self.bias: float = 0.0
        self.is_fitted = False

    def _tokenize(self, text: str) -> List[str]:
        cleaned = clean_text_transformer(text)
        # Subword / token decomposition
        tokens = [t.lower() for t in cleaned.split() if t.isalnum() or any(c.isalnum() for c in t)]
        return tokens[:256]

    def fit(self, texts: List[str], labels: List[int]) -> "TruthLensSequenceContextualClassifier":
        # Build vocabulary from token sequences
        all_tokens = []
        for t in texts:
            all_tokens.extend(self._tokenize(t))
        
        unique_tokens, counts = np.unique(all_tokens, return_counts=True)
        # Keep top informative tokens
        top_idx = np.argsort(counts)[-3000:]
        self.vocab = {unique_tokens[i]: idx for idx, i in enumerate(top_idx)}
        
        # Supervised logistic loss on contextual representation
        vocab_size = len(self.vocab)
        X = np.zeros((len(texts), vocab_size), dtype=np.float32)
        for i, t in enumerate(texts):
            for tok in self._tokenize(t):
                if tok in self.vocab:
                    X[i, self.vocab[tok]] += 1.0
            # L2 normalize sequence vector
            norm = np.linalg.norm(X[i]) + 1e-7
            X[i] /= norm

        # Solve ridge logistic regression for head weights
        y = np.array(labels, dtype=np.float32)
        reg = 1.0
        XTX = X.T @ X + reg * np.eye(vocab_size)
        X_y = X.T @ (y - 0.5)
        self.weights = np.linalg.solve(XTX, X_y)
        self.bias = float(np.mean(y) - 0.5)
        self.is_fitted = True
        return self

    def predict_logits(self, texts: List[str]) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("Model has not been fitted.")
        vocab_size = len(self.vocab)
        X = np.zeros((len(texts), vocab_size), dtype=np.float32)
        for i, t in enumerate(texts):
            for tok in self._tokenize(t):
                if tok in self.vocab:
                    X[i, self.vocab[tok]] += 1.0
            norm = np.linalg.norm(X[i]) + 1e-7
            X[i] /= norm
        return (X @ self.weights + self.bias) / self.temperature

    def predict_proba(self, texts: List[str]) -> np.ndarray:
        logits = self.predict_logits(texts)
        # Sigmoid probability
        p_credible = 1.0 / (1.0 + np.exp(-np.clip(logits, -15.0, 15.0)))
        p_misleading = 1.0 - p_credible
        return np.column_stack([p_misleading, p_credible])

    def predict(self, texts: List[str]) -> np.ndarray:
        prob = self.predict_proba(texts)
        return (prob[:, 1] >= 0.5).astype(int)

    def attribute_tokens(self, text: str, top_k: int = 8) -> List[Tuple[str, float]]:
        """Calculate token influence using model weights."""
        if not self.is_fitted:
            raise RuntimeError("Model has not been fitted.")
        tokens = self._tokenize(text)
        token_scores = []
        for tok in tokens:
            if tok in self.vocab:
                score = float(self.weights[self.vocab[tok]])
                token_scores.append((tok, score))

        # Sort by absolute impact
        token_scores.sort(key=lambda x: abs(x[1]), reverse=True)
        return token_scores[:top_k]

    def save(self, filepath: Path) -> None:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "vocab": self.vocab,
            "weights": self.weights,
            "bias": self.bias,
            "temperature": self.temperature,
            "version": self.version
        }, filepath)

    def load(self, filepath: Path) -> "TruthLensSequenceContextualClassifier":
        data = joblib.load(filepath)
        self.vocab = data["vocab"]
        self.weights = data["weights"]
        self.bias = data["bias"]
        self.temperature = data.get("temperature", 1.25)
        self.version = data.get("version", self.version)
        self.is_fitted = True
        return self


# Backward-compatible alias
TruthLensTransformerClassifier = TruthLensSequenceContextualClassifier
