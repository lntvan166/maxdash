#!/usr/bin/env python3
"""Repo checks for maxdash: private-data leaks, source labels, relative links.

Usage: python3 tools/lint.py [--leaks FILE]... [PATH]...
With no PATH it checks every tracked or untracked-but-not-ignored file.
Rules: leak, label (Source columns), link (relative links), ref (paths in the skill).
Prints `path:line: rule: detail` per finding and exits 1 if there are any.

Private leak patterns (names, domains, serials) never live in this file:
put one regex per line in tools/leaks.local.txt (git-ignored).
"""
import os
import re
import subprocess
import sys
from collections import namedtuple

Finding = namedtuple("Finding", "path line rule detail")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_LEAKS = os.path.join(ROOT, "tools", "leaks.local.txt")

# Public patterns: things that only appear when text was pasted from a private codebase or setup.
PUBLIC_LEAKS = [
    r"\b\w+\.swift:\d+",  # source line references
    r"\bcloudflared\b",
    r"CF-Access-Client",
]

LABELS = ("observed", "partly observed", "documented — not yet observed", "assumed")

TEXT_EXT = {".md", ".html", ".css", ".json", ".js", ".mjs", ".py", ".yml", ".yaml", ".txt", ".mdc", ".svg"}
SKIP_DIRS = {".git", "node_modules", ".superpowers"}
SKIP_REL = ("docs/superpowers/", "tools/fixtures/", "media/raw/")
SELF = {"tools/lint.py", "tools/test_lint.py", "tools/leaks.local.txt"}

LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def load_leaks(files):
    pats = list(PUBLIC_LEAKS)
    for f in files:
        if os.path.exists(f):
            with open(f, encoding="utf-8") as fh:
                pats += [l.strip() for l in fh if l.strip() and not l.startswith("#")]
    return [re.compile(p, re.IGNORECASE) for p in pats]


def check_leaks(path, lines, leaks):
    for n, line in enumerate(lines, 1):
        for p in leaks:
            if p.search(line):
                yield Finding(path, n, "leak", p.pattern)
                break


def cells(row):
    return [c.strip() for c in re.split(r"(?<!\\)\|", row.strip().strip("|"))]


def check_labels(path, lines):
    col = None
    for n, line in enumerate(lines, 1):
        if not line.lstrip().startswith("|"):
            col = None
            continue
        row = cells(line)
        if col is None:
            lower = [c.lower() for c in row]
            col = lower.index("source") if "source" in lower else -1
            continue
        if col < 0 or set(line.strip()) <= set("|-: "):
            continue
        cell = row[col] if col < len(row) else ""
        if not cell.lower().startswith(LABELS):
            yield Finding(path, n, "label", cell or "(empty)")


def check_links(path, lines):
    base = os.path.dirname(path)
    for n, line in enumerate(lines, 1):
        for target in LINK.findall(line):
            if re.match(r"^(https?:|mailto:|#)", target):
                continue
            target = target.split("#", 1)[0]
            if target and not os.path.exists(os.path.join(base, target)):
                yield Finding(path, n, "link", target)


TICK = re.compile(r"`([^`\s]+/[^`\s]*)`")


def is_skill(path):
    p = path.replace(os.sep, "/")
    return os.path.basename(p) == "AGENTS.md" or "/.claude/skills/" in p


def check_refs(path, lines):
    """Backticked repo paths in the skill must exist (relative to the file, or to the repo root)."""
    base = os.path.dirname(path)
    for n, line in enumerate(lines, 1):
        for ref in TICK.findall(line):
            if ref.startswith(("../", "http", "~")) or "<" in ref:
                continue
            if not any(os.path.exists(os.path.join(b, ref)) for b in (base, ROOT)):
                yield Finding(path, n, "ref", ref)


def check_file(path, leaks):
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except (UnicodeDecodeError, OSError):
        return []
    out = list(check_leaks(path, lines, leaks))
    if path.endswith(".md"):
        out += check_labels(path, lines)
        out += check_links(path, lines)
        if is_skill(path):
            out += check_refs(path, lines)
    return out


def wanted(rel):
    rel = rel.replace(os.sep, "/")
    return (
        os.path.splitext(rel)[1] in TEXT_EXT
        and rel not in SELF
        and not rel.startswith(SKIP_REL)
        and not any(part in SKIP_DIRS for part in rel.split("/"))
    )


def expand(paths):
    for p in paths:
        if os.path.isdir(p):
            for d, dirs, files in os.walk(p):
                dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
                for f in sorted(files):
                    full = os.path.abspath(os.path.join(d, f))
                    inside = full.startswith(ROOT + os.sep)
                    if wanted(os.path.relpath(full, ROOT if inside else p)):
                        yield full
        else:
            yield p


def repo_files():
    out = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.split()
    return [os.path.join(ROOT, f) for f in out if wanted(f) and os.path.exists(os.path.join(ROOT, f))]


def check(paths, leak_files=None):
    leaks = load_leaks(leak_files if leak_files is not None else [LOCAL_LEAKS])
    findings = []
    for f in expand(paths):
        findings += check_file(f, leaks)
    return findings


def main(argv):
    leak_files, paths = [], []
    it = iter(argv)
    for a in it:
        if a == "--leaks":
            leak_files.append(next(it))
        else:
            paths.append(a)
    findings = check(paths or repo_files(), leak_files or None)
    for f in findings:
        print(f"{os.path.relpath(f.path)}:{f.line}: {f.rule}: {f.detail}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
