"""forge-mind — Layer 3 of the Forge ecosystem.

AutoAgent-style self-improvement loops where the meta-agent is paid for
in CU rather than driven by a human.
"""

from forge_mind.agent import ForgeMindAgent
from forge_mind.benchmark import Benchmark, InMemoryBenchmark
from forge_mind.budget import CUBudget
from forge_mind.cycle import ImprovementCycleRunner
from forge_mind.harness import Harness
from forge_mind.meta_optimizer import (
    EchoMetaOptimizer,
    MetaOptimizer,
    PromptRewriteOptimizer,
)
from forge_mind.types import (
    BenchmarkResult,
    CycleDecision,
    ImprovementCycle,
    ImprovementProposal,
    ModelStrategy,
    ToolDefinition,
)

__version__ = "0.1.0"

__all__ = [
    "Benchmark",
    "BenchmarkResult",
    "CUBudget",
    "CycleDecision",
    "EchoMetaOptimizer",
    "ForgeMindAgent",
    "Harness",
    "ImprovementCycle",
    "ImprovementCycleRunner",
    "ImprovementProposal",
    "InMemoryBenchmark",
    "MetaOptimizer",
    "ModelStrategy",
    "PromptRewriteOptimizer",
    "ToolDefinition",
    "__version__",
]
