# Owen's AI prompts

Disclosure for the *Decode & Detect* terms (clauses 3.3 and 3.4): which AI was used, how, and the prompts given to it.

## Model and settings

| | |
|---|---|
| Model | Claude Opus 5.5 (`claude-opus-5-5`), Anthropic |
| Tool | Claude Code (command-line agent), default settings |
| Used by | Owen, on 24 October 2026 (one session) |
| Used for | Environment setup, reading the organisers' files, writing and editing code, testing, git commits and pushes, documentation, and explaining concepts |
| Used at runtime? | **No.** The submitted code never calls an LLM. Predictions are fully reproducible without any AI service |

Other team members also used Claude via Claude Code (see `THIRD_PARTY.md` and the `Co-Authored-By` lines in the git history). This log covers Owen's session only.

## What Claude wrote or changed

| Commit | Change |
|---|---|
| `aa7b051` | `.gitignore` for data, virtual environment and secrets |
| `d56611c` | `case_summary.py` (first case summary writer) and a copy of the organisers' `payments.py` |
| `ff8bbd1`, `f204405`, `8912136`, `46b6194` | `TEAM_NOTES.md` handover notes and leaderboard scores |
| `7f4164f` | Plain-English intro and glossary in `xrpl-detector/case_writer.py` |
| `54c9bc0` | Repo-relative paths in `config.py`, `run_pipeline.py`, `train_model.py`; removed unused `xrpl-py` |
| `4a66fec` | `outputs/submission.csv` in the upload format, and its format check in `schemas.py` |
| `003b4e2` | Removed `alert_tracker.py` (team decision to keep one alert system) |
| `217c5c8` | Alerts: flag the top 1% of scores and group by 10-minute bursts (`config.py`, `trail_tracker.py`) |

Analyses run but not committed: comparison of the two alert groupings and of burst windows from 3 to 60 minutes, scored against the training labels with out-of-fold predictions.

## Prompts about the entry

Prompts are copied as typed, including typos. Long pasted material is summarised in square brackets, and teammates' names are replaced with [teammate].

| # | Prompt | What Claude did |
|---|---|---|
| 1 | pip install xrpl-py==5.2.0 pandas networkx scikit-learn | Tried to install; found Python 3.9 is too old for xrpl-py 5.2.0; explained options |
| 2 | How do you create a new account on the XRP Ledger? | Explained key pairs, funding and the reserve, with xrpl-py examples |
| 3 | what is a mule network finder | Explained money mule networks and how to detect them |
| 4 | ok so im doing a hackathon about ai and block chains and there is six ideas, mule network dinfer,money trail tracker,limit-dodge detector,fake trading detector,alert ranker,case summary writer | Explained each idea, difficulty and how they fit together |
| 5 | in a team of four and we have time until 4pm | Proposed roles and a timeline |
| 6 | we have training data go look at my downlaod files | Read the organisers' README, starter notebook and label counts; explained the real task and scoring |
| 7 | so we diving into teams team 1 do money trail tracker , team 2 do alert ranker and i am doing case sumarry writer | Explained how the three parts connect and planned the case summary writer |
| 8 | can u instal the libraries and notebook | Created a virtual environment, installed libraries, ran the starter notebook (baseline) |
| 9 | so i should sent them this notebook | Explained teammates can download it themselves; gave setup steps |
| 10 | we already hv a shared github so what should i do | Gave next steps |
| 11 | how to check num3 | Explained how to check `.gitignore` |
| 12 | there is no giles | Found the repo; created `.gitignore` |
| 13 | yes | Committed `.gitignore`; push failed (GitHub login needed) |
| 14 | wait so can i not verify the mac to github | Explained GitHub login options |
| 15 | so can i push sth in terminal to try? | Explained personal access tokens |
| 16 | ok so done now everything set and pushe | Checked the push; confirmed |
| 17 | so how can i upload the baseline to site | Built the baseline code ZIP (licence, README, dependencies) and explained uploading |
| 18 | can u share claude session | Explained `/export`; offered a handover note |
| 19 | do the handover note and push it to github | Wrote and pushed `TEAM_NOTES.md` |
| 20 | i uploaded baseline 33.5 score 62 precision 20 recall | Explained the numbers; recorded them |
| 21 | so do i need a description of the data so its more user friendly | Proposed an intro and glossary for the reports |
| 22 | yes do it , i also pulled see what is updated | Reviewed the team's new pipeline; added the glossary to `case_writer.py`; flagged data in repo and path issues |
| 23 | [Link to the team's Google Slides] look at this and see what we can do better | Could not open it (private); explained how to share it |
| 24 | can u fix 2 and 3 | Fixed pipeline paths and requirements; trained and tested the pipeline |
| 25 | [Pasted the organisers' participant terms] | Checked the entry against the terms; listed gaps |
| 26 | Should I add a step that also writes outputs/submission.csv in the right format, so you can upload the better score straight away? yes, also push everything after this step | Added `submission.csv`; built and verified a reproducible code ZIP |
| 27 | so what am i adding to the website | Explained which two files to upload |
| 28 | its not lettign me to upload the same csv? | Checked the files differ; explained likely causes |
| 29 | 59.2 94 30 in the same order | Explained the numbers; recorded them |
| 30 | so did u see my teamate pushed the alert tracker should i run the thing again to see if our score improved | Explained it doesn't change scores; ran it on the latest scores |
| 31 | who did the pipeline alert_ranker | Checked the git history |
| 32 | so how can i fix the two alert system isseue, which one is working better | Compared both groupings against the training labels |
| 33 | so ru sure its not two system a trail tracker and alert ranker , [teammate]'s code should be a alert ranker instead | Explained the overlap and a role-aligned design |
| 34 | ok so can we just delete [teammate] side of code and keep the pipeline approach, all of them agreed | Removed `alert_tracker.py`; tested and pushed |
| 35 | what would be a good change? chaning time frame? | Compared 3 and 10-minute bursts and flagging rules |
| 36 | whats the difference between using a 3 min and 10 min time frame | Explained how burst windows link payments |
| 37 | what other time frame might be bettwe what about 15/20 | Compared windows from 3 to 60 minutes |
| 38 | please update to 1% and 10 min, pull before push | Changed the settings; checked the upload file is unchanged; pushed |
| 39 | can u git pull and see whats changed | Reviewed the team's new two-stage ranker |
| 40 | ok we updated againg 65.4 91 29 | Explained the numbers; recorded them |
| 41 | ok so how should deal with problem 1 where it will break until u retrain , download scipy | Installed scipy; retrained the new model on Python 3.9 |
| 42 | ok so can u explain what is payments left out and why does it happen and how are cases found | Explained |
| 43 | so what should we do to improve score right now? do we want to implment new features from the list before or keep polishing the stuff we have | Recommended priorities |
| 44 | wait so if i upload sth to the website it takes 15 min to give me and answer | Explained training time vs instant scoring |
| 45 | are u sure its 3 not 4 the feature freeze | Clarified 15:00 was a suggested buffer, not a rule |
| 46 | ok what the polishing 6 points can u furthur go into it and give details | Detailed each remaining submission requirement |
| 47 | for 1 is decode and detect test and training data causing the issue | Listed the tracked data files |
| 48 | can we js remove the two files so the model is public | Explained git history and the fresh-repo option |
| 49 | where did it say we cant publish the data sets | Quoted the relevant clauses |
| 50 | can u keep check all the promts from today and write it a document | Wrote this file (then renamed it and anonymised names) |

## Reproducibility notes

- No AI service is needed to run the code or reproduce `submission.csv`.
- Claude's suggestions were checked by running the code: format checks, a clean-folder reproduction of the upload file, and comparisons against the training labels.
- Model results depend slightly on library versions (cross-validation 55.4 on Python 3.14 vs 57.1 on Python 3.9 with scikit-learn 1.6.1, same code).
