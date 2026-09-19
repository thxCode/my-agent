# Credits

Parts of this repository are distilled from other people's work. None of it is vendored wholesale: each
file below was rewritten for this repository's routing, hosts, and typography, and several merge more than
one source. This file is the attribution a dependency would otherwise have carried.

All three upstreams are MIT, as is this repository, so the permission notice travels with the copyright
line reproduced in each section.

Every derived file carries its own provenance in a line under its title, naming the upstream it came from.
The commit each upstream was read at is recorded once here, per upstream, so a sync updates one line rather
than seven. `my-refine`'s sync pass joins the two; `validate_shared_skills.py` checks they agree.

## addyosmani/agent-skills

<https://github.com/addyosmani/agent-skills> — MIT, `Copyright (c) 2025 Addy Osmani`

Read at `c004a74784a08295d52749b04cda634125b9a581` (0.6.10).

| Derived file | Upstream source |
| --- | --- |
| `skills/api-and-interface-design/SKILL.md` | `skills/api-and-interface-design/SKILL.md` |
| `skills/browser-testing/SKILL.md` | `skills/browser-testing-with-devtools/SKILL.md` |
| `skills/debugging-and-error-recovery/SKILL.md` | `skills/debugging-and-error-recovery/SKILL.md` |
| `skills/documentation-and-adrs/SKILL.md` | `skills/documentation-and-adrs/SKILL.md` |
| `skills/frontend-ui-engineering/SKILL.md` | `skills/frontend-ui-engineering/SKILL.md` |
| `skills/interview-me/SKILL.md` | `skills/interview-me/SKILL.md` and `skills/idea-refine/SKILL.md` |
| `skills/my-workflow/references/review-doctrine.md` | `skills/code-review-and-quality/`, `skills/code-simplification/`, `skills/doubt-driven-development/` |

The review doctrine takes the severity-by-leverage ordering and the "propose the move" requirement from
`code-review-and-quality`, the behaviour-preservation and project-convention rules from
`code-simplification`, and the finding triage that treats a reviewer's output as data rather than verdict
from `doubt-driven-development`, including its checkable signal for a review that has stopped finding
anything.

## mattpocock/skills

<https://github.com/mattpocock/skills> — MIT, `Copyright (c) 2026 Matt Pocock`

Read at `c55ee46073ed923f86ce59a5eb3b6d895095d1b7`.

| Derived file | Upstream source |
| --- | --- |
| `skills/my-workflow/references/skill-craft.md` | `skills/productivity/writing-great-skills/` |
| `skills/my-workflow/references/smells.md` | `skills/engineering/code-review/SKILL.md` |
| `skills/my-workflow/references/roles/spec-reviewer.md` | `skills/engineering/code-review/SKILL.md` |
| `skills/my-workflow/references/review-doctrine.md` | `skills/engineering/code-review/`, `skills/in-progress/retro/` |
| `skills/debugging-and-error-recovery/SKILL.md` | `skills/engineering/diagnosing-bugs/SKILL.md` |

The two-axis split this repository runs — Standards alongside Spec, in separate contexts, never merged or
re-ranked — is his, as is the smell baseline with its two binding rules, the per-reviewer output budget, and
the rule that a mechanical standard belongs in a linter rather than in a review. The debugging gate that
refuses to form a hypothesis before a failing command exists comes from `diagnosing-bugs`.

## DietrichGebert/ponytail

<https://github.com/DietrichGebert/ponytail> — MIT, `Copyright (c) 2026 DietrichGebert`

Read at `e3ba2aa6f1e6f0bc4d69eb09c9f0d0a93af56156`.

| Derived file | Upstream source |
| --- | --- |
| `skills/my-build/SKILL.md` (the decision ladder in Phase 3) | `skills/ponytail/SKILL.md` |
| `skills/my-workflow/references/review-doctrine.md` | `skills/ponytail-review/`, `skills/ponytail-debt/`, `skills/ponytail-gain/` |

The ladder that climbs from "does this need to exist" through the standard library and platform features
before writing anything is his. So is the finding grammar that will not accept a criticism without a named
replacement, the dignified null verdict that removes the pressure to manufacture findings, and the
`shortcut:` comment convention — renamed here, but the idea of making a deliberate ceiling greppable, and of
flagging the markers that name no trigger as the ones that rot, is `ponytail-debt`'s.

`ponytail-gain`'s honesty boundary is adopted as a rule rather than as text: a saving that has no measured
baseline does not get printed as a number.
