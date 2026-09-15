# TruthLens Decision Logic & Calibration Architecture

## Decision Flow Diagram

```
Raw Input Text / Headline
            ↓
Language Check (English?) ──[No]──→ UNCERTAIN / NEEDS VERIFICATION
            ↓ [Yes]
Length Check (>= 20 chars) ─[No]──→ UNCERTAIN / INSUFFICIENT TEXT
            ↓ [Yes]
Dual Preprocessing (Traditional ML + Transformer)
            ↓
Inference across 4 Baseline Models:
  • P_lr (Logistic Regression)
  • P_svm (Linear SVM)
  • P_gb (HistGradientBoosting)
  • P_trans (Sequence Transformer)
            ↓
Compute Weighted Raw Score:
  Score = 0.25*P_lr + 0.25*P_svm + 0.20*P_gb + 0.30*P_trans
            ↓
Isotonic Probability Calibration:
  Calibrated_P = IsotonicCalibrator(Score)
            ↓
Model Consensus & Agreement:
  Std = std([P_lr, P_svm, P_gb, P_trans])
  Agreement = High if Std <= 0.12 else Medium if Std <= 0.22 else Low
            ↓
Out-of-Distribution Scoring (OOD):
  OOD = 0.7 * UnseenVocabRatio + 0.3 * LengthAnomaly
            ↓
Decision Gating:
  IF OOD >= 0.85 ─────────────────────────→ UNCERTAIN
  IF Agreement == Low AND 0.30 <= P <= 0.70 → UNCERTAIN
  IF 0.35 <= Calibrated_P <= 0.65 ─────────→ UNCERTAIN
  IF Calibrated_P > 0.65 AND Agreement != Low → LIKELY CREDIBLE
  IF Calibrated_P < 0.35 AND Agreement != Low → LIKELY MISLEADING
            ↓
Generate Attributed Signals, Highlights, & Claims
```

## Threshold Configuration (`configs/model/model_config.json`)

- `UNCERTAINTY_THRESHOLD_LOW`: `0.35`
- `UNCERTAINTY_THRESHOLD_HIGH`: `0.65`
- `MIN_MODEL_AGREEMENT`: `0.60`
- `MAX_OOD_SCORE`: `0.75`
- `MIN_HEADLINE_LENGTH`: `15`
- `MIN_ARTICLE_LENGTH`: `50`
