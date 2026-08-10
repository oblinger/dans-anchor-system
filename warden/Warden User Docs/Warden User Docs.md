---
description: Warden user documentation — the manual for writing and running rules
---

| -[[Warden User Docs]]- | : the manual — how to write and run Warden rules<br>→ [[DAS]] → [[WARD]] → [Warden User Docs](hook://p/Warden%20User%20Docs)  |
| --- | --- |
| [[Warden Examples]]  | worked examples of every rule-execution mode (start here) |
| ... | [[Warden Examples Extended]],   |

# Warden User Docs
The task-oriented manual for authoring and running Warden rules — start at [[Warden Examples]].

**Warden** lets you state a rule once — *when* a moment happens, *where* (which file), and optionally *if* a condition holds — and have it enforced automatically, with a corrective message fed back to the agent. This is the user-facing manual: how to author rules and what they can do.

> [!note] Where the precise specs live
> This manual is task-oriented (*how do I…*). The authoritative formats are the reference specs: the rule/ruleset file format is [[Warden Rule]], the `when::` moment vocabulary is [[Warden Events]], and `where::` is [[DAS Ruleset]] § Where clause. New here? **[[Warden Examples]]** is the fastest way in.

## Contents

- **[[Warden Examples]]** — one worked ruleset, ten complete rules: a prose `tell`, a Python test, an LLM judgment, a script-assisted judgment, an `edit`, a `deny`, a shell (`sh`) condition, a Python `run`, a shell `run`, and sensing `agent` state.
- **[[#Reading this manual — mechanism vs recommendation]]** — how to tell a rule of the engine from a habit of ours.
- **[[#Remediation messages]]** — teaching an agent how to fix what a rule caught.
- *Getting started, the importer (Vale/Hookify), and the CLI — to come as Warden is built (see [[Warden Roadmap]]).*

## Reading this manual — mechanism vs recommendation

Two very different kinds of statement appear in these pages, and the difference matters more than it looks:

- **Mechanism** — what the engine does. Break it and nothing works. *"The scanner indexes any `# RULESET` or `### MEND` heading anywhere under the corpus root."* You cannot opt out of mechanism; you can only be right or wrong about it.
- **Recommendation** — what we found works. Break it and the engine does not notice. *"Keep a rule's remediation message in the ruleset that owns the rule."* You are meant to weigh these against your own corpus.

Every convention below is labelled one or the other. This is not decoration. Warden's scanner is deliberately permissive about *where* things live, so almost everything about corpus layout is advice — and advice that reads like a requirement quietly becomes a requirement, invented by nobody, that the next consumer has to reverse-engineer. When a section says **Recommendation**, you may ignore it and the engine will not care.

## Remediation messages

A rule that fires tells the agent *what is wrong*. A **mend message** tells it *what to do about it* — so an agent who does not know the convention can recover without the author being in the room.

The agent-facing surface is one word. A steer line whose rule has a message ends with the bare word `mend`; running `warden mend <rule-id>` prints it. There is no topic and no namespace to learn — the rule id already on the line is the lookup key.

### Mechanism — what the engine requires

- A message is a heading `### MEND <slug>`; its body runs to the next heading at the same or shallower level. Parsing is fence-aware, so a quoted example inside a code fence is never mistaken for a declaration.
- A rule claims a message with a `mend:: <slug>` field **in the rule's own spec**. The reference points rule → slug, never the other way: rule ids are machine-numbered and move, slugs are hand-chosen and do not, so a renumber carries the reference with it and nothing can orphan. Many rules may name one slug; the text exists once.
- The scanner finds `### MEND` **anywhere under the corpus root**, in any file, including a file that contains nothing else. Placement is not a mechanism.
- The `mend` marker on a steer line is *derived*, never declared — `warden compile` marks a rule only when its slug resolves to a real message, so the marker cannot promise text that does not exist.
- `warden compile` warns on: a slug defined twice (first wins), a `mend::` naming no block (the row's mend is cleared), a block no rule references, and a numbered slug.
- Slugs are semantic, never numbered. A numbered slug invites mirroring the rule's own number, and then two numbering schemes drift against each other — harmless to the machine, wrong to read.

### Recommendation — where to put them

- **Default: a `## Mend` section at the bottom of the ruleset that owns the rules.** The message sits in the same file as the rules it teaches, so an author editing a rule sees its remediation without opening anything, and a reader who follows a rule id lands where the fix is. [[R-log]] is the worked instance — two `### MEND` blocks under one `## Mend` section, referenced by `mend::` on the rules above them.
- **Only when a message genuinely spans rulesets: a dedicated `rulesets/M-<name>.md`.** Cross-cutting advice — one fix that several unrelated rule families all point at — has no owning ruleset, and duplicating it into each would reintroduce the drift the many-to-one reference was designed to avoid. The `M-` prefix keeps it sorted beside the rulesets it serves while reading as a distinct kind of file.
- **A separate top-level `mend/` directory is the shape to avoid.** It was tried and removed. It bought nothing but a second place to look, and its filenames read as generated output — a reader could not tell whether `DAS Mend Log.md` was a message source or a log of messages the engine had emitted.

### Recommendation — what to write

State the fix, then point at the facet and a worked example. Do not restate the documentation.

The failure mode is not length. It is a message slowly absorbing the facet it points at until the two disagree, at which point the agent is being taught something the spec no longer says. A message whose job is *the fix* has no reason to grow into the facet — so the shape to aim for is *"do X; for the model see [the facet] and the worked example at [the instance]."*
