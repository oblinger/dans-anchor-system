#!/usr/bin/env python3
"""TINK F640 — the interactive gate, end to end against the real judge (haiku).

Runs ctrl.py with a fake session, two canned transcripts and a temp config
dir, and asserts exit codes, stderr text, judge-record presence and the
five-minute pass memory. Chrome is never touched: a call that passes the
gate is stopped next by the browser lease (nobody holds it), and that
refusal text is the proof the gate let it through.

Run: python3 ~/.claude/skills/ctrl/tests/live/test-f640-judge.py
"""
import json, os, subprocess, sys, tempfile, time, uuid
from pathlib import Path

CTRL = Path(__file__).resolve().parents[2] / "ctrl.py"
NOW = time.time()
P = F = 0


def ok(label, cond, detail=""):
    global P, F
    if cond:
        P += 1; print(f"  ✓ {label}")
    else:
        F += 1; print(f"  ✗ {label}  {detail}")


def ts(offset_s):
    return time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime(NOW - offset_s))


def user(text, age):
    return {"type": "user", "timestamp": ts(age), "message": {"role": "user", "content": text}}


def call(name, inp, age):
    return {"type": "assistant", "timestamp": ts(age),
            "message": {"role": "assistant", "content": [{"type": "tool_use", "name": name, "input": inp}]}}


def write_transcript(path, lines):
    path.write_text("".join(json.dumps(l) + "\n" for l in lines))


def run(env_extra, *argv, cfg):
    env = {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE")}
    env.update({"CLAUDECODE": "1", "CTRL_CONFIG_DIR": str(cfg), "CTRL_TEST": "1",
                "CTRL_HOSTNAME": "Daniels-MacBook-Pro"})
    env.update(env_extra)
    t0 = time.time()
    r = subprocess.run([sys.executable, str(CTRL), *argv], capture_output=True, text=True, env=env, timeout=60)
    return r, time.time() - t0


def judge_files(cfg):
    d = cfg / "judge"
    return sorted(p.name for p in d.glob("*.json")) if d.is_dir() else []


def main():
    root = Path(tempfile.mkdtemp(prefix="f640-"))
    cfg = root / "ctrl"; cfg.mkdir()
    (cfg / "config.yaml").write_text("interactive_hosts: [Daniels-MacBook-Pro]\n")

    inter = root / "interactive.jsonl"
    write_transcript(inter, [
        user("can you pull up the pricing page for example.com and tell me what the pro tier costs", 40),
        call("Bash", {"command": "ls ~/ob/kmr/SYS"}, 30),
        call("Read", {"file_path": "/Users/oblinger/ob/kmr/SYS/SYS.md"}, 20),
    ])
    crawl = root / "crawl.jsonl"
    write_transcript(crawl, [
        user("build me a table of every YC W25 company with their pricing page, I'll look at it tomorrow", 1900),
        user("ok", 1700),
        *[call("Bash", {"command": f"ctrl cpage https://startup{i}.example/pricing --output /tmp/s{i}.json --yaml"}, 1500 - i * 90)
          for i in range(12)],
    ])
    s_inter = f"f640-{uuid.uuid4()}"
    s_crawl = f"f640-{uuid.uuid4()}"
    url = "https://example.com/pricing"

    print("no flag on an interactive host")
    r, dt = run({"CLAUDE_CODE_SESSION_ID": s_inter}, "cpage", url, cfg=cfg)
    ok("exit 2", r.returncode == 2, r.stderr[-200:])
    ok("names the work + prints the form", "background work on this machine" in r.stderr
       and "bridge tmux dexter" in r.stderr and "ctrl cpage" in r.stderr, r.stderr[-300:])
    ok("under one second", dt < 1.0, f"{dt:.2f}s")
    ok("no judge record", judge_files(cfg) == [])

    print("--bridge prints the form and exits 0")
    r, _ = run({"CLAUDE_CODE_SESSION_ID": s_inter, "BRIDGE_AGENT": "tink"}, "--bridge", "cpage", url,
               "--output", "/tmp/f640.json", "--yaml", cfg=cfg)
    ok("exit 0", r.returncode == 0, r.stderr[-200:])
    ok("send-keys carries the verb + args", "send-keys" in r.stdout and "ctrl cpage https://example.com/pricing --output /tmp/f640.json --yaml" in r.stdout, r.stdout)
    ok("window is the agent's own", "bridge-dexter:agent-tink" in r.stdout, r.stdout)
    ok("scp line for --output", "scp " in r.stdout and "/tmp/f640.json" in r.stdout, r.stdout)
    r, _ = run({"CLAUDE_CODE_SESSION_ID": s_inter}, "--bridge", "box", "ls", cfg=cfg)
    ok("--bridge on a screen verb refuses", r.returncode == 1 and "screen verb" in r.stderr, r.stderr)

    print("--interactive, session whose user is waiting on the page")
    r, dt = run({"CLAUDE_CODE_SESSION_ID": s_inter, "CLAUDE_TRANSCRIPT_PATH": str(inter)},
                "--interactive", "cpage", url, cfg=cfg)
    ok("passed the judge (stopped next by the lease)", "you do not hold it" in r.stderr, r.stderr[-300:])
    ok("judge ran within budget", dt < 20, f"{dt:.1f}s")
    first = judge_files(cfg)
    ok("one judge record", len(first) == 1, str(first))
    ok("last-pass written", (cfg / "judge" / f"last-pass.{s_inter}").is_file())
    if first:
        rec = json.loads((cfg / "judge" / first[0]).read_text())
        ok("record says interactive", rec["verdict"].get("interactive") is True, json.dumps(rec["verdict"]))
        ok("evidence bundle has no agent prose", "PENDING CALL" in rec["evidence_bundle"]
           and "pricing page" in rec["evidence_bundle"], "")

    print("second --interactive inside five minutes")
    r, dt = run({"CLAUDE_CODE_SESSION_ID": s_inter, "CLAUDE_TRANSCRIPT_PATH": str(inter)},
                "--interactive", "cpage", url, cfg=cfg)
    ok("runs without judging", "you do not hold it" in r.stderr and judge_files(cfg) == first, r.stderr[-200:])
    ok("fast", dt < 1.0, f"{dt:.2f}s")

    print("--interactive, session in a crawl loop")
    r, dt = run({"CLAUDE_CODE_SESSION_ID": s_crawl, "CLAUDE_TRANSCRIPT_PATH": str(crawl)},
                "--interactive", "cpage", "https://startup12.example/pricing", cfg=cfg)
    ok("exit 2", r.returncode == 2, r.stderr[-300:])
    ok("failed-judgement message, no form", "did not find this interactive" in r.stderr
       and "send-keys" not in r.stderr, r.stderr[-300:])
    ok("fail not cached", not (cfg / "judge" / f"last-pass.{s_crawl}").exists())
    ok("judge record written", len(judge_files(cfg)) == 2, str(judge_files(cfg)))

    print("--interactive with no transcript")
    r, _ = run({"CLAUDE_CODE_SESSION_ID": f"f640-{uuid.uuid4()}"}, "--interactive", "cpage", url, cfg=cfg)
    ok("refused, names the missing transcript", r.returncode == 2 and "transcript" in r.stderr, r.stderr[-200:])

    print("a host not listed (Dexter)")
    n = len(judge_files(cfg))
    r, _ = run({"CLAUDE_CODE_SESSION_ID": s_crawl, "CTRL_HOSTNAME": "dexter"}, "cpage", url, cfg=cfg)
    ok("no gate — straight to the lease", "you do not hold it" in r.stderr and "background work" not in r.stderr, r.stderr[-200:])
    ok("no judge", len(judge_files(cfg)) == n)

    print(f"\n{P} passed, {F} failed — {'PASS' if not F else 'FAIL'}   ({root})")
    return 0 if not F else 1


if __name__ == "__main__":
    sys.exit(main())
