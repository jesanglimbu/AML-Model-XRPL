"""SCORE EVERY TRANSACTION.  Shared (run by whoever submits)

    python predict.py              # scores data/test
    python predict.py data/train   # scores the training data (for demos)

Writes outputs/predictions.csv: hash, probability, is_suspicious (0/1), burst ids,
plus every feature -- the trail tracker and ranker read this file.
The probability comes from the two-stage ranker in aml_ranker/; features.py still
supplies the contract columns and the features behind each alert's reasons.
On the test data it also writes one upload file per scoring variant
(config.SUBMISSION_VARIANTS): stage 1 only, stage 2 only, their blend (65.9 on the
leaderboard vs 65.6 and 65.4), and the blend mixed with the medium specialist.
config.DEFAULT_SCORE picks which one becomes `probability` and submission.csv.
"""
import sys

import joblib
import pandas as pd

import config
from aml_ranker.data import load_split
from aml_ranker.features import build_features
from aml_ranker.model import blend, with_specialist
from aml_ranker.mule import neighbour_max, with_mule
from features import make_features


def predict(folder):
    bundle = joblib.load(config.MODEL_PATH)
    df = make_features(folder)
    payments = load_split(folder)
    X, ep_labels = build_features(payments)
    stage1, stage2 = bundle["model"].predict_stages(X[bundle["features"]], ep_labels)
    variants = {"stage1": stage1, "stage2": stage2, "blend": blend(stage1, stage2)}
    if "specialist" in bundle:  # models trained before the specialist existed have none
        variants["specialist"] = with_specialist(variants["blend"], bundle["specialist"].predict(X[bundle["features"]]))
    pay = payments.set_index("TRANSACTION_HASH").loc[X["TRANSACTION_HASH"]]
    near = neighbour_max(variants["blend"], pay.sender.to_numpy(), pay.receiver.to_numpy(), pay.t.to_numpy())
    variants["mule"] = with_mule(variants["blend"], near)
    for name, scores in variants.items():
        df[f"score_{name}"] = df["hash"].map(pd.Series(scores, index=X["TRANSACTION_HASH"])).clip(0, 1)
        assert df[f"score_{name}"].notna().all(), "every payment needs a score"
    df["probability"] = df[f"score_{config.DEFAULT_SCORE}"]
    df["is_suspicious"] = (df["probability"] >= bundle["threshold"]).astype(int)
    return df


def write_submissions(df):
    """One TRANSACTION_HASH,score file per variant, to compare on the leaderboard."""
    for name, path in config.SUBMISSION_VARIANTS.items():
        if f"score_{name}" not in df:
            continue
        df[["hash", f"score_{name}"]].set_axis(["TRANSACTION_HASH", "score"], axis=1).to_csv(path, index=False)
        print(f"    {name:7s} -> {path}")


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else config.TEST_DIR
    df = predict(folder)
    df.drop(columns=["time"]).to_csv(config.PREDICTIONS_CSV, index=False)
    print(f"{len(df)} transactions scored, {df['is_suspicious'].sum()} flagged -> {config.PREDICTIONS_CSV}")
    if folder == config.TEST_DIR:
        write_submissions(df)
