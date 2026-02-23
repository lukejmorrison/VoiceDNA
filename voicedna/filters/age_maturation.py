import io
from typing import Dict

from voice_dna import VoiceDNA

from .audio_helpers import pitch_shift_wav_bytes
from ..plugins.base import IVoiceDNAFilter


class AgeMaturationFilter(IVoiceDNAFilter):
    def name(self) -> str:
        return "AgeMaturation"

    def priority(self) -> int:
        return 10

    def process(self, audio_bytes: bytes, dna: VoiceDNA, params: Dict) -> bytes:
        age = params.get("force_age") or dna.get_current_age()
        pitch_factor = 1.0 - (age - 5) * 0.015
        bounded_factor = max(0.5, min(1.25, pitch_factor))
        params["age_maturation.pitch_factor"] = bounded_factor

        audio_format = params.get("audio_format", "wav")
        try:
            from pydub import AudioSegment

            source = AudioSegment.from_file(io.BytesIO(audio_bytes), format=audio_format)
            shifted = source._spawn(source.raw_data, overrides={"frame_rate": int(source.frame_rate * bounded_factor)})
            normalized = shifted.set_frame_rate(source.frame_rate)
            output = io.BytesIO()
            normalized.export(output, format=audio_format)
            return output.getvalue()
        except Exception as error:
            params["age_maturation.error"] = str(error)
            if audio_format == "wav":
                try:
                    return pitch_shift_wav_bytes(audio_bytes, bounded_factor)
                except Exception as fallback_error:
                    params["age_maturation.fallback_error"] = str(fallback_error)
            return audio_bytes
