# Host adapters — installation and discovery

The shared workflows use capabilities rather than a fixed host list. This reference holds client-specific
installation and discovery details; update it when adding a host. Permission setup for workers belongs in
[agent-runtime.md](agent-runtime.md).

## Existing host links

```text
~/.claude/CLAUDE.md             -> ~/.agents/AGENTS.md
~/.claude/skills                -> ~/.agents/skills
~/.claude/agents                -> ~/.agents/agents
~/.claude/statusline.sh         -> ~/.agents/statusline-claude.sh
~/.codex/AGENTS.md              -> ~/.agents/AGENTS.md
~/.omp/agent/AGENTS.md          -> ~/.agents/AGENTS.md
~/.minimax/AGENTS.md            -> ~/.agents/AGENTS.md
~/.kimi-code/statusline.sh      -> ~/.agents/statusline-kimi.sh
~/.qwen/skills                  -> ~/.agents/skills
```

Kimi reads `~/.agents/AGENTS.md` and `~/.agents/skills` directly; its only link is the status line
script above. Codex and OMP read the shared skills directly but need their global `AGENTS.md` links. Claude
needs the four links shown above. Qwen discovers skills only under `.qwen/skills`, so it needs that root linked.
Do not create per-skill links under `~/.codex/skills` or `~/.kimi-code/skills`.

`AGENTS.md` is the canonical shared instruction file. Global loading depends on the host's supported paths;
Qwen's project-only boundary is described below.

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

## Install the links

Link each host to the shared root. Claude and Qwen need links, Codex, OMP, and mcode need one each for their
instructions files, and Kimi needs one for its status line script:

Install [OMP](https://github.com/can1357/oh-my-pi) before creating its link, for example with
`brew install can1357/tap/omp`; its user configuration directory must exist. OMP discovers
`~/.agents/skills` directly through its agents skill provider.

```bash
ln -s ../.agents/AGENTS.md             ~/.claude/CLAUDE.md
ln -s ../.agents/skills                ~/.claude/skills
ln -s ../.agents/agents                ~/.claude/agents
ln -s ../.agents/statusline-claude.sh  ~/.claude/statusline.sh
ln -s ../.agents/AGENTS.md             ~/.codex/AGENTS.md
ln -s ../../.agents/AGENTS.md          ~/.omp/agent/AGENTS.md
ln -s ../.agents/AGENTS.md             ~/.minimax/AGENTS.md
ln -s ../.agents/statusline-kimi.sh    ~/.kimi-code/statusline.sh
ln -s ../.agents/skills                ~/.qwen/skills
```

The status line link is required whenever Claude's `settings.json` points `statusLine` at
`~/.claude/statusline.sh`; without it the status line silently fails. Kimi's link is
likewise required by the `[status_line]` command in `tui.toml`; see
[Kimi Code helpers](../../../README.md#kimi-code-helpers).

`~/.qwen/skills` may already exist as a real directory holding links from other tools. Move what you still
want out of it first — `ln -s` will not replace a populated directory, and forcing it would drop those
links.

## Invocation and MCP

Keep the workflow portable, but do not symlink whole client configuration files. Their model, permission, hook,
and MCP schemas differ:

| Host | Explicit invocation | User MCP configuration | Tool-definition loading |
| --- | --- | --- | --- |
| [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) | `/my-spec …` | user-scoped MCP state plus project `.mcp.json` | Tool Search defers MCP tools by default; use `alwaysLoad` only for a small always-needed server |
| [Codex](https://github.com/openai/codex) | `$my-spec …` | `~/.codex/config.toml` | no per-tool `defer_loading`; use server enablement and tool allow/deny lists |
| [Kimi Code](https://code.kimi.com) | `/skill:my-spec …` | `~/.kimi-code/mcp.json` | no per-tool `defer_loading`; use server enablement and tool allow/deny lists |
| [Qwen Code](https://github.com/QwenLM/qwen-code) | `/my-spec …` | `~/.qwen/settings.json`, under `mcpServers` | no per-tool `defer_loading`; HTTP servers use `httpUrl`, not `url` |
| [OMP](https://github.com/can1357/oh-my-pi) | `/skill:my-spec …` | `~/.omp/agent/mcp.json` | built-in tools and skills; use OMP's own configuration |
| [MiniMax Code](https://agent.minimax.cn/docs/cli/quick-start) | `/my-spec …` or `/skills` | inspect `/mcp` and `/doctor` for the active runtime | use the current runtime's exposed tools and skills |

Qwen's global instructions file
is not linked above: its documented context filename is `QWEN.md`, but the path it reads at user scope is not
confirmed here, so Qwen currently picks up `AGENTS.md` only per project.

Keep equivalent server names across hosts when practical, and keep credentials in each host's supported
environment-variable or OAuth mechanism. Shared skills may declare a dependency, but they do not own or copy
credentials. Models and reasoning effort remain host settings; shared workflow text uses capability classes and
inherits the active session configuration.

## MiniMax Code (`mcode`)

MiniMax Code discovers `~/.agents/skills` through its external `user-agents` source when that source is enabled.
No per-skill copy is needed. It also scans compatibility roots such as `~/.claude/skills`, so check `/skills`
for duplicate or missing entries before relying on discovery. Use `/doctor` to inspect configuration and
`/status` to inspect the active workspace, permissions, and instruction-file sources.

Invoke an installed skill with `/my-spec …` or select it through `/skills`. Keep the shared workflow's
explicit-only routing rules even when a host does not enforce `disable-model-invocation` frontmatter.

Project instructions use the workspace's `AGENTS.md`. Global instructions use `<data-dir>/AGENTS.md`;
the default data directory is `~/.minimax`, overridable with `MINIMAX_DATA_DIR`. Create that directory if
needed, then use the `~/.minimax/AGENTS.md` link above; with a custom data directory, put the link there
instead. If an instruction file already exists, reconcile its contents before replacing it. Verify the
loaded sources in `/status`. Client settings and credentials remain in the host's own data directory rather
than being linked to another client's configuration. Inspect MCP entries through `/mcp`.

For unattended TUI workers, follow **Prepare unattended workers** in [agent-runtime.md](agent-runtime.md):
Full access is enabled inside the running TUI, before task delivery. Headless `mcode exec` has a separate
permission option.

Sources: [CLI configuration](https://agent.minimax.cn/docs/cli/configuration),
[CLI security](https://agent.minimax.cn/docs/cli/security). External shared-root discovery, global instruction
loading, and slash skill invocation are also present in the installed CLI package; recheck its catalog and
instruction sources when upgrading.
