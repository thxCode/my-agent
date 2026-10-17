# Multi-Agent Host Integration Guide (9 Coding Agents)

This skill lives in `~/.agents/skills/jev` and is shared across all 9 target coding agents. It requires no per-host
duplication and no external Python packages.

## 1. Host Discovery & Explicit Invocation Matrix

All hosts share `~/.agents/skills/jev/SKILL.md` (either directly or via the symlinks in
`~/.agents/skills/my-workflow/references/host-adapters.md`).

| Coding Agent | Discovery Path | Explicit Invocation | Natural-Language Trigger |
| --- | --- | --- | --- |
| **Claude Code** | `~/.claude/skills/jev` -> `~/.agents/skills/jev` | `/jev <task>` | `"use the jev skill to ..."` |
| **Codex** | `~/.agents/skills/jev` (or `~/.codex/skills/jev`) | `$jev <task>` | `"use the jev skill to ..."` |
| **Kimi Code** | `~/.agents/skills/jev` | `/skill:jev <task>` | `"use the jev skill to ..."` |
| **Antigravity (`agy`)** | `~/.gemini/config/skills/jev` -> `~/.agents/skills/jev` | `/jev <task>` | `"use the jev skill to ..."` |
| **ZCode (`zcode`)** | `~/.agents/skills/jev` | `/skill jev <task>` | `"use the jev skill to ..."` |
| **MiniMax Code (`mcode`)** | `~/.agents/skills/jev` (`user-agents` / `~/.claude/skills`) | `/jev <task>` or via `/skills` | `"use the jev skill to ..."` |
| **Qwen Code** | `~/.qwen/skills/jev` -> `~/.agents/skills/jev` | `/jev <task>` | `"use the jev skill to ..."` |
| **GitHub Copilot** | `~/.agents/skills/jev` / `.github/skills/jev` / `.claude/skills/jev` | `/jev <task>` (Agent mode / CLI) | `"use the jev skill (~/.agents/skills/jev/SKILL.md) to ..."` |
| **Oh-my-pi (`omp`)** | `~/.agents/skills/jev` (native agents skill provider) | `/skill:jev <task>` | `"use the jev skill to ..."` |

## 2. Ensuring `TYPESAFE_API_KEY` Works Across All Host Subshells

Different coding agents launch shell commands differently:
- **Claude Code, Codex, Kimi Code, Qwen Code, OMP** typically run `/bin/zsh -c` or `/bin/sh -c` (non-interactive, non-login), which reads `~/.zshenv` (for `zsh`) but skips `~/.zshrc`.
- **Antigravity, ZCode, MiniMax Code, GitHub Copilot** may sanitize or inherit only the parent daemon environment.

To guarantee zero-friction authentication in every agent:
1. Always prefer invoking `~/.agents/skills/jev/scripts/jev_cli.py`, which checks `os.environ["TYPESAFE_API_KEY"]` first and automatically falls back to `zsh -ic` and `zsh -lc` to extract `TYPESAFE_API_KEY` from `~/.zshrc` or `~/.zshenv`.
2. When running user application code (`pytest`, `node`, `uv run`) that reads `TYPESAFE_API_KEY` directly from `os.environ`, wrap the command if the current subshell lacks the variable:
   ```bash
   TYPESAFE_API_KEY="${TYPESAFE_API_KEY:-$(zsh -ic 'printf "%s" "$TYPESAFE_API_KEY"' 2>/dev/null)}" <your-command>
   ```
3. Never echo or log `$TYPESAFE_API_KEY` in terminal output, commit messages, or skill artifacts.

## 3. Configuring `.claude/jev-mode.json` (Project & Global Switch)

`jev_cli.py` reads `.claude/jev-mode.json` in the current project root first, falling back to `~/.claude/jev-mode.json`
for global settings.

### Initialize or Toggle via CLI

```bash
python3 ~/.agents/skills/jev/scripts/jev_cli.py mode init             # Write full default .claude/jev-mode.json in current project
python3 ~/.agents/skills/jev/scripts/jev_cli.py mode init --global    # Write global ~/.claude/jev-mode.json
python3 ~/.agents/skills/jev/scripts/jev_cli.py mode on               # Enable Jev reflex mode
python3 ~/.agents/skills/jev/scripts/jev_cli.py mode off              # Disable Jev reflex mode (for A/B baseline comparison)
python3 ~/.agents/skills/jev/scripts/jev_cli.py mode status           # Inspect active config and resolved file path
```

### Full `.claude/jev-mode.json` Schema

```json
{
  "enabled": true,
  "model": "jev-latest",
  "positions": {
    "route": true,
    "batch": true,
    "review_diff": true
  },
  "route": {
    "skills_dir": "~/.agents/skills",
    "top_k": 3,
    "min_skill_prob": 0.08
  },
  "batch": {
    "concurrency": 16,
    "top_k": 10
  },
  "review_diff": {
    "noul_threshold": 0.5,
    "score_threshold": 1.0,
    "rules_file": null,
    "long_context": false
  },
  "updated_at": "2026-10-16T00:00:00Z"
}
```

`review-diff` and `route` honor `enabled` and their `positions` flag. `batch` runs only as an explicit call, so
`positions.batch` has no effect.

## 4. Optional Hook Wiring for Automatic Per-Turn Routing & Verification

Because `jev_cli.py route` and `jev_cli.py review-diff` automatically check `enabled` and `positions` inside
`.claude/jev-mode.json` (and exit cleanly as a no-op when `false`), you can wire them directly into host hooks:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.agents/skills/jev/scripts/jev_cli.py review-diff"
          }
        ]
      }
    ]
  }
}
```

## 5. Delegating Follow-Up Work to Subagents

When `jev_cli.py` finishes pre-screening (Position 1 routing, Position 2 top-K filtering, or Position 3 diff/comment flagging) and the coding agent needs to dispatch workers:
- Read `~/.agents/skills/my-workflow/references/agent-runtime.md` for the current host's native subagent adapter.
- Pass the file path of the `.claude/jev/*.json` output rather than pasting large JSON payloads into worker prompts (critical for MiniMax Code `mcode` single-line prompt submission and universal token hygiene).
