from typing import Dict

from voice_dna import VoiceDNA

from ..plugins.base import IVoiceDNAFilter


class ImprintConverterFilter(IVoiceDNAFilter):
    def name(self) -> str:
        return "ImprintConverter"

    def priority(self) -> int:
        return 20

    def process(self, audio_bytes: bytes, dna: VoiceDNA, params: Dict) -> bytes:
        params["imprint_converter.strength"] = dna.imprint_strength
        params["imprint_converter.source"] = dna.imprint_source
        return audio_bytes
