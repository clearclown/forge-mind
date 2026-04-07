"""Benchmark abstraction.

A `Benchmark` runs a harness against a fixed task set and returns a
`BenchmarkResult` (score in [0, 1]). Implementations vary:

- `InMemoryBenchmark`: deterministic, fast, no inference cost. Used for tests.
- `LiveBenchmark` (planned): runs real inference via forge-sdk, costs CU.

The benchmark must be **deterministic** for the same harness — running it
twice on the same harness must produce the same score. This is what makes
the improvement cycle reliable.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable

from forge_mind.harness import Harness
from forge_mind.types import BenchmarkResult


class Benchmark(ABC):
    """Abstract benchmark interface."""

    @abstractmethod
    def run(self, harness: Harness) -> BenchmarkResult:
        """Evaluate `harness` against this benchmark and return a result."""
        raise NotImplementedError

    def name(self) -> str:
        return self.__class__.__name__


class InMemoryBenchmark(Benchmark):
    """A deterministic, in-memory benchmark.

    Useful for tests and for the v0.1 scaffold. Caller supplies a scoring
    function `f(harness) -> float in [0, 1]` and a sample count.
    """

    def __init__(
        self,
        scoring_fn: Callable[[Harness], float],
        sample_count: int = 100,
        cu_cost_per_run: int = 0,
    ) -> None:
        self.scoring_fn = scoring_fn
        self.sample_count = sample_count
        self.cu_cost_per_run = cu_cost_per_run

    def run(self, harness: Harness) -> BenchmarkResult:
        score = self.scoring_fn(harness)
        # Clamp to [0, 1] for safety against scoring functions that return
        # marginally out-of-range values.
        score = max(0.0, min(1.0, score))
        return BenchmarkResult(
            harness_version=harness.version,
            score=score,
            sample_count=self.sample_count,
            duration_ms=0,
            cu_consumed=self.cu_cost_per_run,
        )
