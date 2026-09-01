# RULESET R-ha
include::
where:: `**/HookAnchorApp/**/*.rs`
description:: HookAnchor's own enforceable constraints — the write-amplification gate, the print-vs-log boundary, and the build-tool gate. Authored 2026-08-11 against checks that were run, not guessed.

**Registered 2026-09-01 per [[Tink Backlog#^T362|T362]].** This block lived in `HA Rules.md` from 2026-08-11 and never compiled: Warden's corpus is a single directory and an anchor's `.anchor` `rules:` key is not read by the engine. It now lives here, in the enumerated git-tracked corpus, and is activated by the `ha` trait on HookAnchor's `.anchor` — `warden compile` derives the trait name from the ruleset name. `HA Rules.md` links here and holds no copy.

**The header binding is scoped, not `always`.** As authored it read `` where:: `always` `` with a ruleset-level `` when:: `write:rust` ``, which would have fired these HookAnchor-specific conventions at every `.rs` write anywhere on the machine — docket, SVP, any repo — and that is the shape that cost TINK 140 wasted LLM calls via `R-mac`. The glob confines the set to HookAnchor's own tree, and each rule below carries its own moment: `write:rust` for the two file rules, `tool:pre:Bash` for the build-tool gate, which is an action and has no file to select.

**Every rule below was measured against the real tree before it was written, and the measuring is the point.** This block sat deliberately unwritten from 2026-08-08 because a selector that reaches nothing is silently inert while reading as enforced. Three findings came out of finally doing the measurement, and they shape the whole ruleset:

- **A `where::` file glob cannot reach a `.rs` file at all.** The audit sweep's scope enumerator is `.md`-only (`audit-plan.py` § `enumerate_scope`, anchor mode: `target.rglob("*.md")`), and its scope is rooted at the anchor folder — which for HA is the vault directory, not `~/ob/grove/HookAnchorApp/` where the source actually lives. Measured directly: an anchor-mode plan over `prj/Hook Anchor` produces **94 rules, of which 0 have a `.rs` target**. So HA's code rules are bound to the **`when:: write:rust` moment** instead, which the hook derives from the written file's extension (`warden_hook.py` § `_CONTENT_KIND`) and therefore reaches source wherever it lives. Any future HA rule phrased as `` where:: `file:{anchor}/**/*.rs` `` is dead on arrival — [[R-ob-cmd-proc]] is already written that way and does not appear in HA's plan at all.
- **The shipped R01 check was reporting 144 hits, so nobody could have been running it.** Its `grep -v test` filters on the *path*, so every `#[cfg(test)]` block inside a production-named file (`sys_data.rs`, `description.rs`, `sections.rs`) counted as a violation. Excluding real test blocks brings it to **2**, both accounted for. A check nobody can act on is the same failure as a check that selects nothing — it just fails loudly instead of quietly.
- **⚠️ And the decisive one: this block does not load, and no rewriting of it will change that.** Warden's corpus is a **single directory** — `corpus_root()` resolves to `dans-anchor-system` and nothing else (`warden_root.py`; `$WARDEN_CORPUS_ROOT` / `corpus_root:` / vendored-copy, then a loud exit). `warden compile` scans only that root, and an anchor's `.anchor` `rules:` key — HA declares `rules: HA Track/HA Rules.md` — **is never read by the engine at all**. Verified after authoring: a fresh `warden compile` reports *"617 rules from 122 rulesets / 121 files"* and `~/.warden/rules-ir.json` contains **zero** `R-ha-*` rules, with `hooks-ir.json` installing no `write:rust` hook. So the [[DAS Decisions]] companion convention — *"the `# RULESET` goes in the same file, directly after the Decisions section"* — is **unreachable for any anchor whose docs live outside the corpus repo**, which is every project anchor in the vault. Until that is resolved ([[HA Backlog#^T285|T285]] Q1), **read the three rules below as documentation, not as enforcement.**
- **Brace-counting to find those test blocks is itself a trap.** A plain `count("{")` counts the braces inside `format!("{}", x)`, so the depth drifts and a test module reads as closed hundreds of lines early — which is exactly how the first measurement pass reported test-only `fs::write` calls in `sections.rs` as production violations. String and comment stripping is load-bearing, not tidiness.

### RULE R-ha-01 — Production file writes go through `write_if_changed` (checked)
when:: write:rust

*implements [[HA Rules#D07|D07]]*

Every production write of file content goes through `crate::utils::write_str_if_changed()` or `write_if_changed()`. A bare `fs::write` / `std::fs::write` in production code is a violation, because HA's architecture is filesystem-event-driven end to end: an unconditional rewrite of unchanged content emits a watcher event, which triggers a rebuild, which writes more unchanged files.

**Check pattern:** scan each `.rs` file for `\bfs::write\b` on lines that are neither inside a `#[cfg(test)]` item nor inside a string literal or comment. Allowed sites are the documented exceptions — `process_lock.rs` (EX001), `execution_server_management.rs` (EX002), the `write_if_changed` implementation itself (EX005) — plus a write whose target is a fresh temp path that is then renamed, which is the atomic-write pattern and cannot echo.

**Measured 2026-08-11 — 2 sites, 0 violations.** `core/data/sys_data.rs:650` writes the `commands.txt.missing` backup marker, already carried as EX003. `test_support/config_env.rs:118` writes a temp file it then renames — the atomic-write shape, and its own comment says so. The rule passes today, which is what makes it worth installing: it is a ratchet, not a cleanup task.

### RULE R-ha-02 — Diagnostic output goes through the logging layer (checked)
when:: write:rust

*implements [[HA Rules#D08|D08]]*

`println!` / `eprintln!` belong only to code whose contract is "produces terminal output". Everything else — GUI processes, background services, library code — calls `crate::utils::log`, `detailed_log`, or `log_error`. A `println!` in the popup, the supervisor, or the installer writes to a terminal nobody is attached to; it does nothing but convince the developer they instrumented something.

**Check pattern:** scan each `.rs` file for `println!` / `eprintln!` on lines outside `#[cfg(test)]`, and outside string literals and comments. **The allowlist is by declared site, not by path** — see the measurement below for why the path form does not work.

**Measured 2026-08-11 — 18 sites in 3 functions, 0 violations, and the path-based allowlist fails.** The obvious allowlist (`ha.rs`, `cmd.rs`, `cli/`, `bin/`, `execution_server.rs` — the vocabulary `CLAUDE.md` uses) misses every remaining site, because all three are console-contract functions that live outside a CLI folder: `utils/logging.rs` § `print` / `print_and_log` (2) are *the sanctioned console primitives themselves*, standing to this rule exactly as `write_if_changed` stands to R-ha-01; `systems/grabber.rs` § `grab_debug` (10) is documented "Debug function for CLI testing and rule development"; `utils/subprocess.rs` § `show_process_status` (6) is a process-monitor dump. Red-checked so the allowlist is not vacuous: with it removed the same scan reports **41** sites, so it is doing real work rather than matching everything.

### RULE R-ha-03 — Release binaries are built only through `just` (checked)
when:: tool:pre:Bash

*implements [[HA Rules#D09|D09]]*

A bare `cargo build --release` (or any bare `cargo` subcommand that relinks `target/release/`) is forbidden. `just build` sets `BUILT_WITH_JUST=1` at compile time, signs the output, and refreshes the app-bundle symlinks; a raw cargo relink silently strips the signature and the marker, so the running app fails its own startup `build_verification` check and stays broken until the next `just build`. `just cargo <args>` exists for the one-off cases and re-signs even when cargo itself fails.

**This is a moment rule, not a file rule** — it fires on `tool:pre:Bash` against the command string, because the failure is an action taken, not a state on disk. No `where::` selector can express it, which is the second reason the three D-records could not simply become file-glob rules.

**Check pattern:** a Bash command matching `\bcargo\s+(build|test|clippy|check|run)\b` that is not prefixed by `just` and not already inside a `just` recipe. **Enforcement today** is the compile-time stamp in `build.rs` plus the runtime assertion in `src/utils/build_verification.rs`; this rule moves the catch earlier, to before the command runs rather than after the app is already unsigned.
