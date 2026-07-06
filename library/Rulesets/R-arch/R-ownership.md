# RULESET R-ownership
include::
description:: Every mutable resource has exactly one owner; invariants are made true by construction rather than defended at runtime.

Recurs in MUX + HA + SKD. MUX: "Buffer Manager owns the text view; nobody else modifies it directly" (`CLAUDE.md`) and "no runtime mutex is needed, because no other path can produce a second brain" (MUX Decisions). SKD: "SKD is the sole authority for updating task status … Agents never edit the roadmap directly." HA: "every module belongs to exactly one subsystem … enforced by architect" (`HA Design/HA Architecture/HA Architecture.md`).

### RULE R-ownership-01 — One owner-writer per mutable resource (sampled)

Each mutable resource (a file, a state object, a UI region, a doc) has exactly one owning component; every other component reads through the owner or requests changes from it. **Check pattern:** for a sampled resource, search for write sites; writes outside the owner are violations.

### RULE R-ownership-02 — Structural guarantees over runtime discipline (stated)

When a property must hold ("exactly one X", "only Y touches Z"), prefer making it true by construction — a single spawner, a monopoly on the constructor, hardcoded routing — over defending it with runtime mutexes, guards, or conventions. A guard defends against a threat; a structure removes it.

### RULE R-ownership-03 — Every module belongs to exactly one subsystem (checked)

**Check pattern:** the architecture doc's subsystem→module map covers every source module exactly once; orphans and double-assignments are violations.
