"""Tests for forge_mind.agent."""

from forge_mind import (
    CUBudget,
    ForgeMindAgent,
    Harness,
    InMemoryBenchmark,
    PromptRewriteOptimizer,
)
from forge_mind.types import CycleDecision


def test_agent_keeps_improving_proposal():
    h = Harness(system_prompt="hello")
    bench = InMemoryBenchmark(
        scoring_fn=lambda h: 0.85 if "concise" in h.system_prompt else 0.5
    )
    opt = PromptRewriteOptimizer(transform=lambda p: p + " concise")
    agent = ForgeMindAgent(
        harness=h,
        benchmark=bench,
        optimizer=opt,
        budget=CUBudget(min_score_delta=0.001, min_roi_threshold=0.0),
    )
    agent.improve(n_cycles=1)
    assert agent.harness.system_prompt == "hello concise"
    assert agent.harness.version == 2
    assert agent.kept_count == 1
    assert agent.reverted_count == 0


def test_agent_reverts_regressing_proposal():
    h = Harness(system_prompt="hello")
    bench = InMemoryBenchmark(
        scoring_fn=lambda h: 0.3 if "concise" in h.system_prompt else 0.7
    )
    opt = PromptRewriteOptimizer(transform=lambda p: p + " concise")
    agent = ForgeMindAgent(
        harness=h,
        benchmark=bench,
        optimizer=opt,
        budget=CUBudget(min_score_delta=0.001, min_roi_threshold=0.0),
    )
    agent.improve(n_cycles=1)
    # Harness unchanged (still v1)
    assert agent.harness.system_prompt == "hello"
    assert agent.harness.version == 1
    assert agent.kept_count == 0
    assert agent.reverted_count == 1


def test_agent_runs_multiple_cycles():
    """Each successful cycle adds 'good' to the prompt."""
    score_target = 0.95

    def scoring(h):
        # 0.5 + 0.1 per "good" word, capped at 1.0
        return min(1.0, 0.5 + 0.1 * h.system_prompt.count("good"))

    h = Harness(system_prompt="hi")
    bench = InMemoryBenchmark(scoring_fn=scoring)
    opt = PromptRewriteOptimizer(transform=lambda p: p + " good")
    agent = ForgeMindAgent(
        harness=h,
        benchmark=bench,
        optimizer=opt,
        budget=CUBudget(min_score_delta=0.001, min_roi_threshold=0.0),
    )
    agent.improve(n_cycles=5)
    # Each cycle adds " good", so after 5 cycles the prompt has 5 goods
    assert agent.harness.system_prompt.count("good") == 5
    assert agent.harness.version == 6  # started at 1, +5
    assert agent.kept_count == 5

    stats = agent.stats()
    assert stats["score_delta"] >= score_target - 0.5 - 0.001  # ~0.45


def test_agent_stops_at_budget_exhaustion():
    h = Harness(system_prompt="x")
    bench = InMemoryBenchmark(scoring_fn=lambda h: 0.5)
    opt = PromptRewriteOptimizer(transform=lambda p: p + ".")
    budget = CUBudget(max_cycles_per_day=2)
    agent = ForgeMindAgent(harness=h, benchmark=bench, optimizer=opt, budget=budget)
    cycles = agent.improve(n_cycles=10)
    # First 2 are real (REVERT due to no score change), third is DEFER → loop stops
    assert len(cycles) == 3
    assert cycles[-1].decision == CycleDecision.DEFER


def test_agent_stats_initial_state():
    agent = ForgeMindAgent(
        harness=Harness(system_prompt="x"),
        benchmark=InMemoryBenchmark(scoring_fn=lambda h: 0.5),
        optimizer=PromptRewriteOptimizer(transform=lambda p: p),
    )
    stats = agent.stats()
    assert stats["cycle_count"] == 0
    assert stats["kept"] == 0
    assert stats["harness_version"] == 1
