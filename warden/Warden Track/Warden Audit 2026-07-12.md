:>> [[DAS]] → [[WARD]] → [[Warden Track]] → [Warden Audit 2026-07-12](hook://p/Warden%20Audit%202026-07-12)
# Warden Audit 2026-07-12

Adversarial spec-vs-code latent-bug audit of the live-wired Warden engine (Fable recipe: build the behavioral model from the design docs, trace the engine against it, construct concrete breaking inputs, verify each by code-trace or executed probe). Read-only. Complements the 2026-07-06 register ([[F232 — Latent-bug audit 2026-07-06 — findings register|F232]]) — every finding here is new to that register or a gap its fixes left open.

## TLDR

**7 findings** — 5 CONFIRMED, 2 PLAUSIBLE.

- **silent-failure: 5** (W1 dropped rules, W2 stale-path inertia, W3 daemon stale-socket loop, W4 veto truncation, W5 dead `if::` guard)
- **data-loss / concurrency: 1** (W6 unsynchronized store under the new threading)
- **wrong-block: 1** (W7 non-atomic reload swap)

Top 3:

1. **W1 — Rules authored in the currently-documented field style (`when::` on its own line, no heading paren) are silently dropped by the compiler.** The four `R-fct-claude-*` CLAUDE.md-governance rules and seven `R-fex-*` example rules are **absent from the live IR** — the `_RULE_RE` regex requires a trailing `(...)` the current spec doesn't mandate. CONFIRMED.
2. **W2 — A repo move/rename silently disables the entire Python-body + doc-fire surface with no self-check.** `daemon.cmd`, the `settings.json` binary path, and the IR `root` are absolute-path snapshots; after a move every veto and every doc-fire fails-open, symptom-free but for a 2 s stall per `tool:pre`. This is the exact live-armed form of the known ob-skills→dans-anchor-system incident. CONFIRMED.
3. **W3 — A corpus load failure crashes the daemon *after* it binds the socket but *before* the `try/finally`, leaving a stale `daemon.sock` + `daemon.pid`.** Every subsequent hook then spawns→crashes→retries for ~2 s forever, until a manual recompile. CONFIRMED.

## Fix status

All seven findings fixed 2026-07-12, in two passes (W1/W3 first; W2/W4/W5/W6/W7 second). Every fix carries a regression test; the engine suites + cargo tests are green.

- **W1 — FIXED** (first pass) — `_RULE_RE` paren made optional; malformed headings warn. Tests: `test_paren_less_rule_heading`, `test_malformed_rule_heading_warns`.
- **W2 — FIXED** — stale-path self-check (`warden_hook._stale_paths` / `hook.rs stale_paths`): dead IR `root` / `daemon.cmd` target → stderr + hook.log warning on every hook fire, an agent-visible steer at `session:start`, daemon-start warning (daemon stays up — fail-open), `spawn_daemon` fast-fails on a dead script (no more 2 s stall per call), and `warden status` reports all three staleness classes incl. a dead installed hook command. Tests: `test_stale_paths_surfaced`, `test_stale_root_loud_but_up`, `daemon_cmd_script_parsing` (cargo).
- **W3 — FIXED** (first pass) — socket/pid cleanup owns the corpus load. Test: `test_corpus_load_failure_no_stray_socket`.
- **W4 — FIXED** — daemon read cap raised 4 MB → 64 MB; a capped newline-less request now raises `RequestTooLarge` → explicit `ok:false` error response + hook.log line, instead of parsing truncated bytes to `{}`; the Rust client logs any non-ok daemon response at fire_rules and doc-fire (fail-open, but never silent). Test: `test_large_request_not_truncated`.
- **W5 — FIXED** — synthesised guards bind the full documented environment (`event`/`anchor`/`git`/`re`/`json`/`today`/`now` alongside `file`/`agent`), and compile warns when an `if::` references a name outside it. Test: `test_synth_guard_full_env`. The new warning immediately surfaced a live instance: `R-fex-bundle-02` (`if:: fex_bundle.manifest_count(file) != 1`, FEX Bundle.md) references an unbound `fex_bundle` — that rule can never fire; needs an authoring fix.
- **W6 — FIXED** — `RevalStore` load-mutate-replace and the `store()` singleton are lock-guarded; `ask_oracle`'s cache write is merge-under-lock + tmp/`os.replace`. Tests: `test_store_thread_safety`, `test_oracle_cache_concurrent`.
- **W7 — FIXED** — `Corpus` holds one `(ir, module)` tuple; readers take `snapshot()` (one reference grab), `_fire_rules` snapshots once per request. Test: `test_corpus_snapshot_pair_consistency`.

Adjacent repairs made in passing (pre-existing F229-rename fallout, verified present at pristine HEAD): `test_warden_fire.py`'s stale `FCT Track/FCT Query.md` path → `facets/DAS Query.md`; `warden_docfire`'s `{ANCHOR}` display token and `test_warden_docfire`'s fixture `where::` lowercased to the MS-1 `{anchor}` vocabulary. Still red and deliberately untouched: `test_warden_docfire.test_signature_matches_audit_plan` — the blessed golden corpus pre-dates R-query-16, whose `check:: queries_banner_form` has no checker implementation (every queries case gains an `error` row); re-bless only after ruling on that checker.

---

## W1 · Field-style RULE headings are silently dropped by the compiler

**Hypothesis.** A rule authored in the style the current spec documents — `### RULE R-slug-NN — name` with `when::`/`if::` as **field lines** below the heading and **no trailing paren** — is never parsed as a rule, so it silently vanishes from the corpus. It looks adopted; it does nothing.

**Breaking sequence (live, not hypothetical).** `facets/DAS Claude.md` authors four such rules (`R-fct-claude-01..04`, each `when:: write:markdown` + an `if::`, enforcing CLAUDE.md location/shape). `examples/FEX Repo/*` authors seven more (`R-fex-pin-*`, `R-fex-bundle-*`, `R-fex-manifest-*`). None carry a heading paren.

**Evidence.**
- `warden_compile.py:47` — `_RULE_RE = re.compile(r"^(#+)\s+RULE\s+(R-[\w-]+-\d+)\s+[—-]\s+(.*?)\s*\((.*?)\)\s*$")`. The trailing `\((.*?)\)\s*$` makes a **paren mandatory**.
- `warden_compile.py:213` — `rule_idxs = [j for j, ln in enumerate(block) if not bmask[j] and _RULE_RE.match(ln)]`. A paren-less heading never enters `rule_idxs`, so the rule (and its `when::`/`if::`/body) is never collected.
- Every rule that *does* reach the live IR carries a paren: `### RULE R-query-14 — … (when:: skill:post:audit-q)`, `### RULE R-pathguard-01 — … (when:: tool:pre:Edit)`. The kept-vs-dropped split is exactly paren-vs-no-paren.
- Executed probe: all of `R-fct-claude-01..04`, `R-fex-pin-01`, `R-fex-manifest-01` return `in ir["rules"] == False`; trait `fct-claude` is absent from `ir["traits"]`. A corpus walk finds **11 unfenced `RULE R-…` headings that fail `_RULE_RE`**, all field-style.
- The documented format ([[Warden Rule]] § The rule) lists the heading as `<H> RULE R-<slug>-NN` with `— <short name>` optional and `when::`/`if::` as **fields** — no paren in the grammar. So rules written to the current spec are the ones that disappear; the paren is a leftover F180 executable-form requirement the parser never relaxed.

**Severity:** silent-failure (governance rules that appear present never fire). **Confidence:** CONFIRMED.

**Fix direction.** Make the heading paren optional in `_RULE_RE` (match `R-<slug>-NN` with an optional `— name` and an optional `(...)` tail); a rule with no paren simply has no tier/inline-moment and takes its `when::`/`if::` from field lines, which the body-field loop already parses. Add a compile-time warning when an unfenced `RULE R-…` line is seen but not collected.

## W2 · A repo move/rename silently disables the Python-body + doc-fire surface — no self-check

**Hypothesis.** Warden pins its own machinery to absolute paths captured at `warden compile` / `warden install` time. Move or rename the repo and, until both are re-run, every Python-bodied veto and every markdown doc-fire silently no-ops — the same failure that already happened once (MEMORY: "Recompile Warden after any repo rename/move").

**Breaking sequence.** Rename `dans-anchor-system/` (or any ancestor). Then: (a) `~/.warden/daemon.cmd` still holds `python3 /old/path/warden_daemon.py --serve`; (b) `~/.claude/settings.json` still holds `'/old/path/rs/target/release/warden-rs' hook`; (c) `~/.warden/rules-ir.json` `root` still points at the old tree. No recompile is triggered by the move.

**Evidence.**
- `~/.warden/daemon.cmd` verbatim: `python3 '/Users/oblinger/ob/kmr/SYS/Bespoke/Skill Agent/dans-anchor-system/warden/engine/warden_daemon.py' --serve` — an absolute snapshot written by `warden:96` `_write_daemon_cmd`.
- `settings.json` PreToolUse entries invoke `'/…/dans-anchor-system/warden/rs/target/release/warden-rs' hook` — absolute, written by `warden.py` `RUST_HOOK_CMD` (`warden:43-44`).
- `hook.rs:355-378` `spawn_daemon` runs `daemon.cmd` through `/bin/sh -c` with `stderr` to `/dev/null`; a bad path fails **silently** — `daemon_request` returns `None`, "owed steers skipped this call" (`hook.rs:444`). All 5 live veto rules (`R-pathguard-01..04`, `R-ob-remote-ops-01`) and `R-query-14` are `body_py` (probe-confirmed), so all of them ride this path.
- A missing `warden-rs` binary makes Claude Code's hook command itself fail; a failed hook is non-blocking (fail-open), so the veto surface goes inert with no user-visible error.
- Executed sandbox repro: with a `daemon.cmd` pointing at a non-existent command, a `PreToolUse:Bash` hook took **2.076 s** and logged `daemon MISS — spawned but not answering in time; owed steers skipped this call`; a `write:markdown` PostToolUse took **20.079 s** (the doc-fire's 20 s daemon timeout) and also silently produced no audit steer.
- The compiler has a drift check for *moment deliverability* (`warden.py` `_warn_undeliverable`, F232 D2) but **nothing validates that the absolute paths it wrote still resolve.**

**Severity:** silent-failure (whole veto + doc-fire surface inert; per-call 2–20 s latency tax the only symptom). **Confidence:** CONFIRMED.

**Fix direction.** At hook entry (or daemon spawn) verify `daemon.cmd`'s target file and the `warden-rs` path exist; if not, log a loud one-line "Warden stale — run `warden install` after a move" and, ideally, self-trigger a recompile when the IR `root` ≠ the binary's own resolved repo root. A cheap `SessionStart` self-check is the natural home.

## W3 · Corpus load failure leaves a stale socket + pid → self-perpetuating spawn-crash loop

**Hypothesis.** If `Corpus(home)` fails to construct (corrupt/half-written emitted module or IR), the daemon dies *after* binding the socket and writing the pid file but *before* entering the `try/finally` that cleans them up — leaving a stale `daemon.sock` that makes every future hook spawn a daemon that also crashes.

**Evidence.**
- `warden_daemon.py:275-295` — `srv.bind`, `srv.listen(8)`, `pid_path().write_text(...)`, then **`corpus = Corpus(home)`** at line 294. The `try:` that owns the cleanup `finally` (`sock_p.unlink`, `pid_path().unlink`) only opens at line 303, *after* the Corpus line.
- `Corpus.__init__` → `reload` → `wf.load_compiled` → `spec.loader.exec_module` (`warden_fire.py:53`). A `SyntaxError`/`ImportError` in the emitted `rules_all.py` propagates straight out of line 294 — the `finally` never runs, so the bound socket file and pid file survive the crash.
- Executed repro: appended `def broken(:` to a sandbox `rules_all.py`; `warden_daemon --serve` printed `SyntaxError: invalid syntax` and exited **leaving `daemon.sock` + `daemon.pid`**. A subsequent `warden-rs hook` against that home stalled ~2 s (`spawn_daemon` re-launches the crasher, retry loop exhausts the timeout) — and would do so on *every* call until a good recompile.
- F232 B6's stale-socket probe (retry-before-unlink) and B5's atomic writes reduce the *odds* of a bad artifact, but neither closes this window: any load-time exception (a compiler bug emitting invalid Python, an IR the deserializer rejects) reopens it, and the stale socket then defeats B6's own liveness probe on the next spawn.

**Severity:** silent-failure (persistent; recovers only on manual recompile). **Confidence:** CONFIRMED.

**Fix direction.** Build the `Corpus` *inside* a `try/finally` (or wrap the whole post-bind body) so any load failure unlinks the socket + pid before exit; log the load error explicitly rather than dying bare. Consider building the Corpus *before* binding the socket, so a bad corpus never claims the socket at all.

## W4 · Large Write/Edit tool_input truncates the daemon request → veto silently skipped

**Hypothesis.** A tool call whose serialized request exceeds the daemon's 4 MB read cap is truncated, fails JSON parse, and the owed `deny`/steer is silently dropped — the guarded write proceeds un-vetoed.

**Breaking sequence.** A `Write`/`Edit` whose `tool_input` (e.g. `content`, or a large `old_string`/`new_string`) pushes the request line past 4 MB. `hook.rs` forwards the full `tool_input` to the daemon (`hook.rs:566-573`).

**Evidence.**
- `warden_daemon.py:213-220` — `_recv_line(conn, limit=4*1024*1024)` stops reading at 4 MB and returns `buf.split(b"\n",1)[0]`; a request longer than that is truncated mid-string.
- `_serve_conn:230-234` — `json.loads(line)` on the truncated bytes raises `ValueError`, caught → `req = {}` → `handle` returns `{"ok": false, "error": "unknown op ''"}`.
- `hook.rs:575-578` — the client only harvests `steers_by_rule` when `resp["ok"] == true`; on `ok:false` the owed deny is simply absent, and the fire loop emits nothing for that rule. Fail-open ⇒ the `Write` lands.
- Executed unit probe: a 5 MB `fire_rules` request through `warden_daemon._recv_line` received **4 194 304 bytes** (exactly 4 MB) and `json.loads` raised `Unterminated string` → `req = {}`. The pathguard denies key off filename (`R-pathguard-03` denies wholesale `Write` to `* Backlog.md` / `* queries.md`), so a large enough write to such a file bypasses the guard.

**Severity:** silent-failure / wrong-block (veto bypass on large payloads). **Confidence:** CONFIRMED (truncation + parse-fail path executed; end-to-end bypass is the direct consequence).

**Fix direction.** Raise/remove the request cap for `fire_rules` (or length-prefix the framing so the daemon reads the declared length), and — since a deny that can't be evaluated is a *fail-open* — treat a parse failure at a `tool:pre` veto request as a logged hard error rather than silent `ok:false`. At minimum the Rust client should distinguish "daemon said no rules" from "daemon errored" and log the latter.

## W5 · A synthesized `if::` guard sees only `file` and `agent` — spec-legal `event`/`anchor`/`git`/`re` usage silently evaluates False

**Hypothesis.** A non-vocabulary `if::` compiles to a synthesized `guard()` whose scope injects only `file` and `agent`. Any `if::` using the rest of the documented interpretation environment (`event`, `anchor`, `git`, `re`, `json`, `today`) raises `NameError`, is swallowed to `False`, and the rule **never fires** — a silent deny-bypass or lost steer.

**Breaking sequence.** Author the exact example [[Warden Semantics]] § `event` gives: `if:: event.target.size > 2_000_000`. Or any `if:: re.search(...)`, `if:: git.is_dirty`, `if:: anchor.slug == 'X'` that isn't a `file.`-only expression.

**Evidence.**
- `warden_compile.py:416-439` `synth_guard_src` emits:
  `def guard(ctx): file = getattr(ctx,'file',None); agent = getattr(ctx,'agent',None); try: return bool(<conj>) except Exception: return False`.
  Only `file` and `agent` are bound; the emitted module has no module-level `import re`/`json` (the live `rules_all.py` does its imports *inside* bodies), and `event`/`anchor`/`git`/`today`/`now` are never injected.
- The `except Exception: return False` (line 437-439) converts the resulting `NameError` into a silent non-fire.
- Executed probe: `synth_guard_src` for `if:: event.target is not None` returned a guard that yields **`False`** even with `ctx.event.target` set (the name `event` is unbound in the guard scope, not read from `ctx`); likewise `if:: re.search(r'x', file.text)` returned `False`.
- Contrast: [[Warden Semantics]] § The interpretation environment explicitly lists `event`, `anchor`, `git`, `re`, `json`, `datetime`, `today`, `now` as in-scope for `if::`. The synth guard honors only two of them.
- Currently **zero `guard_py` rules** exist in the live IR (probe-confirmed — all live logic is `body_py`, which *does* receive full `ctx`), so this is **latent**. But it is armed: the first rule authored with a residual `if::` per the documented surface silently dies, and the spec's own `event.target.size` example is one such rule.

**Severity:** silent-failure (rule inert; a deny rule so authored is a silent veto bypass). **Confidence:** CONFIRMED mechanism / LATENT trigger.

**Fix direction.** Bind the full lazy `ctx` surface into the synthesized guard (`event = getattr(ctx,'event',None)`, `anchor`, `git`, plus `import re, json` and `today`/`now`), mirroring what `body_py` rules already receive; and make a guard that *raises* a logged event, not a silent `False`, at least at compile-test time (a guard referencing an unbound name is an authoring error worth surfacing).

## W6 · RevalStore and oracle-cache are unsynchronized under the new thread-per-connection daemon

**Hypothesis.** F232 B1/T013 made the daemon thread-per-connection and lock-guarded `TURN_FIRED` and the session registry — but the F215 `RevalStore` and the F217 oracle cache are shared, mutable, non-atomic-at-the-dict-level, and got no lock. Concurrent handler threads racing `mark_evaluated` (or `ask_oracle`) lose writes.

**Evidence.**
- `warden_reval.py:47-107` — `RevalStore` is a process-wide singleton (`store()`, line 112-117) with `self._data: dict` mutated by `mark_evaluated` (read-modify-`os.replace`) and `_load`. **No `threading.Lock` anywhere in the class.** Two threads firing file-bearing rules on different files each do `_load` → mutate `self._data` → rewrite the whole JSON; the second `os.replace` wins and drops the first thread's record (a lost `mark_evaluated` ⇒ that rule re-judges next time, or worse serves a stale verdict).
- `warden_agent.py:453-487` `ask_oracle` reads `oracle-cache.json`, mutates, and `write_text`s it with **no lock and no tmp+rename** — concurrent oracle calls last-writer-wins and can leave a partially-written cache (a later `json.loads` then silently resets the cache to `{}`, line 471-473).
- Contrast the guarded state: `_TURN_LOCK` (`warden_daemon.py:122`) and `_REGISTRY_LOCK` (`warden_agent.py:68`) were added for exactly this threading change; reval + oracle-cache were left out. F232 B8 flagged reval growth and the *cross-process* `warden fire` CLI clobber, but not the *intra-daemon* thread race the T013 fix introduced.
- Latent today: probe shows **zero `file_bearing` rules** and no `reval.json`/`oracle-cache.json` on this machine; materializes when a file-bearing or oracle rule is adopted.

**Severity:** data-loss / concurrency (lost verdict records, corrupt cache). **Confidence:** PLAUSIBLE (code-read; no live trigger — the stores are empty).

**Fix direction.** Give `RevalStore` a lock around load-mutate-write (or serialize marks through a single writer), and make `ask_oracle`'s cache write tmp+`os.replace` under a lock — the same treatment `TURN_FIRED`/registry already got.

## W7 · Corpus.reload swaps IR and module in two separate assignments — a reader can get a mismatched pair

**Hypothesis.** `Corpus.reload` does `self.ir, self.module = load_compiled(...)`, which is two attribute stores. A handler thread that reads `corpus.ir` and `corpus.module` at different moments during a concurrent reload can pair a *new* IR with an *old* module (or vice versa) — the intra-process analogue of F232 B5's new-IR/old-module mismatch.

**Evidence.**
- `warden_daemon.py:104-107` — `reload` is lock-guarded, but the tuple assignment `self.ir, self.module = wf.load_compiled(...)` is two bytecode `STORE_ATTR`s; a reader is not holding `_lock`.
- `_fire_rules` reads `corpus.ir` (line 149, 157, 168) and `corpus.module` (line 170) as **separate** accesses passed together to `wf.fire`; `handle` calls `corpus.fresh()` (line 187) which may `reload` on another thread between them.
- The docstring (`warden_daemon.py:85-87`) claims "readers take `self.ir`/`self.module` references, which swap atomically under the GIL" — but that guarantee holds per-attribute, not across the pair. A rule id present in the new IR but keyed to a `body_py` name that only exists in the new module (or removed from the old) can miss its function (`getattr(module, name)` → `AttributeError`, caught by `_safe_handle` → the veto silently doesn't fire).
- Reload only happens on recompile, so the window is narrow → rare.

**Severity:** wrong-block / silent-failure during the reload window. **Confidence:** PLAUSIBLE (code-read; timing-dependent).

**Fix direction.** Snapshot the `(ir, module)` pair atomically — read both under `_lock`, or store them in one container object the reader grabs by a single reference (`self._state = (ir, module)`), so a reader always sees a consistent pair.

---

## Audited surface

**Read in full (spec):** Warden Semantics, Warden Runtime, Warden Architecture, Warden Rule, Warden Interface, Warden Events; the F232 prior-audit register.

**Read in full (code):** `rs/src/hook.rs`, `rs/src/lib.rs`; `engine/warden_hook.py`, `warden_fire.py`, `warden_daemon.py`, `warden_reval.py`, `warden_agent.py`, `warden_compile.py`, `warden_scan.py`, `warden_engine.py`, `warden_docfire.py`, and the `warden` CLI.

**Probed read-only (live state):** `~/.warden/` layout (`daemon.cmd`, `daemon.pid`, `rules-ir.json`, `rules_all.py`), the compiled IR (moments, traits, per-rule rows, `base_traits`), `~/.claude/settings.json` hook wiring, the emitted veto bodies. Executed pure-logic probes in `/private/tmp` sandboxes only (broken-`daemon.cmd` stall timing, corrupt-module daemon crash, 4 MB request truncation, synth-guard NameError, corpus RULE-heading regex sweep). **No** live daemon/socket/settings/`~/.warden` file was modified; the daemon was never restarted, killed, or recompiled.

**NOT covered (out of scope or not reached):**
- `audit-plan.py` and its checker/fixer registry + never-delete floor (lives in the sibling `skills/audit/` tree) — the doc-fire delegates fix execution to it; its safety floor was not re-audited here.
- The Rust `fire_plan` ↔ Python `fire_records` **differential parity** beyond spot-reads — F232 C-cluster covered it; I did not re-run the differential harness.
- `warden_docfire`'s `_match_file_glob`/selector performance rewrite (F232 B3) beyond confirming the mtime cache exists.
- The full test suite (`test_warden_*.py`) was read only for the daemon/hook/reval areas, not exhaustively.
- Content-kind sniffing correctness, the F216 agent-state classifier's heuristic accuracy, and the timer/M8 reserved surfaces (not yet implemented).
- **Previously-documented, reconfirmed in passing (not re-counted):** the `DENY: ` in-band sentinel is still unvalidated (F232 D1 — any steer beginning `DENY: ` at `tool:pre` becomes a real veto); Python-bodied deny remains best-effort when the daemon is cold (F232 B2 / [[Warden Interface]] § Non-guarantees).

This audit is a targeted adversarial pass, not full coverage — absence of a finding in an unread area is not evidence of correctness.
