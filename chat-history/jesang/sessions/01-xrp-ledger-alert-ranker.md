# XRP Ledger alert ranker

_Desktop app · 2026-10-24 10:07 → 2026-10-24 11:23 UTC_


## 🧑 User

Using the training and testing data, create a XRP Ledger alert ranker in Python

<details><summary>Tool calls (5)</summary>

- `update_plan`
- `Bash` — List project and data directories
- `Bash` — Read README and helper script
- `Bash` — Read truncated README section and payments.py
- `Bash` — Read starter notebook and check Python libs

</details>

## 🤖 Claude

I'll set up a project venv in the repo and install the needed libraries.

<details><summary>Tool calls (1)</summary>

- `Bash` — Create venv and install data/ML libraries

</details>

## 🤖 Claude

LightGBM needs a system OpenMP library; I'll use scikit-learn's HistGradientBoosting instead (no system deps, easier to reproduce).

<details><summary>Tool calls (1)</summary>

- `Bash` — Inspect schema of train tables and labels

</details>

## 🤖 Claude

Now let me explore the labels and what suspicious patterns look like.

<details><summary>Tool calls (6)</summary>

- `Bash` — Explore label distribution and example scenarios
- `Bash` — Rerun EDA showing scenarios
- `Bash` — Rerun EDA showing scenarios
- `Bash` — Investigate hard relay scenarios
- `Bash` — Rank suspicious scenario among cohort peers
- `Bash` — Check suspicious-neighbor linkage of hard scenarios

</details>

## 🤖 Claude

Only 700 accounts exist and every one is busy, so guilt-by-association is noise. Let me look at flow dynamics inside each relay scenario (hub pass-through, delays, amount matching).

<details><summary>Tool calls (1)</summary>

- `Bash` — Compare hub flow dynamics within relay cohorts

</details>

## 🤖 Claude

Delay-to-forward is mildly lower for hard positives but noisy. Since 82% of positives are easy/medium, let me check what separates those from their decoys — I suspect speed.

<details><summary>Tool calls (8)</summary>

- `Bash` — Compare timing of easy/medium vs decoy scenarios
- `update_plan`
- `Write` — ~/AML-Model-XRPL/aml_ranker/data.py
- `Write` — ~/AML-Model-XRPL/aml_ranker/features.py
- `Edit` — ~/AML-Model-XRPL/aml_ranker/features.py
- `Write` — ~/AML-Model-XRPL/aml_ranker/model.py
- `Write` — ~/AML-Model-XRPL/run.py
- `Bash` — Run grouped cross-validation on training data

</details>

## 🤖 Claude

Baseline grouped-CV: **AP 53.6** (easy 70.6, medium 4.8, hard ~1). Let me see where it's going wrong — which negatives outrank positives, and what medium scenarios look like.

<details><summary>Tool calls (1)</summary>

- `Bash` — Analyse ranking errors by family

</details>

## 🤖 Claude

Most false positives are the legit "decoy" scenarios of the same pattern families. Let me find which features separate positives from their own-family decoys, for easy and medium separately.

<details><summary>Tool calls (1)</summary>

- `Bash` — Univariate AUC of features vs family decoys

</details>

## 🤖 Claude

Medium cases are essentially per-transaction indistinguishable from decoys. Let me test at the scenario level (aggregating each scenario's features) to see if anything separates medium from decoys.

<details><summary>Tool calls (1)</summary>

- `Bash` — Scenario-level AUC medium/easy vs decoys

</details>

## 🤖 Claude

Easy scenarios separate at AUC 0.93 when aggregated per scenario, but per-transaction ranking loses some of that. Let me inspect low-ranked easy positives and high-ranked decoys.

<details><summary>Tool calls (3)</summary>

- `Bash` — Inspect worst easy scenarios and top decoys
- `Bash` — Check per-account suspicious concentration
- `Bash` — Test account-level guilt excluding own scenario

</details>

## 🤖 Claude

Account-level guilt is weak (AUC ≤0.59). One last check: among *fast* scenarios only, does anything separate suspicious from decoy? If not, the decoys set a ceiling and I'll stop chasing it.

<details><summary>Tool calls (1)</summary>

- `Bash` — Scenario AUC among fast scenarios only

</details>

## 🤖 Claude

Speed is a continuous signal even among fast scenarios. I'll add finer episode scales (30 s – 5 min), episode median gap, and nearest-event gaps for sender/receiver.

<details><summary>Tool calls (1)</summary>

- `Bash` — Add finer speed features and rerun CV

</details>

## 🤖 Claude

Small gain (55.5). Let me cache features and try a few model settings quickly with one seed.

<details><summary>Tool calls (1)</summary>

- `Bash` — Compare gradient-boosting hyperparameters

</details>

## 🤖 Claude

Hyperparameters barely matter, so features are the bottleneck. Let me check the remaining raw fields (LastLedgerSequence offset, account Sequence continuity) for any signal before settling.

<details><summary>Tool calls (1)</summary>

- `Bash` — Check raw ledger fields for label signal

</details>

## 🤖 Claude

No leakage in raw fields — the dataset is clean, so gains must come from modelling scenario structure. I'll adopt the stronger "big" config and feed the stage-1 score itself into stage 2.

<details><summary>Tool calls (1)</summary>

- `Bash` — Tune model and stage-2 inputs, rerun CV

</details>

## 🤖 Claude

While CV runs, I'll write the packaging files the hackathon requires (README with exact command, requirements, licence, attributions).

<details><summary>Tool calls (3)</summary>

- `Bash` — Get library versions and hardware
- `Bash` — Write requirements, gitignore, licence, attributions
- `Bash` — Check CV progress output

</details>

## 🤖 Claude

Still running; I'll wait for it to finish.

<details><summary>Tool calls (1)</summary>

- `ToolSearch` — select:Monitor

</details>

## 🤖 Claude

The CV job will notify me when it finishes. Meanwhile, I'll write the README.

<details><summary>Tool calls (2)</summary>

- `Write` — ~/AML-Model-XRPL/README.md
- `Bash` — Wait for CV run to finish

</details>

## 🤖 Claude

Final CV: **AP 55.4** (stage 2 adds a little on medium/hard). Now I'll generate the test predictions.

<details><summary>Tool calls (2)</summary>

- `update_plan`
- `Bash` — Train on all data and score test split

</details>

## 🤖 Claude

Prediction is running in the background; I'll check the output once it completes.

<details><summary>Tool calls (1)</summary>

- `Bash` — Wait for prediction run to finish

</details>

## 🤖 Claude

The prediction run is still going. I'll wait for it to finish.

<details><summary>Tool calls (1)</summary>

- `Bash` — Wait again for prediction run

</details>

## 🤖 Claude

Validating the CSV against the submission rules:

<details><summary>Tool calls (3)</summary>

- `Bash` — Validate predictions file format
- `Bash` — Inspect pre-existing tracked files
- `Bash` — Restore team gitignore and view repo layout

</details>

## 🤖 Claude

Your team has an existing `xrpl-detector/alert_ranker.py` and recorded a baseline leaderboard score. Let me see how mine compares, and fix the README title so it keeps the original header.

<details><summary>Tool calls (4)</summary>

- `Bash` — Find recorded baseline score
- `Bash` — Read team detector's CV score
- `Edit` — ~/AML-Model-XRPL/README.md
- `wrap_up`

</details>

## 🤖 Claude

I've built the XRPL alert ranker, trained it on `train/`, and scored the test data. [predictions.csv](predictions.csv) has one score per test payment (40,101 IDs, matching the test set exactly, all between 0 and 1), ready to upload.

**Results** (5-fold cross-validation on `train/`, holding out whole scenarios and whole hard cohorts, so it's a strict check):

| Metric | Score |
|---|---|
| **Site score (100 × AP)** | **55.4** |
| AP, easy cases | 68.8 |
| AP, medium cases | 7.5 |
| AP, hard cases | 1.5 |
| Precision / recall in top 1% | 75.8% / 24.3% |

Your team's last upload in `TEAM_NOTES.md` scored 33.5. The site's score on the test data may come out lower than 55.4, because the README says the test set has batch variations that aren't in training.

**What I found in the data:**
- **Speed:** easy suspicious scenarios finish in about 5 minutes. Legitimate ones with the same shape take about an hour.
- **New relationships:** suspicious payments almost always go between a sender and receiver who haven't paid each other before. Legitimate relationships repeat.
- **Look-alikes:** every pattern family includes legitimate scenarios with the same shape, and these cause most false alarms. Medium cases are slow and hard to tell apart from them.
- **Hard relay cases:** each of the 12 hard groups hides one suspicious scenario among 99 matching legitimate ones. Nothing I tried separates them, including linking accounts to other suspicious activity; with only 700 accounts, every account is busy.

**How it works:**
- [data.py](aml_ranker/data.py) turns each payment into one sender→receiver edge, valued in USD.
- [features.py](aml_ranker/features.py) builds about 220 features per payment: activity bursts over windows from 1 minute to 2 days, money passed on in matching amounts, and groups of linked payments at several time scales.
- [model.py](aml_ranker/model.py) uses scikit-learn gradient boosting in two stages. The second stage adds how suspicious each payment's linked payments look, which lifts a whole pattern together.

**To run:** one command, about 16 minutes on your M4:
```bash
.venv/bin/python run.py predict --train-dir ~/Downloads/decode-and-detect-training-data/train --test-dir ~/Downloads/decode-and-detect-test-data --out predictions.csv
```
`run.py cv` gives the cross-validation report. I added the files the code ZIP needs: [README.md](README.md) with the exact command, `requirements.txt`, an MIT `LICENSE` in your name, and [THIRD_PARTY.md](THIRD_PARTY.md), which lists the libraries and AI help.

**Repo changes:** your team pushed commits while I was working.
- My new `.gitignore` overwrote the team's. I've put theirs back and added my entries at the end.
- I replaced the two-line stub `README.md` with the full one.
- I didn't touch `xrpl-detector/`, or `TEAM_NOTES.md` and `alert_tracker.py` (someone else's uncommitted work).
- I used scikit-learn instead of LightGBM, which needs a system library that isn't installed, so the code runs on a plain `pip install`.

## 🧑 User

Before committing/pushing, make sure you have the updated branch in the repository.
Read TEAM_NOTES.md and any other files that may give an update on the current development workflow and progress. Update and edit them accordingly.

I made an alert_tracker, but I meant to make an alert_ranker in one of the repo branches. Could you remove the tracker without breaking the repo and add the ranker?

<details><summary>Tool calls (5)</summary>

- `update_plan`
- `Bash` — Fetch remote and list branches
- `Bash` — Inspect new upstream commits
- `Bash` — Compare local tracker files with history
- `Bash` — Back up, stash ranker work, fast-forward main

</details>

## 🤖 Claude

Main is now up to date with `origin/main`. Next I'll check for leftover tracker references and read the team docs and the `xrpl-detector` pipeline in full.

<details><summary>Tool calls (6)</summary>

- `update_plan`
- `Bash` — Find tracker references and read team docs
- `Bash` — Read xrpl-detector pipeline files
- `Bash` — Evaluate team model under the same CV
- `update_plan`
- `Bash` — Create branch, restore stash, move package

</details>

## 🤖 Claude

Now I'll refactor `AlertRanker.fit` to reuse the stage-1 out-of-fold scores from the CV run, so training doesn't repeat the expensive step.

<details><summary>Tool calls (2)</summary>

- `Edit` — ~/AML-Model-XRPL/xrpl-detector/aml_ranker/model.py
- `Read` — ~/AML-Model-XRPL/xrpl-detector/features.py

</details>

## 🤖 Claude

Now rewriting `train_model.py` to train the two-stage ranker. It keeps the same outputs (`models/model.joblib` with `model`/`threshold`/`features`, plus `cv_metrics.json`) and the same printouts.

<details><summary>Tool calls (2)</summary>

- `Write` — ~/AML-Model-XRPL/xrpl-detector/train_model.py
- `Edit` — ~/AML-Model-XRPL/xrpl-detector/predict.py

</details>

## 🤖 Claude

Kicking off training in the background (~17 min) while I update the docs.

<details><summary>Tool calls (2)</summary>

- `Bash` — Train the ranker via the pipeline
- `update_plan`

</details>

## 🤖 Claude

While that runs, the docs. First `xrpl-detector/README.md`: the diagram, ownership, run time and score sections.

<details><summary>Tool calls (1)</summary>

- `Bash` — Update xrpl-detector README sections

</details>

## 🤖 Claude

Next, `TEAM_NOTES.md`: add a status section for the branch, update the repo table and the Team 2 target, and tick the checklist items this branch covers.

<details><summary>Tool calls (1)</summary>

- `Bash` — Update TEAM_NOTES with branch status

</details>

## 🤖 Claude

Now the top-level README (the ZIP needs the exact command there), plus updated credits and licence.

<details><summary>Tool calls (1)</summary>

- `Bash` — Write root README, licence holder, credits

</details>

## 🤖 Claude

I wrote "16 GB" and "about 2 minutes" in the README without checking either. I'll measure both and correct them after the pipeline run.

<details><summary>Tool calls (1)</summary>

- `Bash` — Check machine RAM

</details>

## 🤖 Claude

16 GB is correct. Now I'll wait for training to finish.

<details><summary>Tool calls (1)</summary>

- `Bash` — Wait for training to finish

</details>

## 🤖 Claude

Training is still running; I'll be notified when it finishes.

## 🧑 User

_[Clicked the app's **Create PR** button]_

## 🤖 Claude

The user wants the PR now, but the docs still have CV placeholders and training hasn't finished. Let me check how far training has got.

<details><summary>Tool calls (5)</summary>

- `Bash` — Check training, remote state, existing PR
- `Bash` — Wait for training process to exit
- `Bash` — Fill CV numbers and run full pipeline on test
- `Bash` — Fix runtime note, compare scores, train smoke test
- `Bash` — Regenerate test outputs and stage changes

</details>

## 🤖 Claude

`models/` holds only generated files (`.gitignore` covers the `.joblib`, not `cv_metrics.json`), so I'm leaving it out of the commit.

<details><summary>Tool calls (1)</summary>

- `Bash` — Commit and push alert-ranker branch

</details>

## 🤖 Claude

The push worked, but `origin/main` has moved to `11f7a02` since I branched. Before opening the PR, I'll check that it doesn't conflict with this branch.

<details><summary>Tool calls (1)</summary>

- `Bash` — Inspect new main commits and test merge

</details>

## 🤖 Claude

The new commit on main is a one-line tweak to the alert-score formula in `alert_ranker.py`, a file this branch doesn't touch, and it merges cleanly. Opening the PR:

<details><summary>Tool calls (4)</summary>

- `Bash` — Open pull request against main
- `ToolSearch` — select:mcp__ccd_pr__get_status,mcp__ccd_pr__bind_pr
- `get_status`
- `wrap_up`

</details>

## 🤖 Claude

I've opened PR #2 to merge the new ranker into `main`. It's ready for review, and the repo has no CI checks.

<pr-created>https://github.com/jesanglimbu/AML-Model-XRPL/pull/2</pr-created>

**Getting up to date first:** your local `main` was 4 commits behind. Since this session started, the team had merged your tracker in PR #1, recorded a 59.2 leaderboard run, and then **already removed `alert_tracker.py` from `main`** ([teammate]'s commit `003b4e2`; the team agreed to keep one alert system). The only copies left were a stale untracked `alert_tracker.py` and a `TEAM_NOTES.md` edit in your folder. Both match what's in git history (commit `b96cf6d`), so I deleted them; a backup is in `/private/tmp/claude-501/-Users-jesang-AML-Model-XRPL/e67aff1f-128e-4660-8668-a36212b68395/scratchpad/backup/`. After that `main` updated cleanly and nothing in the repo refers to the tracker.

**The ranker, on a new `alert-ranker` branch:**
- **Where it lives:** my scoring model is now inside the team pipeline at `xrpl-detector/aml_ranker/`, rather than a separate tool.
- **What changed:** `train_model.py` now trains it, and `predict.py` takes its `probability` from it.
- **What didn't change:** `predictions.csv` keeps exactly the same columns. Trails, alert ranking, graphs and case summaries all work as before.
- **Score:** under the same validation split, it scores **AP 55.4** against **49.1** for the previous model, and it's better on easy, medium and hard cases.
- **Not uploaded yet:** I haven't put these scores on the site, so I can't say yet whether it beats the 59.2 run.
- **Checks:** training reproduced the same CV exactly (about 17 min). `run_pipeline.py` on the test data (34 s) and on `data/train` both pass every `schemas.py` check, and `outputs/submission.csv` has 40,101 rows.

**Docs I updated:**
- **`TEAM_NOTES.md`:** a status section for the branch, an updated repo table, and the four ZIP checklist items this branch covers ticked off.
- **`xrpl-detector/README.md`:** how scoring works, who owns what, and the new score.
- **New for the ZIP:** a top-level `README.md` with the exact command, an MIT `LICENSE` in the team's name, and `THIRD_PARTY.md`, which lists what we didn't write.

**For you or the team to decide:**
- **New commit on `main`:** while I worked, a one-line change to the alert score formula landed (`11f7a02`). It touches a file this branch doesn't change and merges cleanly.
- **Data in git:** the `decode-and-detect-*` data folders are tracked in git, even though the notes say never to commit data. They must stay out of the ZIP. I flagged this in TEAM_NOTES and didn't remove them myself.
- **Old branch:** the `alert-tracker` branch on GitHub is now out of date and can be deleted.

## 🧑 User

I'll upload outputs/submission.csv and tell you the leaderboard score.

## 🤖 Claude

Sounds good. `outputs/submission.csv` is the right file: it's from the test-data run, with 40,101 rows and all format checks passing.

When you report back, please send the **precision and recall** the site shows as well as the score. They're for the top 1% of scores, so they show where any change came from.

Once you have it, I'll:
- **If it beats 59.2:** record it in TEAM_NOTES' "Best run so far", push that to PR #2, and it's ready to merge.
- **If it doesn't:** compare it with the 55.4 from cross-validation. A big drop would point at the test data's new batch variations, and I'd look at which features shift between training and test.

## 🧑 User

I need to submit a .zip file with the source code and the predictions CSV.
Please provide me with these

## 🤖 Claude

I'll build the code ZIP from the committed `alert-ranker` branch, since that's the code that produced the scores, and leave out the data folders. Then I'll test the ZIP from a clean folder before handing it over.

<details><summary>Tool calls (4)</summary>

- `update_plan`
- `Bash` — Build code ZIP excluding data folders
- `update_plan`
- `Bash` — Run pipeline from unpacked ZIP and compare

</details>

## 🤖 Claude

The unpacked ZIP produces a byte-identical `submission.csv`, and every format check passes. Here are both files:

<details><summary>Tool calls (2)</summary>

- `SendUserFile`
- `wrap_up`

</details>

## 🤖 Claude

Both files are ready to upload together; they're attached above and saved in `outputs/`:

- **Code ZIP:** [outputs/AML-Model-XRPL-code.zip](outputs/AML-Model-XRPL-code.zip). It's 38 KB with 29 files, far inside the 8 MiB / 2,000-file limits. It contains the source code, `README.md` with the exact command, `xrpl-detector/requirements.txt`, the MIT `LICENSE` and `THIRD_PARTY.md`, and no data files.
- **Predictions CSV:** [outputs/submission.csv](outputs/submission.csv). It has one score for each of the 40,101 test payments, between 0 and 1.

**How I checked them:** I unpacked the ZIP into an empty folder and pointed it at the data. Running `run_pipeline.py` from there reproduced `submission.csv` byte for byte, and every format check passed. For that test I reused the already-trained model, so I didn't re-run the 17-minute training step from the ZIP. That same training code did give identical CV results on two separate runs.

**Things to know:**
- **The ZIP comes from the `alert-ranker` branch,** which isn't merged into `main` yet (PR #2). That's correct, because that branch's code produced these scores.
- **Library versions aren't pinned** in `requirements.txt`. If the organisers re-run it later with newer libraries, the scores could differ slightly. These ran on Python 3.14.8, NumPy 2.5.4, pandas 3.1.0, scikit-learn 1.9.1 and SciPy 1.18.1, and I can pin those if you want.
- **Rebuilding the ZIP:** the `outputs/` folder is ignored by git. If the code changes, ask me to rebuild the ZIP so it matches the new CSV.

Once it's uploaded, send me the score and I'll record it in TEAM_NOTES and on PR #2.

