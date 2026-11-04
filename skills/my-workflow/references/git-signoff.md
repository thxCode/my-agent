# Commit signoff

Shared by `my-build`, its Team lane, and `my-ship`. Apply the existing commit and history-rewrite approval gates first.

## Create and rewrite

- Use `git commit --signoff` for every new commit, including finalization, amend, and fixup commits.
- Include a detail list in every commit body: 1 to 5 `- ` bullet items summarizing the work in that commit, with at most 15 words per item (excluding the leading `- `).
- When tidying or squashing commits in `my-ship`, rewrite each resulting commit message so its detail bullets (1 to 5 items, at most 15 words each) describe the tidied work. Do not leave `--no-edit` or bare `fixup!` commits that drop or stale the detail list.
- Let Git append `Signed-off-by:` from the real committer identity. Do not hand-write another person's signoff.
- Preserve existing authors and trailers. Signoff is a commit-message trailer; it is not a cryptographic signature.
- Use `git rebase --signoff` for approved autosquash and reorder operations.
  For signoff repair alone, use `git rebase --force-rebase --signoff <base>` so an unchanged history is actually replayed.
- Limit history repair to `<base>..HEAD`. Include missing signoffs or invalid detail lists in the proposed history and obtain the existing rewrite approval.
  Preserve merge topology when present; do not use a linear rebase to flatten merge commits.
- If identity is missing or incorrect, surface it before committing. Do not invent identity or change Git configuration silently.
- If nothing is stageable, skip the commit. Do not create an empty commit to satisfy this procedure.

## Verify commit objects

After every commit, amend, or fixup, run the check below as `new HEAD`.
After a rebase, check each rewritten commit as `new <sha>`.
The commit must carry 1 to 5 detail bullets (each at most 15 words), and the signoff must match that commit's recorded committer.

Before tidying and again before pushing, run the same check as `history "<base>..HEAD"`.
History mode requires 1 to 5 detail bullets (each at most 15 words) on every non-merge commit and a well-formed signoff on every commit; it does not require older commits to carry the current user's identity.
Report missing signoffs or invalid detail lists before tidying; after repair, require a clean result before pushing.
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

def parse_bullets(body, trailer_lines):
    lines = body.splitlines()[1:]
    bullets, active = [], False
    for raw in lines:
        s = raw.strip()
        if not s or s in trailer_lines or re.fullmatch(r"Task \d+ of [^\s.]+\.?", s):
            active = False
            continue
        if s.startswith("- "):
            bullets.append(s[2:].strip())
            active = True
        elif active and raw[:1].isspace():
            bullets[-1] = (bullets[-1] + " " + s).strip()
        else:
            active = False
    return bullets

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
    trailers = [
        t.strip()
        for t in git("interpret-trailers", "--parse", text=body).splitlines()
        if t.strip()
    ]
    signers = []
    for line in trailers:
        match = re.fullmatch(r"Signed-off-by:\s+(.+ <[^<>\s]+>)", line, re.IGNORECASE)
        if match:
            signers.append(match.group(1))
    committer = git("show", "-s", "--format=%cn <%ce>", sha).strip()
    reasons = []
    if not signers or (mode == "new" and committer not in signers):
        reasons.append("missing or mismatched signoff")
    parents = git("rev-list", "--parents", "-n", "1", sha).split()[1:]
    if len(parents) <= 1:
        bullets = parse_bullets(body, set(trailers))
        if not 1 <= len(bullets) <= 5:
            reasons.append(f"expected 1..5 detail bullets, found {len(bullets)}")
        for idx, item in enumerate(bullets, 1):
            words = len(item.split())
            if not 1 <= words <= 15:
                reasons.append(f"bullet {idx} has {words} words (max 15)")
    if reasons:
        failed.append(f"{sha[:7]} ({'; '.join(reasons)})")
if failed:
    print("FAIL: " + ", ".join(failed))
    raise SystemExit(1)
print(f"PASS: checked detail bullets and signoff on {len(commits)} commit(s)")
PY
```

A body sentence that mentions `Signed-off-by` is not a trailer. Parse the actual footer rather than searching the whole message.
Preserve valid trailers during repair. Re-run verification after every history change because earlier commit checks cover different objects.
