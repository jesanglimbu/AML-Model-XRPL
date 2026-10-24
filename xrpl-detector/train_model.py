"""TRAIN THE CLASSIFIER.  Owner: alert ranker person (C)

    python train_model.py

1. Builds the ranker's features for data/train (aml_ranker/features.py)
2. 5-fold cross-validation GROUPED BY SCENARIO, and by COHORT for the relay families
   (look-alike scenarios never appear in both train and validation -- otherwise the
   score is fake-high). Prints the site metric (100 x average precision)
   for the blend (the default upload) and for the blend + medium specialist mix.
3. Picks the probability threshold with the best F1 (used for is_suspicious)
4. Trains on everything and saves models/model.joblib

Takes about 20-25 minutes on a laptop CPU. The model is a two-stage gradient-boosting
ensemble plus a small medium-case specialist: see aml_ranker/model.py.
"""
import json
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, precision_recall_fscore_support, roc_auc_score

import config
from aml_ranker.data import load_split
from aml_ranker.features import build_features
from aml_ranker.model import (AlertRanker, blend, cross_validate, cv_groups, fit_specialist, report,
                               specialist_oof, with_specialist)
from aml_ranker.relay import fit_relay


if __name__ == "__main__":
    feats, ep_labels = build_features(load_split(config.TRAIN_DIR))
    labels = feats[["TRANSACTION_HASH"]].merge(pd.read_csv(f"{config.TRAIN_DIR}/labels.csv"),
                                               on="TRANSACTION_HASH", how="left")
    X, y = feats.drop(columns="TRANSACTION_HASH"), labels["is_suspicious"].to_numpy()
    print(f"{len(y):,} payments, {y.sum():,} suspicious, {X.shape[1]} features")

    difficulty = labels["difficulty"].to_numpy()
    stage1, stage2 = cross_validate(X, y, cv_groups(labels), ep_labels)
    oof = blend(stage1, stage2)  # the default upload score
    mixed = with_specialist(oof, specialist_oof(X, y, difficulty, cv_groups(labels)))

    best_t, best_f1, best_p, best_r = 0.5, 0, 0, 0
    for t in np.arange(0.05, 0.96, 0.05):
        p, r, f1, _ = precision_recall_fscore_support(y, oof >= t, average="binary", zero_division=0)
        if f1 > best_f1:
            best_t, best_f1, best_p, best_r = t, f1, p, r

    print(f"Cross-validated  PR-AUC {average_precision_score(y, oof):.3f}   ROC-AUC {roc_auc_score(y, oof):.3f}")
    print("Site metric and top-1% review budget:\n"
          + pd.DataFrame({"blend": report(y, oof, difficulty), "+specialist": report(y, mixed, difficulty)}).to_string())
    print(f"Threshold {best_t:.2f}: precision {best_p:.2f}  recall {best_r:.2f}  F1 {best_f1:.2f}")
    recall = labels.assign(hit=(oof >= best_t)).query("is_suspicious == 1").groupby("family")["hit"].mean()
    print("Recall by laundering family:\n" + recall.round(2).to_string())

    model_dir = os.path.dirname(config.MODEL_PATH)
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump({"model": AlertRanker().fit(X, y, stage1, ep_labels),
                 "specialist": fit_specialist(X, y, difficulty), "relay": fit_relay(X, labels["family"].to_numpy()),
                 "threshold": float(best_t),
                 "features": list(X.columns)}, config.MODEL_PATH)
    json.dump({"pr_auc": average_precision_score(y, oof), "f1": best_f1, "precision": best_p,
               "recall": best_r, "threshold": best_t}, open(f"{model_dir}/cv_metrics.json", "w"), indent=2)
    print(f"Saved {config.MODEL_PATH}")
