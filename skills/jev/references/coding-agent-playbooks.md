# Three Coding-Agent Playbooks (System 1 + System 2)

Derived from TypeSafe AI's published System One + System Two coding-agent architecture: let **Jev** execute
high-frequency, millisecond decisions (routing, bulk pre-screening, checklist verification) and reserve the
**System Two coding agent** for deep reasoning, planning, and code generation.

## Playbook 1 — Pre-Execution Routing (Save Tokens & Latency)

### 1a. Dynamic Capability Tier Routing

Instead of running every prompt on the most expensive flagship model, evaluate the prompt with `jev_cli.py route` and
map the result onto the portable capability classes defined in
`~/.agents/skills/my-workflow/references/model-routing.md`:

| `recommended_capability_class` | Complexity Score | Typical Tasks | Action in Coding Agent |
| --- | --- | --- | --- |
| `fast` | `< 0.8` | Locate a file path, convert text/JSON format, inspect function parameters, run a bounded test or mechanical edit | Dispatch a `fast` subagent/worker (`fast-worker` / `test-worker`) or keep reasoning effort minimal |
| `balanced` | `0.8 – 2.0` | Implement a scoped feature, write unit tests, fix a localized bug, review a standard diff | Use the session's default `balanced` model and standard effort |
| `strongest` | `> 2.0` or `confidence < 0.5` | Cross-package redesign, concurrency/race debugging, security/auth/billing changes, schema migrations | Escalate to the `strongest` capability class or higher reasoning effort |

**Prompt cache discipline:** Respect `model-routing.md`. Do not switch the primary session's model mid-turn if
doing so invalidates the host's prompt cache. Apply the tier selection when spawning subagents/workers, or at natural
session boundaries.

### 1b. Two-Stage Skill & Tool Selection

When `~/.agents/skills` holds dozens or hundreds of skills, scanning every file wastes thousands of tokens and slows
down startup.

1. Run `python3 ~/.agents/skills/jev/scripts/jev_cli.py route --prompt "<user request>" --skills-dir ~/.agents/skills`.
2. Jev evaluates the skill descriptions in a single `Choice` call (up to 255 skills per `Choice`). When the
   catalog is larger, split `--skills-dir` into subsets and merge the results by probability.
3. Load only the top 1 to 3 returned `SKILL.md` files whose probability clears `--min-skill-prob`.

## Playbook 2 — Bulk Data Classification, Scoring & Triage

**Golden rule:** Whenever a task asks the **same question(s)** across many items (comments, leads, tickets, posts,
logs, or transcript chunks), **forbid the System Two LLM from iterating over raw items**.

### Standard 4-Step Pipeline

1. **Extract items to `.jsonl` or `.csv`:** Have the coding agent write a small parser or query that dumps raw items
   to disk (for example, `.claude/jev/input.jsonl`).
2. **Design atomic questions (`questions.json`):**
   - Multi-class routing (e.g., 5 comment categories or 6 department queues) -> `choice` with an `other` fallback.
   - Multi-condition filtering (e.g., `is_decision_maker` AND `is_in_us`) -> separate `noul` questions per condition.
   - Graded risk or highlight ranking (e.g., member churn risk or short-video clip virality) -> `score` with 3 to 5
     situational levels, or multiple `score` dimensions combined via Composite Scoring.
3. **Run `jev_cli.py batch`:**
   ```bash
   python3 ~/.agents/skills/jev/scripts/jev_cli.py batch \
     --input .claude/jev/input.jsonl \
     --questions-file .claude/jev/questions.json \
     --out .claude/jev/output.jsonl \
     --sort-by highlight_score --top-k 15
   ```
4. **System Two handles only the essence:** The coding agent reads the compact JSON digest and only the top-K records
   (or records with low confidence requiring human/LLM adjudication) to generate the final CSV/Excel report, dashboard,
   or tailored outreach.

### Worked Decomposition — Long Video / Transcript Highlight Extraction

To extract top short-form clips from a 1-hour transcript without human fatigue:
1. Split the transcript by semantic boundaries into 100–300 candidate segments in `segments.jsonl`.
2. Evaluate every segment in parallel with three atomic `Score` questions (`standalone_clarity`, `counter_intuitive_insight`,
   `emotional_or_practical_punch`) and one `Noul` exclusion gate (`depends_on_missing_prior_context`).
3. Compute composite score in code: `(0.4 * clarity + 0.4 * insight + 0.2 * punch) * (1 - missing_context)`.
4. Surface the top 10 segments for cross-checking against the creator's manual picks.

## Playbook 3 — Post-Code Automated Verification & Feedback Loop

### 3a. Plain-English Semantic Linter

AST linters struggle with semantic conventions. Define project-specific plain-English rules in `.claude/jev/lint-rules.json`
and run `jev_cli.py review-diff --rules-file .claude/jev/lint-rules.json`:

```json
{
  "function_name_matches_side_effects": {
    "type": "noul",
    "instructions": "Does `diff` define or modify a function whose name omits a side effect it performs (such as mutating arguments, writing to disk, or making a network call)?"
  },
  "raw_error_leaked_to_client": {
    "type": "noul",
    "instructions": "Does `diff` return an internal stack trace, raw database error, or unredacted upstream error string directly in an HTTP or RPC response?"
  }
}
```

### 3b. Codebase-Wide Comment & Code-Smell Sweep

To audit a legacy repository for stale/misleading comments, dead code, duplicate blocks, or magic numbers:
1. Extract candidate `{id, file, line, comment, surrounding_code}` objects into `.claude/jev/comments.jsonl`.
2. Run `jev_cli.py batch` with two `Noul` questions:
   - `is_redundant_noise`: `"Does comment merely restate what surrounding_code trivially says without adding why or constraints?"`
   - `contradicts_code`: `"Does comment describe behavior, parameters, or return values that no longer match surrounding_code?"`
3. Filter to records where `is_redundant_noise > 0.8` or `contradicts_code > 0.7`, then dispatch a `fast-worker` to
   update or remove only those flagged lines.

### 3c. 100-Question PR Checklist Review (Speculative Fan-Out)

Before opening a PR or completing `my-build` / `my-ship`:
1. Run `python3 ~/.agents/skills/jev/scripts/jev_cli.py review-diff --git-diff HEAD`.
2. Jev evaluates the entire checklist in one ~100 ms call.
3. If `flagged_for_system2_review` is empty, proceed. If specific checks fire, the coding agent inspects only those
   exact failure modes in the diff and fixes them before final verification.

### 3d. System Two Calibrating System One

Whenever Jev misclassifies an edge case during verification or batch triage:
1. Inspect the exact `state`, `probabilities`, and `confidence` of the misclassified item.
2. Have the coding agent refine the question: split compound conditions into separate `Noul` questions, add `what` /
   `not_for` / `examples` objects to `criteria`, or adjust the numeric threshold in code.
3. Re-run `jev_cli.py` on the validation sample until accuracy stabilizes.
