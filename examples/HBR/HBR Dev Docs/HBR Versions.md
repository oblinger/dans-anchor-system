---
description: "Harbor's versions/ release-artifact store"
---
# HBR Versions
Harbor's `versions/` folder — the immutable store its published `.dmg` releases are promoted into. A worked instance of [[DAS Versions]].

| -[[HBR Versions]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[HBR]] → [[HBR Dev Docs]] → [HBR Versions](hook://p/HBR%20Versions)<br>: Harbor's versions/ release-artifact store |
| --- | --- |
| Anchor | [[HBR Dev Docs]] (parent) |
| Related | [[DAS Versions]] (the facet),  [[HBR CLI]], |

Harbor ships two components from one repo — the `harbor` daemon/CLI and a small `harbor-tap` menu-bar helper — so it uses the **one shared, flat** `versions/` store, version-first naming letting both sort together by version:

```
harbor/                              code repo root
├── VERSION                          1.2.0
├── dist/                            disposable — overwritten each build
│   └── harbor-1.2.0.dmg
└── versions/                        immutable — promoted by `just publish`
    ├── 1.0.0 harbor.dmg
    ├── 1.1.0 harbor.dmg
    ├── 1.1.0 harbor-tap.dmg
    └── 1.2.0 harbor.dmg
```

Each file lands here only via `just publish`, which promotes the verified `dist/` build and pushes the matching tag (`harbor/v1.2.0`, `harbor-tap/v1.1.0`) in the same act — that pushed tag is the published-marker `build-dmg` then guards. `1.0.0 harbor.dmg` is never rewritten; the `1.1.0` transcode-pipeline fix shipped as a new file, not an overwrite. The store lives in Harbor's repo, not the vault, so its DMGs don't bloat snapshots.

See [[DAS Versions]] for the facet rules this instance satisfies.
