#!/usr/bin/env python3
"""Prove salvage_full.py before it is pointed at the only 2019 capture of the Drive.

The fixture reproduces the three properties that made the real archive hard, and
each one is here because it broke an earlier version of this code:
  * trailing data descriptors (compressed size is 0 in the local header),
  * a whole nested zip stored raw inside it (the false-`PK\\x03\\x04` trap that
    shredded a .docx in run 2),
  * a destroyed central directory, i.e. a container `zip -FF` cannot rebuild.
"""
import io
import os
import pathlib
import shutil
import struct
import subprocess
import sys
import tempfile
import zipfile

S = str(pathlib.Path(__file__).resolve().with_name("salvage_zip.py"))
T = tempfile.mkdtemp(prefix="salv-")
fails = []


_all = []


def check(label, cond, extra=""):
    _all.append(label)
    print(("  ok    " if cond else "  FAIL  ") + label
          + ("" if cond else "   " + str(extra)[:400]))
    if not cond:
        fails.append(label)


class NoSeek:
    """A sink with no tell() — forces zipfile to emit trailing data descriptors,
    the exact shape the real archive has and the reason slice3 had to measure."""

    def __init__(self):
        self.b = io.BytesIO()

    def write(self, d):
        return self.b.write(d)

    def flush(self):
        pass


docx_buf = io.BytesIO()
with zipfile.ZipFile(docx_buf, "w", zipfile.ZIP_DEFLATED) as dz:
    dz.writestr("word/fonts/Tahoma-bold.ttf", os.urandom(200000))
    dz.writestr("[Content_Types].xml", "<xml/>" * 500)
DOCX = docx_buf.getvalue()

payload = {
    "docs/report.txt": b"hello world\n" * 40000,
    "docs/photo.bin": os.urandom(300000),
    "docs/empty.txt": b"",
    "docs/Resume café.txt": "non-ascii name\n".encode() * 1000,
    "nested/thing.docx": DOCX,
}
ns = NoSeek()
with zipfile.ZipFile(ns, "w", zipfile.ZIP_DEFLATED) as iz:
    iz.writestr("docs/", b"")
    for n, d in payload.items():
        iz.writestr(n, d, zipfile.ZIP_STORED
                    if n.endswith((".bin", ".docx")) else zipfile.ZIP_DEFLATED)
INNER = ns.b.getvalue()
assert INNER.count(b"PK\x07\x08") >= 4, "fixture must use data descriptors"
assert DOCX in INNER, "nested zip must sit raw inside the stream"


def build(inner_bytes, path, stored=True):
    with zipfile.ZipFile(path, "w") as oz:
        oz.writestr("Broken/inner.zip", inner_bytes,
                    zipfile.ZIP_STORED if stored else zipfile.ZIP_DEFLATED)


def run(outer, out, extra=()):
    p = subprocess.run([sys.executable, S, "--outer", outer, "--member",
                        "Broken/inner.zip", "--out", out, *extra],
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


broken = bytearray(INNER)
# Destroy the OUTER archive's central directory -- located exactly, via its own
# EOCD. Searching for the first (or last) PK\x01\x02 finds the nested .docx's
# internal central directory instead, which mangles the fixture rather than the
# container and makes the tool look wrong when it is not.
_eocd = broken.rfind(b"PK\x05\x06")
assert _eocd > 0, "fixture has no EOCD"
_cd = struct.unpack("<I", bytes(broken[_eocd + 16:_eocd + 20]))[0]
assert broken[_cd:_cd + 4] == b"PK\x01\x02", "EOCD does not point at the CD"
broken[_cd:] = b"\x00" * (len(broken) - _cd)

o0 = os.path.join(T, "asis.zip")
with open(o0, "wb") as fh:
    fh.write(bytes(broken))
# "Unopenable" is not always an exception. With the outer central directory
# gone, zipfile scans backward, finds the NESTED .docx's own EOCD, and happily
# presents the .docx's members as if they were the archive's. That is worse than
# an error -- it is a wrong answer delivered confidently -- and it is exactly the
# state the real archive is in. So the assertion is that the container does not
# yield the real payload, not that it raises.
try:
    got0 = set(n for n in zipfile.ZipFile(o0).namelist() if not n.endswith("/"))
except Exception:
    got0 = None
check("fixture container cannot yield the real payload (zip -FF territory)",
      got0 != set(payload), got0)

o1 = os.path.join(T, "outer1.zip")
r1 = os.path.join(T, "out1.zip")
build(bytes(broken), o1)
rc, out = run(o1, r1)
check("destroyed CD: exit 0 — nothing left unexplained", rc == 0, out[-900:])
check("destroyed CD: zero resyncs — the chain held", "resyncs: 0" in out, out[-700:])
check("destroyed CD: no CRC_MISMATCH", "CRC_MISMATCH" not in out, out[-700:])
check("destroyed CD: no INFLATE_FAIL", "INFLATE_FAIL" not in out, out[-700:])
try:
    with zipfile.ZipFile(r1) as rz:
        bad = rz.testzip()
        got = {i.filename: rz.read(i.filename) for i in rz.infolist()
               if not i.filename.endswith("/")}
    check("recovered archive opens; every member inflates (testzip)",
          bad is None, bad)
    mismatch = {k: (len(v), len(got.get(k, b""))) for k, v in payload.items()
                if got.get(k) != v}
    check("recovered archive holds ALL originals byte-for-byte",
          not mismatch, mismatch)
    check("non-ASCII filename survived", "docs/Resume café.txt" in got,
          sorted(got))
    check("nested .docx recovered whole, not shredded into false entries",
          got.get("nested/thing.docx") == DOCX)
    check("empty file preserved as empty rather than dropped",
          got.get("docs/empty.txt") == b"")
    check("no phantom members invented", len(got) == len(payload), sorted(got))
    # The two instruments added for the real run must be shown to FIRE. A
    # counter that cannot reach a non-zero value proves nothing when it reads
    # zero on the 64.9 GB, and "no innards seen" means nothing if the detector
    # is inert.
    check("nested-archive counter engages (not a probe that can never pass)",
          "nested archives measured by descriptor: 1" in out, out[-900:])
    check("innards detector reports clean on a correct walk",
          "none — no sign the walk stepped inside a nested container" in out,
          out[-900:])
except Exception as e:
    check("recovered archive opens", False, repr(e))

# --- the innards detector must be able to FIRE ------------------------------
ns2 = NoSeek()
with zipfile.ZipFile(ns2, "w", zipfile.ZIP_DEFLATED) as iz2:
    iz2.writestr("word/fonts/Tahoma-bold.ttf", b"z" * 500)
    iz2.writestr("[Content_Types].xml", b"<xml/>")
inner2 = bytearray(ns2.b.getvalue())
_e2 = inner2.rfind(b"PK\x05\x06")
_c2 = struct.unpack("<I", bytes(inner2[_e2 + 16:_e2 + 20]))[0]
inner2[_c2:] = b"\x00" * (len(inner2) - _c2)
oI = os.path.join(T, "innards.zip")
build(bytes(inner2), oI)
rc, out = run(oI, os.path.join(T, "outI.zip"))
check("innards detector FIRES on container-interior names at top level",
      "container-interior names seen at top level: 2" in out, out[-900:])
check("innards detector: exits non-zero even with nothing else wrong",
      rc != 0, f"rc={rc}")
check("innards detector: says the exit code cannot see this failure",
      "independent of the exit code" in out, out[-900:])

c2 = bytearray(broken)
hit = c2.find(b"docs/report.txt")
c2[hit + 200:hit + 240] = b"\xff" * 40
o2 = os.path.join(T, "outer2.zip")
r2 = os.path.join(T, "out2.zip")
build(bytes(c2), o2)
rc, out = run(o2, r2)
check("corrupted entry: exit non-zero — does not claim success", rc != 0, out[-500:])
check("corrupted entry: lands in a NAMED failure class",
      ("CRC_MISMATCH" in out or "INFLATE_FAIL" in out), out[-900:])
try:
    with zipfile.ZipFile(r2) as rz:
        names = rz.namelist()
    check("corrupted entry: NOT written into the clean archive",
          "docs/report.txt" not in names, names)
    check("corrupted entry: the other files were still salvaged",
          "docs/photo.bin" in names, names)
except Exception as e:
    check("output still opens after a bad entry", False, repr(e))

o3 = os.path.join(T, "outer3.zip")
build(bytes(broken), o3, stored=False)
rc, out = run(o3, os.path.join(T, "out3.zip"))
check("compressed nested member: REFUSES rather than computing garbage offsets",
      "REFUSED" in out and rc != 0, out[-300:])

r4 = os.path.join(T, "out4.zip")
rc, out = run(o1, r4, ("--dry-run",))
check("--dry-run verifies and writes nothing", not os.path.exists(r4), out[-200:])

shutil.rmtree(T, ignore_errors=True)
print(f"\n  {len(_all) - len(fails)}/{len(_all)} passed" if not fails else f"\n  FAILED: {fails}")
sys.exit(1 if fails else 0)
