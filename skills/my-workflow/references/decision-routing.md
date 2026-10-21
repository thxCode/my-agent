# Jev decisions in the workflow

Apply `jev` at bounded classification and screening steps. Call it before resolving those steps in the lead's context.
Keep architecture, root-cause confirmation, code, and prose generation with the lead.

## Check boundaries first

- Honor explicit skill, tool, model, and review choices. A recommendation cannot override them.
- Keep explicit-only skill entry rules. Jev ranking a skill does not authorize entering it.
- Check disclosure restrictions before sending any request, including routing prompts and diff checks.
  Under `my-advisory`'s embargo, disable Jev throughout the run and its downstream skills.
- Use Git, tests, parsers, and runtime queries for exact facts. Jev does not verify signoff, permissions, task dependencies,
  worker completion, or CI results. User-reserved decisions stay with the user.

## Call at the decision

Read `~/.agents/skills/jev/SKILL.md` on first use. Inspect mode without changing configuration:

```bash
python3 ~/.agents/skills/jev/scripts/jev_cli.py mode status
```

If `enabled` is false, use the existing workflow without automatic Jev calls. Respect the relevant `positions` switch too:
`route` for routing and single classification, `batch` for repeated classification, `review_diff` for semantic diff checks.
The CLI's `eval` and `batch` commands do not enforce these switches; check them before calling either command.
If mode inspection fails, fall back to the lead rather than assuming permission to call.

| Stage | Bounded decisions to send to Jev |
| --- | --- |
| `my-workflow` | Select an entry lane and relevant skills from the existing catalog. |
| `my-spec` | Classify Feature versus Bug fix after gathering context; select supporting skills. |
| `my-plan` | Screen compatibility and reliability risks; suggest review gates from the existing rubric. |
| `my-build` | Select supporting skills; classify routine versus heavy review; screen the actual task diff. |
| `my-ship` | Screen stale docs, ADR need, and commit-fold candidates; screen the actual branch or changed-scope diff. |
| `my-debug`, `my-triage` | Rank collected hypotheses and classify evidence gaps. The lead confirms the cause and verdict. |
| `my-loop` | Classify candidate work and rank priorities within the charter. |
| `my-crew`, `my-handoff` | Classify task and role candidates. The user chooses the agent and placement. |
| `my-refine` | Screen conflict and pruning candidates. Verify both source citations before accepting a finding. |
| `my-advisory` | Screen public report categories and evidence gaps only after checking disclosure boundaries. |
| `crosscheck` | Classify uncertain novelty, complexity, or risk against its existing spend gate. |

For an unresolved lane or skill choice, use the existing router:

```bash
python3 ~/.agents/skills/jev/scripts/jev_cli.py route \
  --prompt "<bounded routing question and relevant facts>" --skills-dir ~/.agents/skills
```

For a known set of options, use `choice` questions with explicit criteria and a `needs_lead` option.
Use `score` for rubric ranking and `noul` for independent yes/no checks. Send focused evidence, not the whole conversation.
Combine independent questions about the same evidence into one `eval` request. Use `batch` for repeated questions across records.

```bash
python3 ~/.agents/skills/jev/scripts/jev_cli.py eval \
  --state-file "<scratch>/state.json" --questions-file "<scratch>/questions.json"
```

Keep input and result files in the host's scratch directory, outside tracked files and single-artifact workflow boundaries.
Use files for structured questions rather than long inline JSON arguments.

For example, give a review-gate question the raw evidence and `crosscheck`'s existing trigger list in `state`:

```json
{
  "review_gate": {
    "type": "choice",
    "instructions": "Classify `evidence` against `review_triggers`. Missing facts require needs_lead.",
    "criteria": {
      "run": "The evidence establishes at least one review trigger.",
      "skip": "The evidence establishes local, well-patterned, reversible work with no review trigger.",
      "needs_lead": "Evidence is missing, conflicting, or insufficient to choose run or skip."
    }
  }
}
```

## Consume results

- Adopt a `choice` only when `confidence >= 0.8` and the answer belongs to the offered set.
  `needs_lead`, missing fields, or lower confidence return the decision to the lead.
- Apply the same confidence floor to rubric scores. For `noul`, use `abs(2 * noul - 1) >= 0.8`.
- If the API fails or times out, note the fallback and continue with the existing rules. Do not add a retry loop.
- Cache the decision with its stage, question, and evidence revision in the current workflow context.
  Reuse it while the evidence is unchanged. Carry it through an existing checkpoint when needed; do not create a second ledger.
- A confirmed review trigger or explicit review request bypasses classification. Jev cannot cancel that review.
- Jev cannot grant approval, switch the session model, or choose the user's reviewer. Capability suggestions follow `model-routing.md`.

## Semantic diff screening

In `my-build`, screen the task diff before committing. In `my-ship`, screen the frozen branch diff before finalization.
If later changes alter the reviewed evidence, screen only the changed scope again. Reuse a build result for an unchanged ship scope.

Export the intended non-empty diff to a scratch file, then call:

```bash
python3 ~/.agents/skills/jev/scripts/jev_cli.py review-diff --diff-file "<scratch>/scope.diff"
```

Use the task's working-copy diff or `git diff <base>...HEAD`, as appropriate. Do not use `HEAD` after committing as a branch review.
Verify the base and diff before calling; an empty diff is a skip, not a passed review.
Inspect flagged checks against source. They are candidates, not established defects or permission to apply fixes.
An empty findings list does not replace tests, self-review, or required independent review.
