"""Tests for forge_mind.harness."""

import json

from forge_mind.harness import Harness
from forge_mind.types import ModelStrategy, ToolDefinition


def test_harness_default_version():
    h = Harness(system_prompt="hi")
    assert h.version == 1
    assert h.parent_version is None


def test_evolve_bumps_version_and_sets_parent():
    h = Harness(system_prompt="v1")
    h2 = h.evolve(system_prompt="v2")
    assert h2.version == 2
    assert h2.parent_version == 1
    assert h2.system_prompt == "v2"
    # Original is untouched
    assert h.version == 1
    assert h.system_prompt == "v1"


def test_evolve_chained():
    h = Harness(system_prompt="v1")
    h = h.evolve(system_prompt="v2")
    h = h.evolve(system_prompt="v3")
    assert h.version == 3
    assert h.parent_version == 2


def test_evolve_unspecified_fields_are_preserved():
    tools = [ToolDefinition(name="t", description="d", parameters_schema={})]
    h = Harness(
        system_prompt="hi",
        tools=tools,
        model_strategy=ModelStrategy(routes={"default": "qwen-8b"}),
        description="original",
    )
    h2 = h.evolve(system_prompt="bye")
    assert h2.tools == tools
    assert h2.model_strategy.routes == {"default": "qwen-8b"}
    assert h2.description == "original"


def test_to_dict_round_trip():
    h = Harness(
        system_prompt="hello",
        tools=[ToolDefinition(name="search", description="s", parameters_schema={"q": "string"})],
        model_strategy=ModelStrategy(routes={"default": "qwen-8b", "code": "qwen-32b"}),
        version=3,
        parent_version=2,
        description="test harness",
    )
    data = h.to_dict()
    h2 = Harness.from_dict(data)
    assert h2.system_prompt == h.system_prompt
    assert len(h2.tools) == 1
    assert h2.tools[0].name == "search"
    assert h2.model_strategy.routes == {"default": "qwen-8b", "code": "qwen-32b"}
    assert h2.version == 3
    assert h2.parent_version == 2


def test_to_json_is_valid_json():
    h = Harness(system_prompt="hi", description="test")
    raw = h.to_json()
    decoded = json.loads(raw)
    assert decoded["system_prompt"] == "hi"
    assert decoded["version"] == 1


def test_from_json_round_trip():
    h = Harness(system_prompt="round-trip test", version=5, parent_version=4)
    raw = h.to_json()
    h2 = Harness.from_json(raw)
    assert h2.system_prompt == h.system_prompt
    assert h2.version == 5
    assert h2.parent_version == 4


def test_model_strategy_default_fallback():
    s = ModelStrategy(routes={"default": "qwen-8b"})
    assert s.model_for("default") == "qwen-8b"
    assert s.model_for("nonexistent") == "qwen-8b"


def test_model_strategy_routing():
    s = ModelStrategy(routes={"default": "small", "reasoning": "large"})
    assert s.model_for("reasoning") == "large"
    assert s.model_for("default") == "small"
