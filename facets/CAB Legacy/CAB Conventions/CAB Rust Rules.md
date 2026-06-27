---
description: Workspace layout, shared util crate, Cargo conventions
---
# CAB Rust Rules

The CAB conventions for Rust-based anchors — Cargo workspace layout, shared util crates, and standard justfile recipes.

Conventions for Rust-based anchors that use a Cargo workspace with multiple crates.

See also [[CAB Repository Structure]] for general repo conventions and [[CAB Code Repository]] for the .anchor code: key pattern.


# Reference Example
---

The CAE project as a Rust workspace with two member crates and a shared util dependency:

```
~/ob/proj/CAE/cae-example/
├── Cargo.toml                  Workspace root
├── Cargo.lock
├── justfile
├── README.md
├── core/                       Library crate
│   ├── Cargo.toml
│   └── src/lib.rs
├── cli/                        Binary crate
│   ├── Cargo.toml
│   └── src/main.rs
└── target/
```

The workspace root `Cargo.toml`:

```toml
[workspace]
members = ["core", "cli"]
resolver = "2"
```

A member crate `cli/Cargo.toml`:

```toml
[package]
name = "tsk-cli"
version = "0.1.0"
edition = "2021"

[dependencies]
tsk-core = { path = "../core" }
```

---



# Format Specification


## Workspace Structure

A Rust anchor uses a Cargo workspace at the repo root. Member crates live in subdirectories, each with its own `Cargo.toml`.

- The workspace root `Cargo.toml` declares `[workspace]` with a `members` list and `resolver = "2"`
- Member crates reference each other via `path = "../{crate}"` dependencies
- `Cargo.lock` is committed for binary projects, gitignored for pure library projects


## Shared Util Crate

When a project suite (like ClaudiMux) has multiple repos that share common code, factor the shared logic into a `-utils` crate. Each workspace member depends on it via a local path:

```toml
[dependencies]
cmx-utils = { path = "../../cmx-utils" }
```

Conventions:
- The util crate lives as a sibling repo under the same `~/ob/proj/` grouping folder
- Name it `{suite}-utils` (e.g., `cmx-utils` for the ClaudiMux suite)
- Keep it focused — common types, helpers, and shared config only
- Each consuming repo references it via relative `path` in `Cargo.toml`


## Justfile — Rust Recipes

Rust projects use the standard justfile recipes (see [[CAB Repository Structure]]) mapped to Cargo commands:

```just
default:
    @just --list

build:
    cargo build

rebuild:
    cargo clean && cargo build

test:
    cargo test

lint:
    cargo clippy -- -D warnings
    cargo fmt -- --check

check: lint test

dev:
    cargo build

clean:
    cargo clean
```

Add `run` for binary crates:

```just
run *ARGS:
    cargo run -- {{ARGS}}
```

# BRIEF

- **This file is the authoritative Rust-flavor convention spec** within CAB — sibling to other language/runtime rule files; cited by anchors whose `.anchor` declares `code: rust`. Edit when Rust-ecosystem conventions evolve (workspace shape, shared-crate pattern, justfile recipes).
- **Scope is Rust-specific Cargo/workspace conventions** — what to put in `Cargo.toml`, how member crates relate, the `-utils` shared-crate pattern, and the Rust mapping of standard justfile recipes. Generic repo layout (top-level files, README shape, justfile presence) belongs in [[CAB Repository Structure]]; the `.anchor` code-key mechanism belongs in [[CAB Code Repository]] — link out, do not inline.
- **Inclusion test** — a rule belongs here only if it is (a) Rust-specific AND (b) applies across multiple Rust anchors. Per-project Cargo settings, crate-specific dependency choices, and one-off recipes live in the project's own docs, not here.
- **Two structural zones**: the `# Reference Example` (a single concrete worked example — CAE) and the `# Format Specification` (the actual prescriptive rules). Keep them separate; do not pile new prescriptive rules into the reference example, and do not invent new examples in the spec section.
- **Naming conventions are load-bearing**: `{suite}-utils` for shared crates (e.g. `cmx-utils`), `resolver = "2"` in workspace root, `path = "../{crate}"` for member-to-member deps. Changing any of these breaks downstream anchors that follow this spec.
- **Justfile recipes mirror the standard set** in [[CAB Repository Structure]] — `build`, `rebuild`, `test`, `lint`, `check`, `dev`, `clean`, plus `run` for binary crates. Do not add Rust-only recipes here that diverge from the cross-language standard names; if a new standard recipe is needed, propose it in `CAB Repository Structure` first, then mirror here.
- **Don't pile non-Rust content here**: Python conventions, shell-script rules, or general code-style guidance belong in their own CAB facets. This file is Rust and only Rust.
