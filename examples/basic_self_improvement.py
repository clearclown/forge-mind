"""Basic forge-mind self-improvement example.

Shows the autonomous self-improvement loop in action with an in-memory
benchmark and a simple prompt-rewrite optimizer. No real CU is spent;
this demonstrates the cycle without needing a live Forge node.

A real deployment would replace `InMemoryBenchmark` with a benchmark that
runs actual inference (paid in CU) and `PromptRewriteOptimizer` with a
`CUPaidOptimizer` that calls a frontier model via forge-sdk.
"""

from forge_mind import (
    CUBudget,
    ForgeMindAgent,
    Harness,
    InMemoryBenchmark,
    PromptRewriteOptimizer,
)


def main() -> None:
    # 1. Define the initial harness
    initial = Harness(
        system_prompt="You are an assistant.",
        description="initial naive prompt",
    )

    # 2. A scoring function that rewards specific keywords
    #
    # Each beneficial keyword in the prompt adds 0.05 to the score.
    # The cap is 1.0.
    BENEFICIAL_KEYWORDS = ["concise", "step-by-step", "verify", "honest"]

    def score(h: Harness) -> float:
        base = 0.5
        for kw in BENEFICIAL_KEYWORDS:
            if kw in h.system_prompt:
                base += 0.1
        return min(1.0, base)

    benchmark = InMemoryBenchmark(scoring_fn=score, sample_count=50)

    # 3. A meta-optimizer that adds the next missing beneficial keyword
    keyword_iter = iter(BENEFICIAL_KEYWORDS)

    def transform(prompt: str) -> str:
        # Find the next keyword that isn't in the prompt yet
        for kw in BENEFICIAL_KEYWORDS:
            if kw not in prompt:
                return f"{prompt} Be {kw}."
        return prompt  # all keywords present; no improvement

    optimizer = PromptRewriteOptimizer(
        transform=transform,
        proposer_model="example-rewriter",
        cu_cost_per_proposal=100,  # simulate paying 100 CU per proposal
    )

    # 4. Configure budget
    budget = CUBudget(
        max_cu_per_cycle=10_000,
        max_cu_per_day=50_000,
        max_cycles_per_day=10,
        min_score_delta=0.05,
        min_roi_threshold=0.0,  # accept any positive improvement
    )

    # 5. Create the agent and let it self-improve
    agent = ForgeMindAgent(
        harness=initial,
        benchmark=benchmark,
        optimizer=optimizer,
        budget=budget,
    )

    print("=== Initial harness ===")
    print(f"  prompt: {agent.harness.system_prompt}")
    print(f"  version: {agent.harness.version}")
    print(f"  baseline score: {benchmark.run(agent.harness).score:.3f}")
    print()

    # Run up to 10 improvement cycles
    cycles = agent.improve(n_cycles=10)

    print(f"=== Ran {len(cycles)} cycles ===")
    for i, c in enumerate(cycles, 1):
        print(
            f"  cycle {i}: {c.decision.value:7} "
            f"baseline={c.baseline.score:.3f} "
            f"candidate={c.candidate.score:.3f} "
            f"delta={c.delta:+.3f}"
        )
    print()

    print("=== Final harness ===")
    print(f"  prompt: {agent.harness.system_prompt}")
    print(f"  version: {agent.harness.version}")
    print(f"  final score: {benchmark.run(agent.harness).score:.3f}")
    print()

    print("=== Stats ===")
    for key, value in agent.stats().items():
        if isinstance(value, float):
            print(f"  {key:>20}: {value:.3f}")
        else:
            print(f"  {key:>20}: {value}")


if __name__ == "__main__":
    main()
