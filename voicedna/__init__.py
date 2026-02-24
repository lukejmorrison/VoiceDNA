from .voice_dna import VoiceDNA
from .consistency import VoiceConsistencyEngine
from .framework import VoiceDNAProcessor
from .filters import AgeMaturationFilter, ImprintConverterFilter
from .providers import PersonaPlexTTS

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
]

__version__ = "2.9.0"
