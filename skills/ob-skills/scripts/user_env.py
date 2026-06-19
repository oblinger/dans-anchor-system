#!/usr/bin/env python3
"""user_env.py — accessor for the User Environment doc (per F182).

The User Environment doc is a single in-vault markdown file holding per-machine
facts skills consume (GSA path, default exp remote, Mail-rule names, …), one
`## <section>` H2 per consumer, each opening with a parseable `key: value`
block (optionally fenced ```yaml) followed by prose. Non-secret facts only.

Path resolution (first hit wins):
    1. env  OB_SKILLS_USER_ENV_DOC
    2. global.yaml  user_env_doc
    3. computed default  {vault_root}/MY/User Environment.md
       (vault_root: env OB_SKILLS_VAULT_ROOT → global.yaml vault_root → ~/ob/kmr)

Usage (called by the `ob-skills env` subcommand):
    user_env.py                       → print the resolved doc path
    user_env.py <section>             → print that section's H2 body
    user_env.py <section> <key>       → print one scalar (exit 1 if absent)
    user_env.py --set <section> <key> <value>
                                      → set/replace key in section (creates
                                        doc/section/yaml-fence as needed)
"""
from __future__ import annotations

import os
import re
import sys

GLOBAL_YAML = os.path.expanduser(
    os.environ.get("OB_SKILLS_ROOT", "~/.config/ob-skills") + "/global.yaml"
)
H2_RE = re.compile(r"^##\s+(.*?)\s*$")
FENCE_RE = re.compile(r"^\s*```")


def _expand(p: str) -> str:
    return os.path.expanduser(p.strip()) if p.startswith("~") else p.strip()


def _yaml_global(key: str) -> str | None:
    """Read a top-level scalar from global.yaml; None on any miss."""
    try:
        import yaml
        with open(GLOBAL_YAML) as f:
            data = yaml.safe_load(f) or {}
        v = data.get(key)
        return str(v) if isinstance(v, (str, int, float)) else None
    except Exception:
        return None


def resolve_doc() -> str:
    env = os.environ.get("OB_SKILLS_USER_ENV_DOC")
    if env:
        return _expand(env)
    cfg = _yaml_global("user_env_doc")
    if cfg:
        return _expand(cfg)
    vault = (
        os.environ.get("OB_SKILLS_VAULT_ROOT")
        or _yaml_global("vault_root")
        or "~/ob/kmr"
    )
    return os.path.join(_expand(vault), "MY", "User Environment.md")


def _section_bounds(lines: list[str], section: str) -> tuple[int, int] | None:
    """Return (start, end) line indices for the body of `## <section>`
    (exclusive of the header line), or None if the section is absent."""
    sec = section.strip().lower()
    for i, ln in enumerate(lines):
        m = H2_RE.match(ln)
        if m and m.group(1).strip().lower() == sec:
            end = len(lines)
            for j in range(i + 1, len(lines)):
                if H2_RE.match(lines[j]):
                    end = j
                    break
            return (i + 1, end)
    return None


def _key_in_body(body: list[str], key: str) -> str | None:
    pat = re.compile(r"^\s*" + re.escape(key) + r"\s*:\s*(.*?)\s*$")
    for ln in body:
        if FENCE_RE.match(ln):
            continue
        m = pat.match(ln)
        if m:
            v = m.group(1).strip().strip("`").strip('"').strip("'")
            return _expand(v) if v.startswith("~") else v
    return None


def cmd_get(doc: str, section: str | None, key: str | None) -> int:
    if section is None:
        print(doc)
        return 0
    try:
        lines = open(doc, encoding="utf-8").read().splitlines()
    except OSError:
        sys.stderr.write(f"ob-skills env: doc not found: {doc}\n")
        return 2
    b = _section_bounds(lines, section)
    if b is None:
        sys.stderr.write(f"ob-skills env: no '## {section}' section in {doc}\n")
        return 1
    body = lines[b[0]:b[1]]
    if key is None:
        print("\n".join(body).strip())
        return 0
    val = _key_in_body(body, key)
    if val is None:
        sys.stderr.write(
            f"ob-skills env: key '{key}' not found in section '{section}'\n"
        )
        return 1
    print(val)
    return 0


def cmd_set(doc: str, section: str, key: str, value: str) -> int:
    os.makedirs(os.path.dirname(doc), exist_ok=True)
    if os.path.exists(doc):
        lines = open(doc, encoding="utf-8").read().splitlines()
    else:
        lines = [
            "---",
            "description: Per-machine local-environment facts skills consume "
            "(per F182). Non-secret only.",
            "---",
            "",
            "# User Environment",
            "",
        ]
    b = _section_bounds(lines, section)
    if b is None:
        if lines and lines[-1].strip():
            lines.append("")
        lines += [f"## {section}", "", "```yaml", f"{key}: {value}", "```", ""]
        open(doc, "w", encoding="utf-8").write("\n".join(lines) + "\n")
        print(doc)
        return 0
    start, end = b
    pat = re.compile(r"^\s*" + re.escape(key) + r"\s*:")
    for j in range(start, end):
        if not FENCE_RE.match(lines[j]) and pat.match(lines[j]):
            lines[j] = f"{key}: {value}"
            open(doc, "w", encoding="utf-8").write("\n".join(lines) + "\n")
            print(doc)
            return 0
    # Insert: before a closing ``` fence if present, else right after header.
    insert_at = start
    fence_open = None
    for j in range(start, end):
        if FENCE_RE.match(lines[j]):
            if fence_open is None:
                fence_open = j
            else:
                insert_at = j  # closing fence
                break
    else:
        insert_at = start
    if fence_open is not None and insert_at > fence_open:
        lines.insert(insert_at, f"{key}: {value}")
    else:
        lines.insert(start, f"{key}: {value}")
    open(doc, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(doc)
    return 0


def main(argv: list[str]) -> int:
    doc = resolve_doc()
    if argv and argv[0] == "--set":
        rest = argv[1:]
        if len(rest) < 3:
            sys.stderr.write(
                "usage: ob-skills env --set <section> <key> <value>\n"
            )
            return 2
        section, key = rest[0], rest[1]
        value = " ".join(rest[2:])
        return cmd_set(doc, section, key, value)
    section = argv[0] if len(argv) >= 1 else None
    key = argv[1] if len(argv) >= 2 else None
    return cmd_get(doc, section, key)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
