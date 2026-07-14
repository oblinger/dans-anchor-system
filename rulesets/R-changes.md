# RULESET R-changes
include::
where:: `file: **/changes/C*/proposal.md`
description:: Rules for the OpenSpec-conformant `changes/` folder ([[DAS Changes]]) — C-numbered change folders created by `/change`, executed by `/mint`, closed by `/finalize`'s archive-merge.

### RULE R-changes-01 — One folder per change, required artifacts (stated)
Each change is a `changes/C<NNN>-<kebab-slug>/` folder holding `proposal.md` and `tasks.md` (required); `design.md`/`design/` and a `specs/` delta are optional. The C-number matches a backlog row minted by `state Backlog C+ define`.
**Why:** the folder is the change's whole record; a change without a proposal or task list can't be executed or audited.

### RULE R-changes-02 — Delta requirements carry scenarios (stated)
A change's `specs/<capability>/spec.md` delta marks requirement sections `## ADDED` / `## MODIFIED` / `## REMOVED`; every ADDED or MODIFIED requirement carries at least one `#### Scenario:` Given/When/Then block.
**Why:** OpenSpec's validator hard-errors otherwise — and the scenario is the change's minimum acceptance criterion.

### RULE R-changes-03 — Archived changes are immutable (stated)
`/finalize` moves a completed change to `changes/archive/C<NNN>-<slug>/`; archived folders are never edited or un-archived — follow-up work is a new C-number.
**Why:** the archive is the anchor's change history; editing it destroys the audit trail the layout exists to provide.
