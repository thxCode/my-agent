---
name: jev
description: >-
  Offload fast, calibrated System One decisions (routing, skill selection, bulk classification, rubric scoring,
  semantic linting, and 100-question diff verification) to TypeSafe AI's Jev model via TYPESAFE_API_KEY, or build
  TypeSafe API/SDK integrations in application code. Triggers on jev, typesafe, system one, systemone,
  choice/score/noul/box primitives, model routing, skill routing, bulk classify/score, semantic linter,
  100-question code review, jev on/off.
---

# jev — System One Decision Node & TypeSafe Integration

Derived from [`typesafe-ai`](https://github.com/typesafe-ai/skills/tree/main/skills/typesafe-ai)
(MIT, Copyright (c) 2026 TypeSafe AI); see `CREDITS.md`.

Pairs any System Two coding agent with TypeSafe AI's **Jev** (`jev-latest` / `jev-1.13.0` / `jev-preview`
`jev-1.14.0`), a **System One** model built for sub-second (~100 ms), calibrated, typed judgments (`choice`,
`score`, `noul`, `box`) where output tokens are free and input costs $0.042/Mtok.

**Core rule:** When a workflow step selects from known options, scores against a rubric, or checks whether a
condition holds, delegate that judgment to **Jev** (`scripts/jev_cli.py` or `POST https://api.typesafe.ai/v1/systemone`).
Keep deep reasoning, architecture, and code or prose generation in the System Two agent.

- **API & Primitives Reference:** [references/api-and-primitives.md](references/api-and-primitives.md)
- **Three Coding-Agent Playbooks (Routing, Bulk Triage, Verification):** [references/coding-agent-playbooks.md](references/coding-agent-playbooks.md)
- **Multi-Agent Host Integration (9 Coding Agents, zsh Key & SSL Resolution):** [references/host-integration.md](references/host-integration.md)

## 1. Environment, `TYPESAFE_API_KEY` (`zsh`) & macOS SSL CA Resolution

The user provides `TYPESAFE_API_KEY` in their `zsh` environment. Coding agents often spawn non-interactive
subshells that skip `~/.zshrc`.

Two CA conditions break HTTPS on macOS. A `Python.framework` build can ship without its `cert.pem` link, and a
stale `SSL_CERT_FILE` that names a missing file leaves the default context with zero roots. Either way every
request fails with `CERTIFICATE_VERIFY_FAILED`.

- **Bundled CLI (`~/.agents/skills/jev/scripts/jev_cli.py`):**
  - Reads `TYPESAFE_API_KEY` from the process environment and falls back to `zsh -ic 'printf "%s" "${TYPESAFE_API_KEY:-}"'` (then `zsh -lc`) if unset.
  - Builds an SSL context it can verify against. The interpreter default wins when no `ssl_cert_file` is configured and that default carries roots. Otherwise it tries `ssl_cert_file` from the mode config, then `SSL_CERT_FILE` / `REQUESTS_CA_BUNDLE` / `CURL_CA_BUNDLE`, then `certifi`, then common system bundles. The context is cached per process.
- **Direct shell or Python SDK calls:** Export both variables without printing the secret to stdout:
  ```bash
  export TYPESAFE_API_KEY="${TYPESAFE_API_KEY:-$(zsh -ic 'printf "%s" "$TYPESAFE_API_KEY"' 2>/dev/null)}"
  export SSL_CERT_FILE="${SSL_CERT_FILE:-$(python3 -c 'import certifi; print(certifi.where())' 2>/dev/null || echo /etc/ssl/cert.pem)}"
  : "${TYPESAFE_API_KEY:?TYPESAFE_API_KEY is missing in environment and zsh config}"
  ```
- **Health check:** Run `python3 ~/.agents/skills/jev/scripts/jev_cli.py doctor` to confirm `key_source`,
  `ssl_source`, `ssl_ca_count`, and connectivity against `GET https://api.typesafe.ai/v1/models`. A `ssl_source`
  of `none` with `ssl_ca_count` 0 means no usable bundle was found.

## 2. Mode Switch (`jev init` | `jev on` | `jev off` | `jev status`)

Persist project or global reflex mode in `.claude/jev-mode.json` via `jev_cli.py mode`:

```bash
python3 ~/.agents/skills/jev/scripts/jev_cli.py mode init     # Write the default config
python3 ~/.agents/skills/jev/scripts/jev_cli.py mode on       # Enable System 1 pre-routing & verification
python3 ~/.agents/skills/jev/scripts/jev_cli.py mode off      # Disable automatic Jev offloading (baseline comparison)
python3 ~/.agents/skills/jev/scripts/jev_cli.py mode status   # Check current mode, CA source, and thresholds
```

When mode is `on`, run **Position 1** before heavy task dispatch and **Position 3** before finalizing non-trivial
code changes. Toggle `off` to A/B test token savings and output quality on representative tasks.

## 3. Three Positions in Coding Workflows

Detailed templates and JSON schemas live in [references/coding-agent-playbooks.md](references/coding-agent-playbooks.md).

### Position 1 — Pre-Execution Routing (Model Tier & Skill Selection)

Before spending flagship LLM tokens on routing or loading dozens of `SKILL.md` files into context, call `route`:

```bash
python3 ~/.agents/skills/jev/scripts/jev_cli.py route \
  --prompt "<user request or subtask>" \
  --skills-dir ~/.agents/skills
```

- **Capability tier routing:** Evaluates atomic task signals in parallel and maps them to portable capability classes
  (`fast`, `balanced`, `strongest` per `~/.agents/skills/my-workflow/references/model-routing.md`). Route mechanical
  lookups, format conversions, and simple edits to `fast`; standard coding and review to `balanced`; ambiguous
  architecture, security, or migrations to `strongest`.
- **Skill selection:** Ranks the skills in `--skills-dir` by frontmatter `name` and `description` in one request
  (~100 ms) and returns `top_skills`. Read only the selected `SKILL.md` files into context. One `choice` question
  holds at most 255 skills, so point `--skills-dir` at a subset when the catalog is larger.

### Position 2 — Bulk Data Classification, Scoring & Pre-Filtering

When a task applies the **same judgment** across dozens or thousands of records (comments, leads, support tickets,
community posts, log lines, or transcript chunks for video highlights), never loop a System Two LLM over raw items.

1. Write atomic `Choice`, `Score`, and `Noul` questions in a JSON file (`questions.json`).
2. Run concurrent batch evaluation to a file (token discipline: keep raw dataset outputs on disk, not in chat context):
   ```bash
   python3 ~/.agents/skills/jev/scripts/jev_cli.py batch \
     --input records.jsonl \
     --questions-file questions.json \
     --out .claude/jev/results.jsonl \
     --top-k 20 --sort-by priority_score
   ```
3. **Jev pre-screens; the coding agent handles the distilled subset:** Inspect only the summary statistics and the
   top-ranked or low-confidence records that need deep reasoning, report generation, or custom drafting.

### Position 3 — Post-Code Automated Verification (System 2 Training System 1)

Close the coding feedback loop at near-zero cost before committing or opening a PR:

- **100-Question Diff Checklist & Semantic Linter (`review-diff`):** Pack 10 to 100 atomic `Noul` and `Score`
  checks into a **single parallel API call** (Speculative Fan-Out) against the current git diff:
  ```bash
  python3 ~/.agents/skills/jev/scripts/jev_cli.py review-diff \
    --git-diff "HEAD" \
    --rules-file .claude/jev/lint-rules.json \
    --out .claude/jev/diff-review.json
  ```
  Checks plain-English semantic rules (function naming vs. side effects, secret/amount/PII logging, unintended shared
  module edits, weakened unit tests, swallowed errors, magic numbers). Escalate **only** high-probability findings
  (`noul >= threshold` or `score >= threshold`) to the System Two coding agent for deep inspection and repair.
- **Codebase-Wide Sweep:** Extract all comments or functions into a `.jsonl` file, run `jev_cli.py batch` to flag
  noise/stale comments or code smells for cents, then dispatch a `fast` worker to clean up only the flagged locations.
- **Calibration loop:** When the coding agent spots a false positive or false negative in Jev's output, tighten the
  question's `instructions`, add contrastive `criteria` (`what`, `not_for`, `examples`), or adjust the confidence
  threshold in code, then re-run.

## 4. Workflow Audit (Discover Jev Opportunities)

When the user asks where Jev fits in their daily work or repository:

1. Scan recent task history, scripts, or LLM prompts in the workspace.
2. Identify steps that perform closed-set classification, routing, rubric grading, boolean guardrails, or candidate
   reranking.
3. Present a compact table of candidate nodes, the recommended primitive (`Choice`, `Score`, `Noul`, `Box`), and the
   expected latency/cost reduction.

## 5. Building TypeSafe Integrations in Application Code

When writing Python (`typesafe-sdk`), JavaScript/TypeScript (`@typesafe-ai/sdk`), or HTTP integrations for a user's
application, follow [references/api-and-primitives.md](references/api-and-primitives.md):

1. **Keep control flow in code:** Deterministic checks run in code before calling `POST https://api.typesafe.ai/v1/systemone`.
2. **Send focused, structured `state`:** Pass a JSON object with named fields and reference nested paths in backticks
   (for example, `` `ticket.messages[0].text` ``).
3. **Decompose and fan out:** Split multi-factor judgments into atomic questions and send all independent and
   speculative questions in **one request**. Combine scores with explicit weights in code (`score / (len(criteria) - 1)`).
4. **Gate on `confidence` and `probabilities`:** Act automatically on high confidence, confirm on medium confidence,
   and escalate to a human or System Two LLM when confidence falls below the risk floor.
5. **Centralize questions and thresholds:** Keep all question definitions and threshold constants in one module so
   humans can review and tune them without hunting through business logic.
