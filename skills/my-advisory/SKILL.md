---
name: my-advisory
description: Handle a security advisory from report triage through coordinated disclosure and release.
disable-model-invocation: true
---

# my-advisory

Address the security report: **the user's current request**

A vulnerability report is an ordinary bug wearing a second job. The technical half is already covered, and this
skill runs it through `my-debug` → `my-build` → `my-ship` unchanged. What it **owns** is the other half: an
embargo that begins before the first line of code, and three clocks — credit acceptance, CVE assignment,
downstream upgrades — that run for days and gate a **Publish** button nobody can un-press.

**Why a skill and not a mode on `my-ship`.** The advisory is opened *before* code is written, which is
upstream of ship; and the embargo is read by three lanes, which is three hooks to maintain against one entry to
find. `my-spec` sets the precedent — name the artifact, be the entry to the chain.

- **Language.** Write the artifact, the advisory and every outward draft in **English**; talk to the user in
  their configured language.
- **Source lookup.** Read/trace source: **GitNexus** (if available) → **DeepWiki** → `grep`/`find`.

**Boundaries.**

- **Under embargo, nothing about the vulnerability leaves this machine.** Any external-provider cross-check
  sends the diff outside the embargo boundary, so `crosscheck` is **off** for every lane of the run — say so the
  first time a lane would have offered it, and stop offering it.
- **Confirm the exact text before it leaves the machine** — the advisory body, the branch name, the commit
  message, the PR title and body, the tag, the reporter email, the publish. This skill drafts, the user
  approves, then it runs.
- **The PoC is a working exploit.** It stays out of the repo, out of the test suite, and out of the advisory
  until publish. The artifact holding it is local and never staged.
- **Publish is irreversible and global.** It makes the CVE and the advisory public and fires Dependabot alerts
  on every consumer. It happens once Phase 7's checklist is fully checked, and only on the user's word.

## Phase 1 — Triage the report

Nothing is created and nothing is spent until three things are settled: whether the report is **real**, what it
is **worth**, and how the fix will **travel**. The reporter's severity is a claim like any other in the report,
and it is the one most often wrong.

### 1a · Resume — the artifact is the memory

A run waits on other people for days, so it resumes from disk and never from the conversation:

```sh
grep -l '^## Disclosure' .claude/debugs/*.md
```

A hit → read that file and print `Disclosure:`, `Route:`, `Advisory:`, `CVE:` and the **publish checklist**,
then pick up at the first unchecked box. That print **is** the recovered state. No hit → 1b.

### 1b · Validate the claim against the code (read-only)

`the user's current request` arrives in one of three shapes, and the shape settles 1d's classification:

| Shape | Read it with |
| --- | --- |
| `GHSA-xxxx-xxxx-xxxx`, or a GitHub advisory URL | `gh api /repos/<owner>/<repo>/security-advisories/<ghsa>` |
| a pasted report email | as given — it is the whole of what we have |
| a public issue number or URL | `~/.agents/skills/my-workflow/references/resolve-issue.md` |

Then:

- **Confirm the flaw at the path the report names**, and that the path is reachable on a **default**
  configuration. A flaw behind a non-default option is a different severity and a different conversation.
- **Read the siblings first.** An analogous path already carrying the guard makes this an *inconsistency* rather
  than a novel finding — and it hands you the fix, in the house style, already reviewed once.
- **Not a vulnerability, or not ours** → say so, draft the reply, stop. A dependency's flaw is a report to file
  upstream, not an advisory to open here.
- **Real, but it will not reproduce here** → the instrument is `my-triage`, with one change: under embargo its
  rounds run on the private channel, and the issue thread stays untouched.

### 1c · Score it yourself, then reconcile

The reporter's number is an input, not the finding. Score it independently before reading theirs again, and
score it **twice** — a library's severity belongs to its consumers, and one vector cannot hold two realities:

| Reading | Vector | The caller it describes |
| --- | --- | --- |
| trusted intake | `PR:L` | feeds it files it already owns |
| untrusted intake | `PR:N` | feeds it whatever arrives on a socket |

Then reconcile against what the reporter claimed:

- **We agree** → record both readings, and move on.
- **We score it lower** → say so, to them, with **the vector and the metric you differ on, not the adjective**.
  `AV:N` on input that only ever arrives as a local file, `C:H` on a flaw that costs availability alone, `PR:N`
  on an API a consumer has to choose to expose — those three inflate most. They will see our number at publish;
  a disagreement discovered *then* is a far worse conversation than this one.

The score is what the rest of this skill is priced against: whether a CVE is worth requesting, how tight the
release window has to be, and — with 1d — how the fix travels.

### 1d · Classify the embargo, and pick the route

Two decisions taken together, because between them they set how every lane below writes: the branch name, the
commit message, the PR, and where the fix lives until release. **Both are recorded in the artifact Phase 2
opens** (`Disclosure:`, `Route:`) — Phase 5 executes them days later, possibly in another session.

| The report arrived | `Disclosure:` | What that turns on |
| --- | --- | --- |
| privately — a security email, a GitHub private report | `embargoed` | neutral wording on every public surface until publish; both routes are open |
| publicly — an issue, a PR, a posted PoC | `public` | neither buys anything — the route is the public PR, and the release window is the only thing left that matters |

Then the route, which only `embargoed` leaves open:

| `Route:` | When | What it costs |
| --- | --- | --- |
| **neutral public PR** — the ordinary case | the diff self-discloses anyway, and the repo fixes in the open | a legible diff for as long as it takes to release — so it is right exactly when you can release fast |
| **temporary private fork** | genuine pre-release secrecy: multi-vendor coordination, or a fix whose diff hides what it fixes | CI, review and house-style history — and the days those would have bought back |

**Say the honest thing about `embargoed`, once, to the user.** The diff self-discloses — a bound added to an
unbounded read is legible to anyone reading the patch. Neutral wording slows a casual scanner and buys the
release→publish window; it is a courtesy, not secrecy. What protects consumers is keeping that window **tight**,
which is why the public route usually wins.

## Phase 2 — Diagnose — `my-debug`, plus two things

Run `my-debug` **by reading `~/.agents/skills/my-debug/SKILL.md` and executing its phases here**. Apply the same
composition rule to `my-triage` at 1b so the embargo context stays in this session. `my-debug` writes
`.claude/debugs/<yyyy-mm-dd>-<title>.md`; this skill adds the
`Disclosure:` header line and the `## Disclosure` section (appendix), and two overrides:

1. **Choose a neutral title under embargo.** `my-build` derives the branch from it (`fix/<title>`), and on the
   public-PR route pushes that branch to a public remote — so the title discloses one push ahead of the diff.
   `fix/readstring-length-bound` says what the code now does.
2. **Sweep the bug class.** Every sibling call site and analogous path gets checked for the same flaw. The
   reported instance is one member of a class, the fix closes the class, and the sweep's hits are tasks in the
   Fix Plan.

## Phase 3 — Open the advisory, and start the clocks

Two of Phase 7's four boxes are answered here, and both take days — so they start before a line of code is
written. **The advisory gates them both:** the CVE request and the credit are calls against the `{ghsa}` id it
returns, and neither can be issued until it exists.

1. **Draft the advisory, and create it private.** Content template and the `gh` call in the appendix. Two things
   it needs that a bug report doesn't:
   - **1c's two readings, and which one the advisory carries.** It has room for a single vector, so name in
     `## Impact` whose reality that vector describes and what the other one is. Publishing one number as if it
     were the whole answer is what the two readings exist to prevent.
   - **The affected range and the patched version** — Phase 2's sweep settles the range; the version is the one
     you are *about* to cut, by the repo's convention. Both are one `PATCH` away if the release slips.
2. **Request the CVE** against that id. It reserves an identifier asynchronously and is **decoupled from
   publish** — asking now removes a blocker later, and a request on a private draft discloses nothing.
3. **Ask the reporter how they want to be credited** — email template in the appendix, two questions, because
   the halves are independent and either can be anonymous without the other:
   - **structured credit** — a `credits[]` entry carrying their GitHub login, public at publish, and it needs
     **their acceptance**;
   - **the prose** in `## Acknowledgements` — their name, their handle, or *an anonymous security researcher*,
     with the address and the handle scrubbed from it either way.

   **Their reply is answered with the `PATCH`, in the session it arrives.** Adding `credits[]` is what starts
   the acceptance clock, and it is the only clock running on a stranger's attention. Holding the reply until
   Phase 7 puts two human latencies end to end and stalls publish behind a call that could have been made days
   earlier. **Entered `public`** → the same ask, in the thread.

Write `Advisory:`, `CVE:` and their answer into the artifact's `## Disclosure` as each returns.

## Phase 4 — Fix — `my-build`, plus the guard rule

Run `my-build` on the artifact's Fix Plan as documented. Two overrides:

**The regression guard has to survive its own suite.** The values that prove a memory-exhaustion or crash bug
*kill the test binary* — a declared length of `1<<40` gets the process OOM-killed, `MaxUint64` panics on a slice
bound — and a suite that dies proves nothing to CI. So the guard triggers on a **moderate** over-declaration: a
length far past the file but cheap to allocate (`1_000_000`), asserting **the guard's own error**. That is what
regressing actually looks like — the bound stops firing. The real values stay in the PoC, which stays out of the
repo.

**Neutral wording, under embargo, from the first commit.** Write it as the maintenance change it also is — what
the code now does, in the repo's ordinary voice: *bound the declared length against the remaining file size*.
The vocabulary of the report — the impact, the attacker, the advisory id — is what publish adds later, and
reaching for it now means rewriting every commit before the branch can be pushed.

## Phase 5 — Ship & merge — `my-ship`, plus the route

Run `my-ship` as documented; its PR title and body take Phase 4's wording rule. **The route was picked at 1d**
— reopen it only if Phase 2's Fix Plan came out materially larger or subtler than triage assumed, and say so
when you do.

- **`Route: neutral public PR`** → open it as an ordinary fix, and let CI and review run on it. Prefer it over
  the advisory's own *merge to upstream* button, which lands the commit without either.
- **`Route: temporary private fork`** → create the fork from the advisory (appendix), push the branch to it, and
  open the PR there. Nothing reaches public `main` until Phase 6.

**A private fork opened and then routed around is the cheap half of the decision**, taken before the route was
clear — keep it, don't hide it. Where one exists and is not the route, close its PR **without a comment** (the
API refuses comments on a temporary private fork; it is a workspace repository) and leave it for GitHub to
auto-clean at publish.

## Phase 6 — Release

**The advisory releases nothing.** The fix reaches public `main` first, and the tag is what the release workflow
triggers on.

1. **Land it on public `main`.** The public-PR route did this at Phase 5. **The private-fork route lands here,
   and not before** — merge the fork's PR upstream, and know what that moment is: the diff goes public, and the
   release→publish window starts running from it. Everything below follows it closely.
2. **Match the repo's tag convention** — inspect an existing one rather than assuming. `git cat-file -t
   v<previous>` returns `commit` for a lightweight tag, `tag` for an annotated one.
3. Tag the merged commit on `main`, push the tag, and watch the release workflow through.
4. **Update the downstream consumers you know of** to the patched version — **before** publish, not after.
   Publish fires Dependabot alerts across every consumer, and the ones we own should not be among the alerted.
   It is the slowest box on Phase 7's checklist and the one that actually protects anyone.

Check *Fix released* and *Downstream consumers upgraded* in the artifact as each lands. Nothing below can be
hurried, so **the run pauses here between sessions** and 1a resumes it.

## Phase 7 — Clear the checklist, then publish

**The checklist is the gate.** All four boxes, in the artifact, each carrying the date it was checked:

- [ ] **Fix released** — the tag is cut and the release workflow finished.
- [ ] **Downstream consumers upgraded** — the ones we know of are on the patched version.
- [ ] **Credit settled** — the reporter accepted, or their answer was anonymous-only and there is nothing to
      accept.
- [ ] **CVE assigned** — the reserved ID came back assigned.

**The credit was applied in 3.3; this box only checks that it landed.** A `credits[]` entry sits at `pending`
until the reporter accepts, and **an unaccepted credit does not appear** — which is why the box is a box.
Structured and anonymous are not opposites: a `credits: [{login, type: "finder"}]` entry alongside an
acknowledgement reading *"Reported by an anonymous security researcher"* is one coherent answer. Arriving here
with nothing applied means a reply was never `PATCH`ed — go back to 3.3 and send it now, because the clock this
box waits on has not started.

Then **present the advisory as it will publish, and ask.** On the user's word, publish: it makes the CVE and the
advisory public, fires Dependabot alerts across every consumer, and auto-cleans the temporary private fork.

Set `Disclosure: published`, and close with what shipped, what was credited, and under which CVE.

## Appendix — templates and runbook

### The `## Disclosure` section

Added to `my-debug`'s artifact in Phase 2 — the header line under `Type:`, the section after *Background*.
`Status:` keeps `my-debug`'s ladder and tracks the **code**; `Disclosure:` tracks the **report**.

```markdown
Disclosure: <embargoed | public | published>

## Disclosure

Channel: <security email · GitHub private report · public issue #<n>>
Route: <neutral public PR | temporary private fork>
Advisory: <GHSA-xxxx-xxxx-xxxx>          # — until Phase 3
CVE: <CVE-YYYY-NNNNN>                    # — until requested; RESERVED until assigned
Reporter: <contact, and their credit preference in their own words>
CVSS: <vector> (<score>) trusted intake · <vector> (<score>) untrusted intake
        <what the reporter claimed, if we differ — and the metric we differ on>
CWE: <CWE-NNN, …>
Affected: <package> <vulnerable range> → patched in <version>

### Publish checklist
- [ ] Fix released — <tag>, <date>
- [ ] Downstream consumers upgraded — <what>, <date>
- [ ] Credit settled — applied <date>, accepted <date>   # or: anonymous only, nothing to accept
- [ ] CVE assigned — <id>, <date>
```

### Advisory content

The body, as `description`:

```markdown
## Impact
<What it costs the consumer, and which consumers. For a library, say plainly that this depends on how the
caller feeds it input, and which of the two CVSS readings applies to whom.>

## Affected usage
<The concrete call path: the exported function(s), and what input reaches them.>

## Workarounds
<What a consumer can do without upgrading — bound or validate upstream — or that there is none.>

## Fix
<What the patch does, and the version it landed in.>

## Acknowledgements
<Reported by <name or handle>.  — or —  Reported by an anonymous security researcher.>
```

The `advisory.json` around it. The vector below is the **untrusted-intake** reading; the advisory carries one
vector, so name which one it is in `## Impact` and keep both in the artifact:

```json
{
  "summary": "<one line: the flaw, and the exported surface it reaches>",
  "description": "<the markdown above>",
  "cvss_vector_string": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H",
  "cwe_ids": ["CWE-<n>"],
  "vulnerabilities": [{
    "package": { "ecosystem": "<go | npm | …>", "name": "<module path>" },
    "vulnerable_version_range": "< X.Y.Z",
    "patched_versions": "X.Y.Z"
  }]
}
```

### The credit request

```markdown
Subject: Credit for your report — <repo>

Hi,

Thank you for the report. We have confirmed it, the fix is <landing / released in vX.Y.Z>, and we have
opened a private GitHub security advisory for it.

We would like to credit you, and that is two separate questions:

1. Your GitHub handle, if you would like structured credit on the advisory itself. GitHub asks you to
   accept it, and it becomes public when the advisory publishes.
2. How you would like to be named in the advisory text — your name, your handle, or "an anonymous
   security researcher".

Either can be anonymous without the other. If you would rather not be credited at all, that is fine
too — just say so.

<name>, <repo> maintainers
```

### Runbook

```sh
# open the advisory, private — Phase 3
gh api --method POST /repos/{owner}/{repo}/security-advisories --input advisory.json

# request the CVE — Phase 3; async, private, decoupled from publish
gh api --method POST /repos/{owner}/{repo}/security-advisories/{ghsa}/cve

# temporary private fork — Phase 5, private-fork route only
gh api --method POST /repos/{owner}/{repo}/security-advisories/{ghsa}/forks

# close the private PR, no comment — Phase 5; the API refuses comments on a workspace repository
gh pr close <n> --repo <owner>/<temp-fork>

# release — Phase 6; the tag triggers the workflow, and it has to sit on merged main
git tag vX.Y.Z <merged-sha>        # lightweight; an annotated-tag repo needs -a -m
git push origin vX.Y.Z

# credit and the anonymized prose, one call — Phase 3, the session the reporter replies
gh api --method PATCH /repos/{owner}/{repo}/security-advisories/{ghsa} --input credit.json
# credit.json: {"credits":[{"login":"<login>","type":"finder"}],"description":"<markdown>"}
```

**Publish from the advisory page.** It is the one step here worth doing by hand: it is irreversible, and its
confirmation dialog is the last look at what goes public.
