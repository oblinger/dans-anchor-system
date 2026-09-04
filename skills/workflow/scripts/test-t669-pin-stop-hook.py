#!/usr/bin/env python3
"""T669 — the pin Stop hook nudges once, only when vault files were written and
pin was not called. Run: python3 test-t669-pin-stop-hook.py"""
import importlib.util, json, os, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("pinhook", HERE / "pin-stop-hook.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

td = Path(tempfile.mkdtemp(prefix="t669-"))
m.GATE_DIR = td / "stopgate"; m.LOG = m.GATE_DIR / "pin-nudge.jsonl"; m.CONF = m.GATE_DIR / "pin-nudge.conf"
VAULT = td / "vault"; (VAULT / "Ag").mkdir(parents=True); (VAULT / "Ag" / ".anchor").write_text("slug: AG\n")
m._vault_root = lambda: str(VAULT.resolve())
results = []


def check(name, got, want=True):
    ok = got == want
    results.append(ok)
    print(("  ok  " if ok else "  FAIL") + " " + name + ("" if ok else f"\n        got:  {got!r}\n        want: {want!r}"))


def entry(kind, blocks):
    return {"type": kind, "message": {"role": kind, "content": blocks}}


def user(text): return entry("user", [{"type": "text", "text": text}])
def result(): return entry("user", [{"type": "tool_result", "content": "ok"}])
def tool(name, **inp): return entry("assistant", [{"type": "tool_use", "name": name, "input": inp}])
def text(t): return entry("assistant", [{"type": "text", "text": t}])


def transcript(*entries):
    p = td / "t.jsonl"
    p.write_text("\n".join(json.dumps(e) for e in entries) + "\n")
    return str(p)


def ev(tp, active=False):
    return {"transcript_path": tp, "cwd": str(VAULT / "Ag"), "session_id": "s1", "stop_hook_active": active}


def logged():
    try:
        return [json.loads(l)["verdict"] for l in m.LOG.read_text().splitlines()]
    except OSError:
        return []


# 1. wrote a vault file, no pin → one block carrying the invocation
tp = transcript(user("do the thing"), tool("Write", file_path=str(VAULT / "Ag" / "Report.md"), content="x"),
                result(), text("done"))
out = m.hook(ev(tp))
check("a vault write with no pin blocks the stop", out.get("decision"), "block")
check("...and the reason names the slug and the file", "AG" in out.get("reason", "") and '"[[Report]]"' in out.get("reason", ""))
check("...and carries the pin script's full path", str(m.PIN) in out.get("reason", ""))
check("...and is logged as nudged", logged(), ["nudged"])

# 2. the second stop of the same turn (harness flag) passes and is logged
out = m.hook(ev(tp, active=True))
check("stop_hook_active → no second block", out, {})
check("...logged as passed-after-nudge", logged()[-1], "passed-after-nudge")

# 3. the turn pinned → silent
tp = transcript(user("do"), tool("Write", file_path=str(VAULT / "Ag" / "Report.md"), content="x"), result(),
                tool("Bash", command=f'"{m.PIN}" AG "[[Report]]"'), result(), text("done"))
check("a write followed by a pin call is silent", m.hook(ev(tp)), {})
check("...and logged as pinned", logged()[-1], "pinned")

# 4. nothing written → silent, nothing logged
n = len(logged())
tp = transcript(user("q?"), tool("Read", file_path=str(VAULT / "Ag" / "Report.md")), result(), text("answer"))
check("a read-only turn is silent", m.hook(ev(tp)), {})
check("...and not logged", len(logged()), n)

# 5. a write OUTSIDE the vault → silent
tp = transcript(user("code"), tool("Edit", file_path=str(td / "repo" / "x.py"), old_string="a", new_string="b"), result())
check("a non-vault write is silent", m.hook(ev(tp)), {})

# 6. writes before the last user prompt do not count
tp = transcript(user("first"), tool("Write", file_path=str(VAULT / "Ag" / "Old.md"), content="x"), result(),
                text("ok"), user("second, just answer"), text("answer"))
check("only the current turn's writes count", m.hook(ev(tp)), {})

# 7. `spin` / `pin-foo` are not pin calls; `…/pin AG` is
check("`spin` is not a pin call", m._PIN_CALL_RE.search("spin AG x") is None)
check("`pin-stop-hook.py` is not a pin call", m._PIN_CALL_RE.search("python3 pin-stop-hook.py") is None)
check("a path-invoked pin is", m._PIN_CALL_RE.search("/x/scripts/pin AG '[[A]]'") is not None)

# 8. log mode: logged, never blocks
m.GATE_DIR.mkdir(exist_ok=True); m.CONF.write_text('{"mode": "log"}')
tp = transcript(user("do"), tool("Write", file_path=str(VAULT / "Ag" / "R.md"), content="x"), result())
check("log mode never blocks", m.hook(ev(tp)), {})
check("...but still records the miss", logged()[-1], "nudged")

# 9. fail-open on garbage
check("a missing transcript is silent", m.warden_hook({"transcript_path": str(td / "nope.jsonl")}), {})
check("an empty event is silent", m.warden_hook({}), {})

print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
