"""Per-transaction features for the alert ranker.

Everything is computed from a single split's own week of activity (the task is an
offline investigation, so looking both backwards and forwards in time is allowed).
Feature families:

* intrinsic   - value, conversion legs, spread, slack, assets, time of day
* pair        - is this sender->receiver relationship new, recurring, reciprocated
* profile     - each account's weekly behaviour and how unusual this payment is for it
* windows     - multi-scale burst counts around the sender and receiver
* chaining    - does money arrive just before / leave just after, in similar amounts
* episodes    - connected groups of payments formed by linking an account's
                consecutive events within a time scale; summarise each group
"""
import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

MIN, HOUR, DAY = 60, 3600, 86400
WINDOWS = [MIN, 5 * MIN, 30 * MIN, 2 * HOUR, 12 * HOUR, 2 * DAY]
EPISODE_SCALES = [30, MIN, 2 * MIN, 5 * MIN, 10 * MIN, 30 * MIN, HOUR]
NOVEL_EPISODE_SCALES = [30 * MIN, 2 * HOUR, 6 * HOUR, DAY]


def _index_by(keys, times, values=None):
    """account -> (sorted times, aligned values, aligned tx positions)."""
    order = np.lexsort((times, keys))
    keys, times = keys[order], times[order]
    values = values[order] if values is not None else None
    cuts = np.flatnonzero(np.diff(keys)) + 1
    out = {}
    for seg in np.split(np.arange(len(keys)), cuts):
        if len(seg):
            out[keys[seg[0]]] = (times[seg], None if values is None else values[seg], order[seg])
    return out


def _count(index, accounts, t, before, after, exclude_self=False):
    """Events of each account in [t - before, t + after]."""
    out = np.zeros(len(t))
    for acc in np.unique(accounts):
        q = np.flatnonzero(accounts == acc)
        if acc not in index:
            continue
        times = index[acc][0]
        out[q] = np.searchsorted(times, t[q] + after, "right") - np.searchsorted(times, t[q] - before, "left")
    return out - exclude_self


def _nearest(index, accounts, t, direction):
    """Gap to the account's nearest event after (direction=+1) or before (-1) t, and that event's value."""
    gap = np.full(len(t), np.nan)
    val = np.full(len(t), np.nan)
    for acc in np.unique(accounts):
        if acc not in index:
            continue
        q = np.flatnonzero(accounts == acc)
        times, values, _ = index[acc]
        if direction > 0:
            i = np.searchsorted(times, t[q], "left")
            ok = i < len(times)
        else:
            i = np.searchsorted(times, t[q], "right") - 1
            ok = i >= 0
        gap[q[ok]] = np.abs(times[i[ok]] - t[q[ok]])
        val[q[ok]] = values[i[ok]]
    return gap, val


def _nearest_other(index, accounts, t):
    """Gap to the account's closest other event (either role, either direction)."""
    out = np.full(len(t), float(7 * DAY))
    for acc in np.unique(accounts):
        times = index[acc][0]
        q = np.flatnonzero(accounts == acc)
        lo = np.searchsorted(times, t[q], "left")
        hi = np.searchsorted(times, t[q], "right")
        # the payment itself occupies one slot in [lo, hi); any extra tie is a 0 gap
        ties = hi - lo > 1
        before = np.where(lo > 0, t[q] - times[np.maximum(lo - 1, 0)], 7 * DAY)
        after = np.where(hi < len(times), times[np.minimum(hi, len(times) - 1)] - t[q], 7 * DAY)
        out[q] = np.where(ties, 0, np.minimum(before, after))
    return out


def _flow(index, accounts, t, amount, lo, hi):
    """Within [t + lo, t + hi] of the account's events: summed value and best amount match."""
    total = np.zeros(len(t))
    match = np.full(len(t), np.nan)
    for acc in np.unique(accounts):
        if acc not in index:
            continue
        times, values, _ = index[acc]
        cs = np.concatenate([[0.0], np.cumsum(values)])
        for k in np.flatnonzero(accounts == acc):
            a, b = np.searchsorted(times, t[k] + lo, "left"), np.searchsorted(times, t[k] + hi, "right")
            if b > a:
                total[k] = cs[b] - cs[a]
                match[k] = np.min(np.abs(np.log(values[a:b] / amount[k])))
    return total, match


def _episodes(sender, receiver, t, scale, mask=None):
    """Label connected payment groups: link each account's consecutive events within `scale` seconds."""
    n = len(t)
    use = np.ones(n, bool) if mask is None else mask
    pos = np.flatnonzero(use)
    acc = np.concatenate([sender[pos], receiver[pos]])
    tt = np.concatenate([t[pos], t[pos]])
    tx = np.concatenate([pos, pos])
    order = np.lexsort((tt, acc))
    acc, tt, tx = acc[order], tt[order], tx[order]
    link = (acc[1:] == acc[:-1]) & (tt[1:] - tt[:-1] <= scale)
    rows, cols = tx[:-1][link], tx[1:][link]
    graph = coo_matrix((np.ones(len(rows)), (rows, cols)), shape=(n, n))
    _, labels = connected_components(graph, directed=False)
    labels = labels.astype(np.int64)
    if mask is not None:
        labels[~use] = -1 - np.flatnonzero(~use)  # excluded payments are singletons
    return labels


def _episode_summary(df, labels, prefix):
    g = pd.DataFrame({
        "ep": labels, "t": df.t, "usd": df.usd, "conv": df.has_sendmax, "novel": df.pair_n == 1,
        "sender": df.sender_id, "receiver": df.receiver_id,
    }).groupby("ep")
    size = g.t.transform("size")
    span = g.t.transform("max") - g.t.transform("min")
    accounts = g.apply(lambda d: len(np.union1d(d.sender, d.receiver)), include_groups=False)
    senders, receivers = g.sender.transform("nunique"), g.receiver.transform("nunique")
    n_acc = pd.Series(labels).map(accounts).to_numpy()
    f = {
        f"{prefix}_size": size,
        f"{prefix}_span": np.log1p(span),
        f"{prefix}_rate": size / (span + 60),
        f"{prefix}_accounts": n_acc,
        f"{prefix}_cyclomatic": size - n_acc + 1,  # >0 means repeated/looping relations
        f"{prefix}_fan_out": size / senders,
        f"{prefix}_fan_in": size / receivers,
        f"{prefix}_log_usd_sum": np.log1p(g.usd.transform("sum")),
        f"{prefix}_usd_cv": (g.usd.transform("std") / g.usd.transform("mean")).fillna(0),
        f"{prefix}_conv": g.conv.transform("mean"),
        f"{prefix}_novel": g.novel.transform("mean"),
        f"{prefix}_position": (df.t - g.t.transform("min")) / (span + 1),
        f"{prefix}_gap_median": np.log1p(g.t.transform(lambda x: np.median(np.diff(np.sort(x))) if len(x) > 1 else 7 * DAY)),
    }
    return pd.DataFrame(f)


def build_features(df):
    """Return (features, episode labels) for a frame from data.load_split."""
    df = df.copy()
    accounts, _ = pd.factorize(pd.concat([df.sender, df.receiver]))
    df["sender_id"], df["receiver_id"] = accounts[: len(df)], accounts[len(df):]
    s, r, t = df.sender_id.to_numpy(), df.receiver_id.to_numpy(), df.t.to_numpy()
    usd, cost = df.usd.to_numpy(), df.cost_usd.to_numpy()
    f = {}

    # --- intrinsic -------------------------------------------------------------
    f["log_usd"] = np.log1p(usd)
    f["log_cost"] = np.log1p(cost)
    f["spread"] = cost / usd - 1
    f["sendmax_slack"] = df.sendmax_usd.to_numpy() / cost - 1
    f["n_legs"] = df.n_legs
    f["conversion"] = df.has_sendmax.astype(float)
    f["same_asset"] = (df.src_asset == df.dst_asset).astype(float)
    f["dst_xrp"] = (df.dst_asset == "XRP").astype(float)
    f["src_xrp"] = (df.src_asset == "XRP").astype(float)
    f["dst_currency"] = pd.Categorical(df.dst_asset.str[-3:], ["XRP", "USD", "EUR", "GBP"]).codes
    f["src_currency"] = pd.Categorical(df.src_asset.str[-3:], ["XRP", "USD", "EUR", "GBP"]).codes
    f["fee"] = df.fee
    f["ledger_pos"] = df.ledger_pos
    f["hour"] = (t % DAY) // HOUR
    f["units_frac"] = np.round(df.dst_units * 100) % 100  # cents of the delivered amount
    f["round_usd"] = (np.abs(usd - np.round(usd, -1)) < 0.5).astype(float)

    # --- pair relationships -----------------------------------------------------
    pair = pd.Series(list(zip(s, r)))
    df["pair_n"] = pair.map(pair.value_counts()).to_numpy()
    f["pair_n"] = df.pair_n
    f["pair_rank"] = pair.groupby(pair).cumcount().to_numpy()
    f["pair_prev_gap"] = np.log1p(pd.Series(t).groupby(pair).diff().fillna(7 * DAY).to_numpy())
    reverse = pd.Series(list(zip(r, s)))
    f["reverse_n"] = reverse.map(pair.value_counts()).fillna(0).to_numpy()

    # --- account profiles over the whole window ---------------------------------
    sends = _index_by(s, t, cost)
    recvs = _index_by(r, t, usd)
    out_cp = pd.Series(r).groupby(s).nunique()
    in_cp = pd.Series(s).groupby(r).nunique()
    n_send = pd.Series(s).value_counts()
    n_recv = pd.Series(r).value_counts()
    med_send = pd.Series(usd).groupby(s).median()
    med_recv = pd.Series(usd).groupby(r).median()
    tot_send = pd.Series(cost).groupby(s).sum()
    tot_recv = pd.Series(usd).groupby(r).sum()
    novel_out = pd.Series(df.pair_n.to_numpy() == 1).groupby(s).mean()
    novel_in = pd.Series(df.pair_n.to_numpy() == 1).groupby(r).mean()
    for role, a in (("snd", s), ("rcv", r)):
        m = pd.Series(a)
        f[f"{role}_n_send"] = m.map(n_send).fillna(0).to_numpy()
        f[f"{role}_n_recv"] = m.map(n_recv).fillna(0).to_numpy()
        f[f"{role}_out_cp"] = m.map(out_cp).fillna(0).to_numpy()
        f[f"{role}_in_cp"] = m.map(in_cp).fillna(0).to_numpy()
        f[f"{role}_pass_through"] = (m.map(tot_send).fillna(0) / m.map(tot_recv).fillna(0).clip(lower=1)).clip(0, 5).to_numpy()
        f[f"{role}_novel_out"] = m.map(novel_out).fillna(0).to_numpy()
        f[f"{role}_novel_in"] = m.map(novel_in).fillna(0).to_numpy()
    f["usd_vs_sender_typical"] = np.log(usd / pd.Series(s).map(med_send).to_numpy())
    f["usd_vs_receiver_typical"] = np.log(usd / pd.Series(r).map(med_recv).to_numpy())

    # --- multi-scale burst windows ---------------------------------------------
    for w in WINDOWS:
        f[f"snd_sends_{w}"] = _count(sends, s, t, w, w, exclude_self=True)
        f[f"snd_recvs_before_{w}"] = _count(recvs, s, t, w, 0)
        f[f"rcv_recvs_{w}"] = _count(recvs, r, t, w, w, exclude_self=True)
        f[f"rcv_sends_after_{w}"] = _count(sends, r, t, 0, w)

    # --- nearest other activity of each party ------------------------------------
    events = _index_by(np.concatenate([s, r]), np.concatenate([t, t]), np.concatenate([usd, usd]))
    for role, acc in (("snd", s), ("rcv", r)):
        f[f"{role}_nearest_event_gap"] = np.log1p(_nearest_other(events, acc, t))

    # --- chaining: money in just before, money out just after -------------------
    gap, val = _nearest(sends, r, t, +1)
    f["rcv_next_send_gap"] = np.log1p(np.nan_to_num(gap, nan=7 * DAY))
    f["rcv_next_send_ratio"] = np.log(val / usd)
    gap, val = _nearest(recvs, s, t, -1)
    f["snd_prev_recv_gap"] = np.log1p(np.nan_to_num(gap, nan=7 * DAY))
    f["snd_prev_recv_ratio"] = np.log(cost / val)
    for w in (HOUR, 6 * HOUR, DAY):
        total, match = _flow(sends, r, t, usd, 0, w)
        f[f"rcv_forward_frac_{w}"] = np.clip(total / usd, 0, 10)
        f[f"rcv_forward_match_{w}"] = np.nan_to_num(match, nan=5)
        total, match = _flow(recvs, s, t, cost, -w, 0)
        f[f"snd_funded_frac_{w}"] = np.clip(total / cost, 0, 10)
        f[f"snd_funded_match_{w}"] = np.nan_to_num(match, nan=5)

    # --- episodes ---------------------------------------------------------------
    labels = {}
    parts = []
    for w in EPISODE_SCALES:
        labels[f"ep{w}"] = _episodes(s, r, t, w)
        parts.append(_episode_summary(df, labels[f"ep{w}"], f"ep{w}"))
    novel = df.pair_n.to_numpy() <= 1
    for w in NOVEL_EPISODE_SCALES:
        labels[f"nv{w}"] = _episodes(s, r, t, w, mask=novel)
        parts.append(_episode_summary(df, labels[f"nv{w}"], f"nv{w}"))

    feats = pd.concat([pd.DataFrame(f)] + parts, axis=1).astype(float)
    feats.insert(0, "TRANSACTION_HASH", df.TRANSACTION_HASH.to_numpy())
    labels["sender"], labels["receiver"], labels["t"] = s, r, t
    return feats, labels


def neighbour_features(scores, labels):
    """Second-stage features: how suspicious do this payment's episode-mates look?"""
    f = {}
    for name, lab in labels.items():
        if name in ("sender", "receiver", "t"):
            continue
        g = pd.Series(scores).groupby(lab)
        size = g.transform("size").to_numpy()
        total = g.transform("sum").to_numpy()
        others = np.maximum(size - 1, 1)
        f[f"nb_{name}_mean"] = np.where(size > 1, (total - scores) / others, 0)
        f[f"nb_{name}_max"] = np.where(size > 1, _max_excluding_self(scores, lab), 0)
    s, r, t = labels["sender"], labels["receiver"], labels["t"]
    for role, acc in (("snd", s), ("rcv", r)):
        for w in (HOUR, 6 * HOUR):
            f[f"nb_{role}_{w}_max"] = _window_max(acc, s, r, t, scores, w)
    return pd.DataFrame(f)


def _max_excluding_self(scores, lab):
    d = pd.DataFrame({"s": scores, "g": lab})
    top = d.groupby("g").s.transform("max").to_numpy()
    rank = d.groupby("g").s.rank(method="first", ascending=False)
    second = d.g.map(d[rank == 2].set_index("g").s).fillna(0).to_numpy()
    return np.where(rank.to_numpy() == 1, second, top)


def _window_max(acc, s, r, t, scores, w):
    """Max score of other payments touching `acc` (either side) within +-w seconds."""
    events = _index_by(np.concatenate([s, r]), np.concatenate([t, t]), np.concatenate([scores, scores]))
    out = np.zeros(len(t))
    for a in np.unique(acc):
        times, vals, pos = events[a]
        pos = pos % len(t)
        for k in np.flatnonzero(acc == a):
            lo, hi = np.searchsorted(times, t[k] - w, "left"), np.searchsorted(times, t[k] + w, "right")
            sel = pos[lo:hi] != k
            if sel.any():
                out[k] = vals[lo:hi][sel].max()
    return out
