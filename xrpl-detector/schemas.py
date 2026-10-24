"""THE CONTRACT BETWEEN TEAM MEMBERS.  Run `python schemas.py` to check every
output file. You may ADD fields; never rename/remove one without telling the team."""
import json
import os
import sys

import pandas as pd

import config

# outputs/predictions.csv (predict.py) -- one row per transaction, at least:
PREDICTION_COLUMNS = ["hash", "ts", "src", "dst", "asset", "value", "usd",
                      "probability", "is_suspicious", "b3m_id", "b10m_id"]

# outputs/alerts.json (trail_tracker.py) -- one alert = one group of linked flagged payments
ALERT_FIELDS = {
    "alert_id": str,            # "A001"
    "tx_hashes": list,          # flagged payments in time order
    "edges": list,              # [[src, dst], ...] same order as tx_hashes
    "assets": list,             # "XRP" or "issuer:CUR", same order
    "amounts": list,            # native amount, same order
    "amounts_usd": list,        # USD value, same order
    "times": list,              # ISO time, same order
    "probabilities": list,      # model probability, same order
    "accounts": list,           # every account involved
    "minutes_total": (int, float),
}

# outputs/ranked_alerts.json (alert_ranker.py) = alert + these, riskiest first
RANKED_EXTRA_FIELDS = {"risk_score": (int, float), "reasons": list}

# outputs/summaries.json (case_writer.py)
SUMMARY_FIELDS = {"alert_id": str, "risk_score": (int, float), "summary": str, "cited_hashes": list}


# outputs/submission.csv (run_pipeline.py on the test data) -- the file uploaded to the site
SUBMISSION_COLUMNS = ["TRANSACTION_HASH", "score"]


def check_submission(path):
    df = pd.read_csv(path)
    if list(df.columns[:2]) != SUBMISSION_COLUMNS:
        return f"first columns must be {SUBMISSION_COLUMNS}"
    if df.TRANSACTION_HASH.duplicated().any():
        return "duplicate TRANSACTION_HASH"
    if df.score.isna().any() or not df.score.between(0, 1).all():
        return "every score must be between 0 and 1"
    return f"ok ({len(df)} rows)"


def check_csv(path, columns):
    df = pd.read_csv(path, nrows=5)
    missing = [c for c in columns if c not in df.columns]
    return f"missing columns {missing}" if missing else "ok"


def check_json_list(path, fields):
    items = json.load(open(path))
    if not isinstance(items, list):
        return "should be a JSON list"
    for i, item in enumerate(items):
        for name, typ in fields.items():
            if name not in item:
                return f"item {i} missing '{name}'"
            if not isinstance(item[name], typ):
                return f"item {i} field '{name}' has type {type(item[name]).__name__}"
        if "edges" in item and len(item["edges"]) != len(item["tx_hashes"]):
            return f"item {i}: edges and tx_hashes must be the same length"
    return f"ok ({len(items)} items)"


def validate_all():
    checks = [
        (config.PREDICTIONS_CSV, lambda p: check_csv(p, PREDICTION_COLUMNS)),
        (config.SUBMISSION_CSV, check_submission),
        (config.ALERTS_JSON, lambda p: check_json_list(p, ALERT_FIELDS)),
        (config.RANKED_JSON, lambda p: check_json_list(p, {**ALERT_FIELDS, **RANKED_EXTRA_FIELDS})),
        (config.SUMMARIES_JSON, lambda p: check_json_list(p, SUMMARY_FIELDS)),
    ]
    ok_all = True
    for path, check in checks:
        if not os.path.exists(path):
            print(f"  -  {path:30s} not created yet")
            continue
        try:
            msg = check(path)
        except Exception as e:
            msg = f"could not read: {e}"
        ok = msg.startswith("ok")
        ok_all &= ok
        print(f"  {'✓' if ok else '✗'}  {path:30s} {msg}")
    return ok_all


if __name__ == "__main__":
    print("Checking handoff files:")
    sys.exit(0 if validate_all() else 1)
