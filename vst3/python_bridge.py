from voice_dna import VoiceDNA
from voicedna.framework import VoiceDNAProcessor


class VoiceDNA_VST_Bridge:
    def __init__(self, dna_path: str, password: str):
        self.dna = VoiceDNA.load_encrypted(password=password, filepath=dna_path)
        self.processor = VoiceDNAProcessor()

    def process(self, audio_bytes: bytes, params: dict | None = None) -> bytes:
        return self.processor.process(audio_bytes, self.dna, params or {})
