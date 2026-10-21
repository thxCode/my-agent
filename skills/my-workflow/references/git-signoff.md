# Commit signoff

Shared by `my-build`, its Team lane, and `my-ship`. Apply the existing commit and history-rewrite approval gates first.

## Create and rewrite

- Use `git commit --signoff` for every new commit, including finalization, amend, and fixup commits.
- Let Git append `Signed-off-by:` from the real committer identity. Do not hand-write another person's signoff.
- Preserve existing authors and trailers. Signoff is a commit-message trailer; it is not a cryptographic signature.
- Use `git rebase --signoff` for approved autosquash and reorder operations.
  For signoff repair alone, use `git rebase --force-rebase --signoff <base>` so an unchanged history is actually replayed.
- Limit history repair to `<base>..HEAD`. Include missing signoffs in the proposed history and obtain the existing rewrite approval.
  Preserve merge topology when present; do not use a linear rebase to flatten merge commits.
- If identity is missing or incorrect, surface it before committing. Do not invent identity or change Git configuration silently.
- If nothing is stageable, skip the commit. Do not create an empty commit to satisfy this procedure.

## Verify commit objects

After every commit, amend, or fixup, run the check below as `new HEAD`.
After a rebase, check each rewritten commit as `new <sha>`.
The signoff must match that commit's recorded committer.

Before tidying and again before pushing, run the same check as `history "<base>..HEAD"`.
History mode requires a well-formed signoff on every commit; it does not require older commits to carry the current user's identity.
Report missing signoffs before tidying; after repair, require a clean result before pushing.
An empty range is reported as a skip, never a successful audit.

```bash
python3 - new HEAD <<'PY'
import re
import subprocess
import sys

def git(*args, text=None):
    return subprocess.run(
        ["git", *args], input=text, text=True, capture_output=True, check=True
    ).stdout

mode, scope = sys.argv[1:]
if mode == "new":
    commits = [git("rev-parse", "--verify", scope + "^{commit}").strip()]
elif mode == "history" and ".." in scope:
    commits = git("rev-list", "--reverse", scope).splitlines()
else:
    raise SystemExit("Use new <commit> or history <base>..HEAD")
if not commits:
    print("SKIP: empty commit range")
    raise SystemExit(0)

failed = []
for sha in commits:
    body = git("show", "-s", "--format=%B", sha)
    trailers = git("interpret-trailers", "--parse", text=body).splitlines()
    signers = []
    for line in trailers:
        match = re.fullmatch(r"Signed-off-by:\s+(.+ <[^<>\s]+>)", line, re.IGNORECASE)
        if match:
            signers.append(match.group(1))
    committer = git("show", "-s", "--format=%cn <%ce>", sha).strip()
    if not signers or (mode == "new" and committer not in signers):
        failed.append(sha)
if failed:
    print("FAIL: missing or mismatched signoff: " + " ".join(failed))
    raise SystemExit(1)
print(f"PASS: checked signoff on {len(commits)} commit(s)")
PY
```

A body sentence that mentions `Signed-off-by` is not a trailer. Parse the actual footer rather than searching the whole message.
Preserve valid trailers during repair. Re-run verification after every history change because earlier commit checks cover different objects.
