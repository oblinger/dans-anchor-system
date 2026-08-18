#!/usr/bin/env python3
"""F336: enumerate the populated parent x method cells per facet from the live vault.

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
"""
import os, collections, json

VAULT = os.path.expanduser("~/ob/kmr")
SKIP_DIRS = {".git", ".obsidian", "node_modules", "__pycache__", ".venv",
             "target", "Yore", "Closet", "examples", "templates"}

FILE_FACETS = ["Backlog", "Inbox", "Log", "Track", "queries", "Status", "Roadmap",
               "Messages", "Icebox", "Chores", "Agenda", "Outputs", "PRD",
               "Architecture", "Testing", "Decisions", "Features", "Brief",
               "API Design", "System Design", "UX Design", "CLI", "Interface",
               "Completed Roadmap", "Exceptions", "Stories", "Versions", "Pebble",
               "Rock", "Notebook", "WP"]
FOLDER_FACETS = ["Log", "Rocks", "Pebbles", "Subs", "Features", "Backlog",
                 "Track", "Design", "WP", "Discussions", "Inbox", "Roadmap",
                 "Architecture"]


def load_anchor_slugs():
    """slug -> shallowest directory whose .anchor declares it."""
    slug_dir = {}
    for dirpath, dirnames, filenames in os.walk(VAULT):
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


def main():
    slug_dir = load_anchor_slugs()
    print(f"# {len(slug_dir)} distinct slugs declared in .anchor files\n")

    file_hits = collections.defaultdict(collections.Counter)
    file_ex = collections.defaultdict(dict)
    folder_hits = collections.defaultdict(collections.Counter)
    folder_ex = collections.defaultdict(dict)
    unowned = collections.Counter()

    def place(container_dir, name, slug, facet, hits, ex, is_dir):
        root = slug_dir.get(slug)
        if root is None:
            unowned[facet] += 1
            return
        target = os.path.join(container_dir, name) if is_dir else container_dir
        base = os.path.dirname(target) if is_dir else target
        rel = os.path.relpath(base, root)
        if rel.startswith(".."):
            unowned[facet] += 1
            return
        tmpl = generalise(rel, slug)
        if is_dir:
            tmpl = tmpl + "{slug} " + facet + "/"
        hits[facet][tmpl] += 1
        ex[facet].setdefault(tmpl, os.path.relpath(target, VAULT))

    for dirpath, dirnames, filenames in os.walk(VAULT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]

        for d in list(dirnames):
            for facet in FOLDER_FACETS:
                suf = " " + facet
                if not d.endswith(suf) or d.startswith(("DAS ", "FEX ", "HBR ")):
                    continue
                slug = d[:-len(suf)]
                if slug:
                    place(dirpath, d, slug, facet, folder_hits, folder_ex, True)
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
                    place(dirpath, fn, slug, facet, file_hits, file_ex, False)
                break

    def report(title, hits, ex):
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

    report("CELL  parent=anchor  method=file", file_hits, file_ex)
    report("CELL  parent=anchor  method=folder", folder_hits, folder_ex)
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


main()
