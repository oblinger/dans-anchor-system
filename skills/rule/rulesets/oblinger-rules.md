# Oblinger's Rules — retired to [[R-ob]]

**This file is a redirect** (2026-07-05, F218 § Housekeeping — R-single-source-of-truth-01 applied to the catalog itself). The canonical home of the user's portable rules is the **[[R-ob]] umbrella** at `library/Rulesets/R-ob/`; the legacy content here duplicated it and the distinct residue (Python check patterns, one Rust fallback shape, the per-project audit convention) was absorbed into R-ob in the same pass:

- OB-R01 (config through the data singleton) → [[R-ob-state-mgt]]-01
- OB-R02 (state through the data singleton) → [[R-ob-state-mgt]]-02
- OB-R03 (no hardcoded config values) → [[R-ob-state-mgt]]-03
- OB-R05 (no silent fallbacks) → [[R-ob-observability]]-01

Projects that synced from this file (`/rule sync`) now sync from R-ob; HA's `HA Rules.md` § Inherited Rules pointer moved in the same pass.
