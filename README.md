# My Agent Workflow

Personal, reusable engineering workflows for CLI agents that can load `SKILL.md` instructions, work in a
repository, and run its verification commands. Clone this repository directly to `~/.agents`; it is the
canonical source for shared instructions, skills, and role contracts.

## Shared layout

```text
~/.agents/                    # this Git repository
├── AGENTS.md                 # shared global instructions
├── CREDITS.md                # upstreams the distilled skills came from
├── skills/                   # shared skill discovery root
│   ├── my-workflow/          # natural-language router and shared references
│   ├── my-spec/              # one workflow stage per skill
│   ├── my-plan/
│   ├── my-build/
│   ├── ...
│   └── interview-me/         # distilled from upstream, see Distilled skills
└── agents/                   # native adapters to shared role contracts
```

Keep one copy of the shared instructions and skill bodies. A host can discover this root directly or link
its supported discovery paths to it; project instructions remain owned by each repository. Installation
paths, invocation syntax, and client-specific exceptions live in
[host-adapters.md](skills/my-workflow/references/host-adapters.md).

Do not add a `CLAUDE.md` here: it would duplicate the shared rules and can displace this repository's
`AGENTS.md` in clients that prefer it. The adapter reference explains instruction loading in detail.

## Install

1. **Clone.** The repository is self-contained; there is nothing to fetch afterwards.

   ```bash
   git clone https://github.com/thxCode/my-agent.git ~/.agents
   ```

2. **Connect your host.** Follow the relevant entry in
   [host-adapters.md](skills/my-workflow/references/host-adapters.md). Use direct discovery where available;
   otherwise link the host's supported instruction and skill paths. Keep model, permission, hook, MCP, and
   credential configuration in that host's own format.
3. **Verify discovery.** Confirm that the host loads the intended instruction sources and lists one copy of
   every `my-*` skill. Run `python3 ~/.agents/skills/my-workflow/scripts/validate_shared_skills.py` to check
   the repository; this does not verify a client's live catalog.

## Update

One pull updates every host connected to this working tree:

```bash
git -C ~/.agents pull --ff-only
```

To find out whether a distilled skill has fallen behind the repository it came from, run `my-refine sync`;
it reports upstream drift and changes nothing.

## Host compatibility

Single-agent stages need skill discovery, repository access, and verification commands. Delegation also needs
a supported worker lifecycle; Orca window placement depends on the installed launcher's capabilities.
[agent-runtime.md](skills/my-workflow/references/agent-runtime.md) defines those checks and unattended permission
setup. Additional hosts belong in the adapter references; this README describes the shared contract.

Keep equivalent server names across hosts when practical, and keep credentials in each host's supported
environment-variable or OAuth mechanism. Shared skills may declare a dependency, but they do not own or copy
credentials. Models and reasoning effort remain host settings; shared workflow text uses capability classes and
inherits the active session configuration.

`my-workflow` is the routing entry point when the user describes an end-to-end job. Individual skills remain
available when the desired stage is already known. Skill bodies use the current user request as input and do not
depend on legacy prompt placeholder expansion.

`my-advisory`, `my-debug`, `my-refine`, `my-spec`, and `my-triage` are explicit-only. Their shared frontmatter
expresses this for hosts that support it; each skill's `agents/openai.yaml` carries the Codex policy.
The router preserves this boundary on every host.
`my-workflow` may recommend these entries but does not enter them implicitly. Explicit `my-loop` invocation
includes its documented `my-spec` stage chain; an implicit match does not.

## Lifecycle

- **`my-loop`** — inventory resources, resolve costly unknowns in a PoC, then coordinate specs through PRs and issue closure.
- **`my-triage`** — investigate a report that cannot be reproduced locally through a resumable evidence ledger.
- **`my-debug`** — diagnose a confirmed local bug and write a local fix artifact.
- **`my-spec`** — create a tracked feature/bug proposal from a request or GitHub issue.
- **`my-plan`** — turn a spec into a tracer-bullet task DAG and test plan.
- **`my-build`** — implement the task list with TDD, one commit per task; `team` uses the portable team lane.
- **`my-ship`** — run final validation, reconcile docs, tidy history, and prepare the PR.
- **`my-advisory`** — add embargo, severity, release, credit, CVE, and publication discipline around the bug lane.
- **`my-handoff`** — transfer ownership to another Orca window/worktree and stop.
- **`my-crew`** — supervise Orca workers or coordinate a read-only review subagent.
- **`my-refine`** — audit and prune this prompt/skill family itself.

Alongside the lifecycle, `skills/` also carries standalone skills that no stage owns — `auto-research`,
`crawl4ai-search`, `crosscheck`, and `address-pr-review` — plus the distilled skills below and whatever a
tool such as Orca or GitNexus installs into the shared root.

The shared references under [`skills/my-workflow/references/`](skills/my-workflow/references/) hold reusable policy. In
particular, `agent-runtime.md` separates host-native subagents from Orca coordination and defines the Orca-host
signals, `multi-window.md` selects a communication carrier, and `model-routing.md` keeps model selection
portable across vendors. `prompt-hygiene.md` keeps reusable prefixes stable, removes legacy prompt patches, and
calibrates effort against evidence.

## Multi-agent boundary

Use the smallest coordination surface that preserves the required state:

- Same-session, bounded exploration/review/test work → the current host's native subagents.
- Adversarial review → `crosscheck` gates it; `my-crew` dispatches through Orca when hosted, otherwise through
  the current host's native read-only subagent.
- Supervised workers, a Task DAG, cross-agent coordination, ask/reply, or completion tracking → Orca
  `orchestration`.
- Full ownership transfer to another window/worktree → Orca `orca-cli` handoff.
- Sequential implementation → stay in the current agent.

Once a surface is chosen, the carrier depends on the peer. Two Claude windows may use Claude's own attributed
cross-session message; every other pairing goes through Orca, which is also the only lifecycle record whatever
carried the message. Substantial context always travels as a file, with the message carrying its path. See
`skills/my-workflow/references/multi-window.md`.

Orca owns all Run/Task/Dispatch provenance. A workflow must load `orca skills get orchestration` or
`orca skills get orca-cli` before issuing Orca commands, so command syntax remains matched to the installed
runtime rather than copied into these skills.

The workflow never hard-codes provider model names, aliases, or vendor-specific switch commands. It inherits the
current model and, only when justified, recommends a portable capability class: `fast`,
`balanced`, or `strongest`. Where the host caches prompt prefixes, it also avoids changing model or effort in
the middle of a live session unless the current capability is insufficient.

## Catalog

The shared `my-*` lifecycle works without these integrations. Install only the capability you need; an absent
optional integration must degrade to the current host's built-in tools.

| Integration | Install when you need | Configured in |
| --- | --- | --- |
| [DeepWiki MCP](https://mcp.deepwiki.com/) | repository documentation lookup | each MCP host |
| [GitHub MCP](https://github.com/github/github-mcp-server) | issues, pull requests, and GitHub code search | each MCP host |
| [anysearch MCP](https://www.anysearch.com) | web search and page extraction for agents | each MCP host |
| [GitNexus](https://github.com/abhigyanpatwari/GitNexus) | code-graph exploration and impact analysis | CLI plus each MCP host |
| [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp) | a browser bridge for `browser-testing`, in an instance it owns | each MCP host that has no bridge of its own |
| [crawl4ai](https://github.com/unclecode/crawl4ai) | clean Markdown extraction and rendered screenshots | local machine |
| [Orca](https://github.com/stablyai/orca) | worktrees, handoffs, or supervised multi-agent runs | local machine plus shared skills |

Browser bridges differ across hosts, so `browser-testing` resolves the available bridge at run time. Use a
built-in browser tool or an installed bridge such as Chrome DevTools MCP. A host with no browser tool or
bridge cannot verify a UI through a live browser.

### MCP servers

MCP registration is deliberately host-owned. The examples below configure two clients globally; adapt the
server name and transport using your host's supported configuration. See
[host-adapters.md](skills/my-workflow/references/host-adapters.md) for client-specific paths.

DeepWiki provides documentation lookup for public GitHub repositories:

```bash
# Claude Code
claude mcp add --scope user --transport http deepwiki https://mcp.deepwiki.com/mcp

# Codex
codex mcp add deepwiki --url https://mcp.deepwiki.com/mcp
```

The official GitHub MCP endpoint requires authentication. This minimal cross-host setup uses a personal access
token; keep it outside this repository and grant only the scopes you need:

```bash
export GITHUB_PAT_TOKEN="replace-with-your-token"

# Claude Code
claude mcp add --scope user --transport http github https://api.githubcopilot.com/mcp/ \
  --header "Authorization: Bearer ${GITHUB_PAT_TOKEN}"

# Codex reads the token from the environment when it starts the server
codex mcp add github --url https://api.githubcopilot.com/mcp/ \
  --bearer-token-env-var GITHUB_PAT_TOKEN
```

anysearch gives the agent web search and page extraction. It authenticates the same way; get a key from
[anysearch.com](https://www.anysearch.com):

```bash
export ANYSEARCH_API_KEY="replace-with-your-key"

# Claude Code
claude mcp add --scope user --transport http anysearch https://api.anysearch.com/mcp \
  --header "Authorization: Bearer ${ANYSEARCH_API_KEY}"

# Codex
codex mcp add anysearch --url https://api.anysearch.com/mcp \
  --bearer-token-env-var ANYSEARCH_API_KEY
```

GitNexus can detect supported hosts and write their MCP entries. Run `analyze` once in each project that should
have a code graph:

```bash
npm install -g gitnexus@latest
gitnexus setup
gitnexus analyze
```

### Distilled skills

Six skills the `my-*` family routes into are distilled from other people's repositories rather than written
from scratch: `api-and-interface-design`, `browser-testing`, `debugging-and-error-recovery`,
`documentation-and-adrs`, `frontend-ui-engineering`, and `interview-me`. The review doctrine in
`skills/my-workflow/references/` is distilled from three.

Distilled, not vendored. Each file was rewritten to carry what its routing site actually needs, which is a
fraction of the upstream text: 143 KB of source became 21 KB, and the descriptions every session loads
whether or not the skill runs went from 3.5 KB to 0.6 KB. Several merge more than one upstream.

Every derived file names its upstream in a line under its title, and `CREDITS.md` records which commit each
upstream was read at and what came from where. All three upstreams are MIT, as is this repository.

The cost of distilling is drift: a fork stops tracking the day it is written. `my-refine sync` is the
counterweight — it compares each derived file against its upstream at the recorded commit, reports what
moved, and changes nothing. Re-distilling is a deliberate, separate run.

### Local helpers

Install crawl4ai for the tracked `crawl4ai-search` skill:

```bash
uv pip install crawl4ai --system
crawl4ai-setup
crawl4ai-doctor
```

Install Orca, then put its two coordination skills only in the shared discovery root. `--agent universal` avoids
creating redundant per-host copies:

```bash
brew install --cask stablyai/orca/orca
orca skills install --skill orca-cli --skill orchestration --agent universal
orca skills installed --json
```

The installed `orca-cli` and `orchestration` skills are discovery stubs. Their full guides come from the
installed binary at execution time, which keeps command syntax matched to the local Orca version.

### Kimi Code helpers

**`statusline-kimi.sh`** is a custom footer status line: model, a context-usage bar, the
account's 5-hour and 7-day quota percentages, the working directory, and the git branch. Kimi's
status-line snapshot carries no quota fields, so the script polls `GET <base_url>/usages` with the
OAuth token from `~/.kimi-code/credentials/kimi-code.json` in a detached background job at most once
a minute and renders only from `~/.kimi-code/cache/statusline-usage.json`, keeping the foreground
path well under the 300 ms the TUI allows. It requires `jq` and `curl`, and `~/.kimi-code/tui.toml`
must point at the link:

```toml
[status_line]
command = "~/.kimi-code/statusline.sh"
```

## Validation

After changing a skill:

```bash
python3 skills/my-workflow/scripts/validate_shared_skills.py
```

The shared validator checks the `my-*` frontmatter schema, accepts the
`disable-model-invocation` extension and verifies its equivalent Codex `agents/openai.yaml` policy, and
rejects any `namespace:name` plugin reference — the form that resolves on one host and silently breaks on
the others — and rejects retired bridge-plugin references. It also holds four things in agreement that drift
apart quietly: every tracked skill is routed into from somewhere, the `.gitignore` allowlist matches the
skills on disk and pairs each directory with its `/**` companion, every distilled file and `CREDITS.md` name
each other, and no tracked document carries an emoji. Use Codex's `quick_validate.py` directly for
standard-only skills.

There is deliberately no check that a backticked name resolves to a skill. Measured against this repository
it flags twenty-five ordinary terms for each real miss, and a gate that noisy gets switched off — which is
worse than no gate, because the bar still looks like it is there.

The validator cannot tell you whether a change to the review doctrine made reviews better. For that, run the
fixture eval in `skills/my-workflow/evals/review-doctrine/`, which grades a known diff on both recall and
silence about its decoys.

Still verify by hand:

- every `SKILL.md` has a unique lowercase `name` and a discriminating `description`;
- every referenced local file exists;
- no shared workflow contains legacy prompt placeholders, stale command paths, or concrete model names;
- every configured host discovers one copy of each `my-*` skill from its normal skill catalog.

This repository's `.gitignore` denies everything and allowlists what it tracks, so a plain `grep -r` run through
an ignore-aware wrapper will silently skip `README.md` and other untracked files. Use `command grep` when
checking that a pattern is truly absent.

## License

MIT. Parts of this repository are distilled from other MIT-licensed work; `CREDITS.md` records which files,
which upstreams, and which commits.
