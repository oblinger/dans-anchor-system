#!/usr/bin/env python3
"""T119 blast-radius measurement — report-only, writes nothing.

Runs the four checks Dan's T115-Q2 ruling names as *true of skill docs
specifically* across the whole skill corpus, and counts findings by class, so
the explosion is a known number before any rule is written.

    path-resolves        every filesystem path named in the doc exists
    artifact-exists      every [[wiki-link]] resolves somewhere in the vault
    dead-anchor          a reference to an anchor that has been retired
    command-runnable     every command named as runnable is on PATH / on disk

Deliberately NOT a ruleset, and named `probe-` rather than `test-` so no suite
picks it up: it reports, asserts nothing, and writes nothing. T119 says measure
first, arm audit-only second, promote to the write moment third.

MEASURED 2026-08-13 over 252 docs: **1097 findings before the instrument was
calibrated, 114 after.** The first number was almost entirely the probe's own
noise, and each class of it is recorded here because the same mistakes are the
ones the eventual `R-skill-doc` ruleset has to avoid making:

  * `/ask`, `/groom`, `/architect` are SLASH-COMMANDS, not absolute paths. 691
    of the original path findings were this one error. A path claim needs a real
    root or at least two segments -- see `is_path_claim`.
  * `[[F<n>]]`, `[[{slug} Backlog]]`, `[[basename]]`, `[[wiki-link]]` are
    ILLUSTRATIONS of the notation inside a spec, not links anyone expects to
    resolve -- see `looks_like_a_hole`. Anything inside a fence or a code span
    is the same thing and is stripped before the link pass.
  * `import`, `tell application`, `end repeat` are python and applescript
    sitting inside fences LABELLED bash. Reporting them as missing commands
    says nothing about the corpus.

A residual false-positive class survives and is left visible on purpose,
because it is a question for the rule rather than for the probe: docs
legitimately name HYPOTHETICAL paths in prose (`/old-path/notes.md`,
`~/bin/myapp`, `/Applications/MyApp.app`, `~/ob/kmr/LST/Weekly/YYYY-Www.md`).
About 20 of the 65 path findings are these. The rule will have to say how an
example path declares itself -- a fence, a marker, a naming convention -- or it
will cry wolf on every doc that teaches by example.
"""
import os
import pathlib
import re
import shutil
import sys
from collections import defaultdict

SKILLS = pathlib.Path.home() / ".claude" / "skills"
VAULT = pathlib.Path.home() / "ob" / "kmr"

# ---------------------------------------------------------------- vault index
print("building vault basename index...", file=sys.stderr)
index = set()
for p in VAULT.rglob("*.md"):
    index.add(p.stem.lower())
    index.add(p.name.lower())
for p in VAULT.rglob("*"):
    if p.is_dir():
        index.add(p.name.lower())
print(f"  {len(index)} unique names", file=sys.stderr)

# Anchors retired in place carry a two-digit creation-year prefix (ANC Standard
# § Anchor retirement: SKD -> 25SKD). A doc naming the BARE form is naming a
# thing that no longer exists under that name.
RETIRED = {}
for dot in VAULT.rglob(".anchor"):
    try:
        m = re.search(r"^\s*slug\s*:\s*(.+?)\s*$", dot.read_text(encoding="utf-8"), re.M)
    except OSError:
        continue
    if m:
        s = m.group(1).strip().strip("\"'")
        r = re.match(r"^(\d{2})([A-Z]{2,})$", s)
        if r:
            RETIRED[r.group(2)] = s
# CAE was retired by deletion rather than by year-prefixing, so it is not
# discoverable from the corpus and is named explicitly.
RETIRED.setdefault("CAE", "(deleted 2026-08)")

findings = defaultdict(list)

PATH_RE = re.compile(r"`([~./][^`\s]{2,}|/[A-Za-z][^`\s]{2,})`")
WIKI_RE = re.compile(r"\[\[([^\]|#^]+)")
CMD_RE = re.compile(r"^\s*(?:\$\s*)?([a-z][a-z0-9_-]{1,20})\s", re.M)

FENCE_RE = re.compile(r"```.*?```", re.S)
SPAN_RE = re.compile(r"`[^`\n]*`")
# A slash-command (`/ask`, `/groom`) is a single segment and is NOT a path.
REAL_ROOTS = ("~/", "./", "../", "/Users/", "/Volumes/", "/tmp/", "/opt/",
              "/etc/", "/var/", "/usr/", "/private/", "/Applications/")
# Fences whose body is plainly not shell, however they are labelled.
NOT_SHELL = ("import ", "tell application", "from __future__", "def ",
             "on run", "#!/usr/bin/env python")
PY_KEYWORDS = {"import", "from", "def", "class", "return", "print", "with",
               "try", "except", "raise", "assert", "lambda", "yield", "pass",
               "tell", "end", "on", "repeat", "set", "get", "make"}


def is_path_claim(cand: str) -> bool:
    """A backticked token is a claim about the filesystem only if it names a
    place. `/ask` is a slash-command; `~/bin/ctrl` is a path."""
    if cand.startswith(REAL_ROOTS):
        return True
    return cand.startswith("/") and cand.count("/") >= 2


def looks_like_a_hole(name: str) -> bool:
    """`F<n>`, `{slug} Backlog`, `<derived-name>.svg`, `basename`, `wiki-link` --
    illustrative text inside a spec, not a link anyone expects to resolve."""
    if any(c in name for c in "<>{}\\"):
        return True
    if name in {"...", "…"}:
        return True
    # A generic lowercase noun-phrase naming a CONCEPT, not a document.
    return name.islower() and not name.startswith(("f", "t")) and " " not in name.strip("-")

docs = sorted(SKILLS.rglob("*.md"))
for doc in docs:
    rel = doc.relative_to(SKILLS)
    try:
        text = doc.read_text(encoding="utf-8")
    except OSError:
        continue
    # A link or path shown INSIDE a fence or a code span is an illustration of
    # the notation, not an assertion that the thing exists. Strip both before
    # the wiki-link pass; the path pass needs the spans, so it runs on `text`.
    prose = SPAN_RE.sub(" ", FENCE_RE.sub(" ", text))

    # ---- path-resolves
    for raw in PATH_RE.findall(text):
        cand = raw.split("#")[0].rstrip(".,;:)")
        if any(c in cand for c in "{}*<>") or cand.endswith("/"):
            continue          # a template hole or a glob is not a claim
        if not is_path_claim(cand):
            continue          # `/ask` is a slash-command, not a path
        p = pathlib.Path(os.path.expanduser(cand))
        if not p.is_absolute():
            continue          # relative paths have no stated base; out of scope
        if not p.exists():
            findings["path-resolves"].append((str(rel), cand))

    # ---- artifact-exists
    for name in WIKI_RE.findall(prose):
        n = name.strip()
        if not n or n.startswith("#") or looks_like_a_hole(n):
            continue
        base = n.split("/")[-1].strip()
        if base.lower() not in index and f"{base.lower()}.md" not in index:
            findings["artifact-exists"].append((str(rel), n))

    # ---- dead-anchor
    for bare, now in RETIRED.items():
        if re.search(rf"\[\[{re.escape(bare)}(?:[\]|#])", prose):
            findings["dead-anchor"].append((str(rel), f"[[{bare}]] -> {now}"))

    # ---- command-runnable: only inside ```bash / ```sh fences
    for fence in re.findall(r"```(?:bash|sh|shell)\n(.*?)```", text, re.S):
        if any(marker in fence for marker in NOT_SHELL):
            continue          # a mislabelled python / applescript fence
        for line in fence.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = CMD_RE.match(line + " ")
            if not m:
                continue
            cmd = m.group(1)
            if cmd in {"cd", "if", "for", "while", "then", "else", "fi", "do",
                       "done", "echo", "export", "set", "source", "return",
                       "exit"} or cmd in PY_KEYWORDS:
                continue
            if shutil.which(cmd) is None:
                findings["command-runnable"].append((str(rel), cmd))

# ---------------------------------------------------------------- report
print()
print(f"T119 blast radius — {len(docs)} skill docs under ~/.claude/skills/")
print("=" * 78)
total = 0
for cls in ("path-resolves", "artifact-exists", "dead-anchor", "command-runnable"):
    items = findings[cls]
    uniq_docs = len({d for d, _ in items})
    total += len(items)
    print(f"\n{cls:20} {len(items):5} findings across {uniq_docs} docs")
    seen = defaultdict(int)
    for d, what in items:
        seen[what] += 1
    for what, n in sorted(seen.items(), key=lambda kv: -kv[1])[:12]:
        print(f"    {n:4}x  {what[:88]}")
    if len(seen) > 12:
        print(f"    ... and {len(seen) - 12} more distinct")

print("\n" + "=" * 78)
print(f"TOTAL {total} findings")
print("\nworst docs:")
per = defaultdict(int)
for cls, items in findings.items():
    for d, _ in items:
        per[d] += 1
for d, n in sorted(per.items(), key=lambda kv: -kv[1])[:15]:
    print(f"  {n:4}  {d}")
