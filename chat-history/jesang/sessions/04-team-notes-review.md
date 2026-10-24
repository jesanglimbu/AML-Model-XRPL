# Team notes review

_Terminal (CLI) · 2026-10-24 10:39 → 2026-10-24 10:53 UTC_


## 🧑 User

Have a look at TEAM_NOTES.md

<details><summary>Tool calls (5)</summary>

- `Bash` — Show team notes and its uncommitted changes
- `Bash` — Check repo files against what the notes describe
- `Bash` — See what untracked files git would now pick up
- `Bash` — Check which rule ignores the data folders
- `Bash` — List tracked files and count tracked data files

</details>

## 🤖 Claude

Still checking the repo against the notes. One thing turned up: the data files are already committed. I'm checking whether they've been pushed.

<details><summary>Tool calls (1)</summary>

- `Bash` — Find when data was committed and whether it's on the remote

</details>

## 🤖 Claude

The notes read well, but they no longer match the repo. One of the gaps needs fixing soon.

**Urgent: the data files are already in git, and on GitHub.**
- The notes say "Never commit the data files", but commit `117545f Folder-Architecture` added both `decode-and-detect-*` folders: 13 parquet/csv files, about 180 MB on disk. That commit is on `origin/main`.
- Your uncommitted `.gitignore` change makes this worse. It drops the rules for `*.parquet`, `*.csv`, `test-data`, `dnd-env/`, `outputs/`, `.DS_Store` and `.env`, so API keys would no longer be ignored either.
- Removing the folders in a new commit stops them being tracked. They'd still be in the history, though, so a ZIP built from a clone or `git archive` stays safe but GitHub still holds the data. Getting them out of the history means a history rewrite and a force-push, which is your team's call.

**Where the notes are out of date:**
- **"What's in this repo"** leaves out `run.py` + `aml_ranker/` (Team 2's ranker), `xrpl-detector/`, `README.md`, `LICENSE`, `THIRD_PARTY.md` and `requirements.txt`.
- **There are two rankers**: `xrpl-detector/` has its own `alert_ranker.py`, `predict.py` and `train_model.py`, and `aml_ranker/` + `run.py` is the other. The notes should say which one makes the uploaded `predictions.csv`, with the exact command, e.g. `python run.py predict --train-dir … --test-dir … --out predictions.csv`.
- **Baseline**: the only score listed is the starter notebook's (33.5). There's nothing yet for the new ranker.
- **Setup**: it installs `pandas pyarrow scikit-learn jupyter` into `~/dnd-env`. But `requirements.txt` pins numpy and scipy too, and this repo uses `.venv`. Pointing the notes at `pip install -r requirements.txt` would keep them in step.
- **Checklist**: `LICENSE`, `requirements.txt` and the list of what we didn't write now exist, but none of them are ticked.

**Problems in `THIRD_PARTY.md`:**
- It's written as one person ("What I did not write myself"), but this is a team entry.
- It says "No organiser code is copied verbatim", but the repo includes the organisers' `payments.py` (the notes say so too) and the starter notebook. Those need listing to meet the checklist.

Want me to restore the `.gitignore` rules, stop tracking the data folders, and bring TEAM_NOTES.md and THIRD_PARTY.md up to date? I won't touch the git history or push anything without asking you first.

## 🧑 User

Yes, please.

<details><summary>Tool calls (1)</summary>

- `Bash` — Read README, run.py and xrpl-detector docs

</details>

## 🤖 Claude

Now making the edits: first `.gitignore`, then untracking the data folders.

<details><summary>Tool calls (2)</summary>

- `Write` — ~/AML-Model-XRPL/.gitignore
- `Bash` — Stop tracking data folders, keeping files on disk

</details>

## 🤖 Claude

Data files are still on disk and are no longer tracked. Next, updating the notes and `THIRD_PARTY.md`.

<details><summary>Tool calls (2)</summary>

- `Bash` — Read THIRD_PARTY.md and check for starter-notebook use
- `Bash` — Check other dependencies and payments.py copy

</details>

## 🤖 Claude

Now writing both files.

<details><summary>Tool calls (5)</summary>

- `Write` — ~/AML-Model-XRPL/THIRD_PARTY.md
- `Edit` — ~/AML-Model-XRPL/TEAM_NOTES.md
- `Edit` — ~/AML-Model-XRPL/TEAM_NOTES.md
- `Edit` — ~/AML-Model-XRPL/TEAM_NOTES.md
- `Edit` — ~/AML-Model-XRPL/TEAM_NOTES.md

</details>

## 🤖 Claude

Fixing the data paths in the older commands so they match the new layout, then checking the result.

<details><summary>Tool calls (2)</summary>

- `Bash` — Fix data paths, then verify ignore rules work
- `Bash` — Confirm data and .env are ignored, code is not

</details>

## 🤖 Claude

I've made the fixes, but nothing is committed or pushed yet.

**Data and `.gitignore`**
- I put back the old ignore rules and kept your new ones (`*.pyc`, `predictions*.csv`, `*.zip`, `data/`). I also added `.venv/`, `alert_tracker_data/` and the two `decode-and-detect-*` folders.
- Both data folders are staged as removed from git (`git rm --cached`), but the files are still on disk. Git now ignores the data and `.env`, and still sees the code.

**`TEAM_NOTES.md`**
- **Setup** now uses `.venv` and `pip install -r requirements.txt`.
- **New "Alert ranker (Team 2)" section** gives the exact `run.py predict` and `cv` commands. It has blank spaces for Team 2 to fill in their latest CV and leaderboard scores; I didn't have those numbers.
- **The file table** now lists `run.py`/`aml_ranker/`, `xrpl-detector/`, `README.md`, `requirements.txt`, `LICENSE` and `THIRD_PARTY.md`. I went with the README and marked `run.py` as the submission command, with `xrpl-detector/` as the earlier pipeline. Correct me if your team decided otherwise.
- **A note on the data in the history**: since the data is still in the history, it says to build the ZIP with `git archive HEAD` or from the working folder, never with `.git/` included.
- **Data paths** in the `case_summary`/`alert_tracker` commands now match the folders inside the repo.
- **Checklist**: I ticked README, requirements, LICENSE and the list of what we didn't write. "All source code" and "no data files" are left for the final check.

**`THIRD_PARTY.md`** is now written for the team ("we"). It lists `payments.py` as organiser code included unchanged and says the starter notebook was only used for the baseline. I updated the matching line in `README.md`.

**Still open:**
1. **Commit and push?** This takes the data folders off `main` from now on. It also commits your untracked files (`run.py`, `aml_ranker/`, `alert_tracker.py`, `LICENSE` and the rest) and the README changes.
2. **The data is still in the GitHub history.** Fully removing it means rewriting the history (e.g. `git filter-repo`) and force-pushing, and everyone would then have to re-clone. If the repo is private, I'd leave the history alone until after the deadline.

## 🧑 User

Ignore these changes.

## 🤖 Claude

I'll put everything back the way it was before my edits, keeping the uncommitted changes you already had.

<details><summary>Tool calls (5)</summary>

- `Bash` — Re-track data folders and restore .gitignore and README
- `Write` — ~/AML-Model-XRPL/THIRD_PARTY.md
- `Read` — ~/AML-Model-XRPL/TEAM_NOTES.md
- `Write` — ~/AML-Model-XRPL/TEAM_NOTES.md
- `Bash` — Confirm working tree matches the original state

</details>

## 🤖 Claude

I've put everything back the way it was before my edits. `git status` now matches what it showed at the start of the session.

- **Data folders:** tracked by git again. Nothing was committed or pushed, so the remote never changed.
- **`.gitignore`, `README.md`, `THIRD_PARTY.md`, `TEAM_NOTES.md`:** your own uncommitted edits are still there, including the `alert_tracker.py` section in the notes. Only my changes are gone.

One thing to watch: with your current `.gitignore`, git no longer ignores `.env` or `*.parquet`. So a `git add .` would pick up API keys, and new data files too if they turn up.

