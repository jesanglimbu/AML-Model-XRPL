"""SCORE EVERY TRANSACTION.  Shared (run by whoever submits)

    python predict.py              # scores data/test
    python predict.py data/train   # scores the training data (for demos)

Writes outputs/predictions.csv: hash, probability, is_suspicious (0/1), burst ids,
plus every feature -- the trail tracker and ranker read this file.
The probability comes from the two-stage ranker in aml_ranker/; features.py still
supplies the contract columns and the features behind each alert's reasons.
"""
import sys

import joblib
import pandas as pd

import config
from aml_ranker.data import load_split
from aml_ranker.features import build_features
from features import make_features


def predict(folder):
    bundle = joblib.load(config.MODEL_PATH)
    df = make_features(folder)
    X, ep_labels = build_features(load_split(folder))
    scores = bundle["model"].predict(X[bundle["features"]], ep_labels)
    df["probability"] = df["hash"].map(pd.Series(scores, index=X["TRANSACTION_HASH"])).clip(0, 1)
    assert df["probability"].notna().all(), "every payment needs a score"
    df["is_suspicious"] = (df["probability"] >= bundle["threshold"]).astype(int)
    return df


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else config.TEST_DIR
    df = predict(folder)
    df.drop(columns=["time"]).to_csv(config.PREDICTIONS_CSV, index=False)
    print(f"{len(df)} transactions scored, {df['is_suspicious'].sum()} flagged -> {config.PREDICTIONS_CSV}")
