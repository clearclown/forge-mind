"""Core data types for forge-mind."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from forge_mind.harness import Harness


@dataclass(frozen=True)
class ToolDefinition:
    """A single tool the agent can use."""

    name: str
    description: str
    parameters_schema: dict  # JSON Schema fragment


@dataclass(frozen=True)
class ModelStrategy:
    """Which model to use for which kind of task.

    Routing key examples: 'default', 'reasoning', 'coding', 'translation'.
    """

    routes: dict[str, str]  # routing_key → model_id

    def model_for(self, routing_key: str) -> str:
        return self.routes.get(routing_key, self.routes.get("default", ""))


@dataclass(frozen=True)
class BenchmarkResult:
    """Outcome of running a harness against a benchmark suite."""

    harness_version: int
    score: float  # 0.0-1.0
    sample_count: int
    duration_ms: int
    cu_consumed: int

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(f"score must be in [0.0, 1.0], got {self.score}")
        if self.sample_count < 1:
            raise ValueError("sample_count must be >= 1")


@dataclass(frozen=True)
class ImprovementProposal:
    """A meta-optimizer's suggested change to a harness."""

    proposed_harness: "Harness"
    proposer_model: str
    rationale: str
    cu_cost_to_propose: int


class CycleDecision(str, Enum):
    """Outcome of evaluating an improvement proposal."""

    KEEP = "keep"           # Apply the proposal, bump version
    REVERT = "revert"       # Discard the proposal
    DEFER = "defer"         # Couldn't decide; budget exhausted or benchmark invalid


@dataclass
class ImprovementCycle:
    """A complete benchmark → propose → benchmark → decide cycle."""

    baseline: BenchmarkResult
    proposal: ImprovementProposal
    candidate: BenchmarkResult
    decision: CycleDecision
    delta: float = 0.0
    roi_cu: float = 0.0

    def __post_init__(self) -> None:
        # Auto-compute delta if it wasn't passed in.
        if self.delta == 0.0 and self.candidate.score != self.baseline.score:
            self.delta = self.candidate.score - self.baseline.score
