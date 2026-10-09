# Host adapters — instructions and skill discovery

The shared workflows use capabilities rather than a fixed host list. This reference holds client-specific
instruction paths, skill discovery, invocation syntax, and MCP configuration locations. Permission setup belongs in
[agent-runtime.md](agent-runtime.md).

## Existing host links

```text
~/.claude/CLAUDE.md             -> ~/.agents/AGENTS.md
~/.claude/skills                -> ~/.agents/skills
~/.claude/agents                -> ~/.agents/agents
~/.claude/statusline.sh         -> ~/.agents/statusline-claude.sh
~/.kimi-code/statusline.sh      -> ~/.agents/statusline-kimi.sh
~/.gemini/config/skills         -> ~/.agents/skills
```

`AGENTS.md` is the canonical shared instruction file. Global loading depends on the host's supported paths;
Qwen's project-only boundary is described below.

One consequence lands on this repository specifically. Opening a session here now also picks up
`~/.agents/AGENTS.md` as *project* instructions, because this is a repository with an `AGENTS.md`. That is the same file the user-level link points at, and Claude skips an `AGENTS.md` it has
already loaded through a link, so the content arrives once.

## Install the links

Link each host to the shared root. Claude and Qwen need links, Codex, OMP, mcode, and ZCode need one each for their
instructions files, and Kimi needs one for its status line script:

Install [OMP](https://github.com/can1357/oh-my-pi) before creating its link, for example with
`brew install can1357/tap/omp`; its user configuration directory must exist. OMP discovers
`~/.agents/skills` directly through its agents skill provider.

The status line link is required whenever Claude's `settings.json` points `statusLine` at
`~/.claude/statusline.sh`; without it the status line silently fails. Kimi's link is
likewise required by the `[status_line]` command in `tui.toml`; see
[Kimi Code helpers](../../../README.md#kimi-code-helpers).

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
| [ZCode](https://github.com/zai-org/ZCode) | `/skill my-spec …` or `/skill` | `~/.zcode/cli/config.json`, under `mcp.servers` | use the current runtime's exposed tools and skills |
| [Antigravity](https://antigravity.google) (`agy`) | `/my-spec …` | `~/.gemini/mcp_config.json` | progressive disclosure for skills and rules; built-in subagents and project `.agents/agents` |

Keep equivalent server names across hosts when practical, and keep credentials in each host's supported
environment-variable or OAuth mechanism. Shared skills may declare a dependency, but they do not own or copy
credentials. Models and reasoning effort remain host settings; shared workflow text uses capability classes and
inherits the active session configuration.

## Not in Orca Agents list

### MiniMax Code (`mcode`)

MiniMax Code discovers `~/.agents/skills` through its external `user-agents` source when that source is enabled.
It also scans compatibility roots such as `~/.claude/skills`; no per-skill copy is needed.

Invoke an installed skill with `/my-spec …` or select it through `/skills`. Keep the shared workflow's
explicit-only routing rules even when a host does not enforce `disable-model-invocation` frontmatter.

Project instructions use the workspace's `AGENTS.md`. Global instructions use `<data-dir>/AGENTS.md`;
the default data directory is `~/.minimax`, overridable with `MINIMAX_DATA_DIR`. Create that directory if
needed, then use the `~/.minimax/AGENTS.md` link above; with a custom data directory, put the link there instead.
Client settings and credentials remain in the host's own data directory. Inspect MCP entries through `/mcp`.

Source: [CLI configuration](https://agent.minimax.cn/docs/cli/configuration). External shared-root discovery, global instruction
loading, and slash skill invocation are also present in the installed CLI package; recheck its catalog and
instruction sources when upgrading.
