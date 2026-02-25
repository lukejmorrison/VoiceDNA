from __future__ import annotations

from dataclasses import dataclass

from voice_dna import VoiceDNA
from voicedna import VoiceDNAProcessor


@dataclass
class VenomBridgeConfig:
    dna_path: str
    password: str


class VoiceDNAVenomBridge:
    def __init__(self, config: VenomBridgeConfig):
        self.config = config
        self.dna = VoiceDNA.load_encrypted(password=config.password, filepath=config.dna_path)
        self.processor = VoiceDNAProcessor()

    def process_pcm_bytes(self, audio_bytes: bytes, base_model: str = "vst3_reaper") -> bytes:
        params = {
            "audio_format": "wav",
            "base_model": base_model,
            "imprint_converter.mode": "simple",
        }
        return self.processor.process(audio_bytes, self.dna, params)

    def get_last_report(self) -> dict:
        return self.processor.get_last_report()
