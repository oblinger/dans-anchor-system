#!/usr/bin/env python3
"""Warden re-evaluation economy (F215) — the significant-edit gate's substrate.

An LLM-judged (or otherwise expensive python-body) rule must not re-run on
every keystroke. The rule throttles itself with an ordinary condition over the
change — `if:: file.diff.lines > 15` — and this module supplies what that
condition reads and what the engine remembers:

  RevalStore — per `(rule_id, file_path)`: the content hash + text of the
      revision the rule LAST EVALUATED, and the verdict that evaluation
      produced. While the gate suppresses re-judgment the stored verdict
      persists (silence is never read as a pass — F215 Q1); a full evaluation
      overwrites the record wholesale. Because the record only advances when
      the rule actually evaluates, sub-threshold edits ACCUMULATE in the diff
      until they cross the threshold together.

  FileView / DiffView — the lazy `file` object a gated rule's guard reads.
      `file.diff` is the change since this rule last evaluated the file
      (distinct from `event.diff`, the current write); on first pass it is the
      whole file, so any positive threshold passes and the rule evaluates
      fully (F215 Q3 — lazy first fire, no adopt-time sweep). Reads never
      raise (the R4 read-discipline `warden_agent` established).

The engine ties it together in `warden_fire.fire`: a `file_bearing` rule gets
`ctx.file` bound per (rule, event-file) before its guards run, and
`mark_evaluated` is called only after its body actually executes.
"""
from __future__ import annotations

import difflib
import hashlib
import json
import os
from pathlib import Path


def warden_home() -> Path:
    return Path(os.environ.get("WARDEN_HOME", str(Path.home() / ".warden")))


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()[:16]


# ── the per-(rule, file) last-evaluated store ────────────────────────────────

class RevalStore:
    """`reval.json` under WARDEN_HOME — {rule_id \\x00 file_path: record}.

    record = {"hash": …, "text": …, "verdict": …}. Written atomically
    (tmp + rename); reloaded when the file changes on disk (the daemon holds
    one warm instance, but a `warden compile`-style external reset must win).
    """

    def __init__(self, home: Path | None = None):
        self.path = (home or warden_home()) / "reval.json"
        self._data: dict[str, dict] = {}
        self._mtime: int = -1
        self._load()

    @staticmethod
    def _key(rule_id: str, file_path: Path | str) -> str:
        return f"{rule_id}\x00{Path(file_path).resolve()}"

    def _load(self) -> None:
        try:
            stat = self.path.stat()
        except OSError:
            self._data, self._mtime = {}, -1
            return
        if stat.st_mtime_ns == self._mtime:
            return
        try:
            self._data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self._data = {}
        self._mtime = stat.st_mtime_ns

    def record(self, rule_id: str, file_path: Path | str) -> dict | None:
        """The last-evaluated record for (rule, file), or None on first pass."""
        self._load()
        return self._data.get(self._key(rule_id, file_path))

    def verdict(self, rule_id: str, file_path: Path | str):
        """The persisted verdict — what the last full evaluation produced.
        Serving this while the gate suppresses re-judgment is the F215 Q1
        persistence rule: a still-present finding is not cleared by a
        one-line edit elsewhere in the file."""
        rec = self.record(rule_id, file_path)
        return rec.get("verdict") if rec else None

    def mark_evaluated(self, rule_id: str, file_path: Path | str,
                       text: str, verdict=None) -> None:
        """Advance the record to `text` — called ONLY after the rule's body
        actually executed against that revision."""
        self._load()
        self._data[self._key(rule_id, file_path)] = {
            "hash": _hash(text), "text": text, "verdict": verdict}
        tmp = self.path.with_suffix(".json.tmp")
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp.write_text(json.dumps(self._data), encoding="utf-8")
            os.replace(tmp, self.path)
            self._mtime = self.path.stat().st_mtime_ns
        except OSError:
            pass  # fail-safe: a store write failure must never break the fire


_STORE: RevalStore | None = None


def store() -> RevalStore:
    """The process-wide store (the daemon's warm instance)."""
    global _STORE
    if _STORE is None or _STORE.path != warden_home() / "reval.json":
        _STORE = RevalStore()
    return _STORE


# ── the lazy views a gated rule reads ────────────────────────────────────────

class DiffView:
    """The change between the last-evaluated revision and the current text.
    Members are computed on first access and cached; reads never raise."""

    def __init__(self, prior: str | None, current: str):
        self._prior = prior
        self._current = current
        self._delta: tuple[list[str], list[str]] | None = None

    def _compute(self) -> tuple[list[str], list[str]]:
        if self._delta is None:
            prior_lines = (self._prior or "").splitlines()
            cur_lines = self._current.splitlines()
            if self._prior is None:
                self._delta = (cur_lines, [])       # first pass: the whole file
            else:
                added, removed = [], []
                for ln in difflib.unified_diff(prior_lines, cur_lines, lineterm=""):
                    if ln.startswith("+") and not ln.startswith("+++"):
                        added.append(ln[1:])
                    elif ln.startswith("-") and not ln.startswith("---"):
                        removed.append(ln[1:])
                self._delta = (added, removed)
        return self._delta

    @property
    def added(self) -> list[str]:
        return self._compute()[0]

    @property
    def removed(self) -> list[str]:
        return self._compute()[1]

    @property
    def lines(self) -> int:
        added, removed = self._compute()
        return len(added) + len(removed)

    @property
    def text(self) -> str:
        if self._prior is None:
            return self._current
        return "\n".join(difflib.unified_diff(
            (self._prior or "").splitlines(), self._current.splitlines(),
            lineterm=""))


class FileView:
    """The `file` object bound per (rule, event-file) at fire time. Root-level
    members only in v1 — what the gate reads (`.diff`) plus the cheap stat/text
    members a threshold ratio needs. Reads never raise."""

    def __init__(self, rule_id: str, path: Path | str,
                 reval: RevalStore | None = None):
        self._rule_id = rule_id
        self._path = Path(path)
        self._reval = reval or store()
        self._text: str | None = None
        self._diff: DiffView | None = None

    @property
    def path(self) -> str:
        return str(self._path)

    @property
    def name(self) -> str:
        return self._path.name

    @property
    def exists(self) -> bool:
        try:
            return self._path.is_file()
        except OSError:
            return False

    @property
    def text(self) -> str:
        if self._text is None:
            try:
                self._text = self._path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                self._text = ""
        return self._text

    @property
    def lines(self) -> list[str]:
        return self.text.splitlines()

    @property
    def size(self) -> int:
        try:
            return self._path.stat().st_size
        except OSError:
            return 0

    @property
    def diff(self) -> DiffView:
        if self._diff is None:
            rec = self._reval.record(self._rule_id, self._path)
            self._diff = DiffView(rec["text"] if rec else None, self.text)
        return self._diff

    def mark_evaluated(self, verdict=None) -> None:
        """Advance the last-evaluated record to the revision this view read."""
        self._reval.mark_evaluated(self._rule_id, self._path, self.text, verdict)
