#!/bin/bash
# EXP Flow helpers for remote experimentation workflow
#
# This file defines shell functions (not standalone scripts).
# It must be sourced before any exp-* function can be called:
#
#   source helpers/exp.sh
#
# Workflow:
#   1. Start a remote instance (vast.ai, etc.)
#   2. source helpers/exp.sh
#   3. exp init <ip:port> -r r1 -l /path/to/project
#   4. exp exe "cmd" 300 -r r1
#
# All commands accept -r/--remote <name> to target a specific remote (default: r1).
# Each remote stores its own local project folder (set at init with -l/--local).
#
# Commands:
#   exp init <ip:port> [-r name] [-l path]  # set up remote + local folder
#   exp init "port root@ip" [-r name]       # vast.ai paste format
#   exp init [-r name]                      # reconnect saved remote
#   exp exe "cmd" [timeout] [-r name]       # full round-trip (push+run+pull)
#   exp push <folder> [-r name]             # rsync experiment folder up
#   exp pull <folder> [-r name]             # rsync results back
#   exp check [lines] [-r name]             # show remote tmux output
#   exp list                                # show all configured remotes
#   exp default [name]                      # show or set default remote

# ── Config ────────────────────────────────────────────────
EXP_CONFIG_DIR="$HOME/.config/exp"
EXP_REMOTE="/workspace"
EXP_LOG="$HOME/.config/exp/exp.log"

# Directory containing this script and exp-watcher.sh (self-relative; portable)
EXP_HELPERS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Logging — every significant action gets logged so we can diagnose issues
_exp-log() {
    mkdir -p "$EXP_CONFIG_DIR"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$EXP_LOG"
}

# SSH helpers (skip host key checks — vast.ai instances are ephemeral)
_EXP_SSH_OPTS=(-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o BatchMode=yes)
_exp-ssh() { ssh "${_EXP_SSH_OPTS[@]}" -p "$EXP_PORT" "root@$EXP_HOST" "$@"; }
_exp-ssh-quick() { timeout 15 ssh "${_EXP_SSH_OPTS[@]}" -o ConnectTimeout=10 -p "$EXP_PORT" "root@$EXP_HOST" "$@"; }

# Tmux wrappers with logging — so we can trace what kills sessions
_exp-tmux-kill() {
    local session="$1"
    local reason="$2"
    _exp-log "TMUX-KILL session='$session' reason='$reason' caller='${FUNCNAME[1]}'"
    tmux kill-session -t "$session" 2>/dev/null
}

_exp-tmux-create() {
    local session="$1"
    local cmd="$2"
    _exp-log "TMUX-CREATE session='$session' caller='${FUNCNAME[1]}'"
    if [ -n "$cmd" ]; then
        tmux new-session -d -s "$session" "$cmd"
    else
        tmux new-session -d -s "$session"
    fi
}

# ── Worker setup ─────────────────────────────────────────

_exp-write-worker-claude-md() {
    # Writes/overwrites CLAUDE.md in the worker's home directory.
    # Always written to ~/.config/exp/workers/<name>/ (where Claude was started),
    # but references EXP_LOCAL (the current project/job folder set by exp zap).
    local remote_name="$1"
    local worker_home="$EXP_CONFIG_DIR/workers/$remote_name"
    local worker_instructions="$HOME/.config/exp/exp-worker.md"

    mkdir -p "$worker_home"
    cat > "$worker_home/CLAUDE.md" <<WORKER_EOF
# Worker — $remote_name

You are a worker on remote **$remote_name**. Use \`-r $remote_name\` for all exp commands.

**Job folder:** $EXP_LOCAL
When given an experiment name, the full path is: $EXP_LOCAL/<experiment_name>/
**Remote Python:** \`$EXP_PYTHON\` (torch $EXP_TORCH_VERSION, CUDA $EXP_CUDA_VERSION)
Use this Python for all remote commands: \`exp exe "cd <experiment> && $EXP_PYTHON code.py" <timeout> -r $remote_name\`

## ⚠️ EVERY TIME you receive a task, your FIRST action MUST be:

1. Read this file: $worker_instructions
2. Read the experiment template: $HOME/.config/exp/exp-template.md

The worker instructions are your complete operating manual. The experiment template defines the format your writeup MUST follow. **Read both fresh every time** — do not rely on memory from previous tasks.

The two most commonly missed steps are:
1. **Verify results were pulled locally** (step 7) — check \`output/\` dir after \`exp exe\`
2. **Complete \`_EXECUTION.md\`** (step 9) — fill in the completion fields in \`output/_EXECUTION.md\`. The health system depends on the \`completed:\` field to detect your task is done.
WORKER_EOF
}


exp-worker() {
    # Usage: exp worker [name] [--host ip:port] [-l path]
    # Creates or updates a combined tmux session with remote view (top) and Claude worker (bottom).
    # Idempotent: safe to call repeatedly. If session exists, refreshes CLAUDE.md and (if --host
    # given) updates the remote and respawns the SSH pane — Claude worker pane is never touched.
    local remote_name=""
    local host_addr=""
    local init_args=()

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --host|-H)
                host_addr="$2"
                shift 2
                ;;
            -f|--force)
                init_args+=("-f")
                shift
                ;;
            -l|--local)
                init_args+=("-l" "$2")
                shift 2
                ;;
            *)
                remote_name="$1"
                shift
                ;;
        esac
    done

    remote_name="${remote_name:-$(_exp-default-name)}"

    # If --host given, init the remote first (always force when updating host)
    if [ -n "$host_addr" ]; then
        exp-init "$host_addr" -r "$remote_name" -f "${init_args[@]}" || return 1
    fi

    _exp-load-remote "$remote_name" || {
        echo ">>> ERROR: Remote '$remote_name' not configured. Run: exp init <ip:port> -r $remote_name"
        echo "    Or: exp worker $remote_name --host <ip:port>"
        return 1
    }

    local session="worker-$remote_name"
    local ssh_cmd="while true; do ssh ${_EXP_SSH_OPTS[*]} -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -p $EXP_PORT root@$EXP_HOST -t 'tmux attach -t watcher-$remote_name'; echo '>>> SSH disconnected. Reconnecting in 3s...'; sleep 3; done"

    # Always refresh the worker CLAUDE.md
    _exp-write-worker-claude-md "$remote_name"

    if tmux has-session -t "$session" 2>/dev/null; then
        # Session exists — refresh top pane if host changed, otherwise just confirm
        if [ -n "$host_addr" ]; then
            echo ">>> [$remote_name] Updating remote view to $EXP_HOST:$EXP_PORT..."
            tmux respawn-pane -t "${session}.{top}" -k "$ssh_cmd"
            _exp-log "WORKER-UPDATE session=$session remote=$remote_name host=$EXP_HOST:$EXP_PORT"
            echo ">>> [$remote_name] Worker updated."
        else
            echo ">>> [$remote_name] Worker '$session' ok."
        fi
        echo ">>>   Attach: tmux attach -t $session"
        return 0
    fi

    echo ">>> [$remote_name] Creating worker session '$session'..."

    # Top pane: SSH to remote watcher (with reconnect loop + keepalive)
    _exp-tmux-create "$session" "$ssh_cmd"

    # Bottom pane: Claude Code worker
    tmux split-window -t "$session" -v
    sleep 1
    local worker_home="$EXP_CONFIG_DIR/workers/$remote_name"
    tmux send-keys -t "${session}.{bottom}" "cd \"$worker_home\" && claude --dangerously-skip-permissions" Enter

    # Give more space to the Claude pane (bottom)
    tmux resize-pane -t "${session}.{top}" -y 12

    _exp-log "WORKER-CREATE session=$session remote=$remote_name"

    echo ">>> [$remote_name] Worker ready: $session"
    echo ">>>   Top pane:    remote watcher"
    echo ">>>   Bottom pane: Claude Code worker"
    echo ">>>   Attach:      tmux attach -t $session"
}


exp-teardown() {
    # Usage: exp teardown [-r name]
    # Full teardown: stop remote command, close watcher, kill local worker tmux session,
    # remove config and task files. This is the only command that tears down the local tmux.
    _exp-parse-remote "$@" || return 1

    local session="worker-$EXP_REMOTE_NAME"

    echo ">>> [$EXP_REMOTE_NAME] Tearing down worker..."

    # Stop any running command on remote
    _exp-ssh-quick "if [ -f $EXP_REMOTE/_pid ]; then kill -TERM -\$(cat $EXP_REMOTE/_pid) 2>/dev/null; fi" 2>/dev/null

    # Close remote watcher
    _exp-ssh-quick "tmux kill-session -t watcher-$EXP_REMOTE_NAME 2>/dev/null" 2>/dev/null
    _exp-ssh-quick "rm -f $EXP_REMOTE/_done $EXP_REMOTE/_run.cmd $EXP_REMOTE/_pid" 2>/dev/null

    # Kill local worker tmux session
    if tmux has-session -t "$session" 2>/dev/null; then
        echo ">>> [$EXP_REMOTE_NAME] Killing tmux session '$session'..."
        tmux kill-session -t "$session" 2>/dev/null
    fi

    # Kill disembodied remote tmux if it exists
    _exp-tmux-kill "remote-$EXP_REMOTE_NAME" "exp-teardown"

    # Remove config and task files
    rm -f "$EXP_CONFIG_DIR/${EXP_REMOTE_NAME}.conf"
    rm -f "$EXP_CONFIG_DIR/${EXP_REMOTE_NAME}.task"
    rm -f "$EXP_CONFIG_DIR/${EXP_REMOTE_NAME}.last-task"

    _exp-log "WORKER-TEARDOWN session=$session remote=$EXP_REMOTE_NAME"

    echo ">>> [$EXP_REMOTE_NAME] Torn down. Config, task files, and tmux session removed."
    echo ">>>   Worker files preserved in: $EXP_LOCAL"
}


# ── Multi-remote helpers ──────────────────────────────────

_exp-default-name() {
    if [ -f "$EXP_CONFIG_DIR/default" ]; then
        cat "$EXP_CONFIG_DIR/default"
    else
        echo "r1"
    fi
}

_exp-set-default() {
    mkdir -p "$EXP_CONFIG_DIR"
    echo "$1" > "$EXP_CONFIG_DIR/default"
}

_exp-save-remote() {
    # Save host/port/local/gpu/python for a named remote
    local name="$1"
    mkdir -p "$EXP_CONFIG_DIR"
    cat > "$EXP_CONFIG_DIR/${name}.conf" <<EOF
EXP_HOST="$EXP_HOST"
EXP_PORT="$EXP_PORT"
EXP_LOCAL="$EXP_LOCAL"
EXP_GPU_NAME="$EXP_GPU_NAME"
EXP_GPU_VRAM="$EXP_GPU_VRAM"
EXP_GPU_COUNT="$EXP_GPU_COUNT"
EXP_PYTHON="$EXP_PYTHON"
EXP_TORCH_VERSION="$EXP_TORCH_VERSION"
EXP_CUDA_VERSION="$EXP_CUDA_VERSION"
EOF
}

_exp-load-remote() {
    # Load a named remote config into EXP_HOST/EXP_PORT/EXP_LOCAL/EXP_REMOTE_NAME.
    # With no argument, loads the default remote.
    # Auto-migrates legacy ~/.exp_remote on first use.
    local name="${1:-$(_exp-default-name)}"
    EXP_REMOTE_NAME="$name"

    local conf="$EXP_CONFIG_DIR/${name}.conf"
    if [ -f "$conf" ]; then
        source "$conf"
        return 0
    fi

    # Legacy migration: if no config exists and ~/.exp_remote does, migrate it to r1
    local legacy="$HOME/.exp_remote"
    if [ -f "$legacy" ] && [ "$name" = "r1" ]; then
        echo ">>> Migrating legacy ~/.exp_remote → $conf"
        mkdir -p "$EXP_CONFIG_DIR"
        source "$legacy"
        EXP_LOCAL="${EXP_LOCAL:-$(pwd)}"
        _exp-save-remote "r1"
        _exp-set-default "r1"
        source "$conf"
        return 0
    fi

    echo ">>> ERROR: No config for remote '$name'. Run: exp init <ip:port> -r $name"
    return 1
}

_exp-parse-remote() {
    # Extract -r/--remote <name> from argument list, load config, store remaining args in _EXP_ARGS.
    # After return: EXP_HOST, EXP_PORT, EXP_LOCAL, EXP_REMOTE_NAME are set.
    _EXP_ARGS=()
    local remote_name=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -r|--remote)
                remote_name="$2"
                shift 2
                ;;
            *)
                _EXP_ARGS+=("$1")
                shift
                ;;
        esac
    done

    if [ -n "$remote_name" ]; then
        _exp-load-remote "$remote_name"
    else
        _exp-load-remote
    fi
}


# ── Check if watcher is running on remote ────────────────

_exp-watcher-alive() {
    # Returns 0 if watcher tmux session exists on remote, 1 otherwise.
    # Requires EXP_HOST/EXP_PORT/EXP_REMOTE_NAME to be set.
    _exp-ssh-quick "tmux has-session -t watcher-$EXP_REMOTE_NAME 2>/dev/null" 2>/dev/null
}


# ── Bootstrap remote environment ─────────────────────────

_exp-bootstrap-remote() {
    # Finds the right Python, installs standard ML packages if missing,
    # and records environment info (EXP_PYTHON, EXP_TORCH_VERSION, EXP_CUDA_VERSION).
    # Safe to run multiple times — skips install if torch is already available.
    # Uses one SSH call for detection, one for install if needed.

    echo ">>> [$EXP_REMOTE_NAME] Checking Python environment..."

    # Detect python and check what's installed
    local env_info
    env_info=$(_exp-ssh-quick "$(cat <<'DETECT'
# Find Python
PY=""
for p in /venv/main/bin/python /usr/bin/python3 python3; do
    if command -v "$p" >/dev/null 2>&1 || [ -x "$p" ]; then
        PY="$p"
        break
    fi
done
if [ -z "$PY" ]; then
    echo "PYTHON=NONE"
    exit 0
fi
echo "PYTHON=$PY"
# Check versions
$PY -c "
import sys
print(f'PYTHON_VERSION={sys.version.split()[0]}')
try:
    import torch
    print(f'TORCH={torch.__version__}')
    print(f'CUDA={torch.version.cuda or \"none\"}')
    print(f'CUDA_AVAIL={torch.cuda.is_available()}')
except ImportError:
    print('TORCH=MISSING')
    print('CUDA=MISSING')
    print('CUDA_AVAIL=false')
try:
    import transformers; print(f'TRANSFORMERS={transformers.__version__}')
except ImportError:
    print('TRANSFORMERS=MISSING')
try:
    import matplotlib; print(f'MATPLOTLIB={matplotlib.__version__}')
except ImportError:
    print('MATPLOTLIB=MISSING')
" 2>/dev/null
DETECT
)" 2>/dev/null)

    if [ -z "$env_info" ]; then
        echo ">>> [$EXP_REMOTE_NAME] WARNING: Could not detect Python environment"
        return 1
    fi

    # Parse results
    local py_path py_version torch_ver cuda_ver needs_install=false
    py_path=$(echo "$env_info" | grep '^PYTHON=' | head -1 | cut -d= -f2)
    py_version=$(echo "$env_info" | grep '^PYTHON_VERSION=' | head -1 | cut -d= -f2)
    torch_ver=$(echo "$env_info" | grep '^TORCH=' | head -1 | cut -d= -f2)
    cuda_ver=$(echo "$env_info" | grep '^CUDA=' | head -1 | cut -d= -f2)

    if [ "$py_path" = "NONE" ]; then
        echo ">>> [$EXP_REMOTE_NAME] WARNING: No Python found on remote"
        return 1
    fi

    echo ">>> [$EXP_REMOTE_NAME] Python: $py_path ($py_version)"

    # Check what's missing
    local missing=()
    [ "$torch_ver" = "MISSING" ] && missing+=("torch")
    local tf_ver=$(echo "$env_info" | grep '^TRANSFORMERS=' | head -1 | cut -d= -f2)
    [ "$tf_ver" = "MISSING" ] && missing+=("transformers")
    local mpl_ver=$(echo "$env_info" | grep '^MATPLOTLIB=' | head -1 | cut -d= -f2)
    [ "$mpl_ver" = "MISSING" ] && missing+=("matplotlib")

    # Standard packages to ensure
    local standard_pkgs="peft accelerate datasets scikit-learn seaborn"

    if [ ${#missing[@]} -gt 0 ]; then
        echo ">>> [$EXP_REMOTE_NAME] Installing: ${missing[*]} $standard_pkgs ..."
        local install_result
        install_result=$(_exp-ssh "$py_path -m pip install -q ${missing[*]} $standard_pkgs 2>&1 | tail -3" 2>/dev/null)
        echo "$install_result" | while read -r line; do
            [ -n "$line" ] && echo ">>>   $line"
        done

        # Re-detect versions after install
        env_info=$(_exp-ssh-quick "$py_path -c \"
import torch, sys
print(f'TORCH={torch.__version__}')
print(f'CUDA={torch.version.cuda or \\\"none\\\"}')
print(f'CUDA_AVAIL={torch.cuda.is_available()}')
\" 2>/dev/null" 2>/dev/null)
        torch_ver=$(echo "$env_info" | grep '^TORCH=' | head -1 | cut -d= -f2)
        cuda_ver=$(echo "$env_info" | grep '^CUDA=' | head -1 | cut -d= -f2)
    else
        echo ">>> [$EXP_REMOTE_NAME] Torch: $torch_ver (CUDA $cuda_ver)"
        # Still ensure secondary packages are present (quick no-op if installed)
        _exp-ssh-quick "$py_path -m pip install -q $standard_pkgs 2>/dev/null" 2>/dev/null &
    fi

    # Save to config
    EXP_PYTHON="$py_path"
    EXP_TORCH_VERSION="${torch_ver:-unknown}"
    EXP_CUDA_VERSION="${cuda_ver:-unknown}"
    _exp-save-remote "$EXP_REMOTE_NAME"

    if [ "$torch_ver" != "MISSING" ] && [ -n "$torch_ver" ]; then
        echo ">>> [$EXP_REMOTE_NAME] Environment ready: torch $torch_ver, CUDA $cuda_ver"
    else
        echo ">>> [$EXP_REMOTE_NAME] WARNING: torch install may have failed"
    fi
}

exp-setup() {
    # Usage: exp setup [-r name]
    # Re-runs environment bootstrap on a remote (find python, install packages).
    _exp-parse-remote "$@" || return 1
    _exp-bootstrap-remote
}


# ── Gather all remote state in one SSH call ──────────────

_exp-gather-remote() {
    # Makes ONE SSH call to gather all monitoring data for a remote.
    # Requires EXP_HOST/EXP_PORT/EXP_REMOTE_NAME to be set.
    # Sets _EXP_GATHER_* variables for callers to read.
    # Returns 0 if SSH succeeded, 1 if SSH failed.

    _EXP_GATHER_SSH=fail
    _EXP_GATHER_WATCHER=unknown
    _EXP_GATHER_PID=""
    _EXP_GATHER_RUNCMD_AGE=""
    _EXP_GATHER_RUNCMD=""
    _EXP_GATHER_DONE=""
    _EXP_GATHER_DISK_FREE=""
    _EXP_GATHER_DISK_PCT=""
    _EXP_GATHER_GPU_UTIL=""
    _EXP_GATHER_GPU_MEM_USED=""
    _EXP_GATHER_GPU_MEM_TOTAL=""
    _EXP_GATHER_GPU_TEMP=""
    _EXP_GATHER_TAIL=""

    local raw
    raw=$(_exp-ssh-quick "
echo '===PID===';       cat $EXP_REMOTE/_pid 2>/dev/null || echo '';
echo '===RUNCMD===';    cat $EXP_REMOTE/_run.cmd 2>/dev/null || echo '';
echo '===RUNCMD_AGE==='; stat -c '%Y' $EXP_REMOTE/_run.cmd 2>/dev/null || echo '';
echo '===DONE===';      cat $EXP_REMOTE/_done 2>/dev/null || echo '';
echo '===DISK===';      df -BG $EXP_REMOTE 2>/dev/null | tail -1;
echo '===GPU===';       nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv,noheader,nounits 2>/dev/null || echo '';
echo '===WATCHER===';   tmux has-session -t watcher-$EXP_REMOTE_NAME 2>/dev/null && echo 'ok' || echo 'down';
echo '===TAIL===';      tmux capture-pane -t watcher-$EXP_REMOTE_NAME -p -S - 2>/dev/null | grep -v '^\$' | tail -8;
echo '===END==='
" 2>/dev/null)

    if [ -z "$raw" ]; then
        return 1
    fi

    _EXP_GATHER_SSH=ok

    # Parse sections
    local section=""
    local tail_lines=""
    while IFS= read -r line; do
        case "$line" in
            '===PID===')      section=pid;      continue ;;
            '===RUNCMD===')   section=runcmd;   continue ;;
            '===RUNCMD_AGE===') section=runcmd_age; continue ;;
            '===DONE===')     section=done;     continue ;;
            '===DISK===')     section=disk;     continue ;;
            '===GPU===')      section=gpu;      continue ;;
            '===WATCHER===')  section=watcher;  continue ;;
            '===TAIL===')     section=tail;     continue ;;
            '===END===')      break ;;
        esac
        case "$section" in
            pid)
                [ -n "$line" ] && _EXP_GATHER_PID="$line"
                ;;
            runcmd)
                [ -n "$line" ] && _EXP_GATHER_RUNCMD="$line"
                ;;
            runcmd_age)
                if [ -n "$line" ]; then
                    local now
                    now=$(date +%s)
                    _EXP_GATHER_RUNCMD_AGE=$(( now - line ))
                fi
                ;;
            done)
                [ -n "$line" ] && _EXP_GATHER_DONE="$line"
                ;;
            disk)
                if [ -n "$line" ]; then
                    # df -BG output: Filesystem 1G-blocks Used Available Use% Mounted
                    _EXP_GATHER_DISK_FREE=$(echo "$line" | awk '{gsub(/G/,"",$4); print $4}')
                    _EXP_GATHER_DISK_PCT=$(echo "$line" | awk '{gsub(/%/,"",$5); print $5}')
                fi
                ;;
            gpu)
                if [ -n "$line" ]; then
                    _EXP_GATHER_GPU_UTIL=$(echo "$line" | cut -d',' -f1 | xargs)
                    _EXP_GATHER_GPU_MEM_USED=$(echo "$line" | cut -d',' -f2 | xargs)
                    _EXP_GATHER_GPU_MEM_TOTAL=$(echo "$line" | cut -d',' -f3 | xargs)
                    _EXP_GATHER_GPU_TEMP=$(echo "$line" | cut -d',' -f4 | xargs)
                fi
                ;;
            watcher)
                [ "$line" = "ok" ] && _EXP_GATHER_WATCHER=ok || _EXP_GATHER_WATCHER=down
                ;;
            tail)
                tail_lines+="$line"$'\n'
                ;;
        esac
    done <<< "$raw"

    _EXP_GATHER_TAIL="${tail_lines%$'\n'}"  # trim trailing newline
    return 0
}


# ── Stop (kill running command on remote) ────────────────

exp-stop() {
    _exp-parse-remote "$@" || return 1

    local pid
    pid=$(_exp-ssh-quick "cat $EXP_REMOTE/_pid 2>/dev/null" 2>/dev/null)
    if [ -z "$pid" ]; then
        echo ">>> [$EXP_REMOTE_NAME] No running command (no _pid file)."
        return 1
    fi

    # The command runs in its own session (setsid), so we can safely
    # kill its entire process group without affecting the watcher.
    _exp-log "STOP killing pid=$pid remote=$EXP_REMOTE_NAME"
    echo ">>> [$EXP_REMOTE_NAME] Killing remote command (pid $pid)..."
    _exp-ssh-quick "kill -- -$pid 2>/dev/null; sleep 0.5; kill -9 -- -$pid 2>/dev/null" 2>/dev/null
    echo ">>> [$EXP_REMOTE_NAME] Stopped."
}


# ── Close (stop watcher on remote) ──────────────────────

exp-close() {
    _exp-parse-remote "$@" || return 1

    echo ">>> [$EXP_REMOTE_NAME] Stopping watcher on remote..."
    _exp-log "REMOTE-TMUX-KILL session='watcher-$EXP_REMOTE_NAME' reason='exp-close'"
    _exp-ssh-quick "tmux kill-session -t watcher-$EXP_REMOTE_NAME 2>/dev/null" 2>/dev/null
    _exp-ssh-quick "rm -f $EXP_REMOTE/_done $EXP_REMOTE/_run.cmd" 2>/dev/null

    echo ">>> [$EXP_REMOTE_NAME] Removing local tmux session..."
    _exp-tmux-kill "remote-$EXP_REMOTE_NAME" "exp-close"

    echo ">>> [$EXP_REMOTE_NAME] Closed."
}


# ── Init (idempotent — safe to call repeatedly) ─────────

exp-init() {
    # Usage: exp-init [<addr>] [-r/--remote name] [-l/--local path] [-f/--force]
    #   exp-init 1.2.3.4:22330 -r r1 -l /path/to/project
    #   exp-init "33354 root@1.2.3.4" --remote r1 --local /path/to/project
    #   exp-init -r r1                     — no-op if already running
    #   exp-init -r r1 -f                  — force: close + re-init
    #
    # Idempotent: if watcher is already running, just updates local path
    # (if -l given) and exits. Use -f to tear down and re-init.

    local args=()
    local remote_name=""
    local local_path=""
    local force=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -r|--remote)
                remote_name="$2"
                shift 2
                ;;
            -l|--local)
                local_path="$2"
                shift 2
                ;;
            -f|--force)
                force=true
                shift
                ;;
            *)
                args+=("$1")
                shift
                ;;
        esac
    done

    # Default remote name
    if [ -z "$remote_name" ]; then
        remote_name="$(_exp-default-name)"
    fi
    EXP_REMOTE_NAME="$remote_name"

    # If a positional address was given, parse it
    local new_host="" new_port=""
    if [ ${#args[@]} -gt 0 ]; then
        local addr="${args[0]}"
        if [[ "$addr" == *:* ]]; then
            new_host="${addr%%:*}"
            new_port="${addr##*:}"
        elif [[ "$addr" =~ ^([0-9]+)\ +root@(.+)$ ]]; then
            new_port="${BASH_REMATCH[1]}"
            new_host="${BASH_REMATCH[2]}"
        else
            echo ">>> ERROR: Expected one of:"
            echo "    exp init ip:port [-r name] [-l path]"
            echo "    exp init \"port root@ip\" [-r name] [-l path]"
            return 1
        fi
    fi

    # Load existing config if it exists
    local have_config=false
    if [ -f "$EXP_CONFIG_DIR/${remote_name}.conf" ]; then
        source "$EXP_CONFIG_DIR/${remote_name}.conf"
        have_config=true
    fi

    # If new address given, check for conflict with existing config
    if [ -n "$new_host" ]; then
        if $have_config && [ "$EXP_HOST" != "$new_host" -o "$EXP_PORT" != "$new_port" ]; then
            if ! $force; then
                echo ">>> ERROR: $remote_name is configured as $EXP_HOST:$EXP_PORT"
                echo "    New address $new_host:$new_port conflicts. Use -f to force."
                return 1
            fi
        fi
        EXP_HOST="$new_host"
        EXP_PORT="$new_port"
        EXP_LOCAL="${local_path:-${EXP_LOCAL:-$EXP_CONFIG_DIR/workers/$remote_name}}"
        _exp-save-remote "$remote_name"
    elif ! $have_config; then
        echo ">>> ERROR: No config for remote '$remote_name'. Run: exp init <ip:port> -r $remote_name"
        return 1
    fi

    # Update local path if -l given (always allowed without force)
    if [ -n "$local_path" ]; then
        EXP_LOCAL="$local_path"
        _exp-save-remote "$remote_name"
        echo ">>> [$remote_name] Updated local: $EXP_LOCAL"
    fi

    # Set as default if no default exists yet
    if [ ! -f "$EXP_CONFIG_DIR/default" ]; then
        _exp-set-default "$remote_name"
        echo ">>> Set default remote: $remote_name"
    fi

    # Check if watcher is already running
    echo ">>> [$remote_name] Verifying connection to $EXP_HOST:$EXP_PORT..."
    local verify
    verify=$(_exp-ssh-quick "echo 'exp-hello-$(date +%s)'" 2>&1)
    if [[ "$verify" != exp-hello-* ]]; then
        echo ">>> ERROR: Could not connect to $EXP_HOST:$EXP_PORT"
        echo "    Got: $verify"
        return 1
    fi
    echo ">>> [$remote_name] Connected."

    if ! $force && _exp-watcher-alive; then
        echo ">>> [$remote_name] Remote already running."
        _exp-write-worker-claude-md "$remote_name"
        echo ">>>   Run 'exp worker $remote_name' to start a worker session."
        return 0
    fi

    # Force: close existing watcher first
    if $force && _exp-watcher-alive; then
        echo ">>> [$remote_name] Force: stopping existing watcher..."
        _exp-log "REMOTE-TMUX-KILL session='watcher-$remote_name' reason='exp-init --force'"
        _exp-ssh-quick "tmux kill-session -t watcher-$remote_name 2>/dev/null" 2>/dev/null
    fi

    # Probe GPU info
    local gpu_csv
    gpu_csv=$(_exp-ssh-quick "nvidia-smi --query-gpu=name,memory.total,count --format=csv,noheader,nounits 2>/dev/null" 2>/dev/null)
    if [ -n "$gpu_csv" ]; then
        EXP_GPU_NAME=$(echo "$gpu_csv" | head -1 | cut -d',' -f1 | xargs)
        EXP_GPU_VRAM=$(echo "$gpu_csv" | head -1 | cut -d',' -f2 | xargs)
        EXP_GPU_COUNT=$(echo "$gpu_csv" | head -1 | cut -d',' -f3 | xargs)
        echo ">>> [$remote_name] GPU: ${EXP_GPU_COUNT}x ${EXP_GPU_NAME} (${EXP_GPU_VRAM} MB)"
        _exp-save-remote "$remote_name"
    else
        EXP_GPU_NAME=""
        EXP_GPU_VRAM=""
        EXP_GPU_COUNT=""
        echo ">>> [$remote_name] No GPU detected (nvidia-smi not found)"
    fi

    # Push watcher to remote
    echo ">>> [$remote_name] Pushing exp-watcher to remote..."
    local helpers_dir="$EXP_HELPERS_DIR"
    rsync -az \
        -e "ssh ${_EXP_SSH_OPTS[*]} -p $EXP_PORT" \
        "$helpers_dir/exp-watcher.sh" "root@$EXP_HOST:$EXP_REMOTE/_exp-watcher.sh"
    _exp-ssh "chmod +x $EXP_REMOTE/_exp-watcher.sh"

    echo ">>> [$remote_name] Starting watcher in remote tmux..."
    # Kill any stale watcher sessions (including legacy 'watcher' from pre-rename era)
    _exp-log "REMOTE-TMUX-KILL session='watcher-$remote_name' reason='exp-init (cleanup before create)'"
    _exp-ssh "tmux kill-session -t watcher 2>/dev/null; tmux kill-session -t watcher-$remote_name 2>/dev/null; tmux new-session -d -s watcher-$remote_name 'EXP_REMOTE_NAME=$remote_name bash $EXP_REMOTE/_exp-watcher.sh'"
    _exp-log "REMOTE-TMUX-CREATE session='watcher-$remote_name'"

    # Bootstrap Python environment (install standard ML packages if missing)
    _exp-bootstrap-remote

    _exp-write-worker-claude-md "$remote_name"

    echo ">>> [$remote_name] Init complete. Remote active at $EXP_HOST:$EXP_PORT"
    echo ">>>   local: $EXP_LOCAL"
    echo ">>>   Run 'exp worker $remote_name' to start a worker session."
}


# ── Push (rsync, differential) ──────────────────────────

exp-push() {
    _exp-parse-remote "$@" || return 1
    local exp="${_EXP_ARGS[0]}"
    if [ ! -d "$EXP_LOCAL/$exp" ]; then
        echo ">>> [$EXP_REMOTE_NAME] ERROR: Local folder not found: $EXP_LOCAL/$exp/"
        echo "    Worker may be writing to a different directory than EXP_LOCAL."
        return 1
    fi
    echo ">>> [$EXP_REMOTE_NAME] Pushing $exp..."
    if ! rsync -az --delete \
        -e "ssh ${_EXP_SSH_OPTS[*]} -p $EXP_PORT" \
        "$EXP_LOCAL/$exp/" "root@$EXP_HOST:$EXP_REMOTE/$exp/"; then
        echo ">>> [$EXP_REMOTE_NAME] ERROR: Push failed (rsync error)."
        return 1
    fi
    echo ">>> [$EXP_REMOTE_NAME] Pushed."
}


# ── Pull (rsync, differential) ──────────────────────────

exp-pull() {
    _exp-parse-remote "$@" || return 1
    local exp="${_EXP_ARGS[0]}"
    echo ">>> [$EXP_REMOTE_NAME] Pulling $exp..."
    mkdir -p "$EXP_LOCAL/$exp"
    rsync -az \
        --include='*/' \
        --include='*.png' --include='*.csv' --include='*.log' \
        --include='*.json' --include='*.pt' --include='*.safetensors' --include='*.npy' \
        --exclude='*' \
        -e "ssh ${_EXP_SSH_OPTS[*]} -p $EXP_PORT" \
        "root@$EXP_HOST:$EXP_REMOTE/$exp/" "$EXP_LOCAL/$exp/"
    echo ">>> [$EXP_REMOTE_NAME] Pulled."
}


# ── Exe (push + trigger + wait + pull) ──────────────────

exp-exe() {
    _exp-parse-remote "$@" || return 1
    local cmd="${_EXP_ARGS[0]}"
    local timeout="${_EXP_ARGS[1]:-300}"
    local remote_tmux="watcher-$EXP_REMOTE_NAME"

    # Ensure watcher is alive on remote; restart if needed
    if ! _exp-watcher-alive; then
        echo ">>> [$EXP_REMOTE_NAME] Watcher not running. Restarting..."
        _exp-log "EXE watcher-dead, restarting remote=$EXP_REMOTE_NAME"
        local helpers_dir="$EXP_HELPERS_DIR"
        rsync -az \
            -e "ssh ${_EXP_SSH_OPTS[*]} -p $EXP_PORT" \
            "$helpers_dir/exp-watcher.sh" "root@$EXP_HOST:$EXP_REMOTE/_exp-watcher.sh"
        _exp-ssh "chmod +x $EXP_REMOTE/_exp-watcher.sh"
        _exp-ssh "tmux kill-session -t $remote_tmux 2>/dev/null; tmux new-session -d -s $remote_tmux 'EXP_REMOTE_NAME=$EXP_REMOTE_NAME bash $EXP_REMOTE/_exp-watcher.sh'"
        sleep 2
        if ! _exp-watcher-alive; then
            echo ">>> [$EXP_REMOTE_NAME] ERROR: Failed to restart watcher."
            return 1
        fi
        echo ">>> [$EXP_REMOTE_NAME] Watcher restarted."
    fi

    # Auto-detect experiment folder from command for push/pull
    local exp=""
    if [[ "$cmd" =~ (Q[0-9]+_[0-9]+[a-z]?_[a-zA-Z0-9_]+) ]] || [[ "$cmd" =~ (D[0-9]+_[a-zA-Z0-9_]+) ]] || [[ "$cmd" =~ ([0-9]{3}[a-z]?_[a-zA-Z0-9_]+) ]]; then
        exp="${BASH_REMATCH[1]}"
        if [ ! -d "$EXP_LOCAL/$exp" ]; then
            echo ">>> [$EXP_REMOTE_NAME] ERROR: Local folder not found: $EXP_LOCAL/$exp/"
            echo "    Worker may be writing to a different directory than EXP_LOCAL ($EXP_LOCAL)."
            return 1
        fi
        echo ">>> [$EXP_REMOTE_NAME] Pushing $exp..."
        if ! rsync -az --delete --exclude='output/' \
            -e "ssh ${_EXP_SSH_OPTS[*]} -p $EXP_PORT" \
            "$EXP_LOCAL/$exp/" "root@$EXP_HOST:$EXP_REMOTE/$exp/"; then
            echo ">>> [$EXP_REMOTE_NAME] ERROR: Push failed (rsync error)."
            return 1
        fi
        echo ">>> [$EXP_REMOTE_NAME] Pushed."
    fi

    _exp-log "EXE cmd='$cmd' timeout=$timeout remote=$EXP_REMOTE_NAME"
    echo ">>> [$EXP_REMOTE_NAME] Triggered: $cmd"
    echo ">>> [$EXP_REMOTE_NAME] Waiting (timeout ${timeout}s)..."

    # Generate a nonce so we can distinguish our _done from a stale one
    local nonce="EXP-$$-$(date +%s)"

    # Write nonce + command to remote via stdin pipe (avoids all shell quoting issues)
    # Format: line 1 = nonce, line 2 = command
    # Write to temp file first, then atomic mv — prevents watcher from reading a
    # partially-written _run.cmd (race: cat > creates empty file before SSH pipe delivers data)
    _exp-ssh-quick "rm -f $EXP_REMOTE/_done $EXP_REMOTE/_run.cmd $EXP_REMOTE/_run.cmd.tmp" 2>/dev/null
    printf '%s\n%s\n' "$nonce" "$cmd" | _exp-ssh "cat > $EXP_REMOTE/_run.cmd.tmp && mv $EXP_REMOTE/_run.cmd.tmp $EXP_REMOTE/_run.cmd"

    # Poll for _done file with simple SSH checks
    local elapsed=0
    local last_dump=0
    local exit_code=""
    local ssh_failures=0
    local max_ssh_failures=5

    while [ $elapsed -lt $timeout ]; do
        sleep 2
        elapsed=$((elapsed + 2))

        # Check if _done exists and read it
        local result
        result=$(_exp-ssh-quick "cat $EXP_REMOTE/_done 2>/dev/null" 2>/dev/null)
        local ssh_rc=$?

        if [ $ssh_rc -ne 0 ] && [ -z "$result" ]; then
            ssh_failures=$((ssh_failures + 1))
            if [ $ssh_failures -ge $max_ssh_failures ]; then
                echo ""
                echo ">>> [$EXP_REMOTE_NAME] ERROR: Remote unreachable ($ssh_failures consecutive SSH failures)"
                _exp-log "EXE remote-unreachable after $ssh_failures SSH failures, elapsed=${elapsed}s nonce=$nonce"
                exit_code=125
                break
            fi
        else
            ssh_failures=0
        fi

        if [ -n "$result" ]; then
            # Check nonce: _done format is "NONCE EXIT_CODE" or legacy "EXIT_CODE"
            if [[ "$result" == "$nonce "* ]]; then
                # Our nonce — extract exit code
                exit_code="${result#$nonce }"
                _exp-ssh-quick "rm -f $EXP_REMOTE/_done" 2>/dev/null
                _exp-log "EXE done exit_code=$exit_code elapsed=${elapsed}s nonce=$nonce"
                break
            elif [[ "$result" == EXP-* ]]; then
                # Stale nonce from a previous run — ignore and clean up
                _exp-log "EXE stale-done nonce-mismatch got='$result' expected='$nonce'"
                _exp-ssh-quick "rm -f $EXP_REMOTE/_done" 2>/dev/null
                # Don't break — keep waiting for our result
            else
                # Legacy format (no nonce) — accept as-is
                exit_code="$result"
                _exp-ssh-quick "rm -f $EXP_REMOTE/_done" 2>/dev/null
                _exp-log "EXE done exit_code=$exit_code elapsed=${elapsed}s (legacy, no nonce)"
                break
            fi
        fi

        # Show progress every 15 seconds
        if [ $((elapsed - last_dump)) -ge 15 ] && [ $elapsed -gt 0 ]; then
            echo ""
            echo ">>> ── progress [$EXP_REMOTE_NAME] (${elapsed}s) ──"
            _exp-ssh-quick "tmux capture-pane -t $remote_tmux -p -S -" 2>/dev/null | grep -v '^$' | tail -15
            echo ">>> ──"
            last_dump=$elapsed
        fi
    done

    # Final tmux dump
    echo ""
    if [ -z "$exit_code" ]; then
        echo ">>> ── remote output [$EXP_REMOTE_NAME] (TIMEOUT) ────────"
        exit_code=124
        _exp-log "EXE timeout after ${timeout}s"
    else
        echo ">>> ── remote output [$EXP_REMOTE_NAME] ──────────────────"
    fi
    _exp-ssh-quick "tmux capture-pane -t $remote_tmux -p -S -" 2>/dev/null | grep -v '^$' | tail -80
    echo ">>> ──────────────────────────────────────────"

    # Pull results
    if [ -n "$exp" ]; then
        echo ">>> [$EXP_REMOTE_NAME] Pulling $exp..."
        mkdir -p "$EXP_LOCAL/$exp"
        rsync -az \
            --include='*/' \
            --include='*.png' --include='*.csv' --include='*.log' \
            --include='*.json' --include='*.pt' --include='*.safetensors' --include='*.npy' \
            --exclude='*' \
            -e "ssh ${_EXP_SSH_OPTS[*]} -p $EXP_PORT" \
            "root@$EXP_HOST:$EXP_REMOTE/$exp/" "$EXP_LOCAL/$exp/"
        echo ">>> [$EXP_REMOTE_NAME] Pulled."
    fi

    if [ $exit_code -eq 125 ]; then
        echo ">>> [$EXP_REMOTE_NAME] ABORTED: remote unreachable"
        return 125
    elif [ $exit_code -eq 124 ]; then
        echo ">>> [$EXP_REMOTE_NAME] TIMEOUT after ${timeout}s"
        return 1
    elif [ $exit_code -eq 0 ]; then
        echo ">>> [$EXP_REMOTE_NAME] Complete (success, ${elapsed}s)"
        return 0
    else
        echo ">>> [$EXP_REMOTE_NAME] Complete (exit $exit_code, ${elapsed}s)"
        return $exit_code
    fi
}


# ── Status (health check for one or all remotes) ─────────

_exp-status-one() {
    # Print status for a single remote using ONE SSH call via _exp-gather-remote.
    # Expects EXP_HOST/EXP_PORT/EXP_REMOTE_NAME set.
    local name="$EXP_REMOTE_NAME"
    local default_name
    default_name=$(_exp-default-name)
    local marker="  "
    [ "$name" = "$default_name" ] && marker="* "

    printf "%s%-4s  %s:%s" "$marker" "$name" "$EXP_HOST" "$EXP_PORT"

    if ! _exp-gather-remote; then
        printf "  SSH:FAIL\n"
        return 1
    fi

    printf "  SSH:ok"
    printf "  Watcher:%s" "$_EXP_GATHER_WATCHER"

    # GPU info
    if [ -n "$_EXP_GATHER_GPU_UTIL" ]; then
        local used_g total_g
        used_g=$(awk "BEGIN {printf \"%.1f\", $_EXP_GATHER_GPU_MEM_USED/1024}")
        total_g=$(awk "BEGIN {printf \"%.1f\", $_EXP_GATHER_GPU_MEM_TOTAL/1024}")
        printf "  GPU:%s%% %s/%sG %sC" "$_EXP_GATHER_GPU_UTIL" "$used_g" "$total_g" "$_EXP_GATHER_GPU_TEMP"
    fi
    printf "\n"

    # Second line: state, disk, worker
    local state="Idle"
    if [ -n "$_EXP_GATHER_PID" ]; then
        state="Running (pid $_EXP_GATHER_PID)"
    elif [ -n "$_EXP_GATHER_DONE" ]; then
        state="Done (exit $_EXP_GATHER_DONE)"
    fi

    local disk_info=""
    if [ -n "$_EXP_GATHER_DISK_FREE" ]; then
        disk_info="Disk:${_EXP_GATHER_DISK_FREE}G free (${_EXP_GATHER_DISK_PCT}%)"
    fi

    local worker_status="none"
    if tmux has-session -t "worker-$name" 2>/dev/null; then
        worker_status="ok"
    fi

    printf "       %s  %s  Worker:%s\n" "$state" "$disk_info" "$worker_status"

    # Third+fourth lines: last 2 lines of watcher tail
    if [ -n "$_EXP_GATHER_TAIL" ]; then
        echo "$_EXP_GATHER_TAIL" | tail -2 | while IFS= read -r line; do
            printf "       | %s\n" "$line"
        done
    fi
}

exp-status() {
    # Usage: exp status [-r name]
    # With -r: show status of one remote. Without: show all.
    local remote_name=""
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -r|--remote) remote_name="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    if [ -n "$remote_name" ]; then
        _exp-load-remote "$remote_name" || return 1
        _exp-status-one
    else
        local found=0
        for conf in "$EXP_CONFIG_DIR"/*.conf; do
            [ -f "$conf" ] || continue
            found=1
            source "$conf"
            EXP_REMOTE_NAME=$(basename "$conf" .conf)
            _exp-status-one
        done
        if [ $found -eq 0 ]; then
            echo "(no remotes configured)"
        fi
    fi
}


# ── Health (comprehensive check with issue detection) ────

_exp-health-one() {
    # Detailed health report for a single remote. Expects EXP_HOST/EXP_PORT/EXP_REMOTE_NAME set.
    # Buffers all output, then prints the whole block in green (healthy/warnings) or red (critical).
    # Critical = SSH down, watcher down, disk <5G, GPU >90C, orphan process.
    # Warnings (low disk, stale _done, etc.) color only the affected line, not the whole block.
    # When _EXP_HEALTH_FIX=true, auto-cleans fixable issues (stale _done, stale _run.cmd).
    local name="$EXP_REMOTE_NAME"
    local issues=0
    local critical=0
    local fixed=0
    local lines=()
    local alerts=()  # critical issue descriptions for alert system

    # Determine project name: from task file, or infer from running command
    local task_file="$EXP_CONFIG_DIR/${name}.task"
    local last_task_file="$EXP_CONFIG_DIR/${name}.last-task"
    local project=""
    local last_project=""
    if [ -f "$task_file" ]; then
        local raw_task
        raw_task=$(cat "$task_file")
        local inferred
        inferred=$(_exp-infer-project "$raw_task")
        if [ -n "$inferred" ]; then
            project="$inferred"
        else
            project="$raw_task"
        fi
    fi
    # If no task file, try to infer from the currently running command
    if [ -z "$project" ] && [ -n "$_EXP_GATHER_RUNCMD" ]; then
        project=$(_exp-infer-project "$_EXP_GATHER_RUNCMD")
    fi
    # Load last project for display when idle
    if [ -z "$project" ] && [ -f "$last_task_file" ]; then
        local raw_last
        raw_last=$(cat "$last_task_file")
        local inferred_last
        inferred_last=$(_exp-infer-project "$raw_last")
        last_project="${inferred_last:-$raw_last}"
    fi
    local has_project=false
    local task_done=false
    local task_done_status=""
    local task_done_summary=""
    [ -n "$project" ] && has_project=true

    # Check if worker task is completed (_EXECUTION.md has a completed: timestamp)
    if $has_project; then
        local exec_file="$EXP_LOCAL/$project/output/_EXECUTION.md"
        # Also check legacy _DELEGATE_DONE
        local legacy_done="$EXP_LOCAL/$project/output/_DELEGATE_DONE"
        if [ -f "$exec_file" ]; then
            local completed_line
            completed_line=$(grep '^completed:' "$exec_file" 2>/dev/null | head -1 | sed 's/^completed: *//')
            if [ -n "$completed_line" ] && [ "$completed_line" != '""' ]; then
                task_done=true
                task_done_status=$(grep '^status:' "$exec_file" 2>/dev/null | head -1 | sed 's/^status: *//')
                task_done_summary=$(grep '^summary:' "$exec_file" 2>/dev/null | head -1 | sed 's/^summary: *//' | sed 's/^"//' | sed 's/"$//')
            fi
        elif [ -f "$legacy_done" ]; then
            task_done=true
            task_done_status=$(grep '^status:' "$legacy_done" 2>/dev/null | head -1 | sed 's/^status: *//')
            task_done_summary=$(grep '^summary:' "$legacy_done" 2>/dev/null | head -1 | sed 's/^summary: *//')
        fi
    fi

    # Header: remote name + project name
    # Active task: black project name (readable, prominent)
    # Done/idle: dark green (fades into background)
    if $has_project && $task_done; then
        local proj_display="$project"
        if [ ${#proj_display} -gt 60 ]; then
            proj_display="${proj_display:0:57}..."
        fi
        lines+=("{HDR}── $name: ✓ {GREEN}$proj_display{/HDR} (${task_done_status:-done}) ──")
    elif $has_project; then
        local proj_display="$project"
        if [ ${#proj_display} -gt 60 ]; then
            proj_display="${proj_display:0:57}..."
        fi
        lines+=("{HDR}── $name: {TASK} {BLACK}$proj_display{/HDR} ──")
    elif [ -n "$last_project" ]; then
        lines+=("{HDR}── $name: {GREEN}no project (last: $last_project){/HDR} ──")
    else
        lines+=("{HDR}── $name: {GREEN}no project{/HDR} ──")
    fi

    # SSH — now includes the IP address
    if [ "$_EXP_GATHER_SSH" = "ok" ]; then
        lines+=("  {OK}   SSH $EXP_HOST:$EXP_PORT")
    else
        lines+=("  {FAIL} SSH $EXP_HOST:$EXP_PORT — unreachable")
        ((issues++)); ((critical++)); alerts+=("$name: SSH unreachable")
        lines+=("  $issues issue(s)")
        lines+=("")
    fi

    if [ "$_EXP_GATHER_SSH" = "ok" ]; then
        # Watcher
        if [ "$_EXP_GATHER_WATCHER" = "ok" ]; then
            lines+=("  {OK}   Watcher running")
        else
            lines+=("  {FAIL} Watcher DOWN")
            ((issues++)); ((critical++)); alerts+=("$name: watcher down")
        fi

        # GPU — flag low utilization only if there's an active task
        if [ -n "$_EXP_GATHER_GPU_TEMP" ]; then
            local temp="$_EXP_GATHER_GPU_TEMP"
            local util="$_EXP_GATHER_GPU_UTIL"
            local used_g total_g
            used_g=$(awk "BEGIN {printf \"%.1f\", $_EXP_GATHER_GPU_MEM_USED/1024}")
            total_g=$(awk "BEGIN {printf \"%.1f\", $_EXP_GATHER_GPU_MEM_TOTAL/1024}")
            local gpu_text="GPU: ${util}% util, ${used_g}/${total_g}G mem, ${temp}C"

            if [ "$temp" -ge 90 ] 2>/dev/null; then
                lines+=("  {FAIL} $gpu_text (critical >90C)")
                ((issues++)); ((critical++)); alerts+=("$name: GPU ${temp}C critical")
            elif [ "$temp" -ge 85 ] 2>/dev/null; then
                lines+=("  {WARN} $gpu_text (high >85C)")
                ((issues++))
            elif [ -n "$_EXP_GATHER_PID" ] && [ "$util" -lt 30 ] 2>/dev/null; then
                lines+=("  {WARN} $gpu_text (low — command running)")
                ((issues++))
            else
                lines+=("  {OK}   $gpu_text")
            fi
        else
            lines+=("  {WARN} GPU: no data (nvidia-smi failed)")
            ((issues++))
        fi

        # Disk space
        if [ -n "$_EXP_GATHER_DISK_FREE" ]; then
            local free="$_EXP_GATHER_DISK_FREE"
            if [ "$free" -lt 5 ] 2>/dev/null; then
                lines+=("  {FAIL} Disk: ${free}G free (critical <5G)")
                ((issues++)); ((critical++)); alerts+=("$name: disk ${free}G critical")
            elif [ "$free" -lt 10 ] 2>/dev/null; then
                lines+=("  {WARN} Disk: ${free}G free (low <10G)")
                ((issues++))
            else
                lines+=("  {OK}   Disk: ${free}G free (${_EXP_GATHER_DISK_PCT}% used)")
            fi
        fi

        # Running state — show the actual command if available
        if [ -n "$_EXP_GATHER_PID" ]; then
            local cmd_info="pid $_EXP_GATHER_PID"
            if [ -n "$_EXP_GATHER_RUNCMD" ]; then
                local cmd_short="$_EXP_GATHER_RUNCMD"
                [ ${#cmd_short} -gt 60 ] && cmd_short="${cmd_short:0:57}..."
                cmd_info="$cmd_short (pid $_EXP_GATHER_PID)"
            fi
            if [ "$_EXP_GATHER_WATCHER" = "ok" ]; then
                lines+=("  {OK}   Running: $cmd_info")
            else
                lines+=("  {WARN} Orphan process: $cmd_info (watcher down!)")
                ((issues++)); ((critical++)); alerts+=("$name: orphan process, watcher down")
            fi
        else
            if $has_project && ! $task_done; then
                lines+=("  {WARN} Remote idle (worker may be preparing/reviewing)")
                ((issues++))
            else
                lines+=("  {OK}   No command running")
            fi
        fi

        # Stale _run.cmd
        if [ -n "$_EXP_GATHER_RUNCMD_AGE" ]; then
            if [ "$_EXP_GATHER_RUNCMD_AGE" -gt 30 ] 2>/dev/null; then
                if [ "${_EXP_HEALTH_FIX:-}" = "true" ]; then
                    _exp-ssh-quick "rm -f $EXP_REMOTE/_run.cmd" 2>/dev/null
                    lines+=("  {FIX}  Removed stale _run.cmd (was ${_EXP_GATHER_RUNCMD_AGE}s old)")
                    ((fixed++))
                else
                    lines+=("  {WARN} Stale _run.cmd: ${_EXP_GATHER_RUNCMD_AGE}s old (watcher not consuming)")
                    ((issues++))
                fi
            fi
        fi

        # Unconsumed _done — show nonce if present (stale from aborted run)
        if [ -n "$_EXP_GATHER_DONE" ]; then
            if [ "${_EXP_HEALTH_FIX:-}" = "true" ]; then
                _exp-ssh-quick "rm -f $EXP_REMOTE/_done" 2>/dev/null
                if [[ "$_EXP_GATHER_DONE" == EXP-* ]]; then
                    local stale_code="${_EXP_GATHER_DONE##* }"
                    lines+=("  {FIX}  Removed stale _done (exit $stale_code, from aborted run)")
                else
                    lines+=("  {FIX}  Removed unconsumed _done (exit code: $_EXP_GATHER_DONE)")
                fi
                ((fixed++))
            else
                if [[ "$_EXP_GATHER_DONE" == EXP-* ]]; then
                    local stale_code="${_EXP_GATHER_DONE##* }"
                    lines+=("  {WARN} Stale _done (exit $stale_code, from aborted run)")
                else
                    lines+=("  {WARN} Unconsumed _done (exit code: $_EXP_GATHER_DONE)")
                fi
                ((issues++))
            fi
        fi

        # Local worker session
        if tmux has-session -t "worker-$name" 2>/dev/null; then
            lines+=("  {OK}   Worker session: worker-$name")
        else
            lines+=("  {DIM}  No local worker session")
        fi

        # Task completion summary
        if $task_done; then
            if [ -n "$task_done_summary" ]; then
                lines+=("  {OK}   Task done: $task_done_summary")
            else
                lines+=("  {OK}   Task done (${task_done_status:-complete})")
            fi
        fi

        # Last activity from log
        local last_log
        last_log=$(grep "\[$name\]\|remote=$name" "$EXP_LOG" 2>/dev/null | tail -1)
        if [ -n "$last_log" ]; then
            local timestamp
            timestamp=$(echo "$last_log" | grep -o '^\[[^]]*\]' | tr -d '[]')
            lines+=("         Last log: $timestamp")
        fi

        if [ $fixed -gt 0 ] && [ $issues -eq 0 ]; then
            lines+=("  ✓ Fixed $fixed issue(s)")
        elif [ $fixed -gt 0 ]; then
            lines+=("  ✓ Fixed $fixed, $issues remaining")
        elif [ $issues -eq 0 ]; then
            lines+=("  ✓ Healthy")
        elif [ $critical -eq 0 ]; then
            lines+=("  ✓ OK ($issues warning(s))")
        else
            lines+=("  ▲ $critical critical, $((issues - critical)) warning(s)")
        fi
    fi

    lines+=("")

    # Now print everything with the right base color
    local R=$'\033[0m'
    local BOLD=$'\033[1m'
    local GREEN=$'\033[32m'
    local BGREEN=$'\033[1;32m'
    local RED=$'\033[91m'
    local BRED=$'\033[1;91m'
    local BLACK=$'\033[1;30m'  # bold black — readable on white backgrounds

    local CYAN=$'\033[36m'
    local BCYAN=$'\033[1;36m'
    local base ok_tag warn_tag fail_tag fix_tag task_tag bold_on bold_off
    if [ $critical -gt 0 ]; then
        # Critical issues: whole block red
        base="$RED"
        ok_tag="${BGREEN}[ok]${R}${RED}"
        warn_tag="${BLACK}[WARN]"
        fail_tag="${BRED}[FAIL]${R}${RED}"
        fix_tag="${BCYAN}[fix]${R}${RED}"
        bold_on="${BOLD}"
        bold_off="${R}${RED}"
    else
        # Healthy or warnings only: block green, warning lines get yellow tag
        base="$GREEN"
        ok_tag="${BGREEN}[ok]${R}${GREEN}"
        warn_tag="${BLACK}[WARN]"
        fail_tag="${BRED}[FAIL]${R}${GREEN}"
        fix_tag="${BCYAN}[fix]${R}${GREEN}"
        bold_on="${BOLD}"
        bold_off="${R}${GREEN}"
    fi
    # Task tag: green arrow if active project, black if none
    if $has_project; then
        task_tag="${GREEN}▶${R}${base}"
    else
        task_tag="${BLACK} ${R}${base}"
    fi

    for line in "${lines[@]}"; do
        # Header lines render in bold (not base color)
        local line_base="$base"
        if [[ "$line" == "{HDR}"* ]]; then
            line="${line#\{HDR\}}"
            line="${line//\{\/HDR\}/${R}}"
            line="${line//\{BOLD\}/${R}${BOLD}}"
            line="${line//\{BLACK\}/${R}${BLACK}}"
            line="${line//\{GREEN\}/${R}${GREEN}}"
            line="${line//\{TASK\}/$task_tag}"
            line="${line//\{DIM\}/${BLACK}}"
            printf "%s%s%s\n" "" "$line" "$R"
            continue
        fi
        # Replace markers with colored tags
        line="${line//\{OK\}/$ok_tag}"
        line="${line//\{WARN\}/$warn_tag}"
        line="${line//\{FAIL\}/$fail_tag}"
        line="${line//\{FIX\}/$fix_tag}"
        line="${line//\{TASK\}/$task_tag}"
        line="${line//\{BOLD\}/$bold_on}"
        line="${line//\{\/BOLD\}/$bold_off}"
        line="${line//\{DIM\}/${BLACK}}"
        printf "%s%s%s\n" "$base" "$line" "$R"
    done

    # Export critical alerts for the alert system
    if [ ${#alerts[@]} -gt 0 ]; then
        for a in "${alerts[@]}"; do
            _EXP_HEALTH_SUMMARY="${_EXP_HEALTH_SUMMARY:+$_EXP_HEALTH_SUMMARY; }$a"
        done
    fi

    return $critical
}

_exp-health-run() {
    # Inner function: run one health report pass. Args: [remote_name]
    # Sets _EXP_HEALTH_SUMMARY (text) for callers (e.g. alert system).
    local remote_name="$1"
    _EXP_HEALTH_SUMMARY=""

    local R=$'\033[0m'
    local BOLD=$'\033[1m'
    local BOK=$'\033[1;32m'
    local BFAIL=$'\033[1;91m'

    echo "${BOLD}=== EXP Health Report ===  $(date '+%H:%M:%S')${R}"
    echo ""

    local total_critical=0
    local total_remotes=0

    if [ -n "$remote_name" ]; then
        _exp-load-remote "$remote_name" || return 1
        _exp-gather-remote
        total_remotes=1
        _exp-health-one
        total_critical=$?
    else
        for conf in "$EXP_CONFIG_DIR"/*.conf; do
            [ -f "$conf" ] || continue
            source "$conf"
            EXP_REMOTE_NAME=$(basename "$conf" .conf)
            ((total_remotes++))
            _exp-gather-remote
            _exp-health-one
            total_critical=$((total_critical + $?))
        done
    fi

    if [ $total_remotes -eq 0 ]; then
        echo "(no remotes configured)"
        return 0
    fi

    echo "${BOLD}=== Summary ===${R}"
    if [ $total_critical -eq 0 ]; then
        echo "${BOK}✓ All $total_remotes remote(s) operational.${R}"
    else
        echo "${BFAIL}▲ $total_critical critical issue(s) across $total_remotes remote(s).${R}"
    fi
}

exp-health() {
    # Usage: exp health [-r name] [-w [secs]] [--fix] [--alert <tmux-target>]
    # Comprehensive health report. -w enables watch mode (default 30s, Ctrl-C to stop).
    # --fix auto-cleans fixable issues (stale _done, stale _run.cmd).
    # --alert <target> sends a message to the specified tmux pane when critical issues
    #   are detected (requires -w). Only alerts on NEW issues, not repeated ones.
    #   Target is a tmux pane identifier (e.g., %14, session:0.1).
    local remote_name=""
    local watch=false
    local interval=30
    local alert_target=""
    _EXP_HEALTH_FIX=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -r|--remote) remote_name="$2"; shift 2 ;;
            --fix) _EXP_HEALTH_FIX=true; shift ;;
            --alert)
                alert_target="$2"; shift 2
                ;;
            -w|--watch)
                watch=true
                shift
                # If next arg is a number, use it as interval
                if [[ "${1:-}" =~ ^[0-9]+$ ]]; then
                    interval="$1"
                    shift
                fi
                ;;
            *) shift ;;
        esac
    done

    if $watch; then
        local last_alert_summary=""
        trap 'echo ""; echo "Stopped."; return 0' INT
        while true; do
            clear
            _exp-health-run "$remote_name"
            echo ""

            # Alert system: send to tmux target if critical issues changed
            if [ -n "$alert_target" ]; then
                if [ -n "$_EXP_HEALTH_SUMMARY" ] && [ "$_EXP_HEALTH_SUMMARY" != "$last_alert_summary" ]; then
                    local alert_msg="[EXP ALERT] Critical: $_EXP_HEALTH_SUMMARY — run 'exp health' to investigate"
                    tmux send-keys -t "$alert_target" "$alert_msg" Enter 2>/dev/null
                    last_alert_summary="$_EXP_HEALTH_SUMMARY"
                    _exp-log "ALERT sent to $alert_target: $_EXP_HEALTH_SUMMARY"
                    echo "(⚡ alert sent to $alert_target)"
                elif [ -z "$_EXP_HEALTH_SUMMARY" ] && [ -n "$last_alert_summary" ]; then
                    # Issues resolved — notify and reset
                    tmux send-keys -t "$alert_target" "[EXP ALERT] All clear — critical issues resolved" Enter 2>/dev/null
                    last_alert_summary=""
                    _exp-log "ALERT cleared, sent to $alert_target"
                    echo "(⚡ all-clear sent to $alert_target)"
                fi
                echo "(alerting $alert_target on critical issues — refreshing every ${interval}s — Ctrl-C to stop)"
            else
                echo "(refreshing every ${interval}s — Ctrl-C to stop)"
            fi
            sleep "$interval"
        done
    else
        if [ -n "$alert_target" ]; then
            echo ">>> WARNING: --alert requires -w (watch mode). Ignoring."
        fi
        _exp-health-run "$remote_name"
    fi
}


# ── Check remote tmux output ─────────────────────────────

exp-check() {
    _exp-parse-remote "$@" || return 1
    local lines="${_EXP_ARGS[0]:-30}"
    # Capture directly from remote tmux (no local session dependency)
    _exp-ssh "tmux capture-pane -t watcher-$EXP_REMOTE_NAME -p -S -" 2>/dev/null | grep -v '^$' | tail -"$lines"
}


# ── List all configured remotes ───────────────────────────

exp-list() {
    local default_name
    default_name=$(_exp-default-name)
    local found=0

    echo "Configured remotes:"
    for conf in "$EXP_CONFIG_DIR"/*.conf; do
        [ -f "$conf" ] || continue
        found=1
        local name
        name=$(basename "$conf" .conf)
        # Source into subshell-safe locals
        local host="" port="" local_dir="" gpu_name="" gpu_vram="" gpu_count=""
        source "$conf"
        host="$EXP_HOST"
        port="$EXP_PORT"
        local_dir="$EXP_LOCAL"
        gpu_name="$EXP_GPU_NAME"
        gpu_vram="$EXP_GPU_VRAM"
        gpu_count="$EXP_GPU_COUNT"
        if [ "$name" = "$default_name" ]; then
            echo "  * $name  $host:$port"
        else
            echo "    $name  $host:$port"
        fi
        if [ -n "$gpu_name" ]; then
            echo "         gpu:   ${gpu_count}x ${gpu_name} (${gpu_vram} MB)"
        fi
        if [ -n "$local_dir" ]; then
            echo "         local: $local_dir"
        fi
    done

    if [ $found -eq 0 ]; then
        echo "  (none)"
        echo ""
        echo "Add one with: exp init <ip:port> -r <name> -l <local_path>"
    fi
}


# ── Show or set default remote ────────────────────────────

exp-default() {
    if [ $# -eq 0 ]; then
        echo "$(_exp-default-name)"
    else
        local name="$1"
        if [ ! -f "$EXP_CONFIG_DIR/${name}.conf" ]; then
            echo ">>> ERROR: No config for remote '$name'. Run: exp init <ip:port> -r $name"
            return 1
        fi
        _exp-set-default "$name"
        echo ">>> Default remote set to: $name"
    fi
}


# ── Build deliverable ZIP ──────────────────────────────────

exp-build() {
    # Uses EXP_LOCAL from the default remote's config
    _exp-load-remote "$(_exp-default-name)" 2>/dev/null
    local base="$EXP_LOCAL"
    local timestamp=$(date '+%Y-%m-%d_%H%M')
    local build_dir="$base/_builds/$timestamp"
    local zip_file="$base/_builds/build_$timestamp.zip"

    echo ">>> Building bundle ($timestamp) from $base..."
    mkdir -p "$build_dir"

    if [ -f "$base/writeup.md" ]; then
        cp "$base/writeup.md" "$build_dir/"
    else
        echo "WARNING: writeup.md not found at project root"
    fi

    # Copy README if it exists at project root
    if [ -f "$base/README.md" ]; then
        cp "$base/README.md" "$build_dir/"
    fi

    for exp_dir in "$base"/[0-9][0-9][0-9]_*/; do
        [ -d "$exp_dir" ] || continue
        local exp_name
        exp_name=$(basename "$exp_dir")
        mkdir -p "$build_dir/$exp_name"
        rsync -a \
            --include='*.md' --include='*.py' --include='*.png' \
            --include='*.csv' --include='*.json' --include='*.log' \
            --exclude='*' \
            "$exp_dir/" "$build_dir/$exp_name/"
    done

    if command -v pandoc &>/dev/null && [ -f "$build_dir/writeup.md" ]; then
        echo ">>> Converting writeup to PDF..."
        if pandoc "$build_dir/writeup.md" \
            --resource-path="$build_dir" \
            --pdf-engine=xelatex \
            -V geometry:margin=1in \
            -o "$build_dir/writeup.pdf" 2>/dev/null; then
            echo ">>> PDF generated."
        else
            echo ">>> PDF conversion failed (missing LaTeX?). Skipping."
        fi
    else
        echo ">>> pandoc not found. Skipping PDF. Install: brew install pandoc basictex"
    fi

    echo ">>> Creating ZIP..."
    (cd "$base/_builds" && zip -rq "build_$timestamp.zip" "$timestamp/")

    local n_experiments
    n_experiments=$(ls -d "$build_dir"/[0-9][0-9][0-9]_*/ 2>/dev/null | wc -l | tr -d ' ')
    echo ""
    echo ">>> Build complete"
    echo "    Folder:      $build_dir"
    echo "    ZIP:         $zip_file"
    echo "    Experiments:  $n_experiments"
    echo "    Writeup:     $([ -f "$build_dir/writeup.md" ] && echo 'yes' || echo 'MISSING')"
    echo "    README:      $([ -f "$build_dir/README.md" ] && echo 'yes' || echo 'MISSING')"
    echo "    PDF:         $([ -f "$build_dir/writeup.pdf" ] && echo 'yes' || echo 'no')"
    echo ""
    echo ">>> Previous builds:"
    ls -d "$base/_builds"/20* 2>/dev/null | while read d; do echo "    $(basename "$d")"; done
}


# ── Project inference ─────────────────────────────────────

_exp-infer-project() {
    # Tries to extract an experiment/project name from a string.
    # Looks for NNN_name, QN_NN_name, or DNN_name patterns.
    # Examples: 001_mnist_mlp, Q1_02_accuracy, D02_width_distillation
    # Returns the match on stdout, or empty string if nothing found.
    local text="$*"
    if [[ "$text" =~ (Q[0-9]+_[0-9]+[a-z]?_[a-zA-Z0-9_]+) ]]; then
        echo "${BASH_REMATCH[1]}"
    elif [[ "$text" =~ (D[0-9]+_[a-zA-Z0-9_]+) ]]; then
        echo "${BASH_REMATCH[1]}"
    elif [[ "$text" =~ ([0-9]{3}[a-z]?_[a-zA-Z0-9_]+) ]]; then
        echo "${BASH_REMATCH[1]}"
    fi
}


# ── Zap (send work to persistent worker) ────────────────

exp-clear-task() {
    # Usage: exp clear-task [-r remote]
    # Clears the saved task for a worker (marks it as no longer active).
    # Saves the old task as .last-task so health can show what was last worked on.
    _exp-parse-remote "$@" || return 1
    local task_file="$EXP_CONFIG_DIR/${EXP_REMOTE_NAME}.task"
    if [ -f "$task_file" ]; then
        mv "$task_file" "$EXP_CONFIG_DIR/${EXP_REMOTE_NAME}.last-task"
    fi
    echo ">>> [$EXP_REMOTE_NAME] Task cleared."
}

exp-zap() {
    # Usage: exp zap <folder> [instruction...] [-r remote]
    #        exp zap --clear [-r remote]
    #
    # Dispatches an experiment to a worker. <folder> is the experiment folder path
    # (relative or absolute). This becomes the worker's job folder:
    #   - EXP_LOCAL is updated to the folder's parent (project directory)
    #   - Worker CLAUDE.md is refreshed with the new path
    #   - _EXECUTION.md is written with dispatch info
    #   - The instruction is sent to the worker Claude
    #
    # If no instruction text is given after the folder, defaults to "Run <project>".
    local raw_args=()

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -t|--task)
                shift 2  # ignore legacy -t flag
                ;;
            *)
                raw_args+=("$1")
                shift
                ;;
        esac
    done

    _exp-parse-remote "${raw_args[@]}" || return 1
    local positional=("${_EXP_ARGS[@]}")

    # Handle --clear flag
    if [ "${positional[0]}" = "--clear" ]; then
        rm -f "$EXP_CONFIG_DIR/${EXP_REMOTE_NAME}.task"
        echo ">>> [$EXP_REMOTE_NAME] Task cleared."
        return 0
    fi

    # First positional = experiment folder (required)
    local folder="${positional[0]}"
    if [ -z "$folder" ]; then
        echo ">>> ERROR: Usage: exp zap <folder> [instruction] [-r remote]"
        echo "    <folder> is the experiment folder path"
        echo "    Example: exp zap ./D02_width_distillation -r r2"
        return 1
    fi

    # Resolve to absolute path
    local abs_folder
    abs_folder=$(cd "$folder" 2>/dev/null && pwd) || {
        echo ">>> ERROR: Folder not found: $folder"
        return 1
    }

    local task_name
    task_name=$(basename "$abs_folder")
    local project_dir
    project_dir=$(dirname "$abs_folder")

    # Remaining positional args = instruction (default: "Run <project>")
    local instruction="${positional[*]:1}"
    [ -z "$instruction" ] && instruction="Run $task_name"

    local worker_session="worker-$EXP_REMOTE_NAME"

    if ! tmux has-session -t "$worker_session" 2>/dev/null; then
        echo ">>> ERROR: Worker '$worker_session' not running. Run: exp worker $EXP_REMOTE_NAME"
        return 1
    fi

    # Update EXP_LOCAL to the project folder (parent of experiment folder)
    EXP_LOCAL="$project_dir"
    _exp-save-remote "$EXP_REMOTE_NAME"

    # Refresh worker CLAUDE.md with new paths
    _exp-write-worker-claude-md "$EXP_REMOTE_NAME"

    _exp-log "ZAP folder='$abs_folder' task='$task_name' project='$project_dir' worker=$worker_session"

    # Save task for health display — archive previous task as last-task
    local task_file="$EXP_CONFIG_DIR/${EXP_REMOTE_NAME}.task"
    [ -f "$task_file" ] && cp "$task_file" "$EXP_CONFIG_DIR/${EXP_REMOTE_NAME}.last-task"
    echo "$task_name" > "$task_file"

    # Write _EXECUTION.md — dispatch record for this run
    local exec_file="$EXP_LOCAL/$task_name/output/_EXECUTION.md"
    mkdir -p "$EXP_LOCAL/$task_name/output"
    local dispatch_time
    dispatch_time=$(date '+%Y-%m-%d %H:%M:%S')
    cat > "$exec_file" <<EXEC_EOF
# Execution Record — $task_name

# Dispatch (written by exp zap)
dispatched: "$dispatch_time"
remote: $EXP_REMOTE_NAME
host: "$EXP_HOST:$EXP_PORT"
gpu: "$EXP_GPU_NAME"
gpu_count: $EXP_GPU_COUNT
vram_mb: $EXP_GPU_VRAM
instruction: "$instruction"
project: "$project_dir"

# Completion (filled in by worker)
completed:
status:
runtime:
summary:
key_files:
EXEC_EOF
    echo ">>>   Wrote _EXECUTION.md"

    # Clean legacy _DELEGATE_DONE if present
    rm -f "$EXP_LOCAL/$task_name/output/_DELEGATE_DONE" 2>/dev/null

    # Prepend instruction to read the worker protocol fresh
    local worker_instructions="$HOME/.config/exp/exp-worker.md"
    local exp_template="$HOME/.config/exp/exp-template.md"
    local full_instruction="[FIRST: Read $worker_instructions now — it is your complete operating manual. THEN read $exp_template — it defines the format your writeup MUST follow. You are worker $EXP_REMOTE_NAME. Your job folder is $abs_folder. Follow every step in order.] $instruction"

    echo ">>> [$EXP_REMOTE_NAME] Sending to $worker_session:"
    echo ">>>   Project: $project_dir"
    echo ">>>   Experiment: $task_name"
    echo ">>>   $instruction"

    # Bottom pane is the Claude worker — send text and Enter separately
    tmux send-keys -t "${worker_session}.{bottom}" "$full_instruction"
    sleep 0.3
    tmux send-keys -t "${worker_session}.{bottom}" Enter
}


exp-check-zap() {
    # Usage: exp-check-zap [-r remote] [lines]
    _exp-parse-remote "$@" || return 1
    local lines="${_EXP_ARGS[0]:-30}"
    local worker_session="worker-$EXP_REMOTE_NAME"

    if ! tmux has-session -t "$worker_session" 2>/dev/null; then
        echo ">>> No worker for $EXP_REMOTE_NAME"
        return 1
    fi

    # Bottom pane is the Claude worker
    tmux capture-pane -t "${worker_session}.{bottom}" -p -S - | grep -v '^$' | tail -"$lines"
}


exp-list-zaps() {
    echo "Workers:"
    local found=0
    for session in $(tmux list-sessions -F '#{session_name}' 2>/dev/null | grep '^worker-'); do
        found=1
        local name="${session#worker-}"
        echo "  $name  (tmux: $session)"
    done
    if [ $found -eq 0 ]; then
        echo "  (none)"
    fi
}


# ── Legacy helpers ──────────────────────────────────────

exp-run() {
    _exp-parse-remote "$@" || return 1
    local script="${_EXP_ARGS[0]}"
    echo ">>> [$EXP_REMOTE_NAME] Running $script on remote..."
    _exp-ssh "cd $EXP_REMOTE && /venv/main/bin/python $script"
    echo ">>> [$EXP_REMOTE_NAME] Done."
}

exp-go() {
    _exp-parse-remote "$@" || return 1
    local exp="${_EXP_ARGS[0]}"
    local script="${_EXP_ARGS[1]}"
    exp-push "$exp" -r "$EXP_REMOTE_NAME" && \
    exp-run "$exp/$script" -r "$EXP_REMOTE_NAME" && \
    exp-pull "$exp" -r "$EXP_REMOTE_NAME" && \
    open "$EXP_LOCAL/$exp/"*.png 2>/dev/null
}
