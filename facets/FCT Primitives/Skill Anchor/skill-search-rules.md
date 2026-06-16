---
description: skill-search-rules — facet specifying how search-family skills layer methodology, default rules, and user rules. Defaults at `<skill>`/rules/; user overrides at SRC rules/.
applies-when-trait: Skill Anchor
location: ~/.claude/skills/`<skill-name>`/rules/  (defaults)  +  ~/ob/kmr/Topic/Search/SRC rules/  (user overrides)
---

# CAB skill-search-rules

The skill-search-rules facet specifies *how a search-family skill (find / describe / survey / …) layers its rules — defaults ship at `<skill>/rules/`; user overrides live at `~/ob/kmr/Topic/Search/SRC rules/`; six load layers compose at invocation with most-specific winning.* Methodology stays in `SKILL.md`; rule files are overlays on that methodology.

What distinguishes a conformant search-rule surface from one-off rule files:

- **Two homes** — defaults ship with the skill (portable); user rules stay personal (live in SRC rules/). Skills are sharable; user preferences aren't.
- **Six load layers** — methodology → default verb → default pair → user verb → user noun → user pair. More-specific wins on conflict.
- **Mandatory default verb file** — every skill carrying this facet MUST have `<skill>/rules/<verb>.md`.
- **Default pair files per noun** — `<verb>-person.md`, `<verb>-corp.md`, `<verb>-product.md` for the three core noun types the skill supports. Absent pair file = noun not supported by this skill.
- **User overlays optional** — all `SRC rules/*` files are optional; absence means default behavior.

This is a CAB facet of the Skill trait. Like skill-testing, the actual content lives at the runtime location, not under the anchor's filesystem folder.


## Two homes for rules

| Home | What it contains | Audience |
|---|---|---|
| **`<skill>/rules/`** | Default rules shipped with the skill — verb defaults, pair defaults with entity knowledge baked in | Anyone installing the skill set; works out of the box |
| **[[SRC rules]]** (`Topic/Search/SRC rules/`) | The user's personal overrides — same file shapes, user-specific preferences | The individual user; their custom behavior |

Skills are portable. User rules stay personal. The two layer at invocation; more specific wins.


## Layout per home

```
~/.claude/skills/<skill>/rules/            ← ships with skill (defaults)
├── <verb>.md                                  default verb rules
├── <verb>-person.md                           default pair rules — entity knowledge for people built in
├── <verb>-corp.md                             same for orgs
└── <verb>-product.md                          same for products

~/ob/kmr/Topic/Search/SRC rules/           ← user overrides
├── <verb>.md                                  your verb rules
├── <noun>.md                                  your noun rules (apply to any verb on this noun)
└── <verb>-<noun>.md                           your pair rules (most specific)
```


## Loading order at invocation

When the skill runs (e.g. `survey products`), the agent loads in this order:

```
1. <skill>/SKILL.md                        methodology         (invariant runbook)
2. <skill>/rules/<verb>.md                 default verb rules  (ships with skill)
3. <skill>/rules/<verb>-<noun>.md          default pair rules  (ships with skill)
4. SRC rules/<verb>.md                     USER verb rules     (overrides 2)
5. SRC rules/<noun>.md                     USER noun rules     (cross-verb override)
6. SRC rules/<verb>-<noun>.md              USER pair rules     (most specific, wins all)
```

Layers 2-3 ship → skill works on a fresh install. Layers 4-6 are user-specific overlays. More-specific wins on conflict (6 beats 5 beats 4 beats 3 beats 2).


## Section name within a rules file

Default files contain prose-formatted defaults (dimensions, sources, behavior). User rule files use a `## Rules` section with imperative bullets — one rule per bullet, written as instructions to the agent. The agent reads both styles as guidance to apply.


## Compile (deferred)

The `/compile` action can later materialize verbatim pair files from default + user overrides, if rules accumulate enough that load-time composition becomes wasteful. Compile-on-the-fly is deferred until the agent's load-time-composition reliability becomes a real problem in practice; for now the agent composes on each invocation from layers 2-6.


## Constraints

- A skill carrying this facet MUST have a `<skill>/rules/<verb>.md` file (the default verb-level rules).
- Default pair files (`<verb>-<noun>.md`) MUST exist for every noun-type the skill documents support for; absent pair file = noun not supported by this skill.
- User rule files (`SRC rules/...`) are all optional; their absence simply means default behavior applies.
- Methodology (the invariant runbook) MUST live in `SKILL.md`, not in rule files. Rule files are *overlays* on the methodology.


## Expected usage

- Most search skills will carry this facet.
- A new noun (e.g. `book`) is added by creating `<skill>/rules/<verb>-book.md` in each verb skill that should support it; users can then add `SRC rules/book.md` and `SRC rules/<verb>-book.md` as preferences emerge.
- Pair files appear in `SRC rules/` gradually as the user's per-pair preferences crystallize.


## Reference

User-facing summary of how this all combines: [[SKL Search Overview]].


## Migration note (F116)

Migrated from `SKA skill-trait search-rules.md` per F116. Substantive content preserved; framing rewritten from "parallel-to-CAB trait" to "CAB facet of the Skill trait." Wiki-link sweep: `[[SKA skill-trait search-rules]]` → `[[CAB skill-search-rules]]`.
