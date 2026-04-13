"""tests/test_voice_adapter.py — Smoke tests for voicedna.openclaw_adapter."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure repo root is on sys.path when running from repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from voicedna.openclaw_adapter import (
    PRESET_REGISTRY,
    DEFAULT_PRESET,
    VoiceAdapter,
    load_presets_from_env,
    AGENT_PRESETS,
)


# ---------------------------------------------------------------------------
# Preset registry basics
# ---------------------------------------------------------------------------


def test_pilot_presets_exist():
    for name in ("neutral", "friendly", "flair"):
        assert name in PRESET_REGISTRY, f"Missing expected preset: {name}"


def test_default_preset_is_valid():
    assert DEFAULT_PRESET in PRESET_REGISTRY


def test_preset_fields():
    required = {
        "description",
        "unique_traits",
        "imprint_strength",
        "morph_allowance",
        "perceived_human_voice_age",
        "maturation_multiplier",
        "stability_age",
    }
    for name, cfg in PRESET_REGISTRY.items():
        missing = required - set(cfg.keys())
        assert not missing, f"Preset '{name}' missing fields: {missing}"


# ---------------------------------------------------------------------------
# VoiceAdapter.select_preset
# ---------------------------------------------------------------------------


class TestSelectPreset:
    def setup_method(self):
        self.adapter = VoiceAdapter(
            agent_presets={
                "agent:namshub": "neutral",
                "agent:david-hardman": "friendly",
                "agent:dr-voss-thorne": "flair",
            }
        )

    def test_select_by_agent_id(self):
        assert self.adapter.select_preset("agent:namshub") == "neutral"
        assert self.adapter.select_preset("agent:david-hardman") == "friendly"
        assert self.adapter.select_preset("agent:dr-voss-thorne") == "flair"

    def test_select_by_agent_name_alias(self):
        adapter = VoiceAdapter(agent_presets={"Namshub": "friendly"})
        assert adapter.select_preset("unknown-id", agent_name="Namshub") == "friendly"

    def test_fallback_to_default(self):
        result = self.adapter.select_preset("agent:unknown")
        assert result == DEFAULT_PRESET

    def test_custom_default(self):
        adapter = VoiceAdapter(agent_presets={}, default_preset="flair")
        assert adapter.select_preset("anything") == "flair"

    def test_invalid_default_raises(self):
        with pytest.raises(ValueError, match="Unknown default preset"):
            VoiceAdapter(default_preset="does-not-exist")


# ---------------------------------------------------------------------------
# VoiceAdapter.synthesize — smoke: output file is created and non-empty
# ---------------------------------------------------------------------------


class TestSynthesize:
    def setup_method(self):
        self.adapter = VoiceAdapter(agent_presets={})

    def test_synthesize_returns_bytes(self):
        wav = self.adapter.synthesize("Hello.", "neutral")
        assert isinstance(wav, bytes)
        assert len(wav) > 0

    def test_synthesize_all_presets(self):
        for preset in PRESET_REGISTRY:
            wav = self.adapter.synthesize(f"Testing {preset}.", preset)
            assert len(wav) > 0, f"Empty output for preset '{preset}'"

    def test_synthesize_writes_file(self, tmp_path):
        out = tmp_path / "test_output.wav"
        self.adapter.synthesize("Write to disk.", "friendly", output_path=str(out))
        assert out.exists()
        assert out.stat().st_size > 0

    def test_synthesize_unknown_preset_raises(self):
        with pytest.raises(ValueError, match="Unknown preset"):
            self.adapter.synthesize("test", "does-not-exist")


# ---------------------------------------------------------------------------
# load_presets_from_env
# ---------------------------------------------------------------------------


class TestLoadPresetsFromEnv:
    def test_valid_json_map(self, monkeypatch):
        monkeypatch.setenv(
            "VOICEDNA_OPENCLAW_PRESETS_MAP",
            '{"agent:test": "flair"}',
        )
        # Clear module-level mapping first
        AGENT_PRESETS.clear()
        result = load_presets_from_env()
        assert result.get("agent:test") == "flair"

    def test_invalid_json_is_ignored(self, monkeypatch, caplog):
        monkeypatch.setenv("VOICEDNA_OPENCLAW_PRESETS_MAP", "not-json")
        AGENT_PRESETS.clear()
        result = load_presets_from_env()
        assert result == {} or result is AGENT_PRESETS  # no crash

    def test_unknown_preset_in_env_is_skipped(self, monkeypatch, caplog):
        monkeypatch.setenv(
            "VOICEDNA_OPENCLAW_PRESETS_MAP",
            '{"agent:test": "ghost-voice"}',
        )
        AGENT_PRESETS.clear()
        result = load_presets_from_env()
        assert "agent:test" not in result


# ---------------------------------------------------------------------------
# register_agent helper
# ---------------------------------------------------------------------------


def test_register_agent():
    adapter = VoiceAdapter(agent_presets={})
    adapter.register_agent("agent:new", "flair")
    assert adapter.select_preset("agent:new") == "flair"


def test_register_agent_unknown_preset_raises():
    adapter = VoiceAdapter(agent_presets={})
    with pytest.raises(ValueError):
        adapter.register_agent("agent:new", "ghost")


# ---------------------------------------------------------------------------
# presets property
# ---------------------------------------------------------------------------


def test_presets_property():
    adapter = VoiceAdapter(agent_presets={})
    p = adapter.presets
    assert set(p) == set(PRESET_REGISTRY.keys())
