# Team notes

Handover for the Decode & Detect hackathon. Deadline: **16:00**. Stop adding features at **15:00**.

## What the task actually is

- The data is a **synthetic** week of payments on a fake XRPL-style ledger. Nothing is live, so we don't need `xrpl-py` or the Testnet.
- We must give **every one of the 40,101 test transactions a score from 0 to 1** (higher = more suspicious).
- Upload two files at https://hackathon.ukcbt.org: `predictions.csv` (`TRANSACTION_HASH,score`, optional `reason` column) and a ZIP of our code.
- **Score = 100 × average precision.** It rewards ranking the suspicious payments at the top. Random guessing gets about 3.
- **50 uploads per day for the whole team.** Only our best run counts on the leaderboard.

## What's in the training data

`train/labels.csv`: 40,131 payments, **1,250 suspicious (about 3%)**. Each is tagged with a pattern family:

| Family | Suspicious | Difficulty |
|---|---|---|
| fan_out_in, fan_in, fan_out | 371 | mostly easy |
| multi_stage, chain, stack | 362 | easy–medium |
| bipartite, cycle, random | 292 | mostly easy |
| aggregate_relay, distributed_relay | 200 | **all hard** |
| ambiguous | 25 | hard, deliberately unpredictable |

- The legitimate data contains **look-alikes from the same families** (for example 152 legitimate fan_out_in payments), so simple "is it a fan-out?" rules give false alarms.
- The hard relay cases play out over **hours or days**, longer than the starter notebook's one-hour windows. That's where the most points are.
- `family`, `difficulty`, `scenario_id` and `cohort_id` are **not available in the test data**. Use them to understand the data and check results, not as model inputs.

## Who's doing what

| Team | Part |
|---|---|
| Team 1 | Money trail tracker |
| Team 2 | Alert ranker (the scores we upload) |
| Owen | Case summary writer |

## Setup (each laptop)

Download and unzip both packages from the hackathon site into the same folder, then:

```sh
python3 -m venv ~/dnd-env
~/dnd-env/bin/pip install pandas pyarrow scikit-learn jupyter
cd path/to/decode-and-detect-training-data
ln -s ../decode-and-detect-test-data test-data   # the notebook looks for test-data/
```

Run `source ~/dnd-env/bin/activate` in every new terminal before using `python` or `jupyter`.

The starter notebook (`starter_notebook.ipynb` in the training download) runs in under a minute and writes `predictions.csv`.

## Baseline

- Starter notebook, unchanged: **24.6** on held-back training data.
- **Uploaded to the site: score 33.5, precision 62%, recall 20%** (precision and recall are for the top 1% of scores, about 400 transactions).
- So of our ~400 highest scores, about 250 are really suspicious, which is about 20% of the ~1,250 suspicious payments. The other 80% are ranked lower down.
- Team 2's target is to beat it. Ideas from the README: longer time windows, `HistGradientBoostingClassifier` instead of logistic regression, money that returns to where it started.

## What's in this repo

| File | What it is |
|---|---|
| `payments.py` | The organisers' loader: one row per payment, valued in USD. **Not written by us.** |
| `case_summary.py` | Case summary writer: turns flagged payments into readable reports |
| `alert_tracker.py` | Alert tracker: the analyst's review queue, with decisions logged |
| `.gitignore` | Keeps data, `dnd-env/` and `.env` (API keys) out of git |

Never commit the data files or API keys. The rules forbid them in the ZIP, and the parquet files are too big for GitHub.

## Using `case_summary.py`

```sh
python case_summary.py --data ../decode-and-detect-test-data --predictions predictions.csv --top 5
```

- `--out reports.md` saves the reports to a file
- `--tx <hash>` summarises one specific payment
- `--reasons-csv out.csv` writes the predictions with a `reason` column (for example `relay; fan-out`)

For each case it lists red flags (relay, pass-on, fan-out, fan-in, cycle, pass-through account, unusually large), describes both accounts' week, and shows where the money went next.

### Where it connects to your parts

- **Team 1:** `follow_money()` in `case_summary.py` is a simple placeholder. Replace it with your trail tracker. It receives `(df, start_account, start_time, start_amount)` and should return a list of steps with `hop`, `from`, `to`, `usd`, `minutes_later`.
- **Team 2:** the case summary picks its cases from your `predictions.csv`. Share each new version so the reports use your latest scores.

Note: with only 700 accounts making 40,000 payments, almost every account is busy, so the red flags fire often. They explain a case; the score from team 2 decides what's suspicious.

## Using `alert_tracker.py`

A review queue for analysts. It groups the top 1% of scores into alerts (flagged payments that share an account within 6 hours), ranks them, says why each is there, and records decisions.

```sh
python alert_tracker.py refresh --data decode-and-detect-test-data --predictions predictions.csv
python alert_tracker.py queue                    # what to look at next
python alert_tracker.py show AL-1a2b3c4d         # payments, reasons, hashes, last decision
python alert_tracker.py escalate AL-1a2b3c4d --by Owen --note "relay, 4 hops in 9 min"
python alert_tracker.py close AL-1a2b3c4d --by Owen --note "payroll look-alike"
python alert_tracker.py handover --out handover.md
```

- Only `refresh` reads the data. Everything else is instant and works offline.
- Decisions are appended to `alert_tracker_data/decisions.csv` and never rewritten. Closing or escalating needs a `--note`.
- Re-running `refresh` with new scores keeps every decision. Alerts are matched by their payments, so an alert that gets regrouped keeps its status, and a closed or escalated alert that gains new flagged payments comes back as **reopened**.
- Checked on the training labels with the default 6-hour window: 97% of the payments in an alert belong to the same laundering scenario. A 24-hour window drops this to 86%.

## Final submission checklist

The code ZIP must include:

- [ ] All source code
- [ ] README with the **exact command** that produces `predictions.csv`, plus language version and run time
- [ ] Dependency list (`requirements.txt`)
- [ ] `LICENSE` (MIT)
- [ ] List of what we didn't write: `payments.py`, the starter notebook if used, libraries, and AI assistance (Claude)
- [ ] **No** data files, `dnd-env/`, or API keys

Limits: 8 MiB compressed, 2,000 files. The organisers may re-run our code, so check the command works from a fresh folder.
