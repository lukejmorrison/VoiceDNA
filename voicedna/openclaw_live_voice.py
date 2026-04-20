"""voicedna.openclaw_live_voice — Live-voice bridge entry point for OpenClaw.

This module provides the single public entry point for OpenClaw's TTS
post-processing hook to route agent speech through VoiceDNA presets.

Opt-in: this module is not imported by any default VoiceDNA code-path.
Enable per-agent voice routing by setting the env var:

    VOICEDNA_OPENCLAW_PRESETS=1

If the env var is not set, render_agent_voice() passes through without
applying any VoiceDNA preset (i.e., it returns None and does nothing).
This ensures OpenClaw's default TTS path is never disrupted.

Public API
----------
render_agent_voice(text, agent_id, agent_name=None, output_path=None) -> bytes | None
    Synthesize speech for the given agent using its registered VoiceDNA
    preset.  Returns WAV bytes on success, or None when the opt-in env
    var is not set.

Usage example (from OpenClaw TTS post-processing hook)
------------------------------------------------------
    from voicedna.openclaw_live_voice import render_agent_voice

    wav_bytes = render_agent_voice(
        text=tts_text,
        agent_id=agent.id,
        agent_name=getattr(agent, "name", None),
        output_path=maybe_output_path,
    )
    if wav_bytes:
        # use wav_bytes as the audio response
        ...

Rollback
--------
Unset VOICEDNA_OPENCLAW_PRESETS and remove the hook import.  No schema
migration or persistent state is required.
"""

from __future__ import annotations

import logging
import os
from typing import Optional

from voicedna.openclaw_adapter import (
    VoiceAdapter,
    load_presets_from_env,
)

logger = logging.getLogger("voicedna.openclaw_live_voice")

# Default pilot mapping (used when VOICEDNA_OPENCLAW_PRESETS_MAP is not set)
_DEFAULT_PILOT_MAP: dict[str, str] = {
    "agent:namshub": "neutral",
    "agent:david-hardman": "friendly",
    "agent:dr-voss-thorne": "flair",
}

# Module-level adapter cache — created once per process when first needed
_adapter: Optional[VoiceAdapter] = None


def _get_adapter() -> VoiceAdapter:
    """Return (and lazily create) the module-level VoiceAdapter instance."""
    global _adapter  # noqa: PLW0603
    if _adapter is None:
        # Populate from env first; fall back to pilot defaults
        env_map = load_presets_from_env()
        agent_presets = dict(_DEFAULT_PILOT_MAP)
        agent_presets.update(env_map)
        _adapter = VoiceAdapter(agent_presets=agent_presets)
        logger.debug(
            "openclaw_live_voice: VoiceAdapter ready with %d agent mappings.",
            len(agent_presets),
        )
    return _adapter


def render_agent_voice(
    text: str,
    agent_id: str,
    agent_name: Optional[str] = None,
    output_path: Optional[str] = None,
) -> Optional[bytes]:
    """Synthesize *text* as the voice of *agent_id* (opt-in guard included).

    Parameters
    ----------
    text:
        The text to speak.
    agent_id:
        Canonical agent identifier (e.g. "agent:namshub", "agent:dr-voss-thorne").
    agent_name:
        Optional human-readable alias used as a secondary lookup key.
    output_path:
        If provided, the generated WAV is written to this path.

    Returns
    -------
    bytes
        Raw WAV bytes when VOICEDNA_OPENCLAW_PRESETS=1 is set and synthesis
        succeeds.
    None
        When the opt-in env var is absent — OpenClaw should use its normal
        TTS path instead.
    """
    if not os.environ.get("VOICEDNA_OPENCLAW_PRESETS"):
        return None

    adapter = _get_adapter()
    preset = adapter.select_preset(agent_id, agent_name=agent_name)

    logger.info(
        "render_agent_voice: agent_id=%r agent_name=%r → preset=%r",
        agent_id,
        agent_name,
        preset,
    )

    return adapter.synthesize(text, preset, output_path=output_path)


def reset_adapter() -> None:
    """Clear the cached adapter (useful for testing or config hot-reload)."""
    global _adapter  # noqa: PLW0603
    _adapter = None
