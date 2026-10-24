# Claude terminal integration

_Desktop app · 2026-10-24 10:34 → 2026-10-24 10:35 UTC_


## 🧑 User

Integrate Claude into the terminal.

<details><summary>Tool calls (8)</summary>

- `update_plan`
- `Bash` — Survey project files and entry points
- `Bash` — Check for Claude CLI, SDK, and tracker commands
- `AskUserQuestion`
- `update_plan`
- `Bash` — Install Claude Code CLI via official installer
- `Bash` — Verify claude works and is on shell PATH
- `wrap_up`

</details>

## 🤖 Claude

I installed the Claude Code CLI (version 2.1.310) at `~/.local/bin/claude` using Anthropic's official installer. Your `~/.zshrc` and `~/.zprofile` already put that folder on your PATH, and a fresh login shell finds `claude`.

To start, open a new terminal window (or run `source ~/.zshrc` in one that's already open), then go to the project and launch it:

```bash
cd ~/AML-Model-XRPL && claude
```

The first time you run it, it will ask you to sign in through your browser. You'll need to do that step yourself. After that, `claude --help` lists the options, and `claude -p "question"` gives you a one-shot answer without opening an interactive session.

