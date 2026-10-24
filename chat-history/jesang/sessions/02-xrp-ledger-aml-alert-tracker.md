# XRP Ledger AML alert tracker

_Desktop app · 2026-10-24 10:31 → 2026-10-24 10:59 UTC_


## 🧑 User

This GitHub repo has the source code and files for an XRP Ledger anti-money-laundering model hackathon.
Read TEAM_NOTES.md and build a simple MVP alert tracker in Python.
We want the final product to be user-friendly, a model/product that an analyst will trust the most on a 4:55 PM Friday.
Make sure to git pull and commit/push without conflicts.

Here is more information about the hackathon:



_[Pasted material, 16 lines, left out]_

<details><summary>Tool calls (13)</summary>

- `update_plan`
- `Bash`
- `Bash`
- `Bash`
- `Bash`
- `Bash`
- `Bash`
- `Bash`
- `update_plan`
- `Write` — ~/AML-Model-XRPL/alert_tracker.py
- `Bash`
- `Bash`
- `Bash`

</details>

## 🤖 Claude

zsh doesn't word-split variables; using a function instead.

<details><summary>Tool calls (3)</summary>

- `Bash`
- `Bash`
- `Bash`

</details>

## 🤖 Claude

Re-check logic verified. While the real model finishes scoring the test set, adding docs and ignoring the tracker's local data folder.

<details><summary>Tool calls (1)</summary>

- `Bash`

</details>

## 🤖 Claude

Docs updated. Waiting for the team's model (`run.py predict`) to finish scoring the 40,101 test payments so I can run the tracker on real scores before committing.

<details><summary>Tool calls (1)</summary>

- `Bash`

</details>

## 🤖 Claude

Still training (about 10 CPU-minutes so far). I'll pick up when it finishes.

<br>

<details><summary>Tool calls (1)</summary>

- `Monitor`

</details>

## 🤖 Claude

The background scoring job will notify me when it's done. I'll continue from there with the real-data test, then commit and push.

## 🧑 User

_[Clicked the app's **Create PR** button]_

<details><summary>Tool calls (4)</summary>

- `update_plan`
- `Bash`
- `Bash`
- `Bash`

</details>

## 🤖 Claude

zsh treated `$C:r` as a modifier; quoting the variable.

<details><summary>Tool calls (1)</summary>

- `Bash`

</details>

## 🤖 Claude

Pushed, based on the current `origin/main` so it merges cleanly. Opening the PR.

<details><summary>Tool calls (2)</summary>

- `Bash`
- `Bash`

</details>

## 🤖 Claude

`gh` isn't installed on this Mac, so I can't open the PR from here. The branch is pushed, though. Saving the PR description so you can paste it in.

<details><summary>Tool calls (2)</summary>

- `Bash`
- `wrap_up`

</details>

## 🤖 Claude

I couldn't open the PR because the GitHub CLI (`gh`) isn't installed on this Mac. The branch is pushed, so you can open the PR from this link:

**https://github.com/jesanglimbu/AML-Model-XRPL/compare/main...alert-tracker?expand=1**

Title: *Add alert tracker: analyst review queue with a decision log*. I saved a ready-to-paste description at `/private/tmp/claude-501/-Users-jesang-AML-Model-XRPL/8fb3a581-9eae-459e-a52e-6c0892c69ebf/scratchpad/pr_body.md`.

**What's in the branch** (one commit, on top of the current `main`, so it won't conflict):
- [alert_tracker.py](alert_tracker.py): the tracker. `refresh` turns `predictions.csv` into ranked alerts; `queue`, `show`, `history` and `handover` show them; `review`, `escalate`, `close` and `reopen` record decisions.
- A section and a table row in [TEAM_NOTES.md](TEAM_NOTES.md), plus two lines in [.gitignore](.gitignore).

**Why an analyst can trust it late on a Friday:**
- **Decisions are never lost.** They're only ever added to the end of a log, and closing or escalating requires a note. Re-scoring keeps every decision and moves it to whichever alert now holds those payments.
- **New activity isn't missed.** A closed or escalated alert that picks up new flagged payments goes back to the top of the queue as "reopened".
- **Bad input fails loudly** with a plain message.
- **Every alert says in plain English why it's there** and lists each payment's full hash.

**Testing so far:**
- On the training labels with simulated scores (the labels plus random noise), the default 6-hour window keeps 97% of the payments in an alert from the same laundering scenario. A 24-hour window drops that to 86%.
- The whole workflow ran correctly on training data, including re-scoring. The test caught two problems, both fixed: an old alert ID couldn't be found after re-scoring, and an escalated alert that gained new payments wasn't reopened.
- **It hasn't been run on the real test-set scores yet.** The team's model (`run.py predict`) is still training.

**Someone else is editing this same folder.** There are uncommitted changes I didn't make: data files staged for removal from git, plus edits to README, LICENSE, `THIRD_PARTY.md`, `requirements.txt`, TEAM_NOTES and `.gitignore`. I left all of them out of the commit and didn't touch their working copy. When they commit, they'll get a small conflict in TEAM_NOTES and `.gitignore`; their copy already has the same tracker lines, so they should keep both sides.

## 🧑 User

Install the GitHub CLI with brew, then open the PR (I'll do gh auth login if needed).

<details><summary>Tool calls (2)</summary>

- `update_plan`
- `Bash`

</details>

## 🤖 Claude

`gh` 2.103.2 is installed, but it isn't logged in yet, so I need you to sign in.

<details><summary>Tool calls (1)</summary>

- `wrap_up`

</details>

## 🤖 Claude

I installed the GitHub CLI (version 2.103.2), but it isn't logged in, so I couldn't open the PR yet. Signing in is interactive and needs your GitHub account, so please run this yourself in a terminal:

```bash
gh auth login
```

Choose **GitHub.com**, then **SSH** (your `origin` remote uses SSH), and sign in through the browser. Once that's done I'll open the PR from the pushed `alert-tracker` branch.

## 🧑 User

I've run gh auth login. Open the PR now.

<details><summary>Tool calls (4)</summary>

- `Bash`
- `ToolSearch` — select:mcp__ccd_pr__get_status,mcp__ccd_pr__bind_pr
- `get_status`
- `wrap_up`

</details>

## 🤖 Claude

PR #1 is open, ready for review rather than a draft, and merges `alert-tracker` into `main`.

<pr-created>https://github.com/jesanglimbu/AML-Model-XRPL/pull/1</pr-created>

- It contains only my commit: `alert_tracker.py`, the new TEAM_NOTES section and table row, and two `.gitignore` lines. The other uncommitted changes in your working folder aren't included, and I didn't touch them.
- The repo has no automated checks, so nothing will run on the PR.
- I still haven't tried the tracker on the real test-set scores; the team's `run.py predict` was still training when I last checked.

## 🧑 User

What are the next steps?
Our current score is 68.7, here are the stats:

What the best run caught: 59.2
Easy: 50% of 800
Medium: 10% of 225
Observable hard: 0% of 200
Ambiguous: 0% of 25

<details><summary>Tool calls (2)</summary>

- `Bash`
- `wrap_up`

</details>

## 🤖 Claude

68.7 is a big jump from the 33.5 baseline. It's 11:52 and features freeze at 15:00, so you have about 3 hours of model work. I'd spend it like this.

**1. Protect 68.7 first (about 20 min, do it now)**
- Write down the exact commit and command that produced the best run, and tag that commit (for example `best-68.7`). Only your best upload counts, so any later experiment can't lose it, but you need to be able to reproduce it.
- Someone in your folder has uncommitted submission prep: the data files untracked from git, plus README, LICENSE, `THIRD_PARTY.md` and `requirements.txt`. Get that committed and pushed today; it covers most of the ZIP checklist.
- From a fresh clone, run the README's `run.py predict` command once. It takes 10–15 minutes, and the organisers may re-run it. A broken command is a worse risk than a few points.

**2. Where the points are**

| Group | Caught | Missed | Worth chasing? |
|---|---|---|---|
| Easy | 50% of 800 | ~400 | **Yes, most likely gain.** They're fast bursts the model should rank highly, so the misses are probably being pushed down by legitimate look-alikes. |
| Medium | 10% of 225 | ~200 | **Yes.** These are slower versions of the same patterns, so longer timing windows should help. |
| Observable hard | 0% of 200 | 200 | Only if time is left. The ranker README says each hard cohort hides 1 real case among 99 identical legitimate ones. |
| Ambiguous | 0% of 25 | 25 | No. They're deliberately unpredictable. |

The score rewards putting real cases at the top, so two things help: lifting missed easy payments above the look-alikes, and cutting the false alarms at the very top of the list.

**3. Measure before changing anything**
Don't guess at features. Run `run.py cv` and look at two lists from the scores each payment gets when it's held out:
- the highest-ranked legitimate payments, to see which look-alike shapes beat real cases;
- the missed easy and medium cases, to see where they rank and what pattern family they're in.

That should point to one or two targeted features. You have about 50 uploads, so upload only versions that beat the current CV score.

**4. Alert tracker (pitch material)**
- Merge PR #1.
- Once the model's test-set scores land, run `refresh` on them so the demo shows real alerts. I'll do this when the scoring job finishes; it's still running.
- `handover --out handover.md` gives a clean "Friday 4:55" slide.
- In TEAM_NOTES, fill in the "Latest CV score" and "Latest leaderboard upload" lines with 68.7.

I'm not sure what cutoff the "caught" figures use. 50% of 800 plus 10% of 225 is about 422 payments, which is more than the top 1% (about 400), so they're probably not counted at the top 1%. That doesn't change the plan above.

## 🤖 Claude

Real test-set scores are ready (40,101 payments, 22 min). Running the tracker on them as promised, in a scratch store so nothing lands in the repo.

<details><summary>Tool calls (2)</summary>

- `Bash`
- `wrap_up`

</details>

## 🤖 Claude

The team model finished scoring the test set (40,101 payments, about 22 minutes). On those real scores, the tracker turned the top 1% (401 payments) into **60 alerts**, so an analyst works through 60 cases instead of 401 separate payments.

- **The top of the queue looks right.** The highest-ranked alerts are tight bursts of 6–12 payments over 2–8 minutes, with money passed on within a minute or two. That matches the fast-moving pattern in the training data.
- **What the alerts look like:** 27 are led by a fan-out, 22 by a relay and 1 by a fan-in. The other 10 have no clear shape and say so rather than inventing a reason. The largest alert has 22 payments; 8 alerts are a single payment.
- **The tracker itself was quick:** about a second on top of loading the data. All of this ran in a scratch folder, so nothing in the repo changed.

These scores come from the committed `run.py`. I can't tell whether that's the same version as your 68.7 upload. For the pitch, run `refresh` on whichever `predictions.csv` you actually uploaded.

The plan from my last message still stands: protect the 68.7 run first, then look at where the model misses before changing any features.

## 🧑 User

Actually, I meant to make an alert_ranker, not a tracker. Could you rewrite the MVP and get rid of this tracker branch?

## 🧑 User

_[Interrupted Claude]_

