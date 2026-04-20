"""tests/test_openclaw_tts_post.py — Smoke tests for the TTS post-processor CLI."""

from __future__ import annotations

import io
import math
import struct
import sys
import wave
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from voicedna.openclaw_tts_post import post_process_wav, main


def _make_wav(duration_s: float = 0.1, sample_rate: int = 22050) -> bytes:
    """Return minimal valid WAV bytes."""
    frames = int(duration_s * sample_rate)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        for i in range(frames):
            val = int(32767 * 0.1 * math.sin(2 * math.pi * 440 * i / sample_rate))
            w.writeframesraw(struct.pack("<h", val))
    return buf.getvalue()


class TestPostProcessWav:
    def test_passthrough_when_env_not_set(self, tmp_path, monkeypatch):
        monkeypatch.delenv("VOICEDNA_OPENCLAW_PRESETS", raising=False)
        inp = tmp_path / "in.wav"
        out = tmp_path / "out.wav"
        inp.write_bytes(_make_wav())
        applied = post_process_wav(str(inp), str(out), "agent:namshub")
        assert applied is False
        assert out.exists()
        assert out.read_bytes() == inp.read_bytes()

    def test_passthrough_empty_env(self, tmp_path, monkeypatch):
        monkeypatch.setenv("VOICEDNA_OPENCLAW_PRESETS", "")
        inp = tmp_path / "in.wav"
        out = tmp_path / "out.wav"
        inp.write_bytes(_make_wav())
        applied = post_process_wav(str(inp), str(out), "agent:namshub")
        assert applied is False

    def test_output_created_on_passthrough(self, tmp_path, monkeypatch):
        monkeypatch.delenv("VOICEDNA_OPENCLAW_PRESETS", raising=False)
        inp = tmp_path / "in.wav"
        out = tmp_path / "subdir" / "out.wav"
        inp.write_bytes(_make_wav())
        post_process_wav(str(inp), str(out), "agent:namshub")
        assert out.exists()

    def test_voicedna_applied_when_opted_in(self, tmp_path, monkeypatch):
        monkeypatch.setenv("VOICEDNA_OPENCLAW_PRESETS", "1")
        inp = tmp_path / "in.wav"
        out = tmp_path / "out.wav"
        inp.write_bytes(_make_wav())
        try:
            applied = post_process_wav(
                str(inp), str(out), "agent:dr-voss-thorne", text="Greetings."
            )
            # If synthesis succeeded, result must be a valid WAV
            if applied:
                data = out.read_bytes()
                assert data[:4] == b"RIFF"
                assert data[8:12] == b"WAVE"
        except RuntimeError as e:
            if "not installed" in str(e):
                pytest.skip(f"Synthesis backend not available: {e}")
            raise

    def test_fallback_on_synthesis_error(self, tmp_path, monkeypatch):
        """If VoiceDNA synthesis raises, input must be copied to output unchanged."""
        monkeypatch.setenv("VOICEDNA_OPENCLAW_PRESETS", "1")
        inp = tmp_path / "in.wav"
        out = tmp_path / "out.wav"
        original = _make_wav()
        inp.write_bytes(original)

        # Patch render_agent_voice to raise
        import voicedna.openclaw_tts_post as module
        original_fn = module.render_agent_voice

        def _boom(*a, **kw):
            raise RuntimeError("Simulated synthesis failure")

        module.render_agent_voice = _boom
        try:
            applied = post_process_wav(str(inp), str(out), "agent:namshub")
            assert applied is False
            assert out.exists()
            assert out.read_bytes() == original
        finally:
            module.render_agent_voice = original_fn


class TestMainCLI:
    def test_missing_input_returns_1(self, tmp_path):
        rc = main(["--input", str(tmp_path / "missing.wav"), "--output", str(tmp_path / "out.wav"), "--agent-id", "agent:namshub"])
        assert rc == 1

    def test_passthrough_via_cli(self, tmp_path, monkeypatch):
        monkeypatch.delenv("VOICEDNA_OPENCLAW_PRESETS", raising=False)
        inp = tmp_path / "in.wav"
        out = tmp_path / "out.wav"
        inp.write_bytes(_make_wav())
        rc = main(["--input", str(inp), "--output", str(out), "--agent-id", "agent:namshub", "--text", "Hello."])
        assert rc == 0
        assert out.exists()
