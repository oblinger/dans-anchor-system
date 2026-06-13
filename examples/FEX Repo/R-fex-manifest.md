---
description: "example rule set — the rules a snapshot manifest.txt must satisfy"
---
# RULESET R-fex-manifest
description:: The structural rules every snapshot manifest must satisfy. The worked example of the **rule-set** kind — paired with the [[FEX Manifest|manifest]] it governs.

An anchor adopts it with `include:: [[R-fex-manifest]]`; an audit then checks each manifest against the rules below. (A real rule set is an `# RULESET` doc, not an anchor page — no dispatch table — so this file is itself an example of the format.)

### RULE R-fex-manifest-01 — one fact per line (checked)
**Check pattern:** every non-blank line matches `^[a-z][a-z0-9_]*: .+$`; no blank lines inside the block.
**Why:** a manifest is machine-parsed on restore; one `key: value` per line keeps the parser trivial.

### RULE R-fex-manifest-02 — required keys present (checked)
**Check pattern:** the keys `label`, `commit`, `branch`, and `created` all appear.
**Why:** a restore can't identify or place a bundle without them.

### RULE R-fex-manifest-03 — paths are bundle-relative (sampled)
**Check pattern:** no value is an absolute path (none begins with `/`).
**Why:** a bundle must restore the same way wherever it is unpacked.
