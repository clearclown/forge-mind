# Contributing to forge-mind

## Scope

`forge-mind` is the self-improvement layer (L3) of the
[Forge](https://github.com/clearclown/forge) ecosystem. In-scope contributions:

- New `MetaOptimizer` implementations (rule-based, ML-based, hybrid)
- New `Benchmark` implementations
- Better budget gating policies
- Improved harness serialization formats (TOML, YAML)
- Documentation
- Tests for edge cases (zero-budget, infinite ROI, etc.)

Out of scope:

- The CU ledger / lending — that's `forge` (Rust)
- Inference execution — that's `forge-mesh`
- Agent discovery / marketplace — that's `forge-agora`

## Setup

```bash
git clone https://github.com/clearclown/forge-mind
cd forge-mind
uv venv
uv pip install -e ".[dev]"
pytest
```

## Code style

- Python 3.10+
- 100-char lines (ruff)
- Strict type annotations (`mypy --strict`)
- Module-level docstrings
- Dataclasses for public types

## Checks

```bash
pytest          # tests
ruff format .   # autoformat
ruff check .    # lint
mypy src/       # type-check
```

## PR guidelines

1. Branch from `main`. Use `feat/*`, `fix/*`, `docs/*`, `test/*`.
2. One logical change per PR.
3. Tests for new behavior. Failing-before / passing-after style.
4. `CHANGELOG.md` entry under `[Unreleased]`.
5. All checks pass locally before pushing.

## Adding a new MetaOptimizer

1. Implement `MetaOptimizer.propose(current, benchmark) -> ImprovementProposal`
2. The proposed harness should be a NEW version (use `current.evolve(...)`)
3. Set `cu_cost_to_propose` honestly — this gates budget consumption
4. Add a test that exercises the optimizer end-to-end via `ImprovementCycleRunner`

## Adding a new Benchmark

1. Inherit from `Benchmark`
2. `run(harness) -> BenchmarkResult` must be deterministic for the same harness
3. Set `cu_consumed` to whatever real cost the benchmark incurred (0 for in-memory)
4. Add a test that verifies determinism

## Code of conduct

Be kind. Critique technical decisions, not people.
