# My Agent Workflow

Personal, reusable engineering workflows for Claude Code, Codex, Kimi Code, and Qwen Code. Clone this
repository directly to `~/.agents`; it is the canonical source for shared instructions, skills, and role
contracts.

## Shared layout

```text
~/.agents/                    # this Git repository
├── AGENTS.md                 # shared global instructions
├── CREDITS.md                # upstreams the distilled skills came from
├── skills/                   # Codex and Kimi discover this directly
│   ├── my-workflow/          # natural-language router and shared references
│   ├── my-spec/              # one workflow stage per skill
│   ├── my-plan/
│   ├── my-build/
│   ├── ...
│   └── interview-me/         # distilled from upstream, see Distilled skills
└── agents/                   # Claude-native adapters to shared role contracts

~/.claude/CLAUDE.md             -> ~/.agents/AGENTS.md
~/.claude/skills                -> ~/.agents/skills
~/.claude/agents                -> ~/.agents/agents
~/.claude/statusline-command.sh -> ~/.agents/statusline-command.sh
~/.codex/AGENTS.md              -> ~/.agents/AGENTS.md
~/.qwen/skills                  -> ~/.agents/skills
```

Kimi reads `~/.agents/AGENTS.md` and `~/.agents/skills` directly. Codex reads the shared skills directly but
needs its global `AGENTS.md` link. Claude needs the four links shown above. Qwen discovers skills only under
`.qwen/skills`, so it needs that root linked. Do not create per-skill links under `~/.codex/skills` or
`~/.kimi-code/skills`.

`AGENTS.md` is the only copy of the shared instructions, and every host above reads that one file.

Claude Code reads `AGENTS.md` natively from v2.1.277, but **at project scope only** — a repository's own
`AGENTS.md`, not a user-level one. There is no `~/.claude/AGENTS.md`, so the `~/.claude/CLAUDE.md` link in
the install step is still what carries these rules into every session, and it is not made redundant by the
native support. Its `instructionFiles` setting, reachable from `/config`, decides the rest: by default a
project with no `CLAUDE.md` of its own gets its `AGENTS.md` instead, and the other modes read both, read
neither, or keep only an organization's managed file.

One consequence lands on this repository specifically. Opening a session here now also picks up
`~/.agents/AGENTS.md` as *project* instructions, because this is a repository with an `AGENTS.md` and no
`CLAUDE.md`. That is the same file the user-level link points at, and Claude skips an `AGENTS.md` it has
already loaded through a link, so the content arrives once.

Do not add a `CLAUDE.md` here. It would duplicate rules the global link already loads, the two copies would
drift, and under the default setting it would also displace this repository's own `AGENTS.md` at project
scope.

## Install

1. **Clone.** The repository is self-contained; there is nothing to fetch afterwards.

   ```bash
   git clone https://github.com/thxCode/my-agent.git ~/.agents
   ```

2. **Link each host to the shared root.** Only Claude and Qwen need links; Codex needs one for its
   instructions file:

   ```bash
   ln -s ../.agents/AGENTS.md             ~/.claude/CLAUDE.md
   ln -s ../.agents/skills                ~/.claude/skills
   ln -s ../.agents/agents                ~/.claude/agents
   ln -s ../.agents/statusline-command.sh ~/.claude/statusline-command.sh
   ln -s ../.agents/AGENTS.md             ~/.codex/AGENTS.md
   ln -s ../.agents/skills                ~/.qwen/skills
   ```

   The status line link is required whenever Claude's `settings.json` points `statusLine` at
   `~/.claude/statusline-command.sh`; without it the status line silently fails.

   `~/.qwen/skills` may already exist as a real directory holding links from other tools. Move what you still
   want out of it first — `ln -s` will not replace a populated directory, and forcing it would drop those
   links.

3. **Verify discovery.** Each host should list one copy of every `my-*` skill in its own skill catalog, and
   `python3 ~/.agents/skills/my-workflow/scripts/validate_shared_skills.py` should print `ok` for each.

## Update

One pull updates every host, because every host reads the same working tree:

```bash
git -C ~/.agents pull --ff-only
```

To find out whether a distilled skill has fallen behind the repository it came from, run `my-refine sync`;
it reports upstream drift and changes nothing.

## Hosts

Keep the workflow portable, but do not symlink whole client configuration files. Their model, permission, hook,
and MCP schemas differ:

| Host | Explicit invocation | User MCP configuration | Tool-definition loading |
| --- | --- | --- | --- |
| [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) | `/my-spec …` | user-scoped MCP state plus project `.mcp.json` | Tool Search defers MCP tools by default; use `alwaysLoad` only for a small always-needed server |
| [Codex](https://github.com/openai/codex) | `$my-spec …` | `~/.codex/config.toml` | no per-tool `defer_loading`; use server enablement and tool allow/deny lists |
| [Kimi Code](https://code.kimi.com) | `/skill:my-spec …` | `~/.kimi-code/mcp.json` | no per-tool `defer_loading`; use server enablement and tool allow/deny lists |
| [Qwen Code](https://github.com/QwenLM/qwen-code) | `/my-spec …` | `~/.qwen/settings.json`, under `mcpServers` | no per-tool `defer_loading`; HTTP servers use `httpUrl`, not `url` |

Every host selects non-restricted skills by natural-language matching as well. Qwen's global instructions file
is not linked above: its documented context filename is `QWEN.md`, but the path it reads at user scope is not
confirmed here, so Qwen currently picks up `AGENTS.md` only per project.

Keep equivalent server names across hosts when practical, and keep credentials in each host's supported
environment-variable or OAuth mechanism. Shared skills may declare a dependency, but they do not own or copy
credentials. Models and reasoning effort remain host settings; shared workflow text uses capability classes and
inherits the active session configuration.

`my-workflow` is the routing entry point when the user describes an end-to-end job. Individual skills remain
available when the desired stage is already known. Skill bodies use the current user request as input and do not
depend on legacy prompt placeholder expansion.

`my-advisory`, `my-debug`, `my-refine`, `my-spec`, and `my-triage` are explicit-only. Their shared frontmatter
enforces this in Claude and Kimi; each skill's `agents/openai.yaml` expresses the equivalent Codex policy.
`my-workflow` may recommend these entries but does not enter them implicitly.

## Lifecycle

- **`my-triage`** — investigate a report that cannot be reproduced locally through a resumable evidence ledger.
- **`my-debug`** — diagnose a confirmed local bug and write a local fix artifact.
- **`my-spec`** — create a tracked feature/bug proposal from a request or GitHub issue.
- **`my-plan`** — turn a spec into a tracer-bullet task DAG and test plan.
- **`my-build`** — implement the task list with TDD, one commit per task; `team` uses the portable team lane.
- **`my-ship`** — run final validation, reconcile docs, tidy history, and prepare the PR.
- **`my-advisory`** — add embargo, severity, release, credit, CVE, and publication discipline around the bug lane.
- **`my-handoff`** — transfer ownership to another Orca window/worktree and stop.
- **`my-crew`** — supervise an Orca Run/Task/Dispatch lifecycle until all workers settle.
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
| [codex-plugin-cc](https://github.com/openai/codex-plugin-cc) | call Codex from inside Claude | Claude Code only |
| [kimi-code-plugin-cc](https://github.com/thxCode/kimi-code-plugin-cc) | call Kimi from inside Claude | Claude Code only |
| [crawl4ai](https://github.com/unclecode/crawl4ai) | clean Markdown extraction and rendered screenshots | local machine |
| [Orca](https://github.com/stablyai/orca) | worktrees, handoffs, or supervised multi-agent runs | local machine plus shared skills |

Browser bridges are the one row where the hosts genuinely diverge, so `browser-testing` resolves the bridge
at run time instead of naming one. Claude and Codex reach a browser through the Chrome DevTools MCP server
above, which drives an instance it launches and owns. Kimi ships its own extension bridge instead, and that
one drives the user's real browser under their live logins — the same verbs, a completely different blast
radius. A host with no bridge cannot verify a UI at all, and the skill is written to say so rather than
substitute a static fetch.

### MCP servers

MCP registration is deliberately host-owned. The examples below configure Claude or Codex globally. In Kimi,
open `/mcp-config` and add the same server name and transport to `~/.kimi-code/mcp.json`. In Qwen, add it under
`mcpServers` in `~/.qwen/settings.json`, where an HTTP server's endpoint key is `httpUrl`.

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

An earlier arrangement installed the upstream Claude plugin instead. Over three months it injected roughly
8.6 KB of skill descriptions into every Claude and Codex session and was invoked zero times, partly because
the routes into it named a plugin namespace that only resolved on one of the four hosts.

### Claude Code plugins

These plugins extend Claude Code only. Codex, Kimi, and Qwen do not need a bridge plugin to use the shared
skills directly.

Install the Codex bridge when Claude should ask Codex for an optional cross-check:

```bash
claude plugin marketplace add openai/codex-plugin-cc
claude plugin install codex@openai-codex
```

Then run `/codex:setup` inside Claude to verify the Codex CLI and login.

Install the Kimi bridge when Claude should ask Kimi for an optional cross-check:

```bash
claude plugin marketplace add thxcode/kimi-code-plugin-cc
claude plugin install kimi@moonshotai-kimi
```

The Kimi bridge also needs the Kimi CLI: install it with
`curl -fsSL https://code.kimi.com/kimi-code/install.sh | bash`, run `kimi login`, then run `/kimi:setup` inside
Claude. See [thxCode/kimi-code-plugin-cc](https://github.com/thxCode/kimi-code-plugin-cc) for provider setup.

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

## Validation

After changing a skill:

```bash
python3 skills/my-workflow/scripts/validate_shared_skills.py
```

The shared validator checks the `my-*` frontmatter schema, accepts the Claude/Kimi
`disable-model-invocation` extension and verifies its equivalent Codex `agents/openai.yaml` policy, and
rejects any `namespace:name` plugin reference — the form that resolves on one host and silently breaks on
the other three. It also holds four things in agreement that drift apart quietly: every tracked skill is
routed into from somewhere, the `.gitignore` allowlist matches the skills on disk and pairs each directory
with its `/**` companion, every distilled file and `CREDITS.md` name each other, and no tracked document
carries an emoji. Use Codex's `quick_validate.py` directly for standard-only skills.

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
- Claude, Codex, Kimi, and Qwen each discover one copy of every `my-*` skill from their normal skill catalog.

This repository's `.gitignore` denies everything and allowlists what it tracks, so a plain `grep -r` run through
an ignore-aware wrapper will silently skip `README.md` and other untracked files. Use `command grep` when
checking that a pattern is truly absent.

## License

MIT. Parts of this repository are distilled from other MIT-licensed work; `CREDITS.md` records which files,
which upstreams, and which commits.
