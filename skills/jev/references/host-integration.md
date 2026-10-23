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
| **Pi (`pi`)** | `~/.agents/skills/jev` (built-in Agent Skills location) | `/skill:jev <task>` | `"use the jev skill to ..."` |

## 2. Ensuring `TYPESAFE_API_KEY` & SSL Certificates Work Across All Host Subshells

Different coding agents launch shell commands differently:
- **Claude Code, Codex, Kimi Code, Qwen Code, Pi** typically run `/bin/zsh -c` or `/bin/sh -c` (non-interactive, non-login), which reads `~/.zshenv` (for `zsh`) but skips `~/.zshrc`.
- **Antigravity, ZCode, MiniMax Code, GitHub Copilot** may sanitize or inherit only the parent daemon environment.
- **macOS `Python.framework` SSL root certificate quirk:** Official macOS Python builds look for `/Library/Frameworks/Python.framework/Versions/<ver>/etc/openssl/cert.pem`, which is absent unless linked (`x509_ca == 0`). A stale `SSL_CERT_FILE` that names a missing file causes the same symptom.

To guarantee zero-friction authentication and TLS verification in every agent:
1. **Built-in auto-resolution in `jev_cli.py`:** It resolves `TYPESAFE_API_KEY` from `os.environ` -> `zsh -ic` -> `zsh -lc`. It builds an SSL context from the interpreter default when no `ssl_cert_file` is configured and that default holds roots, then from `ssl_cert_file` in `.claude/jev-mode.json`, `SSL_CERT_FILE` / `REQUESTS_CA_BUNDLE` / `CURL_CA_BUNDLE`, `certifi`, or common system bundles. The context is cached per process.
2. **When running external Python SDK scripts (`typesafe-sdk`, `httpx`, `urllib`):** Those do not use `jev_cli.py`'s resolution. Export both variables in `~/.zshenv`, which every `zsh` subshell loads, or link Python's OpenSSL `cert.pem` once:
   ```bash
   # Option A: One-time symlink for macOS Python.framework
   ln -sf "$(python3 -c 'import certifi; print(certifi.where())')" \
     "$(python3 -c 'import ssl; print(ssl.get_default_verify_paths().openssl_cafile)')"

   # Option B: Export in ~/.zshenv so all non-interactive Coding Agent subshells inherit it
   export SSL_CERT_FILE="/etc/ssl/cert.pem"
   ```
3. Never echo or log `$TYPESAFE_API_KEY` in terminal output, commit messages, or skill artifacts.

For a direct shell or Python SDK call on a `zsh` host, export the variables without printing the secret:

```bash
export TYPESAFE_API_KEY="${TYPESAFE_API_KEY:-$(zsh -ic 'printf "%s" "$TYPESAFE_API_KEY"' 2>/dev/null)}"
export SSL_CERT_FILE="${SSL_CERT_FILE:-$(python3 -c 'import certifi; print(certifi.where())' 2>/dev/null || echo /etc/ssl/cert.pem)}"
: "${TYPESAFE_API_KEY:?TYPESAFE_API_KEY is missing in environment and zsh config}"
```

Run `python3 ~/.agents/skills/jev/scripts/jev_cli.py doctor` to check `key_source`, `ssl_source`, `ssl_ca_count`,
and connectivity against `GET https://api.typesafe.ai/v1/models`. An `ssl_source` of `none` with `ssl_ca_count` 0
means no usable bundle was found.

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
  "ssl_cert_file": null,
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
