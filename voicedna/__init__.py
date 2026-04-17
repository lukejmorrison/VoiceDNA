"""VoiceDNA package.

Heavy dependencies (cryptography, pydub, etc.) are optional; the lightweight
openclaw_adapter submodule must remain importable without them.
"""

from __future__ import annotations

try:
    from .voice_dna import VoiceDNA
    from .consistency import VoiceConsistencyEngine
    from .framework import VoiceDNAProcessor
    from .filters import AgeMaturationFilter, ImprintConverterFilter
    from .providers import PersonaPlexTTS, PiperTTS
    from .synthesis import (
        is_omarchy_environment,
        play_wav_bytes,
        select_natural_backend,
        synthesize_and_process,
    )
    from .plugins import (
        Base64PassThroughFilter,
        IVoiceDNAFilter,
        PluginManager,
        PromptTagFilter,
    )
except ModuleNotFoundError:  # pragma: no cover – heavy deps not installed
    pass

__version__ = "3.0.0"
