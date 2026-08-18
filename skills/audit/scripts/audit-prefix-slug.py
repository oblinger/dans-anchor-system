#!/usr/bin/env python3
"""Split the 'unowned' instances into the two very different things they contain.

F303 records that `{slug}` is the wrong variable name for a facet file's prefix,
because the prefix is derived from the Backlog filename rather than the anchor's
declared slug -- `Warden Inbox.md` lives under `slug: WARD`.  The placement
measurement's leftover bucket should therefore hold BOTH:

  (1) real instances whose prefix disagrees with the declared slug -- the thing
      F303 is talking about, and the reason a placement key cannot say {{SLUG}};
  (2) documents that merely END in a facet word and are not instances at all --
      "2023 Beta Testing.md", "Precision & Recall - Hypothesis Testing.md".

Telling them apart matters: (1) is a finding, (2) is noise, and reporting the
combined number as though it were (1) would badly overstate the divergence.
"""
import os, collections

VAULT = os.path.expanduser("~/ob/kmr")
SKIP_DIRS = {".git", ".obsidian", "node_modules", "__pycache__", ".venv",
             "target", "Yore", "Closet", "examples", "templates"}
FACETS = ["Backlog", "Inbox", "Log", "Track", "queries", "Status", "Roadmap",
          "Messages", "Icebox", "Chores", "Agenda", "Outputs", "PRD",
          "Architecture", "Testing", "Decisions", "Features", "Brief",
          "API Design", "System Design", "UX Design", "CLI", "Interface",
          "Completed Roadmap", "Exceptions", "Stories", "Versions", "Pebble",
          "Rock", "Notebook", "WP"]


def anchor_slug(d):
    p = os.path.join(d, ".anchor")
    if not os.path.isfile(p):
        return None
    try:
        txt = open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        return None
    for line in txt.splitlines():
        if line.strip().startswith("slug:"):
            return line.split(":", 1)[1].strip().strip('"').strip("'")
    return ""          # anchor exists but declares no slug


def main():
    declared = {}
    for dirpath, dirnames, filenames in os.walk(VAULT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        if ".anchor" in filenames:
            declared[dirpath] = anchor_slug(dirpath)
    slugs = {s for s in declared.values() if s}

    divergent, collisions, noslug = [], [], []
    for dirpath, dirnames, filenames in os.walk(VAULT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            if not fn.endswith(".md") or fn.startswith(("DAS ", "FEX ", "HBR ")):
                continue
            stem = fn[:-3]
            for facet in FACETS:
                if not stem.endswith(" " + facet):
                    continue
                prefix = stem[:-len(facet) - 1]
                if prefix in slugs:
                    break                       # already counted as owned
                # is there an enclosing anchor whose tree this prefix belongs to?
                cur, found = dirpath, None
                while cur.startswith(VAULT) and len(cur) > len(VAULT):
                    if cur in declared and (os.path.basename(cur) == prefix
                                            or os.path.basename(cur).startswith(prefix + " ")):
                        found = cur
                        break
                    cur = os.path.dirname(cur)
                rec = (facet, prefix, declared.get(found), os.path.relpath(
                    os.path.join(dirpath, fn), VAULT))
                if found is None:
                    collisions.append(rec)
                elif declared[found]:
                    divergent.append(rec)
                else:
                    noslug.append(rec)
                break

    print(f"REAL instances whose prefix != the anchor's DECLARED slug: {len(divergent)}")
    for facet, prefix, slug, path in sorted(divergent)[:25]:
        print(f"   prefix '{prefix}' vs slug '{slug}'   {path}")
    if len(divergent) > 25:
        print(f"   ... and {len(divergent)-25} more")

    print(f"\nREAL instances inside an anchor that declares NO slug: {len(noslug)}")
    for facet, prefix, slug, path in sorted(noslug)[:15]:
        print(f"   prefix '{prefix}'   {path}")
    if len(noslug) > 15:
        print(f"   ... and {len(noslug)-15} more")

    print(f"\nNOT instances — documents merely ending in a facet word: {len(collisions)}")
    c = collections.Counter(f for f, _, _, _ in collisions)
    for f, n in c.most_common(12):
        print(f"   {n:4d}  * {f}.md")
    print("   examples:")
    for facet, prefix, slug, path in sorted(collisions)[:8]:
        print(f"      {path}")


main()
