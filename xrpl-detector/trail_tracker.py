"""MONEY TRAIL TRACKER.  Owners: person A (logic) + person B (trail_graph.py)

Input : outputs/predictions.csv  (every payment, its probability and burst ids)
Output: outputs/alerts.json      (schemas.ALERT_FIELDS + extra fields below)

How it works:
  1. Payments are grouped into BURSTS (config.BURST_LEVEL): payments linked by
     chain / fan-out / fan-in within 3 minutes.
  2. A burst becomes an alert if it has >= MIN_ALERT_TXS payments and the
     AVERAGE model probability across the burst >= ALERT_MIN_MEAN_PROB.
     (Scoring the whole burst beats scoring payments one by one: a laundering
     operation is suspicious as a group, so averaging smooths out noise.)
  3. Extra fields describe the trail:
       shape     -> chain / cycle / fan_out / fan_in / fan_out_in / mixed
       origins   -> accounts where money entered (nobody in the burst paid them)
       sinks     -> accounts where money ended up (they paid nobody in the burst)
       cash_out  -> where the sinks sent money NEXT (within CASHOUT_WINDOW_MIN)

Measure it:  python tracker_eval.py   (uses honest out-of-fold predictions)
"""
import json

import networkx as nx
import numpy as np
import pandas as pd

import config

MIN_MEAN_PROB = getattr(config, "ALERT_MIN_MEAN_PROB", 0.6)
CASHOUT_WINDOW_S = 60 * getattr(config, "CASHOUT_WINDOW_MIN", 60)


def classify_shape(edges):
    """Name the pattern formed by a list of [src, dst] payments."""
    G = nx.DiGraph()
    G.add_edges_from(edges)
    if not nx.is_directed_acyclic_graph(G):
        return "cycle"                       # money comes back to an account it passed through
    indeg, outdeg = dict(G.in_degree()), dict(G.out_degree())
    if all(indeg[n] <= 1 and outdeg[n] <= 1 for n in G):
        return "chain"                       # A -> B -> C -> D
    origins = [n for n in G if indeg[n] == 0]
    sinks = [n for n in G if outdeg[n] == 0]
    if len(origins) == 1 and len(sinks) == 1:
        return "fan_out_in"                  # split up, then gathered back together
    if len(origins) == 1:
        return "fan_out"                     # one account spreads money to many
    if len(sinks) == 1:
        return "fan_in"                      # many accounts feed one collector
    return "mixed"


def trace_cash_out(sinks, end_ts, sends_by_acct, exclude):
    """Where did the money go after the burst? Next payments out of each sink."""
    out = []
    for s in sinks:
        g = sends_by_acct.get(s)
        if g is None:
            continue
        nxt = g[(g["ts"] > end_ts) & (g["ts"] <= end_ts + CASHOUT_WINDOW_S) & (~g["hash"].isin(exclude))]
        for _, r in nxt.iterrows():
            out.append({"hash": r["hash"], "from": s, "to": r["dst"], "usd": round(float(r["usd"]), 2),
                        "minutes_after": round((r["ts"] - end_ts) / 60, 1)})
    return out


def find_trails(pred):
    pred = pred.sort_values("ts")
    burst_col = f"{config.BURST_LEVEL}_id"
    stats = pred.groupby(burst_col)["probability"].agg(["size", "mean"])
    keep = stats[(stats["size"] >= config.MIN_ALERT_TXS) & (stats["mean"] >= MIN_MEAN_PROB)]
    keep = keep.sort_values("mean", ascending=False)
    sends_by_acct = {a: g for a, g in pred.groupby("src")}

    alerts = []
    for bid in keep.index:
        g = pred[pred[burst_col] == bid]
        edges = g[["src", "dst"]].values.tolist()
        G = nx.DiGraph()
        G.add_edges_from(edges)
        sinks = sorted(n for n in G if G.out_degree(n) == 0)
        alerts.append({
            # --- contract fields (schemas.ALERT_FIELDS) ---
            "alert_id": f"A{len(alerts) + 1:03d}",
            "tx_hashes": g["hash"].tolist(),
            "edges": edges,
            "assets": [a if a == "XRP" else a.split(":")[1] for a in g["asset"]],
            "amounts": g["value"].round(6).tolist(),
            "amounts_usd": g["usd"].round(2).tolist(),
            "times": pd.to_datetime(g["ts"], unit="s", utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ").tolist(),
            "probabilities": g["probability"].round(3).tolist(),
            "accounts": sorted(set(g["src"]) | set(g["dst"])),
            "minutes_total": round((g["ts"].max() - g["ts"].min()) / 60, 1),
            # --- extra fields ---
            "burst_mean_probability": round(float(keep.loc[bid, "mean"]), 3),
            "shape": classify_shape(edges),
            "origins": sorted(n for n in G if G.in_degree(n) == 0),
            "sinks": sinks,
            "cash_out": trace_cash_out(sinks, g["ts"].max(), sends_by_acct, set(g["hash"])),
        })
    return alerts


if __name__ == "__main__":
    alerts = find_trails(pd.read_csv(config.PREDICTIONS_CSV))
    json.dump(alerts, open(config.ALERTS_JSON, "w"), indent=2)
    print(f"{len(alerts)} alerts -> {config.ALERTS_JSON}")
    print(pd.Series([a["shape"] for a in alerts]).value_counts().to_string())
