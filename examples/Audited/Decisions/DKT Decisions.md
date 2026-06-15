---
description: "Durable architectural decisions + rationale — standard/API split, Rust+Python common docs, anchor-crate separation"
---

# DKT Decisions
include::

| -[[DKT Decisions]]- | : durable architectural decisions + rationale |
| --- | --- |
| Related | [[DKT Design]],  [[DKT Architecture]],  [[DKT Standard]],  [[DKT API]],   |

Each entry records a decision once: the fork, what was chosen, why, and what it commits downstream docs to. Docs that implement a decision link back here rather than re-arguing it.

### D01 — Standard documents semantics; API documents the concrete interface (checked)

**Decision.** The **Standard** ([[DKT Standard]] folder) documents *semantics only* — what anchors are, do, and mean; what a Markdown-Based Item Store *is*; the semantics of agent orchestration. It deliberately does **not** pin down a specific programmatic API. The **API** ([[DKT API]] folder) pins down the concrete interface, **making the standard's abstract claims concrete**. A standard doc and its API doc form a **pair** — e.g. [[DKT Anchor]] (semantics) ⟷ [[DKT Anchor API]] (concrete surface) — that travel together conceptually.

**Why.** Semantics and interface change at different rates and serve different readers (a spec reader vs. a crate consumer). Keeping the API out of the standard lets the standard stay language-agnostic and stable while the concrete surface evolves; keeping them paired (not merged) means the API can be read as "the standard, made executable."

**Consequences.**
- The two stay in their respective folders (`DKT Standard/`, `DKT API/`) and **cross-link** rather than merging.
- Resolves [[F083 — Reconcile DKT Anchor API as the definitive crate spec]] Q1: `DKT Anchor API.md` **stays in `DKT API/`** (not moved into `DKT Standard/`); it is conceptually paired with [[DKT Anchor]], not physically co-located.
- API docs therefore should **not restate** the standard's semantics (F083 Q3 leans the same way) — they map types → behavior *by reference* to the standard.

### D02 — One API document per surface serves both Rust and Python (checked)

**Decision.** DKT supports **both** a Rust implementation and a Python implementation. Each API surface ([[DKT API]], [[DKT Anchor API]], [[DKT MBIS API]], [[DKT Agent API]]) is documented by a **single common document** that specifies both languages: the mental model is identical; only idioms differ (Rust closures ⟷ Python context managers / kwargs — already shown in [[DKT API]] § Python parity). The common document is kept common **as long as the surfaces stay close**. Split into per-language module docs **only if and when they diverge** enough that one doc becomes confusing.

**Why.** The two languages are meant to mirror each other 1:1 in shape; a common doc keeps them honest (divergence becomes visible as soon as one doc can't describe both) and avoids maintaining two parallel specs that silently drift.

**Consequences.**
- "DKT API" (and each sub-API doc) **simultaneously represents two things on purpose**: the Rust crate being built (currently by the HookAnchor Pilot, see [[DKT Anchor Roadmap]]) *and* DKT's Python implementation. This dual-representation is the intended common-document state, not a naming bug.
- The [[DKT API]] § "Naming layers" row split (`docket` Python *module* vs `docket` Rust *crate*) stands; the API docs sit above that split and describe both.
- **Divergence trigger to watch:** the first time a single doc can no longer describe both languages without per-language caveats on most rows, split that surface into `… (Rust)` / `… (Python)` module docs and leave the common doc as the shared mental model. Record the split as a new D-record.

### D03 — The anchor crate is separate from the `docket` crate (shares the common API docs) (checked)

**Decision (current direction; finalized in [[F083 — Reconcile DKT Anchor API as the definitive crate spec]]).** `anchor` is its **own leaf crate**, separate from `docket`; `docket` *depends on it and re-exposes* its surface via `db.anchor`. The common API docs (D02) remain the shared spec for both.

**Why.** The `docket` crate is expected to be large; consumers that need only anchor identity / resolution / metadata (e.g. HookAnchor) should not be forced to compile all of Docket (`store` / `watcher` / `reconcile`). Cargo compiles whole crates, so the separation is the prerequisite for a minimal consumer build.

**Consequences.**
- Refines [[DKT API]]'s "both implementations live in a module / crate named `docket`": the **anchor surface** lives in a separate `anchor` crate that `docket` re-exposes.
- The anchor crate depends only on light external crates (serde / serde_yaml / regex / thiserror), never on docket internals.
- Full reconciliation of the anchor API doc to this shape is tracked in [[F083 — Reconcile DKT Anchor API as the definitive crate spec]] (R1–R11).

### D04 — Anchor writes are surgical: byte-precise frontmatter, order-preserving anchor section (checked)

**Decision.** When an anchor is written back to disk — whether to a Form A `.anchor` dotfile, a Form B markdown file's YAML frontmatter, or a Form B markdown file's `## anchor` H2 section — the write touches **only the anchor's storage region**. Everything else in the file is bit-identical before and after. The `Anchor` record exposes an **ordered (key, value) sequence** reflecting the on-disk order, and the writer consults this sequence when re-serializing. Two contracts, calibrated to what users are likely to hand-edit:

- **Frontmatter (Form A's `.anchor` content; Form B's YAML frontmatter)** — round-trips **byte-for-byte** except for fields whose value the caller explicitly changed. Key order, blank lines between keys, comments (`# …`), trailing whitespace, and unrecognized keys all survive. A field set to its current value is a no-op write — same bytes back out.
- **Anchor section (Form B's `## anchor` H2 body)** — the section may be torn down and rebuilt. The **field order from the original is preserved**; bullets / H3 markers are regenerated cleanly. Whitespace around the `key:: value` separator may normalize. Comments and unrecognized keys inside the anchor section are preserved across rebuild.

In both surfaces, content **outside** the anchor's storage region — body prose, other H2s, other frontmatter blocks elsewhere — is bit-identical before and after every write.

**Why.** Markdown files carry editor state — comments, blank-line groupings, fields the system doesn't yet model — that the user expects to survive automated edits. A non-surgical write that re-emits the whole frontmatter from a schema strips those, eroding trust in the anchor system as a tool that can be wired into hand-edited files. The byte-precise frontmatter rule makes the anchor system safe to use alongside arbitrary editor conventions. The looser anchor-section rule reflects that the anchor block IS the system's surface — torch-and-rebuild is acceptable as long as field order survives.

**Consequences.**
- The `Anchor` record (both crates) exposes an ordered (key, value) sequence — not just a map — so writers can preserve source order. `field_names()` returns them in source order.
- Field-level writes (e.g. `set_field("status", "done")`) **patch one line** in the frontmatter; they do not trigger a full re-emit.
- The frontmatter parser captures (and the writer passes through) blank lines, comments, and unrecognized keys.
- A heavy round-trip test corpus pins these invariants: read → modify-one-field → write → diff. Frontmatter diff is one line; anchor-section diff allows whitespace normalization only. Tracked in [[DKT Anchor Roadmap]] § Surgical-write test strategy and the new F-row.
- Cross-language: the Python and Rust writers must produce the same byte sequence for the same input + same edit. F022-style fixtures pin this.

### D05 — Anchor parsing is total: always yields a verdict, never panics (checked)

**Decision.** The anchor layer **never crashes on input** — no panic, no exception escape, no infinite loop, no resource leak — regardless of how malformed the input is. For any byte sequence (valid UTF-8 or not, syntactically valid YAML or not, semantically consistent or not), the parser returns exactly one of two verdicts:

1. **"Valid anchor (possibly with warnings)"** — the input declares an anchor; the parser surfaces a populated `Anchor` record and a separate (potentially non-empty) list of warnings naming each field-level degradation. Malformed parts of a recognized anchor (a corrupt `traits` list, an unparseable `parents` entry) are **ignored** at the field level — the field defaults to its empty/default value and a warning records what was dropped. The rest of the anchor record is still populated.
2. **"Not an anchor"** — the input does not declare an anchor at all (e.g. a markdown file with no frontmatter and no `## anchor` H2; a `.anchor` file containing arbitrary text that doesn't parse as YAML). The parser returns a "no anchor" verdict cleanly; this is not an error.

Errors (vs. warnings) are reserved for cases that genuinely block the parser from rendering a verdict — out-of-memory, I/O failure, programmer-violated invariants. Bad user input is never an error; it's a verdict plus warnings.

**Why.** The anchor layer sits at the foundation of the system — Docket, HookAnchor, viewer, every consumer leans on it. If a malformed frontmatter or a stray byte can take down the parser, every layer above inherits that fragility. Making parsing total means consumers can iterate over thousands of files without defensive try/except wrapping every read, and they can show the user "this file isn't an anchor" or "this anchor parsed with N warnings" instead of "the indexer crashed."

This also separates **two orthogonal concerns**: *is this an anchor?* (verdict) and *how clean is it?* (warning list). The first is decidable; the second is advisory. Tools can ignore warnings and still index correctly; tools that surface warnings can help users clean their data.

**Consequences.**
- The Anchor API's parse functions return `Result<AnchorVerdict, FatalError>` where `AnchorVerdict ∈ { Valid(Anchor, Warnings), NotAnAnchor }`. `FatalError` is reserved for I/O / OOM / programmer error — never user-input errors.
- Per-field degradation: a malformed `traits: foo: bar` doesn't kill the anchor — the field stays empty, a warning records the input shape, the rest of the record (slug, title, description, etc.) populates normally.
- The warnings catalog in [[DKT Anchor]] § S4 is the canonical list; any new degradation mode adds a row.
- A heavy fuzz + adversarial corpus pins these invariants — see [[DKT Anchor Roadmap]] § Robustness test strategy and the new F-row.
- Property-based test (cross-language): for any byte sequence, `parse(bytes)` terminates within a bounded time and returns a verdict. The Python implementation uses Hypothesis; the Rust uses proptest.
