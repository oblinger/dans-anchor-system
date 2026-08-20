#!/usr/bin/env python3
"""renumber-rows.py — collapse an anchor's row kinds onto one number namespace.

WHY THIS EXISTS. Under the F329 folder form a backlog row's document is named
`{SLUG}{NNN} - {Title}.md` — the slug fused to a bare number, with the kind
letter DROPPED (F300, Dan 2026-08-02). Today F-docs already carry that form
(`TINK079 - Fleet.md`) while T-docs still carry the letter (`TINK T025 - …md`),
so `F079` and `T079` are two files with different basenames and nothing is
broken. The moment T-docs convert, they become the SAME basename. Two files in
the vault may not share one — so before the conversion, the numbers must be
made unique across every kind that mints a document.

Dan, 2026-08-19: *"it's vital that the vault doesn't have repeated base names …
both of them should just have the slug followed by the number, without the
letter F or T"* — and, on kinds: *"B really gets renamed to T, because those are
tasks, and Qs get renamed to T."* So the target vocabulary is F and T only, over
one shared number space per anchor. `backlog_edit.DOC_MINTING_KINDS` already
makes every FUTURE mint respect that; this script fixes the existing corpus.

WHAT MOVES, AND WHY THAT SIDE. F rows never move. Their numbers are the ones
already spent on letterless filenames, they are cited in prose and commit
messages across anchors, and they are the older half of the corpus. Everything
that has to give is on the T/B/Q side:

  * a `T<n>` whose number is also an `F<n>`  → a fresh number above high-water
  * every `B<n>`                             → `T<n>` if n is free, else fresh
  * every `Q<n>` ROW (indent 0, not a hosted `- **Q1 —` sub-bullet) → same rule

Fresh numbers are always allocated ABOVE the anchor's high-water mark, which is
what makes the rewrite safe to apply one row at a time: no new id can ever be an
old id, so no rename can chain into another rename's source.

WHAT GETS REWRITTEN. Structured references only, and every one of them:

  * the row header          `- **T204 —`      → `- **T400 —`
  * the row's block anchor  `^T204`           → `^T400`   (and `^T204-Q1`)
  * inbound block links     `[[X Backlog#^T204|T204]]`    (target AND alias)
  * the doc's own H1        `# [[X]] · T204 —`
  * the doc filename        via `anchor update`, which rewrites inbound
                            wiki-links to the doc as a side effect

BARE PROSE IS DELIBERATELY NOT REWRITTEN. A bare `T204` in running text is
ambiguous — TINK docs discuss HA's T204 constantly, and no regex distinguishes
"our T204" from "their T204" without reading the sentence. Rewriting those
mechanically would silently corrupt cross-anchor citations, which is a worse
failure than a stale one. Instead every surviving mention is REPORTED, scoped to
the anchor's own subtree, so a human (or an agent with the sentence in front of
it) can adjudicate. Silence here would be the lie; the report is the point.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# `RENUMBER_VAULT` exists so the test fixture can stand up a miniature vault —
# two anchors that both have a T002, and a shared Q.md that aggregates them —
# without the suite ever touching the real one.
VAULT = Path(os.environ.get("RENUMBER_VAULT", Path.home() / "ob/kmr"))
ANCHOR_CLI = Path.home() / "bin/anchor"

# An indent-0 row. Hosted questions (`  - **Q1 — …`) are indented and are NOT
# rows — they are sub-bullets whose ids are derived (`^T204-Q1`) and which move
# with their host automatically.
ROW_RE = re.compile(r"^- \*\*([A-Z]+)(\d+)\s+—")
MOVING_KINDS = ("T", "B", "Q")
KEEP_KINDS = ("F",)


def find_backlog(slug):
    """The one `{slug} Backlog.md` in the vault, flat or F329 folder form."""
    hits = [Path(p) for p in subprocess.run(
        ["find", str(VAULT), "-name", f"{slug} Backlog.md",
         "-not", "-path", "*/.git/*", "-not", "-path", "*/Yore/*",
         "-not", "-path", "*/Warden Corpus/*"],
        capture_output=True, text=True, check=True).stdout.split("\n") if p.strip()]
    if len(hits) != 1:
        sys.exit(f"renumber: expected exactly one '{slug} Backlog.md', found {len(hits)}")
    return hits[0]


def anchor_root(backlog, slug):
    """The anchor root — the nearest ancestor whose `.anchor` declares `slug:`.

    Presence of `.anchor` alone is NOT the test: every `{slug} Track/` carries a
    bare `.anchor` holding only a description, so the naive walk stops one level
    too deep and misses `{slug} Design/`, where feature docs live.
    """
    fallback = None
    for parent in backlog.parents:
        dot = parent / ".anchor"
        if not dot.exists():
            continue
        try:
            text = dot.read_text(encoding="utf-8")
        except OSError:
            continue
        m = re.search(r"^slug:\s*(\S+)", text, re.M)
        if m and m.group(1) == slug:
            return parent
        # Not every anchor declares `slug:` — several (the DAS example anchors,
        # among others) let the folder name carry it. Remember the first such
        # match but keep walking, since an explicit declaration always wins.
        if fallback is None and not m and parent.name == slug:
            fallback = parent
    if fallback is not None:
        return fallback
    sys.exit(f"renumber: no anchor root for '{slug}' above {backlog}")


def scan_rows(backlog):
    """[(kind, digits, num, title)] for every indent-0 row, in file order.

    `digits` is the LITERAL spelling as written — anchors zero-pad to three
    (`T002`) but the older `B` rows do not (`B18`), and a rewrite that guesses
    instead of quoting matches nothing and silently reports zero edits.
    """
    rows = []
    for line in backlog.read_text(encoding="utf-8").splitlines():
        m = ROW_RE.match(line)
        if m:
            title = line[m.end():].split("**")[0].strip()
            rows.append((m.group(1), m.group(2), int(m.group(2)), title))
    return rows


def build_plan(rows):
    """[(old_handle, new_handle, title)] — the rows that must be renumbered.

    F keeps everything it has. A T that does not collide with an F keeps its
    number too, so the churn is exactly the set of genuine conflicts plus the
    letter-only B/Q conversions. Fresh numbers start above the anchor's
    high-water mark across ALL kinds, so a new id is never an old id.
    """
    f_nums = {n for k, _d, n, _t in rows if k in KEEP_KINDS}
    t_nums = {n for k, _d, n, _t in rows if k == "T"}
    taken = set(f_nums) | (t_nums - f_nums)      # what stays put
    high = max((n for _k, _d, n, _t in rows), default=0)

    def fresh():
        nonlocal high
        high += 1
        while high in taken:
            high += 1
        taken.add(high)
        return high

    plan = []
    for kind, digits, num, title in rows:
        if kind not in MOVING_KINDS:
            continue
        if kind == "T" and num not in f_nums:
            continue                              # keeps its number and letter
        if kind in ("B", "Q") and num not in taken:
            taken.add(num)                        # letter changes, number free
            new = num
        else:
            new = fresh()
        # New ids are always written in the canonical zero-padded three-digit
        # form (DAS Backlog § Numbering policy), which is also what the mint
        # emits; the OLD id keeps whatever spelling the file actually uses.
        plan.append((f"{kind}{digits}", f"T{new:03d}", title))
    return plan


def qualified_hosts(needles):
    """Every file carrying one of the anchor-QUALIFIED needles.

    Qualified is the operative word. A bare `^T002` is meaningless out of
    context — 22 anchors have one — so only forms that name this anchor (its
    backlog, or its renamed document) can be rewritten outside its own files.
    """
    hits = set()
    for needle in needles:
        grep = subprocess.run(
            ["grep", "-rlF", "--include=*.md", needle, str(VAULT)],
            capture_output=True, text=True)
        hits |= {Path(l) for l in grep.stdout.split("\n")
                 if l.strip() and "/.git/" not in l and "/Yore/" not in l}
    return sorted(hits)


def find_doc(root, slug, old):
    """The row's document — the LETTERED filename form only, H1-confirmed.

    The fused form (`SCOUT003 - Title.md`) is deliberately excluded. It is the
    F-doc spelling: until the T-docs convert, a T row's document always carries
    its letter, and reaching for `{slug}{digits} - *` finds the FEATURE that
    happens to share the number — which is the very collision this whole
    migration exists to remove. An earlier draft did exactly that and renamed
    SCOUT's F003 and LUMEN's F005 feature docs out from under them.

    The H1 check is the belt to that braces: a document that does not introduce
    itself as `· {old} —` is not this row's document, whatever it is named.
    """
    hits = []
    for pat in (f"{slug} {old} - *.md", f"{slug} {old} — *.md"):
        hits.extend(p for p in root.rglob(pat) if ".git" not in p.parts)
    if not hits:
        return None
    if len(hits) > 1:
        sys.exit(f"renumber: {old} matches {len(hits)} docs: {hits}")
    doc = hits[0]
    try:
        head = doc.read_text(encoding="utf-8")[:4000]
    except (OSError, UnicodeDecodeError):
        head = ""
    if not re.search(rf"^#\s.*·\s*{old}\s+—", head, re.M):
        sys.exit(f"renumber: {doc.name!r} does not introduce itself as "
                 f"'· {old} —' — refusing to rename a document that may not be "
                 f"this row's")
    return doc


WIKI_SPAN = re.compile(r"\[\[[^\[\]]*\]\]")


class OutsideLinks:
    """Adapts a regex so `_apply` runs it only on text OUTSIDE `[[…]]` spans.

    Prose rules must not reach inside a wiki-link: the text there is a filename
    or an alias, both owned by the link rules, and a filename in particular must
    keep whatever spelling the file on disk actually has. Rather than bolt more
    lookaheads onto the prose pattern — which is how ` - ` and ` — ` guards got
    added, and how a legitimate `ABIO T002 — as gating…` got skipped — the link
    spans are held out of the substitution entirely.

    Quacks like `re.Pattern` to the extent `_apply` needs: `.subn`.
    """

    def __init__(self, rx):
        self.rx = rx

    def subn(self, repl, text):
        out, total, pos = [], 0, 0
        for span in WIKI_SPAN.finditer(text):
            chunk, n = self.rx.subn(repl, text[pos:span.start()])
            out.append(chunk)
            out.append(span.group(0))
            total += n
            pos = span.end()
        chunk, n = self.rx.subn(repl, text[pos:])
        out.append(chunk)
        return "".join(out), total + n


def _apply(f, subs, apply, counter):
    """Run (regex, replacement) pairs over one file. Returns True if changed."""
    try:
        text = f.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    out = text
    for rx, rep in subs:
        out, n = rx.subn(rep, out)
        counter[0] += n
    if out == text:
        return False
    if apply:
        f.write_text(out, encoding="utf-8")
    return True


def rewrite_qualified(slug, old, new, doc_stem, apply, old_stem=None):
    """Vault-wide, but ONLY the forms that name this anchor explicitly.

    `[[ABIO Backlog#^T002|T002]]` says which anchor it means, so both halves —
    the block target and the display alias — can be moved anywhere in the vault.
    A bare `^T002` cannot: an earlier draft rewrote every one it found in the
    files that happened to contain a qualified link, and silently renumbered
    ATT's own T002 rows and ten unrelated block anchors in the shared `Q.md`.
    That is the whole reason this function is split from the local one.
    """
    def realias(alias):
        """`|T002` → `|T012`, and `|ABIO T002` → `|ABIO T012`.

        The slug-prefixed display form is the one C37 asks for when a row is
        cited from ANOTHER anchor (`[[ABIO Backlog#^T002|ABIO T002]]`), so it is
        exactly the alias most likely to be left pointing at a dead id. A
        trailing title (`|T002 — Move the repo`) survives untouched.
        """
        return re.sub(rf"^(\\?\|)({re.escape(slug)} )?{old}\b",
                      lambda m: f"{m.group(1)}{m.group(2) or ''}{new}", alias)

    # ONE regex per whole link, never a free-floating alias rule: a file such as
    # the shared `Q.md` holds `[[ABIO Backlog#^T002|T002]]` and
    # `[[ATT Backlog#^T002|T002]]` side by side, and an alias rule that did not
    # know which link it sat inside would rewrite both.
    # The `(?<![A-Za-z0-9])` before the slug is load-bearing: without it, slug
    # `SV` matches inside `TSV Backlog`, and renumbering SV's T001/T002 silently
    # repointed TeamSaver's block links to ids TSV does not have. One slug in
    # this vault is a suffix of another; that is enough.
    #
    # `\|` and not just `|`: inside a markdown TABLE CELL the alias pipe must be
    # escaped or it ends the cell, so half the vault's cross-references spell it
    # `[[SV Backlog#^T006\|SV T006]]`. A pattern that only knows the bare pipe
    # silently skips every link that lives in a table.
    block_rx = re.compile(
        rf"\[\[([^\[\]]*?(?<![A-Za-z0-9]){re.escape(slug)} Backlog)"
        rf"#\^{old}((?:\\?\|[^\[\]]*)?)\]\]")
    # `Re-homed from A2X T002` — prose, but the slug qualifies it, so it is as
    # unambiguous as a link and gets moved rather than merely reported. It runs
    # only OUTSIDE `[[…]]` (see `outside_links`): a wiki-link's interior is the
    # link rules' business, and a filename there must keep whatever spelling the
    # file on disk actually has.
    prose_rx = re.compile(
        rf"(?<![A-Za-z0-9])({re.escape(slug)}) {old}(?![0-9A-Za-z])")
    # `[[VEC Backlog|VEC T003]]` — a link to the backlog PAGE whose display text
    # names the row. No block anchor, so the rule above never sees it, and the
    # prose rule refuses it because it ends in `]]`. It is still unambiguous.
    plain_rx = re.compile(
        rf"\[\[([^\[\]|]*(?<![A-Za-z0-9]){re.escape(slug)} Backlog)(\\?\|)([^\[\]]*)\]\]")
    named = re.compile(rf"(?<![A-Za-z0-9]){re.escape(slug)} {old}(?![0-9A-Za-z])")
    subs = [(block_rx, lambda m: f"[[{m.group(1)}#^{new}{realias(m.group(2))}]]"),
            (plain_rx,
             lambda m: f"[[{m.group(1)}{m.group(2)}"
                       f"{named.sub(f'{slug} {new}', m.group(3))}]]"),
            (OutsideLinks(prose_rx), rf"\1 {new}"),
            # A bare, unbracketed `ATT Backlog#^Q002` — the shape an Inbox entry
            # uses inside a code span, where a live wiki-link would be wrong.
            # Runs LAST, so every `[[…]]` occurrence has already been consumed
            # by the two link rules above and only the bare ones are left.
            (re.compile(rf"((?<![A-Za-z0-9]){re.escape(slug)} Backlog)#\^{old}\b"),
             rf"\1#^{new}")]
    if old_stem and doc_stem and old_stem != doc_stem:
        # Retarget any link the anchor CLI left on the OLD filename. It rewrites
        # most of them, but not one wrapped in HookAnchor's struck form
        # (`~~[[HA T013 - Title|T013]]~~`) — two of ~90 renames on 2026-08-19
        # came out that way, and a link to a file that no longer exists is
        # exactly the rot this migration must not create.
        subs.append((re.compile(rf"\[\[{re.escape(old_stem)}(?=[\]|#])"),
                     f"[[{doc_stem}"))
    if doc_stem:
        # `→ [[TINK012 - Title|T002]]` — the anchor CLI moved the target when it
        # renamed the file; the alias it left behind still says the old id.
        doc_rx = re.compile(
            rf"\[\[({re.escape(doc_stem)})((?:\|[^\[\]]*)?)\]\]")
        subs.append((doc_rx, lambda m: f"[[{m.group(1)}{realias(m.group(2))}]]"))
    needles = [f"{slug} Backlog#^{old}", f"{slug} {old}"]
    if doc_stem:
        needles.append(f"[[{doc_stem}")
    if old_stem and old_stem != doc_stem:
        needles.append(f"[[{old_stem}")
    changed, counter = [], [0]
    for f in qualified_hosts(needles):
        if _apply(f, subs, apply, counter):
            changed.append(f)
    return changed, counter[0]


def rewrite_local(backlog, doc, old, new, apply):
    """The two files that OWN the id: the backlog row, and the row's document.

    Inside these, an unqualified `^T002` is unambiguous — it is this anchor's
    block anchor. The one exception is a `#^` inside somebody else's block link
    (`[[HA Backlog#^T002|T002]]` cited in prose), which the lookbehind excludes.
    """
    subs = [
        (re.compile(rf"(?<!#)\^{old}\b"), f"^{new}"),          # `^T002`, `^T002-Q1`
        (re.compile(rf"(?<=\*\*){old}(?=\s+—)"), new),         # the row header
        (re.compile(rf"(?<=·\s){old}(?=\s+—)"), new),          # the doc's H1
        # `[Blocked T068]` / `[Waiting T068]` — C55 resolves a blocker handle
        # against this anchor's own rows, so a renumber that leaves the bracket
        # behind points the row at a blocker that will never exist and can
        # therefore never unblock it.
        (re.compile(rf"(?<=\[)(Blocked|Waiting)\s+{old}(?=[\]\s])"), rf"\1 {new}"),
    ]
    changed, counter = [], [0]
    for f in [p for p in (backlog, doc) if p is not None]:
        if _apply(f, subs, apply, counter):
            changed.append(f)
    return changed, counter[0]


def residual_prose(root, old):
    """Surviving bare mentions inside the anchor's own tree, for human review.

    Both the padded and unpadded spellings are searched — over-reporting here is
    free, while a missed stale citation is exactly what this pass exists to
    surface.
    """
    kind, digits = re.match(r"([A-Z]+)(\d+)", old).groups()
    forms = {old, f"{kind}{int(digits)}", f"{kind}{int(digits):03d}"}
    hits = []
    rx = re.compile(r"(?<![A-Za-z0-9^#|])(" +
                    "|".join(sorted(forms, key=len, reverse=True)) +
                    r")(?![0-9A-Za-z-])")
    for f in sorted(root.rglob("*.md")):
        if ".git" in f.parts:
            continue
        try:
            lines = f.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for i, line in enumerate(lines, 1):
            if rx.search(line):
                hits.append((f, i, line.strip()[:160]))
    return hits


def rename_doc(doc, slug, new, dry):
    """Rename via the anchor CLI so inbound wiki-links are rewritten with it.

    The new stem is the FUSED form — slug, bare number, ASCII hyphen, title —
    which is the whole reason the renumber is happening.
    """
    title = re.sub(r"^.*? - ", "", doc.stem, count=1)
    dest = doc.with_name(f"{slug}{new[1:]} - {title}.md")
    cmd = [str(ANCHOR_CLI), "update", str(doc), str(dest), "--root", str(VAULT)]
    if dry:
        cmd.append("--dry-run")
    res = subprocess.run(cmd, capture_output=True, text=True)
    return dest, res


def fuse_docs(root, slug, apply):
    """Rename `{SLUG} T<n> - Title.md` → `{SLUG}<n> - Title.md`, the F300 form.

    The point of the whole exercise: one filename grammar for every row document,
    the slug fused to a bare number with the kind letter dropped. Safe only once
    the numbers are unique, which is what `apply` above establishes — run it
    first or this collides by construction.

    Nothing but the filename moves. The row's alias (`|T025`), the doc's H1
    (`· T025 —`) and every block anchor keep the letter, exactly as F-docs do:
    per the /feature convention the fused spelling lives in the filename and
    nowhere else. `anchor update` repoints the inbound wiki-links.
    """
    out = []
    for doc in sorted(root.rglob(f"{slug} T*.md")):
        if ".git" in doc.parts:
            continue
        m = re.match(rf"^{re.escape(slug)} T(\d+) - (.+)$", doc.stem)
        if not m:
            continue
        dest = doc.with_name(f"{slug}{m.group(1)} - {m.group(2)}.md")
        if dest.exists():
            out.append((doc, dest, None, "REFUSED — destination exists"))
            continue
        if apply:
            res = subprocess.run(
                [str(ANCHOR_CLI), "update", str(doc), str(dest),
                 "--root", str(VAULT)], capture_output=True, text=True)
            note = (res.stdout + res.stderr).strip().split("\n")[-1]
            out.append((doc, dest, res.returncode, note))
        else:
            out.append((doc, dest, None, "would rename"))
    return out


def verify(slug, backlog):
    """Every reference that NAMES a row of this anchor which no longer exists.

    The renumber's post-condition, and the only honest one: a run that reports
    edits has proved nothing about what it left behind. Both qualified forms are
    checked — `{slug} Backlog#^id` links and `{slug} id` prose — against the ids
    the backlog actually carries.
    """
    text = backlog.read_text(encoding="utf-8")
    live = (set(re.findall(r"\^([A-Z]+\d+)\b", text))
            | {f"{k}{d}" for k, d, _n, _t in scan_rows(backlog)})
    prose = re.compile(rf"(?<![A-Za-z0-9\[]){re.escape(slug)} ([TBQ]\d+)(?![0-9A-Za-z])")
    block = re.compile(rf"(?<![A-Za-z0-9]){re.escape(slug)} Backlog#\^([A-Z]+\d+)")
    dangling = []
    for f in sorted(VAULT.rglob("*.md")):
        if ".git" in f.parts or "/Yore/" in str(f) or ".history" in f.parts:
            continue
        try:
            lines = f.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for i, line in enumerate(lines, 1):
            for form, rx in (("prose", prose), ("block", block)):
                for m in rx.finditer(line):
                    if m.group(1) not in live:
                        dangling.append((form, m.group(1), f, i))
    return dangling


def main():
    ap = argparse.ArgumentParser(
        description="collapse an anchor's row kinds onto one number namespace")
    ap.add_argument("action", choices=["plan", "apply", "verify", "fuse"])
    ap.add_argument("--anchor", required=True)
    ap.add_argument("--limit", type=int, help="apply only the first N rows")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    slug = args.anchor
    backlog = find_backlog(slug)
    root = anchor_root(backlog, slug)
    plan = build_plan(scan_rows(backlog))

    if args.action == "fuse":
        left = build_plan(scan_rows(backlog))
        if left:
            sys.exit(f"{slug}: {len(left)} row(s) still collide — run "
                     f"`apply` before `fuse`, or the rename creates the very "
                     f"duplicate basename it exists to prevent")
        renames = fuse_docs(root, slug, apply=not args.dry_run)
        print(f"{slug}: {len(renames)} document(s)")
        for doc, dest, rc, note in renames:
            print(f"   {doc.name!r} → {dest.name!r}"
                  + (f"  (rc={rc})" if rc is not None else "") + f"  {note}")
        return

    if args.action == "verify":
        bad = verify(slug, backlog)
        if not bad:
            print(f"{slug}: clean — every qualified reference resolves")
            return
        print(f"{slug}: {len(bad)} DANGLING reference(s)")
        for form, rid, f, i in bad:
            print(f"   {form:5} {rid:6} {f.relative_to(VAULT)}:{i}")
        sys.exit(1)

    if args.action == "plan":
        if args.json:
            print(json.dumps(plan))
        else:
            print(f"{slug}: {len(plan)} row(s) to renumber   (backlog: {backlog})")
            for old, new, title in plan:
                print(f"  {old:>6} → {new:<6}  {title[:78]}")
        return

    batch = plan[: args.limit] if args.limit else plan
    print(f"{slug}: {'DRY-RUN over' if args.dry_run else 'applying'} "
          f"{len(batch)} of {len(plan)} row(s)\n")
    for old, new, title in batch:
        print(f"── {old} → {new}   {title[:70]}")
        doc = find_doc(root, slug, old)
        doc_stem = old_stem = None
        if doc:
            old_stem = doc.stem
        if doc:
            # The rename runs FIRST: the anchor CLI repoints every inbound
            # `[[old stem]]` as it moves the file, and the alias fixups below
            # then need the new stem to anchor on.
            dest, res = rename_doc(doc, slug, new, args.dry_run)
            doc_stem = dest.stem
            tag = "would rename" if args.dry_run else "renamed"
            print(f"   doc: {tag} {doc.name!r} → {dest.name!r}  (anchor rc={res.returncode})")
            for line in (res.stdout + res.stderr).strip().split("\n"):
                if line.strip():
                    print(f"        | {line}")
            if not args.dry_run and res.returncode == 0:
                doc = dest
        else:
            print("   doc: none")

        run = not args.dry_run
        loc, n_loc = rewrite_local(backlog, doc, old, new, apply=run)
        qual, n_qual = rewrite_qualified(slug, old, new, doc_stem, apply=run,
                                         old_stem=old_stem)
        print(f"   text: {n_loc} local + {n_qual} qualified edit(s) in "
              f"{len(set(loc) | set(qual))} file(s)")
        for f in sorted(set(loc) | set(qual)):
            print(f"        | {f.relative_to(VAULT)}")
        if run:
            left = residual_prose(root, old)
            if left:
                print(f"   ⚠ {len(left)} unqualified mention(s) of {old} remain "
                      f"in the {slug} tree (ambiguous — review by hand):")
                for f, i, line in left[:8]:
                    print(f"        | {f.relative_to(VAULT)}:{i}  {line}")
        print()


if __name__ == "__main__":
    main()
