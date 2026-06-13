---
description: Skip files already in the catalog by content hash during ingest
---

## Open Questions

_None — design is clean._

### Resolved

- **Q1 — hash the whole file or a sampled prefix?** — **Resolution:** whole-file BLAKE3. Sampled-prefix hashing risks collisions across re-encodes that share a header; ingest is not latency-critical, so the full read is acceptable. Landed in Design § Hashing. See [[HBR Decisions]] (content-hash dedup).

# [[HBR]] · F001 — Content-Hash Dedup

## Summary

During `harbor ingest <path>`, the Deduper folds out files already present in the catalog by comparing a content hash, so re-running ingest on the same library adds nothing and a file moved between folders is not duplicated. This is the spine of US-HBR-1 — "point Harbor at a directory and it appears, deduped, in the catalog."

## Success Criteria

**Tier: Required** (v1 blocker — US-HBR-1 acceptance depends on it).

- Re-running `harbor ingest` on an already-ingested path writes zero new rows.
- A file moved or renamed on disk resolves to the existing catalog row, not a new one.
- Two byte-identical files at different paths produce one catalog entry with both paths recorded.

## Interface

```rust
/// Returns the existing media id if this content hash is already cataloged.
pub fn dedup(catalog: &Catalog, hash: ContentHash) -> Option<MediaId>;

/// BLAKE3 over the full file contents.
pub fn content_hash(path: &Path) -> io::Result<ContentHash>;
```

## Design

The Importer computes `content_hash` (whole-file BLAKE3) before writing a row; the Deduper queries the catalog's unique index on `content_hash`. On a hit it appends the new path to the existing row's path set rather than inserting. The three Ingest stages meet only at the catalog (per [[HBR Architecture]]), so dedup is a pure catalog read plus a conditional write — no cross-stage coupling.

## Status

Done — shipped in v1; covered by ingest integration tests.
