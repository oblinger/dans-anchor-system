#!/usr/bin/env python3
"""F336: facet placement -- measure the populated parent x method cells, and check
live instances against the placement each facet's subsystem implies.

parent  in (anchor, file)          -- what the instance hangs off
method  in (inline, file, folder)  -- how it is materialised

Placement is measured relative to the anchor that DECLARES the instance's slug in
its `.anchor` file.  Two cheaper resolutions were tried first and both lied:

  - deepest enclosing anchor -- `{slug} Track/` carries its own `.anchor`, so every
    instance resolved to "at an anchor root" and the split vanished;
  - topmost slug-NAMED ancestor -- many anchor directories are not named after
    their slug (`sv-pipe` -> SVP, `alg2-experimental` -> A2X), so the climb stopped
    at `SVP Track/` and reported it as the anchor root.

Only the declared slug gets it right, which is itself worth knowing: an anchor's
identity is its `.anchor` slug, never its directory name.

MODES
  (default)     report the populated cells per facet -- the measurement
  --check       flag instances that deviate from their subsystem's placement
  --self-test   seed a deliberate mismatch and assert the checker catches it

WHY --check EXISTS.  A `::` key nothing reads is prose with colons, and this vault
has been bitten by that shape twice (T202's anchor-local ruleset that never loads;
guards that pass without protecting).  The checker is part of F336's design, not a
follow-on -- and --self-test is here because a checker that has never been SEEN to
fail is indistinguishable from one that cannot.
"""
import os, sys, collections, json, tempfile, shutil

VAULT = os.path.expanduser("~/ob/kmr")
SKIP_DIRS = {".git", ".obsidian", "node_modules", "__pycache__", ".venv",
             "target", "Yore", "Closet", "examples", "templates",
             # Warden's test corpus holds synthetic anchors (`FX4 Backlog.md`
             # and friends) built to be malformed on purpose.  Measuring them
             # against the live standard reports the fixture as a defect.
             "Warden Corpus"}

FILE_FACETS = ["Backlog", "Inbox", "Log", "Track", "queries", "Status", "Roadmap",
               "Messages", "Icebox", "Chores", "Agenda", "Outputs", "PRD",
               "Architecture", "Testing", "Decisions", "Features", "Brief",
               "API Design", "System Design", "UX Design", "CLI", "Interface",
               "Completed Roadmap", "Exceptions", "Stories", "Versions", "Pebble",
               "Rock", "Notebook", "WP"]
FOLDER_FACETS = ["Log", "Rocks", "Pebbles", "Subs", "Features", "Backlog",
                 "Track", "Design", "WP", "Discussions", "Inbox", "Roadmap",
                 "Architecture"]

# ── placement rules ─────────────────────────────────────────────────────────
#
# Measured 2026-08-18 (see F336 § What the corpus actually does).  Placement is
# per SUBSYSTEM, not per facet -- so the rule is a default per subsystem plus a
# key only where a facet genuinely deviates.  Anything not named below is
# UNRULED and reported separately: the checker enforces what has been measured
# and ruled, and stays silent on the rest rather than inventing a standard.

SUBSYSTEM_DEFAULT = {
    "Tracking": ["{anchor}/{slug} Track/"],
    "Design":   ["{anchor}/{slug} Design/"],
}

FACET_SUBSYSTEM = {
    # Tracking -- 100%-uniform in the corpus unless noted
    "Backlog": "Tracking", "queries": "Tracking", "Status": "Tracking",
    "Agenda": "Tracking", "Pebble": "Tracking", "Rock": "Tracking",
    "Notebook": "Tracking", "Messages": "Tracking", "Track": "Tracking",
    "Icebox": "Tracking", "Chores": "Tracking", "Exceptions": "Tracking",
    "Inbox": "Tracking",
    # Design
    "PRD": "Design", "Stories": "Design", "Architecture": "Design",
    "Testing": "Design", "Decisions": "Design", "UX Design": "Design",
    "API Design": "Design", "Interface": "Design",
}

# Stated deviations.  Each is a deliberate exception the measurement found and
# F336 § "The default should be the facet's subsystem" names one by one.
FACET_EXCEPTION = {
    # Log sits at the anchor ROOT, alone among tracking facets -- 48 of 60.
    # DAS file-association documented this and it read as a universal rule only
    # because Log is the facet whose folder form is most common.
    "Log": ["{anchor}/", "{anchor}/{slug} Log/"],
    # A CLI reference is user-facing though CLI is a Code facet.
    "CLI": ["{anchor}/{slug} User Docs/"],
    # Mid-migration per F142/DAS Features: Design is canonical, Track is the
    # pre-migration home, anchors reposition on their next /feature touch.
    # BOTH are conforming until the lazy migration completes.
    "Features": ["{anchor}/{slug} Design/", "{anchor}/{slug} Track/"],
    # Backlog and Architecture legitimately populate the folder cell too.
    "Backlog": ["{anchor}/{slug} Track/", "{anchor}/{slug} Track/{slug} Backlog/"],
    "Pebbles": ["{anchor}/{slug} Track/", "{anchor}/{slug} Track/{slug} Pebbles/"],
    # DAS Chores specifies the folder-form backlog as the home -- chores are
    # backlog-shaped work, so they sit with the backlog's own T-docs.  The
    # bare `{slug} Track/` form is the documented interim for an anchor whose
    # backlog is still a flat file.
    "Chores": ["{anchor}/{slug} Track/{slug} Backlog/", "{anchor}/{slug} Track/"],
}

# Genuinely undisciplined -- Roadmap is 23 instances across 6 placements (top
# share 47%), System Design 38% across 4.  These need a ruling from Dan, not a
# template, so the checker reports them as unruled rather than failing them.
UNRULED = {"Roadmap", "System Design"}


def load_anchor_slugs(vault):
    """slug -> shallowest directory whose .anchor declares it."""
    slug_dir = {}
    for dirpath, dirnames, filenames in os.walk(vault):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        if ".anchor" not in filenames:
            continue
        try:
            txt = open(os.path.join(dirpath, ".anchor"), encoding="utf-8",
                       errors="replace").read()
        except OSError:
            continue
        slug = None
        for line in txt.splitlines():
            line = line.strip()
            if line.startswith("slug:"):
                slug = line.split(":", 1)[1].strip().strip('"').strip("'")
                break
        if not slug:
            slug = os.path.basename(dirpath)
        prev = slug_dir.get(slug)
        if prev is None or dirpath.count(os.sep) < prev.count(os.sep):
            slug_dir[slug] = dirpath
    return slug_dir


def generalise(rel, slug):
    if rel in (".", ""):
        return "{anchor}/"
    out = []
    for p in rel.split(os.sep):
        if p == slug:
            out.append("{slug}")
        elif p.startswith(slug + " "):
            out.append("{slug} " + p[len(slug) + 1:])
        else:
            out.append(p)
    return "{anchor}/" + "/".join(out) + "/"


def scan(vault):
    """Walk the vault once and return every located instance.

    Yields dicts: facet, tmpl (generalised placement), path (vault-relative),
    is_dir.  The single walk backs both the report and the check, so the two
    modes can never disagree about what the corpus contains.
    """
    slug_dir = load_anchor_slugs(vault)
    found, unowned = [], collections.Counter()

    def place(container_dir, name, slug, facet, is_dir):
        root = slug_dir.get(slug)
        if root is None:
            unowned[facet] += 1
            return
        # `base` is the container the placement rule names; `target` is the
        # instance itself.  They differ for a file (its directory vs the file)
        # and the two were conflated before --self-test caught it, so every
        # file-form "e.g." in the measurement named a folder, not the document.
        target = os.path.join(container_dir, name)
        base = os.path.dirname(target) if is_dir else container_dir
        rel = os.path.relpath(base, root)
        if rel.startswith(".."):
            unowned[facet] += 1
            return
        tmpl = generalise(rel, slug)
        if is_dir:
            tmpl = tmpl + "{slug} " + facet + "/"
        found.append({"facet": facet, "tmpl": tmpl, "is_dir": is_dir,
                      "root": root, "slug": slug,
                      "path": os.path.relpath(target, vault)})

    for dirpath, dirnames, filenames in os.walk(vault):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]

        for d in list(dirnames):
            for facet in FOLDER_FACETS:
                suf = " " + facet
                if not d.endswith(suf) or d.startswith(("DAS ", "FEX ", "HBR ")):
                    continue
                slug = d[:-len(suf)]
                if slug:
                    place(dirpath, d, slug, facet, True)
                break

        for fn in filenames:
            if not fn.endswith(".md") or fn.startswith(("DAS ", "FEX ", "HBR ")):
                continue
            stem = fn[:-3]
            for facet in FILE_FACETS:
                suf = " " + facet
                if not stem.endswith(suf):
                    continue
                slug = stem[:-len(suf)]
                if slug:
                    place(dirpath, fn, slug, facet, False)
                break

    return found, unowned, len(slug_dir)


def expected_for(facet):
    """The conforming placements for a facet, or None when it is unruled.

    A facet is ruled when it either declares a deviation or belongs to a
    subsystem with a measured default.  Everything else returns None and is
    reported, never failed -- silence is the honest answer for a facet whose
    standard has not been decided.
    """
    if facet in UNRULED:
        return None
    if facet in FACET_EXCEPTION:
        return FACET_EXCEPTION[facet]
    sub = FACET_SUBSYSTEM.get(facet)
    if sub is None:
        return None
    return SUBSYSTEM_DEFAULT[sub]


def _subsystem_folder_exists(inst, expected):
    """True when the anchor actually HAS one of the folders the rule names.

    Resolves each expected template against the instance's own anchor root and
    slug, and asks the filesystem.  Only the leading folder of a template is
    tested -- `{anchor}/{slug} Track/{slug} Backlog/` is satisfied for this
    purpose by `{slug} Track/` existing, because that is the folder whose
    absence would leave the instance homeless.
    """
    for tmpl in expected:
        body = tmpl[len("{anchor}/"):].rstrip("/")
        if not body:
            continue
        first = body.split("/")[0].replace("{slug}", inst["slug"])
        if os.path.isdir(os.path.join(inst["root"], first)):
            return True
    return False


def check(vault, quiet=False):
    """Flag every instance sitting outside its facet's conforming placements.

    Returns the list of deviations so --self-test can assert on it.
    """
    found, _unowned, _n = scan(vault)
    deviations, conforming = [], collections.Counter()
    unruled = collections.Counter()

    for inst in found:
        exp = expected_for(inst["facet"])
        if exp is None:
            unruled[inst["facet"]] += 1
            continue
        # A folder-form instance carries its own `{slug} Facet/` tail; compare
        # the container it sits in, which is what the placement rule names.
        tmpl = inst["tmpl"]
        tail = "{slug} " + inst["facet"] + "/"
        if inst["is_dir"]:
            container = tmpl[:-len(tail)] if tmpl.endswith(tail) else tmpl
            ok = container in exp or tmpl in exp
        else:
            # A facet that materialises as a FOLDER carries an index file named
            # for the facet inside it -- `X Design/X Architecture/X
            # Architecture.md`.  That file is the folder method's own index, not
            # a misplaced file-method instance, so it conforms wherever the
            # folder does.  Without this clause the checker reported 31 of its
            # first 51 findings against perfectly conforming index pages.
            ok = tmpl in exp or (
                tmpl.endswith(tail) and tmpl[:-len(tail)] in exp)
        if not ok and tmpl == "{anchor}/" and not _subsystem_folder_exists(inst, exp):
            # A FLAT anchor -- one that never grew the `{slug} Design/` or
            # `{slug} Track/` folder the rule names -- has nowhere else to put
            # the instance, so the anchor root is not a deviation but the only
            # available placement.  Measured 2026-08-18: 8 of the checker's
            # first 22 findings were this, spread over 7 anchors (CAT, Disk,
            # DFP, START, Eli, AIS, CAT Backup).  Reporting them told the
            # reader to move a file into a folder that does not exist, which is
            # advice no one can follow -- the honest reading is that placement
            # binds an anchor only once it has the subsystem folder.
            #
            # Note this is a claim about the FILESYSTEM, not about the rule:
            # the moment such an anchor grows the folder, its root-placed
            # instances start deviating again, which is the intended behavior.
            ok = True
        if ok:
            conforming[inst["facet"]] += 1
        else:
            deviations.append(inst)

    if quiet:
        return deviations

    ruled = sum(conforming.values()) + len(deviations)
    print(f"{ruled} instances under a ruled facet; "
          f"{sum(conforming.values())} conform, {len(deviations)} deviate.\n")

    by_facet = collections.defaultdict(list)
    for d in deviations:
        by_facet[d["facet"]].append(d)
    for facet in sorted(by_facet, key=lambda f: -len(by_facet[f])):
        exp = expected_for(facet) or []
        print(f"{facet}  ({len(by_facet[facet])} deviating; expected "
              f"{' or '.join(exp)})")
        for d in sorted(by_facet[facet], key=lambda x: x["path"])[:12]:
            print(f"   {d['tmpl']:<44s} {d['path']}")
        if len(by_facet[facet]) > 12:
            print(f"   ... and {len(by_facet[facet]) - 12} more")
        print()

    if unruled:
        print("UNRULED -- no measured standard, reported not failed:")
        for f, n in unruled.most_common():
            why = "needs adjudication" if f in UNRULED else "subsystem not yet measured"
            print(f"   {n:5d}  {f:<20s} ({why})")
    return deviations


def self_test():
    """Seed a deliberate mismatch and assert the checker catches exactly it.

    A checker that has never been observed to fail is indistinguishable from
    one that cannot fail -- the T202 / guards-that-pass-without-protecting
    shape this vault has already been bitten by twice.
    """
    tmp = tempfile.mkdtemp(prefix="f336-selftest-")
    try:
        root = os.path.join(tmp, "zzt-anchor")
        os.makedirs(os.path.join(root, "ZZT Track"))
        os.makedirs(os.path.join(root, "ZZT Design"))
        with open(os.path.join(root, ".anchor"), "w") as fh:
            fh.write("slug: ZZT\n")

        # Conforming: a Tracking facet inside `{anchor}/ZZT Track/`.
        open(os.path.join(root, "ZZT Track", "ZZT Backlog.md"), "w").close()
        # Deviating: the same facet parked in the Design folder instead.
        open(os.path.join(root, "ZZT Design", "ZZT Inbox.md"), "w").close()

        devs = check(tmp, quiet=True)
        paths = sorted(d["path"] for d in devs)
        expect = ["zzt-anchor/ZZT Design/ZZT Inbox.md"]

        if paths == expect:
            print("PASS  seeded mismatch caught, and only it")
            print(f"      flagged: {paths[0]}")
            print("      the conforming ZZT Backlog.md was not flagged")
            return 0
        print("FAIL  checker did not isolate the seeded mismatch")
        print(f"      expected: {expect}")
        print(f"      got:      {paths}")
        return 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def report(vault):
    found, unowned, nslugs = scan(vault)
    print(f"# {nslugs} distinct slugs declared in .anchor files\n")

    file_hits = collections.defaultdict(collections.Counter)
    file_ex = collections.defaultdict(dict)
    folder_hits = collections.defaultdict(collections.Counter)
    folder_ex = collections.defaultdict(dict)
    for inst in found:
        hits = folder_hits if inst["is_dir"] else file_hits
        ex = folder_ex if inst["is_dir"] else file_ex
        hits[inst["facet"]][inst["tmpl"]] += 1
        ex[inst["facet"]].setdefault(inst["tmpl"], inst["path"])

    def emit(title, hits, ex):
        print("=" * 78)
        print(title)
        print("=" * 78)
        rows = []
        for facet in sorted(hits):
            c = hits[facet]
            total = sum(c.values())
            top = c.most_common(5)
            rows.append((facet, total, 100 * top[0][1] // total, len(c), top))
        for facet, total, pct, ndist, top in sorted(rows, key=lambda r: -r[1]):
            flag = "   <== SPLIT" if pct < 85 else ""
            print(f"\n{facet}  ({total} instances, {ndist} distinct placement(s), "
                  f"dominant {pct}%){flag}")
            for t, n in top:
                print(f"   {n:4d}  {t:<46s} {'#' * min(30, n)}")
                print(f"         e.g. {ex[facet][t]}")
        print()

    emit("CELL  parent=anchor  method=file", file_hits, file_ex)
    emit("CELL  parent=anchor  method=folder", folder_hits, folder_ex)
    if unowned:
        print("Instances whose slug matches no declared anchor, or that sit outside it")
        print("(file-parented, free-floating, or a slug the .anchor never declares):")
        for f, n in unowned.most_common():
            print(f"   {n:4d}  {f}")

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "f336-cells.json"), "w") as fh:
        json.dump({"file": {k: dict(v) for k, v in file_hits.items()},
                   "folder": {k: dict(v) for k, v in folder_hits.items()},
                   "unowned": dict(unowned)}, fh, indent=1)


def main():
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    if "--check" in sys.argv:
        devs = check(VAULT)
        sys.exit(1 if devs else 0)
    report(VAULT)


main()
