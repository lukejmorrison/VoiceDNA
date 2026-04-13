"""voicedna.openclaw_adapter — Per-agent voice preset integration for OpenClaw.

Opt-in: this module is not loaded by any existing VoiceDNA code-path.
Enable per-agent voice routing by setting the env var:

    VOICEDNA_OPENCLAW_PRESETS=1

or by calling VoiceAdapter directly in your own code.

Public API
----------
select_preset(agent_id, agent_name=None) -> str
    Return the voice preset name for a given agent.

synthesize(text, preset, output_path=None) -> bytes
    Synthesize speech using the given preset.  Returns raw WAV bytes and
    optionally writes them to *output_path*.

PRESET_REGISTRY : dict[str, dict]
    Read-only registry of built-in pilot presets.

AGENT_PRESETS : dict[str, str]
    Runtime agent-id → preset mapping.  Populate from JSON/env before use
    or call load_presets_from_env() to auto-populate from
    VOICEDNA_OPENCLAW_PRESETS_MAP (JSON string).

Usage example
-------------
    from voicedna.openclaw_adapter import VoiceAdapter

    adapter = VoiceAdapter()
    preset  = adapter.select_preset("agent:namshub")
    wav     = adapter.synthesize("Hello from Namshub.", preset)
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from voice_dna import VoiceDNA
from voicedna.framework import VoiceDNAProcessor
from voicedna.synthesis import _SimpleLocalTTS


logger = logging.getLogger("voicedna.openclaw_adapter")

# ---------------------------------------------------------------------------
# Preset registry
# Each preset entry defines VoiceDNA construction params + processing hints.
# ---------------------------------------------------------------------------

PRESET_REGISTRY: Dict[str, Dict[str, Any]] = {
    "neutral": {
        "description": "Calm, clear, neutral assistant voice.",
        "unique_traits": ["steady_cadence", "neutral_tone", "even_breath"],
        "imprint_strength": 0.60,
        "morph_allowance": 0.06,
        "perceived_human_voice_age": 32.0,
        "maturation_multiplier": 1.0,
        "stability_age": 30.0,
        "process_params": {
            "imprint_converter.mode": "simple",
        },
    },
    "friendly": {
        "description": "Warm, upbeat, approachable voice.",
        "unique_traits": [
            "warm_hum_before_big_ideas",
            "gentle_rising_on_questions",
            "micro_laugh_soft_breath",
        ],
        "imprint_strength": 0.72,
        "morph_allowance": 0.10,
        "perceived_human_voice_age": 28.0,
        "maturation_multiplier": 1.05,
        "stability_age": 25.0,
        "process_params": {
            "imprint_converter.mode": "simple",
        },
    },
    "flair": {
        "description": "Expressive, distinctive voice with strong personality.",
        "unique_traits": [
            "theatrical_pause",
            "dynamic_pitch_shift",
            "sharp_consonants",
        ],
        "imprint_strength": 0.85,
        "morph_allowance": 0.04,
        "perceived_human_voice_age": 38.0,
        "maturation_multiplier": 0.98,
        "stability_age": 40.0,
        "process_params": {
            "imprint_converter.mode": "simple",
        },
    },
}

DEFAULT_PRESET = "neutral"

# Mutable runtime mapping: agent_id (or agent_name) → preset name.
# Populated by load_presets_from_env() or direct assignment.
AGENT_PRESETS: Dict[str, str] = {}


def load_presets_from_env() -> Dict[str, str]:
    """Populate AGENT_PRESETS from VOICEDNA_OPENCLAW_PRESETS_MAP (JSON string).

    Returns the mapping dict (also updates the module-level AGENT_PRESETS).
    Silently skips unknown preset names (logs a warning).
    """
    raw = os.environ.get("VOICEDNA_OPENCLAW_PRESETS_MAP", "")
    if not raw:
        return AGENT_PRESETS

    try:
        mapping: Dict[str, str] = json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.warning("VOICEDNA_OPENCLAW_PRESETS_MAP is not valid JSON: %s", exc)
        return AGENT_PRESETS

    for agent_key, preset_name in mapping.items():
        if preset_name not in PRESET_REGISTRY:
            logger.warning(
                "Unknown preset '%s' for agent '%s'; skipping.", preset_name, agent_key
            )
            continue
        AGENT_PRESETS[agent_key] = preset_name

    return AGENT_PRESETS


def _build_dna_for_preset(preset_name: str) -> VoiceDNA:
    """Construct a synthetic VoiceDNA instance for the given preset."""
    preset = PRESET_REGISTRY[preset_name]
    dna = VoiceDNA.create_new(
        imprint_audio_description=f"openclaw_preset_{preset_name}",
        user_name=f"openclaw_{preset_name}",
    )
    dna.unique_traits = list(preset["unique_traits"])
    dna.imprint_strength = float(preset["imprint_strength"])
    dna.morph_allowance = float(preset["morph_allowance"])
    dna.perceived_human_voice_age = float(preset["perceived_human_voice_age"])
    dna.maturation_multiplier = float(preset["maturation_multiplier"])
    dna.stability_age = float(preset["stability_age"])
    return dna


class VoiceAdapter:
    """Per-agent voice preset selector and synthesiser.

    Parameters
    ----------
    agent_presets:
        Optional agent-id → preset-name mapping.  If omitted, the module-level
        AGENT_PRESETS dict (populated via load_presets_from_env) is used.
    default_preset:
        Fallback preset when no mapping is found.  Defaults to "neutral".
    """

    def __init__(
        self,
        agent_presets: Optional[Dict[str, str]] = None,
        default_preset: str = DEFAULT_PRESET,
    ) -> None:
        if agent_presets is not None:
            self._agent_presets = agent_presets
        else:
            load_presets_from_env()
            self._agent_presets = AGENT_PRESETS

        if default_preset not in PRESET_REGISTRY:
            raise ValueError(
                f"Unknown default preset '{default_preset}'. Choose from: {list(PRESET_REGISTRY)}"
            )
        self._default_preset = default_preset

        self._tts = _SimpleLocalTTS()
        self._processor = VoiceDNAProcessor()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def select_preset(self, agent_id: str, agent_name: Optional[str] = None) -> str:
        """Return the preset name for *agent_id* (or *agent_name* as alias).

        Resolution order:
          1. Exact match on agent_id
          2. Exact match on agent_name (if provided)
          3. default_preset
        """
        if agent_id and agent_id in self._agent_presets:
            return self._agent_presets[agent_id]
        if agent_name and agent_name in self._agent_presets:
            return self._agent_presets[agent_name]
        return self._default_preset

    def synthesize(
        self,
        text: str,
        preset: str,
        output_path: Optional[str] = None,
    ) -> bytes:
        """Synthesise *text* using *preset*.

        Returns raw WAV bytes.  Optionally writes to *output_path*.
        """
        if preset not in PRESET_REGISTRY:
            raise ValueError(
                f"Unknown preset '{preset}'. Choose from: {list(PRESET_REGISTRY)}"
            )

        dna = _build_dna_for_preset(preset)
        raw_audio = self._tts.synthesize(text)

        preset_cfg = PRESET_REGISTRY[preset]
        process_params: Dict[str, Any] = {
            "text": text,
            "audio_format": "wav",
            "base_model": f"openclaw_{preset}",
            **preset_cfg.get("process_params", {}),
        }

        try:
            processed = self._processor.synthesize_and_process(
                text=text,
                dna=dna,
                tts_provider=self._tts,
                params=process_params,
            )
        except AttributeError:
            # Older VoiceDNAProcessor: use process() directly
            processed = self._processor.process(raw_audio, dna, process_params)

        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            Path(output_path).write_bytes(processed)
            logger.info("Wrote %d bytes to %s", len(processed), output_path)

        return processed

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    @property
    def presets(self) -> list[str]:
        """List of available preset names."""
        return list(PRESET_REGISTRY.keys())

    def register_agent(self, agent_id: str, preset: str) -> None:
        """Register a mapping at runtime."""
        if preset not in PRESET_REGISTRY:
            raise ValueError(f"Unknown preset '{preset}'.")
        self._agent_presets[agent_id] = preset
