# RULESET R-fct-move
include::
description:: `/move` relocates an anchor folder to a new path and updates every path-dependent system that indexes it — HookAnchor, Claude Code session history, hardcoded paths inside the anchor's own configs, …

### RULE R-fct-move-01 — Move is executed atomically via `/cab move` (checked)
A move is never performed piecemeal by hand; it is always orchestrated through the `/cab move` skill, which sequences all six steps in order.
**Check pattern:** no anchor whose location changed has a stale `ha -p` path (HA reindex was run).
**Tier:** checked

### RULE R-fct-move-02 — Physical relocation uses move, never copy (checked)
The folder is moved (renamed/relocated) rather than copied; the old location must not remain.
**Check pattern:** after a move, no duplicate folder exists at the old path.
**Tier:** checked

### RULE R-fct-move-03 — Claude session path is updated as part of the move (checked)
Step 3 (session migration) is always executed; it is not optional even when the old session directory appears functional.
**Check pattern:** the Claude Code project directory name matches the anchor's current on-disk path after the move.
**Tier:** sampled

### RULE R-fct-move-04 — Cardinality: one per anchor per move event (stated)
An anchor has at most one current location; each move event is a discrete, non-concurrent operation. Parallel moves of the same anchor are not supported.
**Check pattern:** no anchor has two in-flight move operations simultaneously.
**Tier:** stated
