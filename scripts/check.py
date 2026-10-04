#!/usr/bin/env python3
"""Check this repository's skill metadata and documentation; optionally use the index."""

import argparse
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlsplit


def check(root, validator):
    try:
        import yaml
    except ImportError:
        return ["PyYAML is required: install requirements-check.txt with this Python interpreter."]
    if not validator.is_file():
        return [f"Skill validator missing: {validator}. Set SKILL_VALIDATOR to skill-creator/scripts/quick_validate.py."]

    errors = []
    skills = sorted((root / "skills").glob("*/SKILL.md"))
    if not skills:
        errors.append("No skills/*/SKILL.md found.")
    for skill in skills:
        result = subprocess.run(
            [sys.executable, str(validator), str(skill.parent)],
            capture_output=True, text=True,
        )
        if result.returncode:
            errors.append(f"{skill.relative_to(root)}: {result.stdout.strip()} {result.stderr.strip()}")
        metadata = skill.parent / "agents/openai.yaml"
        try:
            value = yaml.safe_load(metadata.read_text())
            interface = value.get("interface") if isinstance(value, dict) else None
            if not isinstance(interface, dict):
                raise ValueError("interface must be a mapping")
            for field in ["display_name", "short_description"]:
                if not isinstance(interface.get(field), str) or not interface[field].strip():
                    raise ValueError(f"interface.{field} must be a non-empty string")
        except (OSError, ValueError, yaml.YAMLError) as exc:
            errors.append(f"{metadata.relative_to(root)}: {exc}")

    # Synthetic evaluation outputs deliberately discuss missing source files.
    # Only authored repository documentation is a link-integrity contract.
    docs = list(root.glob("*.md"))
    for directory in ["docs", ".scratch", "skills", "scripts"]:
        docs.extend((root / directory).rglob("*.md"))
    docs.extend((root / "tests").rglob("README.md"))
    for doc in sorted(set(docs)):
        fenced = None
        for number, line in enumerate(doc.read_text().splitlines(), 1):
            fence = re.match(r"^\s*(`{3,}|~{3,})", line)
            if fence:
                marker = fence.group(1)[0]
                fenced = None if fenced == marker else marker if fenced is None else fenced
                continue
            if fenced:
                continue
            line = re.sub(r"`[^`]*`", "", line)
            for target in re.findall(r"\[[^\]]*\]\((<[^>]+>|[^\s)]+)(?:\s+\"[^\"]*\")?\)", line):
                target = target.strip("<>")
                url = urlsplit(target)
                if url.scheme or url.netloc or not url.path or url.path.startswith("/"):
                    continue
                if not (doc.parent / unquote(url.path)).exists():
                    errors.append(f"{doc.relative_to(root)}:{number}: missing relative link {target}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true", help="validate staged content, including staged link targets")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    codex_root = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    validator = Path(os.environ.get("SKILL_VALIDATOR", str(codex_root / "skills/.system/skill-creator/scripts/quick_validate.py"))).expanduser().resolve()
    if args.staged:
        with tempfile.TemporaryDirectory(prefix="answer-me-index-") as directory:
            result = subprocess.run(
                ["git", "checkout-index", "--all", f"--prefix={directory}/"], cwd=root,
                capture_output=True, text=True,
            )
            if result.returncode:
                print(result.stderr.strip(), file=sys.stderr)
                return 1
            errors = check(Path(directory), validator)
    else:
        errors = check(root, validator)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("PASS: skill frontmatter, display metadata, and relative documentation links" + (" (staged snapshot)" if args.staged else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
