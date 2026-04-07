"""Harness — the unit of self-improvement.

A harness is a complete agent configuration: system prompt, tool definitions,
sub-agent setup, and model routing strategy. The forge-mind self-improvement
loop mutates harnesses, benchmarks them, and decides whether to keep changes.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from typing import Optional

from forge_mind.types import ModelStrategy, ToolDefinition


@dataclass
class Harness:
    """Complete agent configuration; the unit of self-improvement.

    Mutations should produce a NEW harness via `evolve()` rather than
    mutating in place. This makes versioning, revert, and audit trivial.
    """

    system_prompt: str
    tools: list[ToolDefinition] = field(default_factory=list)
    model_strategy: ModelStrategy = field(
        default_factory=lambda: ModelStrategy(routes={"default": "qwen2.5:0.5b"})
    )
    sub_agents: list["Harness"] = field(default_factory=list)
    version: int = 1
    parent_version: Optional[int] = None
    description: str = ""

    def evolve(
        self,
        *,
        system_prompt: Optional[str] = None,
        tools: Optional[list[ToolDefinition]] = None,
        model_strategy: Optional[ModelStrategy] = None,
        sub_agents: Optional[list["Harness"]] = None,
        description: Optional[str] = None,
    ) -> "Harness":
        """Produce a new harness with selected fields replaced.

        The new harness has `version = self.version + 1` and
        `parent_version = self.version`.
        """
        return replace(
            self,
            system_prompt=system_prompt if system_prompt is not None else self.system_prompt,
            tools=tools if tools is not None else self.tools,
            model_strategy=(
                model_strategy if model_strategy is not None else self.model_strategy
            ),
            sub_agents=sub_agents if sub_agents is not None else self.sub_agents,
            version=self.version + 1,
            parent_version=self.version,
            description=description if description is not None else self.description,
        )

    def to_dict(self) -> dict:
        return {
            "system_prompt": self.system_prompt,
            "tools": [
                {
                    "name": t.name,
                    "description": t.description,
                    "parameters_schema": t.parameters_schema,
                }
                for t in self.tools
            ],
            "model_strategy": {"routes": dict(self.model_strategy.routes)},
            "sub_agents": [a.to_dict() for a in self.sub_agents],
            "version": self.version,
            "parent_version": self.parent_version,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Harness":
        return cls(
            system_prompt=data["system_prompt"],
            tools=[
                ToolDefinition(
                    name=t["name"],
                    description=t["description"],
                    parameters_schema=t["parameters_schema"],
                )
                for t in data.get("tools", [])
            ],
            model_strategy=ModelStrategy(
                routes=dict(data.get("model_strategy", {}).get("routes", {}))
            ),
            sub_agents=[cls.from_dict(a) for a in data.get("sub_agents", [])],
            version=int(data.get("version", 1)),
            parent_version=data.get("parent_version"),
            description=data.get("description", ""),
        )

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_json(cls, raw: str) -> "Harness":
        return cls.from_dict(json.loads(raw))
