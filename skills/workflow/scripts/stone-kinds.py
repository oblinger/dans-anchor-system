#!/usr/bin/env python3
"""Stone-kind declarations, read from the markdown table in `DAS Stone.md`.

**Why this is markdown and not JSON.** Until 2026-08-28 these declarations
lived in `facets/DAS Stone Kinds.json` — the single non-markdown facet in a
set of 77. The duplication that arrangement invited had already gone wrong:
`DAS Stone.md` carried the same declarations as a human-readable table (it had
to; a reader needs them), `sleeper` shipped into the JSON, and the markdown
table kept saying *"they are the two that ship"* with nobody noticing. The
JSON did not prevent a second copy — it created one, and then the two
disagreed. Dan's ruling, 2026-08-28: *"The whole DAS system is supposed to be
a markdown 1st system... so I'm questioning whether or not we should even have
a JSON file here."*

**What stayed configuration.** Where the table lives is NOT hardcoded — it is
`stone_kinds_doc` in `~/.config/anchor-system/global.yaml`, the same F080
namespace `vault_root` and `user_env_doc` come from. Same ruling: *"the stone
table itself should actually be markdown, but the indicator of where it is
should not be hard coded."* The table is content; its address is config.

Borrowed by `stone` and by `audit-plan.py` (never copied — T120), so the two
cannot drift apart the way the JSON and the table did.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

CONFIG_PATH = Path.home() / ".config" / "anchor-system" / "global.yaml"

# Used only when `stone_kinds_doc` is absent from config — the DAS-relative
# location the system ships with, resolved from this file (…/skills/workflow/
# scripts/ -> dans-anchor-system/). Documented as a default in global.yaml
# exactly as `user_env_doc` documents its own; it is not a silent fallback for
# a malformed table, which always raises.
DEFAULT_DOC = Path(__file__).resolve().parents[3] / "facets" / "DAS Stone.md"

# The row labels the table must carry, mapped to the config key each produces.
# `stone file` yields two keys (prefix, digits) and `header display` yields two
# (header_alias, header_line), so the mapping is not one-to-one.
_REQUIRED_ROWS = ("folder", "control file", "stone file", "stone display",
                  "header display")


class StoneKindsError(Exception):
    """Malformed or unreachable kind table. Never swallowed — a reader that
    cannot see its declarations has verified nothing (the vacuous-green shape
    this corner of DAS has hit repeatedly)."""


def _cells(line: str) -> list[str]:
    """Split one markdown table row, honouring `\\|` as an escaped pipe."""
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    parts = re.split(r"(?<!\\)\|", body)
    return [p.strip().replace("\\|", "|") for p in parts]


def _unwrap(cell: str) -> str:
    """Strip the backticks the table wraps every value in."""
    c = cell.strip()
    if len(c) >= 2 and c.startswith("`") and c.endswith("`"):
        c = c[1:-1]
    return c.strip()


def resolve_doc_path() -> Path:
    """`stone_kinds_doc` from F080 config, else the DAS-relative default."""
    if CONFIG_PATH.is_file():
        try:
            import yaml
            with CONFIG_PATH.open() as f:
                data = yaml.safe_load(f) or {}
        except Exception as e:
            raise StoneKindsError(f"{CONFIG_PATH} unreadable: {e}")
        raw = data.get("stone_kinds_doc")
        if raw:
            return Path(os.path.expanduser(str(raw)))
    return DEFAULT_DOC


def parse_kind_table(text: str, where: str = "<text>") -> dict:
    """`{kind: cfg}` from the first table whose row labels are the kind fields.

    The table is identified by carrying a `folder` row, not by position, so
    prose may be added above or below it freely."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if not line.lstrip().startswith("|"):
            continue
        header = _cells(line)
        if len(header) < 2 or header[0] != "":
            continue
        kinds = [_unwrap(c) for c in header[1:]]
        if not all(re.fullmatch(r"[a-z][a-z0-9_-]*", k or "") for k in kinds):
            continue
        rows: dict[str, list[str]] = {}
        for nxt in lines[i + 1:]:
            if not nxt.lstrip().startswith("|"):
                break
            cs = _cells(nxt)
            if set("".join(cs[0:1])) <= set("-: "):   # the |---| separator
                continue
            label = _unwrap(cs[0]).lower()
            if label:
                rows[label] = [_unwrap(c) for c in cs[1:]]
        if "folder" not in rows:
            continue
        missing = [r for r in _REQUIRED_ROWS if r not in rows]
        if missing:
            raise StoneKindsError(
                f"{where}: kind table is missing row(s) {missing}; it must "
                f"carry {list(_REQUIRED_ROWS)}")
        return _build(kinds, rows, where)
    raise StoneKindsError(
        f"{where}: no stone-kind table found — expected a markdown table whose "
        "header row is empty-then-backticked-kind-names and which carries a "
        "`folder` row")


def _build(kinds: list[str], rows: dict[str, list[str]], where: str) -> dict:
    out: dict[str, dict] = {}
    for idx, kind in enumerate(kinds):
        def cell(label: str) -> str:
            vals = rows[label]
            if idx >= len(vals):
                raise StoneKindsError(
                    f"{where}: row {label!r} has {len(vals)} value(s) but "
                    f"{len(kinds)} kinds are declared — the table is ragged")
            return vals[idx]

        # The `stone file` row IS the member-naming declaration — there is no
        # separate `member::` key. Two shapes are legal, and the mint needs the
        # shape declared rather than guessed, which is why it is written down
        # at all (Dan, 2026-08-28: "maybe we can't [be more general], because
        # we need to know what the shape is in order to create one").
        #
        #   numbered  `{slug} P0001`      -> prefix + zero-padded counter
        #   dated     `YYYY-MM-DD {Title}` -> creation date + human title
        #
        # A dated name's date is the date the stone was CREATED. It is NOT the
        # ordering key and must never be read as one — Dan, 2026-08-28: "the
        # only viable date is really gonna be the creation date, and that's not
        # really the date that it gets sorted by. The date that it gets sorted
        # by is gonna be the date of something happening." Ordering lives in the
        # control file, which may be machine-generated from any key at all.
        stone_file = cell("stone file")
        m = re.fullmatch(r"\{slug\}\s+([A-Za-z]+)(\d+)", stone_file)
        if m:
            member, prefix, number = "numbered", m.group(1), m.group(2)
        elif re.fullmatch(r"YYYY-MM-DD\s+\{[Tt]itle\}", stone_file):
            member, prefix, number = "dated", "", ""
        else:
            raise StoneKindsError(
                f"{where}: {kind!r} 'stone file' is {stone_file!r}; expected "
                "either '{slug} <PREFIX><number>' such as '{slug} P0001', or "
                "'YYYY-MM-DD {Title}' for a date-named kind")

        hdr = cell("header display")
        hm = re.fullmatch(r"(.*)\[\[(.*)\]\](.*)", hdr)
        if not hm:
            raise StoneKindsError(
                f"{where}: {kind!r} 'header display' is {hdr!r}; expected a "
                "wikilink with optional wrapper, such as '-[[…|{slug}]]-'")
        pre, inner, post = hm.group(1), hm.group(2), hm.group(3)
        header_alias = inner.split("|")[-1].strip() if "|" in inner else "{slug}"

        out[kind] = {
            "folder": cell("folder").rstrip("/"),
            "control": cell("control file"),
            "member": member,
            "prefix": prefix,
            "digits": len(number),
            "stone_alias": cell("stone display"),
            "header_alias": header_alias,
            "header_line": f"{pre}{{link}}{post}",
        }
    return out


def stones_section() -> dict:
    """The `stones:` section of the F080 global config, or {} — the F628
    type-set declaration. `stone` passes its own cached copy into
    `load_types` (test hermeticity); audit-plan calls `load_types()` bare."""
    if not CONFIG_PATH.is_file():
        return {}
    try:
        import yaml
        with CONFIG_PATH.open() as f:
            data = yaml.safe_load(f) or {}
    except Exception as e:
        raise StoneKindsError(f"{CONFIG_PATH} unreadable: {e}")
    raw = data.get("stones") or {}
    if not isinstance(raw, dict):
        raise StoneKindsError(f"{CONFIG_PATH}: `stones:` must map type names to defaults")
    return raw


def type_defaults(name: str) -> dict:
    """Convention-derived defaults for a type name (F628): numbered members,
    prefix = the name's first letter, folder `{slug} <Name>/` under Track,
    control file = the folder note inside it."""
    word = name.replace("_", " ").replace("-", " ").title()
    tmpl = "{slug} " + word
    return {
        "folder": tmpl,
        "control": tmpl,
        "member": "numbered",
        "prefix": name[0].upper(),
        "digits": 4,
        "stone_alias": "{slug}:",
        "header_alias": "{slug}",
        "header_line": "-{link}-",
    }


def load_types(section: dict = None) -> dict:
    """The live type set (F628 step 4): the config `stones:` section is the
    source of truth once it exists — its names ARE the types, each built on
    `type_defaults` plus its declared fields. Without a section the kind
    table below serves as the shipped default set. Borrowed by `stone` AND
    `audit-plan.py` so the two cannot drift (T120)."""
    sec = stones_section() if section is None else section
    if any(k != "_" for k in sec):
        out = {}
        for name, fields in sec.items():
            if name == "_":
                continue
            cfg = dict(type_defaults(name))
            for k, v in (fields or {}).items():
                cfg[k] = v
            if cfg.get("digits") is not None:
                cfg["digits"] = int(cfg["digits"])
            out[name] = cfg
        return out
    return load_kinds()


def load_kinds(path: Path | None = None) -> dict:
    """The public entry point both readers call."""
    p = path or resolve_doc_path()
    if not p.is_file():
        raise StoneKindsError(
            f"stone-kind table not found at {p} — set `stone_kinds_doc` in "
            f"{CONFIG_PATH} to the doc carrying the kind table")
    return parse_kind_table(p.read_text(encoding="utf-8"), str(p))


if __name__ == "__main__":
    import json as _json
    print(_json.dumps(load_kinds(), indent=2, sort_keys=True))
