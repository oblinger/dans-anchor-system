---
name: rust
description: >
  Discipline. The Rust flavor of [[DSC code-repo]] — Cargo workspace layout
  (workspace root + member crates, resolver 2, path dependencies), the
  {suite}-utils shared-crate pattern for multi-repo project suites, and the
  Rust mapping of the standard justfile recipes (cargo build / test / clippy +
  fmt / clean). Rust-specific and cross-project only; per-project Cargo
  settings live in that project's own docs.
user_invocable: false
---

# Rust Discipline

The Rust-flavor conventions for code repositories — how a Rust repo lays out its Cargo workspace, how a project suite shares code through a util crate, and how the standard justfile recipe names ([[DSC code-repo]]) map onto Cargo commands.

- **Workspace at root** — a Rust repo is a Cargo workspace; member crates live in subdirectories, each with its own `Cargo.toml`.
- **Shared util crate** — a multi-repo project suite factors common code into one `{suite}-utils` crate consumed via relative `path` dependencies.
- **Standard recipes, Cargo-mapped** — the justfile mirrors the cross-language recipe names (`build`, `test`, `lint`, `check`, …); it never invents Rust-only names that diverge from the standard set.
- **Rust and only Rust** — a rule belongs here only if it is Rust-specific AND applies across multiple Rust repos. Generic repo shape belongs in [[DSC code-repo]]; per-project Cargo settings and one-off recipes belong in the project's own docs.

This is a discipline, not a user-invocable skill — Rust-shaped anchors and repo-scaffolding skills cite it via `[[DSC rust]]`.

## Workspace structure

A Rust repo uses a Cargo workspace at the repo root. Member crates live in subdirectories, each with its own `Cargo.toml`.

- **Workspace root** — the root `Cargo.toml` declares `[workspace]` with a `members` list and `resolver = "2"`:

```toml
[workspace]
members = ["core", "cli"]
resolver = "2"
```

- **Member-to-member deps** — member crates reference each other via `path = "../{crate}"` dependencies:

```toml
[package]
name = "tsk-cli"
version = "0.1.0"
edition = "2021"

[dependencies]
tsk-core = { path = "../core" }
```

- **Cargo.lock policy** — `Cargo.lock` is committed for binary projects, gitignored for pure library projects.

## Shared util crate

When a project suite has multiple repos that share common code, factor the shared logic into a `-utils` crate. Each workspace member depends on it via a local path:

```toml
[dependencies]
cmx-utils = { path = "../../cmx-utils" }
```

Conventions:

- **Sibling repo** — the util crate lives as a sibling repo under the same project grouping folder.
- **Naming** — name it `{suite}-utils` (e.g., `cmx-utils` for the ClaudiMux suite).
- **Keep it focused** — common types, helpers, and shared config only.
- **Path references** — each consuming repo references it via relative `path` in `Cargo.toml`.

## Justfile — Rust recipes

Rust repos map the standard justfile recipes ([[DSC code-repo]]) to Cargo commands:

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

If a new standard recipe is needed, propose it in [[DSC code-repo]] first, then mirror it here.

## Related

- [[DSC code-repo]] — the language-agnostic repository shape this discipline specializes.
