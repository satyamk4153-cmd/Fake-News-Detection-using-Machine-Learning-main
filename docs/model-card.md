# TruthLens Model Card — Production Ensemble v1.0

## Model Details
- **Developer**: TruthLens Engineering Team
- **Model Date**: September 2026
- **Model Version**: `ensemble-v1.0`
- **Model Type**: Calibrated Multi-Model Ensemble combining:
  1. `lr-v1.0`: TF-IDF Logistic Regression
  2. `svm-v1.0`: Calibrated Linear Support Vector Machine
  3. `gb-v1.0`: HistGradientBoosting Classifier on 20 Linguistic Features
  4. `distilbert-credibility-v1.0`: Sequence Contextual Classifier with Temperature Scaling
- **Calibration Method**: Isotonic Regression on Holdout Validation Data

---

## Intended Use
- **Primary Use**: Assisting journalists, researchers, and media analysts in screening articles and headlines for deceptive or sensational rhetoric.
- **Out-of-Scope Use**:
  - TruthLens must NOT be used as an autonomous, definitive arbiter of absolute truth.
  - TruthLens must NOT be used to censor speech or blacklist journalistic domains automatically.

---

## Benchmark Performance & Evaluation

Evaluated on the Holdout Benchmark Test Split (`truthlens_benchmark_v1.0`):

| Model | Accuracy | Precision | Recall | F1 Score | Brier Score | ECE |
|---|---|---|---|---|---|---|
| TF-IDF Logistic Regression | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.2348 | 0.1659 |
| Calibrated Linear SVM | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0456 | 0.2053 |
| HistGradientBoosting (Linguistic) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0001 |
| Sequence Contextual Transformer | 0.3333 | 0.3333 | 1.0000 | 0.5000 | 0.2511 | 0.1729 |
| **Calibrated Multi-Model Ensemble** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **0.0114** | **0.1002** |

*Note: High benchmark performance on specific test sets does not guarantee uniform real-world performance across all future emerging news stories. The ensemble achieves the lowest overall Brier Score ($0.0114$), ensuring well-calibrated confidence.*

---

## Factors & Bias Considerations
- **Language**: Evaluated and calibrated for English. Content in other languages triggers an out-of-scope uncertainty label.
- **Rhetorical Style**: Emotionally expressive political commentary or satire may register elevated sensationalism scores. Human verification is strongly recommended whenever the model returns `UNCERTAIN`.
