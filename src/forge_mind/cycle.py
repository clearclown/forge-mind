"""Single improvement cycle execution.

A cycle is the smallest atomic unit of self-improvement:

  baseline benchmark
        ↓
  meta-optimizer proposes change
        ↓
  candidate benchmark
        ↓
  decision: KEEP / REVERT / DEFER
"""

from __future__ import annotations

from forge_mind.benchmark import Benchmark
from forge_mind.budget import CUBudget
from forge_mind.harness import Harness
from forge_mind.meta_optimizer import MetaOptimizer
from forge_mind.types import (
    BenchmarkResult,
    CycleDecision,
    ImprovementCycle,
    ImprovementProposal,
)


class ImprovementCycleRunner:
    """Runs one improvement cycle end-to-end.

    The runner enforces budget gating, runs benchmarks, asks the optimizer
    for a proposal, evaluates the proposal, and returns a fully-populated
    `ImprovementCycle` regardless of outcome.
    """

    def __init__(
        self,
        benchmark: Benchmark,
        optimizer: MetaOptimizer,
        budget: CUBudget,
        *,
        roi_cu_per_score_unit: int = 100_000,
    ) -> None:
        """Construct a cycle runner.

        Args:
            benchmark: How to measure harness quality.
            optimizer: How to propose changes.
            budget: Spending policy.
            roi_cu_per_score_unit: Estimated CU return per 1.0 of score
                improvement. Used for ROI gating. Tune to your domain.
        """
        self.benchmark = benchmark
        self.optimizer = optimizer
        self.budget = budget
        self.roi_cu_per_score_unit = roi_cu_per_score_unit

    def run_one(self, harness: Harness) -> ImprovementCycle:
        """Execute one improvement cycle on the given harness."""
        # Day rollover check.
        self.budget.maybe_reset_day()

        # Gate: are we allowed to start a cycle today?
        if not self.budget.can_start_cycle():
            return self._defer_cycle(
                harness,
                reason="daily cycle limit reached",
            )

        self.budget.record_cycle_start()

        # 1. Baseline benchmark
        baseline = self.benchmark.run(harness)
        self._record_benchmark_cost(baseline)

        # 2. Meta-optimizer proposes a change
        proposal = self.optimizer.propose(harness, baseline)

        # Gate: can we afford the proposal cost?
        if proposal.cu_cost_to_propose > 0:
            if not self.budget.can_spend(proposal.cu_cost_to_propose):
                return ImprovementCycle(
                    baseline=baseline,
                    proposal=proposal,
                    candidate=baseline,  # didn't actually run the candidate
                    decision=CycleDecision.DEFER,
                    delta=0.0,
                    roi_cu=0.0,
                )
            self.budget.record_spend(proposal.cu_cost_to_propose)

        # 3. Candidate benchmark
        candidate = self.benchmark.run(proposal.proposed_harness)
        self._record_benchmark_cost(candidate)

        # 4. Decision
        delta = candidate.score - baseline.score
        cu_invested = proposal.cu_cost_to_propose + baseline.cu_consumed + candidate.cu_consumed
        cu_return_estimate = int(max(0.0, delta) * self.roi_cu_per_score_unit)
        roi = cu_return_estimate / cu_invested if cu_invested > 0 else float("inf")

        keep = self.budget.is_improvement_worth_keeping(
            score_delta=delta,
            cu_invested=cu_invested,
            cu_return_estimate=cu_return_estimate,
        )
        decision = CycleDecision.KEEP if keep else CycleDecision.REVERT

        return ImprovementCycle(
            baseline=baseline,
            proposal=proposal,
            candidate=candidate,
            decision=decision,
            delta=delta,
            roi_cu=roi if roi != float("inf") else 0.0,
        )

    # ---------- Helpers ----------

    def _record_benchmark_cost(self, result: BenchmarkResult) -> None:
        if result.cu_consumed > 0 and self.budget.can_spend(result.cu_consumed):
            self.budget.record_spend(result.cu_consumed)

    @staticmethod
    def _defer_cycle(harness: Harness, *, reason: str) -> ImprovementCycle:
        # Construct a no-op cycle to surface the deferral.
        zero_result = BenchmarkResult(
            harness_version=harness.version,
            score=0.0,
            sample_count=1,
            duration_ms=0,
            cu_consumed=0,
        )
        zero_proposal = ImprovementProposal(
            proposed_harness=harness,
            proposer_model="(deferred)",
            rationale=reason,
            cu_cost_to_propose=0,
        )
        return ImprovementCycle(
            baseline=zero_result,
            proposal=zero_proposal,
            candidate=zero_result,
            decision=CycleDecision.DEFER,
            delta=0.0,
            roi_cu=0.0,
        )
