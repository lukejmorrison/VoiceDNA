"""tests/test_openclaw_live_voice.py — Integration tests for openclaw_live_voice module."""

from __future__ import annotations

import sys

import pytest

# Ensure the project root is importable
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))

from voicedna.openclaw_live_voice import (
    DEFAULT_AGENT_PRESET_MAP,
    _get_adapter,
    render_agent_voice,
    reset_adapter,
)
from voicedna.openclaw_adapter import PRESET_REGISTRY


@pytest.fixture(autouse=True)
def reset_shared_adapter():
    """Reset the module-level adapter before each test."""
    reset_adapter()
    yield
    reset_adapter()


class TestDefaultAgentPresetMap:
    def test_known_agents_present(self):
        assert DEFAULT_AGENT_PRESET_MAP["agent:namshub"] == "neutral"
        assert DEFAULT_AGENT_PRESET_MAP["agent:david-hardman"] == "friendly"
        assert DEFAULT_AGENT_PRESET_MAP["agent:dr-voss-thorne"] == "flair"

    def test_aliases_present(self):
        assert DEFAULT_AGENT_PRESET_MAP["namshub"] == "neutral"
        assert DEFAULT_AGENT_PRESET_MAP["david-hardman"] == "friendly"
        assert DEFAULT_AGENT_PRESET_MAP["dr-voss-thorne"] == "flair"

    def test_all_values_are_valid_presets(self):
        for agent, preset in DEFAULT_AGENT_PRESET_MAP.items():
            assert preset in PRESET_REGISTRY, f"Agent '{agent}' maps to unknown preset '{preset}'"


class TestGetAdapter:
    def test_returns_voice_adapter(self):
        from voicedna.openclaw_adapter import VoiceAdapter
        adapter = _get_adapter()
        assert isinstance(adapter, VoiceAdapter)

    def test_singleton_behavior(self):
        a1 = _get_adapter()
        a2 = _get_adapter()
        assert a1 is a2

    def test_reset_creates_new(self):
        a1 = _get_adapter()
        reset_adapter()
        a2 = _get_adapter()
        assert a1 is not a2

    def test_env_overrides_applied(self, monkeypatch):
        import json
        env_map = {"agent:test-agent": "flair"}
        monkeypatch.setenv("VOICEDNA_OPENCLAW_PRESETS_MAP", json.dumps(env_map))
        # Also clear the module-level AGENT_PRESETS dict from adapter
        import voicedna.openclaw_adapter as adp
        adp.AGENT_PRESETS.clear()
        adapter = _get_adapter()
        assert adapter.select_preset("agent:test-agent") == "flair"


class TestRenderAgentVoice:
    def test_known_agent_id_returns_bytes(self):
        result = render_agent_voice("Hello.", "agent:namshub")
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_known_agent_name_alias(self):
        result = render_agent_voice("Hello.", "agent:unknown", agent_name="david-hardman")
        assert isinstance(result, bytes)

    def test_unknown_agent_falls_back_to_default(self):
        result = render_agent_voice("Hello.", "agent:nobody")
        # Default preset is "neutral"; should return bytes without error
        assert isinstance(result, bytes)

    def test_writes_output_file(self, tmp_path):
        out = str(tmp_path / "test_output.wav")
        render_agent_voice("Test.", "agent:dr-voss-thorne", output_path=out)
        assert __import__("pathlib").Path(out).exists()
        assert __import__("pathlib").Path(out).stat().st_size > 0

    def test_each_known_agent(self):
        agents = [
            ("agent:namshub", "neutral"),
            ("agent:david-hardman", "friendly"),
            ("agent:dr-voss-thorne", "flair"),
        ]
        adapter = _get_adapter()
        for agent_id, expected_preset in agents:
            preset = adapter.select_preset(agent_id)
            assert preset == expected_preset, f"{agent_id} → {preset!r}, expected {expected_preset!r}"
