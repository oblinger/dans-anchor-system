#!/usr/bin/env python3
"""test-t626-stone-push.py — TINK T626: placement. `stone <kind> push` puts one
stone on ANOTHER anchor's list as a deliberate act with a receipt; `recall`
takes it back; `update` keeps an enrolled line where it sweeps a merely
propagated one, and flags a clock nobody is watching.

Fixture: SONAR (owner, no feeds) and SPARKS (the watcher, `accepts: due,
done, importance` — the three parts of ASTR Comms § The handoff contract), plus HUD which `feeds: SONAR` so the feeds-vs-enrollment seam is
exercised. Never touches the real vault.

  A. push            — line lands in the target's control file, the stone
                        gains `enrolled::` + `appears::`, a receipt prints
                        what was pushed and the keys it carries.
  B. refusal         — a stone missing an `accepts:` key is refused by name;
                        nothing is written on either side.
  C. update keeps it — the enrolled line survives `update` (feeds: would have
                        swept it), and a `line::` edit reaches it.
  D. recall          — the line comes off, `enrolled::` is dropped, and the
                        next `update` does not bring it back.
  E. sweep warning   — a live stone with `due::` and no enrollment is named
                        on stderr; silent once pushed.
  F. bad addresses   — unknown target, unknown stone, owner == target.
  G. archive         — archiving the stone withdraws the enrolled line.
  H. idempotent      — a second push says so and changes nothing.
"""
import sys as _sys; _sys.dont_write_bytecode = True
import contextlib, importlib.machinery, importlib.util, io, shutil, sys, tempfile, time
from pathlib import Path

HERE = Path(__file__).parent
_loader = importlib.machinery.SourceFileLoader("stone_mod", str(HERE / "stone"))
_spec = importlib.util.spec_from_loader("stone_mod", _loader)
st = importlib.util.module_from_spec(_spec)
sys.modules["stone_mod"] = st
_loader.exec_module(st)
st._GLOBAL_STONES_CACHE = {}  # hermetic: kind-table mode regardless of user config (F628 step 4)
CFG = st.load_kind_config()["pebble"]

PASS = FAIL = 0
def ok(m):
    global PASS; PASS += 1; print(f"  PASS: {m}")
def no(m):
    global FAIL; FAIL += 1; print(f"  FAIL: {m}")


def mkanchor(root, slug, feeds=(), accepts=()):
    d = root / slug; d.mkdir(parents=True, exist_ok=True)
    txt = f"slug: {slug}\n"
    if feeds: txt += f"feeds: {', '.join(feeds)}\n"
    if accepts: txt += f"accepts: {', '.join(accepts)}\n"
    (d / ".anchor").write_text(txt, encoding="utf-8")
    return d

def control(root, slug): return root / slug / f"{slug} Track" / f"{slug} Pebble.md"
def stone(root, slug, sid): return root / slug / f"{slug} Track" / f"{slug} Pebbles" / f"{slug} {sid}.md"

def run(root, *argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = st.main(["stone", *argv, "--root", str(root)])
    return rc, out.getvalue(), err.getvalue()

def set_key(path, key, val):
    keys, body = st._parse_stone(path.read_text(encoding="utf-8"))
    st._kv_set(keys, key, val)
    path.write_text(st._render_stone(keys, body), encoding="utf-8")

def keys_of(path): return dict(st._parse_stone(path.read_text(encoding="utf-8"))[0])

TMP = Path(tempfile.mkdtemp())
try:
    root = TMP
    mkanchor(root, "SONAR"); mkanchor(root, "SPARKS", accepts=("due", "done", "importance")); mkanchor(root, "HUD", feeds=("SONAR",))
    run(root, "pebble", "new", "SONAR", "--line", "take-home materials due Saturday")
    p7 = stone(root, "SONAR", "P0001")

    # ---- B. refusal first: the stone has no due:: / then:: yet ---------------
    rc, out, err = run(root, "pebble", "push", "SONAR", "P0001", "--to", "SPARKS")
    if rc != 0 and all(f"`{k}::`" in err for k in ("due", "done", "importance")) and "refused" in err:
        ok("B: a stone missing the target's accepts: keys is refused, naming all three")
    else:
        no(f"B: rc={rc} err={err!r}")
    if not control(root, "SPARKS").exists() and "enrolled" not in keys_of(p7):
        ok("B: nothing was written on either side")
    else:
        no("B: the refusal wrote something")
    set_key(p7, "due", "2026-09-02 15:00")
    rc, out, err = run(root, "pebble", "push", "SONAR", "P0001", "--to", "SPARKS")
    if rc != 0 and "`done::`" in err and "`importance::`" in err and "`due::`" not in err.split("--")[0]:
        ok("B: with due:: present only the two still missing are named")
    else:
        no(f"B: partial refusal wrong: {err!r}")

    # ---- E. the sweep warning, before any push ------------------------------
    rc, out, err = run(root, "pebble", "update")
    if "SONAR P0001" in err and "enrolled with nobody" in err and rc == 0:
        ok("E: update names a due:: stone that is enrolled with nobody (and still exits 0)")
    else:
        no(f"E: rc={rc} err={err!r}")

    # ---- A. the push ----------------------------------------------------------
    set_key(p7, "done", "the materials are in the recruiter's inbox")
    set_key(p7, "importance", "high")
    rc, out, err = run(root, "pebble", "push", "SONAR", "P0001", "--to", "SPARKS")
    cp = control(root, "SPARKS")
    if rc == 0 and cp.is_file() and "[[Sonar P0001|SONAR:]] take-home materials due Saturday" in cp.read_text():
        ok("A: the line landed in SPARKS's control file")
    else:
        no(f"A: rc={rc} out={out!r} err={err!r} file={cp.read_text() if cp.is_file() else None!r}")
    if out.startswith("SONAR P0001 -> SPARKS Pebble") and "due:: 2026-09-02 15:00" in out and "importance:: high" in out and "done:: the materials" in out:
        ok("A: the receipt names the stone, the list, and the keys it carries")
    else:
        no(f"A: receipt wrong: {out!r}")
    k = keys_of(p7)
    if k.get("enrolled") == "SPARKS" and "SPARKS" in k.get("appears", ""):
        ok("A: the stone records enrolled:: SPARKS and appears:: SPARKS")
    else:
        no(f"A: keys after push: {k}")

    # ---- H. idempotent ---------------------------------------------------------
    before = cp.read_text()
    rc, out, err = run(root, "pebble", "push", "SONAR", "P0001", "--to", "SPARKS")
    if rc == 0 and "already enrolled" in out and cp.read_text() == before:
        ok("H: a second push says so and changes nothing")
    else:
        no(f"H: rc={rc} out={out!r}")

    # ---- C. update keeps the enrolled line; edits reach it -------------------
    rc, out, err = run(root, "pebble", "update")
    if "SONAR P0001" in cp.read_text():
        ok("C: update keeps the enrolled line (SPARKS has no feeds: from SONAR)")
    else:
        no(f"C: update swept the enrolled line: {cp.read_text()!r}")
    if "enrolled with nobody" not in err:
        ok("E: the sweep warning is silent once the stone is enrolled")
    else:
        no(f"E: warning still fires after push: {err!r}")
    time.sleep(2.1)  # T553: the stone must be demonstrably the newer side
    set_key(p7, "line", "take-home materials due SATURDAY 10:00")
    run(root, "pebble", "update")
    if "due SATURDAY 10:00" in cp.read_text():
        ok("C: a line:: edit on the stone reaches the enrolled copy")
    else:
        no(f"C: edit did not propagate: {cp.read_text()!r}")
    # HUD draws from SONAR by feeds: — the stone is unpublished, so HUD must NOT have it
    hud = control(root, "HUD")
    if not hud.is_file() or "SONAR P0001" not in hud.read_text():
        ok("C: enrollment is not publication — HUD (feeds: SONAR) does not receive it")
    else:
        no("C: enrollment leaked into a feeds: consumer")

    # ---- F. bad addresses ------------------------------------------------------
    rc, _o, err = run(root, "pebble", "push", "SONAR", "P0001", "--to", "NOPE")
    ok("F: unknown target fails and names it") if rc != 0 and "NOPE" in err else no(f"F: {rc} {err!r}")
    rc, _o, err = run(root, "pebble", "push", "SONAR", "P9999", "--to", "SPARKS")
    ok("F: unknown stone fails and names it") if rc != 0 and "P9999" in err else no(f"F: {rc} {err!r}")
    rc, _o, err = run(root, "pebble", "push", "SONAR", "P0001", "--to", "SONAR")
    ok("F: owner == target is refused") if rc != 0 and "own list" in err else no(f"F: {rc} {err!r}")

    # ---- D. recall ---------------------------------------------------------------
    rc, out, err = run(root, "pebble", "recall", "SONAR", "P0001", "--from", "SPARKS")
    if rc == 0 and "SONAR P0001" not in cp.read_text() and "enrolled" not in keys_of(p7):
        ok("D: recall removes the line and drops enrolled::")
    else:
        no(f"D: rc={rc} out={out!r} err={err!r} file={cp.read_text()!r} keys={keys_of(p7)}")
    if out.startswith("SONAR P0001 <- SPARKS Pebble") and "line removed" in out:
        ok("D: recall prints what came off")
    else:
        no(f"D: receipt: {out!r}")
    run(root, "pebble", "update")
    if "SONAR P0001" not in cp.read_text():
        ok("D: the next update does not bring a recalled line back")
    else:
        no("D: update re-added the recalled line")
    rc, _o, err = run(root, "pebble", "recall", "SONAR", "P0001", "--from", "SPARKS")
    ok("D: recalling twice is refused, naming the (empty) enrollment") if rc != 0 and "not enrolled" in err else no(f"D: {rc} {err!r}")

    # ---- G. archive withdraws the watch ---------------------------------------
    run(root, "pebble", "push", "SONAR", "P0001", "--to", "SPARKS")
    own = control(root, "SONAR")
    own.write_text("\n".join(l for l in own.read_text().splitlines() if "P0001" not in l) + "\n", encoding="utf-8")
    rc, out, err = run(root, "pebble", "update")
    if "SONAR P0001" not in cp.read_text() and not p7.exists():
        ok("G: archiving the stone withdraws its enrolled line")
    else:
        no(f"G: archived={not p7.exists()} sparks={cp.read_text()!r}")
finally:
    shutil.rmtree(TMP, ignore_errors=True)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
