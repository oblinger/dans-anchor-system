#!/usr/bin/env python3
"""Print the ob_check agent-kind checks that are DUE — one per line, tab-separated
topic and doc path. Silence means nothing is due, which is a real answer.

Daybreak's Doctor step launches one background subagent per line printed here,
whose entire brief is "read this doc and do what it says". The registry is the
only source of truth: never hard-code a topic into the skill, or the next agent
check added will be registered and silently never run — the exact defect that
left daily.log.review stale for sixteen days (LUMEN F035).
"""
import datetime
import json
import re
import subprocess
import sys

UNITS = {"s": 1, "m": 60, "h": 3600, "d": 86400}

# Daybreak is the only invoker of agent checks, and it runs once a morning.
# So the question is NOT "is this check stale yet?" but "will it be stale
# before I next get a chance to run it?" — subtract one invocation interval
# from the threshold. Getting this wrong is not a near-miss: with max_age=26h
# and a naive `age >= max_age` gate, a daily run finds the check 24h old,
# skips it, and the check goes stale two hours later. It would then alternate
# fresh/stale every other day forever, which reads as a flaky instrument
# rather than a scheduling bug. Found 2026-08-26 on the first morning the
# wiring ran, before it had produced a single wrong report.
INVOCATION_INTERVAL = 24 * 3600


def max_age_seconds(spec):
    m = re.fullmatch(r"(\d+)([smhd])", spec.strip())
    if not m:
        raise ValueError(f"unparseable max_age: {spec!r}")
    return int(m.group(1)) * UNITS[m.group(2)]


def main():
    try:
        raw = subprocess.run(
            ["ob_check", "checks", "--json"],
            capture_output=True, text=True, check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        # Unreachable is a spoken failure, never a skipped step.
        print(f"agent-checks-due: ob_check unreachable — {exc}", file=sys.stderr)
        return 2

    now = datetime.datetime.now(datetime.timezone.utc)
    for check in json.loads(raw):
        if check.get("kind") != "agent":
            continue
        doc = check.get("doc_path")
        if not doc:
            print(f"agent-checks-due: {check['topic']} has no doc_path", file=sys.stderr)
            continue
        last_seen = check.get("last_seen")
        if last_seen:
            age = (now - datetime.datetime.fromisoformat(last_seen)).total_seconds()
            # Run it if it would go stale before tomorrow's run, not merely if
            # it is stale now — see INVOCATION_INTERVAL above.
            if age + INVOCATION_INTERVAL < max_age_seconds(check["max_age"]):
                continue  # will still be inside its window at the next run
        print(f"{check['topic']}\t{doc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
