#!/usr/bin/env bash
# bridge-test.sh — integration test harness for the bridge skill (F151).
# Runs each test in SKA Bridge Testing as PASS / FAIL / SKIP against a live
# remote, addressed by HOSTNAME (link-agnostic — survives TB-unplug / wifi).
#
# Usage: bridge-test.sh [host]   (default: defaults.remote from config.yaml)
#
# Tier-1 tests run mechanically. The e2e identity test (T-e2e-twin-identity)
# is gated on the runtime being present and is invoked separately when ready.

set -u
HOST="${1:-}"
HELP_DIR="$HOME/.claude/skills/bridge"
SSH="ssh -o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
USER_R="oblinger"

PASS=0; FAIL=0; SKIP=0
declare -a RESULTS

rec() { # rec <verdict> <name> <detail>
  RESULTS+=("$1|$2|$3")
  case "$1" in
    PASS) PASS=$((PASS+1));;
    FAIL) FAIL=$((FAIL+1));;
    SKIP) SKIP=$((SKIP+1));;
  esac
  printf '  %-5s %-22s %s\n' "$1" "$2" "$3"
}

# Resolve host from config if not given
if [ -z "$HOST" ]; then
  HOST=$(python3 - <<'PY' 2>/dev/null
import yaml, os
p = os.path.expanduser("~/.config/bridge/config.yaml")
try:
    d = yaml.safe_load(open(p)) or {}
    print(d.get("defaults", {}).get("remote", ""))
except Exception:
    print("")
PY
)
fi
[ -z "$HOST" ] && { echo "No host given and no defaults.remote in config.yaml"; exit 2; }

echo "== bridge-test against $HOST =="

# Reachability gate — everything remote SKIPs if unreachable
REMOTE_UP=no
if $SSH "$USER_R@$HOST" hostname >/dev/null 2>&1; then REMOTE_UP=yes; fi

# ---- Unit (no remote) ----
echo "[Unit]"
# T-manifest-exclude: projects always excluded
if python3 - <<'PY'
import sys, os, yaml
sys.path.insert(0, os.path.expanduser("~/.claude/skills/bridge"))
cfg = yaml.safe_load(open(os.path.expanduser("~/.config/bridge/config.yaml")))
ex = cfg.get("claude_environment", {}).get("claude_home", {}).get("exclude", [])
sys.exit(0 if "projects" in ex else 1)
PY
then rec PASS T-manifest-exclude "projects in exclude set"
else rec FAIL T-manifest-exclude "projects NOT excluded"; fi

# T-cfg-defaults: nested shape readable
if python3 "$HELP_DIR/syncthing-helper.py" defaults >/dev/null 2>&1
then rec PASS T-cfg-defaults "config.yaml parses (nested)"
else rec FAIL T-cfg-defaults "defaults read failed"; fi

# ---- Integration: control ----
echo "[Integration — control]"
if [ "$REMOTE_UP" = yes ]; then
  HN=$($SSH "$USER_R@$HOST" hostname 2>/dev/null)
  [ -n "$HN" ] && rec PASS T-ctl-ssh "key-auth → $HN" || rec FAIL T-ctl-ssh "no hostname returned"
  # F224 — FDA + screen-vision self-test, run INSIDE the canonical mux server
  SC=$("$HELP_DIR/screen-check.sh" "$HOST" 2>/dev/null)
  if echo "$SC" | grep -q "screen-check: PASS"; then
    rec PASS T-ctl-screen "mux server has FDA + screen-vision (screen-check)"
  elif echo "$SC" | grep -q "FAIL  mux"; then
    rec SKIP T-ctl-screen "no canonical mux session yet (Step 5 not done)"
  else
    rec FAIL T-ctl-screen "degraded GUI context — run screen-check.sh $HOST for remediation"
  fi
else
  rec SKIP T-ctl-ssh "remote $HOST unreachable"
  rec SKIP T-ctl-screen "remote unreachable"
fi

# ---- Integration: sync ----
echo "[Integration — sync]"
if [ "$REMOTE_UP" = yes ]; then
  ST=$(python3 "$HELP_DIR/syncthing-helper.py" status --host "$HOST" 2>/dev/null)
  if echo "$ST" | grep -q '"mode": "syncthing"'; then
    rec PASS T-syn-pair "host configured, daemons reachable"
    # forward propagation on the REAL configured folder (read-only check: needBytes 0 = converged)
    if echo "$ST" | grep -q '"needBytes": 0'; then
      rec PASS T-syn-forward "folder converged (needBytes 0)"
    else
      rec SKIP T-syn-forward "folder mid-sync; re-run when idle"
    fi
  else
    rec SKIP T-syn-pair "no syncthing host entry"
    rec SKIP T-syn-forward "no syncthing host entry"
  fi
else
  rec SKIP T-syn-pair "remote unreachable"
  rec SKIP T-syn-forward "remote unreachable"
fi
rec SKIP T-syn-reverse "needs bidirectional throwaway folder (manual)"
rec SKIP T-syn-teardown "destructive on throwaway folder (manual)"
# fastlink (informational)
if ifconfig bridge0 2>/dev/null | grep -q "status: active"; then
  KEY=$(grep -E '<apikey>[^<]+</apikey>' "$HOME/Library/Application Support/Syncthing/config.xml" 2>/dev/null | head -1 | sed -E 's|.*<apikey>([^<]+)</apikey>.*|\1|')
  ADDR=$(curl -sf -H "X-API-Key: $KEY" http://127.0.0.1:8384/rest/system/connections 2>/dev/null | grep -o '169\.254\.[0-9.]*:22000' | head -1)
  [ -n "$ADDR" ] && rec PASS T-syn-fastlink "on TB bridge $ADDR" || rec SKIP T-syn-fastlink "TB up but sync not on it"
else
  rec SKIP T-syn-fastlink "no Thunderbolt bridge (on wifi/LAN)"
fi

# ---- Integration: claude ----
echo "[Integration — claude]"
if [ "$REMOTE_UP" = yes ]; then
  V=$(python3 "$HELP_DIR/claude-provision.py" verify --host "$HOST" 2>/dev/null)
  echo "$V" | grep -q '"twin_ready": true' && rec PASS T-cla-verify "twin_ready: true" || rec FAIL T-cla-verify "twin not ready"
  echo "$V" | grep -q '"transcripts_excluded": true' && rec PASS T-inv-no-transcripts "no transcripts in shared index" || rec FAIL T-inv-no-transcripts "transcript jsonl in shared index!"
  # F159 — memory share + ob-skills config
  echo "$V" | grep -q '"memory_share_recorded": true' && rec PASS T-cla-memory "memory share recorded" || rec SKIP T-cla-memory "memory not shared (off or not yet applied)"
  echo "$V" | grep -q '"ob_skills_present": true' && rec PASS T-cla-obskills "ob-skills config on remote" || rec FAIL T-cla-obskills "ob-skills config missing"
  # runtime gate
  RT=$($SSH "$USER_R@$HOST" 'echo "$(command -v claude),$(command -v node),$([ -f ~/.claude.json ] && echo auth)"' 2>/dev/null)
  if echo "$RT" | grep -q 'claude' && echo "$RT" | grep -q 'auth'; then
    rec PASS T-cla-runtime "claude + node + auth present"
  else
    rec FAIL T-cla-runtime "runtime gap: $RT (env present, runtime absent)"
  fi
else
  rec SKIP T-cla-verify "remote unreachable"
  rec SKIP T-inv-no-transcripts "remote unreachable"
  rec SKIP T-cla-runtime "remote unreachable"
fi

# ---- e2e (gated on runtime) ----
echo "[e2e]"
rec SKIP T-e2e-twin-identity "run separately once T-cla-runtime PASSes"

echo ""
echo "== summary: $PASS pass, $FAIL fail, $SKIP skip =="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
