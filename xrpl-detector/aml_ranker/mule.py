"""Mule network signal: suspicion spreads through the accounts that move the money.

A mule receives suspicious money and passes it on, so payments touching the same accounts
around the same time as a highly scored payment are more likely to belong to the same scheme.
Uses only the payment network and the blend's scores (no labels), so it adds no training time.
"""
from collections import defaultdict

import numpy as np

from aml_ranker.model import _onto, _pct

# Chosen with out-of-fold CV on train: +-1 h at 20% gave AP 57.75 vs 56.86 for the blend
# (10%: 57.52, 30%: 57.78; +-10 min and +-6 h windows gained 0.3 or less).
MULE_WINDOW = 3600       # seconds either side of a payment
MULE_WEIGHT = 0.2        # share of the mule signal's rank in the mix


def _account_events(senders, receivers, times):
    events = defaultdict(list)
    for i, (s, r, t) in enumerate(zip(senders, receivers, times)):
        events[s].append((t, i))
        events[r].append((t, i))
    return {a: (np.array([t for t, _ in ev]), np.array([i for _, i in ev])) for a, ev in events.items()}


def neighbour_max(scores, senders, receivers, times, window=MULE_WINDOW):
    """Highest score among OTHER payments touching the sender or receiver within +-window."""
    order = np.argsort(times, kind="stable")
    events = _account_events(np.asarray(senders)[order], np.asarray(receivers)[order], np.asarray(times)[order])
    sorted_scores = np.asarray(scores)[order]
    out = np.zeros(len(order))
    for j, (s, r, t) in enumerate(zip(np.asarray(senders)[order], np.asarray(receivers)[order],
                                      np.asarray(times)[order])):
        best = 0.0
        for a in (s, r):
            ts, idx = events[a]
            near = idx[np.searchsorted(ts, t - window):np.searchsorted(ts, t + window, "right")]
            near = near[near != j]
            if len(near):
                best = max(best, sorted_scores[near].max())
        out[j] = best
    result = np.empty(len(order))
    result[order] = out
    return result


def with_mule(blended, mule_signal, weight=MULE_WEIGHT):
    """Mix the mule signal's rank into the blend, keeping the blend's score scale."""
    return _onto((1 - weight) * _pct(blended) + weight * _pct(mule_signal), blended)
