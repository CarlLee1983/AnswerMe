#!/usr/bin/env python3
"""Read-only lead index over an existing Understand Anything knowledge graph.

The graph is an index, not evidence: node summaries and edges (especially
LLM-inferred `calls`) are claims that point to places worth reading. Anything
cited to the user must be verified in the source files.

This helper never installs, builds, analyses, writes files, or uses the
network. It reads `<root>/.ua/knowledge-graph.json` (legacy:
`.understand-anything/`) and runs read-only `git` subprocesses to report how
far the working tree has drifted from the commit the graph was built at.

Usage: ua_graph.py [--root DIR] {check | find TERM | neighbors NODE_ID}
Exit codes: 0 usable graph, 1 unknown node, 2 graph missing/invalid/incompatible.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

GRAPH_DIRS = (".ua", ".understand-anything")
MAX_LINES = 20
MAX_TEXT = 200
GIT_TIMEOUT = 30
COMMIT_RE = re.compile(r"[0-9a-fA-F]{7,64}")
REMINDER = ("note: graph edges and summaries are claims from the graph (LLM-inferred calls); "
            "verify at source before citing.")


class GraphError(Exception):
    def __init__(self, status, reason):
        super().__init__(reason)
        self.status, self.reason = status, reason


def git(root, *args):
    """Return stdout of a read-only git command, or None on any failure.

    --no-optional-locks keeps `git status` from refreshing (rewriting) .git/index.
    """
    try:
        done = subprocess.run(["git", "--no-optional-locks", *args], cwd=root, capture_output=True,
                              text=True, timeout=GIT_TIMEOUT)
    except (OSError, subprocess.SubprocessError):
        return None
    return done.stdout if done.returncode == 0 else None


def safe(value):
    """Escape control characters and cap length so graph text cannot forge output lines."""
    return json.dumps(str(value)[:MAX_TEXT], ensure_ascii=False)[1:-1]


def locate(root):
    for name in GRAPH_DIRS:
        path = root / name / "knowledge-graph.json"
        if path.is_file():
            return path
    raise GraphError("missing", f"no .ua/knowledge-graph.json under {root}; read the source directly")


def require_objects(graph, field, keys):
    items = graph.get(field)
    if not isinstance(items, list):
        raise GraphError("invalid", f"{field} must be a list")
    for item in items:
        if not isinstance(item, dict) or not all(isinstance(item.get(k), str) for k in keys):
            raise GraphError("invalid", f"{field} entries must be objects with string {', '.join(keys)}")


def load(path):
    try:
        graph = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, RecursionError) as error:
        raise GraphError("invalid", f"cannot parse graph: {safe(error)}") from error
    if not isinstance(graph, dict):
        raise GraphError("invalid", "top level must be an object")
    version = graph.get("version")
    if not isinstance(version, str):
        raise GraphError("invalid", "version must be a string")
    if version.split(".")[0] != "1":
        raise GraphError("incompatible", f"version {safe(version)}, expected major 1")
    if not isinstance(graph.get("project", {}), dict):
        raise GraphError("invalid", "project must be an object")
    require_objects(graph, "nodes", ("id",))
    require_objects(graph, "edges", ("source", "target", "type"))
    if any(not isinstance(n.get("filePath", ""), str) for n in graph["nodes"]):
        raise GraphError("invalid", "nodes filePath must be a string")
    return graph


def graph_commit(graph, path):
    commit = (graph.get("project") or {}).get("gitCommitHash")
    meta = path.parent / "meta.json"
    if not commit and meta.is_file():
        try:
            commit = json.loads(meta.read_text(encoding="utf-8")).get("gitCommitHash")
        except (OSError, ValueError, RecursionError, AttributeError):
            commit = None
    return commit if isinstance(commit, str) and COMMIT_RE.fullmatch(commit) else None


def working_tree_changes(root):
    """Paths with uncommitted changes (renames include the old path), minus graph dirs."""
    excludes = [f":(exclude){name}" for name in GRAPH_DIRS]
    out = git(root, "status", "--porcelain", "-z", "--untracked-files=all", "--", ".", *excludes)
    paths, entries = [], (out or "").split("\0")
    i = 0
    while i < len(entries):
        entry = entries[i]
        if len(entry) > 3:
            paths.append(entry[3:])
            if "R" in entry[:2] or "C" in entry[:2]:  # next token is the source path
                i += 1
                paths.append(entries[i])
        i += 1
    return paths


def freshness(root, commit):
    """Return (status, head, changed paths)."""
    head = (git(root, "rev-parse", "HEAD") or "").strip() or None
    if not commit or not head or git(root, "cat-file", "-e", f"{commit}^{{commit}}") is None:
        return "unknown", head, None
    full = (git(root, "rev-parse", f"{commit}^{{commit}}") or "").strip()
    prefix = (git(root, "rev-parse", "--show-prefix") or "").strip()
    changed = relative_to_root(working_tree_changes(root), prefix)
    if full == head:
        return ("dirty" if changed else "fresh"), head, changed
    excludes = [f":(exclude){name}" for name in GRAPH_DIRS]
    diff = git(root, "diff", "--name-only", "--no-renames", "--no-relative", "-z", full, head,
               "--", ".", *excludes) or ""
    committed = relative_to_root(filter(None, diff.split("\0")), prefix)
    return "stale", head, sorted(set(committed) | set(changed))


def relative_to_root(paths, prefix):
    """Git reports repository-relative paths; graph paths are relative to the analysed root."""
    return [p[len(prefix):] for p in paths if p.startswith(prefix)]


def short(value):
    return value[:8] if value else "none"


def location(node):
    if not node or not node.get("filePath"):
        return "-"
    lines = node.get("lineRange")
    ints = isinstance(lines, list) and len(lines) == 2 and all(type(n) is int for n in lines)
    suffix = f":{lines[0]}-{lines[1]}" if ints else ""
    return safe(f"{node['filePath']}{suffix}")


def escapes_root(path):
    return os.path.isabs(path) or ".." in re.split(r"[\\/]", path)


def exists(root, path):
    try:
        return (root / path).exists()
    except (OSError, ValueError):
        return False


def flags(node, root, changed):
    path = node.get("filePath") if node else None
    found = []
    if path and escapes_root(path):
        return "[outside root]"
    if path and path in (changed or ()):
        found.append("[changed since graph]")
    if path and not exists(root, path):
        found.append("[missing now]")
    return " ".join(found)


def line(*parts):
    return "  ".join(p for p in parts if p)


def cmd_check(ctx):
    graph, nodes = ctx["graph"], ctx["nodes"]
    dangling = sum(1 for e in graph["edges"] if e["source"] not in nodes or e["target"] not in nodes)
    print(f"graph: {ctx['path'].relative_to(ctx['root'])}")
    print(f"version {safe(graph['version'])}, {len(graph['nodes'])} nodes, {len(graph['edges'])} edges")
    print(f"graph commit: {short(ctx['commit'])}, HEAD: {short(ctx['head'])}")
    changed = ctx["changed"]
    if changed is None:
        print("changed paths: not computed (status unknown); treat every location as unverified")
    else:
        print(f"changed paths: {len(changed)}")
    for item in (changed or [])[:MAX_LINES]:
        print(f"  {safe(item)}")
    if changed and len(changed) > MAX_LINES:
        print(f"  {len(changed) - MAX_LINES} more; find/neighbors flag affected nodes")
    print(f"dangling edges: {dangling}")
    return 0


def cmd_find(ctx, term):
    needle = term.lower()
    hits = [n for n in ctx["graph"]["nodes"]
            if any(needle in str(n.get(k) or "").lower() for k in ("id", "name", "filePath"))]
    if not hits:
        print(f"no matches for {safe(term)!r}")
    for n in hits[:MAX_LINES]:
        print(line(safe(n["id"]), location(n), flags(n, ctx["root"], ctx["changed"])))
    if len(hits) > MAX_LINES:
        print(f"{len(hits) - MAX_LINES} more matches omitted; narrow the term")
    return 0


def cmd_neighbors(ctx, node_id):
    nodes = ctx["nodes"]
    if node_id not in nodes:
        print(f"unknown node id: {safe(node_id)}")
        return 1
    rows = []
    for e in ctx["graph"]["edges"]:
        for direction, own, other_id in (("out", "source", e["target"]), ("in", "target", e["source"])):
            if e[own] != node_id:
                continue
            other = nodes.get(other_id)
            desc = f"-- {safe(e['description'])}" if e.get("description") else ""
            rows.append(line(direction, safe(e["type"]), safe(other_id), location(other),
                             flags(other, ctx["root"], ctx["changed"]), desc))
    for row in rows[:MAX_LINES]:
        print(row)
    if len(rows) > MAX_LINES:
        print(f"{len(rows) - MAX_LINES} more edges omitted")
    return 0


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Query an Understand Anything graph as a lead index.")
    parser.add_argument("--root", default=".", help="repository root (default: cwd)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check")
    sub.add_parser("find").add_argument("term")
    sub.add_parser("neighbors").add_argument("node_id")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    root = Path(args.root).resolve()
    try:
        path = locate(root)
        graph = load(path)
    except GraphError as error:
        print(f"status: {error.status}\nreason: {error.reason}\n{REMINDER}")
        return 2
    commit = graph_commit(graph, path)
    status, head, changed = freshness(root, commit)
    print(f"status: {status}")
    ctx = {"root": root, "path": path, "graph": graph, "commit": commit, "head": head, "changed": changed,
           "nodes": {n["id"]: n for n in graph["nodes"]}}
    if args.command == "check":
        code = cmd_check(ctx)
    elif args.command == "find":
        code = cmd_find(ctx, args.term)
    else:
        code = cmd_neighbors(ctx, args.node_id)
    print(REMINDER)
    return code


if __name__ == "__main__":
    sys.exit(main())
