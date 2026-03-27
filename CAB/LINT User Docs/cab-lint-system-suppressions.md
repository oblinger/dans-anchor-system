# System Suppressions

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
