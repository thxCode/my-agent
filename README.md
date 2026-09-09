# My Agent Workflow

Personal, reusable engineering workflows for Claude Code, Codex, and Kimi Code. Clone this repository directly
to `~/.agents`; it is the canonical source for shared instructions, skills, and role contracts.

## Shared layout

```text
~/.agents/                    # this Git repository
├── AGENTS.md                 # shared global instructions
├── skills/                   # Codex and Kimi discover this directly
│   ├── my-workflow/          # natural-language router and shared references
│   ├── my-spec/              # one workflow stage per skill
│   ├── my-plan/
│   ├── my-build/
│   └── ...
└── agents/                   # Claude-native adapters to shared role contracts

~/.claude/CLAUDE.md -> ~/.agents/AGENTS.md
~/.claude/skills    -> ~/.agents/skills
~/.claude/agents    -> ~/.agents/agents
~/.codex/AGENTS.md  -> ~/.agents/AGENTS.md
```

Kimi reads `~/.agents/AGENTS.md` and `~/.agents/skills` directly. Codex reads the shared skills directly but
needs its global `AGENTS.md` link. Claude needs the three links shown above. Do not create per-skill links under
`~/.codex/skills` or `~/.kimi-code/skills`.

## Install or update

For a fresh install:

```bash
git clone https://github.com/thxCode/my-agent.git ~/.agents
ln -s ../.agents/AGENTS.md ~/.claude/CLAUDE.md
ln -s ../.agents/skills ~/.claude/skills
ln -s ../.agents/agents ~/.claude/agents
ln -s ../.agents/AGENTS.md ~/.codex/AGENTS.md
```

Kimi needs no link. Update all three hosts with one pull:

```bash
git -C ~/.agents pull --ff-only
```

## Host-owned settings

Keep the workflow portable, but do not symlink whole client configuration files. Their model, permission, hook,
and MCP schemas differ:

| Host | User MCP configuration | Tool-definition loading |
| --- | --- | --- |
| Claude Code | user-scoped MCP state plus project `.mcp.json` | Tool Search defers MCP tools by default; use `alwaysLoad` only for a small always-needed server |
| Codex | `~/.codex/config.toml` | no per-tool `defer_loading`; use server enablement and tool allow/deny lists |
| Kimi Code | `~/.kimi-code/mcp.json` | no per-tool `defer_loading`; use server enablement and tool allow/deny lists |

Keep equivalent server names across hosts when practical, and keep credentials in each host's supported
environment-variable or OAuth mechanism. Shared skills may declare a dependency, but they do not own or copy
credentials. Models and reasoning effort remain host settings; shared workflow text uses capability classes and
inherits the active session configuration.

## Invocation

| Host | Explicit invocation | Implicit selection for non-restricted skills |
| --- | --- | --- |
| Claude Code | `/my-spec …` | Natural-language matching |
| Codex | `$my-spec …` | Natural-language matching |
| Kimi Code | `/skill:my-spec …` | Natural-language matching |

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

The shared references under [`skills/my-workflow/references/`](skills/my-workflow/references/) hold reusable policy. In
particular, `agent-runtime.md` separates host-native subagents from Orca coordination, and `model-routing.md`
keeps model selection portable across vendors. `prompt-hygiene.md` keeps reusable prefixes stable, removes
legacy prompt patches, and calibrates effort against evidence.

## Multi-agent boundary

Use the smallest coordination surface that preserves the required state:

- Same-session, bounded exploration/review/test work → the current host's native subagents.
- Supervised workers, a Task DAG, cross-agent coordination, ask/reply, or completion tracking → Orca
  `orchestration`.
- Full ownership transfer to another window/worktree → Orca `orca-cli` handoff.
- Sequential implementation → stay in the current agent.

Orca owns all Run/Task/Dispatch provenance. A workflow must load `orca skills get orchestration` or
`orca skills get orca-cli` before issuing Orca commands, so command syntax remains matched to the installed
runtime rather than copied into these skills.

The workflow never hard-codes provider model names, aliases, or vendor-specific switch commands. It inherits the
current model and, only when justified, recommends a portable capability class: `fast`,
`balanced`, or `strongest`. Where the host caches prompt prefixes, it also avoids changing model or effort in
the middle of a live session unless the current capability is insufficient.

## Optional integrations

The shared `my-*` lifecycle works without these integrations. Install only the capability you need; an absent
optional integration must degrade to the current host's built-in tools.

| Integration | Install when you need | Configuration owner |
| --- | --- | --- |
| [DeepWiki MCP](https://mcp.deepwiki.com/) | repository documentation lookup | each MCP host |
| [GitHub MCP](https://github.com/github/github-mcp-server) | issues, pull requests, and GitHub code search | each MCP host |
| [GitNexus](https://github.com/abhigyanpatwari/GitNexus) | code-graph exploration and impact analysis | CLI plus each MCP host |
| `agent-skills` plugin | Addy Osmani's additional Claude skills | Claude Code only |
| Codex or Kimi plugin | call another provider from inside Claude | Claude Code only |
| [crawl4ai](https://github.com/unclecode/crawl4ai) | clean Markdown extraction and rendered screenshots | local machine |
| [Orca](https://github.com/stablyai/orca) | worktrees, handoffs, or supervised multi-agent runs | local machine plus shared skills |

### MCP servers

MCP registration is deliberately host-owned. The examples below configure Claude or Codex globally; in Kimi,
open `/mcp-config` and add the same server name and transport to `~/.kimi-code/mcp.json`.

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

GitNexus can detect supported hosts and write their MCP entries. Run `analyze` once in each project that should
have a code graph:

```bash
npm install -g gitnexus@latest
gitnexus setup
gitnexus analyze
```

### Claude Code plugins

These plugins extend Claude Code only. Codex and Kimi do not need their corresponding Claude bridge plugin to
use the shared skills directly.

Install Addy Osmani's extra skill collection:

```bash
claude plugin marketplace add addyosmani/agent-skills
claude plugin install agent-skills@addy-agent-skills
```

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

The shared validator accepts the Claude/Kimi `disable-model-invocation` extension and verifies its equivalent
Codex `agents/openai.yaml` policy. Use Codex's `quick_validate.py` directly for standard-only skills.

Also verify:

- every `SKILL.md` has a unique lowercase `name` and a discriminating `description`;
- every referenced local file exists;
- no shared workflow contains legacy prompt placeholders, stale command paths, or concrete model names;
- Claude, Codex, and Kimi each discover one copy of every `my-*` skill from their normal skill catalog.

## License

MIT
