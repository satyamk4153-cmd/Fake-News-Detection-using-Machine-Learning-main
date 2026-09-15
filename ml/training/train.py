"""Reproducible Training Script for TruthLens Models."""

import json
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

from ml.datasets.loader import prepare_and_register_benchmark_dataset, split_dataset, load_curated_benchmark_dataset
from ml.models.logistic_regression import TruthLensLogisticRegression
from ml.models.linear_svm import TruthLensLinearSVM
from ml.models.gradient_boosting import TruthLensGradientBoosting
from ml.models.transformer_classifier import TruthLensTransformerClassifier
from ml.models.ensemble import TruthLensEnsemble
from ml.evaluation.evaluator import ModelEvaluator


def run_training_pipeline(artifacts_dir: Path = Path("ml/artifacts")) -> dict:
    """Execute complete reproducible training, calibration, and evaluation run."""
    print("=" * 65)
    print("TruthLens — Training & Evaluation Pipeline")
    print("=" * 65)

    # 1. Dataset Preparation & Leakage-Safe Splitting
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    reg_info = prepare_and_register_benchmark_dataset()
    print(f"[Dataset] Registered {reg_info['total_records']} benchmark records.")
    print(f"          Splits: {reg_info['train_records']} train, {reg_info['val_records']} val, {reg_info['test_records']} test")

    df_train = pd.read_csv("data/processed/train.csv")
    df_test = pd.read_csv("data/processed/test.csv")

    X_train = df_train["text"].tolist()
    y_train = df_train["label"].tolist()
    h_train = df_train["title"].tolist()

    X_test = df_test["text"].tolist()
    y_test = np.array(df_test["label"].tolist())
    h_test = df_test["title"].tolist()

    # 2. Train Individual Models
    print("\n[Model 1/4] Training Logistic Regression...")
    lr = TruthLensLogisticRegression()
    lr.fit(X_train, y_train)

    print("[Model 2/4] Training Calibrated Linear SVM...")
    svm = TruthLensLinearSVM()
    svm.fit(X_train, y_train)

    print("[Model 3/4] Training Gradient Boosting (Linguistic)...")
    gb = TruthLensGradientBoosting()
    gb.fit(X_train, y_train, h_train)

    print("[Model 4/4] Training Sequence Contextual Transformer...")
    trans = TruthLensTransformerClassifier()
    trans.fit(X_train, y_train)

    print("\n[Ensemble] Assembling Multi-Model Calibrated Ensemble...")
    ensemble = TruthLensEnsemble()
    ensemble.fit(X_train, y_train, h_train)
    ensemble.save(artifacts_dir)
    print(f"[Artifacts] Saved ensemble models to {artifacts_dir}")

    # 3. Evaluate Each Model on Holdout Test Split
    print("\n" + "-" * 65)
    print("Holdout Test Split Evaluation Results (Real Computed Metrics):")
    print("-" * 65)

    dataset_name = "truthlens_benchmark_v1.0"
    evaluations = {}

    # Eval LR
    p_lr = lr.predict_proba(X_test)[:, 1]
    y_pred_lr = (p_lr >= 0.5).astype(int)
    eval_lr = ModelEvaluator.evaluate(y_test, y_pred_lr, p_lr, lr.model_name, lr.version, dataset_name)
    evaluations["logistic_regression"] = eval_lr.to_dict()

    # Eval SVM
    p_svm = svm.predict_proba(X_test)[:, 1]
    y_pred_svm = (p_svm >= 0.5).astype(int)
    eval_svm = ModelEvaluator.evaluate(y_test, y_pred_svm, p_svm, svm.model_name, svm.version, dataset_name)
    evaluations["linear_svm"] = eval_svm.to_dict()

    # Eval GB
    p_gb = gb.predict_proba(X_test, h_test)[:, 1]
    y_pred_gb = (p_gb >= 0.5).astype(int)
    eval_gb = ModelEvaluator.evaluate(y_test, y_pred_gb, p_gb, gb.model_name, gb.version, dataset_name)
    evaluations["gradient_boosting"] = eval_gb.to_dict()

    # Eval Transformer
    p_trans = trans.predict_proba(X_test)[:, 1]
    y_pred_trans = (p_trans >= 0.5).astype(int)
    eval_trans = ModelEvaluator.evaluate(y_test, y_pred_trans, p_trans, trans.model_name, trans.version, dataset_name)
    evaluations["transformer"] = eval_trans.to_dict()

    # Eval Calibrated Ensemble
    ens_probs = []
    ens_preds = []
    for i in range(len(X_test)):
        res = ensemble.assess(X_test[i], h_test[i])
        cal_p = res["calibrated_probability"]
        ens_probs.append(cal_p)
        ens_preds.append(1 if cal_p >= 0.5 else 0)

    ens_probs = np.array(ens_probs)
    ens_preds = np.array(ens_preds)
    eval_ens = ModelEvaluator.evaluate(y_test, ens_preds, ens_probs, ensemble.model_name, ensemble.version, dataset_name)
    evaluations["ensemble"] = eval_ens.to_dict()

    # Print summary table
    print(f"{'Model':<35} | {'Acc':<6} | {'Prec':<6} | {'Rec':<6} | {'F1':<6} | {'Brier':<6} | {'ECE':<6}")
    print("-" * 80)
    for k, ev in evaluations.items():
        print(f"{ev['model_name']:<35} | {ev['accuracy']:<6.4f} | {ev['precision']:<6.4f} | {ev['recall']:<6.4f} | {ev['f1']:<6.4f} | {ev['brier_score']:<6.4f} | {ev['expected_calibration_error']:<6.4f}")

    # 4. Save evaluation metrics JSON
    report_path = artifacts_dir / "evaluation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(evaluations, f, indent=2)
    print(f"\n[Report] Saved evaluation metrics to {report_path}")

    return evaluations


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train TruthLens credibility models.")
    parser.add_argument("--artifacts-dir", default="ml/artifacts", help="Path to save artifacts")
    args = parser.parse_args()
    run_training_pipeline(Path(args.artifacts_dir))
