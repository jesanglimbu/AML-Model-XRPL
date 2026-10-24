"""Two-stage gradient-boosted alert ranker.

Stage 1 scores each payment from its own features. Stage 2 adds how suspicious the
payment's episode-mates and nearby account activity look according to stage 1, so a
planted pattern lifts all of its payments together. On training data the stage-1
scores fed to stage 2 are out-of-fold, matching what stage 2 sees at test time.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score
from sklearn.model_selection import StratifiedGroupKFold

from .features import neighbour_features

SEEDS = (0, 1, 2)
# Share of the medium specialist's rank in the final mix (CV: 5% gave AP 57.1 vs 55.6
# without it, with a flat plateau from 4% to 7.5%; 20% and above clearly hurt).
SPECIALIST_WEIGHT = 0.05


def _gbm(seed):
    return HistGradientBoostingClassifier(
        learning_rate=0.03, max_iter=600, max_leaf_nodes=63, min_samples_leaf=20,
        l2_regularization=1.0, max_features=0.3, early_stopping=False, random_state=seed,
    )


class Ensemble:
    """Average of seed-varied gradient-boosting models."""

    def __init__(self, seeds=SEEDS):
        self.seeds = seeds

    def fit(self, X, y):
        self.models = [_gbm(seed).fit(X, y) for seed in self.seeds]
        return self

    def predict(self, X):
        return np.mean([m.predict_proba(X)[:, 1] for m in self.models], axis=0)


def cv_groups(labels):
    """Hold out whole planted scenarios (and whole cohorts of look-alike scenarios)."""
    return labels.cohort_id.fillna(labels.scenario_id).fillna(labels.TRANSACTION_HASH).to_numpy()


def _stage2_inputs(X, stage1, ep_labels):
    nb = neighbour_features(stage1, ep_labels)
    nb.insert(0, "stage1", stage1)
    return pd.concat([X.reset_index(drop=True), nb], axis=1)


def _oof(X, y, folds, seeds):
    oof = np.zeros(len(y))
    for fit_idx, check_idx in folds:
        oof[check_idx] = Ensemble(seeds).fit(X.iloc[fit_idx], y[fit_idx]).predict(X.iloc[check_idx])
    return oof


def _folds(X, y, groups, n_splits):
    return list(StratifiedGroupKFold(n_splits, shuffle=True, random_state=0).split(X, y, groups))


def cross_validate(X, y, groups, ep_labels, n_splits=5, seeds=SEEDS):
    folds = _folds(X, y, groups, n_splits)
    stage1 = _oof(X, y, folds, seeds)
    X2 = _stage2_inputs(X, stage1, ep_labels)
    stage2 = _oof(X2, y, folds, seeds)
    return stage1, stage2


class AlertRanker:
    def __init__(self, seeds=SEEDS):
        self.seeds = seeds

    def fit(self, X, y, stage1_oof, ep_labels):
        """`stage1_oof` are out-of-fold stage-1 scores, as returned by cross_validate."""
        self.stage1 = Ensemble(self.seeds).fit(X, y)
        X2 = _stage2_inputs(X, stage1_oof, ep_labels)
        self.stage2 = Ensemble(self.seeds).fit(X2, y)
        self.columns = list(X.columns)
        return self

    def predict(self, X, ep_labels):
        return self.predict_stages(X, ep_labels)[1]

    def predict_stages(self, X, ep_labels):
        """(stage-1 scores, stage-2 scores) for the same payments."""
        X = X[self.columns]
        stage1 = self.stage1.predict(X)
        return stage1, self.stage2.predict(_stage2_inputs(X, stage1, ep_labels))


def blend(stage1, stage2):
    """Average of the two stages' rank percentiles, so neither stage's scale dominates.

    The average rank is then mapped onto stage 2's score distribution. That keeps the
    blend's ordering (all the site's metric looks at) while the values still read like
    probabilities, so the alert threshold and the case reports stay meaningful.
    """
    return _onto((_pct(stage1) + _pct(stage2)) / 2, stage2)


def _pct(scores):
    return pd.Series(scores).rank(pct=True).to_numpy()


def _onto(order, reference):
    """Give payments `reference`'s sorted values in the order of `order`, keeping its ties."""
    mapped = np.empty(len(order))
    mapped[np.argsort(order, kind="stable")] = np.sort(reference)
    # payments with the same order value share one value, so ties stay ties
    return pd.Series(mapped).groupby(order).transform("mean").to_numpy()


# --- medium specialist -------------------------------------------------------------
# A second model trained only on medium positives vs all negatives (easy and hard
# positives are left out), mixed into the blend at a small weight. In CV it ranks the
# medium cases worse than the main model; its gain comes from reordering easy cases.

def _specialist_rows(y, difficulty):
    medium = difficulty == "medium"
    return (y == 0) | medium, medium.astype(int)


def specialist_oof(X, y, difficulty, groups, n_splits=5, seeds=SEEDS):
    keep, target = _specialist_rows(y, difficulty)
    oof = np.zeros(len(y))
    for fit_idx, check_idx in _folds(X, y, groups, n_splits):
        fit_idx = fit_idx[keep[fit_idx]]
        oof[check_idx] = Ensemble(seeds).fit(X.iloc[fit_idx], target[fit_idx]).predict(X.iloc[check_idx])
    return oof


def fit_specialist(X, y, difficulty, seeds=SEEDS):
    keep, target = _specialist_rows(y, difficulty)
    return Ensemble(seeds).fit(X[keep], target[keep])


def with_specialist(blended, specialist, weight=SPECIALIST_WEIGHT):
    """Mix the specialist's rank into the blend, keeping the blend's score scale."""
    return _onto((1 - weight) * _pct(blended) + weight * _pct(specialist), blended)


def report(y, scores, difficulty):
    """Site metric (100 x AP) plus per-difficulty AP and top-1% precision/recall."""
    out = {"AP": 100 * average_precision_score(y, scores)}
    neg = y == 0
    for d in ("easy", "medium", "hard"):
        keep = neg | (difficulty == d)
        out[f"AP_{d}"] = 100 * average_precision_score(y[keep], scores[keep])
    k = max(1, int(round(0.01 * len(y))))
    top = np.argsort(-scores, kind="stable")[:k]
    out["P@1%"] = 100 * y[top].mean()
    out["R@1%"] = 100 * y[top].sum() / y.sum()
    return pd.Series(out).round(1)
