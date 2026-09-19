---
name: crawl4ai-search
description: >-
  Fetch web pages as clean Markdown (token-efficient, LLM-ready) and screenshot rendered UIs via the local
  crawl4ai (`crwl` CLI + Python SDK). Use when WebFetch returns noisy/empty content, for JavaScript-rendered
  pages / SPAs, when a research worker needs distilled page content, or when frontend work needs a rendered
  screenshot (a render check, responsive viewports, a component shot). Triggers on crawl4ai, crwl, fetch as
  markdown, scrape JS-heavy page / SPA, screenshot a page / UI / localhost, capture rendered page, md-fit,
  BM25 content filter, batch crawl, schema extraction. SKIP for a plain static page the agent only needs to
  read once (built-in WebFetch is faster, no ~2s browser tax), and for interactive debugging — clicks, console,
  network, form fills — which belongs to browser-testing.
---

# crawl4ai-search

Wraps the locally installed **crawl4ai** to do two jobs well: pull a page down as **clean Markdown** for an LLM to
read, and take a **screenshot** of a rendered page. Built around the `crwl` CLI (no Python needed for retrieval) plus a
small SDK script for screenshots (the CLI has no screenshot flag).

**Throughline — token discipline:** crawl4ai converts HTML→markdown **locally**, so the fetch itself costs no model
tokens; only what you read into context does. Always write output to a file and read selectively. Never pipe a whole
raw page into the conversation.

Verify install once: `crawl4ai-doctor`. CLI reference: [references/cli-guide.md](references/cli-guide.md). Integration
contracts (auto-research / my-*): [references/integration.md](references/integration.md).

---

## Job 1 — Fetch a page as Markdown (retrieval for LLMs)

Use instead of `WebFetch` when the page is **JavaScript-rendered**, content-dense, or WebFetch came back
noisy/empty. Default to a scratchpad file, then read what you need.

```bash
# default: filtered markdown to a file (do NOT print the whole thing back)
crwl <url> -o md-fit -O <scratch>/<slug>.md

# you have a specific question/topic → BM25-relevance filter keeps only what matters
#   first set `query:` in templates/filter_bm25.yml (or copy + edit it)
crwl <url> -f templates/filter_bm25.yml -o md-fit -O <scratch>/<slug>.md

# JavaScript-heavy / SPA — wait for the network to settle
crwl <url> -c "wait_until=networkidle,page_timeout=60000" -o md-fit -O <scratch>/<slug>.md
```

Then read selectively — `grep` for the section you need, or Read with an offset — rather than loading the whole file.

**Optional, needs an LLM provider configured** (`~/.crawl4ai/global.yml`; without it these fail — fall back to the
`md-fit` path above):

```bash
crwl <url> -q "<focused question>"      # crawl4ai answers from the page directly
crwl <url> -e templates/extract_llm.yml -o json   # LLM structured extraction (one-off)
```

`md-fit` vs `markdown`: `md-fit` is filtered (noise removed) — prefer it. Use raw `-o markdown` only when you truly
need the unfiltered page.

## Job 2 — Screenshot a rendered UI (static snapshot)

The `crwl` CLI has **no screenshot flag**; use the bundled SDK script. Good for: confirming a render, responsive
viewports, a specific component. Works against `http://localhost:<port>` dev servers.

```bash
scripts/screenshot.py <url> --out <scratch>/<name>.png                       # viewport shot (1280x800)
scripts/screenshot.py <url> --viewport 375x812 --full-page --out <scratch>/m.png   # mobile, full page
scripts/screenshot.py <url> --element ".pricing-card" --out <scratch>/card.png --md <scratch>/card.md
```

`--element` scrolls that selector into view and scopes the markdown — it is **not** a pixel-tight crop. Run
`scripts/screenshot.py -h` for all options.

**Boundary — do not reach past static rendering.** Anything interactive — clicking, typing, reading the console,
inspecting network requests, multi-step flows — is **not** this skill. Delegate to
**`browser-testing`**, which resolves whatever browser bridge this host has. crawl4ai gives you a
snapshot; a bridge gives you a live, inspectable session.

---

## When NOT to use this skill

- **Plain static page the agent just needs to read once** → built-in `WebFetch`. crawl4ai pays a ~2s browser
  cold-start tax; for static HTML it buys nothing.
- **Interactive frontend debugging** (DOM / console / network / clicks) → `browser-testing`.
- **Building/iterating a UI itself** (components, layout, state) → `frontend-ui-engineering`; come here
  only for the screenshot.

## Advanced (secondary)

- **Many URLs → markdown files:** `scripts/batch_crawl.py <urls.txt|url1,url2> --max-concurrent 5 --out <dir>`
- **Repeating structured data:** `scripts/generate_schema.py <url> "<what to extract>" schema.json` (one-time LLM)
  → `scripts/extract_with_schema.py <url> schema.json out.json` (no LLM, repeatable) — and
  `scripts/batch_extract.py <urls.txt> schema.json` across many URLs.

Templates for the above live in [`templates/`](templates/); CLI flag reference in
[references/cli-guide.md](references/cli-guide.md).

---

## Token rules (non-negotiable)

1. crwl output always goes to a file via `-O` (CLI) or `--out`/`--md` (screenshot script) — never straight to stdout
   into context for anything sizable.
2. Prefer `md-fit` over raw `markdown`; when you have a query, always add a BM25 filter.
3. Read the saved file **selectively** (grep / offset), not whole.
4. Screenshots are images — reference the PNG path; only read it back when you actually need to look.
