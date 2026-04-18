"""voicedna.openclaw_live_voice — Live OpenClaw agent voice pipeline integration.

This module bridges VoiceAdapter (per-agent preset routing) with the
OpenClaw TTS hook pattern (VoiceDNATTSHook / process_tts_output).

Design goals:
- Per-agent preset selection via VoiceAdapter.select_preset()
- Synthesize using the preset's VoiceDNA parameters
- Opt-in only: import is required; no side effects on load
- Zero changes to existing voicedna/ code paths

Wiring entry point (OpenClaw skill / plugin):
    from voicedna.openclaw_live_voice import render_agent_voice

Usage:
    wav_bytes = render_agent_voice(
        text="Hello, I'm Dr Voss Thorne.",
        agent_id="agent:dr-voss-thorne",
        agent_name="dr-voss-thorne",   # optional alias
    )
"""

from __future__ import annotations

import logging
from typing import Optional

from voicedna.openclaw_adapter import VoiceAdapter, load_presets_from_env

logger = logging.getLogger("voicedna.openclaw_live_voice")

# ---------------------------------------------------------------------------
# Default agent → preset wiring for known OpenClaw agents.
# These can be overridden at runtime via VOICEDNA_OPENCLAW_PRESETS_MAP env var
# or by calling VoiceAdapter(agent_presets={...}) directly.
# ---------------------------------------------------------------------------
DEFAULT_AGENT_PRESET_MAP: dict[str, str] = {
    # Agent IDs
    "agent:namshub": "neutral",
    "agent:david-hardman": "friendly",
    "agent:dr-voss-thorne": "flair",
    # Agent name aliases
    "namshub": "neutral",
    "david-hardman": "friendly",
    "dr-voss-thorne": "flair",
}

_adapter: Optional[VoiceAdapter] = None


def _get_adapter() -> VoiceAdapter:
    """Return a shared VoiceAdapter, initialized lazily.

    Agent presets are merged: defaults first, then any env overrides.
    """
    global _adapter
    if _adapter is None:
        merged = dict(DEFAULT_AGENT_PRESET_MAP)
        env_map = load_presets_from_env()
        merged.update(env_map)
        _adapter = VoiceAdapter(agent_presets=merged)
        logger.info(
            "VoiceAdapter initialized with %d agent preset entries.", len(merged)
        )
    return _adapter


def render_agent_voice(
    text: str,
    agent_id: str,
    agent_name: Optional[str] = None,
    output_path: Optional[str] = None,
) -> bytes:
    """Synthesise *text* using the voice preset for *agent_id*.

    Parameters
    ----------
    text:
        The text to synthesise.
    agent_id:
        The agent identifier (e.g. "agent:dr-voss-thorne").
    agent_name:
        Optional alias for preset lookup fallback.
    output_path:
        If provided, writes the output WAV bytes to this path.

    Returns
    -------
    bytes
        Raw WAV audio bytes.
    """
    adapter = _get_adapter()
    preset = adapter.select_preset(agent_id, agent_name=agent_name)
    logger.info("agent_id=%r → preset=%r", agent_id, preset)
    return adapter.synthesize(text, preset, output_path=output_path)


def reset_adapter() -> None:
    """Reset the shared adapter (useful in tests or after env changes)."""
    global _adapter
    _adapter = None
