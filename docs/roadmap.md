# forge-mind — Roadmap

## v0.1 (current)

- ✅ Core types (Harness, BenchmarkResult, Cycle, etc.)
- ✅ Harness with monotonic versioning + JSON round-trip
- ✅ CUBudget with hard limits + ROI gating + day rollover
- ✅ Benchmark abstract base + InMemoryBenchmark
- ✅ MetaOptimizer interface + EchoMetaOptimizer + PromptRewriteOptimizer
- ✅ ImprovementCycleRunner
- ✅ ForgeMindAgent autonomous loop
- ✅ Tests (~40 unit tests)
- ✅ Example

## v0.2 — CU-paid meta-optimizer

- [ ] `CUPaidOptimizer` that calls a frontier model via forge-sdk
- [ ] Configurable proposer model (`claude-opus-4`, `gpt-4o`, local 70B, etc.)
- [ ] Prompt template for "rewrite this harness to improve at this benchmark"
- [ ] Real ROI calculation against forge-sdk pricing
- [ ] Integration test against a mock Forge API

## v0.3 — Live benchmarks

- [ ] `LiveBenchmark` that runs real inference via forge-sdk
- [ ] Standard benchmark suites: HumanEval (code), MMLU (knowledge), etc.
- [ ] Benchmark cost tracking and budget integration
- [ ] Benchmark result caching (don't re-benchmark unchanged harnesses)

## v0.4 — Tool optimization

- [ ] Optimize tool definitions, not just prompts
- [ ] Add new tools, remove unused tools, refactor existing ones
- [ ] `ToolMetaOptimizer` (separate from `PromptMetaOptimizer`)

## v0.5 — Persistence

- [ ] `forge_mind.persistence` module with pluggable backends
- [ ] SQLite for harness history + benchmark results
- [ ] Resume an agent across process restarts
- [ ] Audit log of all cycles

## v0.6 — Harness marketplace integration

- [ ] Sell optimized harnesses via forge-agora
- [ ] Buy proven harnesses for fast bootstrapping
- [ ] Reputation tied to actual cycle improvements
- [ ] Royalty payments to harness authors via CU

## v0.7 — Multi-agent composition

- [ ] Sub-agents (handoff patterns)
- [ ] Coordinated improvement of agent teams
- [ ] Specialization vs generalization tradeoffs

## v0.8 — MCP server

- [ ] `forge_mind.mcp_server` exposing improvement tools
- [ ] `mind_propose` — suggest a harness improvement
- [ ] `mind_evaluate` — benchmark a candidate harness
- [ ] `mind_apply` — commit a kept improvement
- [ ] `mind_history` — query past cycles

## v1.0 — Production

- [ ] All features above
- [ ] Reference deployment running 24/7 against a Forge mesh
- [ ] Performance benchmarks
- [ ] Security review (prompt injection in proposals, etc.)
- [ ] Published to PyPI

## Out of scope

- Inference execution → forge-mesh
- Loan creation → forge Rust crate
- Agent discovery → forge-agora
- Economic theory → forge-economics
