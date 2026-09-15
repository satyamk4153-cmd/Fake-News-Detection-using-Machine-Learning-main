"""CLI entrypoint for evaluating saved TruthLens models."""

import json
from pathlib import Path
import pandas as pd
import numpy as np

from ml.models.ensemble import TruthLensEnsemble
from ml.evaluation.evaluator import ModelEvaluator


def main():
    artifacts_dir = Path("ml/artifacts")
    test_file = Path("data/processed/test.csv")

    if not (artifacts_dir / "ensemble_meta.joblib").exists():
        print("Error: Models not found in ml/artifacts. Run `python -m ml.training.train` first.")
        return

    if not test_file.exists():
        print("Error: Test split not found. Run `python -m ml.training.train` first.")
        return

    print("Evaluating TruthLens Production Ensemble on holdout test set...")
    df_test = pd.read_csv(test_file)
    X_test = df_test["text"].tolist()
    y_test = np.array(df_test["label"].tolist())
    h_test = df_test["title"].tolist()

    ensemble = TruthLensEnsemble()
    ensemble.load(artifacts_dir)

    probs = []
    preds = []
    for i in range(len(X_test)):
        res = ensemble.assess(X_test[i], h_test[i])
        p = res["calibrated_probability"]
        probs.append(p)
        preds.append(1 if p >= 0.5 else 0)

    metrics = ModelEvaluator.evaluate(
        y_test,
        np.array(preds),
        np.array(probs),
        ensemble.model_name,
        ensemble.version,
        "truthlens_test_holdout"
    )

    print("\n" + "=" * 50)
    print("TruthLens Production Model Evaluation Report")
    print("=" * 50)
    print(json.dumps(metrics.to_dict(), indent=2))


if __name__ == "__main__":
    main()
