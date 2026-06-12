# EXP Backlog

Ideas, bugs, and deferred work for the EXP remote experimentation system.

## Bugs

- [x] Orphaned `_done` after SSH abort — **Fixed:** added nonce protocol. `exp exe` writes `EXP-PID-TIMESTAMP` on line 1 of `_run.cmd`, watcher echoes it back in `_done`. Polling only accepts matching nonce; stale `_done` from previous runs is detected, logged, and cleaned up automatically. Health shows "Stale _done (from aborted run)" for nonce-tagged orphans. Backward-compatible with legacy (no-nonce) format.
- [x] Worker `exp exe` can't run while watcher is occupied — **Fixed:** replaced blocking `wait $CMD_PID` in watcher with a polling loop that also checks for new `_run.cmd`. If a new command arrives while the old one is running, the watcher kills the old process group and immediately starts the new one (preemption). Shows "PREEMPTED by new command" in watcher output. Old command gets exit 143 (SIGTERM) written to `_done` with its nonce so the original caller can detect it.

## Research

- [x] Best GPU for our workloads (speed, regardless of price) — **RTX 5090 is the fastest available option** for small-model work (Pythia-410M). Comprehensive comparison of all GPU tiers:
  - **Why 5090 wins for small models:** For a ~1.6GB model, raw TFLOPS are misleading — the workload is memory-bound with low arithmetic intensity. What matters most: (1) L2 cache size (5090: 98MB vs H100: 50MB — model layers partially fit in cache), (2) clock speed (5090: 2.9 GHz vs H100: 1.8 GHz — 60% faster per-operation), (3) memory bandwidth (secondary since cache hits reduce DRAM round-trips).
  - **Our data:** 5090 did Q2_06 causal tracing in 98s vs RTX 6000 Ada's 190s (~2x faster). Beat PRO 6000 Blackwell on LoRA fine-tuning (38 min vs 40-45 min). Molecular dynamics benchmarks (similar compute profile): H200 135 ns/day > PRO 6000 122 > RTX 5090 110 > H100 ~90 > 6000 Ada 72.
  - **H200:** Only GPU that might beat 5090 (~23% faster in mol-dynamics benchmark). 4.8 TB/s HBM3e bandwidth partially compensates for lower clock. Available on vast.ai at $3-4/hr (6-8x the cost of 5090). Worth a head-to-head test on Q2_06 if curious.
  - **B200:** Most powerful on paper (2,250 TFLOPS FP16, 8 TB/s bandwidth) but ~1.5 GHz clock and datacenter L2 cache limit small-model throughput. Sold out through mid-2026. Not on vast.ai. Only wins for models >2B params.
  - **H100 SXM:** 990 TFLOPS but 1.8 GHz clock and 50MB L2 hurt on small models. Actually slower than 5090 in mol-dynamics benchmark. Only wins at 8-GPU NVLink scaling or large models.
  - **A100:** Previous gen, slower than all above. 5090 beats it by ~14% on 8B model inference despite being a "consumer" GPU.
  - **AMD MI300X:** Best bandwidth on paper (5.3 TB/s) but AMD PyTorch software stack achieves only 47% utilization vs NVIDIA's 73%. Real-world 14% slower than H100 for training. Not recommended.
  - **RTX 4090:** Still competent (high clock, 96MB L2 cache) but ~44% slower than 5090 on CV, ~72% slower on NLP tasks.
  - **RTX 5090 Ti / Titan Blackwell:** Rumored Q3 2026, board-level work underway, no specs. Previous gen Titan prototype never shipped. Don't wait for it.
  - **Verdict: stick with RTX 5090 for all current workloads.** Only the H200 is a plausible contender, at 6-8x the cost.

## Improvements

- [x] `exp health --fix` auto-clean — **Done:** `exp health --fix` auto-removes stale `_done` and stale `_run.cmd` files on remotes. Shows cyan `[fix]` tag for each cleaned item. Works with `-r name` for single remote or all remotes. Compatible with `-w` watch mode.
- [x] Auto-alert maintainer on issues — **Done:** `exp health -w --alert <tmux-pane>` sends critical issue alerts to a specified tmux pane (e.g. a Claude Code session). Only fires when the set of critical issues changes (won't repeat same alert). Sends "[EXP ALERT] All clear" when issues resolve. Uses the `-w` interval for check frequency. Example: `exp health -w 60 --alert %14` checks every 60s and alerts pane %14.
- [ ] Auto-clean old experiment data from remotes — old experiment output (especially activations/embeddings from Q2_01 at 3.9G) accumulates on remotes and fills disk. `exp push` uses `--delete` which mirrors the local folder, but output/ dirs generated on the remote persist. Two options: (a) clean all non-current experiments from `/workspace` at the start of each `exp exe` push, or (b) clean the remote workspace when `exp clear-task` is called (end of task). Option (b) is safer — it runs after results have been pulled. Should preserve the fine-tuned model checkpoint (`Q1_01_finetune_baseline/`) which multiple experiments depend on.
