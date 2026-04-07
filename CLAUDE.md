# forge-mind — Development Guide

## What this is

`forge-mind` is **Layer 3 (Intelligence)** of the Forge ecosystem. It is a Python project that implements AutoAgent-style self-improvement loops where the meta-agent (the one proposing improvements) is paid for in CU rather than driven by a human.

Key insight: instead of a human running an outer loop saying "rewrite this prompt", the agent itself spends CU to ask a frontier model to rewrite its own prompt, measures the result, and decides to keep or revert.

## Architecture in one picture

```
                    ┌──────────────────────┐
                    │   ForgeMindAgent     │
                    │  (autonomous loop)   │
                    └──────────┬───────────┘
                               │
            ┌──────────────────┼──────────────────┐
            ▼                  ▼                  ▼
       ┌─────────┐       ┌───────────┐      ┌──────────┐
       │ Harness │       │  Budget   │      │Benchmark │
       │ (config)│       │   (CU)    │      │  Suite   │
       └────┬────┘       └─────┬─────┘      └─────┬────┘
            │                  │                  │
            └──────┬───────────┴──────────────────┘
                   ▼
            ┌──────────────────┐
            │  MetaOptimizer   │
            │ (proposes new    │
            │  harness via CU- │
            │  paid inference) │
            └──────────────────┘
                   │
                   │  uses
                   ▼
            ┌──────────────────┐         ┌──────────────────┐
            │   forge-sdk      │ ──────► │   forge node     │
            │ (CU operations)  │         │  (L1 economy)    │
            └──────────────────┘         └──────────────────┘
```

## Why Python

Same as `forge-agora`: integrates with the existing Python AI ecosystem (`forge-sdk`, `forge-cu-mcp`, `openai`, `anthropic`, `langchain`, `crewai`, `autogen`). The performance-critical path is the inference itself, which happens elsewhere (forge-mesh, OpenAI API, etc.).

## Repository layout

```
forge-mind/
├── README.md
├── CLAUDE.md (this file)
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── pyproject.toml
├── src/
│   └── forge_mind/
│       ├── __init__.py
│       ├── types.py            — Harness, BenchmarkResult, ImprovementCycle, Budget
│       ├── harness.py          — Harness model + serialization (TOML/JSON)
│       ├── budget.py           — CUBudget with spend tracking and ROI gating
│       ├── benchmark.py        — Benchmark abstract base + InMemoryBenchmark
│       ├── meta_optimizer.py   — Stub MetaOptimizer interface + CUPaidOptimizer
│       ├── cycle.py            — Single ImprovementCycle execution
│       └── agent.py            — ForgeMindAgent autonomous loop facade
├── tests/
│   ├── test_harness.py
│   ├── test_budget.py
│   ├── test_benchmark.py
│   ├── test_cycle.py
│   └── test_agent.py
├── docs/
│   ├── architecture.md
│   ├── self-improvement.md
│   └── roadmap.md
└── examples/
    ├── basic_self_improvement.py
    └── budgeted_loop.py
```

## Core types (`src/forge_mind/types.py`)

```python
@dataclass
class Harness:
    """A complete agent configuration. The unit of self-improvement."""
    system_prompt: str
    tools: list[ToolDefinition]
    model_strategy: ModelStrategy   # which model for which task
    sub_agents: list["Harness"]     # nested harnesses (handoffs)
    version: int                    # monotonic version counter
    parent_version: Optional[int]   # for revert tracking

@dataclass
class BenchmarkResult:
    harness_version: int
    score: float                    # 0.0-1.0
    sample_count: int
    duration_ms: int
    cu_consumed: int                # CU spent running the benchmark

@dataclass
class ImprovementProposal:
    proposed_harness: Harness
    proposer_model: str             # e.g., "claude-opus-4" or local 70B
    rationale: str                  # natural-language explanation
    cu_cost_to_propose: int         # what we paid the meta-model

@dataclass
class ImprovementCycle:
    baseline: BenchmarkResult
    proposal: ImprovementProposal
    candidate: BenchmarkResult
    decision: CycleDecision         # KEEP / REVERT / DEFER
    delta: float                    # candidate.score - baseline.score
    roi_cu: float                   # estimated CU return per CU invested

@dataclass
class CUBudget:
    """Spending limits for self-improvement."""
    max_cu_per_cycle: int
    max_cu_per_day: int
    min_score_delta: float          # must improve by at least this much
    min_roi_threshold: float        # CU return per CU spent
    spent_today_cu: int = 0
    cycles_today: int = 0
```

## Key design rules

1. **Reverts are free, improvements are paid for.** The cost of trying an improvement is the CU spent on the meta-optimizer + benchmark. If the improvement fails, the harness reverts at zero cost.

2. **Budgets are hard limits, not soft suggestions.** A CUBudget that says `max_cu_per_day = 1000` will never spend 1001, even if it would be a great improvement.

3. **Benchmarks are deterministic.** Same harness + same benchmark suite → same score. No randomness in evaluation.

4. **ROI is computed honestly.** If the benchmark improvement was 0.62 → 0.78, the ROI should reflect realistic future earnings, not a fantasy scenario.

5. **Versions are monotonic.** Every harness change bumps the version, with `parent_version` pointing to where it came from. This makes revert and audit trivial.

6. **The meta-optimizer is pluggable.** Default is `CUPaidOptimizer` which calls a frontier model. But you can pass any `MetaOptimizer` implementation for tests, local heuristics, or hybrid strategies.

## Integration with the Forge ecosystem

```
forge-mind agent
  │
  │  uses
  ▼
forge_sdk.ForgeClient   ─► /v1/forge/balance      (check budget)
                        ─► /v1/forge/credit       (check borrowing capacity)
                        ─► /v1/forge/borrow       (borrow if needed)
                        ─► /v1/chat/completions   (run benchmark + meta query)
                        ─► /v1/forge/repay        (after improvement pays off)
  │
  │  uses
  ▼
forge_agora.Marketplace ─► find best meta-optimizer provider
                        ─► reputation-checked (don't ask a known bad actor)
```

## Development commands

```bash
uv pip install -e ".[dev]"
pytest
ruff format .
ruff check .
mypy src/
```

## Naming and ownership note

Same as forge-agora: this repo is initially under `nm-arealnormalman/forge-mind` for tooling reasons. Will be **transferred to `clearclown` later**. All cross-references in code/docs assume the eventual `clearclown/forge-mind` URL.

## Out of scope for v0.1

- Real frontier-model meta-optimizer (we use a stub that returns its input)
- Real benchmark execution (we use in-memory deterministic benchmarks)
- Distributed harness marketplace (just local for now)
- Real CU spending against a Forge node (we use a mock client)
- Multi-agent harness composition / handoff orchestration

These come in v0.2+. See `docs/roadmap.md`.
