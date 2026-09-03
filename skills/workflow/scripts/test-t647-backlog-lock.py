#!/usr/bin/env python3
"""T647 / P0020 — concurrent `state define` calls on one backlog must all land.

Before the lock, two sessions interleaved a read-modify-write on
`{slug} Backlog.md` and the later write carried the earlier row away (Winnie
T027, 2026-09-01). This spawns N `state define` processes at once against a
fixture vault and asserts every minted row is present afterwards, and that the
ids are distinct. Run: python3 test-t647-backlog-lock.py
"""
import os
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

STATE = Path(__file__).resolve().parent / "state"
N = 6


def main() -> int:
    root = Path(tempfile.mkdtemp(prefix="t647-"))
    anchor = root / "Lk"
    (anchor / "Lk Track" / "Lk Backlog").mkdir(parents=True)
    (anchor / ".anchor").write_text("slug: Lk\ntraits: [Container]\n")
    (anchor / "Lk.md").write_text("# Lk\n")
    backlog = anchor / "Lk Track" / "Lk Backlog" / "Lk Backlog.md"
    backlog.write_text("---\ndescription: Lk backlog\n---\n\n# Lk Backlog\n\n## Now\n\n## Next\n\n## Later\n\n## Done\n\n")
    env = dict(os.environ, ANCHOR_VAULT_ROOT=str(root), ANCHOR_LOCK_DIR=str(root / "locks"))

    def mint(i: int):
        payload = f"- **T+ — row {i}** [Ready] — body {i}\n- **Next:** step {i}\n"
        r = subprocess.run([sys.executable, str(STATE), "define", "Lk", "Backlog", "T+"],
                           input=payload, capture_output=True, text=True, env=env)
        m = re.search(r"added (T\d+)", r.stdout)
        return m.group(1) if m else f"FAILED: {r.stderr.strip()[-200:]}"

    with ThreadPoolExecutor(max_workers=N) as ex:
        ids = list(ex.map(mint, range(N)))
    text = backlog.read_text()
    present = [i for i in ids if i.startswith("T") and re.search(rf"\^{i}\b", text)]
    ok = len(set(ids)) == N and len(present) == N
    print(f"minted {ids}")
    print(f"present in backlog: {len(present)}/{N}; distinct: {len(set(ids))}/{N}")
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
