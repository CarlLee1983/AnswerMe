#!/usr/bin/env python3
"""Check this repository's skill metadata and documentation; optionally use the index or a release tag."""

import argparse
from html.parser import HTMLParser
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlsplit

RESOURCE_ATTRIBUTES = frozenset({
    ("script", "src"), ("link", "href"), ("img", "src"), ("img", "srcset"), ("iframe", "src"),
    ("source", "src"), ("source", "srcset"), ("video", "src"), ("video", "poster"),
    ("audio", "src"), ("embed", "src"), ("object", "data"),
})
LANDING_HOSTS = frozenset({"fonts.googleapis.com", "fonts.gstatic.com"})
EXAMPLE_VERSION_MARKER = re.compile(r"由 answer-me (v\d+\.\d+\.\d+) 產生")
TECHNIQUE_FOLDER = "skills/answer-me/"
USER_DOCS = frozenset({"README.md", "site/index.html"})
# 只在同一行內比對：冒號後的空白（含全形）不得吃掉換行去借下一行的文字。
NOTES_LINE = re.compile(r"^文件與網站：[^\S\n]*\S", re.M)
LOCAL_PATH = re.compile(r"(?<![\w.:/-])(file://[^\s<>\"')]|/Users/|/home/)")
CSS_EXTERNAL = re.compile(r"""url\(\s*["']?\s*((?:https?:)?//[^)"'\s]+)|@import\s+["']((?:https?:)?//[^"']+)""", re.I)


def local_path(target):
    """Path part of a link that points at a file in the same tree; None for URLs and bare anchors."""
    url = urlsplit(target)
    if url.scheme or url.netloc or not url.path:
        return None
    return unquote(url.path)


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
                path = local_path(target)
                if path is None or path.startswith("/"):
                    continue
                if not (doc.parent / path).exists():
                    errors.append(f"{doc.relative_to(root)}:{number}: missing relative link {target}")
    return errors + check_site(root)


def is_external(value):
    return re.match(r"\s*(https?:)?//", value, re.I) is not None


def is_forbidden(value, allowed_hosts):
    return is_external(value) and urlsplit(value.strip()).hostname not in allowed_hosts


def css_urls(text):
    return [(text.count("\n", 0, m.start()), m.group(1) or m.group(2)) for m in CSS_EXTERNAL.finditer(text)]


def srcset_urls(value):
    return [candidate.split()[0] for candidate in value.split(",") if candidate.strip()]


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.attributes = []  # (line, tag, attribute, value)
        self.css = []  # (line, external url)
        self.in_style = False

    def handle_endtag(self, tag):
        if tag == "style":
            self.in_style = False

    def handle_data(self, data):
        if self.in_style:
            start = self.getpos()[0]
            self.css.extend((start + offset, url) for offset, url in css_urls(data))

    def handle_starttag(self, tag, attrs):
        self.in_style = tag == "style"
        line = self.getpos()[0]
        for name, value in attrs:
            if value is not None:
                if name == "style":
                    self.css.extend((line + offset, url) for offset, url in css_urls(value))
                self.attributes.append((line, tag, name, value))


def site_link_error(site, page, value):
    path = local_path(value)
    if path is None:
        return None
    if path.startswith("/"):
        return f"root-absolute link {value}"
    target = (page.parent / path).resolve()
    if not target.is_relative_to(site.resolve()):
        return f"link leaves site {value}"
    if not (target / "index.html" if target.is_dir() else target).exists():
        return f"missing relative link {value}"
    return None


def check_site(root):
    site = root / "site"
    errors = []
    if not site.is_dir():
        return errors
    for path in sorted(p for p in site.rglob("*") if p.is_file()):
        name = path.relative_to(root)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(text.splitlines(), 1):
            if LOCAL_PATH.search(line):
                errors.append(f"{name}:{number}: local path")
        if path.suffix != ".html":
            continue
        parser = SiteParser()
        parser.feed(text)
        landing = path == site / "index.html"
        css_hosts = LANDING_HOSTS if landing else frozenset()
        errors.extend(
            f"{name}:{number}: loads external resource {url}"
            for number, url in parser.css if is_forbidden(url, css_hosts)
        )
        for number, tag, attribute, value in parser.attributes:
            hosts = LANDING_HOSTS if landing and tag == "link" else frozenset()
            if (tag, attribute) not in RESOURCE_ATTRIBUTES:
                urls = []
            elif attribute == "srcset":
                urls = srcset_urls(value)
            else:
                urls = [value]
            errors.extend(f"{name}:{number}: loads external resource {url}" for url in urls if is_forbidden(url, hosts))
            if attribute in ("href", "src"):
                reason = site_link_error(site, path, value)
                if reason:
                    errors.append(f"{name}:{number}: {reason}")
    return errors


def run_git(root, *args, env=None):
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, errors="replace", env=env)


def example_versions(site):
    """範例頁（site/index.html 以外的 .html）標示的產生版本，對應其出現的檔案。"""
    found = {}
    for path in sorted(site.rglob("*.html")):
        if path == site / "index.html":
            continue
        for version in EXAMPLE_VERSION_MARKER.findall(path.read_text(encoding="utf-8")):
            found.setdefault(version, path.relative_to(site.parent))
    return found


def export_snapshot(root, directory, commit=None):
    """把 Git index（commit 給定時為該 commit 的內容）展開到 directory；失敗回傳錯誤訊息，成功回傳 None。
    以暫時 index 取出而非 git archive，內容才不受 .gitattributes 的 export-ignore / export-subst 影響。"""
    env = None
    if commit:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(directory).parent / f"{Path(directory).name}.index"))
        read = run_git(root, "read-tree", commit, env=env)
        if read.returncode:
            return f"cannot read commit {commit}: {read.stderr.strip()}"
    try:
        result = run_git(root, "checkout-index", "--all", f"--prefix={directory}/", env=env)
    finally:
        if env:
            Path(env["GIT_INDEX_FILE"]).unlink(missing_ok=True)
    if result.returncode:
        return result.stderr.strip() or "cannot export snapshot"
    return None


def docs_reminder(root):
    """staged 變更動到技能資料夾卻沒動使用者文件時的提醒；只看 index 相對 HEAD，不需要提醒時回傳 None。
    尚無 HEAD 的初始提交，`git diff --cached` 會以空 tree 為基準，所有 staged 路徑都算變更。"""
    result = run_git(root, "diff", "--cached", "--name-only", "--no-renames", "-z")
    if result.returncode:
        print(f"警告：無法讀取 staged 變更，略過文件同步提醒：{result.stderr.strip()}", file=sys.stderr)
        return None
    paths = set(result.stdout.split("\0")) - {""}
    if any(path in USER_DOCS for path in paths) or not any(path.startswith(TECHNIQUE_FOLDER) for path in paths):
        return None
    docs = " 或 ".join(sorted(USER_DOCS))
    return f"提醒：本次提交改動了 {TECHNIQUE_FOLDER}，請考慮是否同步更新 {docs}。"


def check_release(root, tag, validator):
    """發布檢查：逐項收集失敗；內容一律取自 tag 指向的 commit，不看工作區。"""
    ref = f"refs/tags/{tag}"
    if run_git(root, "check-ref-format", ref).returncode:
        return [f"{tag!r} is not a valid tag name."]
    kind = run_git(root, "cat-file", "-t", ref)
    if kind.returncode:
        return [f"tag {tag} does not exist."]
    errors = []
    if kind.stdout.strip() != "tag":
        errors.append(f"tag {tag} is not an annotated tag (create it with git tag -a).")
    else:
        notes = run_git(root, "for-each-ref", "--format=%(contents)", ref).stdout
        if not NOTES_LINE.search(notes):
            errors.append(f"tag {tag} message needs a line starting with 「文件與網站：」 followed by text.")
    with tempfile.TemporaryDirectory(prefix="answer-me-release-") as directory:
        failure = export_snapshot(root, directory, f"{ref}^{{commit}}")
        if failure:
            return errors + [failure]
        snapshot = Path(directory)
        for version, page in example_versions(snapshot / "site").items():
            if run_git(root, "rev-parse", "-q", "--verify", f"refs/tags/{version}").returncode:
                errors.append(f"{page}: example says generated by answer-me {version}, but tag {version} does not exist.")
        return errors + check(snapshot, validator)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--staged", action="store_true", help="validate staged content, including staged link targets")
    modes.add_argument("--release", metavar="TAG", help="check that TAG can be released: annotated, notes line, example versions, quick checks on its commit")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    codex_root = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    validator = Path(os.environ.get("SKILL_VALIDATOR", str(codex_root / "skills/.system/skill-creator/scripts/quick_validate.py"))).expanduser().resolve()
    if args.release is not None:
        errors = check_release(root, args.release, validator)
    elif args.staged:
        with tempfile.TemporaryDirectory(prefix="answer-me-index-") as directory:
            failure = export_snapshot(root, directory)
            errors = [failure] if failure else check(Path(directory), validator)
        reminder = docs_reminder(root)
        if reminder:
            print(reminder, file=sys.stderr)
    else:
        errors = check(root, validator)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    if args.release is not None:
        suffix = f" (release {args.release})"
    elif args.staged:
        suffix = " (staged snapshot)"
    else:
        suffix = ""
    print("PASS: skill frontmatter, display metadata, relative documentation links, and site pages" + suffix)
    return 0


if __name__ == "__main__":
    sys.exit(main())
