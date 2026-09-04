#!/usr/bin/env python3
"""F660 — `pin` rewrites the Pin row of an agent's spine. Run: python3 test-f660-pin.py"""
import json, os, subprocess, sys, tempfile
from pathlib import Path

PIN = Path(__file__).resolve().parent / "pin"
MAST = """---
description: fixture
---

| -[[Ag]]- | : the agent.<br>→ [[kmr]] → [Ag](hook://p/Ag)  |
| --- | --- |
| **Identity** | [[Ag Persona\\|Persona]],  [[Ag Mandate\\|Mandate]],   |
| [[Ag Track\\|Track]]+ | [[Ag Backlog\\|Backlog]],   |
| ... |  |
| [[Ag Stray]] | a stray child |

# Ag
The agent.
"""


def main():
    root = Path(tempfile.mkdtemp(prefix="f660-"))
    ag = root / "Ag"; ag.mkdir(); (ag / ".anchor").write_text("slug: AG\n")
    page = ag / "Ag.md"; page.write_text(MAST)
    leaf = root / "Leaf"; leaf.mkdir(); (leaf / ".anchor").write_text("")
    (leaf / "Leaf.md").write_text(":>> [[kmr]] → Leaf\n\n# Leaf\nA leaf.\n")
    for n in ("Report", "Draft", "A very long document title that will not fit"):
        (root / f"{n}.md").write_text(f"# {n}\n")
    fake_bin = root / "bin"; fake_bin.mkdir()
    ha = fake_bin / "ha"
    ha.write_text("#!/usr/bin/env python3\nimport json,sys\nm=json.load(open(%r))\n"
                  "n=sys.argv[2]\nprint(m[n]) if n in m else sys.exit(2)\n" % str(root / "map.json"))
    ha.chmod(0o755)
    (fake_bin / "open").write_text("#!/bin/sh\necho \"$1\" >> %s\n" % (root / "opened.log")); (fake_bin / "open").chmod(0o755)
    (root / "map.json").write_text(json.dumps({
        "Ag": str(page), "Report": str(root / "Report.md"), "Draft": str(root / "Draft.md"),
        "A very long document title that will not fit": str(root / "A very long document title that will not fit.md"),
        "Leaf": str(leaf / "Leaf.md")}))
    env = dict(os.environ, PIN_HA=str(ha), PATH=f"{fake_bin}:{os.environ['PATH']}", HOME=str(root))

    def run(*args):
        return subprocess.run([sys.executable, str(PIN), *args], capture_output=True, text=True, env=env)

    def lines(): return page.read_text().split("\n")
    def pin_rows(): return [l for l in lines() if l.startswith("| **Pin** |")]
    c = {}
    r = run("Ag", "[[Report|the report]]", "Draft")
    c["create rc0"] = r.returncode == 0
    c["create: first body row, pipe escaped"] = lines()[6] == "| **Pin** | [[Report\\|the report]],  [[Draft]] |"
    c["create: Identity row still next"] = lines()[7].startswith("| **Identity** |")
    c["create: stdout shows display count"] = "the report, Draft  (17/60)" in r.stdout
    r = run("Ag", "Draft")
    c["replace: one Pin row, new content"] = pin_rows() == ["| **Pin** | [[Draft]] |"]
    r = run("Ag", "[[A very long document title that will not fit]]", "--max", "20")
    c["over budget: rc1 names count"] = r.returncode == 1 and f"displays {len('A very long document title that will not fit')} characters, budget 20" in r.stderr
    c["over budget: unchanged"] = pin_rows() == ["| **Pin** | [[Draft]] |"]
    r = run("Ag", "Nope")
    c["dead link: rc1 unchanged"] = r.returncode == 1 and "does not resolve" in r.stderr and pin_rows() == ["| **Pin** | [[Draft]] |"]
    r = run("Ag", "Report", "--dry-run")
    c["dry-run: prints row, unchanged"] = r.stdout.strip() == "| **Pin** | [[Report]] |" and pin_rows() == ["| **Pin** | [[Draft]] |"]
    r = run("Ag", "Report", "--glance")
    c["glance: opened the file"] = (root / "opened.log").read_text().strip() == str(root / "Report.md")
    r = run("Ag")
    c["clear: row removed, rest intact"] = r.returncode == 0 and pin_rows() == [] and page.read_text() == MAST
    r = run("Ag")
    c["clear twice: rc0 says nothing to clear"] = r.returncode == 0 and "nothing to clear" in r.stdout
    r = run("Leaf", "Report")
    c["no spine: rc1 cites DAS spine"] = r.returncode == 1 and "DAS spine" in r.stderr and "breadcrumb" in r.stderr
    r = run("Ghost", "Report")
    c["unknown anchor: rc1"] = r.returncode == 1 and "knows no such anchor" in r.stderr
    r = run(str(ag), "Report")
    c["anchor by path"] = r.returncode == 0 and pin_rows() == ["| **Pin** | [[Report]] |"]
    for k, v in c.items():
        print(("ok   " if v else "FAIL ") + k)
    ok = all(c.values()); print("PASS" if ok else "FAIL"); return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
