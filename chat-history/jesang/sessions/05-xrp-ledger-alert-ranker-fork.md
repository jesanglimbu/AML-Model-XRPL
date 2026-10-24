# XRP Ledger alert ranker (fork)

_Desktop app · 2026-10-24 10:07 → 2026-10-24 12:54 UTC_


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

We got 65.4. Here's some stats:

What the best run caught: 65.4
Easy: 40% of 800
Medium: 10% of 225
Observable hard: 0% of 200
Ambiguous: 0% of 25

## 🤖 Claude

65.4 beats the previous best of 59.2. I'll record it in TEAM_NOTES and push to the PR. First I'll check the branch is still current.

<details><summary>Tool calls (7)</summary>

- `update_plan`
- `Bash` — Check branch and remote state
- `Bash` — Inspect the new main commits
- `update_plan`
- `Bash` — Branch off latest main and add breakdown
- `Bash` — Commit breakdown note locally
- `wrap_up`

</details>

## 🤖 Claude

65.4 is your best run yet: up from 59.2, which in turn beat the 33.5 baseline.

**Already done by the team:** PR #2 has been merged into `main`. [teammate] recorded the run in `TEAM_NOTES.md` as 65.4, with 91% precision and 29% recall in the top 1%, and added a table of all leaderboard runs.

**What I added:** your per-difficulty breakdown, as a note under that table. It's committed on a new local branch, `notes-65-4-breakdown`, made from the latest `main`. It's not pushed yet.

**Something to check:** the breakdown doesn't quite match the 29% recall.
- 40% of 800 easy plus 10% of 225 medium is about 342 payments.
- 29% recall in the top 1% means about 363 payments.

The gap of about 20 is too big to be rounding, so the breakdown may use a different cut-off than the top 1%. The note says so, so nobody compares future runs on it without knowing.

**What the breakdown shows:** almost all the gain is from easy cases, and the top 1% (about 400 payments) has room for at most half of the 800 easy ones. For the remaining points:
- **Medium cases (10% caught):** these are the most realistic gain. They're slow, legitimate-looking variants of the easy patterns.
- **Hard relay cases (0% caught):** these are still open. Nothing I tried separates the planted scenario from its 99 legitimate look-alikes.
- **Ambiguous cases (0% caught):** the README says their labels don't depend on anything in the data, so there's nothing to gain there.

## 🧑 User

Push notes-65-4-breakdown and open a PR into main.

<details><summary>Tool calls (1)</summary>

- `Bash` — Check main, push branch, check for existing PR

</details>

## 🤖 Claude

`main` hasn't moved, so the branch is current. It's pushed, and no PR exists for it yet. Opening one:

<details><summary>Tool calls (3)</summary>

- `Bash` — Open PR for breakdown note
- `get_status`
- `wrap_up`

</details>

## 🤖 Claude

I pushed `notes-65-4-breakdown` and opened PR #3 into `main`. It's ready for review.

<pr-created>https://github.com/jesanglimbu/AML-Model-XRPL/pull/3</pr-created>

The PR is the one-line breakdown note in `TEAM_NOTES.md`. `main` hadn't changed since I made the branch, so it merges cleanly, and the repo has no CI checks.

The PR description asks reviewers about the mismatch: your breakdown adds up to about 342 payments, but 29% recall in the top 1% implies about 363. If someone knows which cut-off the site's breakdown uses, they can fix the note before merging.

## 🧑 User

How do we beat our score now?

## 🤖 Claude

You have until 15:00 to add features. Here's where I'd spend that time, based on what we measured.

**Where the points are.** Easy cases are 64% of the suspicious payments. They're also where the site says we're already catching 40%, so better ranking of the remaining easy ones is the biggest lever. Medium (18%) is a realistic second target. The hard relay cases (16%) barely move the score even with a good idea, and the ambiguous ones (2%) can't be predicted by design.

**What I'd do, in order:**

1. **Upload variants of the model we already have.** This is the cheapest option and needs no new features. The test week scores much higher than our CV (65.4 vs 55.4) and has batch variations that aren't in training, so CV is a poor guide for small choices; with 50 uploads a day, let the site decide.
   - Stage 2 helped medium and hard in CV but hurt easy (easy AP 72.3 → 68.8), and easy is most of the points.
   - So upload three versions: stage 1 only, stage 2 only (the current upload), and the average of the two.
   - This needs a small change so `predict.py` writes all three files, plus 2 uploads. About 30 minutes, including retraining once.

2. **Adapt to the test week by training on our own confident test scores.** Retrain with the test week's most and least suspicious payments added as labelled examples. This is aimed at the new batch variations, and it uses only our own scores, not test answers. It's one run of about 20 minutes and one upload.

3. **Score whole episodes, not single payments.** Aggregated per scenario, the easy cases separate from the legitimate look-alikes much better (AUC 0.93) than individual payments do. Stage 2 only approximates this by averaging over neighbours. A model that scores each group of linked payments as a unit, then gives that score to its payments, could beat it. This is about an hour of work.

4. **Hard relays: there's one real lead, but it's weak.** In all 12 training cohorts, the planted hub passes money on sooner than most of its 99 look-alikes do (median about 2–4 hours vs about 1.4 days). That's consistent, but the planted scenario still only ranks about 24th of 100 within its cohort on average, so it would add very little to the score. I'd try it only after 1–3.

**What's not worth the time:** more hyperparameter tuning (four configs moved AP by about ±1), the ambiguous cases, and linking accounts to other suspicious activity (already tested, no signal).

To make each try faster, run experiments with one seed and cached features. That cuts a CV run from about 17 minutes to about 5, and you keep three seeds for the final upload.

I'd start with step 1 now: it's quick and gives you three uploads to compare by about 13:15.

<details><summary>Tool calls (1)</summary>

- `wrap_up`

</details>

## 🤖 Claude

The plan is above, and step 1 is the place to start: three submission files from the current model (stage 1 only, stage 2 only, and their average) that you can compare on the leaderboard. It takes about 30 minutes, mostly one retraining run, and it changes no features, so the main version of the code stays as it is.

## 🧑 User

Make predict write stage-1, stage-2 and blended submissions, retrain, and give me the three files to upload.

## 🤖 Claude

I'll build this on a new branch off the latest `main`.

The saved model already contains both stages, so the variants only need a change to `predict.py`. A retrain should reproduce the same model exactly; I verified that last time. So I'll first check the saved model still matches the merged code, and only retrain if it doesn't (that saves ~17 minutes before the deadline).

<details><summary>Tool calls (5)</summary>

- `update_plan`
- `Bash` — Branch off main and check model inputs
- `Edit` — ~/AML-Model-XRPL/xrpl-detector/aml_ranker/model.py
- `Read` — ~/AML-Model-XRPL/xrpl-detector/predict.py
- `Bash` — Add variant scores and submission files

</details>

## 🤖 Claude

Downstream still reads only `probability` (unchanged, stage 2), so alerts and reports aren't affected. Running the full test pipeline:

<details><summary>Tool calls (5)</summary>

- `update_plan`
- `Bash` — Run test pipeline writing all variants
- `update_plan`
- `Bash` — Validate variants and compare rankings
- `Bash` — Train smoke test, then regenerate test outputs

</details>

## 🤖 Claude

Both runs pass, and after regenerating, the test outputs still match the 65.4 file byte for byte. Last, a short doc update so the team knows about the variant files:

<details><summary>Tool calls (3)</summary>

- `Bash` — Update docs and commit on branch
- `SendUserFile`
- `wrap_up`

</details>

## 🤖 Claude

The three files are attached above and in `outputs/`. You only need to upload two of them: stage 2 is byte-identical to your 65.4 run, so uploading it again would just give 65.4.

| File | What it is | Upload? |
|---|---|---|
| `submission_stage1.csv` | Stage-1 model alone | **Yes** |
| `submission_blend.csv` | Average rank of stage 1 and stage 2 | **Yes** |
| `submission_stage2.csv` | Current two-stage ranker (= the 65.4 run) | No |

**Why these two:** in cross-validation, stage 2 hurt the easy cases (easy AP 72.3 → 68.8), and easy cases are most of the score. The rankings really do differ: stage 1 and stage 2 share only 340 of their top 401 payments. The blend sits in between, sharing 372 with stage 2 and 369 with stage 1.

**I didn't retrain.** Nothing in the scoring code has changed since the saved model was trained at 12:13, and training reproduces the same model exactly. Retraining would have taken ~17 minutes to rebuild a byte-identical model; the stage-2 file matching the 65.4 upload exactly confirms it's that model.

**What changed in the code:**
- **`predict.py`** now keeps both stages' scores and, on the test data, writes the three variant files. `config.py` gives their paths.
- **Unchanged:** `probability`, `submission.csv`, the alerts and the reports all still use stage 2.
- **Checks:** all schema checks pass, and both the test run and the `data/train` smoke run complete.

The change is committed on a local branch, `submission-variants`. It isn't pushed yet.

**Once you have the two scores:**
- **If either beats 65.4:** I'll make it the default `submission.csv`.
- **If neither does:** stage 2 stays, and I'll move on to retraining on our own confident test scores (step 2 of the plan).

## 🧑 User

I'll upload submission_stage1.csv and submission_blend.csv and tell you both scores.

## 🤖 Claude

Sounds good. Please send the top-1% precision and recall the site shows for each file along with its score. If the scores are close, those two numbers will show whether the difference comes from the top of the list or further down.

Once you have them:
- **If stage 1 or the blend beats 65.4:** I'll make the winner the default `submission.csv` (and the `probability` the alerts use), update TEAM_NOTES, then push the branch and open a PR.
- **If neither does:** stage 2 stays the default. I'll still push the variants branch so the team can reuse the files, then start on retraining with our own confident test scores.

The branch `submission-variants` is committed locally and isn't pushed yet; I'll push it once we know which default to set.

## 🧑 User

I also need the source code in a .zip file

## 🤖 Claude

I'll build the ZIP from the `submission-variants` branch, since that's the only code that can reproduce all three files you're uploading (stage 2 / 65.4, stage 1 and blend). It will follow the site's rules: source code, README with the exact command, dependencies, licence and credits, and no data, environments, model files or keys. I'll check it actually works from a fresh unzip.

<details><summary>Tool calls (8)</summary>

- `update_plan`
- `Bash` — Check imports, deps, secrets, file list
- `Bash` — Get tested versions and README section
- `update_plan`
- `Edit` — ~/AML-Model-XRPL/README.md
- `Bash` — Commit README and build code ZIP
- `update_plan`
- `Bash` — Rebuild ZIP and test from fresh unzip

</details>

## 🤖 Claude

From the fresh unzip, the pipeline reproduces all four submission files byte for byte. Last, the site's ZIP limits:

<details><summary>Tool calls (4)</summary>

- `update_plan`
- `Bash` — Check ZIP against site limits
- `SendUserFile`
- `wrap_up`

</details>

## 🤖 Claude

The code ZIP is attached above and saved as [AML-Model-XRPL-code.zip](AML-Model-XRPL-code.zip) in the repo folder. Upload this same ZIP with whichever submission file you send; it can reproduce all three.

**What's in it:** 29 files from the `submission-variants` branch:
- all the source: the `xrpl-detector/` pipeline, the `aml_ranker/` model, `case_summary.py`, and the organisers' `payments.py`
- the top-level `README.md` with the exact command, the language version and the run time
- `xrpl-detector/requirements.txt`, `LICENSE` (MIT), and `THIRD_PARTY.md`, which lists what we didn't write, including the AI assistance
- `TEAM_NOTES.md`

The data folders, the virtual environment, the trained model and the outputs are left out, and there are no API keys or secrets.

**Checked against the site's limits:**

| Limit | Ours |
|---|---|
| 8 MiB compressed | 39 KiB |
| 64 MiB uncompressed | 82 KiB |
| 2,000 files | 29 |
| No encrypted, multi-part or ZIP64 archives | None of those |

**Checked that it reproduces:** I unzipped it into an empty folder, added the data and the trained model, and ran `run_pipeline.py`. All four submission files (`submission`, `stage1`, `stage2`, `blend`) came out byte-identical to the ones you have. I didn't re-run the ~17-minute training from the ZIP. Training is the same code that reproduced its results exactly before.

**Small changes I made for the ZIP:**
- **README:** now explains how the stage-1 and blend files are produced, since your best run may end up being one of them, and lists the library versions we tested with.
- **`.gitignore`:** I added a `*.zip` rule so the ZIP doesn't get committed by accident; the team's version didn't have one.

These are the last 2 of 3 commits on the local branch `submission-variants`, which isn't pushed yet. I'll push it when your stage-1 and blend scores come back.

**If one of the variants wins:** I'll make it the default `submission.csv` and rebuild the ZIP so it matches.

## 🧑 User

_[Clicked the app's **Create PR** button]_

## 🤖 Claude

This PR is for a branch I haven't worked on, `notes-specialist-result`, and another linked session (PR #4) has since changed the code: there's now a "medium specialist" and the blend is the default. So I'll check the current state before committing anything.

<details><summary>Tool calls (1)</summary>

- `Bash` — Inspect branch, changes, remote and PRs

</details>

## 🤖 Claude

Nothing needs a new PR. `notes-specialist-result` is identical to its remote copy (`80fa4b9`), the working tree has no changes (only the generated `models/` folder, which isn't committed), and the branch is **already fully merged** into `main` through PR #7. It has no commits that aren't on `main`, so a new PR would be empty, and GitHub refuses those. Here's the existing PR for this branch:

<pr-created>https://github.com/jesanglimbu/AML-Model-XRPL/pull/7</pr-created>

**While I was away, the linked session [xrp-ledger-alert-rank-2](#local_4732c7f2-dac6-41fa-85c3-c64992bb530f) merged four PRs into `main`:**
- **#4:** made the stage-1/stage-2 blend the default score, after it scored **65.9** on the leaderboard (up from 65.4).
- **#5:** added a medium-case specialist as an upload candidate (CV 57.4 vs 55.7).
- **#6:** recorded the specialist's leaderboard run, **65.9**, a tie with the blend.
- **#7:** added a readable chat history from the project's Claude Code sessions.

The new `train_model.py` I was shown is from those merged commits, so nothing on this branch is uncommitted.

**Two things are out of date because of this:**
- **Your local `main`** is 4 commits behind `origin/main`. Update it before starting new work.
- **The code ZIP I built** came from `submission-variants` before the blend became the default and before the specialist was added. It doesn't match the current best run (65.9), so rebuild it from the latest `main` before you upload it.

## 🧑 User

_[Clicked the app's **Create PR** button]_

## 🤖 Claude

Again a branch I haven't worked on: `chat-history-structure`. Let me check its state.

<details><summary>Tool calls (1)</summary>

- `Bash` — Inspect chat-history-structure branch

</details>

## 🤖 Claude

No PR is possible for this one yet: `chat-history-structure` has no changes.

- **No commits:** it's a local branch at the same commit as `main` (`fb2b463`), with nothing that isn't already on `main`.
- **No uncommitted work:** the working tree is clean apart from the generated `models/` folder.
- **Not on GitHub:** the branch hasn't been pushed, and no PR exists for it.

So there's nothing to commit, and GitHub won't open a PR that has no changes. I haven't pushed the empty branch.

The name suggests someone created it to restructure the chat history added in PR #7, but nothing has been done on it yet. Once that work is committed here, I can push the branch and open the PR.

