"""HOW GOOD ARE THE TRAILS?  Honest test on the training data.

    python tracker_eval.py                 # current config settings
    python tracker_eval.py 0.5             # try a different ALERT_MIN_MEAN_PROB

Uses OUT-OF-FOLD predictions (each payment scored by a model that never saw its
scenario), so the numbers are fair -- not inflated like running on data the model trained on.
The first run builds them (~1 min) and caches outputs/train_oof.csv.

  precision : share of payments in alerts that are really suspicious
  purity    : share of an alert's payments from ONE scenario (1.0 = one clean operation)
  coverage  : real suspicious scenarios that got at least one alert
"""
import os
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import GroupKFold

import config
import trail_tracker
from features import ALL_FEATURES, make_features

OOF_CSV = f"{config.OUT_DIR}/train_oof.csv"

if not os.path.exists(OOF_CSV):
    print("building out-of-fold predictions (first run only)...")
    df = make_features(config.TRAIN_DIR)
    lab = pd.read_csv(f"{config.TRAIN_DIR}/labels.csv").rename(columns={"TRANSACTION_HASH": "hash"})
    df = df.merge(lab[["hash", "is_suspicious", "scenario_id"]], on="hash")
    X, y = df[ALL_FEATURES], df["is_suspicious"]
    df["probability"] = 0.0
    for trn, val in GroupKFold(5).split(X, y, df["scenario_id"].fillna(df["hash"])):
        m = HistGradientBoostingClassifier(max_iter=400, learning_rate=0.05,
                                           class_weight="balanced", random_state=0)
        df.loc[df.index[val], "probability"] = m.fit(X.iloc[trn], y.iloc[trn]).predict_proba(X.iloc[val])[:, 1]
    df.rename(columns={"is_suspicious": "true_label"}).drop(columns=["time"]).to_csv(OOF_CSV, index=False)

pred = pd.read_csv(OOF_CSV)
if len(sys.argv) > 1:
    trail_tracker.MIN_MEAN_PROB = float(sys.argv[1])
alerts = trail_tracker.find_trails(pred)

labels = pd.read_csv(f"{config.TRAIN_DIR}/labels.csv").set_index("TRANSACTION_HASH")
suspicious = set(labels.loc[labels["is_suspicious"] == 1, "scenario_id"])
rows, found = [], set()
for a in alerts:
    lab = labels.loc[a["tx_hashes"]]
    top = lab["scenario_id"].value_counts()
    rows.append({"precision": lab["is_suspicious"].mean(),
                 "purity": top.iloc[0] / len(lab) if len(top) else 0.0,
                 "family": lab["family"].mode().iloc[0], "shape": a["shape"]})
    found |= set(lab.loc[lab["is_suspicious"] == 1, "scenario_id"])
r = pd.DataFrame(rows)

print(f"threshold {trail_tracker.MIN_MEAN_PROB}: {len(r)} alerts   precision {r['precision'].mean():.2f}   "
      f"purity {r['purity'].mean():.2f}   coverage {len(found & suspicious)}/{len(suspicious)} scenarios")
print(f"alerts with a traced cash-out: {sum(bool(a['cash_out']) for a in alerts)}")
print("\nOur shape vs true family:")
print(pd.crosstab(r["family"], r["shape"]).to_string())
