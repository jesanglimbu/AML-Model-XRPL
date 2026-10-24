# Repository without datasets

_Desktop app · 2026-10-24 11:55 → 2026-10-24 12:05 UTC_


## 🧑 User

Create a new repo without the datasets. If possible, with the commit history, if not a clean commit

<details><summary>Tool calls (6)</summary>

- `update_plan`
- `Bash` — Inspect remotes, history, and largest blobs
- `Bash` — List dataset paths ever tracked
- `Bash` — Check code references to dataset dir files
- `Bash` — Mirror-clone repo and normalize branches
- `Bash` — Strip dataset dirs from all history and verify

</details>

## 🤖 Claude

History is rewritten: all 30 commits kept, dataset folders gone, repo shrunk from 124 MB to 172 KB. Now creating the new private GitHub repo and pushing.

<details><summary>Tool calls (2)</summary>

- `Bash` — Create private GitHub repo and push all branches
- `Bash` — Check local and remote state

</details>

## 🤖 Claude

The first push went wrong (it pushed from the wrong clone). The repo is brand new and empty, so I'm repairing it: main as the default branch, all six branches pushed, the stray refs removed.

<details><summary>Tool calls (2)</summary>

- `Bash` — Fix branches, default branch, and stray refs
- `wrap_up`

</details>

## 🤖 Claude

I created the new repo with the commit history kept: **https://github.com/jesanglimbu/AML-Model-XRPL-clean**. It's private and its default branch is `main`.

- **Removed from every commit:** `decode-and-detect-training-data/` and `decode-and-detect-test-data/`. That includes the organisers' README, `payments.py`, `checksums.json` and the starter notebook, since they came in the same download. Your code doesn't import any of them.
- **Kept:** all 30 commits, with their authors, dates and messages. None of them were dataset-only, so none got dropped. Because the history was rewritten, the commit hashes are different from the old repo's. The repo went from 124 MB to about 170 KB.
- **Branches:** `main`, `alert-ranker`, `alert-tracker`, `medium-experiments`, `notes-65-4-breakdown` and `submission-variants`.
- **One new commit** on `main` (and `medium-experiments`): it adds the two data folders to `.gitignore`, so a local copy of the data won't show up as untracked.
- **Fixed during setup:** my first push sent the wrong refs. Since the repo was brand new and nobody had cloned it, I force-pushed the correct branches and deleted the stray ones.

Not touched:
- The original `AML-Model-XRPL` repo and your local checkout. Its history still contains the datasets.
- Your uncommitted changes to `features.py`, `model.py`, `train_model.py` and `models/`. They aren't in the new repo.

`TEAM_NOTES.md:94` still says the data folders are tracked in git, which is no longer true in the new repo. To work from the new repo, clone it fresh and copy your uncommitted files over:

```bash
git clone git@github.com:jesanglimbu/AML-Model-XRPL-clean.git
```

## 🧑 User

How do I add this to github?

## 🤖 Claude

It's already on GitHub, so there's nothing left to add. The repo is at **https://github.com/jesanglimbu/AML-Model-XRPL-clean**, with all six branches and the full history. It's private for now, so only you can see it. You should see it at that link or under your repositories.

Some things you might want to do next:

**Make it public** (or do it in the repo's Settings → General → Danger Zone):
```bash
gh repo edit jesanglimbu/AML-Model-XRPL-clean --visibility public --accept-visibility-change-consequences
```

**Rename it** (for example, back to the original name once you've retired the old repo):
```bash
gh repo rename AML-Model-XRPL-v2 --repo jesanglimbu/AML-Model-XRPL-clean
```

**Add teammates:** go to the repo's Settings → Collaborators → Add people.

**Work from it on your machine:** clone it next to your current folder, then copy your uncommitted edits over:
```bash
git clone git@github.com:jesanglimbu/AML-Model-XRPL-clean.git ~/AML-Model-XRPL-clean
```
```bash
cp ~/AML-Model-XRPL/xrpl-detector/aml_ranker/{features,model}.py ~/AML-Model-XRPL-clean/xrpl-detector/aml_ranker/ && cp ~/AML-Model-XRPL/xrpl-detector/train_model.py ~/AML-Model-XRPL-clean/xrpl-detector/
```

Then put the data folders inside the new clone. The `.gitignore` there keeps git from tracking them.

## 🧑 User

Is it possible to keep working on the old repo and commit it to this?

## 🤖 Claude

Yes. You can keep working in your existing `~/AML-Model-XRPL` folder and push to the new repo. One catch: the two repos' histories don't match anymore. The new repo has the same commits with the dataset files stripped out, so every commit hash changed. If you just pointed your old checkout at the new repo and pushed, git would refuse, or it would push the datasets back in.

The fix is to point your old folder at the new repo and move your local branches onto the new history. Your uncommitted edits and the data files on disk stay where they are.

```bash
cd ~/AML-Model-XRPL && git remote rename origin old-origin && git remote add origin git@github.com:jesanglimbu/AML-Model-XRPL-clean.git && git fetch origin
```

```bash
git reset --mixed origin/medium-experiments && git branch -u origin/medium-experiments
```

```bash
for b in main alert-ranker notes-65-4-breakdown submission-variants; do git branch -f $b origin/$b; git branch -u origin/$b $b; done
```

What this does:
- **The `reset --mixed`** moves your current branch onto the new history but doesn't touch your files. Your edits to `features.py`, `model.py` and `train_model.py` still show as modified. The data folders become untracked, and the new `.gitignore` hides them.
- **The loop** moves your other local branches onto the matching new ones.
- After that, `git commit` and `git push` work as usual and go to the new repo.

Two things to know:
- The `old-origin` remote still points at the old repo. Don't push to it from here, or the old history mixes with the new. Once you're sure you don't need it, remove it with `git remote remove old-origin`.
- Anyone else with a clone of the old repo has to do the same switch, or simply re-clone the new repo.

Want me to run these steps in your folder?

## 🧑 User

I meant to say is it possible to keep working on the old repository until the deadline, and then make a new repo without the datasets?

## 🤖 Claude

Yes, that works fine. Nothing about the old repo has changed, so keep committing and pushing to it as usual until the deadline. Afterwards, rerun the same cleanup on the final history. It takes about a minute, and you can ask me to do it again then.

**What to do with the repo I already made:**
- **Easiest:** keep `AML-Model-XRPL-clean` and overwrite it at the deadline. It's private and nobody uses it, so a force-push with the final cleaned history replaces what's there.
- Or delete it now (repo Settings → Danger Zone → Delete) and create a new one at the deadline.

**At the deadline,** these commands redo the same steps I ran today: a fresh mirror copy, then the dataset folders stripped from every commit on every branch, then a push to the new repo. Your working folder is never touched.

```bash
mkdir -p ~/repo-clean && cd ~/repo-clean && rm -rf clean.git && git clone --mirror git@github.com:jesanglimbu/AML-Model-XRPL.git clean.git && cd clean.git
```

```bash
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --index-filter 'git rm -r -q --cached --ignore-unmatch decode-and-detect-training-data decode-and-detect-test-data' --prune-empty -- --all
```

```bash
git for-each-ref --format='%(refname)' refs/original refs/pull | xargs -n1 git update-ref -d; git reflog expire --expire=now --all && git gc -q --prune=now --aggressive && du -sh .
```

```bash
git push --force --mirror git@github.com:jesanglimbu/AML-Model-XRPL-clean.git
```

A few notes:
- This clones from GitHub, so it only picks up what's been pushed. Push all your branches to the old repo first.
- The `du -sh` line prints the repo size. It should be a few hundred KB. If it's still tens of MB, something with data in it is left over.
- If you add data under another folder name before then (e.g. `data/`), add it to the `git rm` list.
- Your `.gitignore` already blocks `*.parquet` and `*.csv`, so new data files won't sneak in.

