"""CU budget management for self-improvement.

A `CUBudget` is a hard cap on how much the self-improvement loop can spend.
It tracks per-cycle and per-day spending, and gates each spend with a
predicate.
"""

from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class CUBudget:
    """Spending policy for the forge-mind self-improvement loop.

    All limits are HARD limits — the loop will not spend even one CU above
    the policy, even if it would yield a great improvement.
    """

    # Per-cycle limits
    max_cu_per_cycle: int = 5_000

    # Per-day limits
    max_cu_per_day: int = 50_000
    max_cycles_per_day: int = 20

    # Quality gates — improvements below these thresholds are reverted.
    min_score_delta: float = 0.01            # Must improve by 1% absolute
    min_roi_threshold: float = 1.0           # Must pay back > 1x what it cost

    # Internal counters
    spent_today_cu: int = 0
    cycles_today: int = 0
    day_started_ms: int = 0

    def __post_init__(self) -> None:
        if self.day_started_ms == 0:
            self.day_started_ms = int(time.time() * 1000)

    # ---------- Day rollover ----------

    def maybe_reset_day(self, *, now_ms: int | None = None) -> bool:
        """Reset per-day counters if 24 hours have elapsed.

        Returns True if a reset happened.
        """
        now = now_ms if now_ms is not None else int(time.time() * 1000)
        if now - self.day_started_ms >= 24 * 3_600_000:
            self.spent_today_cu = 0
            self.cycles_today = 0
            self.day_started_ms = now
            return True
        return False

    # ---------- Spend gating ----------

    def can_spend(self, cu_amount: int) -> bool:
        """Check if a spend of this size is permitted right now."""
        if cu_amount <= 0:
            return False
        if cu_amount > self.max_cu_per_cycle:
            return False
        if self.spent_today_cu + cu_amount > self.max_cu_per_day:
            return False
        if self.cycles_today >= self.max_cycles_per_day:
            return False
        return True

    def can_start_cycle(self) -> bool:
        """Check if another improvement cycle can start right now."""
        return self.cycles_today < self.max_cycles_per_day

    # ---------- Recording ----------

    def record_spend(self, cu_amount: int) -> None:
        """Record that a spend occurred. Caller must check `can_spend` first."""
        if not self.can_spend(cu_amount):
            raise ValueError(
                f"refused to record spend of {cu_amount} CU — exceeds budget"
            )
        self.spent_today_cu += cu_amount

    def record_cycle_start(self) -> None:
        """Increment the cycle counter for the current day."""
        if not self.can_start_cycle():
            raise ValueError("refused to start cycle — daily cycle limit reached")
        self.cycles_today += 1

    # ---------- Decision helpers ----------

    def is_improvement_worth_keeping(
        self,
        score_delta: float,
        cu_invested: int,
        cu_return_estimate: int,
    ) -> bool:
        """Decide whether an improvement should be kept based on policy."""
        if score_delta < self.min_score_delta:
            return False
        if cu_invested <= 0:
            return score_delta > 0  # Free improvement, always keep
        roi = cu_return_estimate / cu_invested
        return roi >= self.min_roi_threshold
