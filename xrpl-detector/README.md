# XRPL Money Trail Detector — Decode & Detect

Scores every payment for laundering risk, groups suspicious payments into money
trails, ranks the trails, and writes a case report where every claim cites a
transaction hash.

```
data/train ──► train_model.py ──► models/model.joblib     (two-stage ranker, aml_ranker/)
data/test  ──► predict.py ──► trail_tracker.py ──► alert_ranker.py ──► case_writer.py
               predictions.csv    alerts.json         ranked_alerts.json   summaries.md
                                  trail_graph.py ──► graphs/A001.png
```

## Key finding (say this in the pitch)
Suspicious scenarios have the **same shapes** as benign ones (fan-out, chain,
cycle…), so shape alone can't separate them. What does separate them is **speed**:
suspicious money moves about 1 minute per hop vs about 10 minutes in benign lookalikes.
So the features measure velocity: how fast a receiver passes funds on, how
many linked payments happen in 3/10-minute bursts, how much of the amount is passed on.
A second signal is **new relationships**: legitimate commerce repeats the same
sender→receiver pairs, planted flows almost never do.

## Who owns what
| File | Owner |
|---|---|
| `aml_ranker/` (scoring model), `features.py`, `train_model.py`, `alert_ranker.py` | Person C (ranker) |
| `trail_tracker.py` | Person A (trail tracker) |
| `trail_graph.py` | Person B (trail tracker) |
| `case_writer.py` | Person D (case summaries) |
| `config.py`, `schemas.py`, `predict.py`, `run_pipeline.py` | shared — tell the team before changing |

## Team rules
1. Formats in `schemas.py` are the contract. Add fields freely; never rename/remove.
2. `python schemas.py` checks every output file.
3. After any change run `python run_pipeline.py data/train`. If it finishes, you broke nothing.

## Setup
```
python -m venv .venv
.venv\Scripts\activate            # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
```
Put the organisers' files in `data/train/` (transactions.parquet, transfers.parquet,
market_rates.csv, labels.csv) and `data/test/` (same files, no labels).

## Run
```
python train_model.py              # cross-validated scores + saves the model (~20 min)
python run_pipeline.py             # everything on data/test (+ submission_stage1/stage2/blend.csv)
python run_pipeline.py data/train  # everything on training data (demo/debug)
```

## How payments are scored (`aml_ranker/`)
- `data.py`: one row per payment (`ACCOUNT -> Destination`), valued in USD; the first
  transfer leg gives the actual source cost.
- `features.py`: ~220 features per payment from the split's own week: value and
  conversion legs, new vs recurring pair, each account's weekly profile, burst counts
  from 1 min to 2 days, money in just before / out just after, and **episodes** (groups
  formed by linking an account's consecutive payments within 30 s … 1 h, and for new
  relationships only within 30 min … 1 day).
- `model.py`: scikit-learn `HistGradientBoostingClassifier`s (3 seeds). Stage 2 adds
  how suspicious each payment's episode-mates look according to stage 1, so a planted
  pattern lifts all of its payments together.
  The uploaded score is the **blend**: the average rank of stage 1 and stage 2 (65.9 on
  the leaderboard, vs 65.6 for stage 1 and 65.4 for stage 2 alone).
  A small **medium specialist** (medium positives vs all negatives) can be mixed in at 5%:
  CV AP 57.4 vs 55.7 for the blend. It's written as `submission_specialist.csv`; switch
  the default with `DEFAULT_SCORE` in `config.py`.

The top-level `features.py` is still used by `predict.py` for the contract columns in
`predictions.csv` and for the alert reasons.

## Current score (5-fold CV, grouped by scenario and by relay cohort)
Site metric (100 × average precision) **55.4**: easy 68.8, medium 7.5, hard 1.5.
PR-AUC 0.55, ROC-AUC 0.94. Top 1%: precision 0.76, recall 0.24. At the F1-best threshold
(0.15): precision 0.71, recall 0.59, F1 0.64. The previous logistic/HGB model scores 49.1
under the same split.
Strong on cycle (85%), chain and fan-out-in (79%). Still weak on the two "relay" cohorts
(aggregate 4%, distributed 0% recall): each cohort hides 1 planted scenario among 99 that
match it on every feature tried so far. That's the biggest open problem.
