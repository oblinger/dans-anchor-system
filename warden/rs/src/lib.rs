//! Warden performance engine — the fire-time hot path (F213 / M3).
//!
//! This is the Rust port of the moment dispatch in `warden_fire.py`: given a
//! compiled anchor's IR (`rules-ir.json`, produced by `warden_compile.py`) and a
//! runtime moment, compute **which rules fire** and the steers the declarative
//! ones emit. It is deliberately behaviour-identical to the Python reference (the
//! oracle) — the differential harness (`test_warden_rust.py`) runs the same IR
//! through both and diffs the fire plan byte-for-byte.
//!
//! Scope is the ms-budget-critical selection path, exactly as F213 § Design pins
//! it: the moment→rule dispatch table, active-set gating (a rule's keying trait ∈
//! the anchor's declared traits), the declarative `where`/`if` residual (the
//! fixed-vocabulary `guards`), and the declarative `tell`/`deny` action steers.
//! A rule carrying its **own Python** (`body_py`/`guard_py`) is not evaluated
//! here — its firing/steer is deferred to the resident Python interpreter over
//! IPC (F213 § Design, the "one logic language" rule). The plan records that a
//! Python round-trip is owed (`Dispatch::PythonBody` / `PythonGuard`) so the
//! selection is fully decided in Rust and only the body execution crosses the
//! boundary.

use serde::Deserialize;
use serde_json::Value;
use std::collections::HashMap;

pub mod hook;

/// The compiled corpus, deserialized from `rules-ir.json`.
#[derive(Debug, Deserialize)]
pub struct Ir {
    /// moment string → ordered candidate rule ids (the indexed dispatch bucket).
    #[serde(default)]
    pub moments: HashMap<String, Vec<String>>,
    /// rule id → row.
    #[serde(default)]
    pub rules: HashMap<String, Rule>,
    /// trait name → rule ids it keys (the active-set index).
    #[serde(default)]
    pub traits: HashMap<String, Vec<String>>,
    #[serde(default)]
    pub schema: u32,
}

#[derive(Debug, Deserialize)]
pub struct Rule {
    pub id: String,
    #[serde(default)]
    pub action: Option<Action>,
    #[serde(default)]
    pub body_py: Option<String>,
    #[serde(default)]
    pub guard_py: Option<String>,
    #[serde(default)]
    pub guards: Vec<Guard>,
}

#[derive(Debug, Deserialize)]
pub struct Action {
    #[serde(default)]
    pub kind: Option<String>,
    #[serde(default)]
    pub text: Option<String>,
    #[serde(default)]
    pub reason: Option<String>,
}

/// A declarative `{key, op, value}` guard (the F210 fixed vocabulary).
#[derive(Debug, Deserialize)]
pub struct Guard {
    pub key: String,
    pub op: String,
    pub value: Value,
}

/// The moment-fire interpretation environment a guard reads (the subset of
/// `warden_fire.build_ctx` that declarative guards touch). Python-body rules read
/// a richer ctx over IPC; this is only what Rust needs to decide selection.
#[derive(Debug, Clone, Default)]
pub struct Ctx {
    /// `ctx.git_aspect` — a string ("" when absent), or JSON null.
    pub git_aspect: Value,
    /// `ctx.mode` — a string, or JSON null.
    pub mode: Value,
    /// `ctx.traits`.
    pub traits: Vec<String>,
    /// `ctx.facets`.
    pub facets: Vec<String>,
}

impl Ctx {
    /// Mirror of `warden_fire._ctx_value`: map a guard key to the ctx value.
    fn value(&self, key: &str) -> Value {
        match key {
            "git-aspect" => self.git_aspect.clone(),
            "mode" => self.mode.clone(),
            "trait" => Value::Array(self.traits.iter().map(|s| Value::String(s.clone())).collect()),
            "facet" => Value::Array(self.facets.iter().map(|s| Value::String(s.clone())).collect()),
            _ => Value::Null,
        }
    }
}

/// How a fired rule is dispatched — the plan the differential harness compares.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Dispatch {
    /// A declarative `tell`/`deny` action; the steer text is decided in Rust.
    Declarative(String),
    /// A fired rule whose action is not a steer (`judge`/`check`/`track`): it
    /// entered the dispatch but contributes no steer, exactly as Python's
    /// `fire()` appends nothing for a non-`tell`/`deny` action.
    ActionOther,
    /// A rule carrying a Python body — its steer is owed to the resident
    /// interpreter (IPC round-trip), never executed in Rust.
    PythonBody(String),
    /// A rule gated by a Python guard — whether it fires is a Python decision;
    /// Rust has taken it as far as active-set + declarative guards allow.
    PythonGuard(String),
}

/// One fired rule in the plan (fire order preserved from the moment bucket).
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Fired {
    pub rule_id: String,
    pub dispatch: Dispatch,
}

/// The traits that key a rule (mirror of `warden_fire._rule_traits`).
fn rule_traits<'a>(ir: &'a Ir, rule_id: &str) -> Vec<&'a str> {
    ir.traits
        .iter()
        .filter(|(_, ids)| ids.iter().any(|i| i == rule_id))
        .map(|(t, _)| t.as_str())
        .collect()
}

/// Active iff some trait that keys the rule is in the anchor's trait set (mirror
/// of `warden_fire.is_active`).
pub fn is_active(ir: &Ir, rule_id: &str, anchor_traits: &[String]) -> bool {
    rule_traits(ir, rule_id)
        .iter()
        .any(|t| anchor_traits.iter().any(|a| a == t))
}

/// Evaluate one declarative guard against ctx (mirror of `warden_fire.eval_guard`,
/// including the `in`/`has` list/scalar and substring semantics Python's `in`
/// operator gives).
pub fn eval_guard(guard: &Guard, ctx: &Ctx) -> bool {
    let actual = ctx.value(&guard.key);
    match guard.op.as_str() {
        "eq" => actual == guard.value,
        "in" => match &guard.value {
            // `actual in value` when value is a list → membership
            Value::Array(items) => items.iter().any(|i| *i == actual),
            // else `actual in [value]` → equality
            other => actual == *other,
        },
        // `value in (actual or [])`: Python `in` over a list is membership, over a
        // string is substring, over null/empty is false.
        "has" => match &actual {
            Value::Array(items) => items.iter().any(|i| *i == guard.value),
            Value::String(s) => guard.value.as_str().map_or(false, |v| s.contains(v)),
            _ => false,
        },
        _ => false,
    }
}

/// Compute the fire plan for a moment (mirror of `warden_fire.fire`'s selection,
/// stopping short of running Python bodies). Rules keyed under a different moment
/// are never in the bucket, so they never appear — the indexed-dispatch property
/// F211 pins.
pub fn fire_plan(ir: &Ir, moment: &str, ctx: &Ctx, anchor_traits: &[String]) -> Vec<Fired> {
    let mut plan = Vec::new();
    let bucket = match ir.moments.get(moment) {
        Some(b) => b,
        None => return plan,
    };
    for rule_id in bucket {
        let row = match ir.rules.get(rule_id) {
            Some(r) => r,
            None => continue,
        };
        if !is_active(ir, rule_id, anchor_traits) {
            continue;
        }
        if !row.guards.iter().all(|g| eval_guard(g, ctx)) {
            continue;
        }
        // Python-guard rules: firing is a Python decision — defer it, don't drop.
        if let Some(gp) = &row.guard_py {
            plan.push(Fired {
                rule_id: rule_id.clone(),
                dispatch: Dispatch::PythonGuard(gp.clone()),
            });
            continue;
        }
        if let Some(bp) = &row.body_py {
            plan.push(Fired {
                rule_id: rule_id.clone(),
                dispatch: Dispatch::PythonBody(bp.clone()),
            });
        } else if let Some(act) = &row.action {
            let kind = act.kind.as_deref().unwrap_or("");
            if kind == "tell" || kind == "deny" {
                let steer = act
                    .text
                    .clone()
                    .filter(|s| !s.is_empty())
                    .or_else(|| act.reason.clone())
                    .unwrap_or_default();
                plan.push(Fired {
                    rule_id: rule_id.clone(),
                    dispatch: Dispatch::Declarative(steer),
                });
            } else {
                plan.push(Fired {
                    rule_id: rule_id.clone(),
                    dispatch: Dispatch::ActionOther,
                });
            }
        }
    }
    plan
}

/// Serialize a fire plan to the JSON shape the differential harness compares:
/// `[{"rule_id","kind","steer"}]`, fire order preserved.
pub fn plan_to_json(plan: &[Fired]) -> Value {
    Value::Array(
        plan.iter()
            .map(|f| {
                let (kind, steer) = match &f.dispatch {
                    Dispatch::Declarative(s) => ("declarative", Some(s.clone())),
                    Dispatch::ActionOther => ("action-other", None),
                    Dispatch::PythonBody(_) => ("python-body", None),
                    Dispatch::PythonGuard(_) => ("python-guard", None),
                };
                let mut obj = serde_json::Map::new();
                obj.insert("rule_id".into(), Value::String(f.rule_id.clone()));
                obj.insert("kind".into(), Value::String(kind.into()));
                obj.insert("steer".into(), steer.map_or(Value::Null, Value::String));
                Value::Object(obj)
            })
            .collect(),
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    fn syn_ir() -> Ir {
        // Mirrors the SYN fixture in test_warden_rust.py so the Rust unit layer
        // and the Python differential layer exercise the same shape.
        let json = serde_json::json!({
            "schema": 1,
            "moments": {"tool:pre:Bash": ["S1", "S2", "S3", "S4", "S5"]},
            "rules": {
                "S1": {"id": "S1", "action": {"kind": "tell", "text": "beware"},
                       "body_py": null, "guard_py": null,
                       "guards": [{"key": "git-aspect", "op": "eq", "value": "commit"}]},
                "S2": {"id": "S2", "action": {"kind": "deny", "reason": "no push"},
                       "body_py": null, "guard_py": null,
                       "guards": [{"key": "trait", "op": "has", "value": "push"}]},
                "S3": {"id": "S3", "action": {"kind": "judge"},
                       "body_py": null, "guard_py": null, "guards": []},
                "S4": {"id": "S4", "action": null, "body_py": null,
                       "guard_py": "guard_S4", "guards": []},
                "S5": {"id": "S5", "action": null, "body_py": "body_S5",
                       "guard_py": null, "guards": []},
            },
            "traits": {"syn": ["S1", "S2", "S3", "S4", "S5"]},
        });
        serde_json::from_value(json).unwrap()
    }

    fn ctx(git: &str, mode: Option<&str>, traits: &[&str], facets: &[&str]) -> Ctx {
        Ctx {
            git_aspect: Value::String(git.to_string()),
            mode: mode.map_or(Value::Null, |m| Value::String(m.to_string())),
            traits: traits.iter().map(|s| s.to_string()).collect(),
            facets: facets.iter().map(|s| s.to_string()).collect(),
        }
    }

    fn ids(plan: &[Fired]) -> Vec<&str> {
        plan.iter().map(|f| f.rule_id.as_str()).collect()
    }

    #[test]
    fn inactive_trait_fires_nothing() {
        let ir = syn_ir();
        let plan = fire_plan(&ir, "tool:pre:Bash", &ctx("commit", None, &["other", "_base"], &[]),
                             &["other".into(), "_base".into()]);
        assert!(plan.is_empty());
    }

    #[test]
    fn indexed_dispatch_ignores_other_moments() {
        let ir = syn_ir();
        let at = vec!["syn".to_string(), "_base".to_string()];
        let plan = fire_plan(&ir, "session:start", &ctx("", None, &["syn", "_base"], &[]), &at);
        assert!(plan.is_empty(), "no rules keyed at session:start");
    }

    #[test]
    fn guards_and_dispatch_arms() {
        let ir = syn_ir();
        let at = vec!["syn".to_string(), "push".to_string(), "_base".to_string()];
        let plan = fire_plan(&ir, "tool:pre:Bash",
                             &ctx("commit", None, &["syn", "push", "_base"], &[]), &at);
        // S1 tell (git eq commit), S2 deny (trait has push), S3 action-other (judge),
        // S4 python-guard, S5 python-body — fire order preserved.
        assert_eq!(ids(&plan), ["S1", "S2", "S3", "S4", "S5"]);
        assert_eq!(plan[0].dispatch, Dispatch::Declarative("beware".into()));
        assert_eq!(plan[1].dispatch, Dispatch::Declarative("no push".into()));
        assert_eq!(plan[2].dispatch, Dispatch::ActionOther);
        assert_eq!(plan[3].dispatch, Dispatch::PythonGuard("guard_S4".into()));
        assert_eq!(plan[4].dispatch, Dispatch::PythonBody("body_S5".into()));
    }

    #[test]
    fn guard_gating_drops_unmatched() {
        let ir = syn_ir();
        let at = vec!["syn".to_string(), "_base".to_string()];
        // no commit aspect, no push trait → S1 and S2 gated out; S3/S4/S5 survive.
        let plan = fire_plan(&ir, "tool:pre:Bash", &ctx("", None, &["syn", "_base"], &[]), &at);
        assert_eq!(ids(&plan), ["S3", "S4", "S5"]);
    }

    #[test]
    fn eval_guard_ops() {
        let c = ctx("commit", Some("drive"), &["syn", "push"], &["a", "b"]);
        let g = |k: &str, op: &str, v: Value| Guard { key: k.into(), op: op.into(), value: v };
        assert!(eval_guard(&g("git-aspect", "eq", Value::String("commit".into())), &c));
        assert!(!eval_guard(&g("git-aspect", "eq", Value::String("push".into())), &c));
        assert!(eval_guard(&g("git-aspect", "has", Value::String("omm".into())), &c)); // substring
        assert!(eval_guard(&g("trait", "has", Value::String("push".into())), &c));
        assert!(!eval_guard(&g("trait", "has", Value::String("nope".into())), &c));
        assert!(eval_guard(&g("mode", "in", serde_json::json!(["drive", "land"])), &c));
        assert!(eval_guard(&g("mode", "in", Value::String("drive".into())), &c)); // in-scalar
        assert!(eval_guard(&g("facet", "has", Value::String("a".into())), &c)); // list membership
        assert!(!eval_guard(&g("facet", "has", Value::String("z".into())), &c));
        assert!(!eval_guard(&g("mode", "bogus-op", Value::Null), &c)); // unknown op → false
    }
}
