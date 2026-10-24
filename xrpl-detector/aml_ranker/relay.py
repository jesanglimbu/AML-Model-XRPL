"""Relay look-alike penalty: push down payments that look like the relay cohorts.

Each relay cohort hides about 1 planted scenario among 99 legitimate look-alikes, and the main
model scores many of those look-alikes highly (143 of the 400 top-scored legitimate training
payments). The planted relays themselves are almost never caught anyway, so pushing relay-shaped
payments down mostly removes false alarms.

A classifier is trained on the training labels' `family` (relay family or not, whether suspicious
or legitimate), which is allowed: it learns from train labels and only sees features at test time.
"""
import numpy as np

from aml_ranker.model import Ensemble

RELAY_FAMILIES = ("aggregate_relay", "distributed_relay")
# Out-of-fold CV on train: score x (1 - w * p_relay) gave AP 58.32 (w=0.5) and 58.42 (w=0.7)
# vs 57.75 for the mule score; a rank-based penalty hurt. Leaderboard: mule 66.8, w=0.7 66.9,
# w=0.5 67.0, so 0.5 is used.
RELAY_PENALTY = 0.5
RELAY_SEEDS = (0,)


def fit_relay(X, family):
    """Classifier for 'this payment belongs to a relay cohort' (planted or legitimate)."""
    return Ensemble(RELAY_SEEDS).fit(X, np.isin(family, RELAY_FAMILIES).astype(int))


def with_relay_penalty(scores, p_relay, penalty=RELAY_PENALTY):
    return np.asarray(scores) * (1 - penalty * np.asarray(p_relay))
