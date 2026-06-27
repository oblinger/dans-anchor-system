# RULESET R-cae
include::
description:: CAE's anchor-local ruleset — rules truly specific to this example anchor

### RULE R-cae-01 — Anchor-prefixed file names (checked)

Every `.md` file and every subfolder inside the `CAE/` tree starts with the literal prefix `CAE ` (with the trailing space) or `CAE.` (for hyphenated entry points). Unprefixed names like `PRD.md`, `Backlog.md`, `Plan/` are violations.

**Check pattern:** walk every path under `CAE/`. For each `.md` file and each directory, verify the basename starts with `CAE ` or `CAE.`. Exempt: `SKILL.md`, `CLAUDE.md`, `README.md`, `.anchor`.

**Why:** Obsidian's wiki-link namespace is flat — without the prefix, `[[Backlog]]` is ambiguous when multiple anchors carry a Backlog facet. Prefixing makes every name self-disambiguating across anchors.

### RULE R-cae-02 — Scheduler operations are durable across restart (stated)

Every CAE scheduler operation (task creation, completion, priority change) commits to durable storage before returning success to the caller. Crashes between commit and acknowledgment are acceptable (the operation is durable, the caller may retry); operations lost on restart are not acceptable.

**Check pattern:** integration test that kills the scheduler process at each transaction boundary and verifies state-after-restart matches state-immediately-before-kill. Failure-injection harness lives at `CAE Code/tests/durability/`.

**Why:** users rely on CAE for long-running schedules across machine reboots; silent data loss is the worst possible failure mode for this domain.


## See also

- [[FCT Rules]] — meta-spec for this file's format.
- [[CAE Decisions]] — companion facet; D-records may cite these rules.
