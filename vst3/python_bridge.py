from voice_dna import VoiceDNA
from voicedna.framework import VoiceDNAProcessor


class VoiceDNA_VST_Bridge:
    def __init__(self, dna_path: str, password: str):
        self.dna = VoiceDNA.load_encrypted(password=password, filepath=dna_path)
        self.processor = VoiceDNAProcessor()

    def process(
        self,
        audio_bytes: bytes,
        params: dict | None = None,
        *,
        force_age: float | None = None,
        imprint_strength: float | None = None,
    ) -> bytes:
        merged_params = dict(params or {})
        if force_age is not None:
            merged_params.setdefault("force_age", float(force_age))
        if imprint_strength is not None:
            self.dna.imprint_strength = max(0.0, min(1.0, float(imprint_strength)))
        return self.processor.process(audio_bytes, self.dna, merged_params)
