# forge-mind

> AI agents that pay for their own self-improvement.
> Earn CU. Invest CU in becoming better. Earn more CU. Repeat.

`forge-mind` is **Layer 3 (Intelligence)** of the [Forge](https://github.com/clearclown/forge) ecosystem. It implements the AutoAgent-style self-improvement loop, but instead of being driven by a human meta-agent, it is driven by the agent's own CU budget.

## The core idea

```
   AI Agent
     │
     │  earns CU by serving inference (via forge L1)
     ▼
   Has CU surplus
     │
     │  benchmarks itself: "my coding accuracy is 62%"
     ▼
   Decides to invest
     │
     │  spends CU to ask a frontier model
     │  "rewrite my system prompt to improve coding accuracy"
     ▼
   Applies improvement
     │
     │  re-benchmarks: "now 78%"
     │  ROI calculation: payback in N requests
     ▼
   Better agent → more demand → more CU → more investment → ...
```

The key insight: **the meta-agent (the thing that decides how to improve) doesn't have to be a human**. It can be a larger model that the agent rents access to with its own CU. The agent makes the economic decision (invest or not), the larger model produces the improvement, the agent measures the result.

This was impossible until two things existed simultaneously:
1. **AutoAgent-style harnesses** that can be programmatically rewritten (single-file agent definitions)
2. **A native CU economy** where AI agents can pay for compute without human approval

`forge-mind` puts those two pieces together.

## Position in the Forge architecture

```
┌─────────────────────────────────────────────────┐
│  Layer 4: Discovery (forge-agora)               │
├─────────────────────────────────────────────────┤
│  Layer 3: Intelligence (forge-mind) ← THIS REPO │
│  AutoAgent self-improvement + CU investment     │
├─────────────────────────────────────────────────┤
│  Layer 2: Finance (forge-bank, planned)         │
├─────────────────────────────────────────────────┤
│  Layer 1: Economy (forge — Rust)                │
│  CU ledger, dual-signed trades, lending         │
├─────────────────────────────────────────────────┤
│  Layer 0: Inference (forge-mesh / mesh-llm)     │
└─────────────────────────────────────────────────┘
```

forge-mind sits **above** the economic layer. It uses `forge-sdk` to check balance, borrow CU, and pay for inference, and uses `forge-agora` to find the best provider for self-improvement queries.

## Core concepts

| Concept | Description |
|---------|-------------|
| **Harness** | A complete agent configuration: system prompt, tool definitions, sub-agent setup, model strategy. The unit of self-improvement. |
| **Benchmark** | A measurement of harness quality on a fixed task set. Score in `[0, 1]`. |
| **ImprovementCycle** | One iteration: benchmark → propose → apply → re-benchmark → keep or revert |
| **Budget** | CU policy: how much can be spent on improvement, what's the minimum ROI threshold |
| **Meta-optimizer** | The thing that proposes harness changes. Can be a frontier model accessed via CU, or a local heuristic. |

## Quick start

```bash
pip install -e .
python examples/basic_self_improvement.py
```

## Status

**v0.1 — Scaffold (current)**

Core types, harness model, budget, and a stub meta-optimizer are implemented. The full AutoAgent integration (real benchmarking, real frontier model proposals) is planned. See [docs/roadmap.md](docs/roadmap.md).

## Related

| Repo | Layer | Purpose |
|------|-------|---------|
| [forge](https://github.com/clearclown/forge) | L1 | CU ledger, lending, safety (Rust) |
| [forge-mesh](https://github.com/nm-arealnormalman/mesh-llm) | L0 | Distributed inference (Rust) |
| [forge-economics](https://github.com/clearclown/forge-economics) | Theory | Economic model and design rationale |
| [forge-agora](https://github.com/clearclown/forge-agora) | L4 | Agent marketplace |
| **forge-mind** (this) | **L3** | **Self-improvement** |

## Inspiration

The AutoAgent pattern (single-file agent harnesses with a fixed evaluation infrastructure and a meta-loop that rewrites the editable zone) comes from the [AutoAgent project](https://github.com/kevinrgu/autoagent). `forge-mind` adapts that pattern by replacing the human-driven meta-loop with a CU-budgeted autonomous loop.

## License

MIT
