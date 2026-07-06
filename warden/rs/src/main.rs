//! `warden-rs` — the fire-time CLI over the Rust engine (F213).
//!
//! Reads a compiled `rules-ir.json` and a moment, computes the fire plan, and
//! prints it as JSON. The differential harness (`test_warden_rust.py`) drives this
//! against the Python reference and diffs the output byte-for-byte.
//!
//!   warden-rs fire --ir <path> --moment <m> \
//!       [--traits a,b,c] [--git-aspect commit] [--mode drive] [--facets x,y]
//!
//! `--traits` supplies both the anchor active-set and `ctx.traits` (they are the
//! same list in `warden_engine.fire`). Ctx defaults match `build_ctx`:
//! git_aspect "" , mode null, facets [].
//!
//! F213 phase 2 adds the live-dispatcher entry point (event JSON on stdin,
//! Python bodies via the resident daemon, always exits 0):
//!
//!   warden-rs hook

use std::process::exit;
use warden::{fire_plan, hook, plan_to_json, Ctx, Ir};

fn arg_val(args: &[String], flag: &str) -> Option<String> {
    args.iter().position(|a| a == flag).and_then(|i| args.get(i + 1).cloned())
}

fn csv(s: Option<String>) -> Vec<String> {
    s.map(|v| v.split(',').map(|t| t.trim().to_string()).filter(|t| !t.is_empty()).collect())
        .unwrap_or_default()
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.get(1).map(|s| s.as_str()) == Some("hook") {
        exit(hook::run_hook());
    }
    if args.get(1).map(|s| s.as_str()) != Some("fire") {
        eprintln!("usage: warden-rs fire --ir <path> --moment <m> [--traits ..] [--git-aspect ..] [--mode ..] [--facets ..]\n       warden-rs hook   (hook event JSON on stdin)");
        exit(2);
    }
    let ir_path = match arg_val(&args, "--ir") {
        Some(p) => p,
        None => {
            eprintln!("error: --ir <path> required");
            exit(2);
        }
    };
    let moment = match arg_val(&args, "--moment") {
        Some(m) => m,
        None => {
            eprintln!("error: --moment <m> required");
            exit(2);
        }
    };
    let traits = csv(arg_val(&args, "--traits"));
    // The implicit base trait every anchor carries (warden_fire.read_anchor_traits).
    let mut anchor_traits = traits.clone();
    if !anchor_traits.iter().any(|t| t == "anchor-base") {
        anchor_traits.push("anchor-base".to_string());
    }

    let ir_text = match std::fs::read_to_string(&ir_path) {
        Ok(t) => t,
        Err(e) => {
            eprintln!("error: cannot read {ir_path}: {e}");
            exit(1);
        }
    };
    let ir: Ir = match serde_json::from_str(&ir_text) {
        Ok(ir) => ir,
        Err(e) => {
            eprintln!("error: bad IR json: {e}");
            exit(1);
        }
    };

    let ctx = Ctx {
        git_aspect: arg_val(&args, "--git-aspect")
            .map(serde_json::Value::String)
            .unwrap_or(serde_json::Value::String(String::new())),
        mode: arg_val(&args, "--mode")
            .map(serde_json::Value::String)
            .unwrap_or(serde_json::Value::Null),
        traits: anchor_traits.clone(),
        facets: csv(arg_val(&args, "--facets")),
    };

    let plan = fire_plan(&ir, &moment, &ctx, &anchor_traits);
    println!("{}", plan_to_json(&plan));
}
