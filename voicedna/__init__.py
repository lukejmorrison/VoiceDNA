from .voice_dna import VoiceDNA
from .consistency import VoiceConsistencyEngine
from .framework import VoiceDNAProcessor
from .filters import AgeMaturationFilter, ImprintConverterFilter
from .providers import PersonaPlexTTS
from .synthesis import is_omarchy_environment, play_wav_bytes, synthesize_and_process

from .plugins import (
    Base64PassThroughFilter,
    IVoiceDNAFilter,
    PluginManager,
    PromptTagFilter,
)

__all__ = [
    "VoiceDNA",
    "VoiceConsistencyEngine",
    "VoiceDNAProcessor",
    "AgeMaturationFilter",
    "ImprintConverterFilter",
    "IVoiceDNAFilter",
    "PluginManager",
    "Base64PassThroughFilter",
    "PromptTagFilter",
    "PersonaPlexTTS",
    "synthesize_and_process",
    "play_wav_bytes",
    "is_omarchy_environment",
]

__version__ = "2.9.2"
