"""Meta-optimizer abstractions.

A `MetaOptimizer` proposes a new harness given a current harness and
benchmark feedback. Implementations vary:

- `EchoMetaOptimizer`: returns the input harness unchanged. Useful for tests.
- `PromptRewriteOptimizer`: applies a caller-supplied transformation function
  to the system prompt. Useful for testing the cycle without paying CU.
- `CUPaidOptimizer` (planned, v0.2): asks a frontier model to rewrite the
  harness, paying for the inference in CU via forge-sdk.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable

from forge_mind.harness import Harness
from forge_mind.types import BenchmarkResult, ImprovementProposal


class MetaOptimizer(ABC):
    """Abstract interface for harness improvement proposers."""

    @abstractmethod
    def propose(
        self,
        current: Harness,
        benchmark: BenchmarkResult,
    ) -> ImprovementProposal:
        """Propose a new harness based on the current one and its benchmark.

        Implementations are free to use any strategy: rule-based, ML-based,
        frontier-model-paid, hybrid.
        """
        raise NotImplementedError


class EchoMetaOptimizer(MetaOptimizer):
    """Returns the input harness unchanged. Default and useful for tests."""

    def propose(
        self,
        current: Harness,
        benchmark: BenchmarkResult,
    ) -> ImprovementProposal:
        # The proposed harness must be a NEW version (not an alias to current)
        # so version semantics work. We evolve with no actual changes.
        proposed = current.evolve(description=f"echo of v{current.version}")
        return ImprovementProposal(
            proposed_harness=proposed,
            proposer_model="echo",
            rationale="no-op proposal",
            cu_cost_to_propose=0,
        )


class PromptRewriteOptimizer(MetaOptimizer):
    """Applies a caller-supplied transform to the system prompt.

    Useful for testing the cycle: pass a function that, e.g., appends
    "Be concise." to the prompt, and verify the cycle keeps it if it
    improves the benchmark score.
    """

    def __init__(
        self,
        transform: Callable[[str], str],
        *,
        proposer_model: str = "local-rewrite",
        cu_cost_per_proposal: int = 0,
    ) -> None:
        self.transform = transform
        self.proposer_model = proposer_model
        self.cu_cost_per_proposal = cu_cost_per_proposal

    def propose(
        self,
        current: Harness,
        benchmark: BenchmarkResult,
    ) -> ImprovementProposal:
        new_prompt = self.transform(current.system_prompt)
        proposed = current.evolve(
            system_prompt=new_prompt,
            description=f"prompt rewrite via {self.proposer_model}",
        )
        return ImprovementProposal(
            proposed_harness=proposed,
            proposer_model=self.proposer_model,
            rationale=f"applied transform on prompt at v{current.version}",
            cu_cost_to_propose=self.cu_cost_per_proposal,
        )
