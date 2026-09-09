#!/usr/bin/env python3
"""Validate the shared my-* skill schema and cross-host invocation policy."""

from pathlib import Path
import re
import sys

import yaml


ROOT = Path(__file__).resolve().parents[2]
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

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, OSError, yaml.YAMLError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
