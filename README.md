# forge-mind — ARCHIVED (2026-04-07)

> **This Python scaffold has been rewritten in Rust and merged into the main
> Forge workspace.** For the current implementation, see:
>
> **[clearclown/forge — crates/forge-mind](https://github.com/clearclown/forge/tree/main/crates/forge-mind)**

---

## Why

The Forge ecosystem is a 5-layer distributed LLM inference protocol. L0 (inference)
and L1 (economy) were already Rust. Keeping L2/L3/L4 in Python created a language
boundary, pinned semantics twice, and fractured the dependency graph.

In Phase 7 (2026-04-07) forge-bank / forge-mind / forge-agora were ported bit-for-bit
into the clearclown/forge Cargo workspace as `crates/forge-bank`, `crates/forge-mind`,
and `crates/forge-agora`. Every constant, formula, and validation rule from the
Python scaffolds is preserved. The Rust tests (53 / 53 / 42 = 148) cover every
Python test and then some.

All numeric constants are now centralized in
[forge-economics/spec/parameters.md §11](https://github.com/clearclown/forge-economics/blob/main/spec/parameters.md)
as the single source of truth — `forge-mind` constants live in §11 (CU budget
hard limits 5k/cycle, 50k/day, 20 cycles/day; ROI gates min_score_delta=0.01,
min_roi_threshold=1.0, roi_cu_per_score_unit=100k).

## What was ported

| Python file | Rust file |
|-------------|-----------|
| `src/forge_mind/types.py` | `crates/forge-mind/src/types.rs` |
| `src/forge_mind/harness.py` | `crates/forge-mind/src/harness.rs` |
| `src/forge_mind/budget.py` | `crates/forge-mind/src/budget.rs` |
| `src/forge_mind/benchmark.py` | `crates/forge-mind/src/benchmark.rs` |
| `src/forge_mind/meta_optimizer.py` | `crates/forge-mind/src/meta_optimizer.rs` |
| `src/forge_mind/cycle.py` | `crates/forge-mind/src/cycle.rs` |
| `src/forge_mind/agent.py` | `crates/forge-mind/src/agent.rs` |

## This repo's role going forward

This repository is kept **for design provenance only**. The Python sources under
`src/forge_mind/` and the tests under `tests/` document the original v0.1 scaffold
that the Rust implementation was derived from. They are tagged `v0.1.0-python-scaffold`.

New feature work, bug fixes, and API changes happen in
[clearclown/forge/crates/forge-mind](https://github.com/clearclown/forge/tree/main/crates/forge-mind).
This repo is archived — please do not open issues or PRs here.

## License

MIT (unchanged).
