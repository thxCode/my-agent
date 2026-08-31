# My Claude

Record basic plugins/skills/agents for personal Claude workspace. Less is more, KISS.

## Prerequisites

Set up the following before using this workspace. All commands assume the [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI is installed.

### 1. DeepWiki MCP

AI-powered documentation for any GitHub repository.

```bash
claude mcp add -s user -t http deepwiki https://mcp.deepwiki.com/mcp
```

### 2. GitHub MCP

Interact with GitHub (issues, PRs, code search) via the official MCP endpoint. Requires a [personal access token](https://github.com/settings/tokens) exported as `GITHUB_PERSONAL_ACCESS_TOKEN`.

```bash
export GITHUB_PERSONAL_ACCESS_TOKEN=<your-token>
claude mcp add -s user -t http github https://api.githubcopilot.com/mcp -H "Authorization: Bearer ${GITHUB_PERSONAL_ACCESS_TOKEN}"
# or
claude mcp add github -e GITHUB_PERSONAL_ACCESS_TOKEN=$GITHUB_PERSONAL_ACCESS_TOKEN -- npx -y @modelcontextprotocol/server-github
```

### 3. GitNexus MCP

Code knowledge graph for exploring, debugging, and impact analysis.

```bash
npm install -g gitnexus@latest
claude mcp add gitnexus -- npx -y gitnexus@latest mcp
gitnexus setup
```

### 4. agent-skills plugin

Addy Osmani's collection of agent skills (plan, build, test, review, ...).

```bash
claude plugin marketplace add addyosmani/agent-skills
claude plugin install agent-skills@addy-agent-skills
```

### 5. Codex plugin (optional)

Hand off or cross-check tasks with OpenAI Codex from inside Claude Code (e.g. the `codex:codex-rescue` agent).

```bash
claude plugin marketplace add openai/codex-plugin-cc
claude plugin install codex@openai-codex
```

### 6. Kimi plugin (optional)

Hand off or cross-check tasks with Kimi Code from inside Claude Code (e.g. the `kimi:kimi-rescue` agent) — a peer alternative to Codex.

```bash
claude plugin marketplace add thxcode/kimi-code-plugin-cc
claude plugin install kimi@moonshotai-kimi
```

> Needs the Kimi Code CLI: `curl -fsSL https://code.kimi.com/kimi-code/install.sh | bash`, then `kimi login` (OAuth device-code or API key) and `/kimi:setup` to verify. See [thxCode/kimi-code-plugin-cc](https://github.com/thxCode/kimi-code-plugin-cc).

### 7. crawl4ai (optional)

Local web crawler powering the `crawl4ai-search` skill — fetch pages as clean Markdown and screenshot rendered UIs. Provides the `crwl` CLI.

```bash
uv pip install crawl4ai --system
crawl4ai-setup
crawl4ai-doctor
```

### 8. Agent Teams (optional)

Lets `/my-build`'s `team` mode use real teammates — a shared task list with native dependency unblocking, direct teammate-to-teammate messaging, and a plan-approval gate for risky tasks — instead of falling back to parallel subagents. Experimental and off by default; add to `settings.json`:

```json
{
  "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" },
  "teammateMode": "tmux"
}
```

The env switch turns teams **on**; `teammateMode` decides how a teammate *appears*. It defaults to `in-process` — a subagent in this same window — so the switch alone gets you teams without windows. `"tmux"` gives real panes, which [Orca](#9-orca-optional) renders as ADE windows. Avoid `"auto"`: it silently falls back to in-process when no pane backend is found, and **that fallback latches for the rest of the session**.

> Known limits: teammates don't survive `/resume` or `/rewind`, task status can lag, all teammates inherit the lead's permission mode at spawn, and token use scales with teammate count. `/my-build` works without this — it says which path it's running.

### 9. Orca (optional)

[Orca](https://github.com/stablyai/orca) is an IDE for orchestrating AI coding agents — it hosts each agent in its own window, which is what turns Agent Teams' panes into visible ADE windows and what `/my-handoff` uses to hand work to another agent. Provides the `orca` CLI.

```bash
brew install --cask stablyai/orca/orca
```

Then install the skills Claude Code needs from it:

```bash
orca skills install --skill orca-cli --skill orchestration --agent claude-code
```

> Skills land in the shared `~/.agents/skills/` directory, and Claude Code only sees them through symlinks under `~/.claude/skills/`. Without the symlink a skill is installed but invisible — `ls -l ~/.claude/skills/` is the check, and `ln -s ../../.agents/skills/<name> ~/.claude/skills/<name>` is the repair. `orca skills install` with no arguments lists the rest (`computer-use` for desktop app control, plus the Linear and emulator skills).

**Start Claude Code through Orca**, not bare `claude`:

```bash
orca claude-teams '--dangerously-skip-permissions'
```

That puts a `tmux` shim first on `PATH`, so Claude Code's pane calls become Orca windows. Bare `claude` reaches the real tmux and opens panes the ADE panel can't see — teammates run, but you can't watch or drive them.

## Commands

Custom slash commands live in [`commands/`](commands).

- **`/my-triage [issue number or URL]`** — For the report you **cannot reproduce**: turns an issue thread into a diagnosis instrument. Each round states one falsifiable hypothesis, drafts one read-only probe a stranger can run on their own hardware, posts it **only after you approve the exact text**, and files what comes back as cited evidence — over a resumable ledger under `.claude/issues/` that outlives both the latency and the session. Ends in one of five verdicts (`bug-ours` → hands off to `/my-debug`, `bug-upstream`, `not-a-bug`, `undiagnosable`, or `stalled`), never in a guess. Closing the issue and filing upstream are **printed for you to run, never executed**.
- **`/my-spec [what you want to build or fix, or a GitHub issue]`** — Spec-driven development: gathers project/code context, judges intent (feature → user-story refinement; bug → read-only root-cause), then writes a KEP-style spec — committed to `specs/<yyyy-mm-dd>-<title>.md`, or tracked locally (never committed) under `.claude/specs/` if you choose. Hand it a GitHub issue instead (bare number, `#123`, `owner/repo#123`, or a URL — a selector carrying its own `owner/repo` overrides `origin`) and it reads the thread with its comments, distills one requirement from it, and saves as `<issue-number>-<title>.md`.
- **`/my-plan [spec title]`** — Deepens a spec's Design Details and fills its Test Plan (KEP format), breaking the work into a **tracer-bullet task DAG**: each task is a complete vertical path annotated with `Blocked by:` (its real dependencies), `Owns:` (the paths it exclusively touches), and `Gate: review` on the risky ones. Those annotations are what let `/my-build` run independent tasks in parallel. Wide refactors are sequenced expand–contract instead. After your review, writes back the spec only.
- **`/my-debug [bug description, error, or repro]`** — Lightweight bug-fix lane: reproduces and root-causes a bug (with a codex/kimi adversarial cross-check when it's complex), then writes a single throwaway debug artifact (Background / PoC / Root Cause / Fix Plan / Test Plan) to `.claude/debugs/<yyyy-mm-dd>-<title>.md` (always local, never committed) and hands off to `/my-build`. The quick counterpart to `/my-spec`'s tracked Bug-fix path. Also accepts a `/my-triage` handoff — an artifact whose Root Cause is already locked from remote evidence enters at Phase 3 and never asks for the local reproduction that, by construction, does not exist.
- **`/my-build [spec title] [auto|team]`** — Implements a spec's Design Details task by task (TDD + incremental, conforming to project conventions) on a dedicated branch (`spec/<title>` for features, `fix/<title>` for bug fixes); commits per task, then runs the end-of-build review. Three run modes: **per-task confirm** (default), **`auto`** (chains without pausing), and **`team`** — builds the DAG's independent tasks in parallel via [Agent Teams](#8-agent-teams-optional) when enabled, or parallel subagents when not. In `team` mode the lead never writes code and owns every commit; tasks marked `Gate: review` are spawned under plan approval and **their plan is relayed to you** before any code is written.
- **`/my-ship [spec title]`** — Finalizes a spec: optional e2e tests (writing fixes back to spec + the cheapest appropriate test coverage), refreshes the overview, and updates docs/ADRs; conforms to project conventions.
- **`/my-advisory [a GHSA id or advisory URL, a pasted report email, or a public issue number/URL]`** — The lane for a vulnerability report, from intake to published CVE. **Triage comes first:** is the flaw real, is it ours, is it reachable on a default configuration — and **is the reporter's severity right?** It scores the claim itself, and scores it *twice*, because a library's severity belongs to its consumers (`PR:L` for a caller feeding it its own files, `PR:N` for one feeding it whatever arrives on a socket); where it scores lower than the reporter did, it says so with the vector and the metric, not the adjective. Only then does it classify the embargo and pick the merge route — a **neutral public PR**, or the advisory's **temporary private fork** — because that pair decides the branch name and the wording of the very first commit. From there it drives `/my-debug` → `/my-build` → `/my-ship` unchanged and owns only what disclosure adds: the private GHSA advisory, the CVE request and the reporter's credit all started early (each runs for days, and publish waits on all of them), a regression guard that asserts the bound instead of the crash value that would kill the test binary, release-before-publish sequencing, and a four-box checklist — fix released, downstream consumers upgraded, credit **accepted**, CVE assigned — gating the one irreversible step. The embargo lives in the debug artifact's `Disclosure:` / `Route:` lines rather than in the session, so a run resumes from disk days later at the first unchecked box.
- **`/my-handoff [task brief] [--to codex|kimi|claude|opencode]`** — **Full handoff** to another agent in its own [Orca](#9-orca-optional) window: packs the context into `.claude/handoffs/<yyyy-mm-dd>-<title>.md` (background, files, acceptance, boundaries — the receiving agent starts cold), opens it split beside the current window (`--tab` for its own tab, `--worktree` for an independent checkout), delivers one line pointing at that file, and **stops** — there's no callback, so nothing tells you when they finish; `--watch` switches to supervised `orchestration` instead. Ownership transfers, so this is not a cross-check — `crosscheck` governs read-only second opinions where Claude keeps every edit. Fires only when you type it; no `my-*` command calls it. Needs an Orca-hosted session, and says so plainly when there isn't one.
- **`/my-crew [objective] [--agent codex|claude|kimi|…]`** — The **supervised** counterpart to `/my-handoff`. Every worker launches in its non-interactive mode (`--dangerously-bypass-approvals-and-sandbox` / `--dangerously-skip-permissions` / `--auto`), since codex's sandbox otherwise blocks the very RPC it needs to report back. Placement follows agent support: `worker-start` gives any launchable agent its own **tab** (kimi included), while a **split pane beside you** needs an agent Orca can detect from the command string — so kimi always gets a tab. Creates an orchestration **Run**, one **Task** per unit of work, starts each worker in its own [Orca](#9-orca-optional) window, then waits on `worker_done` / `escalation` / `question` — **relaying blocking questions to you** instead of answering them, because a worker blocks exactly when it hits a decision it has no standing to take. On each completion it verifies against the task's own criteria, then either routes that worker's next task or releases it. Where `/my-handoff` transfers ownership and stops, this keeps the Run and routes. Distinct from `/my-build … team`, which builds one repo's planned DAG with the lead owning every commit; here the workers own their edits. Orca places no workers and infers no conflicts, so parallel tasks must own disjoint paths or separate worktrees.
- **`/my-refine [path, or nothing for the whole family]`** — Maintenance pass over the prompt assets themselves. Runs five **conflict probes** (a rule on an unreachable branch, a gate keyed on state that can't be observed when it's read, a claim broader than its consumers, an absolute a newer branch contradicts, an enumeration that fell behind its table), then prunes a word / a phrase / a sentence at a time against [`skill-craft.md`](references/my-workflow/skill-craft.md). Reports conflicts, cuts, **and what it deliberately left alone** with the reason — then applies what you approve and verifies it mechanically. Never fires on its own (`disable-model-invocation`), so it costs no resident context.

The end-of-build review runs **two axes side by side, never merged**: **Standards** (`agent-skills:review`'s five dimensions plus a Fowler smell baseline — *is this code good?*) and **Spec** (`spec-reviewer` — *is this what was asked for?*). A change can pass one and fail the other, so merging them lets the clean axis mask the failing one. A gated codex/kimi cross-check is the optional third voice.

## Agents

Subagent definitions live in [`agents/`](agents). Four narrow contracts rather than one broad one — each says plainly what it will *not* do, so the boundaries hold under delegation.

| Agent | Does | Never |
| --- | --- | --- |
| **`task-worker`** | Implements one task from a planned task list end-to-end, TDD, confined to the paths the task `Owns:`. `/my-build`'s `team` lane executor. | Commits, takes design decisions, or edits outside its owned paths |
| **`spec-reviewer`** | Reviews a diff against the spec that ordered it — missing requirements, scope creep, requirements implemented wrong. Cites the spec line for every finding. | Edits anything, or judges code quality (that's the other axis) |
| **`fast-worker`** | Mechanical write-capable recipes — boilerplate, bulk formatting, scaffolding — driven by an explicit recipe. | Makes judgment calls, commits, or renders test verdicts |
| **`test-worker`** | Runs a bounded test recipe (suite command or browser flows) and reports pass/fail with evidence. | Edits project files or fixes what it finds |

## Skills

Custom skills live in [`skills/`](skills); Claude invokes them automatically when a task matches, or you can call one explicitly (e.g. `/auto-research`). `orca-cli` and `orchestration` are symlinks into `~/.agents/skills/` rather than skills of this repo — Orca ships them, `orca skills update` updates them, and each is a discovery stub whose real guide comes from the `orca` binary so it can't drift from the CLI that will run the commands.

Shared reference the `my-*` commands read on demand lives in [`references/my-workflow/`](references/my-workflow) — target resolution, GitHub-issue resolution, compaction focus, the decision gate, the smell baseline, the parallel team lane, probe craft (the read-only script a stranger runs, its hygiene gate, and the comment that carries it), and skill craft (what to cut from a prompt asset, and what to leave alone). Plain files, not skills: they cost nothing until a command points at them.

- **`address-pr-review`** — Consumes the review comments **already left** on a PR: triages each one against the source (real bug vs. false positive), fixes the real ones surgically, folds the fixes into the right commit to keep history clean, then replies to / resolves the threads. The counterpart to skills that *generate* a review.
- **`auto-research`** — Autonomous research harness: decomposes a topic, fans out web searches, adversarially verifies every claim against its source, then synthesizes a Perplexity-style cited report at `.claude/reports/<title>.md`. Cost-aware (throttles on rate-limit usage) and observable (per-round digest). After showing the plan it runs unattended (**auto mode**) or pauses for per-round approval (**manual-approve mode**).
- **`crawl4ai-search`** — Fetches web pages as clean, token-efficient Markdown (`md-fit` + BM25 filter) and screenshots rendered UIs via the local [crawl4ai](#7-crawl4ai-optional) (`crwl` CLI + a small SDK script). Used in place of `WebFetch` for JavaScript-rendered/content-dense pages and by `auto-research` workers for distilled fetches; supplies frontend render/responsive/component screenshots while delegating interactive debugging to `agent-skills:browser-testing-with-devtools`. Requires the optional crawl4ai install above.


## License

MIT
