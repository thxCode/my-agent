# My Agent Workflow

Personal, reusable engineering workflows for Claude Code, Codex, and Kimi Code. The canonical assets live here;
`~/.agents/skills` points to [`skills/`](skills), which all three agents can discover.

## Shared layout

```text
~/.claude/
├── skills/                 # canonical cross-agent skills
│   ├── my-workflow/        # natural-language router
│   │   └── references/     # shared decision, runtime, and artifact contracts
│   ├── my-spec/            # one workflow stage per skill
│   ├── my-plan/
│   ├── my-build/
│   └── ...
└── agents/                 # optional Claude-native role adapters

~/.agents/skills -> ~/.claude/skills
```

Do not create per-skill links under `~/.codex/skills` or `~/.kimi-code/skills`. Codex and Kimi both scan
`~/.agents/skills`; Claude sees the canonical `~/.claude/skills` directory directly.

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

- [GitNexus](https://github.com/abhigyanpatwari/GitNexus) for code graph exploration and impact analysis.
- [Orca](https://github.com/stablyai/orca) for cross-window agents, worktrees, and structured orchestration.
- [crawl4ai](https://github.com/unclecode/crawl4ai) for clean Markdown extraction and rendered screenshots.
- Provider-specific Claude plugins may still supply read-only cross-check integrations, but shared workflow
  skills never assume they exist.

Install Orca's shared skills for the agents you use, then keep `~/.agents/skills` as the common discovery root.
The local `orca-cli` and `orchestration` skills are discovery stubs; their full guides come from the installed
binary at execution time.

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
