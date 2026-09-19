#!/usr/bin/env python3
"""Validate the shared my-* skill schema, cross-host invocation policy, and provenance."""

from functools import cache
from pathlib import Path
import re
import subprocess
import sys
import unicodedata

import yaml


ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT.parent
AGENTS = REPO / "agents"
CREDITS = REPO / "CREDITS.md"

# Under a title, a derived file names the upstream it was distilled from. CREDITS.md
# records the commit each upstream was read at, once per upstream, so a sync updates
# one line rather than one per file.
PROVENANCE = re.compile(r"^Distilled from ", re.MULTILINE)

# No gate on "every backticked name resolves to a skill": measured against this
# repository it flags 25 ordinary terms (`merge-base`, `md-fit`, `user-auth-flow`)
# for each real miss. A gate that noisy gets switched off, which is worse than none
# because the bar still looks like it is there. Orphan detection below is the
# precise half of the same concern.

# A backticked `namespace:name` is one host's plugin reference. It resolves on that
# host only, so a shared skill naming one is broken everywhere else; name a skill
# that exists in this root instead.
NAMESPACED_REF = re.compile(r"`([a-z0-9-]+:[a-z0-9-]+)`")
# Not a skill reference — the conventional way to cite a source location.
NAMESPACED_ALLOWED = {"file:line"}

ALLOWED = {
    "name",
    "description",
    "license",
    "compatibility",
    "allowed-tools",
    "metadata",
    "disable-model-invocation",
}


def load_frontmatter(path: Path) -> dict:
    text = path.read_text()
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    assert match, f"{path}: missing YAML frontmatter"
    data = yaml.safe_load(match.group(1))
    assert isinstance(data, dict), f"{path}: frontmatter must be a mapping"
    return data


def check_symlinks() -> int:
    """Nothing here is a symlink today, but one added later that dangles fails silently
    at runtime rather than at load, so the guard stays."""
    count = 0
    for base in (ROOT, AGENTS):
        for entry in sorted(base.iterdir()):
            if not entry.is_symlink():
                continue
            assert entry.exists(), f"{entry}: dangling symlink -> {entry.readlink()}"
            count += 1
    return count


@cache
def tracked() -> frozenset[str]:
    """What this repository owns. A third-party installer's skill is untracked, so git
    is what tells ours apart from theirs without a hand-kept list."""
    out = subprocess.run(
        ["git", "-C", str(REPO), "ls-files"], capture_output=True, text=True, check=True
    ).stdout.split()
    return frozenset(out)


def is_tracked(path: Path) -> bool:
    return str(path.relative_to(REPO)) in tracked()


def tracked_skills() -> list[str]:
    parts = [Path(p).parts for p in tracked() if p.startswith("skills/") and p.endswith("/SKILL.md")]
    return sorted({p[1] for p in parts if len(p) == 3})


def corpus() -> list[Path]:
    return sorted(ROOT.rglob("*.md")) + sorted(AGENTS.glob("*.md")) + [REPO / "README.md"]


def check_orphans(names: list[str]) -> None:
    """A skill nothing routes into is dead weight that still costs a description every
    session. my-* skills are entry points and answer to the user, not to a reference."""
    files = [(p, p.read_text()) for p in corpus() if p.exists()]
    for name in names:
        if name.startswith("my-"):
            continue
        own = f"{ROOT / name}/"
        cited = any(f"`{name}`" in text for path, text in files if not str(path).startswith(own))
        assert cited, (
            f"{ROOT / name}: nothing references `{name}`; route into it or remove it, "
            f"because an unreferenced skill still costs its description every session"
        )


def check_provenance(names: list[str]) -> int:
    """A distilled file and CREDITS.md have to agree in both directions: an unlisted
    derivation is an attribution gap, and a listed one that lost its line is a dead entry."""
    assert CREDITS.is_file(), f"{CREDITS}: missing; distilled files cite it for their upstream commit"
    # Left column only. The right column names the upstream path, which lives in
    # somebody else's repository and will not be found here.
    credited = set(re.findall(r"^\|\s*`([^`]+\.md)`[^|]*\|", CREDITS.read_text(), re.MULTILINE))

    declared = set()
    for path in [ROOT / n / "SKILL.md" for n in names] + corpus():
        if not path.exists() or not PROVENANCE.search(path.read_text()):
            continue
        declared.add(str(path.relative_to(REPO)))

    for rel in sorted(declared - credited):
        raise AssertionError(f"{rel}: declares a distillation that CREDITS.md does not list")

    # The reverse direction is looser by design: a file with one derived section credits
    # it inline rather than under its title, so what is required is the pointer back.
    for rel in sorted(credited):
        path = REPO / rel
        assert path.is_file(), f"CREDITS.md: lists {rel}, which does not exist"
        assert "CREDITS.md" in path.read_text(), f"CREDITS.md: lists {rel}, which never points back at it"
    return len(credited)


def check_gitignore(names: list[str]) -> None:
    """This .gitignore denies everything and allowlists what it tracks, so a skill added
    without its entry is silently untracked and a stale entry hides a deletion."""
    lines = (REPO / ".gitignore").read_text().splitlines()
    listed = {m.group(1) for m in (re.match(r"^!skills/([a-z0-9*][a-z0-9*-]*)/$", l) for l in lines) if m}

    for name in sorted(listed):
        # Re-including a directory does not re-include what is inside it. Without the
        # companion line the contents stay ignored, and the miss is invisible while the
        # files already added are tracked -- git does not apply ignore rules to those.
        assert f"!skills/{name}/**" in lines, (
            f".gitignore: allowlists skills/{name}/ with no `!skills/{name}/**`, "
            f"so anything added under it is silently untracked"
        )
        if "*" not in name:
            assert (ROOT / name).is_dir(), f".gitignore: allowlists skills/{name}/, which does not exist"

    for name in names:
        if name.startswith("my-"):
            continue  # covered by the !skills/my-*/ glob
        assert name in listed, f".gitignore: skills/{name}/ is tracked but not allowlisted"


def check_no_emoji(names: list[str]) -> int:
    """AGENTS.md section 6 reserves emphasis for one capitalized word and bans emoji.
    Box drawing is exempt: the README layout tree is built from it."""
    count = 0
    for path in sorted(set(corpus() + [REPO / "AGENTS.md", CREDITS])):
        if not path.exists() or not is_tracked(path):
            continue
        count += 1
        for number, line in enumerate(path.read_text().splitlines(), 1):
            for char in line:
                emoji = char == "️" or (
                    not 0x2500 <= ord(char) <= 0x257F and unicodedata.category(char) == "So"
                )
                assert not emoji, (
                    f"{path.relative_to(REPO)}:{number}: U+{ord(char):04X} is an emoji; "
                    f"use one capitalized word (NEVER, REQUIRED) for emphasis instead"
                )
    return count


def check_namespaced_refs() -> None:
    paths = sorted(ROOT.glob("my-*/**/*.md")) + sorted(AGENTS.glob("*.md"))
    for path in paths:
        for ref in NAMESPACED_REF.findall(path.read_text()):
            assert ref in NAMESPACED_ALLOWED, (
                f"{path}: `{ref}` is one host's plugin reference and does not resolve "
                f"on the others; name a skill under {ROOT} instead"
            )


def main() -> int:
    skills = sorted(ROOT.glob("my-*/SKILL.md"))
    assert skills, f"{ROOT}: no my-* skills found"

    for skill_md in skills:
        data = load_frontmatter(skill_md)
        extra = set(data) - ALLOWED
        assert not extra, f"{skill_md}: unsupported fields: {sorted(extra)}"
        name = data.get("name")
        description = data.get("description")
        assert name == skill_md.parent.name, f"{skill_md}: name must match its directory"
        assert isinstance(name, str) and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name), skill_md
        assert isinstance(description, str) and 0 < len(description.strip()) <= 1024, skill_md

        explicit = data.get("disable-model-invocation", False)
        assert isinstance(explicit, bool), f"{skill_md}: disable-model-invocation must be boolean"
        openai_yaml = skill_md.parent / "agents" / "openai.yaml"
        if explicit:
            assert openai_yaml.is_file(), f"{skill_md}: missing Codex invocation policy"
            openai = yaml.safe_load(openai_yaml.read_text())
            assert openai == {"policy": {"allow_implicit_invocation": False}}, openai_yaml
        elif openai_yaml.exists():
            openai = yaml.safe_load(openai_yaml.read_text())
            assert openai.get("policy", {}).get("allow_implicit_invocation") is not False, (
                f"{openai_yaml}: Codex policy conflicts with shared frontmatter"
            )

        print(f"ok {name}")

    check_namespaced_refs()
    print("ok no host-specific plugin references")

    names = tracked_skills()
    check_orphans(names)
    print(f"ok every one of {len(names)} tracked skills is routed into")
    check_gitignore(names)
    print("ok .gitignore allowlist matches the tracked skills")
    print(f"ok no emoji in {check_no_emoji(names)} tracked documents")
    print(f"ok {check_provenance(names)} distilled files agree with CREDITS.md")
    print(f"ok {check_symlinks()} symlinks resolve")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, OSError, yaml.YAMLError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
