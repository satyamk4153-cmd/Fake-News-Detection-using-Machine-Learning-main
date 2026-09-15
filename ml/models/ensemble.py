"""Model 5: Calibrated Ensemble & Uncertainty Decision Engine for TruthLens."""

from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
import numpy as np
from sklearn.isotonic import IsotonicRegression
import joblib

from .logistic_regression import TruthLensLogisticRegression
from .linear_svm import TruthLensLinearSVM
from .gradient_boosting import TruthLensGradientBoosting
from .transformer_classifier import TruthLensTransformerClassifier
from ml.preprocessing.language_detector import detect_language


class TruthLensEnsemble:
    """Combines predictions from multiple baseline models with calibration,

    computes model consensus/agreement, detects out-of-distribution content,
    and produces the calibrated credibility assessment (Likely Credible, Uncertain, Likely Misleading).
    """

    def __init__(self, version: str = "ensemble-v1.0"):
        self.version = version
        self.model_name = "Calibrated Multi-Model Ensemble"
        self.model_lr = TruthLensLogisticRegression()
        self.model_svm = TruthLensLinearSVM()
        self.model_gb = TruthLensGradientBoosting()
        self.model_transformer = TruthLensTransformerClassifier()
        
        # Model weights in the ensemble (summing to 1.0)
        self.weights = {
            "logistic_regression": 0.25,
            "linear_svm": 0.25,
            "gradient_boosting": 0.20,
            "transformer": 0.30
        }
        self.calibrator = IsotonicRegression(out_of_bounds="clip")
        self.is_fitted = False
        
        # OOD baseline vocabulary and token statistics
        self.known_vocab: set = set()
        self.mean_length: float = 500.0
        self.std_length: float = 300.0

    def fit(self, texts: List[str], labels: List[int], headlines: List[str] = None) -> "TruthLensEnsemble":
        if headlines is None:
            headlines = [""] * len(texts)

        # Fit sub-models
        self.model_lr.fit(texts, labels)
        self.model_svm.fit(texts, labels)
        self.model_gb.fit(texts, labels, headlines)
        self.model_transformer.fit(texts, labels)

        # Compute uncalibrated ensemble raw scores
        raw_scores = []
        for i in range(len(texts)):
            p_lr = self.model_lr.predict_proba([texts[i]])[0, 1]
            p_svm = self.model_svm.predict_proba([texts[i]])[0, 1]
            p_gb = self.model_gb.predict_proba([texts[i]], [headlines[i]])[0, 1]
            p_trans = self.model_transformer.predict_proba([texts[i]])[0, 1]

            score = (
                self.weights["logistic_regression"] * p_lr +
                self.weights["linear_svm"] * p_svm +
                self.weights["gradient_boosting"] * p_gb +
                self.weights["transformer"] * p_trans
            )
            raw_scores.append(score)

        # Fit isotonic calibrator mapping raw ensemble score to empirical probability
        self.calibrator.fit(np.array(raw_scores), np.array(labels))
        
        # Build baseline vocabulary for Out-of-Distribution scoring
        all_words = set()
        lengths = []
        for t in texts:
            words = [w.lower() for w in t.split() if w.isalnum()]
            all_words.update(words)
            lengths.append(len(t))
            
        self.known_vocab = all_words
        self.mean_length = float(np.mean(lengths)) if lengths else 500.0
        self.std_length = float(np.std(lengths)) if lengths else 300.0
        self.is_fitted = True
        return self

    def compute_ood_score(self, text: str) -> float:
        """Compute out-of-distribution score (0.0 = very in-distribution, 1.0 = highly out-of-distribution)."""
        words = [w.lower() for w in text.split() if w.isalnum()]
        if not words:
            return 1.0
            
        unseen_count = sum(1 for w in words if w not in self.known_vocab)
        unseen_ratio = unseen_count / len(words)
        
        # Length anomaly z-score
        length_z = abs(len(text) - self.mean_length) / max(self.std_length, 50.0)
        length_penalty = min(0.3, length_z * 0.05)
        
        ood = min(1.0, (unseen_ratio * 0.7) + length_penalty)
        return round(float(ood), 3)

    def assess(
        self,
        text: str,
        headline: str = "",
        threshold_low: float = 0.35,
        threshold_high: float = 0.65
    ) -> Dict[str, Any]:
        """Perform comprehensive credibility assessment with uncertainty gating and explainability."""
        if not self.is_fitted:
            raise RuntimeError("Ensemble model has not been fitted.")

        # 1. Language validation
        lang_res = detect_language(f"{headline} {text}")
        if not lang_res["supported"]:
            return {
                "assessment": "UNCERTAIN",
                "label": "UNCERTAIN / NEEDS VERIFICATION",
                "calibrated_probability": 0.50,
                "confidence": 0.0,
                "confidence_level": "None",
                "model_agreement": "N/A",
                "agreement_score": 0.0,
                "ood_score": 1.0,
                "reason": lang_res["message"],
                "model_scores": {},
                "summary": "The submitted content is in an unsupported language or lacks sufficient alphabetic text for analysis.",
                "limitations": "TruthLens v1.0 only evaluates English news content. Models cannot produce valid credibility signals for unsupported languages."
            }

        # 2. Input length check
        combined = f"{headline} {text}".strip()
        if len(combined) < 20:
            return {
                "assessment": "UNCERTAIN",
                "label": "UNCERTAIN / NEEDS VERIFICATION",
                "calibrated_probability": 0.50,
                "confidence": 0.0,
                "confidence_level": "Low",
                "model_agreement": "N/A",
                "agreement_score": 0.0,
                "ood_score": 0.9,
                "reason": "Input is too short for reliable credibility assessment.",
                "model_scores": {},
                "summary": "More context or text is required to extract reliable linguistic and machine-learning signals.",
                "limitations": "Headlines or articles with fewer than 20 characters do not contain enough structural or lexical signals for robust statistical inference."
            }

        # 3. Individual model predictions
        p_lr = float(self.model_lr.predict_proba([text])[0, 1])
        p_svm = float(self.model_svm.predict_proba([text])[0, 1])
        p_gb = float(self.model_gb.predict_proba([text], [headline])[0, 1])
        p_trans = float(self.model_transformer.predict_proba([text])[0, 1])

        model_scores = {
            "logistic_regression": round(p_lr, 4),
            "linear_svm": round(p_svm, 4),
            "gradient_boosting": round(p_gb, 4),
            "transformer": round(p_trans, 4)
        }

        # 4. Raw weighted score
        raw_score = (
            self.weights["logistic_regression"] * p_lr +
            self.weights["linear_svm"] * p_svm +
            self.weights["gradient_boosting"] * p_gb +
            self.weights["transformer"] * p_trans
        )

        # 5. Calibrated probability of credibility P(credible)
        calibrated_p = float(self.calibrator.predict([raw_score])[0])
        calibrated_p = max(0.01, min(0.99, calibrated_p))

        # 6. Model agreement (Consensus across models)
        scores_arr = np.array([p_lr, p_svm, p_gb, p_trans])
        score_std = float(np.std(scores_arr))
        # std <= 0.10 is High agreement, 0.10-0.20 Medium, > 0.20 Low
        if score_std <= 0.12:
            agreement_level = "High"
            agreement_score = round(1.0 - (score_std / 0.3), 2)
        elif score_std <= 0.22:
            agreement_level = "Medium"
            agreement_score = round(1.0 - (score_std / 0.3), 2)
        else:
            agreement_level = "Low"
            agreement_score = round(max(0.0, 1.0 - (score_std / 0.3)), 2)

        # 7. Out-of-Distribution (OOD) score
        ood_score = self.compute_ood_score(combined)

        # 8. Confidence determination
        # Confidence is distance from decision boundary (0.5) scaled to 0-100%
        distance = abs(calibrated_p - 0.5) * 2.0
        confidence_pct = round(distance * 100, 1)

        if confidence_pct >= 75 and agreement_level in ["High", "Medium"] and ood_score < 0.65:
            confidence_level = "High"
        elif confidence_pct >= 45 and agreement_level != "Low" and ood_score < 0.80:
            confidence_level = "Medium"
        else:
            confidence_level = "Low"

        # 9. Assessment Decision Logic
        # Explicit multi-signal gating
        if ood_score >= 0.85:
            assessment = "UNCERTAIN"
            assessment_label = "UNCERTAIN / NEEDS VERIFICATION"
            summary = "The content exhibits high vocabulary and structural deviation from verified journalistic training distributions (High OOD score)."
        elif agreement_level == "Low" and 0.30 <= calibrated_p <= 0.70:
            assessment = "UNCERTAIN"
            assessment_label = "UNCERTAIN / NEEDS VERIFICATION"
            summary = "The underlying classification models show significant divergence in their individual assessments, indicating conflicting signals."
        elif threshold_low <= calibrated_p <= threshold_high:
            assessment = "UNCERTAIN"
            assessment_label = "UNCERTAIN / NEEDS VERIFICATION"
            summary = "The calibrated probability falls within the statistical uncertainty boundary. Linguistic signals are mixed and inconclusive."
        elif calibrated_p > threshold_high:
            assessment = "LIKELY CREDIBLE"
            assessment_label = "LIKELY CREDIBLE"
            summary = "The models observed linguistic discipline, standard journalistic attribution, and low sensationalism consistent with credible reporting."
        else:
            assessment = "LIKELY MISLEADING"
            assessment_label = "LIKELY MISLEADING"
            summary = "The models detected elevated sensationalism, emotional vocabulary, capitalization anomalies, or rhetoric commonly associated with deceptive content."

        # 10. Explanations from constituent models
        lr_expl = self.model_lr.explain_instance(text, top_k=4)
        gb_expl = self.model_gb.explain_features(text, headline)
        transformer_tokens = self.model_transformer.attribute_tokens(text, top_k=6)

        return {
            "assessment": assessment,
            "label": assessment_label,
            "raw_score": round(raw_score, 4),
            "calibrated_probability": round(calibrated_p, 4),
            "confidence": confidence_pct,
            "confidence_level": confidence_level,
            "model_agreement": agreement_level,
            "agreement_score": agreement_score,
            "ood_score": ood_score,
            "model_scores": model_scores,
            "summary": summary,
            "supporting_signals": lr_expl["top_supporting_credible"],
            "counter_signals": lr_expl["top_supporting_misleading"],
            "structural_deviations": gb_expl["top_signal_deviations"],
            "attributed_tokens": transformer_tokens,
            "limitations": "This assessment is generated by statistical models based on historical patterns and cannot establish absolute factual truth. Important claims should be corroborated with verified primary sources."
        }

    def save(self, model_dir: Path) -> None:
        model_dir.mkdir(parents=True, exist_ok=True)
        self.model_lr.save(model_dir / "logistic_regression.joblib")
        self.model_svm.save(model_dir / "linear_svm.joblib")
        self.model_gb.save(model_dir / "gradient_boosting.joblib")
        self.model_transformer.save(model_dir / "transformer.joblib")
        joblib.dump({
            "weights": self.weights,
            "calibrator": self.calibrator,
            "known_vocab": self.known_vocab,
            "mean_length": self.mean_length,
            "std_length": self.std_length,
            "version": self.version
        }, model_dir / "ensemble_meta.joblib")

    def load(self, model_dir: Path) -> "TruthLensEnsemble":
        self.model_lr.load(model_dir / "logistic_regression.joblib")
        self.model_svm.load(model_dir / "linear_svm.joblib")
        self.model_gb.load(model_dir / "gradient_boosting.joblib")
        self.model_transformer.load(model_dir / "transformer.joblib")
        data = joblib.load(model_dir / "ensemble_meta.joblib")
        self.weights = data["weights"]
        self.calibrator = data["calibrator"]
        self.known_vocab = data["known_vocab"]
        self.mean_length = data.get("mean_length", 500.0)
        self.std_length = data.get("std_length", 300.0)
        self.version = data.get("version", self.version)
        self.is_fitted = True
        return self
