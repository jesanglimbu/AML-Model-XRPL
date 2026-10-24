"""MONEY TRAIL TRACKER.  Owners: person A (logic) + person B (trail_graph.py)

Input : outputs/predictions.csv  (every payment, its probability and burst ids)
Output: outputs/alerts.json      (schemas.ALERT_FIELDS)

The highest-scored config.FLAG_TOP_SHARE of payments (top 1%) are grouped by their burst id
(config.BURST_LEVEL -- payments linked by chain / fan-out / fan-in within 10 min).
Each group with >= MIN_ALERT_TXS flagged payments becomes one alert.

Ideas to improve (TODO):
  - also pull in UNflagged payments of the same burst so the trail is complete
  - follow funds after the burst ends (where did they cash out?)
  - label the shape: chain / fan-out / fan-in / cycle (nx.simple_cycles on the edges)
"""
import json

import pandas as pd

import config


def find_trails(pred):
    top_n = int(round(config.FLAG_TOP_SHARE * len(pred)))
    flagged = pred.nlargest(top_n, "probability").sort_values("ts")
    alerts = []
    for _, g in flagged.groupby(f"{config.BURST_LEVEL}_id"):
        if len(g) < config.MIN_ALERT_TXS:
            continue
        alerts.append({
            "alert_id": f"A{len(alerts) + 1:03d}",
            "tx_hashes": g["hash"].tolist(),
            "edges": g[["src", "dst"]].values.tolist(),
            "assets": [a if a == "XRP" else a.split(":")[1] for a in g["asset"]],
            "amounts": g["value"].round(6).tolist(),
            "amounts_usd": g["usd"].round(2).tolist(),
            "times": pd.to_datetime(g["ts"], unit="s", utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ").tolist(),
            "probabilities": g["probability"].round(3).tolist(),
            "accounts": sorted(set(g["src"]) | set(g["dst"])),
            "minutes_total": round((g["ts"].max() - g["ts"].min()) / 60, 1),
        })
    return alerts


if __name__ == "__main__":
    alerts = find_trails(pd.read_csv(config.PREDICTIONS_CSV))
    json.dump(alerts, open(config.ALERTS_JSON, "w"), indent=2)
    print(f"{len(alerts)} alerts -> {config.ALERTS_JSON}")
