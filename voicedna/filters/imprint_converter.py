import io
from typing import Dict

from voice_dna import VoiceDNA

from .audio_helpers import imprint_mix_wav_bytes
from ..plugins.base import IVoiceDNAFilter


class ImprintConverterFilter(IVoiceDNAFilter):
    def name(self) -> str:
        return "ImprintConverter"

    def priority(self) -> int:
        return 20

    def process(self, audio_bytes: bytes, dna: VoiceDNA, params: Dict) -> bytes:
        strength = max(0.0, min(1.0, dna.imprint_strength))
        params["imprint_converter.strength"] = strength
        params["imprint_converter.source"] = dna.imprint_source

        audio_format = params.get("audio_format", "wav")
        try:
            from pydub import AudioSegment

            source = AudioSegment.from_file(io.BytesIO(audio_bytes), format=audio_format)
            wet_gain_db = -18 + (12 * strength)
            wet = source.apply_gain(wet_gain_db)
            mixed = source.overlay(wet, gain_during_overlay=-(6 - 4 * strength))
            output = io.BytesIO()
            mixed.export(output, format=audio_format)
            return output.getvalue()
        except Exception as error:
            params["imprint_converter.error"] = str(error)
            if audio_format == "wav":
                try:
                    return imprint_mix_wav_bytes(audio_bytes, strength)
                except Exception as fallback_error:
                    params["imprint_converter.fallback_error"] = str(fallback_error)
            return audio_bytes
