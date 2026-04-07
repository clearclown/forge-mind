# Changelog

All notable changes to forge-mind documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [0.1.0] — 2026-04-07

### Added
- Initial scaffold for the forge-mind self-improvement layer (Layer 3)
- Core types: `Harness`, `BenchmarkResult`, `ImprovementProposal`,
  `ImprovementCycle`, `CycleDecision`, `ModelStrategy`, `ToolDefinition`
- `Harness.evolve()` for monotonic versioning with parent tracking
- JSON serialization round-trip for harnesses
- `CUBudget` with hard daily/per-cycle limits, ROI gating, day rollover
- `Benchmark` abstract base + `InMemoryBenchmark` for deterministic testing
- `MetaOptimizer` interface + `EchoMetaOptimizer` + `PromptRewriteOptimizer`
- `ImprovementCycleRunner` — single benchmark → propose → benchmark → decide
- `ForgeMindAgent` — high-level autonomous self-improvement loop facade
  with `improve(n_cycles)`, `stats()`, history tracking
- Test suite with ~40 unit tests covering harness, budget, benchmark,
  cycle, and agent
- Example: `examples/basic_self_improvement.py`
- Project metadata: README, CLAUDE.md, LICENSE, CONTRIBUTING, pyproject.toml

### Notes
- This is a **scaffold release**. The `CUPaidOptimizer` (real frontier model
  via forge-sdk) and live benchmarks are planned for v0.2.
