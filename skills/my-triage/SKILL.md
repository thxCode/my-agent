---
name: my-triage
description: For the report you cannot reproduce — turn the issue thread into a diagnosis instrument, one probe per round over a resumable ledger, until it reaches a verdict. Not for ordinary issue sorting — labels, duplicates, priority, milestones.
disable-model-invocation: true
---

# my-triage

Triage the report: **the user's current request**

For the report you **cannot reproduce**. The failure lives on the reporter's hardware or cluster, the issue
thread is the only instrument you have, and every measurement costs a stranger's goodwill. Each round asks for
exactly one thing and can falsify exactly one hypothesis, over a ledger that outlives both the latency and the
session. It ends in a **verdict** — ours, someone else's, not a bug at all, or not diagnosable from here — which
is not the same as a fix, and every one of them is a win.

Ordinary triage — labels, duplicates, priority, milestones — is ordinary maintenance, and reading the thread is
enough for it. This instrument is heavy; reproduction failing is what earns its cost.

**Entry by certainty.** Don't know whether the report is real → `my-triage`; real and locally fixable →
`my-debug`; real or a new capability and worth tracking → `my-spec`. Pick the lane yourself — none of the
three routes into another on its own.

- **Language.** Write the ledger and every archived artifact in **English**; talk to the user in their
  configured language. `comment.md` splits: its **prose** mirrors the language the reporter used in the
  thread, while the script, its variable names, its output format and its verdict line stay English —
  `~/.agents/skills/my-workflow/references/probe-craft.md` § 8 has the rule and the reason.
- **Source lookup.** Read/trace source: **GitNexus** (if available) → **DeepWiki** → `grep`/`find`. This skill
  reads source to check a claim; it writes none.

**Boundaries.**

- **Everything this skill writes stays under the project's `.claude/`.** The ledger and its round archive live
  in `.claude/issues/`; a probe is content for the issue thread and a file in that archive, and the repo never
  gains one.
- **Every outward action is the user's.** A comment is posted only after they approve the exact text; closing an
  issue and filing upstream are printed for them to run. This skill never sends, closes, or files. **Fetching
  an attachment is an outward action too** — 4h shows the URL and asks before anything is pulled.
- **Never ask the reporter for a kubeconfig, a token, or a namespace this issue does not concern.** A probe is
  scoped by `-n <ns>` to the workload under discussion; anything wider is someone else's cluster.
- **Never promise a fix date.** Say what we will do with their answer and what ships on what guard — a date is
  a thing we do not know, offered to someone who will remember it.

## Phase 1 — Resolve the issue

Resolve `the user's current request` per `~/.agents/skills/my-workflow/references/resolve-issue.md` — it fixes `<owner>/<repo>` and
`<n>`. Its stop-rule fires at the first actual **read**, which is 2b's or 4h's and not this phase's: a resumed
run may never read the thread at all, and a deleted or transferred issue then surfaces at 4f's post.

Resolution is all this phase does. **Reading the thread is a branch, not a step**: Phase 2 decides whether this
run needs it.

## Phase 2 — Open or resume the ledger

Look for `.claude/issues/<n>-*.md` **before** touching the thread. Which of the two branches you land on is the
most consequential thing about this run.

### The namespace

In the **project's** `.claude/` (not `~/.claude/`), local and never staged:

```
.claude/issues/
  <n>-<title>.md          # the ledger — the single source of truth
  <n>/round-<k>/
    probe.sh              # what we asked them to run
    comment.md            # what we posted, verbatim
    output/               # what came back, raw — archived, never executed or sourced
    verdict.md            # what the round settled, and what it did not
    close.md | upstream.md  # a terminal round's draft (Phase 5) — printed for the user, never sent
    undiagnosable.md      # the honest-end comment (5b), posted through 4f
    upstream-link.md      # the filed issue's link, posted through 4f after the user files it
```

The **ledger's** namespace is deliberately not `.claude/debugs/`: that one is `my-build`'s **build-target**
namespace, and a `Status: Probing` ledger has no Fix Plan to build.

Nothing is paraphrased into the ledger without a pointer to the file it came from — **every Confirmed Fact cites
its `round-<k>/<file>`**.

### 2a · Resume — a ledger is already there

**The ledger is the memory; the thread is not.** Read the file and print, before anything else:

| Print | Why it is on the list |
| --- | --- |
| `Status:` · `Verdict:` · `Build:` | where the loop stands, and whether identity is pinned |
| **Confirmed Facts** | each with the `round-<k>/<file>` it cites |
| **Corroboration (unverified)** | held apart from the facts, so it stays unpromoted |
| **Ruled Out** | so a spent round is not spent twice |
| **Current Hypothesis** | what this round is trying to kill |
| **Next Probe** | what the previous session left drafted |

That print **is** the recovered state, and it is the whole of it. A re-read of the thread adds nothing to it: it
would spend a full context on days of comments to restate one file, and it is not how this skill remembers
anything. The thread is read again only for **what is new since our last post** — Phase 4's intake, which yields
new evidence, never recovered state.

**Resuming does not always add a round.** `<k>` is the highest row in the *Diagnosis Ledger*, and an empty table
means round 0 was never recorded. **That row's own `Sent:` and `Received:` decide where this run picks up** —
opening `<k+1>` while `<k>` is still outstanding asks the reporter a question they already have:

| Row `<k>` | This run resumes at | Because |
| --- | --- | --- |
| `Sent: —` | **4f**, with the drafted comment | it was written and never posted — post it, or leave it for the user |
| `Sent: <d>`, `Received: —` | **4h**, looking for a reply | the question is outstanding; a second ask would double it |
| `Received:` filled | **4a**, opening `<k+1>` | that round is closed, and the next hypothesis is due |

A second run never re-opens round 0, rewrites the header, or re-derives *Reported*.

A ledger carrying neither a `Verdict:` nor a drafted Next Probe is the one broken state — say so plainly, and let
the round that follows start by drafting one.

### 2b · Open — no ledger yet

1. Read the issue and every comment, via the read path in Phase 1's reference. This is the one run that reads the
   whole thread.
2. Create `.claude/issues/<n>-<title>.md` from the template below — `<title>` hyphenated from the issue title,
   issue-number prefix, no date.
3. Fill *Reported* from the thread **verbatim**: the reporter's environment and symptom in their words, not a
   paraphrase. Every other section is filled from evidence, and starts empty.

```markdown
# Triage: <Title>

Status: Probing
Verdict: —
Issue: <URL>
Reporter: <login>
Build: unknown — asked in round 0

## Reported
<The reporter's environment and symptom, verbatim from the thread.>

## Diagnosis Ledger

| # | Hypothesis | Probe | Refuted by | Sent | Received | Verdict |
|---|------------|-------|-----------|------|----------|---------|

## Confirmed Facts
<One per line, each citing the `round-<k>/<file>` that proves it.>

## Corroboration (unverified)
<What anyone other than `Reporter:` reported — held here, never in Confirmed Facts.>

## Ruled Out
<What the evidence killed, with its citation.>

## Current Hypothesis
<One, falsifiable.>

## Next Probe
<The one ask that opens the next round.>

## Verdict
<Empty until reached.>

## Reusable Probes
<Keeper probes, each with the failure shape it separates.>
```

The header lines carry fixed value sets:

| Header | Values |
| --- | --- |
| `Status:` | `Probing` · `Verifying` · `Closed` · `Stalled` — a new ledger opens at `Probing` |
| `Verdict:` | `bug-ours` · `bug-upstream` · `not-a-bug` · `undiagnosable` · `—` |
| `Issue:` | the issue URL |
| `Reporter:` | the login of the thread's author — one loop tracks one environment |
| `Build:` | the image digest once pinned, and exactly `unknown — asked in round 0` until then |

## Phase 3 — Round 0 pins identity

Round 0 buys what every later round is priced against: **which build is actually running**, on **what platform**,
and **the full log**. #130's line numbers matched a tag whose recover helper cannot produce the pasted log, so
the running build was not the one the report claimed — an excerpt would have hidden that, and later rounds would
have been reasoning about the wrong binary.

| Field | Pinned by |
| --- | --- |
| Build version | what the binary reports of itself (`--version`), not what the thread says it is |
| Image digest | the resolved digest (`imageID`), not the tag it was pulled by |
| Platform | OS, kernel, arch, and the vendor hardware the report names |
| Log | the **full** log of the failing container, attached — never an excerpt |

**Round 0 always verifies, and is always recorded. It is *posted* only if the thread leaves one of those four
unpinned.**

**The verification runs first, and it runs every time** — check the thread's claims against each other and
against the source at the tag they name. It costs the reporter nothing, since it reads only what they have
already written and what we already own, and it is what sharpens the ask: not *send us `--version`*, but *send
us `--version`, because the line numbers you pasted and the tag you named cannot both be right*.

The verification is a ledger entry in its own right. Write `round-0/verdict.md` — what was checked, the thread
comment it was checked against, and what it settled — so its findings cite an archived file like every other
round's, **whether or not the round posts**. A match and an inconsistency are both findings; an inconsistency is
the stronger one, and it becomes the next round's target.

| The thread | Then round 0 also | Its ledger row |
| --- | --- | --- |
| leaves a field unpinned | **posts**, asking for exactly the missing fields — draft it through Phase 4 | `Sent: —` at draft; 4f stamps the date only if the post returns |
| already carries the digest and the full log | **posts nothing** — the verification is the whole round | `Sent: —`, and what the verification settled as its verdict |

Round 0's row is drafted like every other round's: **`Sent:` stays `—` until 4f's post returns.** A row stamped
at drafting time claims a comment the reporter may never have received, and 5a's 14-day clock would then run
against a post that does not exist.

`Build:` leaves the template's `unknown — asked in round 0` only when a digest replaces it.

Round 0 is the one round with no hypothesis yet — only an identity to pin — so the one-hypothesis rule does not
bind it. What binds it is that any breadth rides along with something that can be wrong.

## Phase 4 — The round loop

Round `<k>`: one hypothesis, one probe, one comment, one reply. The reporter pays for it in time and goodwill,
so each step below has to earn the next one, and the round ends by asking whether a verdict is now reachable.

### 4a · The hypothesis, and the observation that refutes it

From round 1 on, **one** hypothesis and **one** probe. State the hypothesis so it can be wrong, then name the
observation that would kill it. If nothing the reporter could send back would change our mind, there is no
round here yet — go back and find a claim that can lose.

Prefer an **A/B**: the same command twice with exactly one variable changed, so the answer *discriminates*
rather than *describes*. A survey says what their node looks like; an A/B says which of two stories is true.

Write the round's row in the *Diagnosis Ledger* now, before the probe exists — the hypothesis, the probe in a
phrase, and **`Refuted by`: the observation that would kill it**, with `Sent:` and `Received:` still `—`. That
column is the refuting observation's one home, in the same table as the hypothesis it refutes; *Next Probe*
carries the ask, and the row carries what the ask is *for*.

**`Sent:` is stamped when the post returns — never at intake, and never at drafting.** The row then says where
the round stopped on its own, so a run that dies between the post and the reply resumes with round `<k>`
outstanding rather than recomputing `<k+1>` and re-sending what the reporter already has.

### 4b · Draft the probe

`~/.agents/skills/my-workflow/references/probe-craft.md` holds the probe: the template with its `say` / `run` / `kx` /
`priv` helpers (§ 1), the tool's-own-flag timeouts and their preflight (§ 2), the modes and the `--host-only`
degradation (§ 3), and the privilege rule (§ 4). Start from that template.

This round supplies only the middle of it: the A/B pair 4a named, and one `run` / `kx` per fact that hypothesis
needs. Breadth rides along; it never leads. Bump `PROBE_VERSION` to `<n>-r<k>`.

Before the template, run **5f's seed grep** — a previous loop on a same-shaped failure may already have the
script, and starting from it beats starting from the blank middle.

### 4c · The hygiene gate

Run § 5's twelve checks **before the comment is built**, so a probe that could not survive a stranger's terminal
never reaches one. Item 2, `bash -n`, is the hard gate.

**A probe that fails any item goes back to 4b, and the round does not advance** — an unbounded `kubectl` call
(item 5), a command that bypasses `run` and so reports its own failure as an empty result (item 4), a whole
credential-bearing file dumped where a `grep` would do (item 7). Items 8, 9 and 12 are *run*, not read: the
unprivileged path, the unreachable-cluster path and the script itself are exercised here, locally, before the
user sees anything.

**Item 12 is the one that earns its place.** A script can pass `bash -n` and `shellcheck` and still hang
forever on a flag given no value, or print a confident A/B verdict over two arms that both failed — neither
is visible to a static check, and both land on hardware we do not own.

`shellcheck` absent is the one item that may go unmet. Record `shellcheck: unavailable` in
`round-<k>/verdict.md` — the degradation is declared, never silently skipped. It does not go in the ledger
row: that table's seven columns have no home for it, and inventing an eighth breaks every later round.

### 4d · Build the comment

`comment.md`, to § 7's four sections in that order, bulleted; the worked example there is the shape. A round's
comment carries **both** the script in `<details>` and § 6's minimal ask — the cautious reporter who will not
run a bundle from a stranger is the one most likely to go quiet instead.

The comment is built from the ledger and is far smaller than it (§ 8): what their output settled, what we
suspect, what to run next. The mechanism walkthrough and the tag archaeology stay in the ledger and reach the
thread only if the reporter asks for them.

One rule joins the two registers: in *What we think is happening*, a cause may be tagged `confirmed` only if a
Confirmed Fact cites the archived file that shows it. Everything else is `suspected` — including whatever we are
personally certain of.

### 4e · No interference — the measurement, and nothing that masks it

A workaround, a restart or a config change applied before the probe runs masks the very thing the probe
measures. **A round carrying both is refused**, not quietly trimmed: say which half is the workaround, name the
no-interference rule (F6) as the reason, and rebuild the round around the measurement alone. The comment may
*say* a workaround exists and that it follows once the output lands — that costs the round nothing.

**The same change can be one arm of the A/B and forbidden as advice.** `GODEBUG=cgocheck=0` inside probe (B) is
the measurement. The same variable set on the DaemonSet before the run reaches probe (A) as well, stops it
panicking, and leaves an A/B that proves nothing. The test is not what the change is — it is whether it reaches
the environment the *other* arm runs in.

### 4f · Confirm, then post

Show the user the exact text and ask. Nothing has left the machine yet.

- **Approved** → post it, and not before:
  ```sh
  gh issue comment <n> --repo <owner>/<repo> --body-file .claude/issues/<n>/round-<k>/comment.md
  ```
  Stamp `Sent: <yyyy-mm-dd>` on the row as soon as the post returns.

  **A terminal post goes through this same gate, and names its own file** — `undiagnosable.md` or
  `upstream-link.md`, never `comment.md`, which holds the round's probe comment byte for byte. It does **not**
  re-stamp `Sent:`: that column tracks the round's one outstanding question, and a closing note asks nothing.
- **Declined** → **the file is written and nothing is sent.** The row keeps `Sent: —`, so the next run finds the
  round drafted and unposted rather than lost, and the user can post it by hand from that same file. Say so
  plainly: a decline is a complete, correct ending to the run, not a failure.

If the user edits the text, theirs is what gets posted and archived — `comment.md` is what was posted, never
what we drafted.

### 4g · Archive the round

This step writes three of `round-<k>/`'s entries (Phase 2's layout): `probe.sh` exactly as embedded in the
comment, `comment.md` byte for byte as posted, and `output/` created empty for 4h.

Archiving `probe.sh` is what makes the version stamp worth carrying: the copy on disk is the copy they were
given, so an output stamped `<n>-r<k-1>` is provably an old script re-run rather than a puzzle.

### 4h · Intake — the reply, read as evidence

Read the thread again, and only for **what is new since our last post**.

**What counts as a reply — both conditions, never either.** The author matches the pinned `Reporter:`, **and**
the timestamp is later than our post.

**Both conditions go in the query, not in your head.** Filtering after the fetch spends the whole thread's
tokens to keep two comments, every round — and 2a's reason for not re-reading the thread applies just as much
here.

```sh
gh issue view <n> --repo <owner>/<repo> --json comments --jq \
  '.comments[] | select(.author.login=="<reporter>" and .createdAt > "<the row Sent: timestamp>")'
```

Anyone else's "same here, we see it on the S5000 too" lands in *Corroboration (unverified)* and never in
*Confirmed Facts*, however credible it reads: one loop tracks one environment, and a second environment's
symptom cannot confirm this one's cause. It is a candidate for its own loop.

Nothing new → the row keeps `Received: —` and the round stays outstanding. That is still an answer: carry it to
the question this phase ends on, because **how long a round has been outstanding is an input there** — silence
is evidence about the loop even when it is not evidence about the bug.

**Waiting is never automated.** If the user asks to be reminded, offer the current host's reminder or recurring
task mechanism with a prompt to check issue `<n>`; never schedule it without their explicit request. The reminder
checks for a reply and reports it—it does not automatically run this outward-facing workflow or post anything.

**Archive first, read second — and the fetch is gated like the post.** Show the user the URL and ask, exactly as
4f does. A link in a public thread is a string a stranger chose, and pulling it is us reaching out to a host of
their choosing.

```sh
curl --proto '=https' --max-time 120 --max-filesize 50M -sS \
     -o .claude/issues/<n>/round-<k>/output/att-<i>.bin "<user-attachments URL>"
```

Three things in that line are load-bearing. **`--proto '=https'` with no `-L`**: a redirect is a stranger
re-pointing our request after we approved the destination, and it is how a public URL reaches an address inside
our own network. **The two limits**: the script we hand *them* bounds every call (§ 2), and bytes coming back
deserve the same. **`att-<i>.bin`, a name we generate**: the filename in the thread is theirs, and `../../` in
it walks straight out of `output/`. Record the original name and the URL in `verdict.md`.

Attachments are **archived, never executed or sourced** — a script that comes back from a thread is evidence,
not a program. Pasted output is written into `output/` as a file too, so that every fact has something to cite.
Then read `00-summary.txt` and `00-probe-version.txt`: a `PROBE_VERSION` other than `<n>-r<k>` means an earlier
copy ran, so the output answers an earlier round's question and is recorded against *that* round.

File what came back, **before anything is drafted in reply**:

| Lands in | What goes there |
| --- | --- |
| **Confirmed Facts** | what the archived output *shows*, each citing its `round-<k>/<file>` |
| **Corroboration (unverified)** | anything from anyone who is not `Reporter:` |
| **Ruled Out** | what the output killed, with the same citation |
| **Current Hypothesis** | what survived, or its replacement |

Two rules settle every hard case:

- **No Confirmed Fact exists that the archived output does not show.** An inference stays an inference, however
  short the step, and lives in *Current Hypothesis*.
- **An inconsistent output is itself a finding** — recorded with its citation, never asserted as a fact. "The
  binary reports `v0.5.4`, and the log line at `device.go:57` cannot come from that tag" is a finding about the
  *evidence*; "they are running a patched build" is the inference it supports, and only their `imageID` settles
  it.

Write `round-<k>/verdict.md`, stamp the row's `Received:` and `Verdict:`, then ask the question that ends a
round: **is a verdict now reachable?** → Phase 5.

## Phase 5 — Verdict, handoff and reuse

Every round leaves the ledger carrying **either a `Verdict:` or a drafted Next Probe**. Neither is the one broken
state Phase 2a names, and this phase is where it is prevented: reach a verdict here, or draft round `<k+1>`'s ask
before the run ends. A run that stops in the middle of this phase still has to have written one of the two.

### 5a · Is a verdict reachable?

Reachable when the *Confirmed Facts* — each citing its archived file — leave **one** story standing, and the
alternatives are in *Ruled Out* with their citations. Certainty that no citation carries is not a verdict; it is
a *Current Hypothesis*, and it buys another round.

Three things end the probing regardless of how promising round `<k>` looks:

| Signal | Read it as |
| --- | --- |
| **3 rounds without narrowing** — nothing new entered *Ruled Out* across them | the hypothesis space is wrong, not the probes. Stop drafting probes and challenge the space itself: re-read *Reported* and *Confirmed Facts* for the story nobody has written down yet. A fourth probe that discriminates between two false stories spends the reporter's goodwill on nothing. If the space really is exhausted, the exit is `undiagnosable` |
| **remote evidence cannot separate what remains** | `undiagnosable` — and name what would change it |
| **14 days of reporter silence** since the row's `Sent:` | `stalled` |

Otherwise: draft *Next Probe*, and the next run opens round `<k+1>` at 4a.

### 5b · The five exits

The header table (Phase 2b) carries the vocabulary; this one carries what each exit **means** and **drafts**, and
the `Status:` it moves the ledger to.

| Exit | It means | What it drafts, and where it lands |
| --- | --- | --- |
| `bug-ours` | the cause is locked, and it is in this repo | the `my-debug` artifact (5d) → `Status: Verifying` while 5e's offer stands, then `Closed` |
| `bug-upstream` | the cause is locked, and it belongs to an upstream project or the vendor | `round-<k>/upstream.md`, the upstream issue body, standing on its own evidence for readers who have never seen this thread; **prints** `gh issue create`. Once the user has filed it, the link goes back to the thread through 4f as `round-<k>/upstream-link.md` → `Closed` |
| `not-a-bug` | the evidence points at the reporter's configuration or usage | `round-<k>/close.md`, the explanation, held to **the same evidence chain a `bug-ours` needs** — every claim citing its archived file, and the fix they should apply; **prints** `gh issue close` → `Closed` |
| `undiagnosable` | remote evidence cannot separate the remaining hypotheses | `round-<k>/undiagnosable.md`, saying so plainly and naming the access or hardware that would settle it, posted through 4f — the loop's honest end, not its failure → `Closed` |
| `stalled` | the reporter has been silent 14 days since our last post | the **one exit that is a `Status:`, not a `Verdict:`** — `Verdict:` stays `—`, `Status: Stalled`, and *Next Probe* stays drafted, which is what keeps the invariant true and lets a reply months later resume round `<k>` |

Write the verdict into the ledger's *Verdict* section — the cause, the citations that carry it, and what it does
**not** claim — then move `Verdict:` and `Status:` in the header.

### 5c · The two outward actions are printed, never run

```sh
# print these for the user; this skill executes neither, ever
gh issue close <n> --repo <owner>/<repo> \
  --comment "$(cat .claude/issues/<n>/round-<k>/close.md)"    # close takes --comment, not --comment-file
gh issue create --repo <upstream-owner>/<upstream-repo> \
  --title "<title>" --body-file .claude/issues/<n>/round-<k>/upstream.md
```

**`gh issue close`, `gh issue create` and `gh issue transfer` are never executed by this skill — not on
approval, not on request, not as a convenience.** 4f's approve-then-post exists for `gh issue comment`; these
have no approved-and-then form, because closing a stranger's report and filing in someone else's tracker are
socially expensive to undo, happen once per loop, and cost one paste. Draft the file, print the command, stop.

### 5d · `bug-ours` — write the `my-debug` artifact

Handing off is an **ask-first** step. On approval, write
`.claude/debugs/<yyyy-mm-dd>-issue-<n>-<title>.md` (`date +%Y-%m-%d`; the ledger's `<title>`):

```markdown
# Debug: <Title>

Status: Diagnosed
Type: Bug fix

## Background
<The symptom, and the environment round 0 pinned: build, digest, platform, vendor hardware.>

## Reproduction / PoC
Not reproducible locally — remote evidence: .claude/issues/<n>-<title>.md, round-<k>/<file>

## Root Cause
<The cause in one or two sentences.> Derivation and evidence:
`.claude/issues/<n>-<title>.md` § Verdict, proved by `round-<k>/<file>`.

Local guard feasible: yes, via <mechanism>          # or: no — needs <hardware>

## Fix Plan
TODO

## Test Plan
TODO
```

**Two markers make this a handoff rather than an ordinary artifact: a filled *Root Cause* and the
`Local guard feasible:` line.** `my-debug`'s *Entry — root cause supplied* gates on exactly that pair and skips
its Phase 2; with either one missing it takes the ordinary path and asks for the local reproduction that, here,
does not exist. Emit both, in those words.

- **Referenced, not copied.** The ledger keeps the derivation — the rounds, the ruled-out, the citations. The
  artifact carries the statement and the pointer. Two files, one contract, and `my-build` gets the readable one.
- **`Local guard feasible:` asks what can fail *here*, on hardware we own** — a source-level assertion, a unit
  test over the boundary, a lint. #130's cgo boundary is guarded by asserting that no call hands the C library
  the address of a Go struct field: no S4000 needed, and that guard is what would have caught it at review.
  `no — needs <hardware>` is for when nothing local can be made to fail on this bug.

### 5e · The hardware confirmation round — offered either way, advisory either way

Offer it on `bug-ours` **whichever way the guard line went**, because the reporter's node answers what no guard
of ours can: whether anything *else* in that path fails once the panic is gone.

- **It never gates a merge.** `yes, via <mechanism>` → the fix ships on that guard while the offer is
  outstanding. `no — needs <hardware>` → the fix still ships, and `my-debug`'s Test Plan records the gap.
- `Status: Verifying` marks the ledger while the offer stands. Record the outcome — `confirmed` / `declined` /
  `no reply` — in the *Verdict* section, then `Status: Closed`.
- **A reporter who declines, or never answers, is a normal ending.** 5a's 14-day clock runs on outstanding
  *probes*, never on this offer: nothing is waiting on their answer, so silence closes the loop rather than
  stalling it.

### 5f · Reuse — the archive is the probe library

Nothing is promoted into the repo. Reuse runs through the archive, and it has two halves:

**Name the keepers.** A probe earns a line in *Reusable Probes* when **both** hold: it ran clean on the
reporter's environment, and its output *discriminated* — something entered *Ruled Out* or *Confirmed Facts*
because of it. A probe that ran clean and settled nothing is not a keeper. Write it with the **failure shape it
separates** — the two stories it tells apart and the observation that picks between them, in terms of the
failure, not of this issue:

```markdown
- `130/round-1/probe.sh` — cgo pointer-check panic vs. vendor library fault at device-manager init:
  A/B on `GODEBUG=cgocheck=0`; only the former stops panicking when it is set.
```

**Seed from them.** 4b starts a probe here, not at the template, when the archive already holds one of this
shape:

```sh
grep -rl "<failure-shape keyword>" .claude/issues/*/round-*/probe.sh
```

A hit is a starting point, not an answer: re-read it against *this* hypothesis, cut what does not bear on it,
and bump `PROBE_VERSION` to `<n>-r<k>` so the two runs stay distinguishable in the output header.
