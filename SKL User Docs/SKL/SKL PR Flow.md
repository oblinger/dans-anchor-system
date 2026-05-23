# /pr-flow

`/pr-flow` is the iterative PR-based development workflow — each PR is a small feature unit that you review before it merges. Claude works on a `feature/{name}-work` branch, batches commits until roughly 300 lines (configurable: "PR flow 500"), opens a PR from `-work` into `-base`, surfs the Files tab in your browser, and **stops** to wait for your review. You give feedback or say "done" / "PR flow"; the cycle iterates until the feature is complete, then a final PR from `-base` to `main` lands the whole thing.

Two key rules: Claude always stops after surfing a PR (never continues without your feedback), and if it's waiting on you without a PR up it calls `alert` so you know. Variant: **"PR flow bulk"** spins up ~4 parallel agents and owns the full cycle without per-PR review — batched by parent milestone. The full procedure lives in `CAB Skills/CAB PR Flow.md` (find it with `ha -p CAB`).
