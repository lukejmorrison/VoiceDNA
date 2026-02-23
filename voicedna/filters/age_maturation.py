from typing import Dict

from voice_dna import VoiceDNA

from ..plugins.base import IVoiceDNAFilter


class AgeMaturationFilter(IVoiceDNAFilter):
    def name(self) -> str:
        return "AgeMaturation"

    def priority(self) -> int:
        return 10

    def process(self, audio_bytes: bytes, dna: VoiceDNA, params: Dict) -> bytes:
        age = params.get("force_age") or dna.get_current_age()
        pitch_factor = 1.0 - (age - 5) * 0.015
        params["age_maturation.pitch_factor"] = max(0.5, min(1.25, pitch_factor))
        return audio_bytes
