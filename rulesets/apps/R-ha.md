# RULESET R-ha
include::
where:: `**/HookAnchorApp/**`
description:: HookAnchor's own enforceable constraints — the write-amplification gate, the print-vs-log boundary, and the build-tool gate. Authored 2026-08-11 against checks that were run, not guessed.

**Registered 2026-09-01 per [[Tink Backlog#^T362|T362]].** This block lived in `HA Rules.md` from 2026-08-11 and never compiled: Warden's corpus is a single directory and an anchor's `.anchor` `rules:` key is not read by the engine. It now lives here, in the enumerated git-tracked corpus, and is activated by the `ha` trait on HookAnchor's `.anchor` — `warden compile` derives the trait name from the ruleset name. `HA Rules.md` links here and holds no copy.

| Table of Contents |  |
|---|---|
|    [[#RULE R-ha-01 — Production file writes go through `write_if_changed` (checked)]] |  |
|    [[#RULE R-ha-02 — Diagnostic output goes through the logging layer (checked)]] |  |
|    [[#RULE R-ha-03 — Release binaries are built only through `just` (checked)]] |  |

**The header binding is scoped, not `always`.** As authored it read `` where:: `always` `` with a ruleset-level `` when:: `write:rust` ``, which would have fired these HookAnchor-specific conventions at every `.rs` write anywhere on the machine — docket, SVP, any repo — and that is the shape that cost TINK 140 wasted LLM calls via `R-mac`. The glob confines the set to HookAnchor's own tree, and each rule below carries its own moment: `write:rust` for the two file rules, `tool:pre:Bash` for the build-tool gate, which is an action and has no file to select.

**Every rule below was measured against the real tree before it was written, and the measuring is the point.** This block sat deliberately unwritten from 2026-08-08 because a selector that reaches nothing is silently inert while reading as enforced. Three findings came out of finally doing the measurement, and they shape the whole ruleset:

- **A `where::` file glob cannot reach a `.rs` file at all.** The audit sweep's scope enumerator is `.md`-only (`audit-plan.py` § `enumerate_scope`, anchor mode: `target.rglob("*.md")`), and its scope is rooted at the anchor folder — which for HA is the vault directory, not `~/ob/grove/HookAnchorApp/` where the source actually lives. Measured directly: an anchor-mode plan over `prj/Hook Anchor` produces **94 rules, of which 0 have a `.rs` target**. So HA's code rules are bound to the **`when:: write:rust` moment** instead, which the hook derives from the written file's extension (`warden_hook.py` § `_CONTENT_KIND`) and therefore reaches source wherever it lives. Any future HA rule phrased as `` where:: `file:{anchor}/**/*.rs` `` is dead on arrival — [[R-ob-cmd-proc]] is already written that way and does not appear in HA's plan at all.
- **The shipped R01 check was reporting 144 hits, so nobody could have been running it.** Its `grep -v test` filters on the *path*, so every `#[cfg(test)]` block inside a production-named file (`sys_data.rs`, `description.rs`, `sections.rs`) counted as a violation. Excluding real test blocks brings it to **2**, both accounted for. A check nobody can act on is the same failure as a check that selects nothing — it just fails loudly instead of quietly.
- **⚠️ And the decisive one: this block does not load, and no rewriting of it will change that.** Warden's corpus is a **single directory** — `corpus_root()` resolves to `dans-anchor-system` and nothing else (`warden_root.py`; `$WARDEN_CORPUS_ROOT` / `corpus_root:` / vendored-copy, then a loud exit). `warden compile` scans only that root, and an anchor's `.anchor` `rules:` key — HA declares `rules: HA Track/HA Rules.md` — **is never read by the engine at all**. Verified after authoring: a fresh `warden compile` reports *"617 rules from 122 rulesets / 121 files"* and `~/.warden/rules-ir.json` contains **zero** `R-ha-*` rules, with `hooks-ir.json` installing no `write:rust` hook. So the [[DAS Decisions]] companion convention — *"the `# RULESET` goes in the same file, directly after the Decisions section"* — is **unreachable for any anchor whose docs live outside the corpus repo**, which is every project anchor in the vault. **Resolved by moving the block here rather than by changing the engine** (2026-09-01): the three rules now compile, bind to their moments and fire — see the T346 note below for the probe results. The finding stands as a fact about `rules:` and about that convention; the sentence that used to end this bullet, *"read the three rules below as documentation, not as enforcement"*, no longer describes them and is struck rather than quietly deleted, because a rule doc that misreports its own liveness is the exact failure this ruleset was written about.
- **Brace-counting to find those test blocks is itself a trap.** A plain `count("{")` counts the braces inside `format!("{}", x)`, so the depth drifts and a test module reads as closed hundreds of lines early — which is exactly how the first measurement pass reported test-only `fs::write` calls in `sections.rs` as production violations. String and comment stripping is load-bearing, not tidiness.

> **All three rules now DELIVER — 2026-09-01, [[HA Backlog#^T346|HA T346]].** Registering the set was not the same as arming it: as registered, the three rules carried no `if::`, no `check::` and no body, so `fire_records` considered them and produced zero steers however they were scoped ([[Tink]], verified against the engine). Each now carries an authored `def body(ctx)`. **Every one is ADVISORY — a returned string, never a `deny::`** — because these are conventions worth a reminder, not acts worth blocking, and an over-eager deny in a rule that fires on every Rust write would be felt immediately by every concurrent session.
>
> **The bodies were validated against this document's own recorded measurements, not against a reading of the engine.** The 2026-08-11 hand measurements below are a test oracle, and the scanner reproduces all four figures exactly: R-ha-01 → **2 sites, 0 violations**; R-ha-02 → **41 sites** total, **18** left by the path-only allowlist (`grabber.rs` 10, `logging.rs` 2, `subprocess.rs` 6 — the three functions named below), **0** after the declared-site allowlist. That the scanner independently reproduces a three-week-old hand count, down to the per-file split, is the evidence that it scans what the author scanned.
>
> **`check::` primitives were not an option** — they are wired for doc-rules only, so the R01/R02 scan logic had to be an authored body ([[Tink]], 2026-09-01). The string/comment stripper is duplicated into R-ha-02 by copy rather than imported, because rule bodies are sandboxed standalone; this is the [[R-state-region]]-03 precedent, which inlines its hash algorithm for the same reason. **If the stripper changes, change both.**
>
> **One deliberate narrowing.** R-ha-03's authored check pattern matches any `cargo (build|test|clippy|check|run)`, but only a **release** relink can strip the signature — a plain `cargo build` writes `target/debug` and cannot cause the failure the rule exists for. The body requires `--release` (or `--profile release`) and scopes to HookAnchor's tree. A rule that fires on builds that were never dangerous is read as noise, and then the one that mattered is ignored too.
>
> **`warden compile` warns permanently about R-ha-03, and the warning is a false positive — do not "fix" it.** It reads *"the ruleset-header `where::` is a doc-selector and does not scope this moment rule."* True as far as it goes: `tool:pre:Bash` carries no file, so no glob can scope it, and the scoping lives in the body (session cwd or the command naming HookAnchorApp) where the compiler cannot see it. Verified by the negative probe — the same `cargo build --release` run in `docket` is silent. The compiler looks only for a `where::` or an `if::`, so a rule scoped in python warns forever; [[R-commit-discipline]]-06 and [[R-query]]-14 sit in the same position for the same reason.
>
> **Still true and still worth knowing: `write:rust` only fires on Write/Edit tool events** (`hook.rs` `content_kind` on the extension). A Rust file written through a Bash heredoc raises no `write:` moment at all, so R-ha-01/-02 miss most bypass-mode writes. That is a coverage limit of the moment, not of these bodies.
>
> **Verified by committing the violation, in each rule's own shape — six probes, and the negatives are the ones that matter.** Positive: a `.rs` under `src/` and one at the repo root each drew both advisories, on the production line and **not** on the identical `fs::write` / `println!` inside the file's `#[cfg(test)]` block, and not on a string literal spelling `fs::write(path, x); println!(...)` — with `format!("{} {}", "{", "}")` planted inside the test module to try to drift the brace depth. `cargo build --release` in HookAnchor drew R-ha-03. **Negative:** the same two violations written into `docket/anchorage` drew **nothing** (firing HA's conventions at every `.rs` on the machine is the R-mac shape), `just cargo build --release` drew nothing (the sanctioned form is recognised), and `cargo build` without `--release` drew nothing (the narrowing above). Probes deleted; both repos clean.
>
> **⚠️ A per-rule `where::` takes ONE fnmatch pattern, and a comma list silently matches nothing.** The ruleset-**header** `where::` does accept a comma list with negation — [[R-exception-discipline]] ships `` `file:{anchor}/**/* Exceptions.md, !**/DAS *.md` `` — so the two fields look identical and behave differently. Measured here the hard way: setting the per-rule selector to `` `**/HookAnchorApp/**/*.rs, **/HookAnchorApp/*.rs` `` made both rules go silent on a file that had fired a minute earlier, with **no compile warning and no error** — just `considered, silent`. Filed for [[Tink]].
>
> **`0.0 ms` in `warden log` is how you tell a body never ran.** A rule whose python actually executes shows real time — `R-state-region-03` logs ~150 ms on a markdown write. `write:rust … 0.0 ms (considered, silent: R-ha-01, R-ha-02)` means the selector rejected the path before the interpreter was reached. That one number is what separated *"my scanner is wrong"* from *"my glob is wrong"*, and it is worth knowing before debugging any silent rule.
>
> **The original glob had a real gap: `` `**/HookAnchorApp/**/*.rs` `` cannot match a `.rs` at the repo root**, because the `**/` between the folder and the filename requires an intervening segment. That excluded `build.rs` — the file that sets `BUILT_WITH_JUST`, which is precisely what R-ha-03 exists to protect. The selector is now `` `**/HookAnchorApp/**` ``, which is sufficient rather than loose: `write:rust` already restricts the moment to Rust files, and each body re-checks the extension and the tree.

### RULE R-ha-01 — Production file writes go through `write_if_changed` (checked)
when:: write:rust
where:: `**/HookAnchorApp/**`

```python
def body(ctx):
    # F215: the compiler marks a rule file-bearing (and the engine binds
    # ctx.file) only when the source carries a literal `file.` reference —
    # keep the direct ctx.file.* accesses.
    if getattr(ctx, "file", None) is None:
        return []
    if not ctx.file.name.endswith(".rs") or not ctx.file.exists:
        return []
    path = "/" + ctx.file.path.lstrip("/")
    if "/HookAnchorApp/" not in path or "/target/" in path:
        return []
    # EX001 process_lock, EX002 execution_server_management, EX005 the
    # write_if_changed implementation itself, plus the two atomic
    # temp-then-rename sites — a write that is renamed cannot echo.
    for allowed in ("process_lock.rs", "execution_server_management.rs",
                    "utils/file_ops.rs", "test_support/config_env.rs",
                    "core/data/sys_data.rs"):
        if allowed in path:
            return []
    import re
    hits = _ha_scan(ctx.file.text, r"\bfs::write\b")
    if not hits:
        return []
    where = ", ".join("line %d" % n for n, _ in hits[:4])
    return ["[warden] R-ha-01 — bare `fs::write` in production code (%s). HookAnchor is "
            "filesystem-event-driven end to end: an unconditional rewrite of unchanged "
            "content emits a watcher event, which triggers a rebuild, which writes more "
            "unchanged files. Use `crate::utils::write_str_if_changed()` / "
            "`write_if_changed()`, or add a graded row to `HA Exceptions.md` if this is a "
            "documented site." % where]


# Shared with R-ha-02 by copy, not by import: rule bodies are sandboxed
# standalone (the R-state-region-03 precedent inlines its hash algorithm for the
# same reason). If this changes, change both.
def _ha_strip(text):
    """Blank out strings, char literals and comments, preserving offsets.

    Load-bearing, not tidiness: a plain brace count sees the braces inside
    `format!("{}", x)`, drifts, and closes a `#[cfg(test)]` module hundreds of
    lines early — which is exactly how the first hand measurement reported
    test-only `fs::write` calls in `sections.rs` as production violations.
    """
    import re
    out, i, n = [], 0, len(text)
    line_c = block_c = in_str = in_chr = False
    raw = None
    while i < n:
        c = text[i]
        nxt = text[i + 1] if i + 1 < n else ""
        if line_c:
            out.append(c if c == "\n" else " ")
            line_c = c != "\n" and line_c
            i += 1
            continue
        if block_c:
            if c == "*" and nxt == "/":
                block_c = False
                out.append("  ")
                i += 2
                continue
            out.append("\n" if c == "\n" else " ")
            i += 1
            continue
        if raw is not None:
            if c == '"' and text[i + 1:i + 1 + raw] == "#" * raw:
                out.append(" " * (1 + raw))
                i += 1 + raw
                raw = None
                continue
            out.append("\n" if c == "\n" else " ")
            i += 1
            continue
        if in_str or in_chr:
            q = '"' if in_str else "'"
            if c == "\\":
                out.append("  ")
                i += 2
                continue
            if c == q:
                in_str = in_chr = False
                out.append(" ")
                i += 1
                continue
            out.append("\n" if c == "\n" else " ")
            i += 1
            continue
        if c == "/" and nxt == "/":
            line_c = True
            out.append("  ")
            i += 2
            continue
        if c == "/" and nxt == "*":
            block_c = True
            out.append("  ")
            i += 2
            continue
        if c == "r" and nxt in ('"', "#"):
            m = re.match(r'r(#*)"', text[i:])
            if m:
                raw = len(m.group(1))
                out.append(" " * m.end())
                i += m.end()
                continue
        if c == '"':
            in_str = True
            out.append(" ")
            i += 1
            continue
        if c == "'" and re.match(r"'(\\.|[^\\'])'", text[i:]):
            in_chr = True          # a char literal; a lifetime `'a` is not
            out.append(" ")
            i += 1
            continue
        out.append(c)
        i += 1
    return "".join(out)


def _ha_scan(text, pattern):
    """(line_no, source) for each match outside `#[cfg(test)]`, strings, comments."""
    import re
    code = _ha_strip(text)
    spans = []
    for m in re.finditer(r"#\[cfg\(test\)\]", code):
        brace = code.find("{", m.end())
        if brace == -1:
            continue
        depth, j = 0, brace
        while j < len(code):
            if code[j] == "{":
                depth += 1
            elif code[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        spans.append((m.start(), j))
    lines = text.splitlines()
    out = []
    for m in re.finditer(pattern, code):
        if any(a <= m.start() <= b for a, b in spans):
            continue
        ln = code.count("\n", 0, m.start()) + 1
        out.append((ln, lines[ln - 1].strip() if ln <= len(lines) else ""))
    return out
```

*implements [[HA Rules#D07|D07]]*

Every production write of file content goes through `crate::utils::write_str_if_changed()` or `write_if_changed()`. A bare `fs::write` / `std::fs::write` in production code is a violation, because HA's architecture is filesystem-event-driven end to end: an unconditional rewrite of unchanged content emits a watcher event, which triggers a rebuild, which writes more unchanged files.

**Check pattern:** scan each `.rs` file for `\bfs::write\b` on lines that are neither inside a `#[cfg(test)]` item nor inside a string literal or comment. Allowed sites are the documented exceptions — `process_lock.rs` (EX001), `execution_server_management.rs` (EX002), the `write_if_changed` implementation itself (EX005) — plus a write whose target is a fresh temp path that is then renamed, which is the atomic-write pattern and cannot echo.

**Measured 2026-08-11 — 2 sites, 0 violations.** `core/data/sys_data.rs:650` writes the `commands.txt.missing` backup marker, already carried as EX003. `test_support/config_env.rs:118` writes a temp file it then renames — the atomic-write shape, and its own comment says so. The rule passes today, which is what makes it worth installing: it is a ratchet, not a cleanup task.

### RULE R-ha-02 — Diagnostic output goes through the logging layer (checked)
when:: write:rust
where:: `**/HookAnchorApp/**`

```python
def body(ctx):
    # F215 — keep the literal ctx.file.* accesses so the rule binds a file.
    if getattr(ctx, "file", None) is None:
        return []
    if not ctx.file.name.endswith(".rs") or not ctx.file.exists:
        return []
    path = "/" + ctx.file.path.lstrip("/")
    if "/HookAnchorApp/" not in path or "/target/" in path:
        return []
    # The allowlist is by DECLARED SITE, not by path, and the three entries
    # after the CLI group are why. Each is a console-contract function living
    # outside any cli/ folder: utils/logging.rs `print`/`print_and_log` (2) are
    # the sanctioned console primitives themselves, standing to this rule as
    # write_if_changed stands to R-ha-01; systems/grabber.rs `grab_debug` (10)
    # is documented "Debug function for CLI testing and rule development";
    # utils/subprocess.rs `show_process_status` (6) is a process-monitor dump.
    # The path-only allowlist leaves exactly those 18 sites; with the whole
    # allowlist removed the scan reports 41, so it is doing real work rather
    # than matching everything (red-checked 2026-08-11, reproduced 2026-09-01).
    for allowed in ("src/ha.rs", "src/cmd.rs", "/cli/", "/bin/",
                    "execution_server.rs", "utils/logging.rs",
                    "systems/grabber.rs", "utils/subprocess.rs"):
        if allowed in path:
            return []
    hits = _ha_scan(ctx.file.text, r"\be?println!")
    if not hits:
        return []
    where = ", ".join("line %d" % n for n, _ in hits[:4])
    return ["[warden] R-ha-02 — `println!`/`eprintln!` outside a console-contract site (%s). "
            "The user cannot see terminal output from the popup, the supervisor, the "
            "installer or any background service, so this instruments nothing. Use "
            "`crate::utils::log` / `detailed_log` / `log_error` — they reach "
            "`~/.config/hookanchor/anchor.log`, which is where you will actually read it." % where]
```

*implements [[HA Rules#D08|D08]]*

`println!` / `eprintln!` belong only to code whose contract is "produces terminal output". Everything else — GUI processes, background services, library code — calls `crate::utils::log`, `detailed_log`, or `log_error`. A `println!` in the popup, the supervisor, or the installer writes to a terminal nobody is attached to; it does nothing but convince the developer they instrumented something.

**Check pattern:** scan each `.rs` file for `println!` / `eprintln!` on lines outside `#[cfg(test)]`, and outside string literals and comments. **The allowlist is by declared site, not by path** — see the measurement below for why the path form does not work.

**Measured 2026-08-11 — 18 sites in 3 functions, 0 violations, and the path-based allowlist fails.** The obvious allowlist (`ha.rs`, `cmd.rs`, `cli/`, `bin/`, `execution_server.rs` — the vocabulary `CLAUDE.md` uses) misses every remaining site, because all three are console-contract functions that live outside a CLI folder: `utils/logging.rs` § `print` / `print_and_log` (2) are *the sanctioned console primitives themselves*, standing to this rule exactly as `write_if_changed` stands to R-ha-01; `systems/grabber.rs` § `grab_debug` (10) is documented "Debug function for CLI testing and rule development"; `utils/subprocess.rs` § `show_process_status` (6) is a process-monitor dump. Red-checked so the allowlist is not vacuous: with it removed the same scan reports **41** sites, so it is doing real work rather than matching everything.

### RULE R-ha-03 — Release binaries are built only through `just` (checked)
when:: tool:pre:Bash

```python
def body(ctx):
    import shlex
    ev = getattr(ctx, "event", None)
    inp = getattr(ev, "input", None) or {}
    cmd = inp.get("command") or ""
    if "cargo" not in cmd:
        return []

    # Only HookAnchor's tree. A release build in docket/anchorage or any other
    # repo is fine — `just build`'s stamp-and-sign contract is HA's alone, and a
    # rule that fired on every repo's cargo would be the R-mac shape that cost
    # TINK 140 wasted calls.
    sess = getattr(getattr(ctx, "agent", None), "_session", None) or {}
    cwd = sess.get("cwd") or ""
    if "HookAnchorApp" not in cwd and "HookAnchorApp" not in cmd:
        return []

    try:
        words = shlex.split(cmd)
    except ValueError:
        # T662 — the naive `cmd.split()` this replaced shreds every QUOTED
        # ARGUMENT CONTAINING A SPACE, so an unbalanced quote anywhere in the
        # line (an apostrophe in a message is enough) turned `open -a "Google
        # Chrome Beta"` into the token `"Google` and this rule stopped seeing
        # a browser. `posix=False` tolerates the unbalanced quote and keeps
        # quoted tokens whole; the quotes it leaves on are stripped here.
        # Found on R-ob-commons-01 (T663), where the same fallback let a real
        # commons commit through, and swept to its three siblings.
        words = [w[1:-1] if len(w) >= 2 and w[0] == w[-1] and w[0] in "\"'" else w
                 for w in shlex.split(cmd, posix=False)]

    # `cargo` in COMMAND position, and not the sanctioned `just cargo …` form.
    # Never `echo "cargo build"`, never a path containing the word.
    RELINKS = {"build", "test", "clippy", "check", "run", "bench"}
    for k, w in enumerate(words):
        if not (w == "cargo" or w.endswith("/cargo")):
            continue
        prev = words[k - 1] if k else ""
        if prev == "just" or prev.endswith("/just"):
            return []                      # `just cargo …` — the sanctioned path
        if k and prev[-1:] not in (";", "&", "|", "("):
            continue                       # not in command position
        sub = words[k + 1] if k + 1 < len(words) else ""
        if sub not in RELINKS:
            continue
        # Only a RELEASE relink can strip the signature. `cargo build` alone
        # writes target/debug and cannot cause the failure this rule exists for
        # — firing on it would be crying wolf, and a rule that cries wolf is
        # read as noise. This is narrower than the check pattern as authored,
        # deliberately; see the note below.
        tail = words[k + 1:]
        release = "--release" in tail or (
            "--profile" in tail
            and tail[tail.index("--profile") + 1:tail.index("--profile") + 2] == ["release"])
        if not release:
            continue
        return ["[warden] R-ha-03 — a bare `cargo %s --release` relinks "
                "`target/release/` UNSIGNED and without `BUILT_WITH_JUST=1`, so the app "
                "fails its own startup `build_verification` check and stays broken until "
                "the next `just build`. Use `just build` for a full tracked build, or "
                "`just cargo %s --release` for a one-off — it re-signs afterwards even if "
                "cargo itself fails, and still propagates cargo's exit code." % (sub, sub)]
    return []
```

*implements [[HA Rules#D09|D09]]*

A bare `cargo build --release` (or any bare `cargo` subcommand that relinks `target/release/`) is forbidden. `just build` sets `BUILT_WITH_JUST=1` at compile time, signs the output, and refreshes the app-bundle symlinks; a raw cargo relink silently strips the signature and the marker, so the running app fails its own startup `build_verification` check and stays broken until the next `just build`. `just cargo <args>` exists for the one-off cases and re-signs even when cargo itself fails.

**This is a moment rule, not a file rule** — it fires on `tool:pre:Bash` against the command string, because the failure is an action taken, not a state on disk. No `where::` selector can express it, which is the second reason the three D-records could not simply become file-glob rules.

**Check pattern:** a Bash command matching `\bcargo\s+(build|test|clippy|check|run)\b` that is not prefixed by `just` and not already inside a `just` recipe. **Enforcement today** is the compile-time stamp in `build.rs` plus the runtime assertion in `src/utils/build_verification.rs`; this rule moves the catch earlier, to before the command runs rather than after the app is already unsigned.
