---
description: "test strategy + proposed tests"
status:: drafting
---
:>>
# {slug} Testing
How {slug} is verified: the kinds of test, how much of each, and the concrete inventory consistent with that strategy.

**Related:** [[{slug} Architecture]],  [[{slug} PRD]],  [[DAS verification]]

**TLDR**
- **{{Posture descriptor}}** — {{one line: the shape of the test investment, e.g. "heavy unit + integration; minimal e2e"}}
- **{{Seam / focus}}** — {{one line: where the load-bearing coverage concentrates and why}}
- **{{Bar vocabulary}}** — {{one line: how completeness bars read, e.g. "Strong / Heavy / Bounded / Sampled per kind"}}
- ...

## Tests

| Kind | In system | Expected |
| --- | --- | --- |
| [[DAS Common Testing Types#{{Kind}}\|{{Kind}}]] | {{N}} | {{target count and/or qualitative bar}} |
| ... | | |

## Overview

{{One paragraph: this project's testing posture in plain English — the shape of the test investment, not the inventory.}}

## Strategy

### Test Kinds

- **{{Kind}}** — {{definition + scope for this project}}
- ...

### Completeness Targets

- **{{Kind}}** — {{the bar; be specific — "every public function in `src/`", "one per user story", or "no target — sampled"}}
- ...

### Responsibilities

- **{{Kind}} tests** — {{who authors: agent on `/mint`, author-curated, CI}}
- ...
- **CI** — {{what runs on what trigger}}

### Tier Mapping

Per [[DAS verification]]:

- **Tier {{N}} ({{tier name}})** — {{kinds mapped to this tier}} — {{what confidence this buys}}
- ...

## Proposed Tests

### {{Kind}}

| Test | Exercises | Spec |
| --- | --- | --- |
| `{{test_name}}` | {{what it exercises}} | {{[[wiki-link]] to module doc § Tests, or [bare bracket] if not yet authored}} |
| ... | | |

### ...

## See also

- [[{slug} Architecture]] — peer facet; subsystem boundaries drive the integration-test inventory.
- [[{slug} PRD]] — user stories drive the e2e inventory.
- [[DAS verification]] — four-tier verification discipline mapped in § Tier Mapping.
