#!/usr/bin/env python3
"""Regression + behavior tests for the Warden scan command (F211).

Standalone — run `python3 test_warden_scan.py` (no pytest needed). Builds a
tiny markdown fixture tree in a temp dir and pins the scan contract, above
all the freshen-reads-nothing-when-nothing-changed property (the bug caught
during the build: non-bearing files were re-read on every sweep).
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import warden_scan  # noqa: E402


def write(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


def scan(root, index, rescan=False):
    prior_bearing, prior_seen = warden_scan.load_index(index)
    files, seen, stats = warden_scan.build_index(root, prior_bearing, prior_seen, rescan)
    # Mirrors main()'s index write — `schema` included, without which
    # load_index treats the index as stale and every freshen re-reads
    # everything. Keep in step with main() when the index gains a field.
    obj = {"root": root, "schema": warden_scan.INDEX_SCHEMA,
           "hash": warden_scan.index_hash(files), "files": files, "seen": seen}
    import json
    with open(index, "w", encoding="utf-8") as fh:
        json.dump(obj, fh)
    return obj, stats


def main():
    with tempfile.TemporaryDirectory() as root:
        index = os.path.join(root, ".warden", "idx.json")
        os.makedirs(os.path.dirname(index), exist_ok=True)
        write(root, "spec-a.md", "# Spec A\n\n# RULESET R-a\n- rule a\n")
        write(root, "sub/spec-b.md", "## Doc B\n\n## RULESET R-b\n- rule b\n")
        write(root, "plain.md", "# Just prose\n\nno rulesets here\n")
        write(root, "sub/notes.md", "# Notes\n")

        # 1. From-scratch: finds both bearing files, reads all four.
        obj, st = scan(root, index, rescan=True)
        assert st["bearing"] == 2, st
        assert st["seen"] == 4, st
        assert st["read"] == 4, st
        names = sorted(n for e in obj["files"] for n in e["ruleset_names"])
        assert names == ["R-a", "R-b"], names

        # 2. Freshen with nothing changed: reads ZERO (the regression guard).
        h_before = obj["hash"]
        obj, st = scan(root, index)
        assert st["read"] == 0, f"freshen re-read {st['read']} unchanged files: {st}"
        assert st["reused"] == 4, st
        assert obj["hash"] == h_before, "hash moved on a no-op freshen"

        # 3. Touch a bearing file: exactly one re-read, index unchanged.
        os.utime(os.path.join(root, "spec-a.md"), ns=(2 ** 40, 2 ** 40))
        obj, st = scan(root, index)
        assert st["read"] == 1, st
        assert st["bearing"] == 2, st
        assert obj["hash"] == h_before, "content-identical re-read moved the hash"

        # 4. Add a ruleset to a previously non-bearing file: it joins the index.
        write(root, "plain.md", "# Just prose\n\n# RULESET R-c\n- rule c\n")
        obj, st = scan(root, index)
        assert st["read"] == 1, st
        assert st["bearing"] == 3, st
        assert obj["hash"] != h_before, "new ruleset did not move the hash"

        # 5. Delete a bearing file: it drops out.
        os.remove(os.path.join(root, "sub/spec-b.md"))
        obj, st = scan(root, index)
        assert st["bearing"] == 2, st
        assert st["seen"] == 3, st
        remaining = sorted(n for e in obj["files"] for n in e["ruleset_names"])
        assert remaining == ["R-a", "R-c"], remaining

        # 6. Fence-awareness (F232 A1): a `# RULESET` heading inside a ```
        # code fence is a shown example, not a live declaration — the file is
        # not bearing; a live heading after a closed fence still is.
        write(root, "fenced.md",
              "# Doc\n\n```\n# RULESET R-fenced\n```\n\nprose\n")
        obj, st = scan(root, index)
        assert st["bearing"] == 2, f"fenced ruleset was indexed: {st}"
        write(root, "fenced.md",
              "# Doc\n\n```\n# RULESET R-fenced\n```\n\n# RULESET R-real\n")
        obj, st = scan(root, index)
        names = sorted(n for e in obj["files"] for n in e["ruleset_names"])
        assert names == ["R-a", "R-c", "R-real"], names

    print("test_warden_scan: all 6 behaviors pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
