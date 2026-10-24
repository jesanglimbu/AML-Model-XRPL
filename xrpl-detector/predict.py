"""SCORE EVERY TRANSACTION.  Shared (run by whoever submits)

    python predict.py              # scores data/test
    python predict.py data/train   # scores the training data (for demos)

Writes outputs/predictions.csv: hash, probability, is_suspicious (0/1), burst ids,
plus every feature -- the trail tracker and ranker read this file.
The probability comes from the two-stage ranker in aml_ranker/; features.py still
supplies the contract columns and the features behind each alert's reasons.
On the test data it also writes one upload file per scoring variant
(config.SUBMISSION_VARIANTS): stage 1 only, stage 2 only (= probability), and a blend.
"""
import sys

import joblib
import pandas as pd

import config
from aml_ranker.data import load_split
from aml_ranker.features import build_features
from aml_ranker.model import blend
from features import make_features


def predict(folder):
    bundle = joblib.load(config.MODEL_PATH)
    df = make_features(folder)
    X, ep_labels = build_features(load_split(folder))
    stage1, stage2 = bundle["model"].predict_stages(X[bundle["features"]], ep_labels)
    for name, scores in (("stage1", stage1), ("stage2", stage2), ("blend", blend(stage1, stage2))):
        df[f"score_{name}"] = df["hash"].map(pd.Series(scores, index=X["TRANSACTION_HASH"])).clip(0, 1)
        assert df[f"score_{name}"].notna().all(), "every payment needs a score"
    df["probability"] = df["score_stage2"]
    df["is_suspicious"] = (df["probability"] >= bundle["threshold"]).astype(int)
    return df


def write_submissions(df):
    """One TRANSACTION_HASH,score file per variant, to compare on the leaderboard."""
    for name, path in config.SUBMISSION_VARIANTS.items():
        df[["hash", f"score_{name}"]].set_axis(["TRANSACTION_HASH", "score"], axis=1).to_csv(path, index=False)
        print(f"    {name:7s} -> {path}")


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else config.TEST_DIR
    df = predict(folder)
    df.drop(columns=["time"]).to_csv(config.PREDICTIONS_CSV, index=False)
    print(f"{len(df)} transactions scored, {df['is_suspicious'].sum()} flagged -> {config.PREDICTIONS_CSV}")
    if folder == config.TEST_DIR:
        write_submissions(df)
