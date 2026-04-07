"""ForgeMindAgent — high-level autonomous self-improvement loop facade.

Wraps a Harness, a Benchmark, a MetaOptimizer, a CUBudget, and an
ImprovementCycleRunner into a single object that runs N cycles and tracks
the harness evolution.
"""

from __future__ import annotations

from forge_mind.benchmark import Benchmark
from forge_mind.budget import CUBudget
from forge_mind.cycle import ImprovementCycleRunner
from forge_mind.harness import Harness
from forge_mind.meta_optimizer import MetaOptimizer
from forge_mind.types import CycleDecision, ImprovementCycle


class ForgeMindAgent:
    """A self-improving agent driven by CU-budgeted cycles.

    Example:
        >>> from forge_mind import (
        ...     ForgeMindAgent, Harness, InMemoryBenchmark,
        ...     PromptRewriteOptimizer, CUBudget,
        ... )
        >>> harness = Harness(system_prompt="You are an assistant.")
        >>> benchmark = InMemoryBenchmark(
        ...     scoring_fn=lambda h: 0.6 if "concise" not in h.system_prompt else 0.85
        ... )
        >>> optimizer = PromptRewriteOptimizer(
        ...     transform=lambda p: p + " Be concise."
        ... )
        >>> agent = ForgeMindAgent(
        ...     harness=harness,
        ...     benchmark=benchmark,
        ...     optimizer=optimizer,
        ...     budget=CUBudget(),
        ... )
        >>> agent.improve(n_cycles=1)
        >>> agent.harness.system_prompt
        'You are an assistant. Be concise.'
        >>> agent.harness.version
        2
    """

    def __init__(
        self,
        harness: Harness,
        benchmark: Benchmark,
        optimizer: MetaOptimizer,
        budget: CUBudget | None = None,
    ) -> None:
        self.harness = harness
        self.benchmark = benchmark
        self.optimizer = optimizer
        self.budget = budget or CUBudget()
        self.runner = ImprovementCycleRunner(
            benchmark=self.benchmark,
            optimizer=self.optimizer,
            budget=self.budget,
        )
        self.history: list[ImprovementCycle] = []

    # ---------- Improvement loop ----------

    def improve(self, n_cycles: int = 1) -> list[ImprovementCycle]:
        """Run up to `n_cycles` improvement cycles.

        Stops early if the budget is exhausted or N cycles complete.
        Returns the list of cycles actually executed.
        """
        executed: list[ImprovementCycle] = []
        for _ in range(n_cycles):
            cycle = self.runner.run_one(self.harness)
            executed.append(cycle)
            self.history.append(cycle)

            if cycle.decision == CycleDecision.KEEP:
                self.harness = cycle.proposal.proposed_harness
            elif cycle.decision == CycleDecision.DEFER:
                # Budget hit a hard limit — stop the loop early.
                break
            # REVERT: keep current harness, try again next cycle
        return executed

    # ---------- Inspection ----------

    @property
    def cycle_count(self) -> int:
        return len(self.history)

    @property
    def kept_count(self) -> int:
        return sum(1 for c in self.history if c.decision == CycleDecision.KEEP)

    @property
    def reverted_count(self) -> int:
        return sum(1 for c in self.history if c.decision == CycleDecision.REVERT)

    @property
    def deferred_count(self) -> int:
        return sum(1 for c in self.history if c.decision == CycleDecision.DEFER)

    @property
    def total_cu_invested(self) -> int:
        return sum(
            c.proposal.cu_cost_to_propose + c.baseline.cu_consumed + c.candidate.cu_consumed
            for c in self.history
        )

    def stats(self) -> dict[str, int | float]:
        latest_score = self.history[-1].candidate.score if self.history else 0.0
        first_score = self.history[0].baseline.score if self.history else 0.0
        return {
            "harness_version": self.harness.version,
            "cycle_count": self.cycle_count,
            "kept": self.kept_count,
            "reverted": self.reverted_count,
            "deferred": self.deferred_count,
            "total_cu_invested": self.total_cu_invested,
            "first_score": first_score,
            "latest_score": latest_score,
            "score_delta": latest_score - first_score,
        }
