#!/usr/bin/env python3
"""T592 — `state`/`backlog-edit` must not block on a never-EOF stdin pipe.

The bug this pins: an agent harness hands its child an stdin pipe it never
writes to and never closes. `sys.stdin.read()` waits for an EOF that is never
coming, so a `state` call with no `--body` hung until the CALLER's timeout
killed it — twice, ~7 minutes, on 2026-08-22.

The test has to reproduce that exact shape, which means a real subprocess with
`stdin=PIPE` left open. Feeding `b""` and closing is a DIFFERENT case (it EOFs
immediately) and passes even against the broken code, so it proves nothing.
"""
import importlib.util
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
fails = []


def check(ok, label):
    print(f"{'PASS' if ok else 'FAIL'}  {label}")
    if not ok:
        fails.append(label)


CHILD = r'''
import importlib.util, sys
spec = importlib.util.spec_from_file_location("be", %r)
be = importlib.util.module_from_spec(spec); spec.loader.exec_module(be)
sys.stdout.write("BODY[" + be.read_stdin_body() + "]")
''' % str(HERE / "backlog-edit.py")

env = dict(os.environ, STATE_STDIN_TIMEOUT="0.4")

# 1. The regression itself — pipe open, nothing written, NEVER CLOSED.
#    `communicate()` cannot express this: with no input it closes the child's
#    stdin at once, which EOFs immediately and passes against the broken code
#    too. So the handle is held open deliberately and the child is waited on.
t0 = time.time()
p = subprocess.Popen([sys.executable, "-c", CHILD], stdin=subprocess.PIPE,
                     stdout=subprocess.PIPE, env=env)
held = p.stdin                      # kept referenced so nothing closes it
try:
    p.wait(timeout=15)
    elapsed = time.time() - t0
    out = p.stdout.read()
    check(True, f"never-EOF pipe returns instead of hanging ({elapsed:.1f}s)")
    check(out == b"BODY[]", f"an idle pipe reads as no body (got {out!r})")
    check(elapsed >= 0.3,
          f"it exited via the idle timeout, not an early EOF ({elapsed:.2f}s)")
except subprocess.TimeoutExpired:
    p.kill(); p.wait()
    check(False, "never-EOF pipe returns instead of hanging — STILL HANGS")
finally:
    held.close(); p.stdout.close()

# 2. A real piped body still arrives whole.
p = subprocess.Popen([sys.executable, "-c", CHILD], stdin=subprocess.PIPE,
                     stdout=subprocess.PIPE, env=env)
out, _ = p.communicate(input=b"- **Next:** ship it\n", timeout=15)
check(out == b"BODY[- **Next:** ship it\n]", f"a piped body is read whole (got {out!r})")

# 3. A slow producer is not truncated: two writes straddling the idle window.
p = subprocess.Popen([sys.executable, "-c", CHILD], stdin=subprocess.PIPE,
                     stdout=subprocess.PIPE, env=env)
p.stdin.write(b"first\n"); p.stdin.flush()
time.sleep(0.25)
p.stdin.write(b"second\n"); p.stdin.flush()
p.stdin.close()
out = p.stdout.read(); p.wait(timeout=15)
check(out == b"BODY[first\nsecond\n]", f"a slow producer is not truncated (got {out!r})")

# 4. Single source of truth — `state` delegates rather than carrying its own copy.
state_src = (HERE / "state").read_text()
check("be.read_stdin_body()" in state_src,
      "state.read_body delegates to backlog_edit.read_stdin_body")
check("sys.stdin.read()" not in state_src,
      "state carries no second copy of the raw blocking read")

print()
print(f"{'FAILED' if fails else 'OK'} — {len(fails)} failure(s)")
sys.exit(1 if fails else 0)
