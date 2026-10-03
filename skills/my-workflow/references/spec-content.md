# Spec content and references

Shared by `my-spec`, `my-plan`, and `my-loop`. Apply to both versioned and local-only specs. The local
reference boundary also applies to plans, docs, and code comments written into the target repository.
Program-local records (`STANDARD.md`, `STATUS.md`, `HISTORY.md`, `HANDOFF.md`, `HANDBACK`, and `SUMMARY.md`)
may cite program paths.

## Content contract

A spec must be self-contained, internally consistent, and complete for its current stage. Include the
requirements, decisions, assumptions, evidence, acceptance criteria, risks, and open questions needed to
assess it without program records or another worktree. Preserve placeholders explicitly assigned to a later
stage; record unresolved questions rather than inventing answers.

- Local citations must resolve within the target repository's committed tree. Use relative links; disk or
  Git index existence is insufficient. Absolute host paths and symlinks leading outside the repository do
  not qualify.
- NEVER cite off-repo or never-committed local evidence by link or path, including plain text or inline code.
  Other repo readers cannot resolve program reports, `.claude/reports/`, `evidence/`, `poc/`, or worktree
  scratch that exists only locally. An unexplained artifact or ledger ID is not a substitute.
- Copy or distill necessary content into the spec's relevant section or appendix. Describe the source in
  words; preserve the conditions, results, limitations, and uncertainty needed to assess the claim. Copying
  a summary that still depends on an unavailable appendix, figure, or report does not satisfy this rule.
- Keep local dependencies of cited or copied content in the committed repository too, recursively, including
  documents, images, and attachments. If one is unavailable, inline the necessary content and remove that
  dependency; do not leave a broken reference or silently drop supporting evidence.
- Public external sources may be cited by URL, pinning the version or commit when the claim depends on it.
  Include the essential facts in the spec; links supplement its explanation.
- Write every field per [writing-style.md](writing-style.md) (80% ASD-STE100): short sentences, one idea
  each, active voice.

## Audit

1. Read the whole spec, including appendices, link definitions, images, and plain-text or inline-code
   citations. Distinguish evidence citations from proposed implementation paths and commands.
2. Resolve every local citation from its containing document's directory. Verify its target and content in
   the committed tree, for example `git -C <repo> cat-file -e HEAD:<repo-relative-path>` and
   `git -C <repo> show HEAD:<repo-relative-path>`; check section anchors and symlink destinations too.
3. Follow local references in cited documents and copied content recursively, visiting each target once to
   handle cycles. Inline necessary off-repo content, repair its dependent references, and repeat until all
   remaining local dependencies resolve in the committed repository.
4. Compare requirements, decisions, assumptions, acceptance criteria, and the current stage's plan and tests.
   Reconcile contradictions and missing supporting facts; keep unresolved decisions and limits explicit.
   Confirm a reader can assess the spec without following program-local pointers.
