# CAB Rust Rules

Conventions for Rust-based anchors that use a Cargo workspace with multiple crates.

See also [[CAB Repository Structure]] for general repo conventions and [[CAB Code Repository]] for the Code symlink pattern.


# Reference Example
---

The TSK project as a Rust workspace with two member crates and a shared util dependency:

```
~/ob/proj/TSK/task-runner/
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
