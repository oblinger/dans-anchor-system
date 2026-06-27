---
description: "standard test-kind catalogue — generic strategy per kind, linked from each project's Testing tests-table"
---

# Common Testing Types

| -[[Common Testing Types]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Design Docs]] → [Common Testing Types](hook://p/Common%20Testing%20Types)<br>: standard test-kind catalogue — generic strategy per kind, linked from each project's Testing tests-table |
| --- | --- |
| Up | [[FCT Testing]],   |
| --- | |

This is the **shared reference** for the standard kinds of test. Each project's `{NAME} Testing.md` carries a required **tests-table** (see [[FCT Testing]]) whose left column names the kinds it uses; each kind cell **links here** (e.g. `[[Common Testing Types#Property]]`) when the project's use of that kind is *vanilla*. When a project does something *special* with a kind, the cell instead links to a section **within that project's** `{NAME} Testing.md` explaining the twist. One H2 per kind below; add a kind here only when it recurs across projects.

## Unit

The smallest tests: one function, method, or enum-variant in isolation, asserting exact outputs and every `Result`/error arm. Lives colocated with the code (inline `#[cfg(test)]` for Rust, a `test_*.py` peer for Python). Fast, hermetic, deterministic — the fast tier that gates every commit. **Completeness target form:** "every public function/method and every variant exercised; every error arm hit." Unit tests are the default; reach for the kinds below only where unit example-coverage leaves a gap.

## Property

Generated-input tests (proptest / Hypothesis / QuickCheck) asserting an **algebraic law** over many random inputs rather than one example: round-trips (`decode(encode(x)) == x`), bounds (`len() <= capacity`), monotonicity (a counter never decreases), idempotence (`f(f(x)) == f(x)`), and ordering/lattice laws. One property catches an infinite class of bugs the example tests miss. **Target form:** "one property per identified invariant; no sampling." Prefer a property over a pile of example cases whenever a law exists.

## Golden

Byte-exact or string-exact fixtures that **freeze a contract**: a serialized wire format, a rendered output, a file layout. The test asserts the produced bytes/string equal a stored golden value; any drift fails loudly. Essential wherever a format crosses a boundary another implementation must reproduce (a wire protocol, a cross-language port, a tool that parses the output). **Target form:** "100% of wire/boundary types have a frozen fixture." Normalize nondeterminism (sort map keys, inject a fixed clock) before freezing.

## Fuzz

Arbitrary / adversarial / untrusted input into a decoder or parser, asserting it **never panics and never over-allocates** — only returns `Ok`/`Err`. Covers truncated, oversized, malformed, and deeply-nested inputs. Two forms: byte-level fuzz of a wire decoder, and **model-based** fuzz of a state machine (a random sequence of operations that must preserve invariants and never panic). Tools: proptest with `any::<Vec<u8>>()`, or `cargo-fuzz`/libFuzzer for sustained campaigns. **Target form:** "every untrusted-input boundary has a no-panic fuzz target."

## Integration

Tests that exercise a **real boundary** between components — a real socket, a real file, a real subprocess — rather than a mocked one. Slower and less hermetic than unit tests, so they live apart (a `tests/` dir, a dedicated suite) and the environment-dependent ones are **gated** (`#[ignore]`, a feature flag, or a tag) so the fast tier stays deterministic. **Target form:** "every boundary and every error path of that boundary has one scenario." Make each test deterministic and fast (short timeouts so a failure surfaces as an error, never a hang).

## Concurrency

Tests for behavior under threads/parallelism: compile-time guards that a type is `Send + Sync`; linearizability stress (N threads interleaving operations through a shared lock, asserting no lost updates / no panic / a consistent final state); and isolation of global/singleton state (thread-local overrides, set-once singletons, atomics). Keep thread counts modest and loops bounded so a bug fails fast rather than hanging. **Target form:** "a Send+Sync guard on every shared type + one stress test per shared global." Often gated alongside integration.

## End-to-End

The whole system driven from its real entry point — the CLI, the UI, the public API — asserting the user-visible result. The most realistic and most expensive; keep the count small and tied to user stories. For GUI/desktop, this is the synthesize-input → observe-diagnostic → tri-state pattern (and, when a real display/TCC session is needed, the cross-machine bridge). **Target form:** "one per critical user story." Most library-shaped projects need few or none.

## Smoke

A handful of shallow "does it even start and do the obvious thing" checks — build succeeds, binary runs, the happy path produces the expected output and exit code. The cheapest confidence that nothing is catastrophically broken; often the first integration test written. **Target form:** "the primary happy path of each shipped entry point." Smoke is breadth-first and shallow by design.

## Regression

A test written to lock a **specific past bug** so it can never silently return. Frequently a "pinning" test: it captures the *current* (possibly still-wrong) behavior with a comment naming the issue, so a later intended-behavior change is a deliberate assertion flip rather than an accident. **Target form:** "one per fixed (or knowingly-deferred) defect." Regression tests accrete over a project's life and are never deleted, only updated when the contract genuinely changes.

## Performance

Micro- or macro-benchmarks measuring latency/throughput of a hot path (criterion, `cargo bench`, pytest-benchmark). Almost always **reported, not gated** — wall-clock thresholds are too flaky for CI; the value is catching a large regression and substantiating a performance claim. **Target form:** "one bench per performance claim the design makes; reported."

## Subjective

Specs that can only be judged, not asserted — "does this layout look right?", "is this message clear?". Captured by handing an artifact (a screenshot, a generated text) plus a `## Looks like` spec to an LLM judge for a multi-vote yes/no, or by human review. Inherently sampled, never exhaustive. **Target form:** "no fixed target — sampled per visual/qualitative spec." Use sparingly; prefer an objective assertion whenever one exists.

## See also

- [[FCT Testing]] — the facet spec that requires the tests-table linking here.
- [[DSC verification]] — the four-tier verification discipline test kinds map onto.
