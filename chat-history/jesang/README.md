# Jesang's AI prompts

Disclosure for the *Decode & Detect* terms (clauses 3.3 and 3.4): which AI was used, how, and the prompts given to it.

## Model and settings

| | |
|---|---|
| Model | Claude Opus 5.5 (`claude-opus-5-5`), Anthropic |
| Tool | Claude Code in the Claude desktop app (Code tab, v2.1.308; medium effort, auto permission mode), plus one session in the Claude Code CLI in a terminal (v2.1.310) |
| Used by | Jesang, on 24 October 2026 (nine sessions, two of them forks of the first) |
| Used for | Building the alert ranker and the alert tracker, submission files and code ZIPs, git branches and pull requests, a dataset-free copy of the repo, documentation, and exporting this chat history |
| Used at runtime? | **No.** The submitted code never calls an LLM. Predictions are fully reproducible without any AI service |

Other team members also used Claude via Claude Code (see [`../README.md`](../README.md)). This log covers Jesang's sessions only. Full transcripts are in [`sessions/`](#sessions).

## What Claude wrote or changed

| Commit | Change |
|---|---|
| `b96cf6d` | `alert_tracker.py`: an analyst review queue with a decision log (removed later by the team in `003b4e2`) |
| `e1a0155` | Two-stage alert ranker (`xrpl-detector/aml_ranker/`) as the pipeline's scoring model, with TEAM_NOTES updates |
| `b85c6eb` | `TEAM_NOTES.md`: per-difficulty breakdown for the 65.4 run |
| `3f3d606`, `a6359ec`, `610b335` | Stage-1, stage-2 and blended submission files; README on the variants and tested library versions; ignore submission ZIPs |
| `c631518`, `ce638ba` | The stage-1/stage-2 blend made the default score (65.9), and the README updated |
| `be9670a` | Medium-case specialist as an upload candidate (CV 57.4 vs 55.7) |
| `b773315` | `TEAM_NOTES.md`: the specialist's leaderboard run (65.9, tie) |
| `80fa4b9` and this commit | `chat-history/`: session transcripts, this log, and one layout for every team member's log |

Not written by Claude: `975b7f2`, `b947414` and `796093b` (small `REPORT.md` edits made by hand).

Outside the repo: a private copy of the repo with both dataset folders removed from every commit (`AML-Model-XRPL-clean`), installing the Claude Code CLI and the GitHub CLI, and the code ZIPs uploaded to the site.

Analyses run but not committed: the alert tracker on the team model's test scores (60 alerts from the top 1%), the team pipeline's model scored under the ranker's cross-validation, four medium-case experiments and a seed-noise check, and a review of the data files tracked in git (a proposed clean-up was undone on request).

## Prompts about the entry

Prompts are copied as typed, including typos. Long pasted material is summarised in square brackets, and teammates' names are replaced with [teammate]. Sessions are listed in the order their own work started; forks begin with a copy of the session they were forked from, which is not repeated here.

### [XRP Ledger alert ranker](sessions/01-xrp-ledger-alert-ranker.md)

| # | Prompt | What Claude did |
|---|---|---|
| 1 | Using the training and testing data, create a XRP Ledger alert ranker in Python | Explored the data and labels; built and trained the ranker; cross-validated it (site score 55.4) and wrote `predictions.csv` |
| 2 | Before committing/pushing, make sure you have the updated branch in the repository. Read TEAM_NOTES.md and any other files that may give an update on the current development workflow and progress. Update and edit them accordingly. I made an alert_tracker, but I meant to make an alert_ranker in one of the repo branches. Could you remove the tracker without breaking the repo and add the ranker? | Pulled `main`; found the team had already removed the tracker; moved the ranker into the pipeline as its scoring model; compared it with the team model under the same cross-validation; updated TEAM_NOTES |
| 3 | [Clicked the app's Create PR button] | Finished training, ran the full pipeline on the test data, committed, pushed and opened PR #2 |
| 4 | I'll upload outputs/submission.csv and tell you the leaderboard score. | Confirmed it was the right file and asked for precision and recall too |
| 5 | I need to submit a .zip file with the source code and the predictions CSV. Please provide me with these | Built the code ZIP without data; reproduced the CSV from a fresh unzip; sent both files |

### [XRP Ledger AML alert tracker](sessions/02-xrp-ledger-aml-alert-tracker.md)

| # | Prompt | What Claude did |
|---|---|---|
| 6 | This GitHub repo has the source code and files for an XRP Ledger anti-money-laundering model hackathon. Read TEAM_NOTES.md and build a simple MVP alert tracker in Python. We want the final product to be user-friendly, a model/product that an analyst will trust the most on a 4:55 PM Friday. Make sure to git pull and commit/push without conflicts. Here is more information about the hackathon: [Pasted the organisers' event description] | Built `alert_tracker.py` (review queue with a decision log), tested it and pushed the branch |
| 7 | [Clicked the app's Create PR button] | Could not open the PR (GitHub CLI not installed); gave a compare link and a ready description |
| 8 | Install the GitHub CLI with brew, then open the PR (I'll do gh auth login if needed). | Installed the GitHub CLI; asked for `gh auth login` |
| 9 | I've run gh auth login. Open the PR now. | Opened PR #1 |
| 10 | What are the next steps? Our current score is 68.7, here are the stats: What the best run caught: 59.2 Easy: 50% of 800 Medium: 10% of 225 Observable hard: 0% of 200 Ambiguous: 0% of 25 | Ran the tracker on the team model's test scores (60 alerts) and suggested next steps |
| 11 | Actually, I meant to make an alert_ranker, not a tracker. Could you rewrite the MVP and get rid of this tracker branch? | Interrupted before Claude replied; done in prompt 2 instead |

### [Claude terminal integration](sessions/03-claude-terminal-integration.md)

| # | Prompt | What Claude did |
|---|---|---|
| 12 | Integrate Claude into the terminal. | Installed the Claude Code CLI and checked it was on the shell PATH |

### [Team notes review](sessions/04-team-notes-review.md) (terminal)

| # | Prompt | What Claude did |
|---|---|---|
| 13 | Have a look at TEAM_NOTES.md | Compared the notes with the repo; flagged that the data folders were tracked in git and that an uncommitted `.gitignore` change stopped ignoring `.env` and data files |
| 14 | Yes, please. | Restored the ignore rules, untracked the data folders and updated TEAM_NOTES; nothing committed |
| 15 | Ignore these changes. | Undid its own edits and left the user's uncommitted edits in place |

### [XRP Ledger alert ranker (fork)](sessions/05-xrp-ledger-alert-ranker-fork.md)

| # | Prompt | What Claude did |
|---|---|---|
| 16 | We got 65.4. Here's some stats: What the best run caught: 65.4 Easy: 40% of 800 Medium: 10% of 225 Observable hard: 0% of 200 Ambiguous: 0% of 25 | Recorded the breakdown in TEAM_NOTES on a new branch; pointed out it doesn't quite match the 29% recall |
| 17 | Push notes-65-4-breakdown and open a PR into main. | Pushed and opened PR #3 |
| 18 | How do we beat our score now? | Proposed a plan, starting with comparing stage-1, stage-2 and blended submissions |
| 19 | Make predict write stage-1, stage-2 and blended submissions, retrain, and give me the three files to upload. | Added the variants, retrained, checked them and sent the files (stage 2 identical to the 65.4 run) |
| 20 | I'll upload submission_stage1.csv and submission_blend.csv and tell you both scores. | Explained what it would do with each result |
| 21 | I also need the source code in a .zip file | Documented tested library versions; built the ZIP and reproduced the submissions from a fresh unzip |
| 22 | [Clicked the app's Create PR button] | Found the branch already merged (PR #7); nothing to open |
| 23 | [Clicked the app's Create PR button] | Found the `chat-history-structure` branch empty at the time; nothing to open |

### [Project overview](sessions/06-project-overview.md)

| # | Prompt | What Claude did |
|---|---|---|
| 24 | Give a brief overview of this project. | Summarised the task, the pipeline and its outputs |
| 25 | Are there any GUI components? How can we make this product user-friendly so analysts can review our flagged suspicious activities? | Confirmed there is no GUI; suggested ways to make the alerts easier to review |

### [XRP Ledger alert ranker (fork 2)](sessions/07-xrp-ledger-alert-ranker-fork-2.md)

| # | Prompt | What Claude did |
|---|---|---|
| 26 | Both beat our original run, stage 1 got 65.6, blend got 65.9 Precision was 91% for blend, precision was 92% for stage 1 | Made the blend the default score (fixing the alert threshold it would have broken); opened PR #4 |
| 27 | [teammate], one of the team members, told me to run at least 2-3 experiments on medium cases and upload any that beat 65.4 in cross-validation. Hard stop at 14:30, so the final model is retrained and uploaded by 15:00 | Ran four medium-case experiments and a seed-noise check; one passed, added as `submission_specialist.csv`; opened PR #5 |
| 28 | I'll upload submission_specialist.csv and tell you the score. | Explained what it would do with each result |
| 29 | Could you send the source file (without datasets) and the csv | Interrupted before Claude replied |
| 30 | Send the source code .zip file (without datasets) and the csv | Built the ZIP from `main` without data, models or secrets; reproduced the CSV from it; sent both |
| 31 | It scored the same. | Recorded the tie (blend stays final); rebuilt the ZIP from the latest `main` |
| 32 | [Clicked the app's Create PR button] | Opened PR #6 |

### [Repository without datasets](sessions/08-repository-without-datasets.md)

| # | Prompt | What Claude did |
|---|---|---|
| 33 | Create a new repo without the datasets. If possible, with the commit history, if not a clean commit | Removed both dataset folders from every commit and pushed the result to a new private repo |
| 34 | How do I add this to github? | Explained it was already there; gave commands to make it public or rename it |
| 35 | Is it possible to keep working on the old repo and commit it to this? | Explained how to point the old folder at the new history |
| 36 | I meant to say is it possible to keep working on the old repository until the deadline, and then make a new repo without the datasets? | Confirmed; gave the steps to rerun the clean-up at the deadline |

### [Chat history export](sessions/09-chat-history-export.md)

| # | Prompt | What Claude did |
|---|---|---|
| 37 | Can you export our chat history to the repo | Exported the sessions and converted them to Markdown in `chat-history/` |
| 38 | Commit chat-history/ on this branch (leave models/ out). | Committed it |
| 39 | [Clicked the app's Create PR button] | Opened PR #7 |
| 40 | There's also [teammate]'s chat history. Can you make the structure consistent (and also update the chat history). | Moved both logs into `chat-history/<name>/`, wrote this log in the same format, refreshed the transcripts and updated the links |

## Reproducibility notes

- No AI service is needed to run the code or reproduce `submission.csv`.
- Claude's suggestions were checked by running the code: cross-validation that holds out whole scenarios, format checks on every upload file, and reproducing the upload from a freshly unpacked code ZIP.
- Leaderboard runs from these sessions: 65.4 (two-stage ranker), 65.6 (stage 1), 65.9 (blend, the final default) and 65.9 (medium specialist, a tie).

## Sessions

Full transcripts of each session: prompts and replies, with tool calls folded into one-line notes. Tool output and model reasoning are left out. Times are UTC on 24 October 2026; forks start with a copy of their parent's conversation, so their start time is the parent's.

| # | Session | Tool | Time (UTC) |
|---|---|---|---|
| 1 | [XRP Ledger alert ranker](sessions/01-xrp-ledger-alert-ranker.md) | Desktop app | 10:07–11:23 |
| 2 | [XRP Ledger AML alert tracker](sessions/02-xrp-ledger-aml-alert-tracker.md) | Desktop app | 10:31–10:59 |
| 3 | [Claude terminal integration](sessions/03-claude-terminal-integration.md) | Desktop app | 10:34–10:35 |
| 4 | [Team notes review](sessions/04-team-notes-review.md) | Terminal (CLI) | 10:39–10:53 |
| 5 | [XRP Ledger alert ranker (fork)](sessions/05-xrp-ledger-alert-ranker-fork.md) | Desktop app | 10:07–12:54 |
| 6 | [Project overview](sessions/06-project-overview.md) | Desktop app | 11:32–11:33 |
| 7 | [XRP Ledger alert ranker (fork 2)](sessions/07-xrp-ledger-alert-ranker-fork-2.md) | Desktop app | 10:07–12:45 |
| 8 | [Repository without datasets](sessions/08-repository-without-datasets.md) | Desktop app | 11:55–12:05 |
| 9 | [Chat history export](sessions/09-chat-history-export.md) | Desktop app | 12:49–12:57 |
