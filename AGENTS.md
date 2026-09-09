# AGENTS.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them; don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No flexibility or configurability that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:

- Don't improve adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it; don't delete it.

When your changes create orphans:

- Remove imports, variables, or functions that your changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:

- "Add validation" -> write tests for invalid inputs, then make them pass.
- "Fix the bug" -> write a test that reproduces it, then make it pass.
- "Refactor X" -> ensure tests pass before and after.

For multi-step tasks, state a brief plan:

```text
1. [Step] -> verify: [check]
2. [Step] -> verify: [check]
3. [Step] -> verify: [check]
```

Strong success criteria let you loop independently. Weak criteria such as "make it work" require clarification.

## 5. Verify the Instrument

**Read the criterion out of the thing under test, not out of your notes.**

- Did I read this predicate from the object, or write it myself?
- A check you just wrote is more suspect than the thing it checks.
- Errors clustering on one kind of input mean the check is wrong, not the target.
- Compare contents, not summaries; `diff --stat` cannot see a same-line edit.
- Feed a new gate an input it must reject; confirm it fails before trusting it.
- "Nothing bad is in the set" is vacuously true; it proves nothing.

The test: "Does this look reasonable?" passes for a wrong answer too, and "almost right" hides longest.

## 6. Durable Docs

**Put it where the next person will look. Say it plainly.**

- Emphasis is one capitalized word: `NEVER` `FORBIDDEN` `REQUIRED` `LIMITED` `ALLOWED` `SUGGESTED`.
- No emoji, invented compounds, or unexplained abbreviations.
- Keep a prohibition's reason beside it; the next person is editing code, not specs.
- Committed text carries no timestamps, IPs, hostnames, `user@host`, or cluster IDs.
- Describe infrastructure by shape and role, such as "a three-node Kubernetes cluster".

A rule without a gate is a wish. Confirm its scope; an ignore-aware search never sees ignored files.

## 7. Memory Last

**Route a lesson before you write it. The repo outranks memory.**

- Already in the repo (docs, an instruction file, or an overview skill)? Don't duplicate it.
- A rule that always applies goes in an always-loaded file, not in recalled memory.
- A fact about the code goes beside the code. If it can't, say why.
- Append to the entry that already covers the theme; don't mint a new file.
- Two entries that conflict: verify one, delete the other; both get recalled.
- Cap at 100 entries; measure the index in bytes (`wc -c`), not characters.
- Write it in the session's configured language; keep identifiers as they are.

The test: would an already-loaded file have answered this? Then it isn't memory.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication,
and clarifying questions come before implementation rather than after mistakes.
