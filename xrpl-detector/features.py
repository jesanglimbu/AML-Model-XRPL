"""FEATURES -- shared by train_model.py and predict.py.  Owner: alert ranker person (C)

Per-transaction features. Works on ANY transactions/transfers/market_rates files
(training or test) -- it never looks at labels.

Key finding from the training data: suspicious scenarios have the SAME shapes as
benign ones (fan-out, chain, cycle...) but move MUCH faster (~1 min between
payments vs ~10 min). So most features measure speed / velocity around each payment.
"""
import json

import numpy as np
import pandas as pd


def load(tx_path, tr_path, rates_path):
    tx = pd.read_parquet(tx_path)
    tr = pd.read_parquet(tr_path)
    rates = pd.read_csv(rates_path)
    return tx, tr, rates


def parse_tx(tx, tr, rates):
    df = pd.DataFrame({"hash": tx["TRANSACTION_HASH"], "time": tx["DATETIME"],
                       "ts": pd.to_numeric(tx["TIMESTAMP"]), "src": tx["ACCOUNT"],
                       "fee": tx["FEE"], "seq": pd.to_numeric(tx["SEQUENCE"], errors="coerce")})
    extra = tx["EXTRA_TRANSACTION_FIELDS"].map(json.loads)
    df["dst"] = extra.map(lambda d: d.get("Destination"))

    def amount(d):
        a = d.get("Amount")
        if isinstance(a, str):
            return "XRP", int(a) / 1e6
        return f'{a["issuer"]}:{a["currency"]}', float(a["value"])

    df["asset"], df["value"] = zip(*extra.map(amount))
    df["is_xrp"] = (df["asset"] == "XRP").astype(int)
    df["has_sendmax"] = extra.map(lambda d: "SendMax" in d).astype(int)
    df["has_paths"] = extra.map(lambda d: "Paths" in d).astype(int)
    df["n_transfers"] = df["hash"].map(tr.groupby("TRANSACTION_HASH").size()).fillna(1)

    # convert to USD with the hourly market rates
    rates = rates.assign(hour=rates["TIMESTAMP"] // 3600 * 3600)
    rate = rates.groupby(["hour", "ASSET"])["PRICE_MICRO_USD"].first() / 1e6
    hour = df["ts"] // 3600 * 3600
    df["usd"] = df["value"] * [rate.get((h, a), np.nan) for h, a in zip(hour, df["asset"])]
    df["usd"] = df["usd"].fillna(df["value"])
    return df.sort_values("ts").reset_index(drop=True)


def _prev_event_gap(events, key_col, ts, keys):
    """For each (key, ts): seconds since that key's previous event strictly before ts."""
    out = np.full(len(ts), np.nan)
    ev = events.sort_values("ts")
    by_key = {k: g["ts"].to_numpy() for k, g in ev.groupby(key_col)}
    for i, (k, t) in enumerate(zip(keys, ts)):
        arr = by_key.get(k)
        if arr is None:
            continue
        j = np.searchsorted(arr, t, side="left") - 1
        if j >= 0:
            out[i] = t - arr[j]
    return out


def _next_event_gap(events, key_col, ts, keys):
    out = np.full(len(ts), np.nan)
    by_key = {k: np.sort(g["ts"].to_numpy()) for k, g in events.groupby(key_col)}
    for i, (k, t) in enumerate(zip(keys, ts)):
        arr = by_key.get(k)
        if arr is None:
            continue
        j = np.searchsorted(arr, t, side="right")
        if j < len(arr):
            out[i] = arr[j] - t
    return out


def _count_window(events, key_col, ts, keys, window):
    out = np.zeros(len(ts))
    by_key = {k: np.sort(g["ts"].to_numpy()) for k, g in events.groupby(key_col)}
    for i, (k, t) in enumerate(zip(keys, ts)):
        arr = by_key.get(k)
        if arr is None:
            continue
        out[i] = np.searchsorted(arr, t + window, side="right") - np.searchsorted(arr, t - window, side="left") - 1
    return out


def build_features(df):
    f = df.copy()
    ts = f["ts"].to_numpy()
    # every account appearance (as sender or receiver)
    touch = pd.concat([f[["src", "ts"]].rename(columns={"src": "acct"}),
                       f[["dst", "ts"]].rename(columns={"dst": "acct"})])
    sends = f[["src", "ts"]].rename(columns={"src": "acct"})
    recvs = f[["dst", "ts"]].rename(columns={"dst": "acct"})

    # --- speed / velocity (the main signal) ---
    f["src_hold_s"] = _prev_event_gap(recvs, "acct", ts, f["src"])     # since sender last RECEIVED
    f["src_prev_send_s"] = _prev_event_gap(sends, "acct", ts, f["src"])
    f["dst_next_send_s"] = _next_event_gap(sends, "acct", ts, f["dst"])  # how fast receiver passes it on
    f["dst_prev_touch_s"] = _prev_event_gap(touch, "acct", ts, f["dst"])
    for w, name in [(300, "5m"), (900, "15m"), (3600, "1h")]:
        f[f"src_tx_{name}"] = _count_window(touch, "acct", ts, f["src"], w)
        f[f"dst_tx_{name}"] = _count_window(touch, "acct", ts, f["dst"], w)
    for c in ["src_hold_s", "src_prev_send_s", "dst_next_send_s", "dst_prev_touch_s"]:
        f[c] = np.log1p(f[c].fillna(7 * 86400))

    # --- amounts ---
    f["log_usd"] = np.log1p(f["usd"])
    f["usd_round10"] = (np.abs(f["usd"] - np.round(f["usd"], -1)) < 0.5).astype(int)
    # how this payment compares to what the sender last received (pass-through)
    last_in = {}
    ratio = np.full(len(f), np.nan)
    for i, (s, d, u) in enumerate(zip(f["src"], f["dst"], f["usd"])):
        if s in last_in:
            ratio[i] = u / last_in[s] if last_in[s] else np.nan
        last_in[d] = u
    f["pass_ratio"] = np.clip(ratio, 0, 5)

    # --- account history (relative to first sighting in this file) ---
    first = touch.groupby("acct")["ts"].min()
    f["src_age_h"] = (f["ts"] - f["src"].map(first)) / 3600
    f["dst_age_h"] = (f["ts"] - f["dst"].map(first)) / 3600
    deg_out = f.groupby("src")["dst"].nunique()
    deg_in = f.groupby("dst")["src"].nunique()
    f["src_out_deg"] = f["src"].map(deg_out).fillna(0)
    f["src_in_deg"] = f["src"].map(deg_in).fillna(0)
    f["dst_in_deg"] = f["dst"].map(deg_in).fillna(0)
    f["dst_out_deg"] = f["dst"].map(deg_out).fillna(0)
    f["pair_count"] = f.groupby(["src", "dst"])["hash"].transform("size")
    f["hour_of_day"] = f["time"].dt.hour
    return f


FEATURES = ["is_xrp", "has_sendmax", "has_paths", "n_transfers", "log_usd", "usd_round10",
            "src_hold_s", "src_prev_send_s", "dst_next_send_s", "dst_prev_touch_s",
            "src_tx_5m", "dst_tx_5m", "src_tx_15m", "dst_tx_15m", "src_tx_1h", "dst_tx_1h",
            "pass_ratio", "src_age_h", "dst_age_h", "src_out_deg", "src_in_deg",
            "dst_in_deg", "dst_out_deg", "pair_count", "hour_of_day"]


# ---------------------------------------------------------------------------
# BURST features: link payments that are part of the same fast money movement.
# Two payments are linked if (a) the 2nd sender is the 1st receiver (money moves on),
# (b) same sender, or (c) same receiver -- AND they happen within `window` seconds.
# Each connected group is a "burst" (this is the money-trail idea, as features).
# ---------------------------------------------------------------------------
def _find(parent, i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]
        i = parent[i]
    return i


def burst_ids(f, window):
    n = len(f)
    parent = list(range(n))
    ts = f["ts"].to_numpy()
    last = {}                                     # (role, account) -> (index, ts) of latest event
    for i, (s, d, t) in enumerate(zip(f["src"], f["dst"], ts)):
        for key in (("recv", s), ("send", s), ("recv", d)):   # chain, fan-out, fan-in
            if key in last and t - last[key][1] <= window:
                a, b = _find(parent, i), _find(parent, last[key][0])
                if a != b:
                    parent[a] = b
        last[("send", s)] = (i, t)
        last[("recv", d)] = (i, t)
    return np.array([_find(parent, i) for i in range(n)])


def add_burst_features(f, windows=(180, 600)):
    for w in windows:
        tag = f"b{w // 60}m"
        bid = burst_ids(f, w)
        g = f.assign(_b=bid).groupby("_b")
        size = g["hash"].transform("size")
        span = g["ts"].transform(lambda s: s.max() - s.min())
        f[f"{tag}_size"] = size
        f[f"{tag}_span_min"] = span / 60
        f[f"{tag}_rate"] = size / (span / 60 + 1)           # payments per minute
        accts = pd.concat([f.assign(_b=bid)[["_b", "src"]].rename(columns={"src": "a"}),
                           f.assign(_b=bid)[["_b", "dst"]].rename(columns={"dst": "a"})])
        f[f"{tag}_accts"] = pd.Series(bid).map(accts.groupby("_b")["a"].nunique()).to_numpy()
        f[f"{tag}_usd_cv"] = (g["usd"].transform("std") / g["usd"].transform("mean")).fillna(0)
        f[f"{tag}_usd_total"] = np.log1p(g["usd"].transform("sum"))
        f[f"{tag}_id"] = bid
    return f


BURST_FEATURES = [f"b{w}m_{k}" for w in (3, 10) for k in ("size", "span_min", "rate", "accts", "usd_cv", "usd_total")]


ALL_FEATURES = FEATURES + BURST_FEATURES


def make_features(folder):
    """folder must contain transactions.parquet, transfers.parquet, market_rates.csv"""
    tx, tr, rates = load(f"{folder}/transactions.parquet", f"{folder}/transfers.parquet",
                         f"{folder}/market_rates.csv")
    return add_burst_features(build_features(parse_tx(tx, tr, rates)))


def reasons_for(row):
    """Plain-English reasons for one payment (used by the ranker and case writer)."""
    r = []
    nxt = np.expm1(row["dst_next_send_s"]) / 60
    hold = np.expm1(row["src_hold_s"]) / 60
    if nxt < 5:
        r.append(f"receiver passed funds on within {nxt:.1f} min")
    if hold < 5:
        r.append(f"sender forwarded funds {hold:.1f} min after receiving them")
    if row["b3m_size"] >= 4:
        r.append(f"part of a burst of {int(row['b3m_size'])} linked payments in "
                 f"{row['b3m_span_min']:.0f} min across {int(row['b3m_accts'])} accounts")
    if 0.8 <= row.get("pass_ratio", 0) <= 1.05:
        r.append(f"forwarded {row['pass_ratio']:.0%} of the amount it last received")
    if row["src_tx_5m"] >= 3:
        r.append(f"sender involved in {int(row['src_tx_5m'])} other payments within 5 min")
    return r or ["unusual combination of timing and amount features"]
