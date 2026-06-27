# System Suppressions

The vault-wide LINT suppression table — file/target/rule patterns that are silently exempt from doc-coverage lint across every project, with no per-project exception counted.

These are suppressed globally for all projects. Not counted in the per-project exception count.

| Module          | Target             | Rule                 | Reason                                     |
| --------------- | ------------------ | -------------------- | ------------------------------------------ |
| *.toml          |                    | *                    | Config files                               |
| *.json          |                    | *                    | Data files                                 |
| *.yaml          |                    | *                    | Config files                               |
| *.yml           |                    | *                    | Config files                               |
| *.lock          |                    | *                    | Lock files                                 |
| *.js            |                    | source-no-module-doc | JavaScript config, not primary API          |
| build.rs        |                    | *                    | Rust build script                          |
| Package.swift   |                    | *                    | Swift package manifest                     |
| mod.rs          |                    | *                    | Rust module re-export                      |
| lib.rs          |                    | *                    | Rust crate root                            |
| main.rs         |                    | *                    | Binary entry point                         |
| __init__.py     |                    | *                    | Python package marker                      |
| conftest.py     |                    | *                    | Pytest configuration                       |
| setup.py        |                    | *                    | Python packaging                           |
| *Tests/*        |                    | class-undocumented   | Test files — use test module doc format     |
| *Tests/*        |                    | field-undocumented   | Test files                                 |
| *Tests/*        |                    | method-undocumented  | Test files                                 |
| *tests/*        |                    | class-undocumented   | Test files                                 |
| *tests/*        |                    | field-undocumented   | Test files                                 |
| *tests/*        |                    | method-undocumented  | Test files                                 |
| *Tests          |                    | folder-no-doc        | Test folder — use test design doc           |
| *tests          |                    | folder-no-doc        | Test folder — use test design doc           |
| */src           |                    | folder-no-doc        | Source root — covered by architecture doc   |
| */src/          |                    | folder-no-doc        | Source root — covered by architecture doc   |
| src             |                    | folder-no-doc        | Source root — covered by architecture doc   |
| *.swift         | applicationShould* | method-undocumented  | AppKit delegate boilerplate                |
| *.swift         | applicationWill*   | method-undocumented  | AppKit delegate boilerplate                |
| *.swift         | *.main             | method-undocumented  | Swift entry point                          |
| *               | Methods            | class-stale-doc      | Table header word, not a class             |
| *               | Properties         | class-stale-doc      | Table header word                          |
| *               | Types              | class-stale-doc      | Table header word                          |
| *               | Class              | class-stale-doc      | Table header word                          |
| *               | Field              | class-stale-doc      | Table header word                          |
| *               | Variant            | class-stale-doc      | Table header word                          |
| *               | Name               | class-stale-doc      | Table header word                          |
| *               | Function           | class-stale-doc      | Table header word                          |
| *               | Functions          | class-stale-doc      | Table header word                          |
| *               | Structs            | class-stale-doc      | Table header word                          |
| *               | Step               | class-stale-doc      | Table header word                          |
| *               | Constant           | class-stale-doc      | Table header word                          |
| *               | Files              | class-stale-doc      | Table header word                          |
| *               | Property           | class-stale-doc      | Table header word                          |
| *               | Method             | class-stale-doc      | Table header word                          |

# BRIEF

- **This file IS the authoritative global suppression list** for LINT — every row removes a (Module, Target, Rule) combination from doc-coverage lint across every project; LINT reads this file directly, so the table shape is load-bearing.
- **This file is NOT for per-project exceptions** — those are graded with For/Against justification under each project's own rules/exceptions surface (see [[FCT Ruleset]]); only patterns that are universally noise-not-signal belong here.
- **Inclusion test** — a row earns a place only when the (file kind, target, rule) combination would generate lint noise on essentially every project the user owns (config files, language-mandated scaffolding like `__init__.py` / `mod.rs`, test directories, table-header words misread as class names). If even one project would legitimately want that warning, it belongs in that project's exceptions, not here.
- **Column conventions** — `Module` is a glob over file paths (`*.toml`, `*Tests/*`, `*/src`), `Target` is an optional symbol-name glob (left blank when the rule applies to the whole file), `Rule` is either a specific LINT rule id or `*` for all rules, and `Reason` is a short human phrase. Preserve the column-aligned spacing — the table is read by humans scanning patterns.
- **Don't pile generic markdown / vault-wide policy here** — that lives in [[R-markdown]], [[CLAUDE.md]], or the relevant [[FCT Ruleset]] facet; this page is strictly the LINT suppression matrix.
- **Load-bearing constraint — the table header word suppressions** (Methods / Properties / Class / Field / Method / etc. under `class-stale-doc`) exist because doc-table headers parse as class-name candidates; do not remove those rows without first fixing the parser that mistakes them.

