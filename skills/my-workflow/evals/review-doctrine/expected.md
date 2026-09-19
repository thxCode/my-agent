# Answer key — `fixture.diff`

Do not read this before running the review. It is the grader, not the brief.

## Planted, and the review must find all five

| # | Where | Tag | The defect |
| --- | --- | --- | --- |
| P1 | `merge_layers` | `bug:` | `range(1, len(layers))` starts at index 1, so the first layer is silently dropped. The docstring beside it says later layers win, which is what hides it: the result looks right whenever the first layer is empty |
| P2 | `dedupe` | `stdlib:` | A hand-rolled order-preserving dedupe. `list(dict.fromkeys(names))` is one line and the language already guarantees insertion order |
| P3 | `SettingsSource` / `FileSource` | `yagni:` | An abstract base class with exactly one implementation, introduced in the same diff, whose method only forwards to `load`. Inline both until a second source exists |
| P4 | `env_overrides` | `native:` | A new `dotenv` dependency to read environment variables, which `os.environ` on the next line already reads. It also mutates process-global state from what reads as a pure function, and resolves `.env` relative to the working directory |
| P5 | `load` | `bug:` | The missing-file default was added to the shared `load`, changing the contract for every pre-existing caller rather than only the new layering path. A mistyped required path now yields `{}` and the program runs on defaults instead of failing. Keep `load` strict; test for existence in `resolve`, which is the caller that wants it |

A finding counts only if it names the replacement. "This class may be unnecessary" does not settle P3;
"inline `FileSource`, the ABC has one implementation" does.

P5 was written as a decoy — a defensive check that looks like dead code — and the first run of this eval
disproved that. The finding is not "delete the guard", it is "right behaviour, wrong layer", and the blast
radius on existing callers is real. The key was wrong and was corrected; the review was not.

## Decoys, and the review must report none of them

| # | Where | Why reporting it is a failure |
| --- | --- | --- |
| D1 | `import sys`, unused | A context line. The change did not touch it, and it predates the diff; both are on the drop list |
| D2 | the `# noqa: E501` line in `env_overrides` | A rule the code explicitly silences, and a line-length rule a linter owns. Two separate reasons to drop it |
| D3 | the `shortcut:` comment in `resolve` | A deliberate ceiling carrying both its limit and its trigger. The doctrine defines that marker as a recorded decision; re-raising it as an efficiency finding means the convention was not applied |

D3 is the one that tests a rule nothing else here tests. Naming the re-read as a performance problem looks
productive and is exactly backwards: the author already declared it, with the condition under which it
stops being acceptable.

## Verdict

- All five planted defects named, each with a replacement: **pass**.
- Any decoy reported: **fail**, whatever else the review found. A pass earned by reporting everything is
  what the decoys exist to catch. Naming a decoy while explicitly dropping it in verification is not a
  report — that is the second stage working, and it should say so.
- Unplanted findings beyond the five: allowed, up to two, and each must carry a failure scenario. More than
  that means the verification pass is not filtering.

## Recorded runs

| Date | Result |
| --- | --- |
| First run, before P5 was reclassified | 4/4 planted found with replacements; 2/3 decoys clean; the third was a defect in this key |
