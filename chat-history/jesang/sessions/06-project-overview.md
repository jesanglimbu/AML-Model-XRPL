# Project overview

_Desktop app · 2026-10-24 11:32 → 2026-10-24 11:33 UTC_


## 🧑 User

Give a brief overview of this project.

<details><summary>Tool calls (2)</summary>

- `Bash` — List project files, README, and recent history
- `Bash` — Read detector README, team notes, and uncommitted changes

</details>

## 🤖 Claude

This is your team's entry for the **Decode & Detect** hackathon. The task is to spot money laundering on a synthetic, XRPL-style payment ledger.

**What it does:** It gives each of the 40,101 test payments a suspicion score from 0 to 1 and writes them to `outputs/submission.csv`. The leaderboard score is 100 × average precision. Only about 3% of the training payments are labelled suspicious.

**The main insight** (from [xrpl-detector/README.md](xrpl-detector/README.md)): suspicious flows have the same shapes as legitimate look-alikes (fan-out, chain, cycle and so on), so shape alone doesn't separate them. Two things do:
- **Speed:** suspicious money moves about 1 minute per hop, against about 10 minutes for benign flows.
- **New relationships:** legitimate commerce keeps reusing the same sender→receiver pairs, and planted flows almost never do.

**Pipeline** (in [xrpl-detector/](xrpl-detector/)):
- [train_model.py](xrpl-detector/train_model.py) trains a two-stage ranker ([aml_ranker/](xrpl-detector/aml_ranker/)) on about 220 features per payment: burst counts, money passed on, new vs. recurring pairs, and "episodes" of linked payments. It saves the model to `models/model.joblib` and takes about 15–20 minutes.
- [run_pipeline.py](xrpl-detector/run_pipeline.py) runs the stages in order:
  1. [predict.py](xrpl-detector/predict.py) scores the payments.
  2. [trail_tracker.py](xrpl-detector/trail_tracker.py) groups flagged payments into money trails.
  3. [alert_ranker.py](xrpl-detector/alert_ranker.py) flags the top 1% and groups them into 10-minute bursts.
  4. [trail_graph.py](xrpl-detector/trail_graph.py) draws a graph of each trail.
  5. [case_writer.py](xrpl-detector/case_writer.py) writes case reports where every claim cites a transaction hash.
- [schemas.py](xrpl-detector/schemas.py) defines the output formats the team shares, and running it checks every output file.

**Progress:** The commit history shows the leaderboard score going from 59.2 to 65.4 after the two-stage ranker went in. [TEAM_NOTES.md](TEAM_NOTES.md) is the handover doc, with the data breakdown and who owns what. The hard cases with the most points still to win are the aggregate/distributed relays, which play out over hours or days.

**Current state:** You're on branch `submission-variants`. Four files have uncommitted edits (`model.py`, `config.py`, `predict.py`, `run_pipeline.py`), and `models/` is untracked: it holds the trained model and `cv_metrics.json`.

## 🧑 User

Are there any GUI components?
How can we make this product user-friendly so analysts can review our flagged suspicious activities?

<details><summary>Tool calls (2)</summary>

- `Bash` — Search for UI frameworks, outputs, and the removed alert tracker
- `wrap_up`

</details>

## 🤖 Claude

**No, there's no GUI.** The requirements have no web or UI framework (no Streamlit, Flask, Dash or Tkinter), and the pipeline only writes files to `outputs/`:
- `ranked_alerts.json`: the ranked alerts
- `summaries.json`: the case reports, where every claim cites a transaction hash
- `graphs/*.png`: one trail diagram per alert, made with matplotlib
- `predictions.csv` and `submission*.csv`: the raw scores

To review a case today, an analyst would have to open the JSON, find the matching PNG and look up hashes by hand.

There was briefly something close: commit `b96cf6d` added `alert_tracker.py`, a command-line review queue that kept an append-only log of close/escalate/review decisions. It was removed in `003b4e2` because the team wanted a single alert system. Its decision-log idea is still worth bringing back on top of the current pipeline.

### My suggestion: a review page built by the pipeline itself
Add a last step to `run_pipeline.py` that writes one self-contained `outputs/review.html` from the files the pipeline already produces:

1. **Alert queue:** a sortable, filterable table showing rank, risk score, number of payments, total USD, time span and accounts involved.
2. **Case view:** click an alert to see its plain-English summary, the trail graph and the list of its payments. Each hash links to its row.
3. **Why it was flagged:** show the evidence the model relies on, in plain words. For example, "funds passed on 48 s after arrival" or "first-ever payment between these accounts." Analysts trust a score more when they can see the speed and new-relationship signals behind it.
4. **Decisions:** Escalate, Close or Needs review buttons with a notes box, plus an export to CSV. This brings back the old tracker's decision log.
5. **Search:** look up by account or transaction hash to see every alert it appears in.

**Why a static page rather than Streamlit or a web app:**
- It needs no new dependencies or server and works offline.
- It sits in the code ZIP the team uploads, so judges can open it with a double-click.
- It always matches the same run as the scores, which was the reason for dropping the old tracker.

**What a static page can't do:** store decisions centrally across several analysts. That needs a small backend, or Streamlit with a shared CSV. It's a good point for the pitch, but too much to build before the deadline.

**Timing:** [TEAM_NOTES.md](TEAM_NOTES.md) sets a 15:00 feature freeze. The page is a few hours of work and doesn't touch scoring, so it can't lower the leaderboard number. `run_pipeline.py` is a shared file, though, so tell the team before changing it.

