#!/usr/bin/env python3
"""F306 — crank must EMIT the canonical TRIAGE line, not be told to echo it.

`skills/crank/SKILL.md` line 243 says *"echo that line verbatim as the last line
of the final message"* and **nothing checks that it did**. Lumen, 2026-08-05:
a correct crank, a substantive report — a stale `[Blocked]` diagnosed and
cleared, a cascading dependency unwound, three doc corrections — and no TRIAGE
line. Per [[feedback_structural_gate_over_behavioral_rule]] this recurs until it
is made structural, and a second sentence in the skill would not fix it: the
existing one is already emphatic and already bolded. The line is the *least*
interesting thing in a good report, which is why it is the first thing to fall
off the end of one.

The chokepoint already exists. `warden_hook` runs at every Stop, resolves the
anchor, and already loads the final assistant message for the F275 chat-ask
gate — so this is a deterministic string comparison over text in hand.

Design points this suite pins:
  D1  compare against what `state triage` EMITS (its stamp's `line`), never a
      hand-written pattern — T120 is the named prior failure.
  D2  freshness, not just presence — a pasted old line reports numbers that are
      no longer true, which is worse than reporting none.
  D3  crank sentinel only — /land, a plain turn, and a mid-task pause owe nothing.
  D4  warn-only first; enforce on a measured number.

    python3 test-f306-triage-line-gate.py
"""
# T170: several of these scripts are extensionless, so the import machinery
# caches them under a mangled name (`stonecpython-312.pyc`) that was seen
# serving code no longer on disk — a green run vouching for a source it had
# not read. Must precede every load in this file, hence the top.
import sys as _sys; _sys.dont_write_bytecode = True

import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path

HOOK = Path(__file__).parent / "crank-stop-hook.py"
results = []


def check(name, got, want=True):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"\n          got  {got!r}\n          want {want!r}"))


def load(td):
    """A fresh module with every state dir redirected into the sandbox."""
    spec = importlib.util.spec_from_file_location("csh", HOOK)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.TRIAGE_DIR = td / "triage"
    m.GATE_DIR = td / "stopgate"
    m.TRIAGE_LOG = m.GATE_DIR / "triage-line.jsonl"
    m.TRIAGE_CONF = m.GATE_DIR / "triage-line.conf"
    m.CRANK_DIR = td / "crank"
    for d in (m.TRIAGE_DIR, m.GATE_DIR, m.CRANK_DIR):
        d.mkdir(parents=True, exist_ok=True)
    return m


LINE = "TRIAGE — Runnable 8 (+2) · User 4 · Verify 0"

# The shape of what Lumen actually wrote: substantive, accurate, and with no
# TRIAGE line anywhere in it.
LUMEN = (
    "Cleared the stale `[Blocked]` on T014 — the blocker it named closed three "
    "weeks ago, so the edge was pointing at a Done row. That unwound a "
    "dependency chain: T014 → T019 → T022 are all runnable again.\n\n"
    "Also corrected three docs that cited the retired location.\n\n"
    "Everything committed. Every remaining LUMEN row waits on you or on "
    "another anchor — nothing left I can move.")


def stamp(m, slug, line=LINE, backlog=None, sha=None):
    p = m.TRIAGE_DIR / f"{slug}.json"
    p.write_text(json.dumps({
        "ts": "2026-08-05T12:00:00+00:00",
        "line": line,
        "backlog_path": str(backlog) if backlog else "",
        "backlog_sha256": sha or "",
    }))
    return p


def backlog(td, body="# BL\n\n## Now\n"):
    p = td / "X Backlog.md"
    p.write_text(body, encoding="utf-8")
    return p, hashlib.sha256(p.read_bytes()).hexdigest()


_td = tempfile.TemporaryDirectory()
TD = Path(_td.name)


print("The LUMEN case — a good report with no line")

m = load(TD)
bl, sha = backlog(TD)
stamp(m, "LUMEN", backlog=bl, sha=sha)
verdict, reason = m._triage_line_check("LUMEN", LUMEN)
check("a substantive report with no TRIAGE line is caught", verdict, "missing")
check("...and the remediation names the re-run",
      "state triage LUMEN" in (reason or ""))
# "paste the line" alone would be wrong advice: the counts may have moved while
# the agent worked, which is the whole reason the re-run comes first.
check("...and says to re-run BEFORE pasting",
      "Re-run" in (reason or "") and "LAST line" in (reason or ""))

check("the same report WITH the fresh line passes",
      m._triage_line_check("LUMEN", LUMEN + "\n\n" + LINE)[0], "ok")
check("...and produces no block text",
      m._triage_line_check("LUMEN", LUMEN + "\n\n" + LINE)[1], None)


print("\nD1 — the line comes from the producer's stamp, not a pattern")

# The gate must not recognize the line by SHAPE. A message carrying a
# well-formed but DIFFERENT triage line is not this anchor's line.
check("a well-formed line with the wrong counts does not satisfy the gate",
      m._triage_line_check(
          "LUMEN", LUMEN + "\nTRIAGE — Runnable 1 · User 0 · Verify 0")[0],
      "missing")
# ...and a line the producer would never print still passes if the producer
# printed it, because the stamp is the authority. Pin that by stamping an
# arbitrary string: no regex could accept this, and the gate must.
m2 = load(TD)
bl2, sha2 = backlog(TD / "b2" if (TD / "b2").mkdir(exist_ok=True) or True else TD)
stamp(m2, "ODD", line="whatever the producer said", backlog=bl2, sha=sha2)
check("the stamp is the authority on the line's text, not its format",
      m2._triage_line_check("ODD", "report\n\nwhatever the producer said")[0],
      "ok")


print("\nD2 — freshness, not just presence")

m3 = load(TD)
bl3, sha3 = backlog(TD, "# BL\n\n## Now\n\n- **T1 — x** [Ready] — y ^T1\n")
stamp(m3, "STALE", backlog=bl3, sha=sha3)
check("a fresh stamp with the line present passes",
      m3._triage_line_check("STALE", LINE)[0], "ok")
# Mutate the backlog AFTER the stamp — exactly what an agent that keeps working
# past its triage call does.
bl3.write_text(bl3.read_text() + "- **T2 — z** [Ready] — w ^T2\n",
               encoding="utf-8")
verdict, reason = m3._triage_line_check("STALE", LINE)
check("a pasted line over a mutated backlog is caught", verdict, "stale")
check("...and the remediation says the counts are no longer true",
      "no longer true" in (reason or ""))
check("...and names the re-run rather than the paste",
      "Re-run `state triage STALE`" in (reason or ""))


print("\nFail-open — an unreadable stamp never manufactures a block")

m4 = load(TD)
check("no stamp at all is reported, with a runnable remediation",
      m4._triage_line_check("NOSTAMP", "report")[0], "no-stamp")
check("...and that remediation names the first run",
      "has never stamped" in (m4._triage_line_check("NOSTAMP", "report")[1] or ""))
(m4.TRIAGE_DIR / "BROKEN.json").write_text("{not json")
check("a corrupt stamp fails open", m4._triage_line_check("BROKEN", "r"),
      ("unreadable", None))
stamp(m4, "EMPTY", line="")
check("a stamp with no line fails open",
      m4._triage_line_check("EMPTY", "r"), ("unreadable", None))
# A stamp whose backlog has vanished must not be read as stale — that would
# block on a condition the agent cannot fix.
stamp(m4, "GONE", backlog=TD / "no-such-backlog.md", sha="deadbeef")
check("a stamp whose backlog is gone is treated as fresh, not stale",
      m4._triage_line_check("GONE", LINE)[0], "ok")


print("\nD4 — warn-only by default, enforce only when configured")

m5 = load(TD)
check("absent conf → warn", m5._triage_mode(), "warn")
m5.TRIAGE_CONF.write_text("{not json")
check("corrupt conf → warn", m5._triage_mode(), "warn")
m5.TRIAGE_CONF.write_text(json.dumps({"mode": "enforce"}))
check("explicit enforce is honoured", m5._triage_mode(), "enforce")
m5.TRIAGE_CONF.write_text(json.dumps({"mode": "warn"}))
check("explicit warn is honoured", m5._triage_mode(), "warn")

# The measurement D4 promotes on: every crank stop logs a verdict in both modes.
m5._triage_log("LUMEN", "missing", "warn")
m5._triage_log("LUMEN", "ok", "warn")
recs = [json.loads(x) for x in
        m5.TRIAGE_LOG.read_text().strip().splitlines()]
check("every verdict is logged", len(recs), 2)
check("...with the anchor, verdict and mode",
      sorted(recs[0]) == ["anchor", "mode", "ts", "verdict"])
check("...including the passing ones — the rate is the point",
      [r["verdict"] for r in recs], ["missing", "ok"])


print("\nD3 — scope: the gate is wired behind the crank sentinel")

src = HOOK.read_text(encoding="utf-8")
# Structural, because the alternative is standing up a full transcript + anchor
# + state CLI just to observe a branch. What matters is that the call sits
# inside the `crank is not None` arm and that arm is inside the clean-worklist
# branch — a non-crank stop must never reach it.
gate = src.split("if count == 0:", 1)[1].split("return _allow", 1)[0]
check("the check is called only under `if crank is not None`",
      "if crank is not None:" in gate and "_triage_line_check(" in gate)
check("...and it blocks only in enforce mode",
      'mode == "enforce"' in gate)
check("...and logs regardless of mode", "_triage_log(" in gate)
# It must run before the LLM check: a string comparison over text already in
# hand costs nothing, and its remediation is the more specific of the two.
check("...and runs before the LLM stage-2 check",
      gate.index("_triage_line_check(") < gate.index("_llm_ask_check("))


print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
