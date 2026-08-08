#!/usr/bin/env python3
"""Read the specimens out of `design/Template Examples.md`.

The verification standard for F303 M3 is the real corpus, not invented
fixtures, so every stencil and every specimen document this suite matches is
lifted verbatim from that file's own delimited blocks.  If the corpus changes,
the tests change with it — which is the point.
"""
from __future__ import annotations

import re
from pathlib import Path


def repo_root() -> Path:
    """The dans-anchor-system repo root, found from this file's location."""
    return Path(__file__).resolve().parents[2]


def vault_root() -> Path:
    """`~/ob/kmr` — found by walking up to the directory holding `SYS/`."""
    p = repo_root()
    for anc in [p, *p.parents]:
        if (anc / "SYS").is_dir() and (anc / "AT").is_dir():
            return anc
    raise RuntimeError("vault root not found above " + str(p))


CORPUS = repo_root() / "design" / "Template Examples.md"

_BLOCK = re.compile(
    r"<!-- begin (example|proposal) ([^\s>]+) -->\n(.*?)\n<!-- end \1 \2 -->",
    re.S)
_LABEL = re.compile(r"^\*\*(Example|Proposal) (T\d+\.[A-Za-z])\*\*")


def blocks(text: str | None = None) -> dict[str, str]:
    """Every delimited block, keyed by its label (`T1.a`, `T3.A`, ...)."""
    text = text if text is not None else CORPUS.read_text(encoding="utf-8")
    return {m.group(2): m.group(3) for m in _BLOCK.finditer(text)}


def fenced_tree(label: str, text: str | None = None) -> list[str]:
    """Member names from the fenced file-tree following `**Example/Proposal X**`.

    T2.A and T5.A are folder stencils, drawn as trees rather than delimited
    blocks, so they need their own reader.
    """
    text = text if text is not None else CORPUS.read_text(encoding="utf-8")
    lines = text.split("\n")
    for i, line in enumerate(lines):
        m = _LABEL.match(line)
        if not m or m.group(2) != label:
            continue
        for j in range(i, min(i + 12, len(lines))):
            if lines[j].strip().startswith("```"):
                body = []
                for k in range(j + 1, len(lines)):
                    if lines[k].strip().startswith("```"):
                        return _tree_members(body)
                    body.append(lines[k])
    raise KeyError("no fenced tree for " + label)


_GLYPH = re.compile(r"^[\s│]*(?:├──|└──)\s*")


def _tree_members(body: list[str]) -> list[str]:
    out = []
    for line in body:
        if not _GLYPH.match(line):
            continue
        out.append(_GLYPH.sub("", line).rstrip())
    return out


def read(rel: str) -> str:
    """A real vault file, by path relative to the vault root."""
    return (vault_root() / rel).read_text(encoding="utf-8")


def listdir(rel: str) -> list[str]:
    return sorted(p.name for p in (vault_root() / rel).iterdir()
                  if not p.name.startswith("."))


if __name__ == "__main__":
    b = blocks()
    print(f"{len(b)} delimited blocks in {CORPUS.name}: {', '.join(sorted(b))}")
    print("T2.A tree:", fenced_tree("T2.A"))
    print("T5.A tree:", fenced_tree("T5.A"))
    print("vault root:", vault_root())
