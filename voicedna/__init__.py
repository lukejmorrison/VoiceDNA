"""VoiceDNA package.

Heavy dependencies (cryptography, pydub, etc.) are optional; the lightweight
openclaw_adapter submodule must remain importable without them.
"""

from __future__ import annotations

try:
    from .voice_dna import VoiceDNA  # noqa: F401
    from .consistency import VoiceConsistencyEngine  # noqa: F401
    from .framework import VoiceDNAProcessor  # noqa: F401
    from .filters import AgeMaturationFilter, ImprintConverterFilter  # noqa: F401
    from .providers import PersonaPlexTTS, PiperTTS  # noqa: F401
    from .synthesis import (  # noqa: F401
        is_omarchy_environment,
        play_wav_bytes,
        select_natural_backend,
        synthesize_and_process,
    )
    from .plugins import (  # noqa: F401
        Base64PassThroughFilter,
        IVoiceDNAFilter,
        PluginManager,
        PromptTagFilter,
    )
except ModuleNotFoundError:  # pragma: no cover – heavy deps not installed
    pass

__version__ = "3.0.0"
