#!/usr/bin/env python3
"""test-f301-slug-is-a-handle.py — R-dot-anchor-03, the slug grammar.

TINK F301. A declared `slug:` is a **short handle** for its anchor, and is
declared only when it earns that: either files are prefixed with it, or it is
the short form typed to refer to and navigate to the anchor. Spelling follows
from the job — it sits in front of a name (`TINK Backlog.md`), so it must be
visually separable at a glance: one token, uppercase alphanumeric.

Before this rule existed, 116 of 186 declarations in the vault were
**restatements** — a value byte-identical to the basename, or a re-casing of
it, saying nothing the basename did not already say. `2026-03-18 AI Model
Pricing` was declared as a slug; it is a perfectly good *basename* and was
never a slug. That drift is what made `{slug}` interpolation in `where::`
selectors resolve to tokens no file matched (T111).

Two assertions carry most of the value here, because both are cases where the
obvious rule is wrong:

  * a LEADING DIGIT is legal. ANC Standard retires a slug in place by prefixing
    its two-digit creation year (`SKD` -> `25SKD`), so `^[A-Z][A-Z0-9]*$` would
    condemn every retired slug. The grammar is `^[A-Z0-9]+$`.
  * an anchor declaring NO slug passes. 86% of the corpus declares none, and
    the implied slug (the basename) serves every consumer that needs a handle.

    python3 test-f301-slug-is-a-handle.py
"""
import importlib.util
import pathlib
import sys
import tempfile

HERE = pathlib.Path(__file__).parent
AUDIT = HERE.parent / "skills" / "audit" / "scripts"

results = []


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"  (got {got!r}, want {want!r})"))


spec = importlib.util.spec_from_file_location("audit_plan", AUDIT / "audit-plan.py")
assert spec and spec.loader
ap = importlib.util.module_from_spec(spec)
sys.modules["audit_plan"] = ap
spec.loader.exec_module(ap)

root = pathlib.Path(tempfile.mkdtemp())


def verdict(folder, dot_body):
    d = root / folder
    d.mkdir(parents=True, exist_ok=True)
    (d / ".anchor").write_text(dot_body, encoding="utf-8")
    return ap.chk_slug_is_a_handle(d, d, [])[0]


print("A declared slug is one uppercase alphanumeric token")
check("'ATT' passes", verdict("Atticus", "slug: ATT\n"), "pass")
check("'WEB' passes (moniker, nothing prefixed)", verdict("Website", "slug: WEB\n"), "pass")
check("'A2X' passes", verdict("alg2-experimental", "slug: A2X\n"), "pass")

print("\nA leading digit is LEGAL — retirement prefixes the creation year")
check("'25SKD' passes (retired slug)", verdict("2025 SKD Files", "slug: 25SKD\n"), "pass")
check("'26NORT' passes", verdict("Northwind Head of Product Eng", "slug: 26NORT\n"), "pass")

print("\nNon-conforming spellings fail")
check("multi-token 'A2X Agents' fails", verdict("A2X Agents2", "slug: A2X Agents\n"), "fail")
check("title-case 'Warden' fails", verdict("warden2", "slug: Warden\n"), "fail")
check("dated 'ffff' with spaces fails",
      verdict("Pricing", "slug: 2026-03-18 AI Model Pricing\n"), "fail")
check("lowercase 'web' fails", verdict("Website2", "slug: web\n"), "fail")

print("\nA restatement is never a slug")
# The folder is uppercase so the value is byte-identical AND grammar-valid —
# otherwise the grammar rule fires first and this never exercises the
# restatement branch at all.
check("slug byte-identical to the basename fails",
      verdict("ATTIC", "slug: ATTIC\n"), "fail")
check("another byte-identical restatement fails",
      verdict("PUZZLES", "slug: PUZZLES\n"), "fail")
# The message must tell the author what to do, not just what is wrong.
d = root / "ATTIC"
_, msg = ap.chk_slug_is_a_handle(d, d, [])
check("the refusal says to delete it", "delete it" in msg, True)

print("\nDeclaring NO slug is the common, correct case")
check("an .anchor with no slug passes", verdict("Some Topic", "description: x\n"), "pass")
check("an empty .anchor passes", verdict("Empty Topic", ""), "pass")
check("a folder with no .anchor passes", ap.chk_slug_is_a_handle(root, root, [])[0], "pass")

# A CASE-differing slug is NOT a restatement — it supplies an uppercase prefix
# form the lowercase basename cannot. `MUSE`/`muse` is the general case and
# `TINK`/`Tink` is the same shape, so the roster needs no exemption. Deleting
# `MUSE` would drop the implied slug to `muse` and break every `MUSE F<n>.md`.
print("\nA case-differing slug supplies a prefix form the basename cannot")
check("'MUSE' in folder 'muse' passes", verdict("muse", "slug: MUSE\n"), "pass")
check("'WARDEN' in folder 'warden' passes", verdict("warden3", "slug: WARDEN\n"), "pass")
check("'TINK' in folder 'Tink' passes", verdict("Tink", "slug: TINK\n"), "pass")
check("'ASH' in folder 'Ash' passes", verdict("Ash", "slug: ASH\n"), "pass")
check("'HERMES' in folder 'Hermes' passes", verdict("Hermes", "slug: HERMES\n"), "pass")

print("\nThe live vault conforms")
vault = pathlib.Path.home() / "ob/kmr"
if vault.is_dir():
    bad = []
    for dot in vault.rglob(".anchor"):
        v, m = ap.chk_slug_is_a_handle(dot.parent, dot.parent, [])
        if v == "fail":
            bad.append(f"{dot.parent.relative_to(vault)}: {m}")
    check("zero declared slugs fail the rule vault-wide", bad, [])

print(f"\nR-dot-anchor-03 slug grammar: {sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
