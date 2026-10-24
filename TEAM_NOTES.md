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

## Leaderboard runs

| Run | Score | Top-1% precision | Top-1% recall |
|---|---|---|---|
| Starter notebook (baseline) | 33.5 | 62% | 20% |
| `xrpl-detector`, single model (commit `4a66fec`) | 59.2 | 94% | 30% |
| `xrpl-detector`, two-stage ranker `aml_ranker/` (commit `b176cf4`) | 65.4 | 91% | 29% |
| `xrpl-detector`, stage-1 model alone (`submission_stage1.csv`) | 65.6 | 92% | not recorded |
| `xrpl-detector`, blend of stage 1 and stage 2 (`submission_blend.csv`) | 65.9 | 91% | not recorded |
| `xrpl-detector`, blend + 5% medium specialist (`submission_specialist.csv`) | 65.9 | not recorded | not recorded |
| `xrpl-detector`, blend on Owen's Mac (Python 3.9.6, scikit-learn 1.6.1) | 66.5 | not recorded | not recorded |
| **`xrpl-detector`, blend + mule network signal (`submission_mule.csv`, now the default), Owen's Mac** | **66.8** | 92% | 30% |

- What the 65.4 run caught, from the site's breakdown: easy **40%** of 800, medium **10%** of 225, observable hard **0%** of 200, ambiguous **0%** of 25. That adds up to about 342 payments, a little under the ~363 implied by 29% recall, so check which cut-off the breakdown uses before comparing runs on it.
- **Best run: 66.8** (blend + mule network signal, `submission_mule.csv`, now the default; made on Owen's Mac, Python 3.9). Same Mac's blend scored **66.5**, so the mule signal adds **+0.3**; the other +0.6 over 65.9 comes from library versions (Python 3.9.6 / scikit-learn 1.6.1 beat 3.14 / 1.9.1 here). **So the final upload should be made with the Mac's versions**, and the README must document them.
- Previous best: 65.9 (the blend). Reproduce with `python xrpl-detector/train_model.py` (about 20 min) then `python xrpl-detector/run_pipeline.py`, and upload `outputs/submission.csv`.
- The two-stage ranker ranks the whole list better (score up 6.2), while its top 1% is slightly less clean (91% vs 94%). The top 1% can hold at most ~32% of the ~1,250 suspicious payments, so 29% recall is close to the ceiling.
- **Scoring variants:** `run_pipeline.py` on the test data also writes `outputs/submission_stage1.csv` (stage-1 model alone, 65.6), `submission_stage2.csv` (two-stage ranker alone, 65.4) and `submission_blend.csv` (average rank of the two, 65.9). The blend was the default `probability` until the mule signal beat it, so `submission.csv`, the alerts and the case reports all use it; its values are mapped onto stage 2's score distribution, so they still read like probabilities and rank exactly like the 65.9 upload. In CV stage 2 helped medium and hard but hurt easy (easy AP 72.3 → 68.8), which is why mixing in stage 1 helps.
- Next gains: the medium cases and the relay families (aggregate_relay, distributed_relay), still about 0% recall in cross-validation.

## Medium-case experiments (Owen's request, 13:00)

Rule: keep an experiment only if its CV AP beats the current default (the blend) under the same CV. CV and leaderboard are different scales (the 65.4 run is 55.4 in CV), so "beats 65.4" means "beats the blend's CV". Screening runs used 1 seed; two seeds of the baseline differed by about 0.1, so gaps bigger than that are real.

| Experiment (1 seed) | CV AP | medium AP | Kept? |
|---|---|---|---|
| Baseline: the blend | 55.6 | 7.5 | – |
| A: medium positives weighted ×3, ambiguous ×0 | 55.3 | 7.4 | no |
| B: slow "flow" episodes (forwarding / fan-out / fan-in between new pairs, 30 min–6 h) | 55.0 | 7.5 | no |
| C: A + B | 55.1 | 7.5 | no |
| **D: medium specialist mixed into the blend at 5%** | **57.1** | 6.6 | **yes, as an upload candidate** |

- **D, retrained with 3 seeds: CV AP 57.4 vs 55.7 for the blend (+1.7).** Easy 71.1 → 73.7, medium 7.6 → 6.7, hard unchanged.
- D is a second model trained only on medium positives vs all negatives, mixed in by rank. The mix weight has a flat plateau from 4% to 7.5% (all about 57); 20% and above clearly hurt.
- Honest caveat: **none of these improved the medium cases.** The specialist ranks medium cases worse than the main model; its gain comes from reordering the easy cases. The medium cases are slow and look like the legitimate decoys, and with only 27 medium scenarios in training no feature or weighting found so far separates them.
- `run_pipeline.py` writes D as `outputs/submission_specialist.csv`. **On the leaderboard it tied the blend at 65.9**, so its CV gain didn't carry over to the test week and the blend stayed the default (now replaced by the mule signal). To switch anyway, set `DEFAULT_SCORE = "specialist"` in `xrpl-detector/config.py` and rerun `run_pipeline.py` (no retraining needed).

## The two-stage ranker (`xrpl-detector/aml_ranker/`)

Replaces the pipeline's scoring model. Nothing downstream changes: `predict.py` still writes the same `predictions.csv` columns, so trails, alert ranking, graphs and case summaries work as before.

- **Same cross-validation for both** (5 folds, grouped by scenario and by relay cohort): previous model **AP 49.1**, two-stage ranker **AP 55.4**. On the leaderboard: 59.2 → 65.4.
- Per difficulty (cross-validation): easy 68.8, medium 7.5, hard 1.5. Relay recall is still about 0% (aggregate_relay 4%, distributed_relay 0%).
- What we learned: the easy cases are fast bursts (about 5 min per scenario vs about 60 min for the legitimate look-alikes), and suspicious payments almost always use a sender→receiver pair that hasn't paid before. The medium cases are slow and look like the legitimate decoys. Each relay cohort hides 1 planted scenario among 99 matching legitimate ones, and nothing tried so far separates them (including linking accounts to other suspicious activity), so hard recall is still near 0.

## What's in this repo

| File | What it is |
|---|---|
| `xrpl-detector/` | The pipeline: scoring (`aml_ranker/`), trails, alert ranking, graphs, case reports. See its README |
| `LICENSE`, `THIRD_PARTY.md` | MIT licence and the list of what we didn't write (for the ZIP) |
| `.gitignore` | Keeps data, `dnd-env/` and `.env` (API keys) out of git |

Never commit the data files or API keys. The rules forbid them in the ZIP, and the parquet files are too big for GitHub.

**Heads-up:** the `decode-and-detect-*` data folders are currently tracked in git (they were added before the `.gitignore`). Leave them out of the ZIP, and agree as a team before removing them from the repo.

**Repo plan (agreed):** keep working in this repo for now. At **15:00** we copy the code into a **new repo without the data folders or old history**, and that new repo is the public one we submit. Before switching, copy your local `decode-and-detect-*` folders somewhere safe, because they won't be in the new repo.

## Case reports (`xrpl-detector/case_writer.py`, Owen)

`run_pipeline.py` writes `outputs/summaries.md` for the top 5 alerts (template-based, no LLM). Each report has:

- the **pattern** (fan-out, fan-in, chain, split and recombine, layering, cycle, many-to-many) with a one-line meaning
- **who's who**: sources → intermediaries → collectors
- **why it was flagged**: alert size and duration, how fast intermediaries passed money on, the model's scores, and the ranker's reasons without repeats
- the **trail graph** (`outputs/graphs/<alert>.png`) and every payment with its hash

The top of the file has a "a flag is not proof" note and a glossary. Open `outputs/summaries.md` in VS Code's Markdown preview to see the graphs inline.

## Alerts: one system

The team agreed to use only the `xrpl-detector/` pipeline for alerts: `trail_tracker.py` groups flagged payments, `alert_ranker.py` ranks them, `case_writer.py` explains them. The separate `alert_tracker.py` was removed (it is still in the git history, commit `b96cf6d`, if we need anything from it).

## Final submission checklist

The code ZIP must include:

- [ ] All source code
- [x] README with the **exact command** that produces `predictions.csv`, plus language version and run time (top-level `README.md`)
- [x] Dependency list (`xrpl-detector/requirements.txt`)
- [x] `LICENSE` (MIT)
- [x] List of what we didn't write: `THIRD_PARTY.md` (`payments.py`, the starter notebook, libraries, and AI assistance)
- [ ] **No** data files, `dnd-env/`, or API keys

Limits: 8 MiB compressed, 2,000 files. The organisers may re-run our code, so check the command works from a fresh folder.
