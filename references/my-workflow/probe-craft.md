# Probe craft — the script, its hygiene gate, and the comment that carries it

Read by `/my-triage` on the draft-a-probe branch. A **probe** is content for one issue thread: a read-only
script a stranger runs once, on hardware we do not own, to falsify exactly one hypothesis.

Two things make it work, and both are cheap to lose. The script must **degrade** rather than fail — no
kubectl, no cluster, no root, all still produce a usable bundle. The comment must **stay small** — the
reporter is doing us a favour on a phone between other work.

## 1. The probe's shape

Copy this, then replace the placeholders and add one `run` / `kx` per fact the hypothesis needs. The three
helpers are `say` (echo + append to the summary), `run` (record a command, its output and its exit code) and
`kx` (run a snippet inside the target container); `priv` is `run` for a step that needs root.

```bash
#!/usr/bin/env bash
# <project> — <the one thing this probe separates>
# For <issue URL>
#
# Strictly read-only. Writes nothing to the cluster, and nothing on the host
# outside its own output directory. Records every command's exit code.
#
# Usage:
#   ./probe.sh -n NS --pod POD # cluster + in-pod probes (needs kubectl)
#   ./probe.sh --container C   # container to probe (default: main)
#   ./probe.sh --tail 20000    # log lines per container (default: the whole log)
#   ./probe.sh --host          # also collect host facts (run this ON the node)
#   ./probe.sh --host-only     # host facts only, needs no kubectl

[ -n "${BASH_VERSION:-}" ] || exec bash "$0" "$@"   # a BusyBox sh re-execs into bash
set -uo pipefail
umask 077                     # the bundle holds logs and host state; keep it owner-only

NS=""; POD=""; CTR="main"; TAIL=-1; WANT_HOST=0; HOST_ONLY=0
need() { [ $# -ge 2 ] || { echo "missing value for $1" >&2; exit 2; }; }
while [ $# -gt 0 ]; do
  case "$1" in                # `need` first: a bare `--pod` would leave `shift 2` a no-op, and loop forever
    -n|--namespace) need "$@"; NS="$2";   shift 2 ;;
    --pod)          need "$@"; POD="$2";  shift 2 ;;
    --container)    need "$@"; CTR="$2";  shift 2 ;;
    --tail)         need "$@"; TAIL="$2"; shift 2 ;;
    --host)         WANT_HOST=1; shift ;;
    --host-only)    WANT_HOST=1; HOST_ONLY=1; shift ;;
    -h|--help)      sed -n '/^# Usage:/,/^$/p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

OUT="$PWD/probe-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUT" || exit 1
SUMMARY="$OUT/00-summary.txt"; : >"$SUMMARY"
_n=0
say() { echo "$*" | tee -a "$SUMMARY"; }

PROBE_VERSION="<n>-r<k>"      # F4: detect a reporter re-running an old copy
KTO="--request-timeout=30s"   # bound with the tool's OWN flag — BusyBox may lack GNU `timeout`
printf 'probe %s\n\n' "$PROBE_VERSION" >"$OUT/00-probe-version.txt"

A=""; B=""; A_RC=1; B_RC=1    # the A/B's two arms; an arm that never ran stays unset and non-zero
LAST_F=""; LAST_RC=0
run() {                       # run <slug> <cmd...>
  local slug="$1"; shift
  _n=$((_n + 1))
  local f; f=$(printf '%s/%02d-%s.txt' "$OUT" "$_n" "$slug")
  printf '$ %s\n\n' "$*" >"$f"
  "$@" >>"$f" 2>&1
  local rc=$?
  printf '\n[exit=%d]\n' "$rc" >>"$f"
  printf '  %-42s -> %-34s exit=%d\n' "$slug" "$(basename "$f")" "$rc" | tee -a "$SUMMARY"
  LAST_F="$f"; LAST_RC=$rc    # the verdict reads these; never `ls` for a path we just created
  return 0                    # never abort the collection
}

kx() {                        # kx <slug> <sh-snippet> — inside the target container
  run "$1" kubectl exec -n "$NS" "$POD" -c "$CTR" --request-timeout=180s -- sh -c "$2"
}

IS_ROOT=0; [ "$(id -u)" -eq 0 ] && IS_ROOT=1
priv() {                      # priv <slug> <cmd...> — read-only, but needs root
  [ "$IS_ROOT" = 1 ] && { run "$@"; return 0; }
  printf '  %-42s -> %s\n' "$1" '[skipped: needs root]' | tee -a "$SUMMARY"
}

say "=== <project> probe $PROBE_VERSION ==="
say "date    : $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
say "host    : $(uname -srm) / $(hostname)"
say "euid    : $(id -u)"
say "output  : $OUT"
say ""

if [ "$HOST_ONLY" = 1 ]; then
  say "--- cluster + in-pod: SKIPPED (--host-only) ---"
elif ! command -v kubectl >/dev/null 2>&1; then
  say "--- cluster + in-pod: SKIPPED (no kubectl on PATH) ---"
  HOST_ONLY=1; WANT_HOST=1
elif ! kubectl --request-timeout=10s version >/dev/null 2>&1; then   # preflight, once
  say "--- cluster + in-pod: SKIPPED (API server unreachable with this kubeconfig) ---"
  say "    context: $(kubectl config current-context 2>&1)"
  HOST_ONLY=1
elif [ -z "$NS" ] || [ -z "$POD" ]; then                             # no target, so say so
  say "--- cluster + in-pod: SKIPPED (need -n <namespace> and --pod <pod>) ---"
  say "    find them with: kubectl get pod -A | grep <the failing workload>"
  HOST_ONLY=1
else
  say "--- phase 1: inventory ---"
  run nodes  kubectl $KTO get nodes -o wide
  run dm-log kubectl $KTO logs -n "$NS" "$POD" -c "$CTR" --timestamps --tail="$TAIL"
  # …one run/kx per fact the hypothesis needs. Breadth rides along; it never leads.

  say "--- phase 2: the A/B ---"
  kx detect-A-default "<the command as it runs today>";              A=$LAST_F; A_RC=$LAST_RC
  kx detect-B-changed "<the same command, exactly one variable changed>"; B=$LAST_F; B_RC=$LAST_RC
fi

# Already on the node? Collect host facts unasked — decided by a positive signal, never by
# guessing from which cluster failure led here.
if [ "$WANT_HOST" != 1 ] && { [ -e "/dev/<vendor>0" ] || command -v "<vendor>-smi" >/dev/null 2>&1; }; then
  WANT_HOST=1
fi

say ""
if [ "$WANT_HOST" != 1 ]; then
  say "--- host facts: SKIPPED (re-run with --host on the node) ---"
else
  say "--- phase 3: host facts ---"
  run  host-uname   sh -c "uname -a; cat /etc/os-release"
  priv host-dmesg   sh -c "dmesg 2>&1 | tail -80"
  priv host-lsmod   sh -c "lsmod"
  priv host-devs    sh -c "ls -l /dev"
  # Credential-bearing file: grep the lines that matter, never cat the whole thing.
  run  host-runtime sh -c "grep -n -E 'default_runtime_name|runtimes\.|BinaryName' /etc/containerd/config.toml 2>&1"
fi

say ""
say "--- verdict ---"
if [ -z "$A" ] || [ -z "$B" ]; then
  say "  A/B : incomplete — both arms did not run; read $(basename "$SUMMARY")"
elif [ "$A_RC" -ne 0 ] || [ "$B_RC" -ne 0 ]; then     # an arm that FAILED is not an arm that answered
  say "  A/B : incomplete — an arm exited non-zero (A=$A_RC B=$B_RC); read the two files below"
  say "        $(basename "$A") / $(basename "$B")"
elif grep -q '<the failure signature>' "$A" && ! grep -q '<the failure signature>' "$B"; then
  say "  A/B : (A) failed, (B) did not — the changed variable is the cause"
else
  say "  A/B : hypothesis REFUTED — read $(basename "$A") and $(basename "$B")"
fi

say ""
if tar -czf "$OUT.tar.gz" -C "$(dirname "$OUT")" "$(basename "$OUT")" 2>/dev/null; then
  say "Bundle: $OUT.tar.gz"
else
  say "Bundle: tar failed — please attach the directory $OUT instead"
fi
say "Please skim it for anything you consider sensitive — node names and registry hosts, and"
say "especially the container log, the largest and least predictable file in the bundle."
say "Then attach it to <issue URL>."
```

**The version stamp** goes to two places on purpose: the summary header, which is what a reporter pastes when
they will not attach a file, and `00-probe-version.txt`, which is what survives inside the bundle. Bump `<k>`
every round — a stamp from an earlier round is the cheapest way to catch a reporter re-running an old copy.

**The verdict line** exists so the reporter knows the run worked without reading anything. State the A/B
outcome, including the refuting case; a probe that can only print success is not falsifying anything.

## 2. Bounding every call

Bound each call with **the tool's own flag**, never a wrapper — `timeout(1)` is GNU and a BusyBox container
may not have it.

| | |
| --- | --- |
| Ordinary API calls | `kubectl $KTO`, where `KTO="--request-timeout=30s"` |
| `kubectl exec` | `--request-timeout=180s` — a snippet inside a container legitimately takes longer |
| Preflight, once | `kubectl --request-timeout=10s version` |

The preflight is what turns an unreachable API server from *stalling every step for 30s* into *one skipped
phase*. Run it before the first real call, and on failure record the current context and fall through to the
host-only path.

## 3. Modes, and the degradation that comes free

`-n <ns>` · `--pod` · `--tail` · `--host` · `--host-only` — the paths that differ between reporters, and
nothing else. `--host-only` is the load-bearing one: **it needs no kubectl at all**, so it is already the
graceful-degradation path, and the script falls onto it by itself when kubectl is missing or the cluster is
unreachable. Nothing else has to be written to handle those two failures.

**What fills the bundle on that path is the node probe, not the failure that led there.** A missing kubectl
suggests the reporter is on the node; an unreachable API server suggests nothing, and a laptop's `dmesg` is
evidence about the wrong machine. So host facts turn on a missing kubectl, or on the vendor device node or
its CLI being present; a run with none of the three collects nothing and says which flag would change that.

## 4. Privilege — declared, never assumed

`dmesg`, `/dev/<vendor>*` and the kernel module list are read-only, and usually still need root. The rule:

- **The probe never invokes `sudo`.** It reads `EUID` once and routes root-only steps through `priv`.
- **Unprivileged is a recorded outcome, not a failure.** Each such step writes `[skipped: needs root]` into
  the summary; the run completes and the bundle stays usable.
- **The comment names the commands and the reason** — *which* steps need privilege and *what they would tell
  us* — before it asks for a re-run with `sudo`. Asking is optional for the reporter, in that wording.

A reporter who declines root must still end the round with something we can read. If a hypothesis can only be
falsified by a privileged step, that is a fact for the ledger, and the comment says so plainly.

## 5. The hygiene gate

Run this before the comment gate. Item 2 is hard: a probe that does not parse never reaches a human.

| | Check | How |
| --- | --- | --- |
| 1 | Read-only | no `apply` / `create` / `delete` / `patch` / restart; writes nothing outside `$OUT` |
| 2 | **Parses** | `bash -n probe.sh` — hard gate, no exceptions |
| 3 | Lints | `shellcheck -S warning probe.sh`. Not installed → record `shellcheck: unavailable` in the ledger row; the degradation is declared, never silently skipped |
| 4 | Exit codes | every command goes through `run` / `kx` / `priv`, so a failure reads `[exit=N]` and never as "absent" or "none" |
| 5 | Bounded | every remote call carries the tool's own timeout flag, and the preflight runs first (§ 2) |
| 6 | Portable | no `jq`, no repo checkout, no GNU-only flag; assume BusyBox `sh` inside the container and a kubectl that predates recent flags |
| 7 | Secrets | credential-bearing files are grepped for the lines that matter, never dumped whole; `env` is filtered |
| 8 | Unprivileged | run it as non-root: every root-only step records `[skipped: needs root]` and the bundle is still usable (§ 4) |
| 9 | Failure paths | `KUBECONFIG=/tmp/unreachable-kubeconfig bash probe.sh`, and a run with kubectl off `PATH`, both complete |
| 10 | Self-contained | GitHub rejects `.sh` attachments, so the whole script is embedded in `<details>` in the comment — never a link, never a gist |
| 11 | Skim note | the script's closing lines and the comment both ask the reporter to skim the bundle before attaching, **naming the container log** — the largest and least predictable file in it |
| 12 | **Runs** | actually run it three ways: bare, with a value-taking flag given no value, and against a stubbed CLI that fails every call. Items 2 and 3 both pass on a script that hangs forever or that prints a confident verdict over two failed arms |

## 6. The minimal ask

Every comment offers **three to five copy-pasteable commands** beside the script, for the reporter who will
not run a bundle from a stranger. This is what keeps a cautious reporter from becoming a stalled loop.

- A strict **subset** of what the script does — never a second, divergent instrument.
- It **carries the A/B whenever the round has one**. Drop inventory before you drop either arm; the
  discriminating pair is the whole point. An identity round has no A/B yet, and its ask is inventory —
  the one case where the short path is not a subset of a comparison.
- **Quote the placeholders** (`NS='<your namespace>'`) so a paste with the placeholder left in fails loudly
  instead of parsing into something else.
- Say in one clause **what the short path costs** — usually the surrounding state that would have saved the
  next round.

## 7. The comment

Four sections, in this order, stated as **bullets rather than paragraphs**:

| Section | Content | Rounds |
| --- | --- | --- |
| **What your output settled** | one bullet each for confirmed / ruled out / still open, in their terms not ours | ≥ 1 |
| **What we think is happening** | probable causes as a short ranked list, each tagged `confirmed` or `suspected`; no mechanism walkthrough | all |
| **What would help** | the one script in `<details>`, plus the minimal ask (§ 6) | all |
| **What happens next** | what we do with the answer, and the skim-before-attaching note | all |

Round 0 has no output to settle, so it carries the last three. Prose is for the one or two sentences a bullet
cannot carry — a caveat, a thank-you — and **no paragraph runs past three sentences**. The rule is a length
ceiling with a shape, not a word count.

### Worked example — #130, round 1

The round-0 bundle has landed: probe (A) panicked, probe (B) with `GODEBUG=cgocheck=0` enumerated the cards,
and `--version` disagreed with the log. The workaround is still withheld, because a second A/B is pending.

````markdown
Thanks — the bundle settled the main question, and the `--version` line saved us a round.

## What your output settled

- **Confirmed:** probe (A) panicked with `cgo argument has Go pointer to unpinned Go pointer`
  — the failure you reported, now reproducible on demand.
- **Confirmed:** probe (B) — the same command with `GODEBUG=cgocheck=0` — enumerated all 8
  S4000 cards, so nothing *else* in the MThreads path is broken.
- **Ruled out:** your setup. `libmtml.so` has the same md5 inside the pod as on the host, and
  `/dev/mtgpu*` and PCI vendor `1ed5` are both visible to the container.
- **Still open:** which build you are running. `gpustack-operator --version` says `v0.5.4`, but
  the log line at `device.go:57` cannot come from that tag.

## What we think is happening

1. `confirmed` — Go's cgo pointer check rejects the argument our MTML init passes. Ours to fix.
2. `confirmed` — that failed init latches, which is why every later pass says `INVALID_ARGUMENT`.
3. `suspected` — your image is a patched build rather than the released `v0.5.4`. It only
   changes which version we can tell you carries the fix.

## What would help

Three commands, to pin the build:

```sh
NS='<your operator namespace>'; POD='<the device-manager pod>'
kubectl get pod -n "$NS" "$POD" -o jsonpath='{.status.containerStatuses[*].imageID}'
kubectl exec -n "$NS" "$POD" -c main -- gpustack-operator --version
kubectl logs -n "$NS" "$POD" -c main --tail=-1 > dm-mthreads.log
```

<details><summary><code>probe-130-r1.sh</code> — the same three, plus the surrounding state</summary>

…the script, verbatim…

</details>

`dmesg` and the kernel module list are the only steps that need root, and they would tell us
whether the driver logged anything at load time. Skip them if you would rather not — everything
else runs as your normal user, and the bundle stays usable either way.

## What happens next

- The fix is a one-line change in how we hand MTML its library handle, plus a source-level
  guard so it cannot come back.
- There is an interim workaround that unblocks detection with no new image. We held it back on
  purpose: applying it first would have stopped probe (A) panicking and voided the A/B. It
  follows once the build is pinned.
- Please skim the bundle for anything you consider sensitive — node names, registry hosts —
  before attaching it.
````

## 8. Register, and language

Two audiences, two registers, and the split is what keeps the thread readable.

| | Ledger | Comment |
| --- | --- | --- |
| Reader | the maintainer resuming in three days | a stranger doing us a favour |
| Shape | dense, complete, every inference traced to the file that proves it | scannable, bulleted, minimal |
| Carries | the mechanism walkthrough, the tag archaeology, the refuting observation, the rejected hypotheses | what their output settled, what we suspect, what to run next |

The test on any sentence: does it explain **why we believe it**? Ledger. Does it tell the reporter **what to
do**, or **what their output settled**? Comment. Depth reaches the thread only when the reporter asks for it.

**Language.** The comment's *prose* mirrors the language the reporter used in the thread. The script, its
variable names, its output format and its verdict line stay English regardless — they are read by tooling and
by us, and a translated slug breaks the grep that finds this probe again.
