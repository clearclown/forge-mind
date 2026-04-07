"""Tests for forge_mind.benchmark."""

import pytest

from forge_mind.benchmark import InMemoryBenchmark
from forge_mind.harness import Harness


def test_in_memory_benchmark_returns_score():
    bench = InMemoryBenchmark(scoring_fn=lambda h: 0.7)
    h = Harness(system_prompt="test")
    result = bench.run(h)
    assert result.score == 0.7
    assert result.harness_version == h.version


def test_benchmark_clamps_above_one():
    bench = InMemoryBenchmark(scoring_fn=lambda h: 1.5)
    result = bench.run(Harness(system_prompt="x"))
    assert result.score == 1.0


def test_benchmark_clamps_below_zero():
    bench = InMemoryBenchmark(scoring_fn=lambda h: -0.3)
    result = bench.run(Harness(system_prompt="x"))
    assert result.score == 0.0


def test_benchmark_records_cu_cost():
    bench = InMemoryBenchmark(scoring_fn=lambda h: 0.5, cu_cost_per_run=42)
    result = bench.run(Harness(system_prompt="x"))
    assert result.cu_consumed == 42


def test_benchmark_is_deterministic():
    bench = InMemoryBenchmark(scoring_fn=lambda h: 0.5 if "be concise" in h.system_prompt else 0.3)
    h = Harness(system_prompt="be concise")
    a = bench.run(h)
    b = bench.run(h)
    assert a.score == b.score


def test_score_changes_with_harness():
    bench = InMemoryBenchmark(
        scoring_fn=lambda h: 0.5 + 0.05 * h.system_prompt.count("good")
    )
    h1 = Harness(system_prompt="hello")
    h2 = Harness(system_prompt="good good good")
    assert bench.run(h1).score < bench.run(h2).score
