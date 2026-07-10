# RULESET R-wrapper-cli
include::
description:: All interaction with managed infrastructure flows through the sanctioned command surface; raw primitives are forbidden, missing capability is proposed rather than worked around, and destructive commands check status first.

Recurs in A2X + SKD + the global CLAUDE.md (`ctrl` / `exp` / never-raw-ssh-tmux). A2X EXP: "NEVER run … ANY raw tmux command … NEVER run raw `ssh` commands to remotes" and "If no `exp` command exists for what you need, stop and propose adding one — do not work around the system." SKD: "The cmx command surface must be complete … No escape hatches, no raw shell access for agents."

### RULE R-wrapper-cli-01 — Always through the sanctioned surface, never raw primitives (stated)

Where a project defines a wrapper CLI over managed infrastructure (tmux sessions, remotes, experiment workers), all interaction — human and agent — goes through it. Raw underlying commands are forbidden even when they would work, because they bypass the wrapper's state tracking.

### RULE R-wrapper-cli-02 — Missing capability: stop and propose, never work around (stated)

When the sanctioned surface can't do something, the move is to halt and propose adding the command — not to reach under the wrapper with raw primitives. Workarounds fork the interface and rot the wrapper's authority.

### RULE R-wrapper-cli-03 — Destructive commands check status first; setup is idempotent; force-flags are gated (stated)

Never a destructive action without a status check immediately before it; init/setup commands are safely re-runnable; `-f`/`--force` on live state requires explicit user approval.
