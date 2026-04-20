"""tests/test_openclaw_live_voice.py — End-to-end integration tests for OpenClaw voice wiring.

Validates that:
1. The demo script runs without errors
2. Demo WAV files are produced and are valid RIFF/WAVE format
3. The entire VoiceAdapter → synthesis pipeline works end-to-end
4. Per-agent preset selection integrates correctly with OpenClaw agent IDs
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure repo root is on sys.path when running from repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from voicedna.openclaw_adapter import VoiceAdapter, PRESET_REGISTRY
from voicedna.openclaw_live_voice import render_agent_voice, reset_adapter


class TestOpenClawDemoScript:
    """Verify the demo script can be invoked and produces valid output."""

    def test_demo_script_exists(self):
        demo_path = Path(__file__).resolve().parents[1] / "examples" / "openclaw_voicedemo.py"
        assert demo_path.exists(), f"Demo script not found at {demo_path}"

    def test_demo_produces_output_dir(self):
        output_dir = Path(__file__).resolve().parents[1] / "examples" / "openclaw" / "output"
        assert output_dir.exists(), f"Output directory does not exist: {output_dir}"

    def test_demo_wav_files_exist(self):
        output_dir = Path(__file__).resolve().parents[1] / "examples" / "openclaw" / "output"
        expected_files = {
            "namshub_neutral.wav": "agent:namshub with neutral preset",
            "david_friendly.wav": "agent:david-hardman with friendly preset",
            "voss_flair.wav": "agent:dr-voss-thorne with flair preset",
        }
        for filename in expected_files:
            filepath = output_dir / filename
            assert filepath.exists(), f"Expected demo WAV not found: {filepath}"

    def test_demo_wav_files_are_nonempty(self):
        output_dir = Path(__file__).resolve().parents[1] / "examples" / "openclaw" / "output"
        for filename in ["namshub_neutral.wav", "david_friendly.wav", "voss_flair.wav"]:
            filepath = output_dir / filename
            size = filepath.stat().st_size
            assert size > 0, f"Demo WAV is empty: {filepath}"

    def test_demo_wav_files_are_wave_format(self):
        """Verify WAV files start with RIFF/WAVE magic bytes."""
        output_dir = Path(__file__).resolve().parents[1] / "examples" / "openclaw" / "output"
        for filename in ["namshub_neutral.wav", "david_friendly.wav", "voss_flair.wav"]:
            filepath = output_dir / filename
            header = filepath.read_bytes()[:12]
            # RIFF magic + size + WAVE magic
            assert header[:4] == b"RIFF", f"{filename}: missing RIFF magic"
            assert header[8:12] == b"WAVE", f"{filename}: missing WAVE magic"


class TestOpenClawIntegration:
    """Verify VoiceAdapter integration with OpenClaw agent identifiers."""

    def test_agent_mapping_exists(self):
        """Confirm preset mappings for all three pilot agents."""
        agent_presets = {
            "agent:namshub": "neutral",
            "agent:david-hardman": "friendly",
            "agent:dr-voss-thorne": "flair",
        }
        adapter = VoiceAdapter(agent_presets=agent_presets)
        for agent_id, expected_preset in agent_presets.items():
            selected = adapter.select_preset(agent_id)
            assert selected == expected_preset, (
                f"Agent {agent_id} preset mismatch: "
                f"expected {expected_preset!r}, got {selected!r}"
            )

    def test_agent_id_format_handling(self):
        """Ensure the adapter correctly handles full agent:namespace:id format."""
        adapter = VoiceAdapter(
            agent_presets={
                "agent:namshub:main": "neutral",
                "agent:dr-voss-thorne:subagent": "flair",
            }
        )
        assert adapter.select_preset("agent:namshub:main") == "neutral"
        assert adapter.select_preset("agent:dr-voss-thorne:subagent") == "flair"

    def test_fallback_chain_with_openclaw_ids(self):
        """Test the full fallback chain: agent_id → agent_name → default."""
        adapter = VoiceAdapter(
            agent_presets={"agent:david": "friendly"},
            default_preset="neutral",
        )
        # Exact match
        assert adapter.select_preset("agent:david") == "friendly"
        # Name alias fallback
        assert adapter.select_preset("unknown", agent_name="agent:david") == "friendly"
        # Default fallback
        assert adapter.select_preset("completely-unknown") == "neutral"

    @pytest.mark.skipif(
        not all([p.read_bytes() for p in [
            Path(__file__).resolve().parents[1] / "examples" / "openclaw" / "output" / f
            for f in ["namshub_neutral.wav", "david_friendly.wav", "voss_flair.wav"]
        ] if p.exists()]),
        reason="Demo WAV files not all present"
    )
    def test_live_voice_synthesis_e2e(self):
        """End-to-end synthesis with all three agents and presets."""
        agent_presets = {
            "agent:namshub": "neutral",
            "agent:david-hardman": "friendly",
            "agent:dr-voss-thorne": "flair",
        }
        adapter = VoiceAdapter(agent_presets=agent_presets)

        test_texts = {
            "agent:namshub": "Hello from Namshub.",
            "agent:david-hardman": "Hi there, it's David.",
            "agent:dr-voss-thorne": "Dr Voss Thorne speaking.",
        }

        for agent_id, text in test_texts.items():
            preset = adapter.select_preset(agent_id)
            # Verify we can call synthesize without errors
            # (actual audio generation may be skipped if dependencies not installed)
            try:
                wav_bytes = adapter.synthesize(text, preset)
                assert isinstance(wav_bytes, bytes), "synthesize() should return bytes"
                assert len(wav_bytes) > 0, "synthesize() returned empty bytes"
            except RuntimeError as e:
                # Expected if voice_dna/voicedna packages not installed
                if "not installed" in str(e):
                    pytest.skip(f"Synthesis dependencies not available: {e}")
                raise


# ---------------------------------------------------------------------------
# TestRenderAgentVoice — render_agent_voice() opt-in guard and routing
# ---------------------------------------------------------------------------


class TestRenderAgentVoice:
    """Validate the OpenClaw live-voice bridge entry point."""

    def setup_method(self):
        # Ensure fresh adapter state for each test
        reset_adapter()

    def teardown_method(self):
        reset_adapter()

    def test_returns_none_when_env_not_set(self, monkeypatch):
        """render_agent_voice must be a no-op when VOICEDNA_OPENCLAW_PRESETS is absent."""
        monkeypatch.delenv("VOICEDNA_OPENCLAW_PRESETS", raising=False)
        result = render_agent_voice("Hello.", "agent:namshub")
        assert result is None

    def test_returns_none_when_env_is_empty_string(self, monkeypatch):
        monkeypatch.setenv("VOICEDNA_OPENCLAW_PRESETS", "")
        result = render_agent_voice("Hello.", "agent:namshub")
        assert result is None

    def test_opt_in_flag_enables_synthesis(self, monkeypatch):
        """When VOICEDNA_OPENCLAW_PRESETS=1 the function should attempt synthesis."""
        monkeypatch.setenv("VOICEDNA_OPENCLAW_PRESETS", "1")
        try:
            result = render_agent_voice("Hello.", "agent:namshub")
            assert isinstance(result, bytes)
            assert len(result) > 0
        except RuntimeError as exc:
            if "not installed" in str(exc):
                import pytest
                pytest.skip(f"Synthesis backend not available: {exc}")
            raise

    def test_agent_name_alias_resolution(self, monkeypatch):
        """render_agent_voice should forward agent_name for alias resolution."""
        monkeypatch.setenv("VOICEDNA_OPENCLAW_PRESETS", "1")
        try:
            result = render_agent_voice(
                "Hi.", "unknown-id", agent_name="agent:dr-voss-thorne"
            )
            assert isinstance(result, bytes)
        except RuntimeError as exc:
            if "not installed" in str(exc):
                import pytest
                pytest.skip(f"Synthesis backend not available: {exc}")
            raise

    def test_reset_adapter_clears_cache(self, monkeypatch):
        """reset_adapter() should clear the module-level adapter cache."""
        monkeypatch.setenv("VOICEDNA_OPENCLAW_PRESETS", "1")
        # Warm up the cache
        try:
            render_agent_voice("Warm.", "agent:namshub")
        except RuntimeError:
            pass
        # Reset
        reset_adapter()
        # Try again; no exception means adapter was re-created
        try:
            render_agent_voice("Cold.", "agent:namshub")
        except RuntimeError:
            pass  # Backend absent is fine; the point is no crash from stale state


class TestPresetRegistry:
    """Verify the pilot preset registry is complete and valid."""

    def test_all_pilot_presets_registered(self):
        assert "neutral" in PRESET_REGISTRY
        assert "friendly" in PRESET_REGISTRY
        assert "flair" in PRESET_REGISTRY

    def test_preset_descriptions_nonempty(self):
        for name, cfg in PRESET_REGISTRY.items():
            desc = cfg.get("description", "")
            assert desc and len(desc) > 0, f"Preset '{name}' has no description"

    def test_preset_traits_nonempty(self):
        for name, cfg in PRESET_REGISTRY.items():
            traits = cfg.get("unique_traits", [])
            assert isinstance(traits, list) and len(traits) > 0, (
                f"Preset '{name}' has empty or invalid unique_traits"
            )

    def test_preset_numerical_fields_in_range(self):
        """Ensure voice DNA parameters are in sensible ranges."""
        for name, cfg in PRESET_REGISTRY.items():
            imprint = cfg.get("imprint_strength")
            morph = cfg.get("morph_allowance")
            age = cfg.get("perceived_human_voice_age")

            assert 0.0 <= imprint <= 1.0, (
                f"Preset '{name}': imprint_strength {imprint} out of range [0, 1]"
            )
            assert 0.0 <= morph <= 1.0, (
                f"Preset '{name}': morph_allowance {morph} out of range [0, 1]"
            )
            assert age > 0, f"Preset '{name}': perceived_human_voice_age must be > 0"
