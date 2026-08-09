#!/usr/bin/env python3
"""F052 — salvage `2019-05-01 Google Drive.zip` into a valid, openable archive.

`slice3.py` proved the recovery METHOD (chained walk, 4,000/4,000 entries clean,
zero resyncs).  It cannot do this job: it reads a 600 MB window into RAM and only
CLASSIFIES.  This streams the whole 64.9 GB member and WRITES the result.

Three decisions carried over from slice3, because each one was a bug there first:

  * CHAIN, never scan.  The next local header begins at the byte immediately
    after this entry's data and descriptor.  Signature-search survives only as
    `resync()` after the chain breaks, and every resync is counted with the
    byte-span it skipped -- a silent resync is an invisible miss.
  * MEASURE, never infer.  Nearly every entry is streaming-written, so the
    header's compressed-size field is 0 and the true length sits in a trailing
    data descriptor.  An incremental decompressobj reports exactly how many
    compressed bytes it consumed, so the end is measured and the descriptor is
    then validated against it.
  * A residual bucket is not a result.  Every entry lands in a named class and
    the run prints all of them.

Verification is per entry and it is real: each entry is inflated and its CRC-32
checked against the archive's own recorded CRC BEFORE it is written out.  An
entry that fails is never written -- it is named in the report instead.

The nested member is STORED inside the outer archive, so its bytes are contiguous
and seekable.  That is asserted, not assumed: if it were deflated, none of this
addressing would be valid and the run refuses.
"""
import argparse
import collections
import os
import re
import struct
import sys
import time
import zipfile
import zlib

SIG = b"PK\x03\x04"
DD = b"PK\x07\x08"
CD = b"PK\x01\x02"
CHUNK = 1 << 22          # 4 MB feed to the decompressor
BUF = 64 << 20           # 64 MB sliding window over the nested member
MAX_RESYNC_SCAN = 256 << 20

# Top-level names that are the INTERIOR of a zip-family container (.docx,
# .xlsx, .pptx, .jar, .apk). If these turn up as members, the walk almost
# certainly stepped inside a nested archive and emitted its guts.
INNARDS_RE = re.compile(
    r"^(\[Content_Types\]\.xml|_rels/|word/|xl/|ppt/|docProps/|META-INF/|customXml/)", re.IGNORECASE)


class Slice:
    """A seekable byte-window over [base, base+size) of an open file.

    Everything downstream addresses the nested archive from 0, so the outer
    archive's offset never leaks into the walk logic.
    """

    def __init__(self, fh, base, size):
        self.fh, self.base, self.size = fh, base, size
        self.buf = b""
        self.start = 0                      # logical offset of buf[0]

    def _load(self, pos, need):
        if pos >= self.start and pos + need <= self.start + len(self.buf):
            return
        start = pos
        want = max(need, BUF)
        want = min(want, self.size - start)
        if want < 0:
            want = 0
        self.fh.seek(self.base + start)
        self.buf = self.fh.read(want)
        self.start = start

    def at(self, pos, n):
        """Up to n bytes at logical `pos`. Short read only at end-of-member."""
        if pos >= self.size:
            return b""
        n = min(n, self.size - pos)
        if n > BUF:
            self.fh.seek(self.base + pos)
            return self.fh.read(n)
        self._load(pos, n)
        off = pos - self.start
        out = self.buf[off:off + n]
        if len(out) < n:                    # window ended short; go direct
            self.fh.seek(self.base + pos)
            out = self.fh.read(n)
        return out

    def find(self, needle, pos, limit=MAX_RESYNC_SCAN):
        """Forward search for `needle`; logical offset or -1."""
        step = 8 << 20
        scanned = 0
        p = pos
        tail = b""
        while p < self.size and scanned < limit:
            block = self.at(p, step)
            if not block:
                break
            hay = tail + block
            k = hay.find(needle)
            if k >= 0:
                return p - len(tail) + k
            tail = hay[-(len(needle) - 1):] if len(needle) > 1 else b""
            p += len(block)
            scanned += len(block)
        return -1


def descriptor_at(sl, p):
    """(crc, csize, usize, width) if a data descriptor sits at p, else None."""
    b = sl.at(p, 16)
    if len(b) >= 16 and b[:4] == DD:
        c, cs, us = struct.unpack("<III", b[4:16])
        return c, cs, us, 16
    if len(b) >= 12:
        c, cs, us = struct.unpack("<III", b[:12])
        return c, cs, us, 12
    return None


def inflate_measure(sl, start, sink=None):
    """Inflate the raw-deflate stream at `start`.

    Returns (consumed, crc, usize) or (None, reason, None). `sink` receives each
    decompressed block so a caller can write without buffering the whole entry.
    """
    d = zlib.decompressobj(-15)
    crc = 0
    usize = 0
    p = start
    while p < sl.size:
        block = sl.at(p, CHUNK)
        if not block:
            return None, "truncated: member ended mid-stream", None
        try:
            out = d.decompress(block)
        except zlib.error as e:
            return None, f"inflate: {e}", None
        if out:
            crc = zlib.crc32(out, crc)
            usize += len(out)
            if sink:
                sink(out)
        p += len(block)
        if d.eof:
            return (p - start) - len(d.unused_data), crc & 0xffffffff, usize
    return None, "truncated: stream never ended before end of member", None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outer", required=True)
    ap.add_argument("--member", required=True)
    ap.add_argument("--out", required=True, help="archive to write")
    ap.add_argument("--limit", type=int, default=0,
                    help="stop after N entries (slice test); 0 = whole member")
    ap.add_argument("--dry-run", action="store_true",
                    help="walk and verify, write nothing")
    args = ap.parse_args()

    z = zipfile.ZipFile(args.outer)
    hits = [e for e in z.infolist() if e.filename == args.member]
    if not hits:
        sys.exit(f"member not found in outer archive: {args.member}")
    info = hits[0]
    if info.compress_type != zipfile.ZIP_STORED:
        sys.exit("REFUSED: the nested member is compressed (compress_type="
                 f"{info.compress_type}), so its bytes are not contiguous and "
                 "none of this offset arithmetic would be valid.")

    with open(args.outer, "rb") as fh:
        fh.seek(info.header_offset)
        lh = fh.read(30)
        if lh[:4] != SIG:
            sys.exit("REFUSED: no local header at the member's recorded offset")
        nl, el = struct.unpack("<HH", lh[26:30])
        base = info.header_offset + 30 + nl + el
        sl = Slice(fh, base, info.file_size)

        print(f"outer   : {args.outer}")
        print(f"member  : {args.member}")
        print(f"data at : {base:,}   length {info.file_size:,} bytes")
        print(f"output  : {args.out}{'  (DRY RUN — nothing written)' if args.dry_run else ''}")
        print(flush=True)

        cls = collections.Counter()
        detail = collections.defaultdict(list)
        resyncs = []
        suspect_innards = []
        names = set()
        dup = 0
        recovered_bytes = 0
        written = 0
        pos = 0
        seen = 0
        t0 = time.time()

        out = None
        if not args.dry_run:
            os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
            out = zipfile.ZipFile(args.out, "w", zipfile.ZIP_DEFLATED,
                                  allowZip64=True)

        def report(final=False):
            el = time.time() - t0
            rate = pos / 1e6 / max(el, 1)
            pct = 100.0 * pos / max(info.file_size, 1)
            print(f"  [{time.strftime('%H:%M:%S')}] {seen:,} entries  "
                  f"{pos/1e9:.1f}/{info.file_size/1e9:.1f} GB ({pct:.1f}%)  "
                  f"{rate:.0f} MB/s  recovered {cls['RECOVERED']:,}  "
                  f"resyncs {len(resyncs)}  elapsed {el/60:.0f}m",
                  flush=True)

        try:
            while pos + 30 <= info.file_size:
                if args.limit and seen >= args.limit:
                    break
                head = sl.at(pos, 30)
                if len(head) < 30:
                    break
                if head[:4] != SIG:
                    if head[:4] == CD:
                        cls["REACHED_CENTRAL_DIRECTORY"] += 1
                        break
                    nxt = sl.find(SIG, pos)
                    if nxt < 0:
                        break
                    resyncs.append((pos, nxt - pos))
                    pos = nxt
                    continue

                (ver, flag, meth, mt, md, crc, csz, usz, n2,
                 e2) = struct.unpack("<HHHHHIIIHH", head[4:30])
                if not (0 < n2 < 4096) or pos + 30 + n2 + e2 > info.file_size:
                    resyncs.append((pos, 4))
                    pos += 4
                    continue
                nameb = sl.at(pos + 30, n2)
                try:
                    name = nameb.decode("utf-8")
                except UnicodeDecodeError:
                    # macOS zip leaves the UTF-8 flag clear but writes raw UTF-8;
                    # a name that is not valid UTF-8 is a false header, not a
                    # charset problem (proven on T151).
                    resyncs.append((pos, 4))
                    pos += 4
                    continue

                seen += 1
                if seen % 2000 == 0:
                    report()
                dstart = pos + 30 + n2 + e2
                streaming = bool(flag & 0x08)

                # A directory entry is MEASURED like any other -- it is only
                # WRITTEN differently. Short-circuiting it as "no data, so the
                # next header follows immediately" is wrong: a directory written
                # by a deflating writer carries a 2-byte empty deflate stream and
                # its own 16-byte descriptor, and skipping them desynchronises
                # the chain on every directory in the archive.
                is_dir = name.endswith("/")

                # ---------- measure + verify (always inflate first) ----------
                blocks = []
                if meth == 8:
                    consumed, got_crc, usize = inflate_measure(
                        sl, dstart, blocks.append)
                    if consumed is None:
                        cls["INFLATE_FAIL"] += 1
                        detail["INFLATE_FAIL"].append(f"{name} :: {got_crc}")
                        nxt = sl.find(SIG, dstart)
                        if nxt < 0:
                            break
                        resyncs.append((dstart, nxt - dstart))
                        pos = nxt
                        continue
                elif meth == 0:
                    if not streaming:
                        consumed = csz
                    else:
                        # A stored streaming entry carries its length ONLY in a
                        # trailing descriptor, so the length must be searched
                        # for. Order matters and is the whole bug from run 3:
                        # "the bytes at dstart look like a local header, so this
                        # entry is empty" is FALSE for any stored nested zip —
                        # a .docx/.xlsx/.jar payload BEGINS with PK\x03\x04. That
                        # shortcut made the walk step into the nested archive and
                        # emit its inner members as top-level files. So: look for
                        # a real descriptor first, and only fall back to
                        # empty-because-a-header-follows when none exists.
                        g = descriptor_at(sl, dstart)
                        if g and g[1] == 0 and g[2] == 0:
                            consumed = 0
                        else:
                            probe, found = dstart, None
                            while True:
                                p = sl.find(DD, probe)
                                if p < 0:
                                    break
                                gg = descriptor_at(sl, p)
                                if gg and gg[1] == p - dstart:
                                    found = p
                                    break
                                probe = p + 4
                            if found is not None:
                                consumed = found - dstart
                                if consumed and sl.at(dstart, 4) == SIG:
                                    # THE case the run-3 defect lived in: a
                                    # stored entry whose payload opens with a
                                    # local-header signature, i.e. a nested
                                    # archive. Counted, not merely handled --
                                    # a fix proven only on synthetic input is
                                    # a claim about the fixture. This number
                                    # is how a real run demonstrates the fixed
                                    # path actually ENGAGED on real bytes.
                                    cls["NESTED_ARCHIVE_MEASURED"] += 1
                            elif sl.at(dstart, 4) == SIG:
                                consumed = 0   # empty entry, no descriptor
                            else:
                                cls["STORED_NO_LENGTH"] += 1
                                detail["STORED_NO_LENGTH"].append(name)
                                nxt = sl.find(SIG, dstart)
                                if nxt < 0:
                                    break
                                resyncs.append((dstart, nxt - dstart))
                                pos = nxt
                                continue
                    got_crc = 0
                    usize = consumed
                    p = dstart
                    while p < dstart + consumed:
                        b = sl.at(p, min(CHUNK, dstart + consumed - p))
                        if not b:
                            break
                        blocks.append(b)
                        got_crc = zlib.crc32(b, got_crc)
                        p += len(b)
                    got_crc &= 0xffffffff
                else:
                    cls[f"METHOD_{meth}"] += 1
                    detail[f"METHOD_{meth}"].append(name)
                    nxt = sl.find(SIG, dstart)
                    if nxt < 0:
                        break
                    resyncs.append((dstart, nxt - dstart))
                    pos = nxt
                    continue

                end = dstart + consumed
                exp = crc
                if streaming:
                    g = descriptor_at(sl, end)
                    if g is None or g[1] != consumed:
                        cls["NO_DESCRIPTOR"] += 1
                        got = descriptor_at(sl, end)
                        detail["NO_DESCRIPTOR"].append(
                            f"meth={meth} streaming={streaming} "
                            f"dstart={dstart} consumed={consumed} "
                            f"end={end} hdr_csz={csz} hdr_usz={usz} "
                            f"dd_at_end={got} :: {name[-60:]}")
                        pos = end
                        continue
                    exp = g[0]
                    end += g[3]

                if got_crc != exp:
                    cls["CRC_MISMATCH"] += 1
                    detail["CRC_MISMATCH"].append(
                        f"{name} :: usize={usize} exp={exp:08x} got={got_crc:08x}")
                    pos = end
                    continue

                if is_dir:
                    cls["DIRECTORY"] += 1
                    if out and name not in names:
                        names.add(name)
                        zi = zipfile.ZipInfo(name)
                        zi.external_attr = (0o40755 << 16) | 0x10
                        out.writestr(zi, b"")
                    pos = end
                    continue

                cls["RECOVERED"] += 1
                recovered_bytes += usize
                if INNARDS_RE.match(name):
                    # An independent detector for the failure the exit code
                    # cannot see. Walking INTO a nested archive raises nothing
                    # and produces no resync -- it just emits that archive's
                    # internal members as though they were top-level files and
                    # loses the container. These names are the fingerprints of
                    # an Office/jar/apk interior; in a backup of a person's
                    # Drive they should essentially never appear at top level.
                    # A non-zero count here means look, even on a "clean" run.
                    suspect_innards.append(name)

                if out:
                    wname = name
                    if wname in names:
                        dup += 1
                        stem, ext = os.path.splitext(wname)
                        wname = f"{stem}.dup{dup}{ext}"
                    names.add(wname)
                    zi = zipfile.ZipInfo(wname)
                    try:
                        zi.date_time = (
                            ((md >> 9) & 0x7f) + 1980, (md >> 5) & 0x0f,
                            md & 0x1f, (mt >> 11) & 0x1f, (mt >> 5) & 0x3f,
                            (mt & 0x1f) * 2)
                        if zi.date_time[1] == 0 or zi.date_time[2] == 0:
                            zi.date_time = (1980, 1, 1, 0, 0, 0)
                    except Exception:
                        zi.date_time = (1980, 1, 1, 0, 0, 0)
                    zi.compress_type = zipfile.ZIP_DEFLATED
                    zi.external_attr = 0o644 << 16
                    with out.open(zi, "w") as fh_out:
                        for b in blocks:
                            fh_out.write(b)
                    written += 1
                blocks = None
                pos = end
        finally:
            if out:
                out.close()

    report(final=True)
    total = sum(v for k, v in cls.items()
                if k not in ("REACHED_CENTRAL_DIRECTORY",
                             "NESTED_ARCHIVE_MEASURED"))
    clean = cls["RECOVERED"] + cls["DIRECTORY"]
    print("\n=== salvage result ===")
    for k, v in cls.most_common():
        print(f"  {v:8,}  {k}")
    print(f"  {total:8,}  TOTAL entries classified")
    print(f"  {recovered_bytes:,} bytes inflated and CRC-32 verified")
    print(f"  {written:,} entries written to the new archive")
    print(f"\naccounted clean: {clean:,}/{total:,} = "
          f"{100.0 * clean / max(total, 1):.2f}%")
    print(f"resyncs: {len(resyncs)}   bytes skipped: "
          f"{sum(n for _, n in resyncs):,}")
    nested = cls.get("NESTED_ARCHIVE_MEASURED", 0)
    print(f"\nnested archives measured by descriptor: {nested:,}")
    if nested:
        print("  Each of these is a STORED entry whose payload begins with a")
        print("  local-header signature. The retired defect read them as empty")
        print("  and walked INTO them, emitting their internal members as")
        print("  top-level files. A non-zero count here is the fixed path")
        print("  engaging on real bytes, not on a fixture.")
    else:
        print("  NONE encountered — so this run is NOT evidence about that path"
              " one way or the other.")
    print(f"\ncontainer-interior names seen at top level: {len(suspect_innards)}")
    if suspect_innards:
        print("  !! These are the fingerprint of a walk that stepped inside a")
        print("  !! nested archive. This check is independent of the exit code,")
        print("  !! because that failure raises nothing and causes no resync.")
        for n in suspect_innards[:15]:
            print(f"     {n}")
    else:
        print("  none — no sign the walk stepped inside a nested container")
    for off, n in resyncs[:10]:
        print(f"    resync at {off:,} skipped {n:,} bytes")
    if dup:
        print(f"\nduplicate names disambiguated with .dupN: {dup}")
    for cname in ("CRC_MISMATCH", "NO_DESCRIPTOR", "STORED_NO_LENGTH",
                  "INFLATE_FAIL"):
        if detail[cname]:
            print(f"\n-- {cname} ({len(detail[cname])}) first 10 --")
            for s in detail[cname][:10]:
                print("   ", s[:400])
    bad = (cls["CRC_MISMATCH"] + cls["INFLATE_FAIL"] + cls["NO_DESCRIPTOR"]
           + cls["STORED_NO_LENGTH"])
    # suspect_innards is a finding in its own right: everything else can be
    # clean and the archive still be wrong in the one way that is invisible.
    return 0 if bad == 0 and not resyncs and not suspect_innards else 2


sys.exit(main())
