# forge-mind — Architecture

## The model in one diagram

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
           ┌────────────────────────┐
           │ ImprovementCycleRunner │
           │  - benchmark baseline  │
           │  - ask optimizer       │
           │  - benchmark candidate │
           │  - decide KEEP/REVERT  │
           └────────────────────────┘
                   │
                   │  uses
                   ▼
            ┌──────────────────┐
            │  MetaOptimizer   │
            │ (proposes new    │
            │  harness)        │
            └──────────────────┘
```

## The cycle in detail

```
   ┌─────────────────────┐
   │  current harness    │
   │  version = N        │
   └──────────┬──────────┘
              │
              │  benchmark(harness)  → score_N
              ▼
   ┌─────────────────────┐
   │  baseline result    │
   │  score = 0.62       │
   └──────────┬──────────┘
              │
              │  optimizer.propose(harness, baseline)
              │  cost: cu_propose
              ▼
   ┌─────────────────────┐
   │  proposal           │
   │  harness version    │
   │  N+1 (parent = N)   │
   └──────────┬──────────┘
              │
              │  benchmark(proposal.harness) → score_{N+1}
              ▼
   ┌─────────────────────┐
   │  candidate result   │
   │  score = 0.78       │
   └──────────┬──────────┘
              │
              │  delta = 0.78 - 0.62 = +0.16
              │  cu_invested = cu_propose + 2 * cu_benchmark
              │  cu_return_estimate = delta * roi_cu_per_score_unit
              │  roi = cu_return_estimate / cu_invested
              ▼
   ┌─────────────────────┐
   │  decision           │
   │  budget.is_worth?   │
   │   yes → KEEP        │
   │   no  → REVERT      │
   └─────────────────────┘
```

## Key invariants

1. **Versions are monotonic.** Every harness change increments `version` and sets `parent_version`.
2. **Reverts are free.** A failed cycle leaves the agent at the previous version. The CU spent on benchmarks and the optimizer is sunk cost.
3. **Budgets are hard caps.** The runner will refuse to spend even one CU above the daily limit.
4. **Benchmarks are deterministic.** Same harness, same benchmark, same score. This is what makes the cycle decision reliable.
5. **The optimizer is pluggable.** Tests use stubs; production uses CU-paid frontier-model optimizers.

## Where state lives

| Component | State | Persistence |
|-----------|-------|-------------|
| `Harness` | immutable (mutations via `evolve()`) | JSON serialization |
| `CUBudget` | mutable counters | not persisted yet (caller's job) |
| `Benchmark` | optimizer-defined | depends on impl |
| `ForgeMindAgent` | history list of cycles | not persisted yet |

For v0.1, all state is in-memory. v0.5 will add persistence backends.

## Comparison with AutoAgent

| Aspect | AutoAgent (Kevin Gu, 2026) | forge-mind |
|--------|----------------------------|------------|
| Meta loop driven by | Human via Claude Code | Autonomous via CU budget |
| Harness format | Single Python file | Pydantic dataclass |
| Benchmark execution | Docker containers | Pluggable Benchmark interface |
| Cost gating | None (human decides) | Hard CU budget enforcement |
| Improvement suggestion | Claude Code reads/writes the file | MetaOptimizer.propose() |
| Revert mechanism | git revert | Just don't call `harness = proposal.harness` |
| Deployment target | CI / overnight runs | Embedded in agent runtime |

forge-mind is what AutoAgent becomes when there's no human in the loop and the meta-cost has to be paid in real money (CU).

## Out of scope for v0.1

- Real frontier-model meta-optimizer (`CUPaidOptimizer`)
- Real benchmark execution against forge-sdk
- Distributed harness marketplace
- Multi-agent harness composition / handoff orchestration
- Persistent state backends

These are tracked in `docs/roadmap.md`.
