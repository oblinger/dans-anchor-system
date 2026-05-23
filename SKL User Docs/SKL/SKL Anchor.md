# /Anchor

The `anchor` skill is the low-level toolkit for working with **anchors** — the standardized named folders that this whole system is built around. It bundles scripts and actions for auditing an anchor's docs against its source code, managing its `.anchor` config file, scanning the vault to discover every anchor, and tracking activity status across projects.

You usually won't invoke `/anchor` directly — higher-level skills like `/audit`, `/tidy`, `/lint`, and the `/code` family delegate to it under the hood. Reach for it when you need the underlying operation by itself, or when you're debugging anchor-level behavior. The full spec for what an anchor actually is — its slug, traits, required files — lives in `[[SKD Anchor]]`.
