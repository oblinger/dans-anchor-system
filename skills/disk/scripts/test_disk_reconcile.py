#!/usr/bin/env python3
"""Regression suite for disk_reconcile's row classification, written against the
REAL M3 encoding rather than an invented one.

The first version of the tool classified relocation by matching the words
'moved' / 'reloc' in the M3 disposition column. It tested green against a fixture
that used exactly those words -- and the real workbook uses them in none of its
49 distinct values, so the branch could never have fired in production. The
fixtures below therefore use the encoding the Legend sheet documents:
'M3 YYYY-MM-DD (R<n>/K<n>/M<n>)', per-FILE counts, plus the curated trailing
[MOVED ...] / [NEVER LANDED] path markers.
"""
import json
import os
import pathlib
import unicodedata
import shutil
import subprocess
import sys
import tempfile
import zipfile

import openpyxl

TOOL = str(pathlib.Path(__file__).resolve().with_name("disk_reconcile.py"))
HDR = ["10T Path", "Frozen", "Bytes", "Files", "8T", "BLACK", "Source", "Notes",
       "Content (SHA-256)", "10T ✓", "M3 disposition"]


def write_catalog(path, rows):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Master Contents"
    ws.append(HDR)
    for r in rows:
        ws.append([r.get(h) for h in HDR])
    wb.save(path)


def run(root, catalog, as_json=False):
    argv = [sys.executable, TOOL, "FIXTURE", "--root", root, "--catalog", catalog]
    if as_json:
        argv.append("--json")
    p = subprocess.run(argv, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def main():
    tmp = tempfile.mkdtemp(prefix="dr-")
    root = os.path.join(tmp, "root")
    os.makedirs(os.path.join(root, "__MASTERS__/_ARCHIVES_/present-row"))
    # The M3 destination is created LATER, not here: it has no catalog row, so a
    # green fixture that already contains it is not green -- direction 2 flags it,
    # correctly. (First run of this suite failed on exactly that, and the tool was
    # right.)
    dest = os.path.join(root, "_ARCHIVES_/Master Reconciliation 2026-06-25")
    cat = os.path.join(tmp, "cat.xlsx")

    base = [
        {"10T Path": "__MASTERS__/_ARCHIVES_/present-row", "Bytes": 100,
         "Files": 2, "8T": "C 2026-07-01", "BLACK": "C 2026-07-01",
         "M3 disposition": "M3 clean (2026-06-25)"},
    ]
    moved = {"10T Path": "__MASTERS__/_ARCHIVES_/gone.zip  [MOVED 2026-06-25]",
             "Bytes": 500, "Files": 1, "8T": "C 2026-07-01",
             "BLACK": "C 2026-07-01",
             "Notes": "MOVED-TO-BROKEN by M3 (disposition M1) — bytes preserved",
             "M3 disposition": "M3 2026-06-25 (M1)"}
    never = {"10T Path": "__MASTERS__/_ARCHIVES_/ghost.zip  [NEVER LANDED]",
             "Bytes": 900, "Files": 1, "8T": "C 2026-07-01",
             "BLACK": "C 2026-07-01",
             "Notes": "Never landed on 10T — BEAST-only, proven broken",
             "M3 disposition": "M3 2026-06-25 (M1)"}
    partial = {"10T Path": "__MASTERS__/_ARCHIVES_/partial",
               "Bytes": 700, "Files": 9, "8T": "C 2026-07-01",
               "BLACK": "C 2026-07-01",
               "M3 disposition": "M3 2026-06-25 (R3/K5/M1)"}

    fails = []
    total = [0]

    def check(label, cond, extra=""):
        total[0] += 1
        print(("  ok    " if cond else "  FAIL  ") + label + ("" if cond else f"   {extra}"))
        if not cond:
            fails.append(label)

    # --- green ---------------------------------------------------------
    write_catalog(cat, base)
    rc, out = run(root, cat)
    check("green: everything present -> exit 0", rc == 0, f"rc={rc}")
    check("green: no missing / never / relocated",
          "missing — 0" in out and "NEVER LANDED — 0" in out
          and "RELOCATED (documented, not missing) — 0" in out)

    # --- relocated, real encoding + confirmed destination ---------------
    # The destination DIRECTORY existing is not enough any more (Part 2): the
    # moved file's bytes must actually be listed inside a 'Broken *.zip'
    # archive under it. So the fixture puts a real zip there, containing an
    # entry matching the row's basename, before asserting a clean RELOCATED.
    os.makedirs(dest)
    zip_path = os.path.join(dest, "Broken Archives.zip")
    CATPATH = "__MASTERS__/_ARCHIVES_/gone.zip"

    def write_zip(path, members):
        """members: {name_inside_zip: byte_length}"""
        with zipfile.ZipFile(path, "w") as zf:
            for name, n in members.items():
                zf.writestr(name, b"x" * n)

    write_zip(zip_path, {f"Broken Archives/{CATPATH}": 500})
    base.append({"10T Path": "_ARCHIVES_", "Bytes": 0, "Files": 0,
                 "M3 disposition": "M3 clean (2026-06-25)"})
    write_catalog(cat, base + [moved])
    rc, out = run(root, cat)
    check("relocated: (M1) on a 1-file row, zip contains the entry -> RELOCATED",
          "RELOCATED (documented, not missing) — 1" in out, out[-400:])
    check("relocated: NOT counted as missing", "missing — 0" in out)
    check("relocated: not counted as contents-unverified either",
          "RELOCATED — CONTENTS UNVERIFIED — 0" in out)
    check("relocated: contents were actually opened and confirmed, not assumed",
          "contents confirmed" in out
          and "full catalogued path is listed inside" in out, out[-500:])
    check("relocated: the declared size was compared, and says so with the number",
          "declaring exactly the catalogued 500 bytes" in out, out[-500:])
    check("relocated: admits no CRC was checked — not a byte verification",
          "no CRC was checked" in out, out[-500:])

    # --- Part 2: zip exists but does NOT list the entry -> contents unverified
    good_zip_stash = os.path.join(tmp, "good.zip")
    shutil.move(zip_path, good_zip_stash)
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("something-else.txt", b"not the file we are looking for")
    rc, out = run(root, cat)
    check("zip present but missing the entry -> CONTENTS UNVERIFIED, not RELOCATED",
          "RELOCATED — CONTENTS UNVERIFIED — 1" in out
          and "RELOCATED (documented, not missing) — 0" in out
          and "missing — 0" in out, out[-500:])
    check("zip missing the entry: says destination present, contents unverified",
          "destination directory present, contents unverified" in out)
    check("zip missing the entry: exits non-zero (a finding, not a sentence)",
          rc == 1, f"rc={rc}")
    os.remove(zip_path)

    # --- Part 2: archive is corrupt -> its own state, never reads as verified
    with open(zip_path, "wb") as f:
        f.write(b"this is not a zip file at all")
    rc, out = run(root, cat)
    check("corrupt zip -> CONTENTS UNVERIFIED, exception does not read as verified",
          "RELOCATED — CONTENTS UNVERIFIED — 1" in out
          and "RELOCATED (documented, not missing) — 0" in out, out[-500:])
    check("corrupt zip: names the failure (could not be opened)",
          "could not be opened" in out)
    check("corrupt zip: exits non-zero", rc == 1, f"rc={rc}")
    os.remove(zip_path)

    # --- Part 2: destination directory present, no archive at all inside it
    rc, out = run(root, cat)
    check("no archive under destination at all -> CONTENTS UNVERIFIED",
          "RELOCATED — CONTENTS UNVERIFIED — 1" in out
          and "no 'Broken *.zip' archive" in out, out[-500:])
    check("no archive at all: exits non-zero", rc == 1, f"rc={rc}")

    # restore the good archive so later checks that expect a clean RELOCATED pass
    shutil.move(good_zip_stash, zip_path)

    # --- a SECOND reconciliation pass holds the archive -----------------
    # The destination glob carries a date wildcard because a drive can
    # accumulate more than one Master Reconciliation pass. A row archived by
    # the later pass is confirmed just as well as one archived by the first,
    # so every destination must be searched -- checking only the first would
    # turn a second reconciliation date into a wave of false findings, each
    # one exiting non-zero.
    dest2 = os.path.join(root, "_ARCHIVES_/Master Reconciliation 2026-07-30")
    os.makedirs(dest2)
    shutil.move(zip_path, os.path.join(dest2, "Broken Archives.zip"))
    rc, out = run(root, cat)
    check("archive under the SECOND reconciliation dir still confirms RELOCATED",
          "RELOCATED (documented, not missing) — 1" in out
          and "RELOCATED — CONTENTS UNVERIFIED — 0" in out, out[-500:])
    check("second-dir confirmation names the dir it actually found it in",
          "Master Reconciliation 2026-07-30/" in out)
    check("second-dir confirmation exits clean, not as a finding", rc == 0,
          f"rc={rc}")
    shutil.move(os.path.join(dest2, "Broken Archives.zip"), zip_path)
    os.rmdir(dest2)

    # --- the path is there but declares the WRONG size -> a finding ---------
    # Strictly stronger than a name match: "something called gone.zip is in
    # there" and "the row's bytes are in there" are different claims.
    write_zip(zip_path, {f"Broken Archives/{CATPATH}": 499})
    rc, out = run(root, cat)
    check("size mismatch: refuses to call it relocated",
          "RELOCATED (documented, not missing) — 0" in out, out[-500:])
    check("size mismatch: reports the discrepancy with BOTH numbers",
          "declares 499 bytes where the catalog records 500" in out, out[-600:])
    check("size mismatch: exits non-zero", rc == 1, f"rc={rc}")

    # --- right filename at the WRONG path -> located, but explicitly WEAK ---
    # A bare-name match is how an unrelated hit reads as proof: during the F052
    # hunt a search for 'Google Drive' matched unrelated Aeolus paths.
    write_zip(zip_path, {"Broken Archives/somewhere/else/gone.zip": 500})
    rc, out = run(root, cat)
    check("wrong path, right name: flagged WEAK MATCH, not proof",
          "WEAK MATCH" in out, out[-600:])
    check("wrong path, right name: names where it actually found it",
          "somewhere/else/gone.zip" in out, out[-600:])

    # --- macOS stores names decomposed; the catalog is typed composed -------
    nfd_row = dict(moved)
    nfd_row["10T Path"] = "__MASTERS__/_ARCHIVES_/Resum\u00e9.zip  [MOVED 2026-06-25]"
    write_zip(zip_path, {"Broken Archives/__MASTERS__/_ARCHIVES_/"
                         + unicodedata.normalize("NFD", "Resum\u00e9.zip"): 500})
    write_catalog(cat, base + [nfd_row])
    rc, out = run(root, cat)
    check("NFD vs NFC: the same filename is recognised as the same file",
          "RELOCATED (documented, not missing) — 1" in out, out[-600:])

    write_zip(zip_path, {f"Broken Archives/{CATPATH}": 500})
    write_catalog(cat, base + [moved])

    # --- the same row with NO destination on the drive -> stays missing --
    shutil.move(os.path.join(root, "_ARCHIVES_/Master Reconciliation 2026-06-25"), os.path.join(tmp, "stash"))
    rc, out = run(root, cat)
    check("no destination: refuses to call it relocated",
          "RELOCATED (documented, not missing) — 0" in out and "missing — 1" in out,
          out[-400:])
    check("no destination: says why, rather than silently downgrading",
          "relocation NOT confirmed" in out and "to receive them" in out)
    shutil.move(os.path.join(tmp, "stash"), os.path.join(root, "_ARCHIVES_/Master Reconciliation 2026-06-25"))

    # --- never-landed beats the M-count -------------------------------
    write_catalog(cat, base + [never])
    rc, out = run(root, cat)
    check("never-landed: own section, NOT relocated",
          "NEVER LANDED — 1" in out
          and "RELOCATED (documented, not missing) — 0" in out, out[-500:])
    check("never-landed: names the stamp defect",
          "verification of content this drive never held" in out)
    check("never-landed: exits non-zero (a finding, not bookkeeping)", rc == 1,
          f"rc={rc}")

    # --- partial move does not explain a whole absent row --------------
    write_catalog(cat, base + [partial])
    rc, out = run(root, cat)
    check("partial move (M1 of 9 files): stays missing",
          "missing — 1" in out and "RELOCATED (documented, not missing) — 0" in out)
    check("partial move: explains the refusal",
          "partial move does not explain" in out)

    # --- the retired fiction must NOT resurrect ------------------------
    fiction = dict(moved)
    fiction["M3 disposition"] = "moved to the reconciliation archive"
    fiction["Notes"] = None
    write_catalog(cat, base + [fiction])
    rc, out = run(root, cat)
    check("prose 'moved to ...' alone no longer classifies (the retired bug)",
          "RELOCATED (documented, not missing) — 0" in out and "missing — 1" in out,
          out[-300:])

    # --- json parity ----------------------------------------------------
    write_catalog(cat, base + [moved, never, partial])
    rc, out = run(root, cat)
    rcj, outj = run(root, cat, as_json=True)
    doc = json.loads(outj)
    check("json: same exit code as text", rc == rcj, f"{rc} vs {rcj}")
    check("json: carries all buckets with matching counts",
          len(doc["relocated"]) == 1 and len(doc["never_landed"]) == 1
          and len(doc["missing"]) == 1 and len(doc["relocated_unverified"]) == 0,
          f"rel={len(doc['relocated'])} never={len(doc['never_landed'])} "
          f"miss={len(doc['missing'])} unverified={len(doc['relocated_unverified'])}")


    # --- sidecar READMEs (2026-08-09) -----------------------------------
    # Found by the first clean 10T run, which reported the two `.README.txt`
    # files written the night before as unexplained. A blanket `*.README.txt`
    # suppression would have muted the genuinely-orphaned case too, so the rule
    # keys on the catalogued row beside it -- and these run it through the tool
    # rather than calling the helper, so a rule that never fires cannot pass.
    arch = os.path.join(root, "__MASTERS__/_ARCHIVES_")
    pathlib.Path(arch, "sidecarred.zip").write_bytes(b"x")
    pathlib.Path(arch, "sidecarred.README.txt").write_text("explains the row")
    pathlib.Path(arch, "orphan.README.txt").write_text("explains nothing")
    write_catalog(cat, base + [{"10T Path": "__MASTERS__/_ARCHIVES_/sidecarred.zip",
                                "Bytes": 1, "Files": 1}])
    rc, out = run(root, cat)
    check("sidecar beside a catalogued row is suppressed, not reported",
          "_ARCHIVES_/sidecarred.README.txt" not in out.split("## Suppressed")[0],
          out[-400:])
    check("suppression names the row that explains it",
          "explained by `sidecarred.zip`" in out, out[-400:])
    check("a README with NO catalogued sibling is still reported",
          "orphan.README.txt" in out.split("## Suppressed")[0], out[-400:])
    check("the catalogued file itself is not reported",
          "_ARCHIVES_/sidecarred.zip" not in out.split("## Suppressed")[0], out[-400:])
    for f in ("sidecarred.zip", "sidecarred.README.txt", "orphan.README.txt"):
        os.remove(os.path.join(arch, f))

    shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n  {total[0] - len(fails)}/{total[0]} passed" if not fails
          else f"\n  FAILED ({len(fails)}/{total[0]}): {fails}")
    return 1 if fails else 0


sys.exit(main())
