"""Tests for forge_mind.cycle."""

from forge_mind.benchmark import InMemoryBenchmark
from forge_mind.budget import CUBudget
from forge_mind.cycle import ImprovementCycleRunner
from forge_mind.harness import Harness
from forge_mind.meta_optimizer import EchoMetaOptimizer, PromptRewriteOptimizer
from forge_mind.types import CycleDecision


def make_runner(
    scoring_fn,
    optimizer,
    *,
    cu_cost_per_proposal: int = 0,
    cu_cost_per_benchmark: int = 0,
):
    benchmark = InMemoryBenchmark(
        scoring_fn=scoring_fn, cu_cost_per_run=cu_cost_per_benchmark
    )
    budget = CUBudget(min_score_delta=0.001, min_roi_threshold=0.0)
    return ImprovementCycleRunner(benchmark, optimizer, budget), budget


def test_no_change_proposal_results_in_revert():
    runner, _ = make_runner(
        scoring_fn=lambda h: 0.5,
        optimizer=EchoMetaOptimizer(),
    )
    cycle = runner.run_one(Harness(system_prompt="x"))
    # Echo optimizer doesn't change anything → score is identical → REVERT
    assert cycle.decision == CycleDecision.REVERT
    assert cycle.delta == 0.0


def test_improving_proposal_is_kept():
    def scoring(h):
        return 0.85 if "concise" in h.system_prompt else 0.5

    runner, _ = make_runner(
        scoring_fn=scoring,
        optimizer=PromptRewriteOptimizer(transform=lambda p: p + " concise"),
    )
    cycle = runner.run_one(Harness(system_prompt="hello"))
    assert cycle.decision == CycleDecision.KEEP
    assert cycle.delta == 0.85 - 0.5
    assert cycle.proposal.proposed_harness.version == 2


def test_regressing_proposal_is_reverted():
    def scoring(h):
        return 0.3 if "bad" in h.system_prompt else 0.7

    runner, _ = make_runner(
        scoring_fn=scoring,
        optimizer=PromptRewriteOptimizer(transform=lambda p: p + " bad"),
    )
    cycle = runner.run_one(Harness(system_prompt="hello"))
    assert cycle.decision == CycleDecision.REVERT
    assert cycle.delta < 0


def test_cycle_records_budget_spend():
    runner, budget = make_runner(
        scoring_fn=lambda h: 0.5,
        optimizer=PromptRewriteOptimizer(
            transform=lambda p: p,
            cu_cost_per_proposal=100,
        ),
        cu_cost_per_benchmark=10,
    )
    runner.run_one(Harness(system_prompt="x"))
    assert budget.spent_today_cu >= 100  # at least the proposal cost
    assert budget.cycles_today == 1


def test_proposal_too_expensive_is_deferred():
    runner, budget = make_runner(
        scoring_fn=lambda h: 0.5,
        optimizer=PromptRewriteOptimizer(
            transform=lambda p: p + "x",
            cu_cost_per_proposal=10_000_000,
        ),
    )
    cycle = runner.run_one(Harness(system_prompt="x"))
    assert cycle.decision == CycleDecision.DEFER


def test_daily_cycle_limit_defers():
    benchmark = InMemoryBenchmark(scoring_fn=lambda h: 0.5)
    optimizer = EchoMetaOptimizer()
    budget = CUBudget(max_cycles_per_day=2)
    runner = ImprovementCycleRunner(benchmark, optimizer, budget)
    runner.run_one(Harness(system_prompt="x"))
    runner.run_one(Harness(system_prompt="x"))
    cycle3 = runner.run_one(Harness(system_prompt="x"))
    assert cycle3.decision == CycleDecision.DEFER


def test_min_score_delta_gates_keep():
    def scoring(h):
        return 0.500 if h.version == 1 else 0.501  # tiny improvement

    benchmark = InMemoryBenchmark(scoring_fn=scoring)
    optimizer = PromptRewriteOptimizer(transform=lambda p: p + " ")
    budget = CUBudget(min_score_delta=0.05, min_roi_threshold=0.0)
    runner = ImprovementCycleRunner(benchmark, optimizer, budget)
    cycle = runner.run_one(Harness(system_prompt="x"))
    # 0.001 improvement < 0.05 threshold → REVERT
    assert cycle.decision == CycleDecision.REVERT
