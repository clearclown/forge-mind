"""Tests for forge_mind.budget."""

import pytest

from forge_mind.budget import CUBudget


def test_default_budget_allows_typical_spends():
    b = CUBudget()
    assert b.can_spend(100)
    assert b.can_spend(b.max_cu_per_cycle)


def test_can_spend_rejects_zero_or_negative():
    b = CUBudget()
    assert not b.can_spend(0)
    assert not b.can_spend(-1)


def test_can_spend_rejects_above_per_cycle_cap():
    b = CUBudget(max_cu_per_cycle=1_000)
    assert b.can_spend(1_000)
    assert not b.can_spend(1_001)


def test_can_spend_rejects_above_per_day_cap():
    b = CUBudget(max_cu_per_cycle=10_000, max_cu_per_day=10_000)
    b.record_spend(8_000)
    assert b.can_spend(2_000)
    assert not b.can_spend(2_001)


def test_record_spend_increments_counter():
    b = CUBudget()
    b.record_spend(500)
    assert b.spent_today_cu == 500
    b.record_spend(200)
    assert b.spent_today_cu == 700


def test_record_spend_refuses_when_over_budget():
    b = CUBudget(max_cu_per_cycle=100, max_cu_per_day=100)
    b.record_spend(100)
    with pytest.raises(ValueError):
        b.record_spend(1)


def test_cycle_count_limit():
    b = CUBudget(max_cycles_per_day=3)
    assert b.can_start_cycle()
    b.record_cycle_start()
    b.record_cycle_start()
    b.record_cycle_start()
    assert not b.can_start_cycle()
    with pytest.raises(ValueError):
        b.record_cycle_start()


def test_day_rollover_resets_counters():
    b = CUBudget(max_cycles_per_day=2)
    b.record_cycle_start()
    b.record_spend(500)
    # Simulate 25 hours later
    later = b.day_started_ms + 25 * 3_600_000
    reset = b.maybe_reset_day(now_ms=later)
    assert reset is True
    assert b.cycles_today == 0
    assert b.spent_today_cu == 0
    assert b.can_start_cycle()


def test_day_rollover_no_op_within_24h():
    b = CUBudget()
    b.record_spend(500)
    later = b.day_started_ms + 1 * 3_600_000  # 1 hour
    reset = b.maybe_reset_day(now_ms=later)
    assert reset is False
    assert b.spent_today_cu == 500


def test_is_improvement_worth_keeping_rejects_low_delta():
    b = CUBudget(min_score_delta=0.05)
    assert not b.is_improvement_worth_keeping(
        score_delta=0.01, cu_invested=100, cu_return_estimate=1000
    )


def test_is_improvement_worth_keeping_accepts_good_roi():
    b = CUBudget(min_score_delta=0.01, min_roi_threshold=2.0)
    assert b.is_improvement_worth_keeping(
        score_delta=0.05, cu_invested=100, cu_return_estimate=300
    )


def test_is_improvement_worth_keeping_rejects_low_roi():
    b = CUBudget(min_score_delta=0.01, min_roi_threshold=2.0)
    assert not b.is_improvement_worth_keeping(
        score_delta=0.05, cu_invested=100, cu_return_estimate=150
    )


def test_zero_investment_improvement_always_kept_if_delta_positive():
    b = CUBudget()
    assert b.is_improvement_worth_keeping(
        score_delta=0.1, cu_invested=0, cu_return_estimate=0
    )
