"""TRAIN THE CLASSIFIER.  Owner: alert ranker person (C)

    python train_model.py

1. Builds features for data/train (features.py)
2. 5-fold cross-validation GROUPED BY SCENARIO (payments from one scenario never
   appear in both train and validation -- otherwise the score is fake-high)
3. Picks the probability threshold with the best F1
4. Trains on everything and saves models/model.joblib
"""
import json
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score, precision_recall_fscore_support, roc_auc_score
from sklearn.model_selection import GroupKFold

import config
from features import ALL_FEATURES, make_features


def new_model():
    return HistGradientBoostingClassifier(max_iter=400, learning_rate=0.05,
                                          class_weight="balanced", random_state=0)


if __name__ == "__main__":
    df = make_features(config.TRAIN_DIR)
    labels = pd.read_csv(f"{config.TRAIN_DIR}/labels.csv").rename(columns={"TRANSACTION_HASH": "hash"})
    df = df.merge(labels, on="hash")
    X, y = df[ALL_FEATURES], df["is_suspicious"]
    groups = df["scenario_id"].fillna(df["hash"])

    oof = np.zeros(len(df))
    for trn, val in GroupKFold(5).split(X, y, groups):
        oof[val] = new_model().fit(X.iloc[trn], y.iloc[trn]).predict_proba(X.iloc[val])[:, 1]

    best_t, best_f1, best_p, best_r = 0.5, 0, 0, 0
    for t in np.arange(0.05, 0.96, 0.05):
        p, r, f1, _ = precision_recall_fscore_support(y, oof >= t, average="binary", zero_division=0)
        if f1 > best_f1:
            best_t, best_f1, best_p, best_r = t, f1, p, r

    print(f"Cross-validated  PR-AUC {average_precision_score(y, oof):.3f}   ROC-AUC {roc_auc_score(y, oof):.3f}")
    print(f"Threshold {best_t:.2f}: precision {best_p:.2f}  recall {best_r:.2f}  F1 {best_f1:.2f}")
    recall = df.assign(hit=(oof >= best_t)).query("is_suspicious == 1").groupby("family")["hit"].mean()
    print("Recall by laundering family:\n" + recall.round(2).to_string())

    os.makedirs("models", exist_ok=True)
    joblib.dump({"model": new_model().fit(X, y), "threshold": float(best_t), "features": ALL_FEATURES},
                config.MODEL_PATH)
    json.dump({"pr_auc": average_precision_score(y, oof), "f1": best_f1, "precision": best_p,
               "recall": best_r, "threshold": best_t}, open("models/cv_metrics.json", "w"), indent=2)
    print(f"Saved {config.MODEL_PATH}")
