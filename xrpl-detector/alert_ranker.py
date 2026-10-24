"""ALERT RANKER.  Owner: person C (also owns features.py + train_model.py)

Input : outputs/alerts.json + outputs/predictions.csv (for per-payment features)
Output: outputs/ranked_alerts.json = alert + risk_score (0..1) + reasons, riskiest first

Starter: risk = 0.6 * highest payment probability + 0.4 * average, plus a small
bonus for bigger trails. Reasons come from features.reasons_for().

TODO / stretch -- "learn from what analysts close or escalate":
  add a CSV alert_id,decision and fit a LogisticRegression on alert-level
  features (size, minutes_total, usd total, mean probability) to re-weight.
"""
import json
from collections import Counter

import numpy as np
import pandas as pd

import config
from features import reasons_for


def rank(alerts, pred):
    by_hash = pred.set_index("hash")
    ranked = []
    for a in alerts:
        p = np.array(a["probabilities"])
        size_bonus = min(len(p), 10) / 100                     # up to +0.10
        score = 0.5*p.mean() +0.3*p.max() +0.2* min(len(p), 20) /20
        reasons = Counter()
        for h in a["tx_hashes"]:
            for r in reasons_for(by_hash.loc[h]):
                reasons[r] += 1
        top = [r for r, _ in reasons.most_common(4)]
        top.append(f"{len(p)} flagged payments, total ${sum(a['amounts_usd']):,.0f}, "
                   f"over {a['minutes_total']} min")
        ranked.append({**a, "risk_score": round(float(score), 3), "reasons": top})
    return sorted(ranked, key=lambda x: x["risk_score"], reverse=True)


if __name__ == "__main__":
    alerts = json.load(open(config.ALERTS_JSON))
    ranked = rank(alerts, pd.read_csv(config.PREDICTIONS_CSV))
    json.dump(ranked, open(config.RANKED_JSON, "w"), indent=2)
    for a in ranked[:5]:
        print(f"{a['alert_id']}  {a['risk_score']:.2f}  " + "; ".join(a["reasons"]))
