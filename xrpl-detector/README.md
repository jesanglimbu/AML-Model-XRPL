# XRPL Money Trail Detector — Decode & Detect

Scores every payment for laundering risk, groups suspicious payments into money
trails, ranks the trails, and writes a case report where every claim cites a
transaction hash.

```
data/train ──► train_model.py ──► models/model.joblib
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

## Who owns what
| File | Owner |
|---|---|
| `features.py`, `train_model.py`, `alert_ranker.py` | Person C (ranker) |
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
python train_model.py              # cross-validated scores + saves the model
python run_pipeline.py             # everything on data/test
python run_pipeline.py data/train  # everything on training data (demo/debug)
```

## Current score (5-fold CV, grouped by scenario)
PR-AUC 0.52, ROC-AUC 0.90, F1 0.57 (precision 0.62, recall 0.53).
Strong on chain (82%), cycle (74%), fan-out-in (72%). Weak on the two "relay" cohorts
(~0% recall): their suspicious 1% look statistically identical to the benign 99% on
every feature tried so far. That's the biggest open problem.
