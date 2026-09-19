# Integration contracts

How `crawl4ai-search` plugs into the other tools in this setup. Each caller adds a small routing rule; the contracts
live here so the callers stay terse.

## With `auto-research` (retrieval)

In the **fan-out search** step, a research worker that has a promising URL should prefer crawl4ai over `WebFetch` when
the page is **JavaScript-rendered, content-dense, or WebFetch returned noisy/empty content**:

```bash
crwl <url> -o md-fit -O <scratch>/<slug>.md          # or add: -f templates/filter_bm25.yml (set query:)
```

Then extract the cited evidence from the saved file and return it as a finding (worker still **returns** data; the
orchestrator owns state). Keep `WebSearch` for discovering links and **DeepWiki MCP** for software-ecosystem questions.

Why it fits auto-research's cost governor: crwl does HTML→markdown **locally**, so the fetch spends **no Claude API
budget** — only the distilled `md-fit` the worker reads counts. It is a token/cost reducer, not an addition.

Do **not** use `-q` / LLM extraction here by default — they need a configured LLM provider and add cost. Stick to the
deterministic, free `md-fit` + BM25 path.

In the observability digest, the `fetched:` line should note which sources came via `crwl` (vs `WebFetch`).

## With `my-build` / `my-plan` / `my-spec` (frontend + grounding)

Routing rule for frontend/UI work:

| Need | Tool |
| --- | --- |
| Confirm a render / responsive viewports / a component shot | **`crawl4ai-search`** (`scripts/screenshot.py`) |
| Interactive debugging — clicks, console, network, form fills | `browser-testing` |
| Build/iterate the UI itself (components, layout, state) | `frontend-ui-engineering` |

For a spec that documents existing UI, a screenshot of the current screen is good grounding evidence. For external
facts/prior art, `my-spec` already routes to `auto-research` — which now fetches via crwl per the contract above.

## Token rules (apply everywhere)

- Output to a file (`-O` / `--out` / `--md`); read selectively (grep / offset), never dump a whole page into context.
- Prefer `md-fit` over raw `markdown`; with a query, add a BM25 filter.
- Reference screenshot PNG paths; only read the image back when you actually need to look at it.

## LLM-provider note

`-q`, LLM extraction (`extract_with_llm` path / `templates/extract_llm.yml`), and `generate_schema.py` call an external
LLM via crawl4ai (`~/.crawl4ai/global.yml`, any LiteLLM provider; `ollama/*` needs no token). They are **optional** and
off the default path. Everything load-bearing here — `md-fit`, BM25/pruning filters, screenshots, `extract_with_schema`
— is **no-LLM** and works out of the box.
