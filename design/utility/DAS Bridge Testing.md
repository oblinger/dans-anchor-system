---
description: "testing strategy + proposed integration tests, grouped by bridge kind"
---

| -[[DAS Bridge Testing]]- | : testing strategy + tests<br>→ [[DAS]] → [design](hook://design) → [DAS Bridge Testing](hook://p/DAS%20Bridge%20Testing)  |
| --- | --- |
| [[DAS Bridge PRD\|PRD]]  | the requirements each test verifies |
| [[DAS Bridge UX Design\|UX Design]]  | the verbs under test |
| [[DAS Testing]]  | facet spec this doc instantiates |
| ... |  |

# DAS Bridge Testing


Each **test type** below links to its detail section — click through to see the actual tests of that type.

| TEST TYPE | Target | Rationale |
| --- | --- | --- |
| **[[DAS Bridge Testing#Unit tests\|Unit]]** | the pure-logic islands only | Config load/migration, manifest include/exclude resolution, `.stignore` intent. Small surface; the rest is I/O. |
| **[[DAS Bridge Testing#Integration tests\|Integration]]** | every verb, end-to-end, against a live remote | The load-bearing layer. Each `bridge mux` / `sync*` / `claude *` verb exercised against a reachable host. |
| **[[DAS Bridge Testing#e2e tests\|e2e]]** | one full "twin" scenario | Fresh host → sync + claude → run Claude on the twin and confirm it's the same agent. Proves the composite goal. |
| **[[DAS Bridge Testing#Property tests\|Property / invariant]]** | one hard invariant | `~/.claude/projects/` NEVER lands on the remote after any claude-bridge op. |

## Strategy

Bridge is inherently a **two-machine** system, so its center of gravity is **integration testing against a real remote** — most logic is I/O orchestration (SSH, REST, rsync) that unit tests can't meaningfully cover. Unit tests cover the small islands of pure logic in the helpers; e2e ties the three kinds together into the "twin" scenario.

**Test-environment responsibility.** A **designated test remote** (a reachable Mac — `haorui.local`, or the host in `~/.config/bridge/config.yaml` `defaults.remote`) is required for integration/e2e. Tests **skip-with-warning** (not fail) when no remote is reachable, so they're safe on a disconnected dev Mac. Integration tests use **throwaway folders** (`/tmp/bridge-test-*`), never the real vault, and **tear down** what they create. Tests address the remote by **hostname** (link-agnostic) so they survive a Thunderbolt-cable unplug / wifi switch.

**Tier mapping** (per [[verification]]): Tier 1 (agent-immediate) — all unit + integration tests with a reachable remote, deterministic PASS/FAIL. Tier 2 (agent-over-time) — the e2e twin scenario when it needs a convergence soak. Tier 3 (user-passive) — "does the twin actually feel like this machine in normal use?".

The harness is `bridge-test.sh` under the skill folder: runs the runnable tiers, prints mechanical PASS/FAIL per the [[CLAUDE.md]] no-manual-reproduction discipline.

---

## Unit tests

Pure-logic islands in the helper scripts. No remote required.

### T-cfg-migrate
**Precondition:** a legacy flat `defaults.yaml` exists, no `config.yaml`.
**Steps:** call `syncthing-helper.py::load_config`.
**Pass:** returns nested `defaults: {remote, sync_mode}` + `claude_environment.sync` derived from the legacy `default_folder`; writes `config.yaml`.

### T-cfg-defaults
**Precondition:** `config.yaml` present.
**Steps:** `syncthing-helper.py defaults --set remote=X --set default_mode=Y`.
**Pass:** writes the nested shape; the legacy flat name `default_mode` maps to `defaults.sync_mode`.

### T-manifest-exclude
**Precondition:** any `claude_environment.claude_home` manifest.
**Steps:** `claude-provision.py::get_manifest`, inspect the resolved exclude set.
**Pass:** `projects` is always present in the exclude list regardless of the include list (the hard transcript-exclusion invariant, statically).

### T-stignore-intent
**Precondition:** a Syncthing folder with the bridge `.stignore`.
**Steps:** query `/rest/db/ignores` + `/rest/db/file` for a `.claude/…` path and a normal `.md` path.
**Pass:** the `.claude/` path resolves `ignored: true`; the `.md` path `ignored: false`.

---

## Integration tests

Every verb, end-to-end, against the live test remote. Grouped by bridge kind.

### Control bridge

#### T-ctl-ssh
**Precondition:** test remote reachable.
**Steps:** `ssh -o BatchMode=yes oblinger@<host> hostname`.
**Pass:** returns the remote's hostname (key-auth works, no password prompt).

#### T-ctl-fda
**Precondition:** a Terminal-launched tmux `work` session on the remote.
**Steps:** run `ls /Volumes` (a TCC-protected path) in the tmux pane via `ctrl box2`, and the same over plain SSH.
**Pass:** the tmux-pane command **succeeds** (FDA inherited); the plain-SSH command is **denied** (`Operation not permitted`) — the contrast proves FDA inheritance.

### Sync bridge

#### T-syn-pair
**Precondition:** both Syncthing daemons up.
**Steps:** `syncthing-helper.py pair --host <host>`; read `/rest/config/devices` on both sides.
**Pass:** each device ID appears in the other's device list.

#### T-syn-forward
**Precondition:** a shared throwaway folder, sync converged.
**Steps:** write `/tmp/bridge-test-sync/foo-<stamp>` on the dev Mac; poll the remote.
**Pass:** the file appears on the remote within **15 s** with identical content.

#### T-syn-reverse
**Precondition:** folder flipped to `sendreceive` on both sides.
**Steps:** create a file on the remote; poll the dev Mac.
**Pass:** appears on the dev Mac within **15 s** (two-way works).

#### T-syn-moveaside
**Precondition:** the remote has pre-existing content at the target path.
**Steps:** run the `bridge sync` move-aside step.
**Pass:** prior content is at `<folder>.old.<date>/`; the target is a fresh dir receiving the synced version; nothing of the prior content leaks back to the dev Mac.

#### T-syn-teardown
**Precondition:** an active sync for the host.
**Steps:** `syncthing-helper.py teardown --host <host>`.
**Pass:** the folder share is gone from both daemons' configs; files remain present on both sides.

#### T-syn-fastlink
**Precondition:** a Thunderbolt/USB-C bridge cable connected.
**Steps:** read `/rest/system/connections`.
**Pass:** the active connection `address` is a `169.254.x.x:22000` (the bridge), not the wifi IP. *(Informational — skips cleanly when no cable is present.)*

### Claude bridge

#### T-cla-apply
**Precondition:** `~/.claude` present locally; remote reachable.
**Steps:** `claude-provision.py apply --host <host>`.
**Pass:** `skills/` and `CLAUDE.md` land on the remote (per the manifest include set).

#### T-cla-verify
**Precondition:** a prior `apply`.
**Steps:** `claude-provision.py verify --host <host>`.
**Pass:** `twin_ready: true` — skills present, `CLAUDE.md` present, `~/.claude/projects` empty.

#### T-cla-idempotent
**Precondition:** a prior `apply`.
**Steps:** run `apply` a second time.
**Pass:** completes with no errors; end state unchanged (rsync reports nothing or only-changed).

#### T-cla-runtime
**Precondition:** remote provisioned (environment present).
**Steps:** check for the Claude runtime on the remote — `command -v claude`, `command -v node`, `~/.claude.json` (auth).
**Pass:** all three present → the twin can actually *run* Claude. *(If absent, this test reports the runtime gap — environment parity ≠ runnable twin; the runtime+auth provisioning is a tracked milestone.)*

---

## e2e tests

The headline scenario — the composite "twin" goal.

### T-e2e-twin-identity
**The "is it really me?" test.** Run a real Claude (Code) session on the remote and confirm it is the *same agent* — not the same history, but the same `CLAUDE.md` and base knowledge.

**Precondition:** remote provisioned (environment) AND runtime present (`claude` + auth — see T-cla-runtime).
**Steps:**
1. `bridge <host>` into the control session (or SSH).
2. In the SKA cwd (`~/ob/kmr/SYS/Bespoke/Skill Agent`), run a non-interactive identity probe:
   `claude -p "Without reading any file, answer from your loaded context: (a) what is your role/identity here, (b) name three trigger words from your global CLAUDE.md and what they do, (c) what does the 'outbox' trigger do."`
3. Capture the response.

**Pass:** the response reflects the **synced CLAUDE.md** — it identifies as the Pilot for the SKA project, cites real trigger words (`outbox`, `trot`, `surf`, `grab`, `crank`/`'`, …) with correct behavior, and shows the base knowledge this agent should have. A generic Claude with no CLAUDE.md would fail this — so a pass proves the *same environment* loaded, i.e. "it's really me."

---

## Property tests

### T-inv-no-transcripts
**Invariant:** after *any* claude-bridge operation, `~/.claude/projects/` on the remote is absent or empty — transcripts never travel.
**Steps:** after each of `apply` / re-`apply` / a full e2e run, `ssh <host> 'ls ~/.claude/projects 2>/dev/null | wc -l'`.
**Pass:** always `0`.

---

## What's verified so far (2026-06-11, manual)

The live build against `haorui.local` exercised by hand, all passing: **T-ctl-ssh**, **T-syn-pair**, **T-syn-forward** (~15 s), **T-syn-moveaside** (empty-target variant), **T-syn-fastlink** (Thunderbolt `169.254.139.247`), **T-cla-apply**, **T-cla-verify** (`twin_ready: true`), **T-cla-idempotent**, **T-inv-no-transcripts**.

**Harness:** `bridge-test.sh haorui.local` → **8 PASS, 1 FAIL (T-cla-runtime, expected gap), 4 SKIP (manual/destructive)**. Committed at `~/.claude/skills/bridge/bridge-test.sh`.

**Known gaps blocking T-e2e-twin-identity:**
1. **Runtime absent** — haorui has the environment (65 skills, CLAUDE.md) but no `claude`/`node`/auth.
2. **No internet on haorui** — currently its only live interface is the Thunderbolt link-local bridge (`169.254.x.x`); no default route. So neither the runtime download nor the OAuth login can complete until haorui is back on wifi with internet.
3. **Auth is Keychain-based** — the OAuth token lives in the macOS Keychain (`Claude Code-credentials`), not `~/.claude.json` (which holds only account metadata). It can't be cleanly copied; the twin needs its own one-time `claude` login (or an `ANTHROPIC_API_KEY`).

**Next step:** once haorui is on wifi with internet → install node+claude → user does a one-time `claude` login → run T-e2e-twin-identity. Tracked in [[F151 — Bridge integration tests — verify Control _ Sync _ Claude bridges all work|F151]].
