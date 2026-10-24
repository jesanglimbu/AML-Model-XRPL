"""SCORE EVERY TRANSACTION.  Shared (run by whoever submits)

    python predict.py              # scores data/test
    python predict.py data/train   # scores the training data (for demos)

Writes outputs/predictions.csv: hash, probability, is_suspicious (0/1), burst ids,
plus every feature -- the trail tracker and ranker read this file.
Check with the organisers which columns the submission needs and trim a copy.
"""
import sys

import joblib

import config
from features import make_features


def predict(folder):
    bundle = joblib.load(config.MODEL_PATH)
    df = make_features(folder)
    df["probability"] = bundle["model"].predict_proba(df[bundle["features"]])[:, 1]
    df["is_suspicious"] = (df["probability"] >= bundle["threshold"]).astype(int)
    return df


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else config.TEST_DIR
    df = predict(folder)
    df.drop(columns=["time"]).to_csv(config.PREDICTIONS_CSV, index=False)
    print(f"{len(df)} transactions scored, {df['is_suspicious'].sum()} flagged -> {config.PREDICTIONS_CSV}")
