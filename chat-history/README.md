# Chat history

Each team member's use of AI on this entry, for the *Decode & Detect* terms (clauses 3.3 and 3.4). Every team member who used AI has a folder with a `README.md` in the same layout:

1. **Model and settings**: which model and tool, who used it, what for, and whether it runs at runtime (it never does)
2. **What Claude wrote or changed**: the commits, plus anything outside the repo
3. **Prompts about the entry**: every prompt, as typed, and what Claude did
4. **Reproducibility notes**

A `sessions/` folder holds full transcripts where they were exported.

| Team member | Log | Sessions |
|---|---|---|
| Jesang | [`jesang/README.md`](jesang/README.md) | 9, with transcripts in [`jesang/sessions/`](jesang/sessions/) |
| Owen | [`owen/README.md`](owen/README.md) | 1 (no transcript) |

## Rules for every log

- Prompts are copied as typed, including typos.
- Long pasted material is summarised in square brackets.
- Teammates' names are replaced with [teammate]; each log names only its own author.
- Home-folder paths are shortened to `~`. No API keys, tokens or passwords.

No AI service is used when the code runs, and none is needed to reproduce `outputs/submission.csv`.
