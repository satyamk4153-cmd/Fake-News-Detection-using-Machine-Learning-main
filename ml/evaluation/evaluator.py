"""Comprehensive evaluation suite for TruthLens credibility models."""

from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Tuple
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    brier_score_loss,
)


@dataclass
class EvaluationMetrics:
    model_name: str
    model_version: str
    dataset_name: str
    sample_count: int
    accuracy: float
    precision: float
    recall: float
    f1: float
    macro_f1: float
    roc_auc: float
    pr_auc: float
    brier_score: float
    expected_calibration_error: float
    confusion_matrix: List[List[int]]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ModelEvaluator:
    """Calculates rigorous, real statistical metrics for model predictions."""

    @staticmethod
    def calculate_ece(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 5) -> float:
        """Calculate Expected Calibration Error (ECE) across probability bins."""
        bin_limits = np.linspace(0.0, 1.0, n_bins + 1)
        ece = 0.0
        n_samples = len(y_true)
        if n_samples == 0:
            return 0.0

        for i in range(n_bins):
            bin_lower = bin_limits[i]
            bin_upper = bin_limits[i + 1]
            in_bin = (y_prob >= bin_lower) & (y_prob < bin_upper if i < n_bins - 1 else y_prob <= bin_upper)
            prop_in_bin = np.mean(in_bin)

            if prop_in_bin > 0:
                accuracy_in_bin = np.mean(y_true[in_bin])
                avg_confidence_in_bin = np.mean(y_prob[in_bin])
                ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin

        return round(float(ece), 4)

    @classmethod
    def evaluate(
        cls,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_prob: np.ndarray,
        model_name: str,
        model_version: str,
        dataset_name: str
    ) -> EvaluationMetrics:
        """Compute all classification and calibration metrics from ground truth and predictions."""
        acc = accuracy_score(y_true, y_pred)
        prec = precision_score(y_true, y_pred, zero_division=0)
        rec = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
        
        try:
            roc_auc = roc_auc_score(y_true, y_prob)
        except Exception:
            roc_auc = 0.5

        try:
            pr_auc = average_precision_score(y_true, y_prob)
        except Exception:
            pr_auc = float(np.mean(y_true))

        brier = brier_score_loss(y_true, y_prob)
        ece = cls.calculate_ece(y_true, y_prob)
        cm = confusion_matrix(y_true, y_pred).tolist()

        return EvaluationMetrics(
            model_name=model_name,
            model_version=model_version,
            dataset_name=dataset_name,
            sample_count=len(y_true),
            accuracy=round(float(acc), 4),
            precision=round(float(prec), 4),
            recall=round(float(rec), 4),
            f1=round(float(f1), 4),
            macro_f1=round(float(macro_f1), 4),
            roc_auc=round(float(roc_auc), 4),
            pr_auc=round(float(pr_auc), 4),
            brier_score=round(float(brier), 4),
            expected_calibration_error=ece,
            confusion_matrix=cm
        )
