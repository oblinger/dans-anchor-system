//! `warden-rs hook` — the live hook dispatcher in Rust (F213 phase 2).
//!
//! The Rust port of `warden_hook.py`'s hot path: invoked by Claude Code once
//! per hook event with the event JSON on stdin, it
//!
//!   1. checks the kill switch FIRST (`$WARDEN_HOME/DISABLED` / `WARDEN_DISABLED`);
//!   2. maps the event → Warden moment(s);
//!   3. resolves the anchor from `cwd` (walk up to `.anchor`) and its traits;
//!   4. computes the fire plan **in Rust** (`fire_plan` — the differential-tested
//!      selection engine) and emits declarative steers directly;
//!   5. hands rules owing a Python body/guard to the **resident interpreter**
//!      (`warden_daemon.py`) over the Unix socket — an IPC round-trip, never an
//!      interpreter startup — and re-interleaves the returned steers into
//!      bucket order, exactly matching the Python reference's fire order;
//!   6. runs the F222 audit-on-write doc-fire through the same daemon;
//!   7. prints the steers as hook output and **always exits 0** (fail-safe —
//!      a Warden bug must never break the user's tool call).
//!
//! Most hook calls select zero rules and never touch the daemon — that path is
//! pure Rust. When the daemon is down and a round-trip is owed, it is spawned
//! from `$WARDEN_HOME/daemon.cmd` (written by `warden compile`) and the owed
//! steers are skipped this call (a warm-up miss, logged) — fired next call.

use crate::{fire_plan, Ctx, Dispatch, Ir};
use serde_json::{json, Value};
use std::io::{Read, Write};
use std::os::unix::net::UnixStream;
use std::path::{Path, PathBuf};
use std::time::{Duration, SystemTime, UNIX_EPOCH};

pub fn warden_home() -> PathBuf {
    if let Ok(h) = std::env::var("WARDEN_HOME") {
        if !h.is_empty() {
            return PathBuf::from(h);
        }
    }
    PathBuf::from(std::env::var("HOME").unwrap_or_default()).join(".warden")
}

/// Kill switch — mirror of `warden_hook.disabled` (env, then sentinel file).
pub fn disabled() -> bool {
    if let Ok(v) = std::env::var("WARDEN_DISABLED") {
        if matches!(v.trim().to_lowercase().as_str(), "1" | "true" | "yes" | "on") {
            return true;
        }
    }
    // F217 loop prevention (wall 1): an oracle session is moment-silent.
    if let Ok(v) = std::env::var("WARDEN_ORACLE") {
        if !v.trim().is_empty() {
            return true;
        }
    }
    warden_home().join("DISABLED").exists()
}

fn now_ts() -> f64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_secs_f64())
        .unwrap_or(0.0)
}

fn append_line(name: &str, line: &str) {
    let home = warden_home();
    let _ = std::fs::create_dir_all(&home);
    if let Ok(mut f) = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(home.join(name))
    {
        let _ = writeln!(f, "{line}");
    }
}

/// Human-readable local timestamp, ms precision (mirror of `warden_hook._stamp`
/// — per user direction 2026-07-06, epoch floats told the reader nothing).
fn stamp() -> String {
    chrono::Local::now().format("%Y-%m-%d %H:%M:%S%.3f").to_string()
}

fn log(msg: &str) {
    append_line("hook.log", &format!("{}  {msg}", stamp()));
}

/// Advisory perf lines (OVER-BUDGET) go to their own file — at one line per
/// breaching call they drown hook.log's operational signal otherwise (mirror
/// of `warden_hook._log_perf`).
fn log_perf(msg: &str) {
    append_line("perf.log", &format!("{}  {msg}", stamp()));
}

/// The steer text itself, indented under the log line (mirror of
/// `warden_hook._indent_steers` — "1 issue steer(s)" alone says nothing).
fn indent_steers(steers: &[String]) -> String {
    steers
        .iter()
        .flat_map(|s| s.lines())
        .map(|ln| format!("\n        {ln}"))
        .collect()
}

// ── fire record (F231 — mirror of warden_hook._fire_record) ─────────────────

const FIRES_ROTATE_BYTES: u64 = 5 * 1024 * 1024;

/// Append one JSONL record to `~/.warden/fires.jsonl` — the explainability
/// log: which rules were considered at a moment, which fired, and the steer
/// text VERBATIM as the agent received it. `warden log` is the viewer.
fn fire_record(rec: &Value) {
    let home = warden_home();
    let _ = std::fs::create_dir_all(&home);
    let path = home.join("fires.jsonl");
    if let Ok(meta) = std::fs::metadata(&path) {
        if meta.len() > FIRES_ROTATE_BYTES {
            let _ = std::fs::rename(&path, home.join("fires.jsonl.1"));
        }
    }
    append_line("fires.jsonl", &rec.to_string());
}

// ── per-moment ms budget (M5 — advisory policy; mirror of warden_hook) ──────
// Over-budget fires are LOGGED, never dropped/demoted (PRD Q3, resolved
// advisory-first 2026-07-05).

/// A moment that owes a Python body/guard round-trip is budgeted at the
/// post-hoc 10 ms rate even at tool:pre — the F213 phase-2 design accepts
/// ~4 ms of resident-daemon IPC whenever rule-authored Python must run, so
/// holding such fires to the 2 ms pure-selection budget just logs the same
/// known design cost on every call (mirror of `warden_hook.budget_ms`).
pub fn budget_ms(moment: &str, owed_python: bool) -> f64 {
    if moment.starts_with("tool:pre") {
        if owed_python { 10.0 } else { 2.0 }
    } else if moment.starts_with("tool:post")
        || moment.starts_with("write:")
        || moment.starts_with("read:")
    {
        10.0
    } else {
        100.0 // session:* / prompt:* / git:* / timer: — rare, cost amortized
    }
}

pub fn over_budget(moment: &str, elapsed_ms: f64, owed_python: bool) -> Option<String> {
    let b = budget_ms(moment, owed_python);
    if elapsed_ms <= b {
        None
    } else {
        Some(format!(
            "OVER-BUDGET {moment} fired in {elapsed_ms:.1} ms (budget {b} ms)"
        ))
    }
}

// ── event → moment mapping (mirror of warden_hook.event_to_moments) ─────────

pub fn content_kind(file_path: &str) -> Option<&'static str> {
    let ext = Path::new(file_path)
        .extension()
        .and_then(|e| e.to_str())
        .map(|e| e.to_lowercase())?;
    match ext.as_str() {
        "md" | "markdown" => Some("markdown"),
        "rs" => Some("rust"),
        "py" => Some("python"),
        "json" => Some("json"),
        "svg" => Some("svg"),
        _ => None,
    }
}

fn str_field<'a>(v: &'a Value, key: &str) -> &'a str {
    v.get(key).and_then(Value::as_str).unwrap_or("")
}

pub fn event_to_moments(data: &Value) -> Vec<String> {
    let event = str_field(data, "hook_event_name");
    let tool = str_field(data, "tool_name");
    let empty = json!({});
    let tool_input = data.get("tool_input").filter(|v| !v.is_null()).unwrap_or(&empty);
    let file_path = str_field(tool_input, "file_path");

    match event {
        "PreToolUse" => {
            if tool == "Skill" {
                let skill = {
                    let s = str_field(tool_input, "skill");
                    if s.is_empty() { str_field(tool_input, "command") } else { s }
                }
                .trim();
                if skill.is_empty() {
                    vec!["skill:pre".into()]
                } else {
                    vec![format!("skill:pre:{skill}")]
                }
            } else if tool.is_empty() {
                vec!["tool:pre".into()]
            } else {
                vec![format!("tool:pre:{tool}")]
            }
        }
        "PostToolUse" => {
            let mut moments = if tool.is_empty() {
                vec!["tool:post".into()]
            } else {
                vec![format!("tool:post:{tool}")]
            };
            if (tool == "Write" || tool == "Edit") && !file_path.is_empty() {
                if let Some(kind) = content_kind(file_path) {
                    moments.push(format!("write:{kind}"));
                }
            }
            moments
        }
        "SessionStart" => vec!["session:start".into()],
        "Stop" => vec!["session:stop".into(), "prompt:stop".into()],
        "PreCompact" => vec!["session:compact".into()],
        "UserPromptSubmit" => vec!["prompt:submit".into()],
        _ => vec![],
    }
}

// ── anchor resolution + trait sensing (mirror of warden_fire) ────────────────

/// Python `Path.resolve(strict=False)`: absolutize + follow symlinks, and for
/// a nonexistent leaf canonicalize the nearest existing ancestor and re-append
/// the remainder. `find_anchor` must walk the RESOLVED path (F232 C1) — a
/// relative or symlinked event path (e.g. `~/.claude/skills` → dans-anchor-system) must
/// resolve to the same governing anchor as the Python reference.
fn resolve_lenient(p: &Path) -> PathBuf {
    fn go(p: &Path) -> PathBuf {
        if let Ok(c) = std::fs::canonicalize(p) {
            return c;
        }
        match (p.parent(), p.file_name()) {
            (Some(parent), Some(name)) if !parent.as_os_str().is_empty() => {
                go(parent).join(name)
            }
            _ => p.to_path_buf(),
        }
    }
    let abs = if p.is_absolute() {
        p.to_path_buf()
    } else {
        std::env::current_dir().unwrap_or_default().join(p)
    };
    go(&abs)
}

pub fn find_anchor(start: &Path) -> Option<PathBuf> {
    let mut cur = Some(resolve_lenient(start));
    while let Some(d) = cur {
        if d.join(".anchor").is_file() {
            return Some(d);
        }
        cur = d.parent().map(Path::to_path_buf);
    }
    None
}

/// Resolve a repo-side mirror-route file to its declaring vault anchor
/// (mirror of `warden_hook.mirror_route_anchor`).
///
/// Two-Way Doc Mirror routes (F188) live in code repos outside any anchor
/// tree, so `find_anchor` sees nothing there — exactly where R-code-mirror
/// must fire. The routes index (written by every `code sync`) maps each
/// repo-side route back to the `.anchor` that declared it; per F229 A′
/// (the file's anchor owns the file) that vault anchor governs the copies.
pub fn mirror_route_anchor_in(file_path: &Path, routes_file: &Path) -> Option<PathBuf> {
    let text = std::fs::read_to_string(routes_file).ok()?;
    let idx: Value = serde_json::from_str(&text).ok()?;
    let routes = idx.get("routes")?.as_array()?;
    let fp = resolve_lenient(file_path);
    for e in routes {
        let (Some(there), Some(anchor)) = (
            e.get("there").and_then(Value::as_str),
            e.get("anchor").and_then(Value::as_str),
        ) else {
            continue;
        };
        if there.is_empty() || anchor.is_empty() {
            continue;
        }
        let t = resolve_lenient(Path::new(there));
        if fp.ancestors().any(|a| a == t) {
            let d = Path::new(anchor).parent()?.to_path_buf();
            if d.join(".anchor").is_file() {
                return Some(d);
            }
        }
    }
    None
}

pub fn mirror_route_anchor(file_path: &Path) -> Option<PathBuf> {
    let routes = PathBuf::from(std::env::var("HOME").unwrap_or_default())
        .join(".config/anchor-system/mirror-routes.json");
    mirror_route_anchor_in(file_path, &routes)
}

/// One `.anchor` trait-valued key in either YAML shape (mirror of
/// `warden_fire._read_trait_list`). `key` carries its own colon and is matched
/// at line start, so `traits:` and `traits-:` never catch each other.
fn read_trait_list(text: &str, key: &str) -> Vec<String> {
    let mut traits: Vec<String> = Vec::new();
    let lines: Vec<&str> = text.lines().collect();
    // Mirror the Python reference's TWO regex passes exactly (F232 C2):
    // the whole-file FLOW search runs first — a flow-style `traits: […]`
    // line wins wherever it appears, even below a block-style one; only
    // when no flow line exists anywhere does the block search run.
    let mut flow: Option<&str> = None;
    for line in &lines {
        // the Python regexes anchor the key at line start (no indent)
        let Some(rest) = line.strip_prefix(key) else { continue };
        let rest = rest.trim_start();
        if rest.starts_with('[') && rest.contains(']') {
            flow = rest.strip_prefix('[').and_then(|r| r.split(']').next());
            break;
        }
    }
    if let Some(inner) = flow {
        return inner
            .split(',')
            .map(|t| t.trim().trim_matches(|c| c == '\'' || c == '"').to_string())
            .filter(|t| !t.is_empty())
            .collect();
    }
    for (i, line) in lines.iter().enumerate() {
        let Some(rest) = line.strip_prefix(key) else { continue };
        if !rest.trim().is_empty() {
            continue; // `traits: foo` — matches neither Python regex
        }
        for ln in &lines[i + 1..] {
            let t = ln.trim();
            if t.is_empty() {
                continue; // blank inside the block list (Python `\s*`)
            }
            if let Some(item) = t.strip_prefix('-') {
                traits.push(item.trim().to_string());
            } else {
                break;
            }
        }
        break;
    }
    traits
}

/// from_utf8_lossy mirrors Python's errors="replace": a stray non-UTF-8 byte
/// degrades to whatever parses instead of dropping every trait.
fn read_anchor_text(anchor_root: &Path) -> String {
    match std::fs::read(anchor_root.join(".anchor")) {
        Ok(bytes) => String::from_utf8_lossy(&bytes).into_owned(),
        Err(_) => String::new(),
    }
}

/// The `.anchor` `traits:` list (YAML flow or block) + the implicit `anchor-base`
/// trait (mirror of `warden_fire.read_anchor_traits`). The raw declaration read —
/// opt-outs are applied where effective traits are computed.
pub fn read_anchor_traits(anchor_root: &Path) -> Vec<String> {
    let mut traits = read_trait_list(&read_anchor_text(anchor_root), "traits:");
    traits.push("anchor-base".into());
    traits
}

/// The `.anchor` `traits-:` list — traits this anchor opts OUT of (F285;
/// mirror of `warden_fire.read_anchor_optouts`). Declared, never inherited.
pub fn read_anchor_optouts(anchor_root: &Path) -> Vec<String> {
    read_trait_list(&read_anchor_text(anchor_root), "traits-:")
}

/// The git-aspect string a rule reads, from the anchor's traits (mirror of
/// `warden_fire.git_aspect_of`).
pub fn git_aspect_of(traits: &[String]) -> String {
    for t in traits {
        let low = t.to_lowercase();
        if matches!(low.as_str(), "commit" | "pr" | "push" | "nogit") {
            return low;
        }
    }
    String::new()
}

// ── resident-daemon client ───────────────────────────────────────────────────

fn socket_path() -> PathBuf {
    warden_home().join("daemon.sock")
}

fn daemon_request_once(req: &Value, timeout: Duration) -> std::io::Result<Value> {
    let mut conn = UnixStream::connect(socket_path())?;
    conn.set_read_timeout(Some(timeout))?;
    conn.set_write_timeout(Some(timeout))?;
    let mut line = serde_json::to_vec(req).unwrap_or_default();
    line.push(b'\n');
    conn.write_all(&line)?;
    let mut buf = Vec::new();
    let mut chunk = [0u8; 65536];
    while !buf.contains(&b'\n') {
        let n = conn.read(&mut chunk)?;
        if n == 0 {
            break;
        }
        buf.extend_from_slice(&chunk[..n]);
    }
    let end = buf.iter().position(|&b| b == b'\n').unwrap_or(buf.len());
    serde_json::from_slice(&buf[..end])
        .map_err(|e| std::io::Error::new(std::io::ErrorKind::InvalidData, e))
}

/// The daemon script path inside a `daemon.cmd` line — `python3 <script>
/// --serve`, the script token possibly shell-quoted (Audit 2026-07-12 W2).
fn daemon_cmd_script(cmd: &str) -> Option<PathBuf> {
    let rest = cmd.trim().strip_prefix("python3").unwrap_or(cmd).trim_start();
    let tok = if let Some(r) = rest.strip_prefix('\'') {
        r.split('\'').next().unwrap_or("")
    } else {
        rest.split_whitespace().next().unwrap_or("")
    };
    if tok.is_empty() {
        None
    } else {
        Some(PathBuf::from(tok))
    }
}

/// Audit 2026-07-12 W2: the compiled state's absolute-path snapshots that can
/// dangle after a repo move/rename — one line per dead path, empty = healthy.
/// Detection only; callers warn loudly but stay fail-open.
fn stale_paths(ir_root: Option<&str>) -> Vec<String> {
    let mut out = Vec::new();
    if let Some(root) = ir_root {
        if !root.is_empty() && !Path::new(root).is_dir() {
            out.push(format!("compiled IR root missing: {root}"));
        }
    }
    if let Ok(cmd) = std::fs::read_to_string(warden_home().join("daemon.cmd")) {
        if let Some(script) = daemon_cmd_script(&cmd) {
            if !script.is_file() {
                out.push(format!("daemon.cmd target missing: {}", script.display()));
            }
        }
    }
    out
}

/// Spawn the resident daemon from `$WARDEN_HOME/daemon.cmd` (written by
/// `warden compile`), detached; returns false when no spawn command exists.
fn spawn_daemon() -> bool {
    let cmd_file = warden_home().join("daemon.cmd");
    let Ok(cmd) = std::fs::read_to_string(&cmd_file) else {
        log("daemon MISS — no daemon.cmd; run `warden compile`");
        return false;
    };
    let cmd = cmd.trim();
    if cmd.is_empty() {
        return false;
    }
    // Audit 2026-07-12 W2: a daemon.cmd pointing at a moved/deleted script
    // spawns a shell that dies instantly, and the warm-up retry loop then eats
    // the FULL timeout on every hook call. Fail fast and loudly instead.
    if let Some(script) = daemon_cmd_script(cmd) {
        if !script.is_file() {
            let msg = format!(
                "daemon STALE — daemon.cmd target missing: {} (repo moved? run `warden install`)",
                script.display()
            );
            log(&msg);
            eprintln!("warden: {msg}");
            return false;
        }
    }
    match std::process::Command::new("/bin/sh")
        .arg("-c")
        .arg(cmd)
        .stdin(std::process::Stdio::null())
        .stdout(std::process::Stdio::null())
        .stderr(std::process::Stdio::null())
        .spawn()
    {
        Ok(_) => true,
        Err(e) => {
            log(&format!("daemon spawn failed: {e}"));
            false
        }
    }
}

/// The daemon-client timeout for a moment (T013): a pending tool call must
/// not sit behind a slow daemon — `tool:pre:*` gets ~2 s (the busy-window a
/// veto rule may hold up the tool, down from 20 s); everything else is
/// post-hoc advice and can afford the patient 20 s.
pub fn daemon_timeout(moment: &str) -> Duration {
    if moment.starts_with("tool:pre") {
        Duration::from_secs(2)
    } else {
        Duration::from_secs(20)
    }
}

/// `daemon_request` with the timeout picked from the moment class.
pub fn daemon_request_at(moment: &str, req: &Value) -> Option<Value> {
    daemon_request(req, daemon_timeout(moment))
}

/// One request to the resident daemon, spawning it on demand. Returns None on
/// unreachable/error (fail-safe: the caller skips the owed steers this call).
///
/// Alive-but-slow is terminal (T013): a read timeout means the daemon has the
/// connection but hasn't answered inside `timeout` — give up NOW (the owed
/// steers are skipped this call), never fall into the spawn path where the
/// retry loop would multiply the wait. Only connect-level failures (dead /
/// missing socket) go to spawn + warm-up, bounded by the same `timeout`.
pub fn daemon_request(req: &Value, timeout: Duration) -> Option<Value> {
    match daemon_request_once(req, timeout) {
        Ok(resp) => return Some(resp),
        Err(e)
            if matches!(
                e.kind(),
                std::io::ErrorKind::TimedOut | std::io::ErrorKind::WouldBlock
            ) =>
        {
            log(&format!(
                "daemon SLOW — no response in {:.1}s; owed steers skipped this call",
                timeout.as_secs_f64()
            ));
            return None;
        }
        Err(_) => {} // unreachable → spawn path
    }
    if !spawn_daemon() {
        return None;
    }
    // warm-up: imports + IR preload take a few hundred ms on first spawn;
    // the whole spawn-and-retry phase is bounded by the caller's timeout.
    let deadline = std::time::Instant::now() + timeout;
    while std::time::Instant::now() < deadline {
        std::thread::sleep(Duration::from_millis(100));
        match daemon_request_once(req, timeout) {
            Ok(resp) => return Some(resp),
            Err(e)
                if matches!(
                    e.kind(),
                    std::io::ErrorKind::TimedOut | std::io::ErrorKind::WouldBlock
                ) =>
            {
                break; // accepting but slow — same terminal give-up as above
            }
            Err(_) => continue,
        }
    }
    log("daemon MISS — spawned but not answering in time; owed steers skipped this call");
    None
}

// ── dispatch (mirror of warden_hook.dispatch) ────────────────────────────────

fn load_ir() -> Option<Ir> {
    let ir_path = warden_home().join("rules-ir.json");
    let text = match std::fs::read_to_string(&ir_path) {
        Ok(t) => t,
        Err(_) => {
            log(&format!("no compiled IR at {} — run `warden compile`", ir_path.display()));
            return None;
        }
    };
    match serde_json::from_str(&text) {
        Ok(ir) => Some(ir),
        Err(e) => {
            log(&format!("bad IR json: {e}"));
            None
        }
    }
}

pub fn dispatch(data: &Value) -> Vec<String> {
    let moments = event_to_moments(data);
    if moments.is_empty() {
        return vec![];
    }
    let cwd = {
        let c = str_field(data, "cwd");
        if c.is_empty() {
            std::env::current_dir().unwrap_or_default()
        } else {
            PathBuf::from(c)
        }
    };
    let anchor_cwd = find_anchor(&cwd);
    // F215: the event's file path — the daemon binds ctx.file per
    // file-bearing rule from it (write:/read: moments).
    let empty_ti = json!({});
    let event_ti = data.get("tool_input").filter(|v| !v.is_null()).unwrap_or(&empty_ti);
    let event_fp = str_field(event_ti, "file_path");
    // F229 A′: any moment whose event carries an anchored file — write:/read:,
    // file-bearing tool moments like tool:pre:Edit, and the doc-fire — is
    // governed by the FILE's anchor: the file's anchor owns the file, wherever
    // the session sits. (Extended to tool moments 2026-07-06 — the adoption
    // audit showed a cwd outside the guarded anchor side-stepped R-pathguard.)
    let anchor_file = if event_fp.is_empty() {
        None
    } else {
        Path::new(event_fp)
            .parent()
            .and_then(find_anchor)
            // F188: repo-side mirror-route files sit outside any anchor tree;
            // the routes index maps them back to the declaring vault anchor.
            .or_else(|| mirror_route_anchor(Path::new(event_fp)))
    };
    if anchor_cwd.is_none() && anchor_file.is_none() {
        return vec![];
    }
    let Some(ir) = load_ir() else { return vec![] };
    // Effective traits = declared + `anchor-base` + the base trait's members
    // (mirror of `warden_fire.effective_traits`).
    let effective = |root: &Path| -> Vec<String> {
        let mut ts = read_anchor_traits(root);
        for t in &ir.base_traits {
            if !ts.iter().any(|x| x == t) {
                ts.push(t.clone());
            }
        }
        // F285: subtract what the anchor opts out of. Subtracting an umbrella
        // subtracts its members (else the opt-out is itself a decaying list),
        // but an explicitly declared trait always survives — `traits-` removes
        // only what the anchor gets implicitly.
        let optouts = read_anchor_optouts(root);
        if optouts.is_empty() {
            return ts;
        }
        let declared = read_trait_list(&read_anchor_text(root), "traits:");
        let mut drop: Vec<String> = optouts.clone();
        if optouts.iter().any(|t| t == "anchor-base") {
            drop.extend(ir.base_traits.iter().cloned());
        }
        ts.retain(|t| !drop.contains(t) || declared.contains(t));
        ts
    };

    let mut steers: Vec<String> = Vec::new();
    // Audit 2026-07-12 W2: loudly surface compiled-state paths that no longer
    // resolve (repo moved/renamed) — fail-open, dispatch continues on whatever
    // still works, but the staleness is never symptom-free again (mirror of
    // `warden_hook._stale_paths`).
    let stale = stale_paths(ir.root.as_deref());
    if !stale.is_empty() {
        let detail = stale.join("; ");
        log(&format!("STALE — {detail} (repo moved? run `warden install`)"));
        eprintln!("warden: STALE — {detail} (repo moved? run `warden install`)");
        if moments.iter().any(|m| m == "session:start") {
            steers.push(format!(
                "[warden] STALE compiled state — {detail}; run `warden install` \
                 (rules are NOT enforcing until then)"
            ));
        }
    }
    for moment in &moments {
        let anchor_root = anchor_file.as_ref().or(anchor_cwd.as_ref());
        let Some(anchor_root) = anchor_root else { continue };
        let anchor_name = anchor_root
            .file_name()
            .map(|n| n.to_string_lossy().into_owned())
            .unwrap_or_default();
        let traits = effective(anchor_root);
        let ctx = Ctx {
            git_aspect: Value::String(git_aspect_of(&traits)),
            mode: Value::Null,
            traits: traits.clone(),
            facets: vec![],
        };
        // F231: the considered set = active rules in the bucket, INCLUDING
        // guard-gated ones — mirrors Python's fire_records exactly, so the
        // fire record can distinguish "rule was live and stayed silent" from
        // "no rule was in play" on both engines (fire_plan drops guard-gated
        // rules, so it under-reports considered).
        let considered: Vec<String> = ir
            .moments
            .get(moment.as_str())
            .map(|bucket| {
                bucket
                    .iter()
                    .filter(|rid| ir.rules.contains_key(*rid) && crate::is_active(&ir, rid, &traits))
                    .cloned()
                    .collect()
            })
            .unwrap_or_default();
        if considered.is_empty() {
            continue;
        }
        let fire_t0 = std::time::Instant::now();
        let plan = fire_plan(&ir, moment, &ctx, &traits);
        // rules owing a Python round-trip → one daemon call per moment
        let owed: Vec<String> = plan
            .iter()
            .filter(|f| matches!(f.dispatch, Dispatch::PythonBody(_) | Dispatch::PythonGuard(_)))
            .map(|f| f.rule_id.clone())
            .collect();
        let mut by_rule: Value = json!({});
        if !owed.is_empty() {
            if let Some(resp) = daemon_request_at(moment, &json!({
                "op": "fire_rules",
                "moment": moment,
                "anchor_root": anchor_root.to_string_lossy(),
                "rule_ids": owed,
                "file_path": event_fp,
                // F131: the pending tool call — veto-path rules test
                // event.tool / event.target / event.input in their bodies.
                "tool_name": str_field(data, "tool_name"),
                "tool_input": event_ti,
                // F216: the session mapping — the daemon records the moment in
                // its ledger and binds the agent-state view for rule bodies.
                "session": {
                    "session_id": str_field(data, "session_id"),
                    "transcript_path": str_field(data, "transcript_path"),
                    "cwd": cwd.to_string_lossy(),
                },
            })) {
                if resp.get("ok").and_then(Value::as_bool) == Some(true) {
                    by_rule = resp.get("steers_by_rule").cloned().unwrap_or(json!({}));
                } else {
                    // Audit 2026-07-12 W4: an errored daemon response (e.g. a
                    // truncated request) is NOT "no rules fired" — the owed
                    // steers/vetoes are skipped fail-open, but say so.
                    let err = resp.get("error").and_then(Value::as_str).unwrap_or("?");
                    log(&format!(
                        "daemon ERROR at {moment}: {err} — owed steers skipped this call"
                    ));
                }
            }
        }
        // re-interleave into bucket order, matching the Python fire() exactly
        let before = steers.len();
        let mut fires: Vec<Value> = Vec::new();
        for fired in &plan {
            let mut produced: Vec<String> = Vec::new();
            match &fired.dispatch {
                Dispatch::Declarative(s) => produced.push(s.clone()),
                Dispatch::ActionOther => {}
                Dispatch::PythonBody(_) | Dispatch::PythonGuard(_) => {
                    if let Some(rs) = by_rule.get(&fired.rule_id).and_then(Value::as_array) {
                        produced.extend(rs.iter().filter_map(Value::as_str).map(String::from));
                    }
                }
            }
            for s in &produced {
                fires.push(json!({"rule": fired.rule_id, "steer": s}));
            }
            steers.extend(produced);
        }
        let elapsed_ms = fire_t0.elapsed().as_secs_f64() * 1000.0;
        // owed-budget from the considered set (mirror of warden_hook's records-
        // based owed), not the guard-surviving plan — both engines pick the
        // same budget for the same moment.
        let owed_python = considered.iter().any(|rid| {
            ir.rules
                .get(rid)
                .map(|r| r.body_py.is_some() || r.guard_py.is_some())
                .unwrap_or(false)
        });
        if let Some(warn) = over_budget(moment, elapsed_ms, owed_python) {
            log_perf(&warn);
        }
        // F231: the explainability record — considered set + verbatim steers.
        fire_record(&json!({
            "ts": (now_ts() * 1000.0).round() / 1000.0, "engine": "rs",
            "moment": moment, "anchor": &anchor_name, "traits": &traits,
            "tool": str_field(data, "tool_name"), "file": event_fp,
            "considered": considered,
            "fires": fires,
            "ms": (elapsed_ms * 10.0).round() / 10.0,
        }));
        if steers.len() > before {
            log(&format!(
                "FIRED {moment} @ {anchor_name} traits={traits:?} → {} steer(s){}",
                steers.len() - before,
                indent_steers(&steers[before..])
            ));
        }
    }

    // F222 / F229 A′ audit-on-write — the doc-fire runs warm in the daemon,
    // governed by the FILE's anchor (`audit-on-write` rides `anchor-base` via
    // ir.base_traits, so every anchored file is audited on write; an
    // un-anchored file is not).
    //
    // F297: ANY typed write kind, not just `write:markdown`. The moment
    // vocabulary already distinguished them (`content_kind` maps `.svg` → svg),
    // so the narrow condition here was the whole reason a non-markdown document
    // rule could compile, register, and be declared on an anchor and still
    // never be considered. Which rules a kind puts in play is decided
    // downstream, in `warden_docfire.rows_for` — a file no declared glob names
    // flattens nothing and costs nothing.
    let write_moment = moments.iter().find(|m| m.starts_with("write:"));
    if let (Some(afile), Some(wm)) = (anchor_file.as_ref(), write_moment) {
        if !event_fp.is_empty() && effective(afile).iter().any(|t| t == "audit-on-write") {
            steers.extend(doc_fire(event_fp, afile, str_field(data, "tool_name"), wm));
        }
    }

    // F297 leg 2 — a file a SCRIPT wrote. A Bash event carries the command
    // string and nothing about what it touched, so `python3 make_diagram.py`
    // is invisible to every file-keyed moment. After the call, stat the
    // governed paths the compile resolved and doc-fire whatever moved: 0.5 ms
    // over the vault's SVGs, against 228 ms to rediscover them live.
    if !ir.governed_paths.is_empty() && moments.iter().any(|m| m == "tool:post:Bash") {
        for moved in governed_moved(&ir) {
            let p = PathBuf::from(&moved);
            let Some(a) = p.parent().and_then(find_anchor) else { continue };
            if !effective(&a).iter().any(|t| t == "audit-on-write") {
                continue;
            }
            steers.extend(doc_fire(&moved, &a, "Bash", "tool:post:Bash"));
        }
    }
    steers
}

/// One doc-fire — the daemon's audit pass over `file`, owned by anchor `afile`.
/// Shared by the on-write path and the F297 post-Bash sweep so a script's write
/// and a direct write produce the same steers and the same fire record.
fn doc_fire(file: &str, afile: &Path, tool: &str, timeout_moment: &str) -> Vec<String> {
    let Some(resp) = daemon_request(&json!({"op": "audit", "file_path": file}),
                                    daemon_timeout(timeout_moment))
    else {
        return vec![];
    };
    if resp.get("ok").and_then(Value::as_bool) != Some(true) {
        // Audit 2026-07-12 W4: log an errored doc-fire response too.
        let err = resp.get("error").and_then(Value::as_str).unwrap_or("?");
        log(&format!("daemon ERROR at doc-fire: {err} — audit skipped this call"));
        return vec![];
    }
    let Some(aow) = resp.get("steers").and_then(Value::as_array) else {
        return vec![];
    };
    let aow_texts: Vec<String> = aow.iter().filter_map(Value::as_str).map(String::from).collect();
    if !aow_texts.is_empty() {
        let anchor_name = afile
            .file_name()
            .map(|n| n.to_string_lossy().into_owned())
            .unwrap_or_default();
        log(&format!(
            "AUDIT-ON-WRITE {} @ {anchor_name} → {} issue steer(s){}",
            Path::new(file).file_name().map(|n| n.to_string_lossy()).unwrap_or_default(),
            aow_texts.len(),
            indent_steers(&aow_texts)
        ));
        // F231: doc-fire steers land in the fire record too.
        fire_record(&json!({
            "ts": (now_ts() * 1000.0).round() / 1000.0, "engine": "rs",
            "moment": "doc-fire", "anchor": anchor_name,
            "traits": [], "tool": tool,
            "file": file, "considered": ["audit-on-write"],
            "fires": aow_texts.iter()
                .map(|s| json!({"rule": "audit-on-write", "steer": s}))
                .collect::<Vec<_>>(),
            "ms": 0.0,
        }));
    }
    aow_texts
}

/// The governed paths whose mtime moved since the last sweep (F297 leg 2).
///
/// The snapshot lives beside the compiled state and is keyed on the IR's
/// `source_hash`: a recompile re-baselines rather than reporting the entire
/// list as changed, and a path that is stat-able but absent from the previous
/// snapshot is adopted silently for the same reason. Both directions fail
/// quiet — a sweep that cannot read or write its snapshot reports nothing
/// rather than firing on everything.
fn governed_moved(ir: &Ir) -> Vec<String> {
    let snap_path = warden_home().join("governed.json");
    let stamp = ir.source_hash.clone().unwrap_or_default();
    let prev: Value = std::fs::read_to_string(&snap_path)
        .ok()
        .and_then(|t| serde_json::from_str(&t).ok())
        .unwrap_or_else(|| json!({}));
    let rebased = prev.get("source_hash").and_then(Value::as_str) != Some(stamp.as_str());
    let empty = serde_json::Map::new();
    let prev_m = prev.get("mtimes").and_then(Value::as_object).unwrap_or(&empty);
    let mut now_m = serde_json::Map::new();
    let mut moved: Vec<String> = Vec::new();
    for p in &ir.governed_paths {
        let Ok(md) = std::fs::metadata(p) else { continue };
        let ns = md
            .modified()
            .ok()
            .and_then(|t| t.duration_since(std::time::UNIX_EPOCH).ok())
            .map(|d| d.as_nanos() as u64)
            .unwrap_or(0);
        if let Some(was) = prev_m.get(p).and_then(Value::as_u64) {
            if !rebased && was != ns {
                moved.push(p.clone());
            }
        }
        now_m.insert(p.clone(), json!(ns));
    }
    if rebased || now_m != *prev_m {
        let snap = json!({"source_hash": stamp, "mtimes": now_m});
        if let Ok(text) = serde_json::to_string(&snap) {
            let _ = std::fs::write(&snap_path, text);
        }
    }
    moved
}

// ── F328: the DAS hook registry — Warden executes it for free (mirror of
// `warden_hook.run_registry`) ────────────────────────────────────────────────
//
// One file (~/.config/anchor-system/hooks/registry): each line is a moment,
// whitespace, one executable path — no inline arguments (grammar owned by
// DAS's hook-install / hook-run). Warden is already spawned at the moment, so
// fanning out from here costs zero additional processes; on Warden-less
// machines the `hook-run` fallback does the same job over the same file, and
// both executors log to the same file in the same line format. A failing
// child is logged with its exit status and never suppresses its neighbours
// or the hook itself. A child's stdout is returned as a tell — it joins the
// steers on the same `additionalContext` surface its output would have landed
// on as a separate settings.json entry. (Structured hook-decision JSON from a
// registry child is not interpreted — a hook that needs `permissionDecision`
// keeps its own settings.json entry rather than a registry line.)

fn registry_path() -> PathBuf {
    if let Ok(p) = std::env::var("DAS_HOOK_REGISTRY") {
        if !p.is_empty() {
            return PathBuf::from(p);
        }
    }
    PathBuf::from(std::env::var("HOME").unwrap_or_default())
        .join(".config/anchor-system/hooks/registry")
}

fn registry_log(line: &str) {
    let path = std::env::var("DAS_HOOK_LOG")
        .ok()
        .filter(|p| !p.is_empty())
        .map(PathBuf::from)
        .unwrap_or_else(|| {
            PathBuf::from(std::env::var("HOME").unwrap_or_default())
                .join(".config/anchor-system/hooks/hook-run.log")
        });
    if let Some(dir) = path.parent() {
        let _ = std::fs::create_dir_all(dir);
    }
    if let Ok(mut f) = std::fs::OpenOptions::new().create(true).append(true).open(&path) {
        let _ = writeln!(f, "{line}");
    }
}

/// Run every registry line matching this event's moments, in file order.
/// Returns the children's non-empty stdouts as tells. Never panics outward.
pub fn run_registry(data: &Value, raw: &str) -> Vec<String> {
    let Ok(text) = std::fs::read_to_string(registry_path()) else {
        return vec![];
    };
    let moments = event_to_moments(data);
    let mut tells: Vec<String> = Vec::new();
    for line in text.lines() {
        let t = line.trim();
        if t.is_empty() || t.starts_with('#') {
            continue;
        }
        let Some((m, rest)) = t.split_once(char::is_whitespace) else { continue };
        let cmd = rest.trim();
        if cmd.is_empty() || !moments.iter().any(|mm| mm == m) {
            continue;
        }
        let ts = chrono::Local::now().format("%Y-%m-%d %H:%M:%S").to_string();
        let spawned = std::process::Command::new(cmd)
            .stdin(std::process::Stdio::piped())
            .stdout(std::process::Stdio::piped())
            .spawn();
        let mut child = match spawned {
            Ok(c) => c,
            Err(e) => {
                registry_log(&format!("{ts}  {m}  error={e}  {cmd}"));
                continue;
            }
        };
        // Threaded stdin write: the event JSON can exceed the pipe buffer
        // (an Edit's tool_input carries file content), and a child that
        // writes before it reads would deadlock a same-thread write+drain.
        let payload = raw.as_bytes().to_vec();
        let mut si = child.stdin.take();
        let writer = std::thread::spawn(move || {
            if let Some(ref mut s) = si {
                let _ = s.write_all(&payload);
            }
        });
        let out = child.wait_with_output();
        let _ = writer.join();
        match out {
            Ok(o) => {
                if o.status.success() {
                    registry_log(&format!("{ts}  {m}  ok  {cmd}"));
                } else {
                    registry_log(&format!(
                        "{ts}  {m}  exit={}  {cmd}",
                        o.status.code().unwrap_or(-1)
                    ));
                }
                let text = String::from_utf8_lossy(&o.stdout).trim().to_string();
                if !text.is_empty() {
                    tells.push(text);
                }
            }
            Err(e) => registry_log(&format!("{ts}  {m}  error={e}  {cmd}")),
        }
    }
    tells
}

/// The F131 deny sentinel — a steer carrying this prefix is a veto, converted
/// to a real `permissionDecision: deny` at a PreToolUse event (mirror of
/// `warden_hook.DENY_SENTINEL`).
pub const DENY_SENTINEL: &str = "DENY: ";

/// Hook output that injects the steers as agent-visible context (mirror of
/// `warden_hook.emit`). At PreToolUse, `DENY: `-sentinel steers become a
/// `permissionDecision: deny` with the deny text(s) as the reason; at any
/// other event the sentinel degrades to a plain steer (deny is `tool:pre`-only
/// — fail-open, never fail-closed).
pub fn emit(event: &str, steers: &[String]) {
    if steers.is_empty() {
        return;
    }
    let denies: Vec<String> = steers
        .iter()
        .filter_map(|s| s.strip_prefix(DENY_SENTINEL).map(String::from))
        .collect();
    let mut tells: Vec<String> = steers
        .iter()
        .filter(|s| !s.is_empty() && !s.starts_with(DENY_SENTINEL))
        .cloned()
        .collect();
    let mut hso = serde_json::Map::new();
    hso.insert("hookEventName".into(), json!(event));
    if !denies.is_empty() && event == "PreToolUse" {
        hso.insert("permissionDecision".into(), json!("deny"));
        hso.insert("permissionDecisionReason".into(), json!(denies.join("\n\n")));
    } else {
        tells.extend(denies); // non-pre deny degrades to a plain steer
    }
    let text = tells.join("\n\n");
    if !text.is_empty() {
        hso.insert("additionalContext".into(), json!(text));
    }
    if hso.len() == 1 {
        return;
    }
    println!("{}", json!({ "hookSpecificOutput": hso }));
}

/// The `warden-rs hook` entry point. Always returns 0 (fail-safe).
pub fn run_hook() -> i32 {
    // 1. kill switch — before ANY work.
    if disabled() {
        return 0;
    }
    // 2. read the event; malformed payload is a no-op, never an error.
    let mut raw = String::new();
    if std::io::stdin().read_to_string(&mut raw).is_err() {
        return 0;
    }
    let data: Value = match serde_json::from_str(raw.trim()) {
        Ok(v) => v,
        Err(_) => {
            if raw.trim().is_empty() {
                json!({})
            } else {
                return 0;
            }
        }
    };
    // 3. dispatch — any panic is caught so the tool call is never broken.
    let event = str_field(&data, "hook_event_name").to_string();
    let mut steers = std::panic::catch_unwind(|| dispatch(&data)).unwrap_or_else(|_| {
        log("ERROR panic in dispatch");
        vec![]
    });
    // F328: fan out to the DAS hook registry at this event's moments —
    // children's stdout joins the steers as agent-visible context.
    steers.extend(
        std::panic::catch_unwind(|| run_registry(&data, &raw)).unwrap_or_else(|_| {
            log("ERROR panic in run_registry");
            vec![]
        }),
    );
    emit(&event, &steers);
    0
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn event_mapping_mirrors_python() {
        let e = |v: Value| event_to_moments(&v);
        assert_eq!(
            e(json!({"hook_event_name": "PostToolUse", "tool_name": "Write",
                     "tool_input": {"file_path": "x.md"}})),
            vec!["tool:post:Write", "write:markdown"]
        );
        assert_eq!(e(json!({"hook_event_name": "PostToolUse", "tool_name": "Bash"})),
                   vec!["tool:post:Bash"]);
        assert_eq!(e(json!({"hook_event_name": "PreToolUse", "tool_name": "Bash"})),
                   vec!["tool:pre:Bash"]);
        assert_eq!(e(json!({"hook_event_name": "PreToolUse", "tool_name": "Skill",
                            "tool_input": {"skill": "audit-q"}})),
                   vec!["skill:pre:audit-q"]);
        assert_eq!(e(json!({"hook_event_name": "UserPromptSubmit"})), vec!["prompt:submit"]);
        assert_eq!(e(json!({"hook_event_name": "SessionStart"})), vec!["session:start"]);
        assert_eq!(e(json!({"hook_event_name": "Stop"})), vec!["session:stop", "prompt:stop"]);
        assert_eq!(e(json!({"hook_event_name": "PreCompact"})), vec!["session:compact"]);
        assert_eq!(e(json!({"hook_event_name": "Nonsense"})), Vec::<String>::new());
    }

    #[test]
    fn traits_flow_and_block() {
        let td = std::env::temp_dir().join(format!("warden-rs-traits-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&td);
        std::fs::create_dir_all(&td).unwrap();
        std::fs::write(td.join(".anchor"), "slug: FX\ntraits: [warden-selftest, Commit]\n").unwrap();
        assert_eq!(read_anchor_traits(&td), vec!["warden-selftest", "Commit", "anchor-base"]);
        std::fs::write(td.join(".anchor"), "slug: FX\ntraits:\n  - a\n  - b\nother: x\n").unwrap();
        assert_eq!(read_anchor_traits(&td), vec!["a", "b", "anchor-base"]);
        std::fs::write(td.join(".anchor"), "slug: FX\n").unwrap();
        assert_eq!(read_anchor_traits(&td), vec!["anchor-base"]);
        let _ = std::fs::remove_dir_all(&td);
    }

    /// F285 — `traits-` parses in both YAML shapes and never collides with
    /// `traits:` in either direction. The subtraction semantics themselves are
    /// exercised through dispatch; this pins the read that feeds them.
    #[test]
    fn optouts_parse_without_colliding_with_traits() {
        let td = std::env::temp_dir().join(format!("warden-rs-optout-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&td);
        std::fs::create_dir_all(&td).unwrap();

        // flow shape, both keys present — each reads only its own
        std::fs::write(td.join(".anchor"),
                       "slug: FX\ntraits: [track]\ntraits-: [anchor-base]\n").unwrap();
        assert_eq!(read_anchor_traits(&td), vec!["track", "anchor-base"]);
        assert_eq!(read_anchor_optouts(&td), vec!["anchor-base"]);

        // block shape
        std::fs::write(td.join(".anchor"),
                       "slug: FX\ntraits-:\n  - pathguard\n  - ios\nother: x\n").unwrap();
        assert_eq!(read_anchor_optouts(&td), vec!["pathguard", "ios"]);
        assert_eq!(read_anchor_traits(&td), vec!["anchor-base"]);

        // absent → empty, and today's anchors are unaffected
        std::fs::write(td.join(".anchor"), "slug: FX\ntraits: [track]\n").unwrap();
        assert!(read_anchor_optouts(&td).is_empty());

        let _ = std::fs::remove_dir_all(&td);
    }

    #[test]
    fn mirror_route_resolves_declaring_anchor() {
        // F188: a repo-side mirror-route file outside any anchor tree resolves
        // to the vault anchor that declared the route; non-route files don't.
        let td = std::env::temp_dir().join(format!("warden-rs-mirror-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&td);
        let vault = td.join("vault/anchor");
        let repo = td.join("proj/repo");
        std::fs::create_dir_all(&vault).unwrap();
        std::fs::create_dir_all(repo.join("Docs")).unwrap();
        std::fs::write(vault.join(".anchor"), "slug: FX\ntraits: [code]\n").unwrap();
        let routes = td.join("mirror-routes.json");
        std::fs::write(
            &routes,
            json!({"routes": [{
                "anchor": vault.join(".anchor").to_string_lossy(),
                "here": vault.join("Docs").to_string_lossy(),
                "there": repo.join("Docs").to_string_lossy(),
                "direction": "two-way"
            }]})
            .to_string(),
        )
        .unwrap();
        assert_eq!(
            mirror_route_anchor_in(&repo.join("Docs/x.md"), &routes),
            Some(vault.clone())
        );
        assert_eq!(
            mirror_route_anchor_in(&repo.join("Docs/sub/deep.md"), &routes),
            Some(vault.clone())
        );
        assert_eq!(mirror_route_anchor_in(&repo.join("src/code.rs"), &routes), None);
        assert_eq!(mirror_route_anchor_in(&repo.join("Docs/x.md"), &td.join("missing.json")), None);
        let _ = std::fs::remove_dir_all(&td);
    }

    #[test]
    fn git_aspect_from_traits() {
        assert_eq!(git_aspect_of(&["Commit".into(), "anchor-base".into()]), "commit");
        assert_eq!(git_aspect_of(&["x".into()]), "");
    }

    #[test]
    fn content_kinds() {
        assert_eq!(content_kind("a/b.md"), Some("markdown"));
        assert_eq!(content_kind("a/b.MD"), Some("markdown"));
        assert_eq!(content_kind("a/b.rs"), Some("rust"));
        assert_eq!(content_kind("a/b.txt"), None);
        assert_eq!(content_kind("noext"), None);
    }

    #[test]
    fn daemon_timeout_by_moment() {
        // T013: a pending tool call gets the short leash; post-hoc moments
        // keep the patient one.
        assert_eq!(daemon_timeout("tool:pre:Edit"), Duration::from_secs(2));
        assert_eq!(daemon_timeout("tool:pre:Bash"), Duration::from_secs(2));
        assert_eq!(daemon_timeout("write:markdown"), Duration::from_secs(20));
        assert_eq!(daemon_timeout("session:start"), Duration::from_secs(20));
    }

    #[test]
    fn slow_daemon_gives_up_inside_timeout() {
        // T013: an alive-but-slow daemon (accepts, never answers) must cost
        // at most ~the moment timeout — never fall into the 20-retry spawn
        // loop. A listener that accepts and sleeps stands in for a busy daemon.
        use std::os::unix::net::UnixListener;
        let td = std::env::temp_dir().join(format!("warden-rs-slow-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&td);
        std::fs::create_dir_all(&td).unwrap();
        std::env::set_var("WARDEN_HOME", &td); // no daemon.cmd → spawn is a no-op
        let listener = UnixListener::bind(td.join("daemon.sock")).unwrap();
        let handle = std::thread::spawn(move || {
            if let Ok((mut conn, _)) = listener.accept() {
                let mut buf = [0u8; 65536];
                let _ = conn.read(&mut buf); // swallow the request, never reply
                std::thread::sleep(Duration::from_secs(3));
            }
        });
        let t0 = std::time::Instant::now();
        let resp = daemon_request(&json!({"op": "ping"}), Duration::from_millis(300));
        let elapsed = t0.elapsed();
        assert!(resp.is_none(), "no answer expected from the mute daemon");
        assert!(
            elapsed < Duration::from_secs(2),
            "gave up in {elapsed:?} — must not stack retries against a slow daemon"
        );
        std::env::remove_var("WARDEN_HOME");
        let _ = handle.join();
        let _ = std::fs::remove_dir_all(&td);
    }

    #[test]
    fn daemon_cmd_script_parsing() {
        // Audit 2026-07-12 W2: the stale-path check must find the script token in
        // both the quoted (path with spaces) and bare forms.
        assert_eq!(
            daemon_cmd_script("python3 '/a b/warden_daemon.py' --serve"),
            Some(PathBuf::from("/a b/warden_daemon.py"))
        );
        assert_eq!(
            daemon_cmd_script("python3 /plain/warden_daemon.py --serve"),
            Some(PathBuf::from("/plain/warden_daemon.py"))
        );
        assert_eq!(daemon_cmd_script("python3 "), None);
        assert_eq!(daemon_cmd_script(""), None);
    }

    #[test]
    fn budget_advisory_mirrors_python() {
        assert_eq!(budget_ms("tool:pre:Bash", false), 2.0);
        // owed Python round-trip → the post-hoc rate, even at tool:pre
        assert_eq!(budget_ms("tool:pre:Bash", true), 10.0);
        assert_eq!(budget_ms("tool:post:Write", false), 10.0);
        assert_eq!(budget_ms("write:markdown", false), 10.0);
        assert_eq!(budget_ms("session:start", false), 100.0);
        assert!(over_budget("write:markdown", 9.9, false).is_none());
        assert!(over_budget("tool:pre:Bash", 4.0, true).is_none(), "IPC floor inside owed budget");
        let warn = over_budget("write:markdown", 25.0, false).unwrap();
        assert!(warn.contains("OVER-BUDGET write:markdown") && warn.contains("budget 10 ms"), "{warn}");
    }
}
