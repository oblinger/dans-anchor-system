---
description: "example ruleset — the rules a snapshot manifest.txt must satisfy"
---
# RULESET R-fex-manifest
include::
where:: `**/manifest.txt`
description:: The structural rules every snapshot manifest must satisfy. The worked example of the **ruleset** kind — paired with the [[FEX Manifest|manifest]] it governs.

An anchor adopts it with `include:: [[R-fex-manifest]]`; an audit then checks each manifest against the rules below. (A real ruleset is an `# RULESET` doc, not an anchor page — no dispatch table — so this file is itself an example of the format.)

### RULE R-fex-manifest-01 — one fact per line
description:: Every non-blank line in the manifest matches the key: value format with no blank lines in the block.
if:: `any(not re.match(r'^[a-z][a-z0-9_]*: .+$', l) for l in file.lines if l.strip())`
A non-blank line doesn't match `key: value` format — every line must be `[a-z][a-z0-9_]*: <value>` with no blank lines in the block so the parser stays trivial.

**Why:** a manifest is machine-parsed on restore; one `key: value` per line keeps the parser trivial.

### RULE R-fex-manifest-02 — required keys present
description:: The manifest contains all four required keys: label, commit, branch, and created.
if:: `not all(re.search(r'^' + k + r':', file.text, re.M) for k in ['label', 'commit', 'branch', 'created'])`
The manifest is missing one or more required keys (`label`, `commit`, `branch`, `created`) — a restore can't identify or place a bundle without all four.

**Why:** a restore can't identify or place a bundle without them.

### RULE R-fex-manifest-03 — paths are bundle-relative
description:: No manifest value is an absolute path; all paths are bundle-relative so the bundle restores identically anywhere.
if:: `re.search(r'^[a-z][a-z0-9_]*: /', file.text, re.M)`
A manifest value starts with `/` — paths must be bundle-relative (no absolute paths) so the bundle restores the same way wherever it is unpacked.

**Why:** a bundle must restore the same way wherever it is unpacked.
