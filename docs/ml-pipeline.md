# TruthLens Machine Learning Pipeline Guide

## 1. Directory Structure

```
ml/
├── datasets/            # Dataset registration, loaders, splitting
├── preprocessing/       # Traditional ML cleaner vs Transformer tokenizer
├── features/            # 20 linguistic and structural feature extractors
├── models/              # Logistic Regression, SVM, Gradient Boosting, Transformer, Ensemble
├── training/            # CLI training pipeline (`python -m ml.training.train`)
├── evaluation/          # Comprehensive evaluation metrics (ECE, Brier, ROC-AUC, PR-AUC, F1)
├── explainability/      # Token attribution, feature weights, highlighted spans, claims
├── inference/           # Production inference CLI and prediction engine
└── artifacts/           # Serialized models (.joblib) and evaluation reports (.json)
```

## 2. Running Training & Evaluation

To train all models on the benchmark splits and calculate real metrics:
```bash
python -m ml.training.train --artifacts-dir ml/artifacts
```

To evaluate the current production ensemble model on holdout test data:
```bash
python -m ml.evaluation.evaluate
```

To test inference via CLI:
```bash
python -m ml.inference.predict --headline "Fed Rate Decision" --text "Federal Reserve held interest rates steady on Wednesday..."
```

## 3. Preprocessing Separation

TruthLens preserves clean separation between:
1. **Traditional ML Text Preprocessing** (`clean_text_traditional`):
   - NFKC normalization, lowercasing, HTML stripping, punctuation normalization.
2. **Transformer Text Preprocessing** (`clean_text_transformer`):
   - Retains capitalization, quote punctuation, sentence casing, and contextual tokens.
